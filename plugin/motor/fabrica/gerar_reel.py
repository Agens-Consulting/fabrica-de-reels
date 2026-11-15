"""Fábrica diária de trial reels (tipo A). Não usa IA: escolhe, monta e publica com regras fixas.

O que faz, por reel:
  1. Escolhe um texto do banco (hook + legenda) cujo recurso está ativo e que não saiu nos últimos 14 dias.
  2. Escolhe um B-roll do registo (não fraco, nem retirado), o menos usado, nunca repetindo o par texto + B-roll.
  3. Escolhe uma das músicas de fundo (a menos usada) e um trecho ao acaso.
  4. Sorteia 2 ou 3 alterações técnicas (edicao/variacoes.md): zoom, velocidade, brilho, cor, corte.
  5. Corta para 6 s (máximo 8), põe em 1080x1920 e queima o hook com o estilo fixo
     (hooks/estetica-e-posicionamento.md). A cor de destaque escolhe-se pelo fundo.
  6. Faz a capa, escreve a legenda e publica no Zernio como trial reel MANUAL (nunca promove).
  7. Regista tudo em fabrica/historico.jsonl.

Uso:
  PY=.venv/bin/python   # o ambiente do projeto
  $PY fabrica/gerar_reel.py um --quando "2026-11-14T21:00:00"      # um reel, publicado à hora dada (Lisboa)
  $PY fabrica/gerar_reel.py um --ensaio                             # só gera os ficheiros, não publica
  $PY fabrica/gerar_reel.py dia [--data AAAA-MM-DD] [--ensaio]      # os reels do dia (6, 8 ou 10), agendados
Opções de "um": --texto H001 --broll <nome do ficheiro> para forçar escolhas.
"""
import argparse
import colorsys
import json
import math
import pathlib
import random
import re
import subprocess
import sys
from datetime import date, datetime, timedelta

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FAB = RAIZ / 'fabrica'
BANCO = RAIZ / 'banco'
HIST = FAB / 'historico.jsonl'
SAIDA = FAB / 'saida'
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402  (tudo o que é pessoal vem do .env)

CONTA = cfg.get('ZERNIO_ACCOUNT_ID')         # conta de Instagram na Zernio
CHAVE_ENV = 'ZERNIO_API_KEY'
W, H = 1080, 1920

# --- regras fixas -------------------------------------------------------------------------------
DURACOES = [5.0, 6.0, 7.0, 8.0]   # variável de teste desde 14/11 (sorteada; limitada pelo corte do B-roll)
DURACAO_MAX = 8.0           # nunca mais do que isto
DURACAO_MIN = 5.0           # nunca mais curto do que isto
DIAS_SEM_REPETIR = 1        # o mesmo texto pode repetir dentro dos 14 dias (é preciso repetir para ver padrões);
                            # só não sai em dois dias seguidos. Dentro disso, sai o menos usado (todos rodam por igual).
VOLUMES = [6, 8, 10]        # conta não verificada; roda por dia
HORA_INICIO, HORA_FIM = cfg.hora('HORA_INICIO'), cfg.hora('HORA_FIM')   # janela de publicação (.env), nunca fora
INTERVALO_MIN = 5                   # minutos mínimos entre dois reels
ESTADOS_BROLL_OK = {'novo', 'a testar', 'vencedor'}

FONTE = str(cfg.caminho('FONTE_FICHEIRO'))
PESO = cfg.get('FONTE_PESO', 'SemiBold').encode()
EMOJI = cfg.fonte_emoji()   # Mac: Apple Color Emoji; Windows: Segoe UI Emoji
TAM, TAM_MIN, ENTRELINHA, LARGURA_UTIL, CENTRO_Y = 52, 40, 1.12, 900, 432   # 52 px desde 14/11 (62 e 60 eram grandes)
FONTE_IT = str(cfg.caminho('FONTE_ITALICO_FICHEIRO'))
PESO_IT = cfg.get('FONTE_ITALICO_PESO', 'Medium Italic').encode()

