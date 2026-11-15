"""Envia à Agens os números do Instagram para o caso de estudo da fase gratuita (sem IA).

  inicio  Ponto de partida, no fim do passo 5 do /comecar: fotografia do perfil + últimas 50 publicações.
  ciclo   De 14 em 14 dias (chamado pela tarefa automática; sai logo se ainda não passaram 14 dias):
          fotografia do perfil + métricas de cada trial reel da fábrica e de cada talking head
          + últimas 50 publicações.
  relatorio <pasta do ciclo>  Depois da análise de 14 dias: o que o modelo percebeu (analise.json + texto do
          relatório com as conclusões) e o PDF, para a Agens melhorar o método.
  csv <pasta do ciclo>  Escreve na pasta do ciclo videos.csv (uma linha por vídeo publicado: tudo o que a fábrica
          decidiu — texto, hook, legenda, recurso, B-roll, música, letra, cor… — e as últimas métricas) e
          leituras.csv (todas as leituras de métricas de todos os vídeos, dia a dia). Não envia nada.
  estado  Mostra quando foi o último envio.

Só envia se REGISTO_AGENS=sim no .env (a pessoa aceitou no /comecar).
Vai só o que está aqui: números do Instagram, o @ e o nome. Nunca chaves, nunca o .env.
A tabela só aceita escritas: ninguém consegue ler os números de outra pessoa com esta chave.
"""
import base64
import csv
import io
import html as html_mod
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402

URL = 'https://xqbaqifcyxtajrsbpwga.supabase.co/rest/v1/fabrica_registos'
CHAVE = 'sb_publishable_DlQcZhk2UpQmQm-QGF_a8A_XehKnuxA'  # chave pública do Supabase (a tabela só aceita escritas)
CICLO_DIAS = 14
ESTADO = RAIZ / 'registos' / 'registo-agens.json'
M = RAIZ / 'metricas'


def ler_json(p, padrao=None):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return padrao


def jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]


def perfil_recente():
    fotos = sorted((M / 'perfil').glob('20*.json'))
    return ler_json(fotos[-1]) if fotos else None


def publicacoes():
    d = ler_json(M / 'perfil' / 'publicacoes.json', {}) or {}
    out = []
    for p in d.get('posts', []):
        a = p.get('analytics') or {}
        out.append({
            'publicado': p.get('publishedAt'),
            'tipo': p.get('mediaType') or p.get('type'),
            'url': p.get('platformPostUrl') or a.get('platformPostUrl'),
            'texto': (p.get('content') or '')[:160],
            **{k: a.get(k) for k in ('views', 'reach', 'likes', 'comments', 'shares', 'saves', 'follows',
                                     'profileViews', 'engagementRate', 'igReelsAvgWatchTime', 'reelsSkipRate')},
        })
    return out


def reels_fabrica():
    ultimo = ler_json(M / 'reels_ultimo.json', {}) or {}
    textos = {t.get('id'): t for t in (ler_json(RAIZ / 'banco' / 'textos.json', []) or [])}
    out = []
    for h in jsonl(RAIZ / 'fabrica' / 'historico.jsonl'):
        t = textos.get(h.get('texto'), {})
        hook = t.get('hook')
        out.append({
            'data': h.get('data'), 'quando': h.get('quando'), 'texto': h.get('texto'),
            'hook': ' '.join(hook) if isinstance(hook, list) else hook,
            'recurso': h.get('recurso'), 'molde': h.get('molde'), 'tipo_broll': h.get('tipo_broll'),
            'duracao_s': h.get('duracao_s'), 'post_id': h.get('post_id'),
            'metricas': ultimo.get(h.get('post_id') or ''),
        })
    return out


def talking_heads():
    ultimo = ler_json(M / 'reels_ultimo.json', {}) or {}
    out = []
    for h in jsonl(RAIZ / 'talking-head' / 'historico.jsonl'):
        out.append({k: h.get(k) for k in ('data', 'quando', 'hook', 'recurso', 'duracao_s', 'post_id')}
                   | {'metricas': ultimo.get(h.get('post_id') or '')})
    return out


def enviar(tipo, dados, guardar_data=True):
    corpo = {
        'tipo': tipo,
        'instagram': (cfg.get('INSTAGRAM_CONTA', '', obrigatorio=False) or '?').lstrip('@')[:60],
        'nome': (cfg.get('NOME_PESSOA', '', obrigatorio=False) or '')[:120],
        'dados': dados,
    }
    r = urllib.request.Request(URL, data=json.dumps(corpo, ensure_ascii=False, default=str).encode('utf-8'),
                               method='POST', headers={'apikey': CHAVE, 'Authorization': f'Bearer {CHAVE}',
                                                       'Content-Type': 'application/json',
                                                       'Prefer': 'return=minimal'})
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            ok = 200 <= x.status < 300
    except (urllib.error.URLError, TimeoutError) as e:
        print('registo: falhou o envio:', getattr(e, 'code', ''), str(e)[:200])
        return False
    if ok:
        ESTADO.parent.mkdir(parents=True, exist_ok=True)
        est = ler_json(ESTADO, {}) or {}
        if guardar_data:
            est['ultimo_envio'] = date.today().isoformat()
        est.setdefault('envios', []).append({'tipo': tipo, 'quando': datetime.now().isoformat(timespec='seconds')})
        ESTADO.write_text(json.dumps(est, indent=1), encoding='utf-8')
        print(f'registo: enviado ({tipo})')
    return ok


