"""Ler pastas da Google Drive partilhadas por link ("qualquer pessoa com o link pode ver"), sem chaves.

As pastas RAW, B-rolls e Músicas são partilhadas por link no /comecar (pela ligação Google Drive do
Claude). Assim os scripts automáticos leem-nas e descarregam os vídeos sozinhos, sem conta-robô, sem app
e sem login, em Mac e Windows. Escrever na Drive (arquivar, recursos) só se faz em conversa, pela ligação.

    $PY ferramentas/drive_publico.py listar <id_pasta> [--recursivo]
    $PY ferramentas/drive_publico.py baixar <id_ficheiro> <destino>
"""
import html as _html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (reels-de-teste)'}
VIDEO = ('.mp4', '.mov', '.m4v', '.avi', '.mkv', '.webm', '.hevc', '.3gp')
AUDIO = ('.mp3', '.m4a', '.wav', '.aac', '.ogg', '.flac')


def _get(url, tentativas=3):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(3 * (i + 1))


def listar(pasta, recursivo=False, _caminho=''):
    """[{id, nome, pasta (bool), caminho}] — só funciona em pastas partilhadas por link."""
    h = _get(f'https://drive.google.com/embeddedfolderview?id={pasta}#list')
    if 'flip-entry' not in h and ('ServiceLogin' in h or 'accounts.google.com' in h):
        raise PermissionError(f'A pasta {pasta} não está partilhada por link (qualquer pessoa com o link pode ver).')
    out = []
    for bloco in re.findall(r'<div class="flip-entry" id="entry-([\w-]+)"(.*?)</a>', h, re.S):
        fid, corpo = bloco
        m = re.search(r'<div class="flip-entry-title">(.*?)</div>', corpo, re.S)
        nome = _html.unescape(m.group(1)).strip() if m else fid
        e_pasta = '/drive/folders/' in corpo
        item = {'id': fid, 'nome': nome, 'pasta': e_pasta, 'caminho': f'{_caminho}{nome}'}
        out.append(item)
        if e_pasta and recursivo:
            out += listar(fid, True, f'{_caminho}{nome}/')
    return out


def ficheiros(pasta, extensoes=VIDEO, recursivo=False):
    return [f for f in listar(pasta, recursivo) if not f['pasta'] and f['nome'].lower().endswith(extensoes)]


def baixar(fid, destino):
    """Descarrega um ficheiro partilhado por link (qualquer tamanho; trata o aviso de antivírus da Google)."""
    destino = pathlib.Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    url = f'https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t'
    for _ in range(3):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=900) as r:
            tipo = r.headers.get('Content-Type', '')
            if 'text/html' in tipo:   # página de confirmação: lê o formulário e segue
                pag = r.read().decode('utf-8', errors='replace')
                acao = re.search(r'<form[^>]+action="([^"]+)"', pag)
                campos = dict(re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]*)"', pag))
                if not acao or not campos:
                    raise PermissionError(f'Ficheiro {fid} não está acessível por link.')
                url = _html.unescape(acao.group(1)) + '?' + urllib.parse.urlencode(campos)
                continue
            tmp = destino.with_suffix(destino.suffix + '.parcial')
            with open(tmp, 'wb') as f:
                while True:
                    bloco = r.read(4 * 1024 * 1024)
                    if not bloco:
                        break
                    f.write(bloco)
            tmp.replace(destino)
            return destino
    raise RuntimeError(f'Não consegui descarregar {fid}.')


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == 'listar':
        print(json.dumps(listar(a[1], '--recursivo' in a), ensure_ascii=False, indent=1))
    elif len(a) == 3 and a[0] == 'baixar':
        print(baixar(a[1], a[2]))
    else:
        sys.exit(__doc__)