# --- variáveis de teste do hook (sorteadas por reel e guardadas no histórico para cruzar com métricas) ---
CAIXAS = ['maiusculas', 'frase']   # TUDO EM MAIÚSCULAS / Só a primeira (minúsculas saiu a 14/11: não resultou)
FIM_HOOK = ['nada', 'segundo_0', 'segundo_3']   # por baixo do hook: nada / 2.º hook desde 0 s / aos 3 s (setas: nunca)
SEGUNDOS = ['(vê a legenda)', '(está tudo na legenda)', '(lê a legenda até ao fim)', '(o resto está na legenda)']
TAM_SEGUNDO = 36
NOMES = {'CLAUDE': 'Claude', 'CHATGPT': 'ChatGPT', 'GITHUB': 'GitHub', 'GMAIL': 'Gmail', 'GOOGLE': 'Google',
         'DRIVE': 'Drive', 'EXCEL': 'Excel', 'WORD': 'Word', 'GEMINI': 'Gemini', 'COWORK': 'Cowork', 'CODE': 'Code',
         'CLAUDE.MD': 'CLAUDE.md', 'POV': 'POV', 'IA': 'IA', 'PDF': 'PDF', 'API': 'API', 'MCP': 'MCP',
         'WHATSAPP': 'WhatsApp', 'INSTAGRAM': 'Instagram', 'PORTUGAL': 'Portugal', 'OUTLOOK': 'Outlook',
         'ANTHROPIC': 'Anthropic', 'OPENAI': 'OpenAI', 'NOTION': 'Notion', 'COPILOT': 'Copilot'}
CONTORNO = 3
PALETA = cfg.cores_destaque()     # [(hex, rgb)] pela ordem do .env; a 1.ª é a de defeito
DELTA_E_MIN = 40


# --- utilitários --------------------------------------------------------------------------------
def ler_json(p, defeito):
    return json.loads(p.read_text()) if p.exists() else defeito


def historico():
    if not HIST.exists():
        return []
    return [json.loads(l) for l in HIST.read_text().splitlines() if l.strip()]


