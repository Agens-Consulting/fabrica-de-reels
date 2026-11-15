"""Envia à Agens os números do Instagram para o caso de estudo da fase gratuita (sem IA).

  inicio  Ponto de partida, no fim do passo 5 do /comecar: fotografia do perfil + últimas 50 publicações.
  ciclo   De 14 em 14 dias (chamado pela tarefa automática; sai logo se ainda não passaram 14 dias):
          fotografia do perfil + métricas de cada trial reel da fábrica e de cada talking head
          + últimas 50 publicações.
  estado  Mostra quando foi o último envio.

Só envia se REGISTO_AGENS=sim no .env (a pessoa aceitou no /comecar).
Vai só o que está aqui: números do Instagram, o @ e o nome. Nunca chaves, nunca o .env.
A tabela só aceita escritas: ninguém consegue ler os números de outra pessoa com esta chave.
"""
import json
import pathlib
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


def enviar(tipo, dados):
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
        est['ultimo_envio'] = date.today().isoformat()
        est.setdefault('envios', []).append({'tipo': tipo, 'quando': datetime.now().isoformat(timespec='seconds')})
        ESTADO.write_text(json.dumps(est, indent=1), encoding='utf-8')
        print(f'registo: enviado ({tipo})')
    return ok


def aceitou():
    return cfg.get('REGISTO_AGENS', 'nao', obrigatorio=False) == 'sim'


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'estado'
    if cmd == 'estado':
        print(json.dumps({'aceitou': aceitou(), **(ler_json(ESTADO, {}) or {})}, indent=1))
        return
    if not aceitou():
        print('registo: a pessoa não aceitou (REGISTO_AGENS != sim); nada enviado')
        return
    if cmd == 'inicio':
        ok = enviar('inicio', {'perfil': perfil_recente(), 'publicacoes': publicacoes()})
        sys.exit(0 if ok else 1)
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
