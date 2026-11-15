"""Drive (pasta RAW, só leitura por link), Zernio (trial reels e automações) e bancos de imagens grátis.

Tudo o que é pessoal (chaves, conta, pastas) vem do .env da raiz do projeto, por ferramentas/config.py.
"""
import json
import mimetypes
import pathlib
import sys
import urllib.parse
import urllib.request
import uuid

AQUI = pathlib.Path(__file__).resolve().parent.parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402

PASTA_RAW = cfg.get('DRIVE_PASTA_TALKING_HEAD_RAW', obrigatorio=False)
PASTA_PUBLICADOS = cfg.get('DRIVE_PASTA_TALKING_HEAD_PUBLICADOS', obrigatorio=False)

CONTA_IG = cfg.get('ZERNIO_ACCOUNT_ID')
ZERNIO = 'https://zernio.com/api/v1'
UA = 'reels-talking-head/1.0'


def env(nome):
    return cfg.get(nome)


# --- Drive (pasta RAW partilhada por link: lê-se sem chaves) -----------------------------------------
import drive_publico as dp  # noqa: E402


def drive_listar(pasta, so_videos=False):
    """[{id, name}] dos ficheiros da pasta (partilhada por link)."""
    fs = dp.ficheiros(pasta, dp.VIDEO) if so_videos else [f for f in dp.listar(pasta) if not f['pasta']]
    return [{'id': f['id'], 'name': f['nome']} for f in fs]


def drive_descarregar(fid, destino):
    return dp.baixar(fid, destino)