def duracao(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def ff(*args):
    r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        sys.exit('ffmpeg falhou: ' + r.stderr[-800:])


# --- escolhas -----------------------------------------------------------------------------------
def recursos_ativos():
    rec = ler_json(BANCO / 'recursos.json', {})
    return {k for k, v in rec.items() if v.get('ativo') and v.get('automacao_id')}


def escolher_texto(hist, rng, hoje, forcado=None, ja_hoje=()):
    textos = ler_json(BANCO / 'textos.json', [])
    if forcado:
        t = next((t for t in textos if t['id'] == forcado), None)
        return t or sys.exit(f'texto {forcado} não está no banco')
    ativos = recursos_ativos()
    limite = (hoje - timedelta(days=DIAS_SEM_REPETIR)).isoformat()
    recentes = {h['texto'] for h in hist if h['data'] >= limite} | set(ja_hoje)
    usos = {}
    for h in hist:
        usos[h['texto']] = usos.get(h['texto'], 0) + 1
    ok = [t for t in textos if t.get('estado', 'novo') not in ('retirado',)
          and t['recurso'] in ativos and t['id'] not in recentes]
    if not ok:
        sys.exit('não há textos disponíveis no banco (recursos ativos e fora da janela de 14 dias)')
    # 80/20: com vencedores no banco, 80% das vezes sai um vencedor; senão, o menos usado
    venc = [t for t in ok if t.get('estado') == 'vencedor']
    if venc and rng.random() < 0.8:
        ok = venc
    menor = min(usos.get(t['id'], 0) for t in ok)
    return rng.choice([t for t in ok if usos.get(t['id'], 0) == menor])


def escolher_broll(hist, rng, texto_id, forcado=None, ja_hoje=()):
    reg = ler_json(RAIZ / 'videos/registo.json', {})
    # só B-rolls já cortados nos melhores 6 s (videos/cortar.py)
    vids = [v for v in reg.values() if v.get('estado', 'novo') in ESTADOS_BROLL_OK and v.get('corte')
            and v['corte']['duracao_s'] >= DURACAO_MIN]
    if forcado:
        v = next((v for v in reg.values() if forcado in v['ficheiro']), None)
        return v or sys.exit(f'B-roll {forcado} não está no registo')
    usados_com_texto = {h['broll'] for h in hist if h['texto'] == texto_id}
    vids = [v for v in vids if v['ficheiro'] not in usados_com_texto and v['ficheiro'] not in ja_hoje] or vids
    usos = {}
    for h in hist:
        usos[h['broll']] = usos.get(h['broll'], 0) + 1
    menor = min(usos.get(v['ficheiro'], 0) for v in vids)
    return rng.choice([v for v in vids if usos.get(v['ficheiro'], 0) == menor])


def escolher_musica(hist, rng, ja_hoje=()):
    reg = ler_json(RAIZ / 'audios/registo.json', {})
    mus = [m for m in reg.values() if m.get('estado', 'novo') != 'retirado']
    usos = {}
    for f in [h['musica'] for h in hist] + list(ja_hoje):
        usos[f] = usos.get(f, 0) + 1
    menor = min(usos.get(m['ficheiro'], 0) for m in mus)
    m = rng.choice([m for m in mus if usos.get(m['ficheiro'], 0) == menor])
    d = m.get('duracao_s') or duracao(RAIZ / m['ficheiro'])
    bons = m.get('trechos_bons') or []                    # escritos pela análise de 14 dias
    if bons and rng.random() < 0.8:                       # 80% num trecho que ganhou, 20% a explorar
        t0, t1 = rng.choice(bons)
        inicio = round(rng.uniform(t0, max(t0, t1 - 8)), 1)
    else:
        inicio = round(rng.uniform(8, max(9, d - 20)), 1)  # salta a introdução, fica longe do fim
    return m, inicio


def sortear_variacoes(rng, tipo):
    """2 ou 3 alterações técnicas de edicao/variacoes.md (T7, a música, já muda sempre)."""
    # T5 (espelho) nunca: os B-rolls têm ecrãs, logótipos e texto filmado que ficariam ao contrário.
    # T6 (corte) já vem do videos/cortar.py; T7 (música) muda sempre.
    pool = ['T1', 'T2', 'T3', 'T4']
    esc = sorted(rng.sample(pool, rng.choice([2, 3])))
    v = {'lista': esc,
         'zoom': round(rng.uniform(1.01, 1.03), 3) if 'T1' in esc else 1.0,
         'velocidade': round(rng.choice([rng.uniform(0.97, 0.99), rng.uniform(1.01, 1.05)]), 3) if 'T2' in esc else 1.0,
         'brilho': round(rng.choice([-1, 1]) * rng.uniform(0.02, 0.04), 3) if 'T3' in esc else 0.0,
         'cor': rng.choice(['quente', 'fria']) if 'T4' in esc else None,
         'espelho': 'T5' in esc,
         'corte_inicio': round(rng.uniform(0.1, 0.3), 2) if 'T6' in esc else 0.0}
    return v


# --- texto no ecrã ------------------------------------------------------------------------------
def e_emoji(c):
    o = ord(c)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D)


def fatias(linha):
    """Parte uma linha em pedaços de texto normal e de emoji (bandeiras = 2 indicadores regionais)."""
    out, buf, em = [], '', None
    for c in linha:
        x = e_emoji(c)
        if em is None or x == em:
            buf += c
        else:
            out.append((buf, em)); buf = c
        em = x
    if buf:
        out.append((buf, em))
    return out


def fonte(size):
    f = ImageFont.truetype(FONTE, size)
    f.set_variation_by_name(PESO)
    return f


def img_emoji(txt, altura):
    # bandeiras e outros emoji compostos: o Pillow sem raqm não os junta, por isso vêm de PNG
    # extraídos da Apple Color Emoji para fabrica/assets/emoji_<códigos>.png
    png = FAB / 'assets' / ('emoji_' + '_'.join(f'{ord(c):x}' for c in txt) + '.png')
    if png.exists():
        im = Image.open(png).convert('RGBA')
        im = im.crop(im.getbbox())
        return im.resize((max(1, int(im.width * altura / im.height)), altura), Image.LANCZOS)
    if not EMOJI:
        return Image.new('RGBA', (1, altura), (0, 0, 0, 0))
    f = ImageFont.truetype(EMOJI, 160)
    w = int(f.getlength(txt)) + 10
    im = Image.new('RGBA', (w, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), txt, font=f, embedded_color=True)
    if not im.getbbox():
        return Image.new('RGBA', (1, altura), (0, 0, 0, 0))
    im = im.crop(im.getbbox())
    return im.resize((max(1, int(im.width * altura / im.height)), altura), Image.LANCZOS)


