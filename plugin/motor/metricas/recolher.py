"""Recolhe métricas do Zernio (sem IA).

  perfil  Fotografia do perfil: seguidores, crescimento, histórico diário de seguidores e os totais da conta
          nos últimos 30 dias (visualizações, alcance, visitas ao perfil, contas que interagiram, interações).
          Grava metricas/perfil/AAAA-MM-DD.json. A primeira fotografia é o ponto de partida (linha de base).
  reels   Métricas de cada trial reel do histórico da fábrica (views, alcance, guardados, partilhas, comentários,
          gostos, skip rate, tempo médio de visualização…). Grava a leitura do dia em
          metricas/reels/AAAA-MM-DD.jsonl e a última leitura de cada reel em metricas/reels_ultimo.json.

  publicacoes  Últimas 50 publicações da conta com legenda e números (metricas/perfil/publicacoes.json).

Uso: $PY metricas/recolher.py perfil|reels|tudo|publicacoes
"""
import json
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
M = RAIZ / 'metricas'
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402
import zernio_posts as z  # noqa: E402

CONTA = cfg.get('ZERNIO_ACCOUNT_ID')


def get(caminho):
    r = urllib.request.Request(z.BASE + caminho, headers={'Authorization': z.chave()})
    try:
        with urllib.request.urlopen(r, timeout=90) as x:
            return json.load(x)
    except urllib.error.HTTPError as e:
        return {'erro': e.code, 'mensagem': e.read().decode()[:300]}


def perfil():
    hoje = date.today()
    seg = get(f'/accounts/follower-stats?accountIds={CONTA}&fromDate={hoje - timedelta(days=365)}&toDate={hoje}')
    conta = (seg.get('accounts') or [{}])[0]
    ins = get(f'/analytics/instagram/account-insights?accountId={CONTA}'
              '&metrics=reach,views,profile_views,accounts_engaged,total_interactions,follows_and_unfollows')
    foto = {
        'data': hoje.isoformat(),
        'seguidores': conta.get('currentFollowers'),
        'crescimento_seguidores': conta.get('growth'),
        'a_seguir': (conta.get('accountStats') or {}).get('followsCount'),
        'publicacoes': (conta.get('accountStats') or {}).get('mediaCount'),
        'ultimos_30_dias': {k: v.get('total') for k, v in (ins.get('metrics') or {}).items()},
        'periodo_30_dias': ins.get('dateRange'),
        'historico_seguidores': (seg.get('stats') or {}).get(CONTA, []),
        'aviso': ins.get('dataDelay'),
    }
    (M / 'perfil').mkdir(parents=True, exist_ok=True)
    f = M / 'perfil' / f'{hoje}.json'
    f.write_text(json.dumps(foto, ensure_ascii=False, indent=1))
    print('perfil:', f.relative_to(RAIZ), foto['seguidores'], 'seguidores ·', foto['ultimos_30_dias'])


def reels():
    hist = [json.loads(l) for l in (RAIZ / 'fabrica/historico.jsonl').read_text().splitlines() if l.strip()]
    ultimo_f = M / 'reels_ultimo.json'
    ultimo = json.loads(ultimo_f.read_text()) if ultimo_f.exists() else {}
    hoje = date.today()
    (M / 'reels').mkdir(parents=True, exist_ok=True)
    n = 0
    with (M / 'reels' / f'{hoje}.jsonl').open('a') as fh:
        for h in hist:
            if not h.get('post_id'):
                continue
            d = get(f"/analytics?postId={h['post_id']}")
            if d.get('status') != 'published':
                continue
            a = d.get('analytics') or {}
            leitura = {'data_leitura': hoje.isoformat(), 'post_id': h['post_id'], 'publicado': d.get('publishedAt'),
                       'url': a.get('platformPostUrl'), **{k: a.get(k) for k in (
                           'views', 'reach', 'impressions', 'likes', 'comments', 'shares', 'saves', 'follows',
                           'profileViews', 'igReelsAvgWatchTime', 'igReelsVideoViewTotalTime', 'reelsSkipRate',
                           'completionRate', 'replays', 'engagementRate', 'lastUpdated')}}
            fh.write(json.dumps(leitura, ensure_ascii=False) + '\n')
            ultimo[h['post_id']] = leitura
            n += 1
    ultimo_f.write_text(json.dumps(ultimo, ensure_ascii=False, indent=1))
    print(f'reels: {n} lidos')


def publicacoes(n=50):
    """Últimas publicações da conta (também as que não saíram pela Zernio), com legenda e números.
    Grava metricas/perfil/publicacoes.json — é o que o /comecar lê para estudar o perfil."""
    r = get(f'/analytics?platform=instagram&accountId={CONTA}&limit={n}')
    out = M / 'perfil' / 'publicacoes.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    print('publicações:', len(r.get('posts', [])), '→', out)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if cmd == 'publicacoes':
        publicacoes()
    if cmd in ('perfil', 'tudo'):
        perfil()
    if cmd in ('reels', 'tudo'):
        reels()
