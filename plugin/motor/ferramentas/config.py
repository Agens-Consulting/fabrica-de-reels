"""Configuração da pasta de trabalho: tudo o que é pessoal ou privado vem do .env da raiz.

O código não tem nada da pessoa (chaves, contas, pastas, links, marca). Para pôr isto a correr para
outra pessoa: copiar .env.exemplo para .env, preencher, e pôr a credencial da Google em .credenciais/.

    import sys, pathlib; sys.path.insert(0, str(<raiz> / 'ferramentas'))
    import config as cfg
    cfg.get('ZERNIO_API_KEY'); cfg.caminho('FONTE_FICHEIRO'); cfg.cores_destaque(); cfg.hora('HORA_INICIO')
"""
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENV = RAIZ / '.env'
_cache = None


def _ler():
    global _cache
    if _cache is None:
        if not ENV.exists():
            sys.exit(f'Falta o ficheiro {ENV}. Copia .env.exemplo para .env e preenche-o.')
        _cache = {}
        for linha in ENV.read_text(encoding='utf-8').splitlines():
            linha = linha.strip()
            if linha and not linha.startswith('#') and '=' in linha:
                k, v = linha.split('=', 1)
                _cache[k.strip()] = v.strip().strip('"').strip("'")
    return _cache


def get(nome, defeito=None, obrigatorio=True):
    v = _ler().get(nome) or defeito
    if v is None and obrigatorio:
        sys.exit(f'{nome} não está preenchido no .env')
    return v


def caminho(nome):
    """Valor do .env como caminho; relativo à raiz do projeto se não for absoluto."""
    p = pathlib.Path(get(nome)).expanduser()
    return p if p.is_absolute() else RAIZ / p


def lista(nome):
    return [x.strip() for x in get(nome, '', obrigatorio=False).split(',') if x.strip()]


def cores_destaque():
    """[(hex, (r, g, b)), ...] pela ordem do .env."""
    out = []
    for h in lista('CORES_DESTAQUE') or ['#F4EE00']:
        h = h.lstrip('#')
        out.append(('#' + h.upper(), tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))))
    return out


def hora(nome):
    """'09:00' → 9.0; '20:30' → 20.5"""
    h, m = get(nome).split(':')
    return int(h) + int(m) / 60


def conta():
    """Conta de Instagram, sempre com @."""
    return '@' + get('INSTAGRAM_CONTA').lstrip('@')


# --- sistema (Mac e Windows) --------------------------------------------------------------------------
import os as _os
import platform as _plat
import shutil as _shutil
import subprocess as _sp

WINDOWS = _plat.system() == 'Windows'


def venv_bin(nome):
    """Executável do .venv do projeto (python, whisper, yt-dlp…), em Mac/Linux ou Windows."""
    if WINDOWS:
        p = RAIZ / '.venv' / 'Scripts' / (nome + '.exe')
    else:
        p = RAIZ / '.venv' / 'bin' / nome
    return p


PY = venv_bin('python')


def fonte_emoji():
    """Fonte de emoji do sistema, se houver (as bandeiras vêm de PNG em assets/)."""
    for f in ('/System/Library/Fonts/Apple Color Emoji.ttc', r'C:\Windows\Fonts\seguiemj.ttf',
              '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'):
        if pathlib.Path(f).exists():
            return f
    return None


def claude_cli():
    return _shutil.which('claude') or _shutil.which('claude.cmd') or 'claude'


def pdf_de_html(html, pdf, largura='A4'):
    """HTML → PDF com o Chromium do Playwright (instalado no .venv pelo instalar.py)."""
    from playwright.sync_api import sync_playwright
    html, pdf = pathlib.Path(html).resolve(), pathlib.Path(pdf)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html.as_uri() + '?tema=claro', wait_until='networkidle')
        pg.emulate_media(media='print')
        pg.pdf(path=str(pdf), format=largura, print_background=True,
               margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'}, prefer_css_page_size=True)
        b.close()
    return pdf


def notificar(texto, titulo='Reels de Teste'):
    """Notificação no ecrã; nunca falha."""
    try:
        if _plat.system() == 'Darwin':
            _sp.run(['osascript', '-e', f'display notification "{texto}" with title "{titulo}"'], timeout=10)
        elif WINDOWS:
            ps = ('[reflection.assembly]::loadwithpartialname("System.Windows.Forms")|Out-Null;'
                  '$n=New-Object System.Windows.Forms.NotifyIcon;$n.Icon=[System.Drawing.SystemIcons]::Information;'
                  f'$n.Visible=$true;$n.ShowBalloonTip(8000,"{titulo}","{texto}",0);Start-Sleep 9')
            _sp.Popen(['powershell', '-NoProfile', '-Command', ps])
    except Exception:
        pass
    pend = RAIZ / 'avisos.txt'   # o comando /reels mostra isto na próxima conversa
    with open(pend, 'a', encoding='utf-8') as f:
        from datetime import datetime as _dt
        f.write(f'{_dt.now():%Y-%m-%d %H:%M} · {texto}\n')