def largura_linha(linha, f, size):
    w = 0
    for txt, em in fatias(linha):
        w += img_emoji(txt.replace('️', ''), int(size * 0.9)).width if em else f.getlength(txt)
    return w


def ajustar_tamanho(linhas):
    size = TAM
    while size > TAM_MIN and max(largura_linha(l, fonte(size), size) for l in linhas) > LARGURA_UTIL:
        size -= 2
    return size


def caixa_hook(linhas, size):
    lh = int(size * ENTRELINHA)
    alto = lh * len(linhas)
    larg = max(largura_linha(l, fonte(size), size) for l in linhas)
    return int((W - larg) / 2), int(CENTRO_Y - alto / 2), int((W + larg) / 2), int(CENTRO_Y + alto / 2)


def srgb_lab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(lin, rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def cor_destaque(frames, caixa):
    """Primeira cor da paleta com ΔE >= 40 em relação ao fundo por trás do hook (spec, secção 3)."""
    x0, y0, x1, y1 = caixa
    zona = (max(0, x0 - 40), max(0, y0 - 40), min(W, x1 + 40), min(H, y1 + 40))
    medias = [ImageStat.Stat(Image.open(f).convert('RGB').crop(zona)).mean for f in frames]
    fundo = tuple(sum(m[i] for m in medias) / len(medias) for i in range(3))
    lf = srgb_lab(fundo)
    for nome, rgb in PALETA:
        de = math.dist(lf, srgb_lab(rgb))
        if de >= DELTA_E_MIN:
            return nome, rgb, round(de, 1), fundo
    return PALETA[0][0], PALETA[0][1], round(math.dist(lf, srgb_lab(PALETA[0][1])), 1), fundo


def _palavra(img, xy, txt, f, cor):
    """Contorno preto nítido de 3 px + sombra quase invisível (2 px abaixo, desfoque 4, ~35%)."""
    s = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).text((xy[0], xy[1] + 2), txt, font=f, fill=(0, 0, 0, 90),
                           stroke_width=CONTORNO, stroke_fill=(0, 0, 0, 90))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(img).text(xy, txt, font=f, fill=(*cor, 255), stroke_width=CONTORNO, stroke_fill=(0, 0, 0, 255))


def aplicar_caixa(linhas, modo):
    """O banco guarda os hooks em MAIÚSCULAS; aqui passam à caixa sorteada."""
    if modo == 'maiusculas':
        return [l.upper() for l in linhas]
    if modo == 'minusculas':                                # POV fica sempre em maiúsculas
        return [re.sub(r'\bpov\b', 'POV', l.lower()) for l in linhas]
    out, inicio = [], True                                  # 'frase': só a 1.ª letra (e os nomes próprios)
    for l in linhas:
        pal = []
        for p in l.split(' '):
            nucleo = p.strip('.,?!:;"“”()').upper()
            q = p.replace(p.strip('.,?!:;"“”()'), NOMES[nucleo]) if nucleo in NOMES else p.lower()
            if inicio and q[:1].isalpha():
                q = q[0].upper() + q[1:]; inicio = False
            elif inicio and q[:1].isdigit():
                inicio = False
            if q.rstrip().endswith(('.', '?', '!', ':')):
                inicio = True
            pal.append(q)
        out.append(' '.join(pal))
    return out


