"""Análise de um ciclo de 14 dias dos trial reels (Python puro, sem IA).

Lê o histórico da fábrica, o banco de textos e as métricas recolhidas por recolher.py, e escreve:
  metricas/ciclos/AAAA-MM-DD/analise.json   números do ciclo (perfil, reels, famílias, textos, B-rolls, músicas,
                                             recursos, volume e horários)
  metricas/ciclos/AAAA-MM-DD/relatorio.html relatório autónomo com a estética da marca do .env
  metricas/ciclos/AAAA-MM-DD/relatorio.pdf  só com --pdf (Chromium do Playwright)

O ciclo são os 14 dias que acabam em --ate (inclusive). Como só se analisa um reel 7 dias depois de sair,
os reels analisados são os que fizeram 7 dias dentro do ciclo, ou seja, os publicados entre 7 e 20 dias antes
de --ate. Assim cada reel entra num ciclo e só num. Os reels publicados nos últimos 7 dias contam para o
volume e para a soma das views, mas não para as famílias (ficam para o ciclo seguinte).

Uso:
  PY=.venv/bin/python   # o ambiente do projeto
  $PY metricas/analisar.py                       # ciclo que acaba hoje
  $PY metricas/analisar.py --ate 2026-11-28 --pdf
  $PY metricas/analisar.py --raiz /outra/pasta    # para testar com dados de ensaio
"""
import argparse
import base64
import html
import json
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

RAIZ_PROJETO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO / 'ferramentas'))
import config as cfg  # noqa: E402
CONTA_IG = cfg.conta()
MARCA_COR = cfg.get('MARCA_COR_PRINCIPAL', '#1F3A5F', obrigatorio=False)
MARCA_COR_ESCURO = cfg.get('MARCA_COR_SECUNDARIA', '#7FA7D9', obrigatorio=False)
MARCA_LETRA = cfg.get('MARCA_LETRA_TEXTO', 'Plus Jakarta Sans', obrigatorio=False)
NOME = cfg.get('NOME_PESSOA', '', obrigatorio=False)

DIAS_CICLO = 14
DIAS_MATURO = 7
MIN_SAIDAS = 3
DESTAQUE_MIN = 1.05   # índice mínimo para uma família ser realçada no relatório

MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro',
         'novembro', 'dezembro']
MESES_C = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.']
DIAS_SEMANA = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']

# taxas por 1000 contas alcançadas: chave interna -> (campo do Zernio, rótulo)
TAXAS = {
    'guardados': ('saves', 'Guardados'),
    'partilhas': ('shares', 'Partilhas'),
    'comentarios': ('comments', 'Comentários'),
    'gostos': ('likes', 'Gostos'),
    'visitas_perfil': ('profileViews', 'Visitas ao perfil'),
    'seguidores': ('follows', 'Seguidores novos'),
}
# o índice de uma família compara-a com a média do ciclo nestas quatro métricas (1,0 = na média)
INDICE = ['views', 'guardados', 'partilhas', 'comentarios']

VARIAVEIS = [  # chave, rótulo
    ('molde', 'Molde do hook'),
    ('gancho', 'Gancho da lista (guia 2)'),
    ('guia', 'Versão do guia de hooks'),
    ('recurso', 'Recurso (tema)'),
    ('caixa', 'Caixa do hook'),
    ('fim', 'Fim do hook'),
    ('segundo', 'Texto do segundo hook'),
    ('duracao_alvo', 'Duração'),
    ('musica', 'Música'),
    ('trecho', 'Trecho da música'),
    ('broll', 'B-roll'),
    ('tipo_broll', 'Tipo de B-roll'),
    ('cor_destaque', 'Cor de destaque'),
    ('faixa', 'Faixa horária'),
    ('dia_semana', 'Dia da semana'),
    ('volume_dia', 'Volume do dia'),
    ('bandeira', 'Bandeira 🇵🇹 no hook'),
    ('numero', 'Número no hook'),
    ('linhas', 'Linhas do hook'),
    ('origem', 'Origem do texto'),
]
NOMES_VALOR = {
    'caixa': {'maiusculas': 'TUDO EM MAIÚSCULAS', 'frase': 'Só a primeira', 'minusculas': 'minúsculas'},
    'fim': {'nada': 'Nada por baixo', 'segundo_0': 'Segundo hook desde 0 s', 'segundo_3': 'Segundo hook aos 3 s'},
    'molde': {'lista': 'Lista', 'pov': 'POV', 'condicao': 'Condição'},
}


# ---------------------------------------------------------------------------------------------- leitura

