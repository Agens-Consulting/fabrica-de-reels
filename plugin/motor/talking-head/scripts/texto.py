"""Texto queimado no vídeo: hook (topo) e legendas (3 palavras de cada vez).

Hook: estilo fixo dos Reels de Teste (hooks/estetica-e-posicionamento.md): Montserrat SemiBold,
branco, contorno preto 3 px, sombra quase invisível, centro em y=432, largura útil 900 px, máx. 3 linhas,
1 palavra de destaque (2 no máximo) com a cor escolhida pelo fundo.

Legendas: Montserrat SemiBold branca, contorno preto, sem itálico nem efeitos. Uma linha, centro em
y = 80% da altura (a posição da skill /legendas: --position lower --marginv 0.20).
"""
import math
import pathlib
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

import sys
AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI.parent / 'ferramentas'))
import config as cfg  # noqa: E402
ASSETS = AQUI / 'assets'
FONTE = str(cfg.caminho('FONTE_FICHEIRO'))
PESO = cfg.get('FONTE_PESO', 'SemiBold').encode()
EMOJI = cfg.fonte_emoji()   # Mac: Apple Color Emoji; Windows: Segoe UI Emoji
W, H = 1080, 1920

# hook
TAM_HOOK, TAM_HOOK_MIN, ENTRELINHA, LARGURA_UTIL, CENTRO_HOOK = 52, 40, 1.12, 900, 432
CONTORNO = 3
PALETA = cfg.cores_destaque()   # do .env, a 1.ª é a de defeito
DELTA_E_MIN = 40

# legendas
TAM_LEG, TAM_LEG_MIN, CONTORNO_LEG = 62, 44, 4
CENTRO_LEG = int(H * 0.80)          # = /legendas --marginv 0.20
LARGURA_LEG = 900


def fonte(size, peso=None):
    f = ImageFont.truetype(FONTE, size)
    f.set_variation_by_name(peso or PESO)
    return f


# --- emoji (bandeira 🇵🇹 e afins vêm de PNG; o Pillow sem raqm não junta indicadores regionais) ---------
def e_emoji(c):
    o = ord(c)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D)


def fatias(linha):
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


def img_emoji(txt, altura):
    png = ASSETS / ('emoji_' + '_'.join(f'{ord(c):x}' for c in txt) + '.png')
    if png.exists():
        im = Image.open(png).convert('RGBA')
    else:
        if not EMOJI:
            return Image.new('RGBA', (1, altura), (0, 0, 0, 0))
        f = ImageFont.truetype(EMOJI, 160)
        im = Image.new('RGBA', (int(f.getlength(txt)) + 10, 200), (0, 0, 0, 0))
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


# --- cor de destaque pelo fundo -----------------------------------------------------------------------
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
    x0, y0, x1, y1 = caixa
    zona = (max(0, x0 - 40), max(0, y0 - 40), min(W, x1 + 40), min(H, y1 + 40))
    medias = [ImageStat.Stat(Image.open(f).convert('RGB').crop(zona)).mean for f in frames]
    fundo = tuple(sum(m[i] for m in medias) / len(medias) for i in range(3))
    lf = srgb_lab(fundo)
    for nome, rgb in PALETA:
        if math.dist(lf, srgb_lab(rgb)) >= DELTA_E_MIN:
            return nome, rgb
    return PALETA[0]


# --- desenho ------------------------------------------------------------------------------------------
def _palavra(img, xy, txt, f, cor, contorno):
    """Contorno preto nítido + sombra quase invisível (2 px abaixo, desfoque 4, ~35%)."""
    s = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).text((xy[0], xy[1] + 2), txt, font=f, fill=(0, 0, 0, 90),
                           stroke_width=contorno, stroke_fill=(0, 0, 0, 90))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(img).text(xy, txt, font=f, fill=(*cor, 255), stroke_width=contorno, stroke_fill=(0, 0, 0, 255))


def tamanho_hook(linhas):
    size = TAM_HOOK
    while size > TAM_HOOK_MIN and max(largura_linha(l, fonte(size), size) for l in linhas) > LARGURA_UTIL:
        size -= 2
    return size


def caixa_hook(linhas):
    size = tamanho_hook(linhas)
    lh = int(size * ENTRELINHA)
    alto = lh * len(linhas)
    larg = max(largura_linha(l, fonte(size), size) for l in linhas)
    return int((W - larg) / 2), int(CENTRO_HOOK - alto / 2), int((W + larg) / 2), int(CENTRO_HOOK + alto / 2)


def png_hook(linhas, destaque, cor_dest):
    size = tamanho_hook(linhas)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f = fonte(size)
    lh = int(size * ENTRELINHA)
    asc, desc = f.getmetrics()
    y0 = CENTRO_HOOK - lh * len(linhas) / 2
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
                    _palavra(img, (x, y), p, f, cor, CONTORNO)
                x += f.getlength(p)
    return img


def png_legenda(texto):
    size = TAM_LEG
    while size > TAM_LEG_MIN and fonte(size).getlength(texto) > LARGURA_LEG:
        size -= 2
    f = fonte(size)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    asc, desc = f.getmetrics()
    x = (W - f.getlength(texto)) / 2
    y = CENTRO_LEG - (asc + desc) / 2
    _palavra(img, (x, y), texto, f, (255, 255, 255), CONTORNO_LEG)
    return img


def png_vazio():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


# imagem por frase: plana, sem cantos nem efeitos, acima da cabeça
IMG_MAX_W, IMG_MAX_H, IMG_CENTRO_Y = 760, 540, 480


def png_imagem(caminho):
    src = Image.open(caminho).convert('RGB')
    esc = min(IMG_MAX_W / src.width, IMG_MAX_H / src.height)
    nova = src.resize((max(1, int(src.width * esc)), max(1, int(src.height * esc))), Image.LANCZOS)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    img.paste(nova, ((W - nova.width) // 2, IMG_CENTRO_Y - nova.height // 2))
    return img