def texto_html(p):
    t = p.read_text(encoding='utf-8') if p.exists() else ''
    t = re.sub(r'(?is)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr)>', '\n', t)
    t = html_mod.unescape(re.sub(r'<[^>]+>', ' ', t))
    return re.sub(r'[ \t]+', ' ', re.sub(r'\n\s*\n+', '\n', t)).strip()[:60000]


PRIMEIRAS = ['tipo_video', 'data', 'quando', 'post_id', 'm_url', 'texto', 'texto_hook', 'texto_legenda', 'recurso',
             'molde', 'tipo_broll', 'duracao_s', 'm_views', 'm_reach', 'm_likes', 'm_comments', 'm_shares', 'm_saves',
             'm_follows', 'm_profileViews', 'm_igReelsAvgWatchTime', 'm_reelsSkipRate', 'm_completionRate',
             'm_replays', 'm_engagementRate', 'm_data_leitura']


def plano(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return v


def escrever_csv(caminho, linhas, primeiras=()):
    cols = [c for c in primeiras if any(c in l for l in linhas)]
    for l in linhas:
        cols += [k for k in l if k not in cols]
    with open(caminho, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for l in linhas:
            w.writerow({k: plano(v) for k, v in l.items()})
    return caminho


def gerar_csv(pasta):
    d = pathlib.Path(pasta)
    d = d if d.is_absolute() else RAIZ / d
    d.mkdir(parents=True, exist_ok=True)
    ultimo = ler_json(M / 'reels_ultimo.json', {}) or {}
    textos = {t.get('id'): t for t in (ler_json(RAIZ / 'banco' / 'textos.json', []) or [])}
    videos, origem = [], {}
    for tipo, f in (('trial_reel', RAIZ / 'fabrica' / 'historico.jsonl'),
                    ('talking_head', RAIZ / 'talking-head' / 'historico.jsonl')):
        for h in jsonl(f):
            l = {'tipo_video': tipo, **h}
            t = textos.get(h.get('texto')) if tipo == 'trial_reel' else None
            for k, v in (t or {}).items():
                if k != 'id':
                    l[f'texto_{k}'] = ' / '.join(v) if k == 'hook' and isinstance(v, list) else v
            for k, v in (ultimo.get(h.get('post_id') or '') or {}).items():
                if k != 'post_id':
                    l[f'm_{k}'] = v
            videos.append(l)
            if h.get('post_id'):
                origem[h['post_id']] = (tipo, l.get('texto_hook') or h.get('hook') or h.get('texto'))
    leituras = []
    for f in sorted((M / 'reels').glob('20*.jsonl')):
        for r in jsonl(f):
            tipo, hook = origem.get(r.get('post_id'), ('?', None))
            leituras.append({'tipo_video': tipo, 'hook': hook, **r})
    a = escrever_csv(d / 'videos.csv', videos, PRIMEIRAS)
    b = escrever_csv(d / 'leituras.csv', leituras, ['data_leitura', 'tipo_video', 'post_id', 'hook', 'url', 'views'])
    print(f'csv: {len(videos)} vídeos → {a.relative_to(RAIZ) if a.is_relative_to(RAIZ) else a}; '
          f'{len(leituras)} leituras → {b.name}')
    return a, b


def relatorio(pasta):
    d = pathlib.Path(pasta)
    d = d if d.is_absolute() else RAIZ / d
    pdf = d / 'relatorio.pdf'
    gerar_csv(d)
    dados = {'ciclo': d.name, 'analise': ler_json(d / 'analise.json'), 'relatorio_texto': texto_html(d / 'relatorio.html'),
             'videos_csv': (d / 'videos.csv').read_text(encoding='utf-8-sig'),
             'leituras_csv': (d / 'leituras.csv').read_text(encoding='utf-8-sig')}
    if pdf.exists() and pdf.stat().st_size < 1_200_000:
        dados['relatorio_pdf_base64'] = base64.b64encode(pdf.read_bytes()).decode()
    return enviar('relatorio', dados, guardar_data=False)


def aceitou():
    return cfg.get('REGISTO_AGENS', 'nao', obrigatorio=False) == 'sim'


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'estado'
    if cmd == 'estado':
        print(json.dumps({'aceitou': aceitou(), **(ler_json(ESTADO, {}) or {})}, indent=1))
        return
    if cmd == 'csv':
        gerar_csv(sys.argv[2])
        return
    if not aceitou():
        print('registo: a pessoa não aceitou (REGISTO_AGENS != sim); nada enviado')
        return
    if cmd == 'inicio':
        ok = enviar('inicio', {'perfil': perfil_recente(), 'publicacoes': publicacoes()})
        sys.exit(0 if ok else 1)
    if cmd == 'relatorio':
        sys.exit(0 if relatorio(sys.argv[2]) else 1)
    if cmd == 'ciclo':
        ult = (ler_json(ESTADO, {}) or {}).get('ultimo_envio')
        if ult and (date.today() - date.fromisoformat(ult)).days < CICLO_DIAS:
            return
        if not ult:                       # o início ainda não foi: não há ponto de partida
            return
        py = cfg.PY if pathlib.Path(cfg.PY).exists() else sys.executable
        for c in ('tudo', 'publicacoes'):
            subprocess.run([str(py), str(M / 'recolher.py'), c], cwd=RAIZ, capture_output=True, timeout=1800)
        enviar('ciclo', {'perfil': perfil_recente(), 'reels_fabrica': reels_fabrica(),
                         'talking_heads': talking_heads(), 'publicacoes': publicacoes()})


if __name__ == '__main__':
    main()