def ler_json(p, defeito=None):
    try:
        return json.loads(pathlib.Path(p).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return defeito


def ler_jsonl(p):
    try:
        return [json.loads(l) for l in pathlib.Path(p).read_text().splitlines() if l.strip()]
    except FileNotFoundError:
        return []


def data_de(txt):
    return date.fromisoformat(str(txt)[:10]) if txt else None


def leituras_ate(m, ate):
    """Última leitura de cada reel com data_leitura <= ate (série diária; reels_ultimo como reserva)."""
    out = {}
    for f in sorted((m / 'reels').glob('*.jsonl')):
        if data_de(f.stem) and data_de(f.stem) > ate:
            continue
        for l in ler_jsonl(f):
            if data_de(l.get('data_leitura')) and data_de(l['data_leitura']) <= ate:
                out[l['post_id']] = l
    for pid, l in (ler_json(m / 'reels_ultimo.json', {}) or {}).items():
        if pid not in out and data_de(l.get('data_leitura')) and data_de(l['data_leitura']) <= ate:
            out[pid] = l
    return out


def perfil_ate(m, ate):
    fs = [f for f in (m / 'perfil').glob('????-??-??.json') if data_de(f.stem) <= ate]
    return ler_json(max(fs), {}) if fs else {}


def seguidores_em(perfil, dia):
    """Seguidores no fim do dia `dia` (ou no último dia antes, se faltar)."""
    hs = sorted((h for h in perfil.get('historico_seguidores') or [] if h.get('date')), key=lambda h: h['date'])
    val = None
    for h in hs:
        if data_de(h['date']) <= dia:
            val = h['followers']
    return val


# ---------------------------------------------------------------------------------------------- contas

def media(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def mediana(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def r(x, casas=2):
    return None if x is None else round(x, casas)


def por_mil(v, alcance):
    if v is None or not alcance:
        return None
    return v * 1000 / alcance


def pct(x):
    """O Zernio pode devolver taxas como fração (0-1) ou percentagem (0-100); normaliza para percentagem."""
    if x is None:
        return None
    return x * 100 if 0 < x <= 1 else x


def faixa_horaria(quando):
    if not quando:
        return None
    t = datetime.fromisoformat(quando[:19])
    h = t.hour + t.minute / 60
    if 9 <= h < 12:
        return 'Manhã (9h-12h)'
    if 12 <= h < 14:
        return 'Almoço (12h-14h)'
    if 14 <= h < 17:
        return 'Tarde (14h-17h)'
    if 17 <= h <= 20.5:
        return 'Fim de tarde (17h-20h30)'
    return 'Fora da janela'


def nome_ficheiro(caminho):
    """videos/raw/1eh1F0HI_IMG_7502.MOV -> IMG_7502; audios/raw/1wEb_3vf_Hier_encore.mp3 -> Hier encore."""
    if not caminho:
        return None
    s = pathlib.Path(caminho).stem
    s = re.sub(r'^[A-Za-z0-9_-]{8}_', '', s, count=1)
    return s.replace('_', ' ') if pathlib.Path(caminho).suffix.lower() in ('.mp3', '.wav', '.m4a', '.aac') else s


# ---------------------------------------------------------------------------------------------- reel a reel

def montar_reel(h, leit, textos, volume_por_dia, ate):
    t = textos.get(h.get('texto')) or {}
    hook = t.get('hook') or h.get('hook_render') or []
    hv = h.get('hook_variaveis') or {}
    pub = data_de((leit or {}).get('publicado')) or data_de(h.get('quando')) or data_de(h.get('data'))
    leitura = data_de((leit or {}).get('data_leitura'))
    dur = h.get('duracao_s')
    trecho = h.get('musica_trecho_s') or ([h['inicio_musica'], round(h['inicio_musica'] + (dur or 0), 2)]
                                         if h.get('inicio_musica') is not None else None)
    m = leit or {}
    alcance = m.get('reach')
    watch_s = m['igReelsAvgWatchTime'] / 1000 if m.get('igReelsAvgWatchTime') is not None else None
    taxas = {k: r(por_mil(m.get(campo), alcance)) for k, (campo, _) in TAXAS.items()}
    quando = h.get('quando') or ''
    dia = data_de(h.get('data')) or pub
    balde = int(trecho[0] // 20) * 20 if trecho else None
    fam = {
        'molde': h.get('molde') or t.get('molde'),
        'gancho': t.get('gancho'),
        'guia': f"guia {t.get('guia', 1)}",
        'recurso': h.get('recurso') or t.get('recurso'),
        'caixa': hv.get('caixa'),
        'fim': hv.get('fim'),
        'segundo': (hv.get('segundo') or 'Sem segundo hook') if hv else None,
        'duracao_alvo': f"{h['duracao_alvo']:g} s" if h.get('duracao_alvo') else None,
        'musica': nome_ficheiro(h.get('musica')),
        'trecho': f'{balde}-{balde + 20} s' if balde is not None else None,
        'broll': nome_ficheiro(h.get('broll')),
        'tipo_broll': h.get('tipo_broll'),
        'cor_destaque': h.get('cor_destaque'),
        'faixa': faixa_horaria(quando),
        'dia_semana': DIAS_SEMANA[dia.weekday()] if dia else None,
        'volume_dia': f"{volume_por_dia.get(h.get('data'), 0)} por dia",
        'bandeira': 'Com 🇵🇹' if any('🇵🇹' in l for l in hook) else 'Sem 🇵🇹',
        'numero': 'Com número' if any(re.search(r'\d', l) for l in hook) else 'Sem número',
        'linhas': f'{len(hook)} linha' + ('s' if len(hook) != 1 else '') if hook else None,
        'origem': ('Reescrito' if str(t.get('origem', '')).startswith('reescrito') else 'Novo') if t else None,
    }
    return {
        'post_id': h.get('post_id'),
        'texto': h.get('texto'),
        'hook': ' '.join(hook),
        'recurso': fam['recurso'],
        'url': m.get('url'),
        'quando': quando or None,
        'publicado': pub.isoformat() if pub else None,
        'data_leitura': leitura.isoformat() if leitura else None,
        'idade_dias': (leitura - pub).days if (leitura and pub) else None,
        'maduro': bool(leitura and pub and (leitura - pub).days >= DIAS_MATURO),
        'musica_trecho_s': trecho,
        'duracao_s': dur,
        'views': m.get('views'),
        'alcance': alcance,
        'guardados': m.get('saves'),
        'partilhas': m.get('shares'),
        'comentarios': m.get('comments'),
        'gostos': m.get('likes'),
        'visitas_perfil': m.get('profileViews'),
        'seguidores': m.get('follows'),
        'replays': m.get('replays'),
        'taxas_por_1000': taxas,
        'skip_rate_pct': r(pct(m.get('reelsSkipRate')), 1),
        'conclusao_pct': r(pct(m.get('completionRate')), 1),
        'tempo_medio_s': r(watch_s, 2),
        'tempo_sobre_duracao': r(watch_s / dur, 2) if (watch_s is not None and dur) else None,
        'familias': fam,
    }


def agregar(reels):
    out = {
        'n': len(reels),
        'views_media': r(media([x['views'] for x in reels]), 1),
        'views_mediana': r(mediana([x['views'] for x in reels]), 1),
        'alcance_medio': r(media([x['alcance'] for x in reels]), 1),
        'skip_medio_pct': r(media([x['skip_rate_pct'] for x in reels]), 1),
        'tempo_sobre_duracao_medio': r(media([x['tempo_sobre_duracao'] for x in reels]), 2),
        'taxas': {},
    }
    for k in TAXAS:
        vals = [x['taxas_por_1000'][k] for x in reels]
        out['taxas'][k] = {'media': r(media(vals)), 'mediana': r(mediana(vals))}
    if len(reels) < MIN_SAIDAS:
        out['poucos_dados'] = True
    return out


def valor_ref(ag, k):
    return ag['views_media'] if k == 'views' else ag['taxas'][k]['media']


def indice(ag, ref):
    rs = []
    for k in INDICE:
        a, b = valor_ref(ag, k), valor_ref(ref, k)
        if a is not None and b:
            rs.append(a / b)
    return r(media(rs), 2)


def sugestao(ag, ref):
    if ag['n'] < MIN_SAIDAS:
        return 'poucos dados'
    v, rv = ag['views_media'], ref.get('views_media')
    g, rg = ag['taxas']['guardados']['media'], ref['taxas']['guardados']['media']
    c, rc = ag['taxas']['comentarios']['media'], ref['taxas']['comentarios']['media']
    if None in (v, rv):
        return 'a testar'
    acima_gc = (g is not None and rg is not None and g > rg) or (c is not None and rc is not None and c > rc)
    abaixo_gc = (g is None or rg is None or g < rg) and (c is None or rc is None or c < rc)
    if v > rv and acima_gc:
        return 'vencedor'
    if v < rv and abaixo_gc:
        return 'retirado'
    return 'a testar'


def agrupar(reels, chave):
    g = defaultdict(list)
    for x in reels:
        v = chave(x)
        if v is not None:
            g[v].append(x)
    return g


# ---------------------------------------------------------------------------------------------- análise

def analisar(raiz, ate):
    m = raiz / 'metricas'
    ini = ate - timedelta(days=DIAS_CICLO - 1)
    jan_ini, jan_fim = ate - timedelta(days=DIAS_CICLO + DIAS_MATURO - 1), ate - timedelta(days=DIAS_MATURO)
    hist = [h for h in ler_jsonl(raiz / 'fabrica/historico.jsonl') if h.get('post_id')]
    textos = {t['id']: t for t in (ler_json(raiz / 'banco/textos.json', []) or [])}
    leit = leituras_ate(m, ate)
    vol = defaultdict(int)
    for h in hist:
        vol[h.get('data')] += 1
    todos = [montar_reel(h, leit.get(h['post_id']), textos, vol, ate) for h in hist if data_de(h.get('data')) <= ate]

    def no(x, a, b):
        d = data_de(x['publicado'])
        return d is not None and a <= d <= b

    do_ciclo = [x for x in todos if no(x, ini, ate)]
    candidatos = [x for x in todos if no(x, jan_ini, jan_fim)]
    analisados = [x for x in candidatos if x['maduro'] and x['alcance'] is not None]

    # referência para vencedor/retirado: a média do ciclo anterior, se já houver; senão a deste
    ant = ler_json(m / 'ciclos' / (ate - timedelta(days=DIAS_CICLO)).isoformat() / 'analise.json')
    ciclo_med = agregar(analisados)
    if ant and (ant.get('medias_ciclo') or {}).get('n', 0) >= MIN_SAIDAS:
        ref, ref_txt = ant['medias_ciclo'], f"média do ciclo anterior (até {ant['ciclo']['ate']})"
    else:
        ref, ref_txt = ciclo_med, 'média deste ciclo (ainda não há ciclo anterior com dados)'

    # --- perfil
    p_fim = perfil_ate(m, ate)
    base = ler_json(m / 'perfil/linha-de-base.json', {}) or {}
    s_ini = seguidores_em(p_fim, ini - timedelta(days=1))
    s_fim = seguidores_em(p_fim, ate) or p_fim.get('seguidores')
    u30, b30 = p_fim.get('ultimos_30_dias') or {}, base.get('ultimos_30_dias') or {}
    per30 = p_fim.get('periodo_30_dias') or {}
    a30 = data_de(per30.get('since')) or (ate - timedelta(days=30))
    z30 = data_de(per30.get('until')) or ate
    reels_30 = [x for x in todos if no(x, a30, z30)]
    views_reels_30 = sum(x['views'] or 0 for x in reels_30)
    views_ciclo = sum(x['views'] or 0 for x in do_ciclo)

    def dif(a, b):
        return None if a is None or b is None else a - b

    def var_pct(a, b):
        return r((a - b) * 100 / b, 1) if (a is not None and b) else None

    perfil = {
        'data_fotografia': p_fim.get('data'),
        'linha_de_base': base.get('data'),
        'seguidores_inicio': s_ini,
        'seguidores_fim': s_fim,
        'seguidores_ganhos_ciclo': dif(s_fim, s_ini),
        'seguidores_linha_de_base': base.get('seguidores'),
        'seguidores_vs_linha_de_base': dif(s_fim, base.get('seguidores')),
        'views_30_dias': u30.get('views'),
        'views_30_dias_linha_de_base': b30.get('views'),
        'views_30_dias_variacao_pct': var_pct(u30.get('views'), b30.get('views')),
        'alcance_30_dias': u30.get('reach'),
        'alcance_30_dias_linha_de_base': b30.get('reach'),
        'alcance_30_dias_variacao_pct': var_pct(u30.get('reach'), b30.get('reach')),
        'visitas_perfil_30_dias': u30.get('profile_views'),
        'visitas_perfil_30_dias_linha_de_base': b30.get('profile_views'),
        'views_trial_reels_ciclo': views_ciclo,
        'views_trial_reels_janela_30_dias': views_reels_30,
        'fracao_views_conta_pct': r(views_reels_30 * 100 / u30['views'], 1) if u30.get('views') else None,
        'fracao_explicacao': (
            f"Soma das views (última leitura até {data_longa(ate)}) "
            f"{'do único trial reel publicado' if len(reels_30) == 1 else f'dos {len(reels_30)} trial reels publicados'} "
            f"entre {data_curta(a30)} e {data_curta(z30)}, a dividir pelas views da conta nesses mesmos 30 dias "
            f"(account-insights do Zernio). É uma estimativa: as views de cada reel são acumuladas até ao dia da "
            f"leitura (podem incluir dias depois da janela), o Instagram pode atrasar até 48 h, e não está "
            f"confirmado que as views dos trial reels (mostrados a quem não segue) entram no total da conta. "
            f"Acima de 100 % quer dizer que não entram, ou não entram todas."),
    }

    # --- famílias
    familias = {}
    for k, rot in VARIAVEIS:
        grupos = agrupar(analisados, lambda x, k=k: x['familias'].get(k))
        linhas = []
        for v, xs in grupos.items():
            ag = agregar(xs)
            ag['valor'] = NOMES_VALOR.get(k, {}).get(v, v)
            ag['indice'] = indice(ag, ciclo_med)
            linhas.append(ag)
        linhas.sort(key=lambda a: (a.get('poucos_dados', False), -(a['indice'] or 0), -a['n']))
        familias[k] = {'rotulo': rot, 'valores': linhas}

    ranking = [{'variavel': k, 'rotulo': familias[k]['rotulo'], 'valor': a['valor'], 'n': a['n'],
                'indice': a['indice'], 'views_media': a['views_media'],
                'guardados': a['taxas']['guardados']['media'], 'comentarios': a['taxas']['comentarios']['media'],
                'partilhas': a['taxas']['partilhas']['media']}
               for k in familias for a in familias[k]['valores']
               if not a.get('poucos_dados') and a['indice'] is not None and len(familias[k]['valores']) > 1]
    ganham = sorted([x for x in ranking if x['indice'] > 1], key=lambda x: -x['indice'])
    perdem = sorted([x for x in ranking if x['indice'] < 1], key=lambda x: x['indice'])

    # --- textos, B-rolls, trechos de música
    def tabela(chave, extra=None):
        out = []
        for v, xs in agrupar(analisados, chave).items():
            ag = agregar(xs)
            ag['id'] = v
            ag['sugestao'] = sugestao(ag, ref)
            if extra:
                ag.update(extra(v, xs))
            out.append(ag)
        ordem = {'vencedor': 0, 'a testar': 1, 'retirado': 2, 'poucos dados': 3}
        out.sort(key=lambda a: (ordem[a['sugestao']], -(a['views_media'] or 0)))
        return out

    tx = tabela(lambda x: x['texto'], lambda v, xs: {
        'hook': xs[0]['hook'], 'recurso': xs[0]['recurso'], 'molde': xs[0]['familias']['molde'],
        'estado_no_banco': (textos.get(v) or {}).get('estado')})
    br = tabela(lambda x: x['familias']['broll'], lambda v, xs: {'tipo': xs[0]['familias']['tipo_broll']})
    tr = tabela(lambda x: (f"{x['familias']['musica']} · {x['familias']['trecho']}"
                           if x['familias']['musica'] and x['familias']['trecho'] else None),
                lambda v, xs: {'musica': xs[0]['familias']['musica'], 'trecho': xs[0]['familias']['trecho']})
    mus = tabela(lambda x: x['familias']['musica'])

    # --- recursos: comentários por 1000 views
    recs = []
    for v, xs in agrupar(analisados, lambda x: x['recurso']).items():
        cv = sum(x['comentarios'] or 0 for x in xs)
        vv = sum(x['views'] or 0 for x in xs)
        recs.append({'recurso': v, 'n': len(xs), 'views': vv, 'comentarios': cv,
                     'comentarios_por_1000_views': r(cv * 1000 / vv) if vv else None,
                     'poucos_dados': len(xs) < MIN_SAIDAS})
    recs.sort(key=lambda a: -(a['comentarios_por_1000_views'] or 0))
    for i, a in enumerate(recs):
        a['regra'] = ('fica' if i < 3 else 'sai' if i >= len(recs) - 2 else '—') if len(recs) >= 5 else '—'

    # --- volume e horários
    dias = []
    for i in range(DIAS_CICLO):
        d = ini + timedelta(days=i)
        xs = [x for x in do_ciclo if x['publicado'] == d.isoformat()]
        al = [x['alcance'] for x in xs if x['alcance'] is not None]
        dias.append({'data': d.isoformat(), 'reels': len(xs), 'alcance_total': sum(al) if al else None,
                     'views_total': sum(x['views'] or 0 for x in xs) if xs else None,
                     'alcance_por_reel': r(sum(al) / len(al), 1) if al else None,
                     'todos_maduros': bool(xs) and all(x['maduro'] for x in xs)})
    por_volume = []
    for v, xs in sorted(agrupar([x for x in todos if x['maduro'] and x['alcance'] is not None],
                                lambda x: vol.get(x['publicado'])).items(), key=lambda kv: kv[0] or 0):
        ndias = len({x['publicado'] for x in xs})
        por_volume.append({'reels_por_dia': v, 'dias': ndias, 'reels': len(xs),
                           'alcance_medio_por_reel': r(media([x['alcance'] for x in xs]), 1),
                           'alcance_total_medio_por_dia': r(sum(x['alcance'] for x in xs) / ndias, 1)})

    return {
        'gerado': datetime.now().isoformat(timespec='seconds'),
        'ciclo': {'inicio': ini.isoformat(), 'ate': ate.isoformat(), 'dias': DIAS_CICLO,
                  'reels_publicados': len(do_ciclo),
                  'janela_analise': [jan_ini.isoformat(), jan_fim.isoformat()],
                  'reels_na_janela': len(candidatos), 'reels_analisados': len(analisados),
                  'nota': (f'Reels analisados = publicados entre {data_curta(jan_ini)} e {data_curta(jan_fim)} '
                           f'(fizeram {DIAS_MATURO} dias dentro do ciclo) com leitura de pelo menos '
                           f'{DIAS_MATURO} dias. Taxas por 1000 contas alcançadas.')},
        'referencia_vencedor': ref_txt,
        'regras': {'maduro_dias': DIAS_MATURO, 'min_saidas': MIN_SAIDAS,
                   'indice': 'média de (família ÷ média do ciclo) em views, guardados, partilhas e comentários '
                             'por 1000 de alcance; 1,0 = na média',
                   'vencedor': 'acima da referência em views e em guardados ou comentários por 1000',
                   'retirado': 'abaixo da referência em views e em guardados e comentários por 1000',
                   'recursos': 'comentários por 1000 views; ficam os 3 melhores, saem os 2 piores'},
        'perfil': perfil,
        'medias_ciclo': ciclo_med,
        'reels': analisados,
        'reels_a_amadurecer': [{'post_id': x['post_id'], 'texto': x['texto'], 'publicado': x['publicado'],
                                'idade_dias': x['idade_dias']} for x in todos
                               if no(x, jan_ini, ate) and not x['maduro']],
        'familias': familias,
        'familias_ganham': ganham,
        'familias_perdem': perdem,
        'textos': tx,
        'brolls': br,
        'musicas': mus,
        'trechos_musica': tr,
        'recursos': recs,
        'volume': {'por_dia': dias, 'por_volume': por_volume},
    }


# ---------------------------------------------------------------------------------------------- formatação

def fn(x, casas=0, vazio='—'):
    """2000 -> '2 000'; 1.25 -> '1,3' (casas=1). Espaço fixo como separador de milhares."""
    if x is None:
        return vazio
    s = f'{x:,.{casas}f}'.replace(',', ' ').replace('.', ',').replace(' ', ' ')
    return s


def fsinal(x, casas=0):
    if x is None:
        return '—'
    return ('+' if x > 0 else '−' if x < 0 else '') + fn(abs(x), casas)


def data_longa(s):
    d = data_de(s)
    return f'{d.day} de {MESES[d.month - 1]} de {d.year}' if d else '—'


def data_curta(s):
    d = data_de(s)
    return f'{d.day} {MESES_C[d.month - 1]}' if d else '—'


def periodo(a, b):
    a, b = data_de(a), data_de(b)
    if a.year != b.year:
        return f'{data_longa(a)} a {data_longa(b)}'
    if a.month != b.month:
        return f'{a.day} de {MESES[a.month - 1]} a {b.day} de {MESES[b.month - 1]} de {b.year}'
    return f'{a.day} a {b.day} de {MESES[b.month - 1]} de {b.year}'


e = html.escape


def plural(n, um, varios):
    return f'{fn(n)} {um if n == 1 else varios}'


# ---------------------------------------------------------------------------------------------- HTML

CSS = r"""
:root{--marca:__MARCA__;--marca-escuro:__MARCA2__;--fundo:#F3F1F1;--superficie:#FFFFFF;--superficie-2:#F8F7F7;--recesso:#ECE9E9;--recesso-forte:#E2DEDF;--tinta:#1C1719;--texto-2:#6B6264;--texto-3:#9C9395;--linha:rgba(28,23,25,.07);--linha-forte:rgba(28,23,25,.12);--sobre-tinta:#FFFFFF;--acento:var(--marca);--acento-texto:var(--marca);--acento-suave:color-mix(in oklab,var(--marca) 8%,transparent);--acento-medio:color-mix(in oklab,var(--marca) 16%,transparent);--acento-brilho:color-mix(in oklab,var(--marca) 22%,transparent);--ok:#2F7A4D;--aviso:#9A5B00;--erro:#B3261E;--vidro:rgba(255,255,255,.7);--vidro-borda:rgba(255,255,255,.6);--luz-topo:inset 0 1px 0 rgba(255,255,255,.9);--sombra-1:0 1px 2px rgba(28,23,25,.04),0 6px 20px rgba(28,23,25,.04);--sombra-2:0 2px 6px rgba(28,23,25,.05),0 18px 48px rgba(28,23,25,.08);--letra:"__LETRA__","Plus Jakarta Sans",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;--t-ecra:30px;--t-numero:34px;--t-secao:16px;--t-corpo:14px;--t-pequeno:12.5px;--t-rotulo:11.5px;--e1:4px;--e2:8px;--e3:12px;--e4:16px;--e5:20px;--e6:24px;--e8:32px;--e10:40px;--r-superficie:24px;--r-cartao:18px;--r-interior:14px;--capsula:999px;--mola:cubic-bezier(.32,.72,0,1);color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fundo:#0E0C0D;--superficie:#171415;--superficie-2:#1D191B;--recesso:#221E20;--recesso-forte:#2B2629;--tinta:#F2EDEE;--texto-2:#A69C9F;--texto-3:#6F6669;--linha:rgba(255,236,240,.07);--linha-forte:rgba(255,236,240,.12);--sobre-tinta:#141112;--acento:var(--marca-escuro);--acento-texto:var(--marca-escuro);--acento-suave:color-mix(in oklab,var(--marca-escuro) 12%,transparent);--acento-medio:color-mix(in oklab,var(--marca-escuro) 22%,transparent);--acento-brilho:color-mix(in oklab,var(--marca-escuro) 40%,transparent);--ok:#6CC290;--aviso:#E0A350;--erro:#F08A80;--vidro:rgba(23,20,21,.66);--vidro-borda:rgba(255,236,240,.08);--luz-topo:inset 0 1px 0 rgba(255,236,240,.06);--sombra-1:0 1px 2px rgba(0,0,0,.3);--sombra-2:0 2px 8px rgba(0,0,0,.35),0 24px 60px rgba(0,0,0,.45);color-scheme:dark}}
:root[data-theme="dark"]{--fundo:#0E0C0D;--superficie:#171415;--superficie-2:#1D191B;--recesso:#221E20;--recesso-forte:#2B2629;--tinta:#F2EDEE;--texto-2:#A69C9F;--texto-3:#6F6669;--linha:rgba(255,236,240,.07);--linha-forte:rgba(255,236,240,.12);--sobre-tinta:#141112;--acento:var(--marca-escuro);--acento-texto:var(--marca-escuro);--acento-suave:color-mix(in oklab,var(--marca-escuro) 12%,transparent);--acento-medio:color-mix(in oklab,var(--marca-escuro) 22%,transparent);--acento-brilho:color-mix(in oklab,var(--marca-escuro) 40%,transparent);--ok:#6CC290;--aviso:#E0A350;--erro:#F08A80;--vidro:rgba(23,20,21,.66);--vidro-borda:rgba(255,236,240,.08);--luz-topo:inset 0 1px 0 rgba(255,236,240,.06);--sombra-1:0 1px 2px rgba(0,0,0,.3);--sombra-2:0 2px 8px rgba(0,0,0,.35),0 24px 60px rgba(0,0,0,.45);color-scheme:dark}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--fundo);color:var(--tinta);font-family:var(--letra);font-size:var(--t-corpo);line-height:1.45;-webkit-font-smoothing:antialiased}
button{font:inherit;color:inherit}a{color:inherit}
.num{font-variant-numeric:tabular-nums}.mudo{color:var(--texto-2)}.mudo-3{color:var(--texto-3)}
:focus-visible{outline:2px solid var(--acento);outline-offset:2px;border-radius:10px}
svg.i{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
/* topo em vidro (flutua) */
.topo{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:var(--e4);padding:14px max(20px,env(safe-area-inset-right,0px)) 14px max(20px,env(safe-area-inset-left,0px));background:var(--vidro);-webkit-backdrop-filter:blur(24px) saturate(180%);backdrop-filter:blur(24px) saturate(180%);border-bottom:1px solid var(--linha)}
.marca{display:flex;align-items:center;gap:12px;flex:none}.marca img{height:20px;width:auto;display:block}.marca .escuro{display:none}
.marca .txt{font-weight:600;font-size:16px;letter-spacing:.02em;color:var(--acento-texto)}
.marca .sep{width:1px;height:18px;background:var(--linha-forte)}.marca .ctx{font-size:13px;color:var(--texto-2);font-weight:500}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .marca .claro{display:none}:root:not([data-theme="light"]) .marca .escuro{display:block}}
:root[data-theme="dark"] .marca .claro{display:none}:root[data-theme="dark"] .marca .escuro{display:block}
.topo .direita{margin-left:auto;display:flex;gap:var(--e2);align-items:center}
.btn-icone{width:38px;height:38px;border-radius:50%;border:0;display:inline-grid;place-items:center;cursor:pointer;background:var(--superficie);color:var(--tinta);box-shadow:var(--sombra-1),var(--luz-topo)}
.btn-icone.plano{background:transparent;box-shadow:none;color:var(--texto-2)}
.conteudo{max-width:1180px;margin:0 auto;padding:var(--e6) max(24px,env(safe-area-inset-right,0px)) var(--e10) max(24px,env(safe-area-inset-left,0px));display:flex;flex-direction:column;gap:var(--e5)}
.cabecalho h1{margin:0;font-size:var(--t-ecra);font-weight:500;letter-spacing:-.02em;line-height:1.1}
.subtitulo{color:var(--texto-2);margin:6px 0 0}
.segmentos{display:flex;gap:2px;padding:4px;border-radius:var(--capsula);background:var(--recesso);overflow-x:auto;max-width:100%;width:max-content;scrollbar-width:none}
.segmentos::-webkit-scrollbar{display:none}
.segmentos a{padding:6px 14px;border-radius:var(--capsula);color:var(--texto-2);font-weight:500;font-size:13px;white-space:nowrap;text-decoration:none}
.segmentos a:hover{background:var(--superficie);color:var(--tinta);box-shadow:var(--sombra-1)}
section.bloco{display:flex;flex-direction:column;gap:var(--e3);scroll-margin-top:84px}
.seccao-titulo{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px var(--e2);margin:var(--e3) 0 0;font-size:20px;font-weight:500;letter-spacing:-.01em}
.seccao-titulo span{font-size:12.5px;color:var(--texto-2);font-weight:400;letter-spacing:0}
.superficie{background:var(--superficie);border-radius:var(--r-superficie);box-shadow:var(--sombra-1),var(--luz-topo)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .superficie{box-shadow:inset 0 0 0 1px var(--linha),var(--luz-topo)}}
:root[data-theme="dark"] .superficie{box-shadow:inset 0 0 0 1px var(--linha),var(--luz-topo)}
.titulo-bloco{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px var(--e2);padding:var(--e5) var(--e6) 0}
.titulo-bloco h3{margin:0;font-size:var(--t-secao);font-weight:500}
.titulo-bloco .nota{margin-left:auto;font-size:12px;color:var(--texto-2)}
.rotulo{font-size:var(--t-pequeno);color:var(--texto-2)}
.numero{font-size:var(--t-numero);font-weight:400;letter-spacing:-.03em;line-height:1;font-variant-numeric:tabular-nums}
.numero small{font-size:.45em;letter-spacing:0;color:var(--texto-2);margin-left:3px}
.delta{font-size:12px;color:var(--texto-2);font-variant-numeric:tabular-nums}.delta.sobe{color:var(--ok)}.delta.desce{color:var(--erro)}
.estado{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--texto-2);white-space:nowrap}
.estado::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--texto-3);flex:none}
.estado.ok::before{background:var(--ok)}.estado.aviso::before{background:var(--aviso)}
.estado.erro{color:var(--erro)}.estado.erro::before{background:var(--erro)}
.estado.acento{color:var(--acento-texto)}.estado.acento::before{background:var(--acento);box-shadow:0 0 0 3px var(--acento-suave)}
.chip{display:inline-flex;align-items:center;height:22px;padding:0 9px;border-radius:var(--capsula);font-size:11.5px;color:var(--texto-2);border:1px solid var(--linha-forte);white-space:nowrap}
/* cartões de números: um por número, separados */
.cartoes{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--e3)}
.cartoes.seis{grid-template-columns:repeat(6,minmax(0,1fr))}
.cartao-n{padding:var(--e5);display:flex;flex-direction:column;gap:10px;min-width:0}
.cartao-n .numero{white-space:nowrap}
.cartao-n.pico{box-shadow:var(--sombra-1),var(--luz-topo),inset 0 0 0 1px var(--acento-medio)}
.cartao-n.pico .numero{color:var(--acento-texto)}
.explica{font-size:12.5px;color:var(--texto-2);margin:0;padding:0 4px;max-width:880px}
.vazio{padding:var(--e6);color:var(--texto-2)}
/* ganham / perdem */
.dupla{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--e3);align-items:start}
.lista-f{list-style:none;margin:0;padding:var(--e3) var(--e6) var(--e5)}
.lista-f li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px var(--e3);padding:10px 0;border-top:1px solid var(--linha)}
.lista-f li:first-child{border-top:0}
.lista-f .v{font-weight:500;min-width:0;overflow-wrap:anywhere}.lista-f .k{font-size:12px;color:var(--texto-2)}
.lista-f .ind{grid-row:1/3;grid-column:2;align-self:center;text-align:right;font-variant-numeric:tabular-nums;font-size:18px}
.lista-f .ind small{display:block;font-size:11.5px;color:var(--texto-2)}
/* famílias: barras horizontais com pontas redondas, uma só no acento */
.grelha-f{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--e3);align-items:start}
.fam .linhas{padding:var(--e3) var(--e6) var(--e5);display:flex;flex-direction:column;gap:12px}
.hb{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px var(--e3);align-items:baseline}
.hb .v{font-weight:500;min-width:0;overflow-wrap:anywhere}.hb .x{font-variant-numeric:tabular-nums;font-size:13px}
.hb .meta{grid-column:1/-1;font-size:11.5px;color:var(--texto-2);font-variant-numeric:tabular-nums;display:flex;flex-wrap:wrap;gap:2px 10px;align-items:center}
.hb .pista{grid-column:1/-1;height:8px;border-radius:var(--capsula);background:var(--recesso);position:relative}
.hb .pista i{position:absolute;left:0;top:0;bottom:0;border-radius:var(--capsula);background:var(--recesso-forte)}
.hb .pista .media{position:absolute;top:-3px;bottom:-3px;width:2px;border-radius:2px;background:var(--texto-3)}
.hb.foco .pista i{background:var(--acento);box-shadow:0 4px 12px -4px var(--acento-brilho)}
.hb.foco .x{color:var(--acento-texto)}
.hb.poucos .pista i{background:repeating-linear-gradient(135deg,var(--recesso-forte) 0 4px,transparent 4px 8px);box-shadow:inset 0 0 0 1px var(--recesso-forte)}
.hb.poucos .v{color:var(--texto-2)}
/* gráfico de barras verticais */
.grafico{padding:var(--e4) var(--e6) var(--e5)}
.barras{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);align-items:end;gap:10px;height:170px;margin-top:var(--e4)}
.barra{display:flex;flex-direction:column;align-items:center;gap:6px;height:100%;justify-content:flex-end;min-width:0}
.barra .pv{flex:1 1 0;min-height:0;width:100%;display:flex;align-items:flex-end;justify-content:center}
.barra i{display:block;width:100%;max-width:40px;border-radius:10px;background:var(--recesso-forte);min-height:4px;flex:none}
.barra.foco i{background:var(--acento);box-shadow:0 8px 20px -8px var(--acento-brilho)}
.barra.parcial i{background:repeating-linear-gradient(135deg,var(--recesso-forte) 0 5px,transparent 5px 9px);box-shadow:inset 0 0 0 1px var(--recesso-forte)}
.barra.zero i{background:transparent;box-shadow:inset 0 0 0 1px var(--linha-forte)}
.barra span{font-size:11px;color:var(--texto-2);white-space:nowrap}
.barra b{font-weight:500;font-size:11.5px;font-variant-numeric:tabular-nums;white-space:nowrap}
.barra em{font-style:normal;font-size:10.5px;color:var(--texto-3)}
/* tabelas: linhas sem grelha */
.tabela-caixa{overflow-x:auto}
table.tabela{width:100%;border-collapse:separate;border-spacing:0;font-variant-numeric:tabular-nums}
.tabela th{font-size:var(--t-rotulo);font-weight:500;color:var(--texto-2);text-align:left;padding:12px 14px;white-space:nowrap}
.tabela td{padding:11px 14px;border-top:1px solid var(--linha);vertical-align:top}
.tabela td:first-child,.tabela th:first-child{padding-left:var(--e6)}
.tabela td:last-child,.tabela th:last-child{padding-right:var(--e6)}
.tabela tbody tr:hover td{background:var(--superficie-2)}
.tabela .dir{text-align:right;white-space:nowrap}
.tabela .zero{color:var(--texto-3)}
.tabela .hook{max-width:340px;color:var(--texto-2);font-size:12.5px}
.tabela .id{font-weight:500;white-space:nowrap}
.conclusoes{padding:var(--e6);min-height:120px}
.conclusoes .por-preencher{color:var(--texto-2)}
details.superficie>summary{cursor:pointer;list-style:none;padding:var(--e5) var(--e6);display:flex;align-items:center;gap:var(--e2);font-weight:500}
details.superficie>summary::-webkit-details-marker{display:none}
details.superficie>summary svg{transition:transform .25s var(--mola);color:var(--texto-2)}
details[open].superficie>summary svg{transform:rotate(180deg)}
.rodape{font-size:12px;color:var(--texto-3);padding:var(--e4) 4px 0}
@media (max-width:1000px){.cartoes.seis{grid-template-columns:repeat(3,minmax(0,1fr))}.grelha-f{grid-template-columns:minmax(0,1fr)}}
@media (max-width:760px){.dupla{grid-template-columns:minmax(0,1fr)}.cartoes{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){
 :root{--t-ecra:26px;--t-numero:28px}
 .topo{padding-left:16px;padding-right:16px}.marca .ctx,.marca .sep{display:none}
 .conteudo{padding-left:16px;padding-right:16px}
 .cartoes.seis{grid-template-columns:repeat(2,minmax(0,1fr))}
 .cartao-n{padding:var(--e4)}
 .titulo-bloco{padding:var(--e4) var(--e4) 0}.titulo-bloco .nota{margin-left:0;width:100%}
 .lista-f,.fam .linhas{padding-left:var(--e4);padding-right:var(--e4)}
 .grafico{padding:var(--e4)}
 .barras{gap:4px}.barra span,.barra em{font-size:9.5px}.barra b{font-size:10px}
 .barras.muitas .barra b{writing-mode:vertical-rl;transform:rotate(180deg)}
 /* tabelas passam a listas de linhas */
 table.lista thead{display:none}
 table.lista,table.lista tbody,table.lista tr,table.lista td{display:block;width:100%}
 table.lista tr{padding:12px var(--e4);border-top:1px solid var(--linha)}
 table.lista tbody tr:first-child{border-top:0}
 table.lista td{border:0;padding:2px 0!important;display:flex;justify-content:space-between;gap:var(--e3);text-align:right;white-space:normal}
 table.lista td::before{content:attr(data-l);color:var(--texto-2);font-size:12px;text-align:left;flex:none}
 table.lista td.cab{display:block;text-align:left;padding-bottom:4px!important}
 table.lista td.cab::before{content:none}
 table.lista .hook{max-width:none}
 table.lista tbody tr:hover td{background:transparent}
}
@page{size:A4;margin:0}
@media print{
 html{background:var(--fundo)}.conteudo{padding-top:12mm;padding-bottom:12mm}
 .topo{position:static;-webkit-backdrop-filter:none;backdrop-filter:none}.topo .direita,.segmentos{display:none}
 .superficie,.cartao-n,.hb,tr{break-inside:avoid}section.bloco{break-inside:auto}
 details.superficie>summary svg{display:none}
 body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
"""

ICONES = {
    'lua': '<path d="M19.5 14.5A7.5 7.5 0 0 1 9.5 4.5a7.5 7.5 0 1 0 10 10z"/>',
    'baixo': '<path d="m6.5 9.5 5.5 5.5 5.5-5.5"/>',
}


def icone(n):
    return f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true">{ICONES[n]}</svg>'


def css_marca():
    return CSS.replace('__MARCA__', MARCA_COR).replace('__MARCA2__', MARCA_COR_ESCURO).replace('__LETRA__', MARCA_LETRA)


def cartao(rotulo, numero, unidade='', delta='', classe_delta='', pico=False):
    u = f'<small>{e(unidade)}</small>' if unidade and numero != '—' else ''
    d = f'<span class="delta {classe_delta}">{delta}</span>' if delta else '<span class="delta">&nbsp;</span>'
    return (f'<div class="superficie cartao-n{" pico" if pico else ""}"><span class="rotulo">{e(rotulo)}</span>'
            f'<span class="numero">{numero}{u}</span>{d}</div>')


def classe_sinal(x):
    return '' if not x else ('sobe' if x > 0 else 'desce')


def estado_sug(s):
    c = {'vencedor': 'ok', 'retirado': 'erro', 'a testar': '', 'poucos dados': ''}[s]
    t = {'vencedor': 'Vencedor', 'retirado': 'Retirar', 'a testar': 'A testar', 'poucos dados': 'Poucos dados'}[s]
    return f'<span class="estado {c}">{t}</span>'


def html_resumo(a):
    p, c, mc = a['perfil'], a['ciclo'], a['medias_ciclo']
    s1 = [
        cartao('Seguidores no fim do ciclo', fn(p['seguidores_fim']),
               delta=f"{fsinal(p['seguidores_vs_linha_de_base'])} vs linha de base",
               classe_delta=classe_sinal(p['seguidores_vs_linha_de_base'])),
        cartao('Seguidores ganhos no ciclo', fsinal(p['seguidores_ganhos_ciclo']),
               delta=f"de {fn(p['seguidores_inicio'])} para {fn(p['seguidores_fim'])}", pico=True),
        cartao('Views da conta, 30 dias', fn(p['views_30_dias']),
               delta=(f"{fsinal(p['views_30_dias_variacao_pct'], 1)} % vs linha de base"
                      if p['views_30_dias_variacao_pct'] is not None else 'sem linha de base'),
               classe_delta=classe_sinal(p['views_30_dias_variacao_pct'])),
        cartao('Alcance da conta, 30 dias', fn(p['alcance_30_dias']),
               delta=(f"{fsinal(p['alcance_30_dias_variacao_pct'], 1)} % vs linha de base"
                      if p['alcance_30_dias_variacao_pct'] is not None else 'sem linha de base'),
               classe_delta=classe_sinal(p['alcance_30_dias_variacao_pct'])),
        cartao('Views dos trial reels no ciclo', fn(p['views_trial_reels_ciclo']),
               delta=plural(c['reels_publicados'], 'reel publicado', 'reels publicados')),
        cartao('Peso nas views da conta', fn(p['fracao_views_conta_pct'], 1) if p['fracao_views_conta_pct']
               is not None else '—', unidade='%' if p['fracao_views_conta_pct'] is not None else '',
               delta='estimativa, ver nota'),
        cartao('Reels analisados', fn(c['reels_analisados']),
               delta=f"de {fn(c['reels_na_janela'])} com 7 dias no ciclo"),
        cartao('Visitas ao perfil, 30 dias', fn(p['visitas_perfil_30_dias']),
               delta=f"linha de base {fn(p['visitas_perfil_30_dias_linha_de_base'])}"),
    ]
    t = mc['taxas']
    s2 = [
        cartao('Views por reel', fn(mc['views_media'])),
        cartao('Alcance por reel', fn(mc['alcance_medio'])),
        cartao('Guardados', fn(t['guardados']['media'], 1), 'por 1000'),
        cartao('Partilhas', fn(t['partilhas']['media'], 1), 'por 1000'),
        cartao('Comentários', fn(t['comentarios']['media'], 1), 'por 1000'),
        cartao('Skip rate médio', fn(mc['skip_medio_pct'], 1), '%' if mc['skip_medio_pct'] is not None else '',
               delta=(f"tempo médio = {fn(mc['tempo_sobre_duracao_medio'], 2)}× a duração"
                      if mc['tempo_sobre_duracao_medio'] is not None else '')),
    ]
    return f"""
<section class="bloco" id="resumo">
  <h2 class="seccao-titulo">Resumo do ciclo <span>perfil comparado com a linha de base de {e(data_longa(p['linha_de_base']))}</span></h2>
  <div class="cartoes">{''.join(s1)}</div>
  <p class="explica"><b style="font-weight:500">Como se calcula o peso nas views.</b> {e(p['fracao_explicacao'])}</p>
  <h2 class="seccao-titulo">Médias dos reels analisados <span>{e(c['nota'])}</span></h2>
  <div class="cartoes seis">{''.join(s2)}</div>
</section>"""


def html_lista_familias(xs, titulo, nota, vazio):
    if not xs:
        corpo = f'<p class="vazio">{e(vazio)}</p>'
    else:
        lis = ''.join(
            f'<li><span class="v">{e(str(x["valor"]))}</span>'
            f'<span class="ind">{fn(x["indice"], 2)}×<small>n {x["n"]}</small></span>'
            f'<span class="k">{e(x["rotulo"])} · {fn(x["views_media"])} views · '
            f'{fn(x["guardados"], 1)} guard. · {fn(x["comentarios"], 1)} coment.</span></li>' for x in xs[:8])
        corpo = f'<ul class="lista-f">{lis}</ul>'
    return (f'<div class="superficie"><div class="titulo-bloco"><h3>{e(titulo)}</h3>'
            f'<span class="nota">{e(nota)}</span></div>{corpo}</div>')


def html_familias(a):
    regra = a['regras']['indice']
    topo = (html_lista_familias(a['familias_ganham'], 'Ganham', 'índice acima de 1,0',
                                f'Ainda nenhuma família com {MIN_SAIDAS} ou mais saídas acima da média.') +
            html_lista_familias(a['familias_perdem'], 'Perdem', 'índice abaixo de 1,0',
                                f'Ainda nenhuma família com {MIN_SAIDAS} ou mais saídas abaixo da média.'))
    cards = []
    for k, f in a['familias'].items():
        vals = f['valores']
        if not vals:
            linhas = '<p class="mudo" style="margin:0">Sem dados neste ciclo.</p>'
        else:
            mx = max([v['indice'] or 0 for v in vals] + [1.0]) * 1.08
            # só se realça (no acento) o melhor valor quando se destaca mesmo: n >= 3 e índice >= 1,05
            melhor = next((v for v in vals if not v.get('poucos_dados') and (v['indice'] or 0) >= DESTAQUE_MIN
                           and len(vals) > 1), None)
            linhas = ''
            for v in vals:
                cl = 'hb' + (' foco' if v is melhor else '') + (' poucos' if v.get('poucos_dados') else '')
                w = (v['indice'] or 0) * 100 / mx
                t = v['taxas']
                pd = '<span class="estado">Poucos dados</span>' if v.get('poucos_dados') else ''
                linhas += (
                    f'<div class="{cl}"><span class="v">{e(str(v["valor"]))}</span>'
                    f'<span class="x">{fn(v["indice"], 2)}×</span>'
                    f'<span class="pista"><i style="width:{w:.1f}%"></i><span class="media" style="left:{100 / mx:.1f}%"></span></span>'
                    f'<span class="meta"><span>n {v["n"]}</span><span>{fn(v["views_media"])} views</span>'
                    f'<span>{fn(t["guardados"]["media"], 1)} guard.</span><span>{fn(t["partilhas"]["media"], 1)} part.</span>'
                    f'<span>{fn(t["comentarios"]["media"], 1)} coment.</span>'
                    f'<span>skip {fn(v["skip_medio_pct"], 0)}{"%" if v["skip_medio_pct"] is not None else ""}</span>{pd}</span></div>')
        cards.append(f'<div class="superficie fam"><div class="titulo-bloco"><h3>{e(f["rotulo"])}</h3>'
                     f'<span class="nota">{len(vals)} {"valor" if len(vals) == 1 else "valores"}</span></div>'
                     f'<div class="linhas">{linhas}</div></div>')
    return f"""
<section class="bloco" id="familias">
  <h2 class="seccao-titulo">Famílias que ganham e perdem <span>só famílias com {MIN_SAIDAS} ou mais saídas</span></h2>
  <div class="dupla">{topo}</div>
  <p class="explica">Índice: {e(regra)}. Taxas por 1000 contas alcançadas. A risca vertical em cada barra marca a média (1,0); a riscado, as famílias com menos de {MIN_SAIDAS} saídas.</p>
  {f'<div class="grelha-f">{"".join(cards)}</div>' if a['reels'] else '<div class="superficie"><p class="vazio">Ainda não há reels com 7 dias neste ciclo: as famílias aparecem quando houver.</p></div>'}
</section>"""


def html_tabela_itens(itens, sid, titulo, sub, primeira, extra_cols=(), vazio_txt=''):
    """Tabela de textos, B-rolls ou trechos. extra_cols: [(cabeçalho, função(item) -> html)]."""
    if not itens:
        corpo = f'<p class="vazio">{e(vazio_txt)}</p>'
    else:
        cab = (f'<th>{e(primeira)}</th>' + ''.join(f'<th>{e(h)}</th>' for h, _ in extra_cols) +
               '<th class="dir">Saídas</th><th class="dir">Views médias</th><th class="dir">Guard./1000</th>'
               '<th class="dir">Coment./1000</th><th class="dir">Part./1000</th><th class="dir">Skip</th><th>Sugestão</th>')
        linhas = ''
        for x in itens:
            t = x['taxas']
            linhas += (
                f'<tr><td class="cab id" data-l="{e(primeira)}">{e(str(x["id"]))}</td>' +
                ''.join(f'<td data-l="{e(h)}" class="{"hook" if h == "Hook" else ""}">{f(x)}</td>'
                        for h, f in extra_cols) +
                f'<td class="dir" data-l="Saídas">{x["n"]}</td>'
                f'<td class="dir" data-l="Views médias">{fn(x["views_media"])}</td>'
                f'<td class="dir" data-l="Guardados por 1000">{fn(t["guardados"]["media"], 1)}</td>'
                f'<td class="dir" data-l="Comentários por 1000">{fn(t["comentarios"]["media"], 1)}</td>'
                f'<td class="dir" data-l="Partilhas por 1000">{fn(t["partilhas"]["media"], 1)}</td>'
                f'<td class="dir" data-l="Skip">{fn(x["skip_medio_pct"])}{"%" if x["skip_medio_pct"] is not None else ""}</td>'
                f'<td data-l="Sugestão">{estado_sug(x["sugestao"])}</td></tr>')
        corpo = f'<div class="tabela-caixa"><table class="tabela lista"><thead><tr>{cab}</tr></thead><tbody>{linhas}</tbody></table></div>'
    return f"""
<section class="bloco" id="{sid}">
  <h2 class="seccao-titulo">{e(titulo)} <span>{e(sub)}</span></h2>
  <div class="superficie">{corpo}</div>
</section>"""


def resumo_sug(itens):
    n = defaultdict(int)
    for x in itens:
        n[x['sugestao']] += 1
    return (f"{n['vencedor']} vencedores · {n['a testar']} a testar · {n['retirado']} a retirar · "
            f"{n['poucos dados']} com menos de {MIN_SAIDAS} saídas")


def html_textos(a):
    com = [x for x in a['textos'] if x['n'] >= MIN_SAIDAS]
    sub = f"{resumo_sug(a['textos'])} · referência: {a['referencia_vencedor']}"
    return html_tabela_itens(
        com, 'textos', 'Textos', sub, 'Texto',
        [('Hook', lambda x: e(x['hook'])), ('Recurso', lambda x: e(x['recurso'] or '—')),
         ('No banco', lambda x: e(x.get('estado_no_banco') or '—'))],
        f'Ainda nenhum texto saiu {MIN_SAIDAS} vezes entre os reels analisados.')


def html_brolls(a):
    com = [x for x in a['brolls'] if x['n'] >= MIN_SAIDAS]
    return html_tabela_itens(com, 'brolls', 'B-rolls', resumo_sug(a['brolls']), 'B-roll',
                             [('Tipo', lambda x: e(x.get('tipo') or '—'))],
                             f'Ainda nenhum B-roll saiu {MIN_SAIDAS} vezes entre os reels analisados.')


def html_musicas(a):
    mus = html_tabela_itens(a['musicas'], 'musicas', 'Músicas', 'todas as músicas do ciclo', 'Música', (),
                            'Sem reels analisados neste ciclo.')
    com = [x for x in a['trechos_musica'] if x['n'] >= MIN_SAIDAS]
    tr = html_tabela_itens(com, 'trechos', 'Trechos de música', f"baldes de 20 s · {resumo_sug(a['trechos_musica'])}",
                           'Música e trecho', (),
                           f'Ainda nenhum trecho saiu {MIN_SAIDAS} vezes entre os reels analisados.')
    return mus + tr


def html_recursos(a):
    rs = a['recursos']
    if not rs:
        corpo = '<p class="vazio">Sem reels analisados neste ciclo.</p>'
    else:
        mx = max([x['comentarios_por_1000_views'] or 0 for x in rs] + [0.01]) * 1.05
        linhas = ''
        for i, x in enumerate(rs):
            regra = {'fica': '<span class="estado ok">Fica</span>', 'sai': '<span class="estado erro">Sai</span>',
                     '—': ''}[x['regra']]
            cl = 'hb' + (' foco' if i == 0 and not x['poucos_dados'] else '') + (' poucos' if x['poucos_dados'] else '')
            pd = '<span class="estado">Poucos dados</span>' if x['poucos_dados'] else ''
            linhas += (f'<div class="{cl}"><span class="v">{e(x["recurso"])}</span>'
                       f'<span class="x">{fn(x["comentarios_por_1000_views"], 1)}</span>'
                       f'<span class="pista"><i style="width:{(x["comentarios_por_1000_views"] or 0) * 100 / mx:.1f}%"></i></span>'
                       f'<span class="meta"><span>n {x["n"]}</span><span>{fn(x["comentarios"])} comentários</span>'
                       f'<span>{fn(x["views"])} views</span>{regra}{pd}</span></div>')
        corpo = f'<div class="linhas">{linhas}</div>'
    nota = 'ficam os 3 melhores, saem os 2 piores' if len(rs) >= 5 else 'a regra dos 3 e 2 precisa de 5 recursos'
    return f"""
<section class="bloco" id="recursos">
  <h2 class="seccao-titulo">Recursos <span>comentários por 1000 views · {e(nota)}</span></h2>
  <div class="superficie fam">{corpo}</div>
</section>"""


def html_volume(a):
    dias = a['volume']['por_dia']
    mx = max([d['alcance_total'] or 0 for d in dias] + [1])
    validos = [d for d in dias if d['alcance_total'] and d['todos_maduros']]
    melhor = max(validos, key=lambda d: d['alcance_total']) if validos else None
    bs = ''
    for d in dias:
        al = d['alcance_total']
        cl = 'barra'
        if not d['reels']:
            cl += ' zero'
        elif d is melhor:
            cl += ' foco'
        elif not d['todos_maduros']:
            cl += ' parcial'
        h = (al or 0) * 100 / mx
        dd = data_de(d['data'])
        bs += (f'<div class="{cl}"><b>{fn(al) if al is not None else "—"}</b><div class="pv"><i style="height:{max(h, 2):.1f}%"></i></div>'
               f'<span>{dd.day}</span><em>{d["reels"]} r.</em></div>')
    pv = a['volume']['por_volume']
    if pv:
        mxv = max([x['alcance_medio_por_reel'] or 0 for x in pv] + [1])
        best = max(pv, key=lambda x: x['alcance_medio_por_reel'] or 0)
        vb = ''.join(
            f'<div class="barra{" foco" if x is best and len(pv) > 1 else ""}"><b>{fn(x["alcance_medio_por_reel"])}</b>'
            f'<div class="pv"><i style="height:{(x["alcance_medio_por_reel"] or 0) * 100 / mxv:.1f}%"></i></div>'
            f'<span>{x["reels_por_dia"]} por dia</span><em>{x["dias"]} dias</em></div>' for x in pv)
        vol = f'<div class="barras" style="height:150px">{vb}</div>'
    else:
        vol = '<p class="mudo">Ainda sem dias com reels maduros.</p>'
    fx = a['familias']['faixa']['valores']
    if fx:
        ordem = ['Manhã (9h-12h)', 'Almoço (12h-14h)', 'Tarde (14h-17h)', 'Fim de tarde (17h-20h30)', 'Fora da janela']
        fx = sorted(fx, key=lambda v: ordem.index(v['valor']) if v['valor'] in ordem else 9)
        mxf = max([v['alcance_medio'] or 0 for v in fx] + [1])
        okf = [v for v in fx if not v.get('poucos_dados')]
        bf = max(okf, key=lambda v: v['alcance_medio'] or 0) if okf else None
        hb = ''.join(
            f'<div class="barra{" foco" if v is bf and len(fx) > 1 else ""}{" parcial" if v.get("poucos_dados") else ""}">'
            f'<b>{fn(v["alcance_medio"])}</b><div class="pv"><i style="height:{(v["alcance_medio"] or 0) * 100 / mxf:.1f}%"></i></div>'
            f'<span>{e(v["valor"].split(" (")[0])}</span><em>n {v["n"]}</em></div>' for v in fx)
        hor = f'<div class="barras" style="height:150px">{hb}</div>'
    else:
        hor = '<p class="mudo">Sem reels analisados neste ciclo.</p>'
    return f"""
<section class="bloco" id="volume">
  <h2 class="seccao-titulo">Volume e horários <span>alcance somado dos reels de cada dia</span></h2>
  <div class="superficie grafico">
    <div class="titulo-bloco" style="padding:0"><h3>Alcance total por dia</h3><span class="nota">por baixo: dia e reels publicados · a riscado, dias com reels com menos de 7 dias</span></div>
    <div class="barras muitas">{bs}</div>
  </div>
  <div class="dupla">
    <div class="superficie grafico"><div class="titulo-bloco" style="padding:0"><h3>Alcance médio por reel, por volume do dia</h3><span class="nota">reels maduros</span></div>{vol}</div>
    <div class="superficie grafico"><div class="titulo-bloco" style="padding:0"><h3>Alcance médio por reel, por faixa horária</h3><span class="nota">reels analisados</span></div>{hor}</div>
  </div>
</section>"""


def html_reels(a):
    rs = sorted(a['reels'], key=lambda x: -(x['views'] or 0))
    if not rs:
        corpo = '<p class="vazio">Ainda não há reels com 7 dias neste ciclo.</p>'
    else:
        linhas = ''
        for x in rs:
            t = x['taxas_por_1000']
            q = datetime.fromisoformat(x['quando'][:19]) if x['quando'] else None
            quando = f"{data_curta(x['publicado'])}, {q:%H:%M}" if q else data_curta(x['publicado'])
            link = f'<a href="{e(x["url"])}">{e(x["texto"])}</a>' if x.get('url') else e(x['texto'] or '—')
            linhas += (f'<tr><td class="cab id" data-l="Texto">{link}</td><td data-l="Publicado">{e(quando)}</td>'
                       f'<td class="dir" data-l="Views">{fn(x["views"])}</td><td class="dir" data-l="Alcance">{fn(x["alcance"])}</td>'
                       f'<td class="dir" data-l="Guard./1000">{fn(t["guardados"], 1)}</td>'
                       f'<td class="dir" data-l="Part./1000">{fn(t["partilhas"], 1)}</td>'
                       f'<td class="dir" data-l="Coment./1000">{fn(t["comentarios"], 1)}</td>'
                       f'<td class="dir" data-l="Gostos/1000">{fn(t["gostos"], 1)}</td>'
                       f'<td class="dir" data-l="Visitas/1000">{fn(t["visitas_perfil"], 1)}</td>'
                       f'<td class="dir" data-l="Skip">{fn(x["skip_rate_pct"])}{"%" if x["skip_rate_pct"] is not None else ""}</td>'
                       f'<td class="dir" data-l="Tempo / duração">{fn(x["tempo_sobre_duracao"], 2)}{"×" if x["tempo_sobre_duracao"] is not None else ""}</td></tr>')
        corpo = ('<div class="tabela-caixa"><table class="tabela lista"><thead><tr><th>Texto</th><th>Publicado</th>'
                 '<th class="dir">Views</th><th class="dir">Alcance</th><th class="dir">Guard./1000</th>'
                 '<th class="dir">Part./1000</th><th class="dir">Coment./1000</th><th class="dir">Gostos/1000</th>'
                 '<th class="dir">Visitas/1000</th><th class="dir">Skip</th><th class="dir">Tempo / duração</th>'
                 f'</tr></thead><tbody>{linhas}</tbody></table></div>')
    am = a['reels_a_amadurecer']
    return f"""
<section class="bloco" id="reels">
  <details class="superficie"><summary>Reels analisados <span class="mudo" style="font-weight:400">{len(rs)} · {len(am)} ainda a amadurecer</span><span style="margin-left:auto">{icone('baixo')}</span></summary>{corpo}</details>
</section>"""


def gerar_html(a):
    c = a['ciclo']
    marca = f'<span class="txt">{e(NOME or CONTA_IG)}</span>'
    titulo = periodo(c['inicio'], c['ate'])
    nav = ''.join(f'<a href="#{i}">{t}</a>' for i, t in [
        ('resumo', 'Resumo'), ('familias', 'Famílias'), ('textos', 'Textos'), ('brolls', 'B-rolls'),
        ('musicas', 'Músicas'), ('recursos', 'Recursos'), ('volume', 'Volume e horários'),
        ('conclusoes', 'Conclusões')])
    gerado = datetime.fromisoformat(a['gerado'])
    return f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Trial reels · {e(titulo)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={MARCA_LETRA.replace(" ", "+")}:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap">
<style>{css_marca()}</style>
<script>
(function(){{try{{var t=new URLSearchParams(location.search).get('tema')||localStorage.getItem('tema');
if(t==='escuro')document.documentElement.dataset.theme='dark';if(t==='claro')document.documentElement.dataset.theme='light';}}catch(e){{}}}})();
function trocarTema(){{var r=document.documentElement,esc=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
r.dataset.theme=esc?'light':'dark';try{{localStorage.setItem('tema',esc?'claro':'escuro')}}catch(e){{}}}}
</script>
</head>
<body>
<header class="topo">
  <div class="marca">{marca}<span class="sep"></span><span class="ctx">Trial reels · {CONTA_IG}</span></div>
  <div class="direita"><button class="btn-icone plano" onclick="trocarTema()" aria-label="Mudar entre claro e escuro">{icone('lua')}</button></div>
</header>
<main class="conteudo">
  <div class="cabecalho">
    <h1>Ciclo de {e(titulo)}</h1>
    <p class="subtitulo">{plural(c['reels_publicados'], 'reel publicado', 'reels publicados')} · {plural(c['reels_analisados'], 'analisado', 'analisados')} com 7 ou mais dias · gerado a {e(data_longa(a['gerado']))}, {gerado:%H:%M}</p>
  </div>
  <nav class="segmentos" aria-label="Secções">{nav}</nav>
  {html_resumo(a)}
  {html_familias(a)}
  {html_textos(a)}
  {html_brolls(a)}
  {html_musicas(a)}
  {html_recursos(a)}
  {html_volume(a)}
  {html_reels(a)}
  <section class="bloco" id="conclusoes">
    <h2 class="seccao-titulo">Conclusões e mudanças <span>o que muda no próximo ciclo</span></h2>
    <div class="superficie conclusoes">
<!--CONCLUSOES-->
      <p class="por-preencher">Por preencher.</p>
<!--/CONCLUSOES-->
    </div>
  </section>
  <p class="rodape">Gerado por metricas/analisar.py, sem IA, a partir de fabrica/historico.jsonl, banco/textos.json e das leituras em metricas/. Os números do Instagram podem chegar com até 48 h de atraso.</p>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------------------------------------- PDF

def exportar_pdf(html_f):
    pdf = html_f.with_suffix('.pdf')
    try:
        cfg.pdf_de_html(html_f, pdf)
    except Exception as ex:
        print('pdf: falhou:', ex)
        return None
    return pdf if pdf.exists() else None


def main():
    ap = argparse.ArgumentParser(description='Análise de um ciclo de 14 dias dos trial reels.')
    ap.add_argument('--ate', default=date.today().isoformat(), help='último dia do ciclo (AAAA-MM-DD), por defeito hoje')
    ap.add_argument('--pdf', action='store_true', help='exporta também relatorio.pdf com o Chromium do Playwright')
    ap.add_argument('--raiz', default=str(RAIZ_PROJETO), help='pasta do projeto (para testar com dados de ensaio)')
    a = ap.parse_args()
    raiz = pathlib.Path(a.raiz).resolve()
    ate = date.fromisoformat(a.ate)
    analise = analisar(raiz, ate)
    pasta = raiz / 'metricas' / 'ciclos' / ate.isoformat()
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / 'analise.json').write_text(json.dumps(analise, ensure_ascii=False, indent=1), encoding='utf-8')
    html_f = pasta / 'relatorio.html'
    novo = gerar_html(analise)
    if html_f.exists():   # se outro passo já preencheu as conclusões, mantêm-se
        velho = html_f.read_text(encoding='utf-8')
        mm = re.search(r'<!--CONCLUSOES-->(.*?)<!--/CONCLUSOES-->', velho, re.S)
        if mm and 'por-preencher' not in mm.group(1):
            novo = re.sub(r'<!--CONCLUSOES-->.*?<!--/CONCLUSOES-->',
                          lambda _: f'<!--CONCLUSOES-->{mm.group(1)}<!--/CONCLUSOES-->', novo, flags=re.S)
    html_f.write_text(novo, encoding='utf-8')
    c = analise['ciclo']
    print(f"ciclo {c['inicio']} a {c['ate']}: {c['reels_publicados']} publicados, {c['reels_analisados']} analisados")
    print('json:', pasta / 'analise.json')
    print('html:', html_f)
    if a.pdf:
        pdf = exportar_pdf(html_f)
        if pdf:
            print('pdf: ', pdf)


if __name__ == '__main__':
    sys.exit(main())
