"""Reels talking head: do vídeo bruto (Drive/RAW) ao trial reel publicado (Drive/PUBLICADOS).

As partes mecânicas são deste script. As decisões (o que cortar, hooks, imagens, legenda, recurso) são do
Claude, escritas em trabalho/<slug>/plano.json, seguindo a skill reel-talking-head.

    correr a partir de talking-head/ com o Python do .venv da pasta de trabalho
    $PY scripts/th.py novos                         # vídeos na RAW ainda por tratar
    $PY scripts/th.py baixar <drive_id>             # descarrega para trabalho/<slug>/ e devolve o slug
    $PY scripts/th.py preparar <slug>               # 1080x1920, transcrição palavra a palavra (Whisper)
    $PY scripts/th.py imagens <slug>                # candidatas por frase + folhas de contacto para escolher
    $PY scripts/th.py render <slug>                 # corte, áudio, música, hook, imagens, legendas → saida/vN.mp4
    $PY scripts/th.py publicar <slug> [--ensaio]    # Zernio (trial MANUAL) + publicados/<slug> + histórico
    $PY scripts/th.py por-arquivar                  # brutos ainda na RAW (a skill move-os para PUBLICADOS)
    $PY scripts/th.py vigiar                        # para o launchd: se houver vídeo novo, chama o Claude
"""
import argparse
import json
import math
import pathlib
import random
import re
import subprocess
import sys
import unicodedata
import wave
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import servicos as sv  # noqa: E402
import texto as tx     # noqa: E402

AQUI = pathlib.Path(__file__).resolve().parent.parent
TRAB = AQUI / 'trabalho'
MUSICAS = AQUI.parent / 'audios' / 'raw'   # as músicas da Drive (videos/sincronizar.py)
ESTADO = AQUI / 'estado.json'
HIST = AQUI / 'historico.jsonl'
RAIZ = AQUI.parent
WHISPER = str(sv.cfg.venv_bin('whisper'))
MODELOS = str(RAIZ / 'ferramentas/modelos-whisper')
LISBOA = ZoneInfo(sv.cfg.get('FUSO', 'Europe/Lisbon'))
W, H, FPS = 1080, 1920, 30

# --- regras de edição (regras de base) ---------------------------------------------
GAP_JUNTA = 0.15        # pausas até isto ficam (respiração natural); acima corta-se
PAD_ANTES = 0.05        # margem antes da primeira palavra de um troço
PAD_DEPOIS = 0.06       # margem depois da última palavra (o fim das palavras não se come)
ESTENDE_MAX = 0.18      # a energia do áudio pode alargar a margem até isto (consoantes finais, "s", "r")
ZOOMS = (1.0, 1.08)     # alternado em cada corte
HOOK_DUR = (5.0, 6.0)   # o hook fica 5 a 6 s; depois entram as imagens
IMG_FOLGA = 0.3         # topo vazio entre imagens, quando a frase dura mais de 1,2 s
IMG_MIN = 1.0           # imagem com menos tempo do que isto não entra
VOL_MUSICA = 0.08       # música de fundo a 8% (10% ou menos)
GANHO_VOZ = 1.15        # +15% depois da redução de ruído (sempre, pelo menos 15%)
PALAVRAS_LEG = 3        # legendas de 3 em 3 palavras
CHARS_LEG = 20          # se 3 palavras passarem disto, vão 2 (ou 1)


# --- utilitários --------------------------------------------------------------------------------------
def ff(*args, log=None):
    r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        sys.exit('ffmpeg falhou: ' + r.stderr[-1500:])