def zernio(metodo, caminho, corpo=None, extra=None):
    h = {'Authorization': 'Bearer ' + env('ZERNIO_API_KEY'), 'Content-Type': 'application/json',
         'User-Agent': UA, **(extra or {})}
    r = urllib.request.Request(ZERNIO + caminho, method=metodo, headers=h,
                               data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        with urllib.request.urlopen(r, timeout=180) as x:
            dados = x.read()
            return json.loads(dados) if dados else {}
    except urllib.error.HTTPError as e:
        sys.exit(f'Zernio {metodo} {caminho} → {e.code}: {e.read().decode(errors="replace")[:500]}')


def zernio_carregar(ficheiro):
    f = pathlib.Path(ficheiro)
    tipo = mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
    p = zernio('POST', '/media/presign', {'filename': f.name, 'contentType': tipo})
    r = urllib.request.Request(p['uploadUrl'], method='PUT', data=f.read_bytes(), headers={'Content-Type': tipo})
    urllib.request.urlopen(r, timeout=900).read()
    return p['publicUrl']


def zernio_trial_reel(video, capa, legenda, quando):
    """Trial reel MANUAL (só não-seguidores; nunca se promove). quando = 'AAAA-MM-DDTHH:MM:SS' em Lisboa."""
    psd = {'instagramThumbnail': zernio_carregar(capa), 'trialParams': {'graduationStrategy': 'MANUAL'}}
    corpo = {'content': legenda.strip(), 'mediaItems': [{'type': 'video', 'url': zernio_carregar(video)}],
             'platforms': [{'platform': 'instagram', 'accountId': CONTA_IG, 'platformSpecificData': psd}],
             'scheduledFor': quando, 'timezone': cfg.get('FUSO', 'Europe/Lisbon')}
    res = zernio('POST', '/posts', corpo, {'Idempotency-Key': str(uuid.uuid5(uuid.NAMESPACE_URL, str(video) + quando))})
    post = res.get('post', res)
    return post.get('_id'), post.get('status')


# Automações comentário → DM (mesmas regras do ctas/como-construir-cta.md)
COMUNS = {
    'IA', 'AI', 'INTELIGENCIA', 'INTELIGÊNCIA', 'ARTIFICIAL', 'SIM', 'NAO', 'NÃO', 'QUERO', 'EU', 'TOP', 'BOM', 'BOA',
    'OBRIGADO', 'OBRIGADA', 'LINK', 'INFO', 'MAIS', 'FUNDO', 'PROCESSO', 'PROCESSOS', 'AGENDA', 'LISTA', 'EMPRESA',
    'NEGOCIO', 'NEGÓCIO', 'DADOS', 'TAREFA', 'TAREFAS', 'EQUIPA', 'CLIENTE', 'CLIENTES', 'TEMPO', 'DINHEIRO', 'AJUDA',
    'GUIA', 'VIDEO', 'VÍDEO', 'POST', 'AGENTE', 'AGENTES', 'CHATGPT', 'CLAUDE', 'GEMINI', 'AUTOMAÇÃO', 'AUTOMACAO',
    'DIAGNOSTICO', 'DIAGNÓSTICO', 'PROMPT', 'PROMPTS', 'MODELO', 'PLANO', 'CUSTO', 'PREÇO', 'PRECO', 'GRATIS', 'GRÁTIS',
}
RESPOSTAS = ['Está na tua caixa de mensagens. Depois diz-me se ajudou.',
             'Enviado 📩 Se não aparecer, espreita os pedidos de mensagem.',
             'Já seguiu por mensagem. Conta-me como correu.',
             'Mandei-te agora por mensagem ✨',
             'Feito: está nas tuas mensagens 📩']


def zernio_automacoes():
    return zernio('GET', '/comment-automations').get('automations', [])


def zernio_criar_automacao(palavra, dm, botao_texto, botao_link, nome, ensaio=False):
    palavra = palavra.strip().upper()
    if palavra in COMUNS or len(palavra) < 4:
        sys.exit(f'{palavra}: palavra comum ou curta demais')
    for au in zernio_automacoes():
        if palavra in [k.upper() for k in au.get('keywords', [])]:
            sys.exit(f'{palavra}: já está numa automação ({au.get("name")})')
    if len(dm) > 640:
        sys.exit('DM com botão: máximo 640 caracteres')
    corpo = {'accountId': CONTA_IG, 'name': nome, 'trigger': 'comment', 'keywords': [palavra], 'matchMode': 'word',
             'typoTolerance': True, 'dmMessage': dm, 'alsoMatchInDms': True,
             'commentReply': 'Já te enviei por mensagem 📩', 'commentReplyVariations': RESPOSTAS,
             'publicReplyPolicy': 'always', 'commentReplyDelaySeconds': 40,
             'buttons': [{'type': 'url', 'title': botao_texto[:20], 'url': botao_link}]}
    if ensaio:
        return corpo
    au = zernio('POST', '/comment-automations', corpo)
    au = au.get('automation', au)
    return {'id': au.get('_id') or au.get('id'), 'palavra': palavra}


# --- imagens grátis (Pixabay, Openverse, Wikimedia Commons) ------------------------------------------
def _get_json(url, headers=None):
    r = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
    with urllib.request.urlopen(r, timeout=30) as x:
        return json.load(x)


def pixabay(q, n=6):
    chave = cfg.get('PIXABAY_API_KEY', '', obrigatorio=False)
    if not chave:          # opcional: sem chave, ficam a Openverse e a Wikimedia
        return []
    u = 'https://pixabay.com/api/?' + urllib.parse.urlencode(
        {'key': chave, 'q': q[:100], 'image_type': 'photo', 'safesearch': 'true',
         'per_page': max(3, n), 'order': 'popular'})
    return [{'fonte': 'pixabay', 'url': h['largeImageURL'], 'mini': h['webformatURL'], 'pagina': h['pageURL'],
             'w': h['imageWidth'], 'h': h['imageHeight']} for h in _get_json(u).get('hits', [])[:n]]


def openverse(q, n=6):
    u = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(
        {'q': q[:200], 'page_size': n, 'license_type': 'commercial', 'mature': 'false'})
    return [{'fonte': 'openverse', 'url': r['url'], 'mini': r.get('thumbnail') or r['url'],
             'pagina': r.get('foreign_landing_url'), 'w': r.get('width') or 0, 'h': r.get('height') or 0,
             'licenca': r.get('license'), 'autor': r.get('creator')} for r in _get_json(u).get('results', [])]


def wikimedia(q, n=6):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(
        {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': q + ' filetype:bitmap',
         'gsrnamespace': 6, 'gsrlimit': n, 'prop': 'imageinfo', 'iiprop': 'url|size', 'iiurlwidth': 1200})
    pags = _get_json(u).get('query', {}).get('pages', {}).values()
    out = []
    for p in pags:
        ii = (p.get('imageinfo') or [{}])[0]
        if ii.get('thumburl'):
            out.append({'fonte': 'wikimedia', 'url': ii['thumburl'], 'mini': ii['thumburl'],
                        'pagina': ii.get('descriptionurl'), 'w': ii.get('thumbwidth', 0), 'h': ii.get('thumbheight', 0)})
    return out


def procurar_imagens(pesquisas, n_por_fonte=4, fontes=('pixabay', 'openverse', 'wikimedia')):
    fun = {'pixabay': pixabay, 'openverse': openverse, 'wikimedia': wikimedia}
    vistos, out = set(), []
    for q in pesquisas:
        for nome in fontes:
            try:
                res = fun[nome](q, n_por_fonte)
            except Exception as e:                       # uma fonte em baixo não pára o resto
                print(f'  aviso: {nome} falhou para "{q}": {e}', file=sys.stderr)
                continue
            for r in res:
                if r['url'] not in vistos and min(r.get('w') or 999, r.get('h') or 999) >= 400:
                    vistos.add(r['url'])
                    out.append({**r, 'pesquisa': q})
    return out


def descarregar(url, destino):
    r = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(r, timeout=60) as x:
        pathlib.Path(destino).write_bytes(x.read())
    return destino