def png_segundo(txt, y_topo):
    """Segundo hook: pequeno, Montserrat Medium Italic, entre parênteses, logo abaixo do hook."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f = ImageFont.truetype(FONTE_IT, TAM_SEGUNDO)
    f.set_variation_by_name(PESO_IT)
    x = (W - f.getlength(txt)) / 2
    s = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).text((x, y_topo + 2), txt, font=f, fill=(0, 0, 0, 90), stroke_width=2, stroke_fill=(0, 0, 0, 90))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(img).text((x, y_topo), txt, font=f, fill=(255, 255, 255, 255), stroke_width=2,
                             stroke_fill=(0, 0, 0, 255))
    return img


FORCAR = {}   # para testes: {'caixa': ..., 'segundo_aos_s': ...} vindos da linha de comandos


def sortear_hook(rng, texto):
    caixa = FORCAR.get('caixa') or rng.choice(CAIXAS)
    fim = FORCAR.get('fim') or rng.choice(FIM_HOOK)
    segundo = (texto.get('segundo') or rng.choice(SEGUNDOS)) if fim.startswith('segundo') else None
    seta = None                                         # o campo 'seta' do banco já não se usa
    return {'caixa': caixa, 'fim': fim, 'segundo': segundo,
            'segundo_aos_s': float(fim.split('_')[1]) if segundo else None, 'seta': seta}


def png_hook(linhas, destaque, cor_dest, size):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f = fonte(size)
    lh = int(size * ENTRELINHA)
    asc, desc = f.getmetrics()
    y0 = CENTRO_Y - lh * len(linhas) / 2
    chave = {d.upper() for d in destaque}
    for i, ln in enumerate(linhas):
        x = (W - largura_linha(ln, f, size)) / 2
        y = y0 + i * lh + (lh - (asc + desc)) / 2
        for txt, em in fatias(ln):
            if em:
                e = img_emoji(txt.replace('️', ''), int(size * 0.9))
                img.alpha_composite(e, (int(x), int(y + (asc - e.height) * 0.8)))
                x += e.width
                continue
            for p in re.split(r'(\s+)', txt):
                if not p:
                    continue
                limpa = p.strip('.,?!:;"“”()').upper()
                cor = cor_dest if limpa and limpa in chave else (255, 255, 255)
                if not p.isspace():
                    _palavra(img, (x, y), p, f, cor)
                x += f.getlength(p)
    return img


# --- montagem -----------------------------------------------------------------------------------
def montar(texto, broll, musica, inicio_mus, var, pasta, rng):
    pasta.mkdir(parents=True, exist_ok=True)
    src = RAIZ / broll['corte']['ficheiro']           # corte de 6 s já escolhido
    d_src = duracao(src)
    vel = var['velocidade']
    ini = var['corte_inicio']
    # duração sorteada entre as que o corte aguenta (com a velocidade aplicada)
    possiveis = [d for d in DURACOES if d * vel <= d_src - ini + 0.02] or [min(DURACOES)]
    alvo = FORCAR.get('duracao') or rng.choice(possiveis)
    precisa = min(alvo * vel, d_src - ini)

    z = var['zoom']
    filtros = [f'scale={int(W * z)}:{int(H * z)}:force_original_aspect_ratio=increase',
               f'crop={W}:{H}', f'setpts=PTS/{vel}', 'fps=30']
    if var['brilho']:
        filtros.append(f"eq=brightness={var['brilho']}")
    if var['cor'] == 'quente':
        filtros.append('colorbalance=rs=0.04:bs=-0.03')
    elif var['cor'] == 'fria':
        filtros.append('colorbalance=rs=-0.03:bs=0.04')
    if var['espelho']:
        filtros.append('hflip')
    base = pasta / '_base.mp4'
    ff('-ss', ini, '-t', round(precisa, 3), '-i', src, '-an', '-vf', ','.join(filtros),
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', base)

    # cor de destaque a partir do fundo por trás do hook
    hv = sortear_hook(rng, texto)
    linhas = aplicar_caixa(texto['hook'], hv['caixa']) + ([hv['seta']] if hv['seta'] else [])
    size = ajustar_tamanho(linhas)
    caixa = caixa_hook(linhas, size)
    frames = []
    for k, t in enumerate((0.3, alvo / 2, alvo - 0.4)):
        fr = pasta / f'_f{k}.png'
        ff('-ss', t, '-i', base, '-frames:v', 1, fr)
        frames.append(fr)
    nome_cor, rgb, de, fundo = cor_destaque(frames, caixa)
    hook_png = pasta / 'hook.png'
    png_hook(linhas, texto.get('destaque', []), rgb, size).save(hook_png)
    seg_png = pasta / 'segundo.png'
    png_segundo(hv['segundo'] or '', caixa[3] + 14).save(seg_png)
    quando_seg = f"gte(t,{hv['segundo_aos_s']})" if hv['segundo'] else '0'

    final = pasta / 'reel.mp4'
    dur = round(min(duracao(base), alvo), 3)            # duração exata sorteada
    ff('-i', base, '-i', hook_png, '-i', seg_png, '-ss', inicio_mus, '-t', dur, '-i', RAIZ / musica['ficheiro'],
       '-filter_complex',
       f"[0:v][1:v]overlay=0:0[h];[h][2:v]overlay=0:0:enable='{quando_seg}',format=yuv420p[v];"
       f'[3:a]volume=0.85,afade=t=in:d=0.3,afade=t=out:st={max(0, dur - 0.6)}:d=0.6[a]',
       '-map', '[v]', '-map', '[a]', '-t', dur, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
       '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', final)
    capa = pasta / 'capa.jpg'
    ff('-ss', 0.5, '-i', final, '-frames:v', 1, '-q:v', 2, capa)
    (pasta / 'legenda.txt').write_text(texto['legenda'].strip() + '\n')
    for f in frames + [base]:
        f.unlink()
    if dur > DURACAO_MAX + 0.05:
        sys.exit(f'reel com {dur} s, acima do máximo de {DURACAO_MAX} s')
    return {'musica_trecho_s': [inicio_mus, round(inicio_mus + dur, 2)],   # segundos da música usados (para achar os melhores)
            'duracao_alvo': alvo, 'duracao_s': dur, 'inicio_broll': ini, 'tamanho_letra': size, 'hook_variaveis': hv,
            'hook_render': linhas,
            'cor_destaque': nome_cor, 'delta_e': de, 'fundo_rgb': [round(c) for c in fundo]}


def publicar(pasta, quando):
    import zernio_posts as z
    z.CHAVE_ENV = CHAVE_ENV
    import uuid
    psd = {'instagramThumbnail': z.carregar(pasta / 'capa.jpg'),
           'trialParams': {'graduationStrategy': 'MANUAL'}}       # nunca SS_PERFORMANCE
    corpo = {'content': (pasta / 'legenda.txt').read_text().strip(),
             'mediaItems': [{'type': 'video', 'url': z.carregar(pasta / 'reel.mp4')}],
             'platforms': [{'platform': 'instagram', 'accountId': CONTA, 'platformSpecificData': psd}],
             'scheduledFor': quando, 'timezone': cfg.get('FUSO', 'Europe/Lisbon')}
    res = z.api('POST', '/posts', corpo, {'Idempotency-Key': str(uuid.uuid5(uuid.NAMESPACE_URL, str(pasta) + quando))})
    post = res.get('post', res)
    return post.get('_id'), post.get('status')


def fazer_um(rng, hist, quando, n, ensaio, texto_id=None, broll_nome=None, ja_hoje=None):
    hoje = datetime.fromisoformat(quando).date() if quando else date.today()
    ja_hoje = ja_hoje or {'textos': [], 'brolls': [], 'musicas': []}
    texto = escolher_texto(hist, rng, hoje, texto_id, ja_hoje['textos'])
    broll = escolher_broll(hist, rng, texto['id'], broll_nome, ja_hoje['brolls'])
    musica, ini_mus = escolher_musica(hist, rng, ja_hoje.setdefault('musicas', []))
    var = sortear_variacoes(rng, broll.get('tipo'))
    pasta = SAIDA / hoje.isoformat() / f'{n:02d}_{texto["id"]}'
    info = montar(texto, broll, musica, ini_mus, var, pasta, rng)
    reg = {'data': hoje.isoformat(), 'quando': quando, 'texto': texto['id'], 'recurso': texto['recurso'],
           'molde': texto.get('molde'), 'broll': broll['ficheiro'], 'tipo_broll': broll.get('tipo'),
           'musica': musica['ficheiro'], 'inicio_musica': ini_mus, 'variacoes': var, **info,
           'pasta': str(pasta.relative_to(RAIZ)), 'post_id': None, 'estado': 'ensaio'}
    if not ensaio:
        reg['post_id'], reg['estado'] = publicar(pasta, quando)
        with HIST.open('a') as fh:
            fh.write(json.dumps(reg, ensure_ascii=False) + '\n')
    ja_hoje['textos'].append(texto['id'])
    ja_hoje['brolls'].append(broll['ficheiro'])
    ja_hoje['musicas'].append(musica['ficheiro'])
    print(json.dumps(reg, ensure_ascii=False))
    return reg


def agora_lisboa():
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(cfg.get('FUSO', 'Europe/Lisbon'))).replace(tzinfo=None)


def horarios(dia, n, rng, desde=None):
    """n horas de Lisboa entre 09:00 e 20:30 (regra fixa, nunca fora), com pelo menos 5 min entre elas.
    Com o dia inteiro pela frente, espalham-se pelo dia. Se o computador só ligou mais tarde, começam 15 min
    depois (tempo para montar e carregar os vídeos) e encolhem os intervalos até ao mínimo de 5 min, para sair
    o número do dia inteiro. Só saem menos se nem com 5 min de intervalo couberem até às 20:30."""
    ini, fim = HORA_INICIO * 60, HORA_FIM * 60
    if desde and desde.date() == dia:
        ini = max(ini, desde.hour * 60 + desde.minute + 15)
    if fim - ini < 0:
        return []
    n = max(1, min(n, int((fim - ini) // INTERVALO_MIN) + 1))
    if n == 1:
        minutos = [ini + rng.uniform(0, min(30, fim - ini))]
    else:
        passo = (fim - ini) / (n - 1)                      # intervalo médio entre reels
        folga = max(0.0, passo - INTERVALO_MIN)            # quanto cada um pode mexer sem ficar a <5 min do seguinte
        minutos = [ini + i * passo - rng.uniform(0, folga) * (i > 0) for i in range(n)]
    out = [datetime.combine(dia, datetime.min.time()) + timedelta(minutes=round(m)) for m in minutos]
    return [h.strftime('%Y-%m-%dT%H:%M:00') for h in out]


def main():
    a = argparse.ArgumentParser()
    s = a.add_subparsers(dest='cmd', required=True)
    u = s.add_parser('um')
    u.add_argument('--quando', help='AAAA-MM-DDTHH:MM:SS, hora de Lisboa')
    u.add_argument('--texto'); u.add_argument('--broll'); u.add_argument('--ensaio', action='store_true')
    u.add_argument('--caixa', choices=CAIXAS); u.add_argument('--fim', choices=FIM_HOOK)
    u.add_argument('--duracao', type=float, choices=DURACOES)
    u.add_argument('--n', type=int, help='número da pasta de saída (ensaios)')
    d = s.add_parser('dia')
    d.add_argument('--data'); d.add_argument('--ensaio', action='store_true')
    a = a.parse_args()
    rng = random.Random()
    hist = historico()
    if a.cmd == 'um':
        if not a.ensaio and not a.quando:
            sys.exit('para publicar é preciso --quando (hora de Lisboa)')
        if a.quando:
            hm = datetime.fromisoformat(a.quando)
            if not HORA_INICIO <= hm.hour + hm.minute / 60 <= HORA_FIM:
                sys.exit('fora da janela de publicação (09:00-20:30 de Lisboa)')
        if a.caixa:
            FORCAR['caixa'] = a.caixa
        for k in ('fim', 'duracao'):
            if getattr(a, k):
                FORCAR[k] = getattr(a, k)
        fazer_um(rng, hist, a.quando, a.n or len(hist) + 1, a.ensaio, a.texto, a.broll)
    else:
        agora = agora_lisboa()
        dia = date.fromisoformat(a.data) if a.data else agora.date()
        if any(h['data'] == dia.isoformat() and h['estado'] != 'ensaio' for h in hist):
            print(f'{dia} já tem reels agendados; nada a fazer')     # corre de hora a hora: sai em silêncio
            return
        n = VOLUMES[dia.toordinal() % len(VOLUMES)]
        horas = horarios(dia, n, rng, agora)
        if not horas:
            print(f'{dia}: já passou a janela de publicação (09:00-20:30); nada a fazer')
            return
        ja = {'textos': [], 'brolls': []}
        for i, q in enumerate(horas, 1):
            fazer_um(rng, hist, q, i, a.ensaio, ja_hoje=ja)
        print(f'{dia}: {len(horas)} reels {"gerados (ensaio)" if a.ensaio else "agendados"}')


if __name__ == '__main__':
    main()