def duracao(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def ler(p, defeito=None):
    p = pathlib.Path(p)
    return json.loads(p.read_text()) if p.exists() else defeito


def gravar(p, dados):
    pathlib.Path(p).write_text(json.dumps(dados, ensure_ascii=False, indent=1))


def slugify(nome):
    s = unicodedata.normalize('NFKD', pathlib.Path(nome).stem).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()[:40] or 'video'


def pasta(slug):
    p = TRAB / slug
    if not p.exists():
        sys.exit(f'não existe trabalho/{slug}')
    return p


# --- 1. entrada ---------------------------------------------------------------------------------------
def cmd_novos(_):
    est = ler(ESTADO, {})
    novos = [f for f in sv.drive_listar(sv.PASTA_RAW, so_videos=True) if f['id'] not in est]
    print(json.dumps(novos, ensure_ascii=False, indent=1))
    return novos


def cmd_baixar(a):
    est = ler(ESTADO, {})
    info = next((f for f in sv.drive_listar(sv.PASTA_RAW, so_videos=True) if f['id'] == a.id), None)
    if not info:
        sys.exit('esse id não está na pasta RAW')
    slug = datetime.now(LISBOA).strftime('%Y-%m-%d') + '_' + slugify(info['name'])
    p = TRAB / slug
    p.mkdir(parents=True, exist_ok=True)
    ext = pathlib.Path(info['name']).suffix or '.mov'
    sv.drive_descarregar(a.id, p / f'raw{ext}')
    gravar(p / 'origem.json', {'drive_id': a.id, 'nome': info['name'], 'criado': info.get('createdTime')})
    est[a.id] = {'slug': slug, 'estado': 'descarregado', 'nome': info['name'], 'quando': datetime.now(LISBOA).isoformat()}
    gravar(ESTADO, est)
    print(slug)


def cmd_preparar(a):
    p = pasta(a.slug)
    raw = next(p.glob('raw.*'))
    # vertical 1080x1920 a 30 fps (preenche e corta ao centro se vier noutro formato)
    ff('-i', raw, '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p',
       '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '1', p / 'base.mov')
    ff('-i', p / 'base.mov', '-vn', '-ac', '1', '-ar', '16000', p / 'audio16k.wav')
    r = subprocess.run([WHISPER, str(p / 'audio16k.wav'), '--model', a.modelo, '--language', 'pt',
                        '--word_timestamps', 'True', '--model_dir', MODELOS, '--output_format', 'json', '--output_dir', str(p),
                        '--condition_on_previous_text', 'False'], capture_output=True, text=True)
    if r.returncode:
        sys.exit('whisper falhou: ' + r.stderr[-800:])
    wj = ler(p / 'audio16k.json')
    palavras = []
    for seg in wj['segments']:
        for w in seg.get('words', []):
            palavras.append({'i': len(palavras), 'w': w['word'].strip(), 's': round(w['start'], 3),
                             'e': round(w['end'], 3)})
    gravar(p / 'palavras.json', palavras)
    # transcrição legível para o Claude: índice:palavra, com as pausas marcadas
    linhas, atual = [], []
    for k, w in enumerate(palavras):
        if k and w['s'] - palavras[k - 1]['e'] > 0.5:
            linhas.append(' '.join(atual)); atual = [f'⏸{w["s"] - palavras[k - 1]["e"]:.1f}s']
        atual.append(f'{w["i"]}:{w["w"]}')
    linhas.append(' '.join(atual))
    (p / 'transcricao.txt').write_text(
        f'# {len(palavras)} palavras, {duracao(p / "base.mov"):.1f} s. Formato índice:palavra; ⏸ = pausa.\n'
        + '\n'.join(linhas) + '\n')
    print(p / 'transcricao.txt')


# --- 2. cortes ----------------------------------------------------------------------------------------
def energia(p):
    with wave.open(str(p / 'audio16k.wav')) as wv:
        x = np.frombuffer(wv.readframes(wv.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    j = 160                                                   # janelas de 10 ms
    n = len(x) // j
    rms = np.sqrt((x[:n * j].reshape(n, j) ** 2).mean(axis=1) + 1e-12)
    fala = rms[rms > np.percentile(rms, 50)]
    limiar = max(np.percentile(rms, 20) * 3, (np.median(fala) if len(fala) else 0.01) * 0.10)
    return rms, float(limiar)


def tem_som(rms, limiar, t):
    k = int(t * 100)
    return 0 <= k < len(rms) and rms[k] > limiar


def palavras_mantidas(plano, palavras):
    out = []
    for de, ate in plano['manter']:
        out += [i for i in range(de, ate + 1) if i < len(palavras)]
    return out


def apertar(palavras, rms, limiar):
    """O Whisper estica as palavras por cima das pausas ("é..." a durar 1 s). Aperta cada palavra à zona
    onde há som de facto, para as pausas aparecerem e serem cortadas."""
    out = []
    for w in palavras:
        k0, k1 = int(w['s'] * 100), int(w['e'] * 100)
        ativos = [k for k in range(k0, min(k1 + 1, len(rms))) if rms[k] > limiar]
        s, e = w['s'], w['e']
        if ativos:
            s, e = max(s, ativos[0] / 100 - 0.01), min(e, ativos[-1] / 100 + 0.02)
            if e - s < 0.06:
                s, e = w['s'], w['e']
        out.append({**w, 's': round(s, 3), 'e': round(e, 3)})
    return out


def calcular_cortes(plano, palavras, rms, limiar):
    """Troços a manter (tempo do original) e o novo tempo de cada palavra mantida."""
    palavras = apertar(palavras, rms, limiar)
    manter = palavras_mantidas(plano, palavras)
    if not manter:
        sys.exit('plano sem palavras a manter')

    def inicio(i):
        lim = palavras[i - 1]['e'] + 0.02 if i > 0 else 0
        t = palavras[i]['s'] - PAD_ANTES
        while t - 0.01 > max(lim, palavras[i]['s'] - ESTENDE_MAX) and tem_som(rms, limiar, t - 0.01):
            t -= 0.01
        return max(lim, t, 0)

    def fim(i):
        lim = palavras[i + 1]['s'] - 0.02 if i + 1 < len(palavras) else palavras[i]['e'] + 0.3
        t = palavras[i]['e'] + PAD_DEPOIS
        while t + 0.01 < min(lim, palavras[i]['e'] + ESTENDE_MAX) and tem_som(rms, limiar, t + 0.01):
            t += 0.01
        return min(lim, t)

    trocos, atual = [], [manter[0]]
    for a, b in zip(manter, manter[1:]):
        if b == a + 1 and palavras[b]['s'] - palavras[a]['e'] <= GAP_JUNTA:
            atual.append(b)
        else:
            trocos.append(atual); atual = [b]
    trocos.append(atual)

    segs, novo, off = [], {}, 0.0
    for t in trocos:
        s, e = inicio(t[0]), fim(t[-1])
        if e - s < 0.1:
            continue
        for i in t:
            novo[i] = (round(off + palavras[i]['s'] - s, 3), round(off + palavras[i]['e'] - s, 3))
        segs.append((round(s, 3), round(e, 3)))
        off += e - s
    return segs, novo, round(off, 3)


# --- 3. imagens ---------------------------------------------------------------------------------------
def folha(cands, destino, titulo):
    lado, cols = 300, 3
    linhas = math.ceil(len(cands) / cols) or 1
    img = Image.new('RGB', (cols * lado, linhas * lado + 40), (20, 20, 20))
    d = ImageDraw.Draw(img)
    d.text((8, 10), titulo[:110], fill=(255, 255, 255), font=tx.fonte(18, b'Medium'))
    for n, c in enumerate(cands):
        try:
            im = Image.open(c['local']).convert('RGB')
        except Exception:
            continue
        im.thumbnail((lado - 6, lado - 6))
        x, y = (n % cols) * lado + 3, (n // cols) * lado + 43
        img.paste(im, (x, y))
        d.rectangle((x, y, x + 34, y + 30), fill=(0, 0, 0))
        d.text((x + 6, y + 2), str(n + 1), fill=(255, 230, 0), font=tx.fonte(24))
    img.save(destino, quality=85)


def cmd_imagens(a):
    p = pasta(a.slug)
    plano = ler(p / 'plano.json') or sys.exit('falta o plano.json')
    cand_dir = p / 'candidatos'
    cand_dir.mkdir(exist_ok=True)
    todas = ler(p / 'candidatos.json', {})
    for k, fr in enumerate(plano['frases']):
        if not fr.get('pesquisa') or (str(k) in todas and not a.refazer):
            continue
        res = sv.procurar_imagens(fr['pesquisa'], n_por_fonte=3)[:9]
        cands = []
        for n, c in enumerate(res):
            loc = cand_dir / f'{k:02d}_{n + 1}.jpg'
            try:
                sv.descarregar(c['mini'], loc)
                cands.append({**c, 'local': str(loc)})
            except Exception as e:
                print(f'  aviso: não desceu {c["mini"]}: {e}', file=sys.stderr)
        todas[str(k)] = cands
        folha(cands, cand_dir / f'folha_{k:02d}.jpg', f'frase {k}: ' + ' | '.join(fr['pesquisa']))
        print(f'frase {k}: {len(cands)} candidatas → candidatos/folha_{k:02d}.jpg')
    gravar(p / 'candidatos.json', todas)


def imagem_escolhida(p, k, fr, todas):
    """Descarrega a versão grande da candidata escolhida (fr['escolha'] = número na folha)."""
    if not fr.get('escolha'):
        return None
    c = todas[str(k)][int(fr['escolha']) - 1]
    grande = p / 'candidatos' / f'{k:02d}_escolhida.jpg'
    if not grande.exists():
        try:
            sv.descarregar(c['url'], grande)
            Image.open(grande).verify()
        except Exception:
            grande = pathlib.Path(c['local'])
    return grande


# --- 4. render ----------------------------------------------------------------------------------------
def texto_legenda(w):
    w = w.strip().strip('"“”«»')
    return re.sub(r'[.,;:…]+$', '', w)


def blocos_legenda(manter, palavras, novo, correcoes):
    """Grupos de 3 palavras (2 ou 1 se forem compridas), sem atravessar o fim de uma frase."""
    grupos, atual = [], []
    for i in manter:
        if i not in novo:
            continue
        w = texto_legenda(correcoes.get(str(i), palavras[i]['w']))
        if not w:
            continue
        cand = atual + [(i, w)]
        if atual and (len(cand) > PALAVRAS_LEG or len(' '.join(x for _, x in cand)) > CHARS_LEG):
            grupos.append(atual); cand = [(i, w)]
        atual = cand
        if re.search(r'[.?!…]$', palavras[i]['w'].strip()):
            grupos.append(atual); atual = []
    if atual:
        grupos.append(atual)
    out = []
    for g, prox in zip(grupos, grupos[1:] + [None]):
        s = novo[g[0][0]][0]
        e = novo[g[-1][0]][1] + 0.15
        if prox and novo[prox[0][0]][0] - e < 0.5:
            e = novo[prox[0][0]][0]
        out.append((s, e, ' '.join(w for _, w in g)))
    return out


def lista_concat(eventos, total, vazio, destino):
    """eventos [(início, fim, png)] → ficheiro do concat demuxer, com o PNG vazio nos buracos."""
    def _q(x):   # barras normais e plicas escapadas: funciona igual em Mac e Windows (C:/…)
        return pathlib.Path(x).as_posix().replace("'", "'\\''")
    vazio = _q(vazio)
    eventos = [(s, e, _q(png)) for s, e, png in eventos]
    linhas, t = [], 0.0
    for s, e, png in sorted(eventos):
        s, e = max(s, t), min(e, total)
        if e - s < 0.04:
            continue
        if s - t > 0.001:
            linhas += [f"file '{vazio}'", f'duration {s - t:.3f}']
        linhas += [f"file '{png}'", f'duration {e - s:.3f}']
        t = e
    if total - t > 0.001:
        linhas += [f"file '{vazio}'", f'duration {total - t:.3f}']
    linhas.append(f"file '{vazio}'")
    destino.write_text('ffconcat version 1.0\n' + '\n'.join(linhas) + '\n', encoding='utf-8')


def cmd_render(a):
    p = pasta(a.slug)
    plano = ler(p / 'plano.json') or sys.exit('falta o plano.json')
    palavras = ler(p / 'palavras.json')
    rms, limiar = energia(p)
    segs, novo, total = calcular_cortes(plano, palavras, rms, limiar)
    gravar(p / 'cortes.json', {'segmentos': segs, 'total_s': total, 'limiar_energia': limiar})
    print(f'{len(segs)} troços, {total:.1f} s (original {duracao(p / "base.mov"):.1f} s)')

    # 4.1 corte com zoom alternado (100% / 108%) em cada troço
    corte = p / 'corte.mov'
    fc, ins = [], []
    for k, (s, e) in enumerate(segs):
        z = ZOOMS[k % 2]
        zw, zh = int(round(W * z / 2) * 2), int(round(H * z / 2) * 2)
        fc.append(f'[0:v]trim={s}:{e},setpts=PTS-STARTPTS,scale={zw}:{zh},'
                  f'crop={W}:{H}:{(zw - W) // 2}:{int((zh - H) * 0.35)},setsar=1[v{k}]')
        d = e - s
        fc.append(f'[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,'
                  f'afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[a{k}]')
        ins.append(f'[v{k}][a{k}]')
    fc.append(''.join(ins) + f'concat=n={len(segs)}:v=1:a=1[v][a]')
    (p / 'corte_filtro.txt').write_text(';\n'.join(fc))
    ff('-i', p / 'base.mov', '-/filter_complex', p / 'corte_filtro.txt', '-map', '[v]', '-map', '[a]',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', corte)
    total = duracao(corte)

    # 4.2 camadas comuns: legendas e imagens
    camadas = p / 'camadas'
    camadas.mkdir(exist_ok=True)
    vazio = camadas / 'vazio.png'
    tx.png_vazio().save(vazio)
    manter = palavras_mantidas(plano, palavras)
    eventos_leg = []
    for n, (s, e, t) in enumerate(blocos_legenda(manter, palavras, novo, plano.get('correcoes', {}))):
        png = camadas / f'leg_{n:03d}.png'
        tx.png_legenda(t).save(png)
        eventos_leg.append((s, e, png))
    lista_concat(eventos_leg, total, vazio, camadas / 'legendas.txt')

    hook_dur = min(max(float(plano.get('hook_dur', 5.5)), HOOK_DUR[0]), HOOK_DUR[1], total)
    todas = ler(p / 'candidatos.json', {})
    eventos_img = []
    for k, fr in enumerate(plano['frases']):
        ks = [i for i in range(fr['de'], fr['ate'] + 1) if i in novo]
        if not ks:
            continue
        s, e = max(novo[ks[0]][0], hook_dur), novo[ks[-1]][1]
        if k + 1 < len(plano['frases']):          # vai até ao início da frase seguinte, menos a folga
            nk = [i for i in range(plano['frases'][k + 1]['de'], plano['frases'][k + 1]['ate'] + 1) if i in novo]
            if nk:
                e = max(e, novo[nk[0]][0])
        if e - s > 1.2:
            e -= IMG_FOLGA
        if e - s < IMG_MIN:
            continue
        img = imagem_escolhida(p, k, fr, todas)
        if not img:
            continue
        png = camadas / f'img_{k:02d}.png'
        tx.png_imagem(img).save(png)
        eventos_img.append((s, e, png))

    # 4.3 música: a menos usada nas últimas renderizações, trecho ao acaso
    hist = [json.loads(l) for l in HIST.read_text().splitlines() if l.strip()] if HIST.exists() else []
    mus = sorted(f for f in MUSICAS.glob('*') if f.suffix.lower() in ('.mp3', '.m4a', '.wav', '.aac', '.ogg'))
    usos = {m.name: sum(1 for h in hist if h.get('musica') == m.name) for m in mus}
    rng = random.Random()
    musica = rng.choice([m for m in mus if usos[m.name] == min(usos.values())])
    ini_mus = round(rng.uniform(5, max(6, duracao(musica) - total - 5)), 1)

    # 4.4 frames para a cor de destaque do hook
    frames = []
    for n, t in enumerate((0.4, hook_dur / 2, hook_dur - 0.3)):
        fr_ = camadas / f'_f{n}.png'
        ff('-ss', t, '-i', corte, '-frames:v', 1, fr_)
        frames.append(fr_)

    saida = p / 'saida'
    saida.mkdir(exist_ok=True)
    resumo = []
    for v, hk in enumerate(plano['hooks'], 1):
        nome_cor, rgb = tx.cor_destaque(frames, tx.caixa_hook(hk['linhas']))
        hook_png = camadas / f'hook_v{v}.png'
        tx.png_hook(hk['linhas'], hk.get('destaque', []), rgb).save(hook_png)
        lista_concat([(0, hook_dur, hook_png)] + eventos_img, total, vazio, camadas / f'topo_v{v}.txt')
        final = saida / f'v{v}.mp4'
        filtro = (
            '[0:v][1:v]overlay=0:0:eof_action=pass[t];[t][2:v]overlay=0:0:eof_action=pass,format=yuv420p[v];'
            f'[0:a]highpass=f=70,afftdn=nr=10:nf=-40,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,'
            f'volume={GANHO_VOZ}[voz];'
            f'[3:a]atrim=0:{total:.3f},volume={VOL_MUSICA},afade=t=in:d=0.6,'
            f'afade=t=out:st={max(0, total - 1.2):.3f}:d=1.2,aresample=48000[mus];'
            '[voz][mus]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.94:level=disabled[a]')
        ff('-i', corte, '-f', 'concat', '-safe', 0, '-i', camadas / f'topo_v{v}.txt',
           '-f', 'concat', '-safe', 0, '-i', camadas / 'legendas.txt',
           '-ss', ini_mus, '-i', musica, '-filter_complex', filtro, '-map', '[v]', '-map', '[a]',
           '-t', f'{total:.3f}', '-r', FPS, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', final)
        ff('-ss', 0.6, '-i', final, '-frames:v', 1, '-q:v', 2, saida / f'v{v}_capa.jpg')
        (saida / f'v{v}_legenda.txt').write_text(hk['legenda'].strip() + '\n')
        # folha de verificação: 8 frames ao longo do vídeo
        verif = []
        for n in range(8):
            fv = camadas / f'_v{v}_{n}.jpg'
            ff('-ss', round(total * (n + 0.5) / 8, 2), '-i', final, '-frames:v', 1, '-vf', 'scale=270:480', fv)
            verif.append(Image.open(fv))
        sheet = Image.new('RGB', (270 * 4, 480 * 2))
        for n, im in enumerate(verif):
            sheet.paste(im, ((n % 4) * 270, (n // 4) * 480))
        sheet.save(saida / f'v{v}_verificacao.jpg', quality=80)
        resumo.append({'variante': v, 'ficheiro': str(final.relative_to(AQUI)), 'hook': hk['linhas'],
                       'cor_destaque': nome_cor, 'duracao_s': round(duracao(final), 2)})
    gravar(p / 'render.json', {'musica': musica.name, 'inicio_musica': ini_mus, 'hook_dur': hook_dur,
                               'troços': len(segs), 'imagens': len(eventos_img), 'legendas': len(eventos_leg),
                               'variantes': resumo})
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


# --- 5. publicar --------------------------------------------------------------------------------------
def horarios(n, agora=None):
    """Primeira daqui a ~30 min; as seguintes com 3 h entre elas; só dentro da janela HORA_INICIO-HORA_FIM do .env, nunca fora. O que não couber no dia passa para as 09:00 do dia seguinte."""
    t = (agora or datetime.now(LISBOA)) + timedelta(minutes=30)
    out = []
    for _ in range(n):
        ini, fim = sv.cfg.hora('HORA_INICIO'), sv.cfg.hora('HORA_FIM')
        h_ini, m_ini = int(ini), round((ini % 1) * 60)
        if t.hour + t.minute / 60 < ini:
            t = t.replace(hour=h_ini, minute=m_ini)
        if t.hour + t.minute / 60 > fim:
            t = (t + timedelta(days=1)).replace(hour=h_ini, minute=m_ini)
        out.append(t.replace(second=0, microsecond=0))
        t += timedelta(hours=3)
    return [x.strftime('%Y-%m-%dT%H:%M:00') for x in out]


def cmd_publicar(a):
    p = pasta(a.slug)
    plano, render, origem = ler(p / 'plano.json'), ler(p / 'render.json'), ler(p / 'origem.json', {})
    if not render:
        sys.exit('ainda não há render')
    saida = p / 'saida'
    variantes = render['variantes']
    quando = horarios(len(variantes))
    if a.ensaio:
        print(json.dumps([{'v': v['variante'], 'quando': q, 'hook': v['hook']} for v, q in zip(variantes, quando)],
                         ensure_ascii=False, indent=1))
        return
    posts = []
    for v, q in zip(variantes, quando):
        n = v['variante']
        pid, estado = sv.zernio_trial_reel(saida / f'v{n}.mp4', saida / f'v{n}_capa.jpg',
                                           (saida / f'v{n}_legenda.txt').read_text(encoding='utf-8'), q)
        posts.append({'v': n, 'post_id': pid, 'estado': estado, 'quando': q})
        with HIST.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps({'data': q[:10], 'quando': q, 'slug': a.slug, 'variante': n, 'post_id': pid,
                                 'hook': v['hook'], 'molde': plano['hooks'][n - 1].get('molde'),
                                 'recurso': plano.get('recurso'), 'duracao_s': v['duracao_s'],
                                 'musica': render['musica'], 'cor_destaque': v['cor_destaque'],
                                 'imagens': render['imagens'], 'troços': render['troços']}, ensure_ascii=False) + '\n')
        print(f'v{n}: {estado} {q} ({pid})')
    # arquivo local: publicados/<slug>/ com as variantes e as legendas. Na Drive, o bruto passa da RAW para a
    # PUBLICADOS na próxima conversa (a skill faz isso pela ligação Google Drive; os vídeos ficam no disco).
    arq = AQUI / 'publicados' / a.slug
    arq.mkdir(parents=True, exist_ok=True)
    import shutil
    for v in variantes:
        n = v['variante']
        for f in (f'v{n}.mp4', f'v{n}_legenda.txt', f'v{n}_capa.jpg'):
            if (saida / f).exists():
                shutil.copy2(saida / f, arq / f)
    est = ler(ESTADO, {})
    if origem.get('drive_id'):
        est.setdefault(origem['drive_id'], {}).update({'estado': 'publicado', 'posts': posts, 'arquivo': str(arq),
                                                       'drive_arquivado': False})
        gravar(ESTADO, est)
    gravar(p / 'publicado.json', {'posts': posts, 'arquivo': str(arq)})


def cmd_por_arquivar(_):
    """Vídeos já publicados cujo bruto ainda está na RAW da Drive (a skill move-os pela ligação)."""
    est = ler(ESTADO, {})
    out = [{'drive_id': k, **v} for k, v in est.items() if v.get('estado') == 'publicado' and not v.get('drive_arquivado')]
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_arquivado(a):
    est = ler(ESTADO, {})
    if a.id in est:
        est[a.id]['drive_arquivado'] = True
        gravar(ESTADO, est)


# --- 6. vigiar (launchd) ------------------------------------------------------------------------------
def cmd_vigiar(_):
    if not sv.PASTA_RAW or sv.cfg.get('AUTOMATICO_CLAUDE', 'nao', obrigatorio=False) != 'sim':
        return
    hora = datetime.now(LISBOA)
    if not (sv.cfg.hora('HORA_INICIO') - 2 <= hora.hour + hora.minute / 60 <= sv.cfg.hora('HORA_FIM')):
        return
    trinco = AQUI / '.a_trabalhar'
    if trinco.exists() and (datetime.now().timestamp() - trinco.stat().st_mtime) < 3 * 3600:
        return
    est = ler(ESTADO, {})
    try:
        novos = [f for f in sv.drive_listar(sv.PASTA_RAW, so_videos=True) if f['id'] not in est]
    except Exception as ex:
        print('RAW ilegível:', ex)
        return
    if not novos:
        return
    logs = TRAB / '_logs'
    logs.mkdir(parents=True, exist_ok=True)
    trinco.write_text(novos[0]['id'])
    try:
        f = novos[0]
        prompt = (f'A pasta de trabalho dos Reels de Teste é {RAIZ}. Usa a skill reels-de-teste:reel-talking-head '
                  f'para tratar o vídeo novo da pasta RAW: drive_id {f["id"]} ("{f["name"]}"). '
                  'Estás em modo automático: faz tudo até publicar, sem perguntar nada.')
        with open(logs / f'{datetime.now():%Y%m%d-%H%M%S}.log', 'w', encoding='utf-8') as lg:
            r = subprocess.run([sv.cfg.claude_cli(), '-p', prompt, '--dangerously-skip-permissions'],
                               cwd=str(RAIZ), stdout=lg, stderr=subprocess.STDOUT, timeout=3 * 3600)
        if r.returncode != 0:
            sv.cfg.notificar(f'O vídeo {f["name"]} não foi publicado. Escreve /reels no Claude para ver.')
    finally:
        trinco.unlink(missing_ok=True)


def main():
    a = argparse.ArgumentParser()
    s = a.add_subparsers(dest='cmd', required=True)
    s.add_parser('novos')
    b = s.add_parser('baixar'); b.add_argument('id')
    pr = s.add_parser('preparar'); pr.add_argument('slug'); pr.add_argument('--modelo', default='medium')
    im = s.add_parser('imagens'); im.add_argument('slug'); im.add_argument('--refazer', action='store_true')
    r = s.add_parser('render'); r.add_argument('slug')
    pu = s.add_parser('publicar'); pu.add_argument('slug'); pu.add_argument('--ensaio', action='store_true')
    s.add_parser('vigiar')
    s.add_parser('por-arquivar')
    ar = s.add_parser('arquivado'); ar.add_argument('id')
    a = a.parse_args()
    {'novos': cmd_novos, 'baixar': cmd_baixar, 'preparar': cmd_preparar, 'imagens': cmd_imagens,
     'render': cmd_render, 'publicar': cmd_publicar, 'vigiar': cmd_vigiar,
     'por-arquivar': cmd_por_arquivar, 'arquivado': cmd_arquivado}[a.cmd](a)


if __name__ == '__main__':
    main()
