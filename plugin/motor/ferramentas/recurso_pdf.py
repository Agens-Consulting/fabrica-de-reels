"""PDF de um recurso grátis (A4, 3 a 5 páginas) com a estética da pessoa (MARCA_* do .env).

    $PY ferramentas/recurso_pdf.py recursos/PALAVRA/spec.json            → recursos/PALAVRA/recurso.pdf
    $PY ferramentas/recurso_pdf.py recursos/PALAVRA/spec.json --previa   → também previa_N.png de cada página

spec.json:
{
 "titulo": "A cábula do Claude", "subtitulo": "30 prompts para o dia a dia",
 "paginas": [
   {"titulo": "Antes de começar", "blocos": [
      {"p": "Texto corrido. **negrito** funciona."},
      {"lista": ["um", "dois"]},
      {"passos": ["Abre…", "Escreve…"]},
      {"code": "Prompt para copiar"},
      {"tabela": [["Coluna", "Coluna"], ["a", "b"]]},
      {"nota": "Caixa de destaque"}
   ]}
 ],
 "cta": true
}
A última página (CTA) usa CTA_* do .env: comunidade, Instagram, conversa/site — só os que estiverem preenchidos.
"""
import html as _h
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402

COR = cfg.get('MARCA_COR_PRINCIPAL', '#1F3A5F', obrigatorio=False)
COR2 = cfg.get('MARCA_COR_SECUNDARIA', '#E8EEF6', obrigatorio=False)
LT = cfg.get('MARCA_LETRA_TITULOS', 'Montserrat', obrigatorio=False)
LX = cfg.get('MARCA_LETRA_TEXTO', 'Inter', obrigatorio=False)
NOME = cfg.get('NOME_PESSOA', '', obrigatorio=False)
IG = cfg.get('INSTAGRAM_CONTA', '', obrigatorio=False).lstrip('@')


def inl(t):
    t = _h.escape(str(t))
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', t)


def bloco(b):
    if 'p' in b:
        return f'<p>{inl(b["p"])}</p>'
    if 'lista' in b:
        return '<ul>' + ''.join(f'<li>{inl(x)}</li>' for x in b['lista']) + '</ul>'
    if 'passos' in b:
        return '<ol class="passos">' + ''.join(f'<li>{inl(x)}</li>' for x in b['passos']) + '</ol>'
    if 'code' in b:
        return f'<pre>{_h.escape(b["code"])}</pre>'
    if 'tabela' in b:
        t = b['tabela']
        cab = ''.join(f'<th>{inl(c)}</th>' for c in t[0])
        corpo = ''.join('<tr>' + ''.join(f'<td>{inl(c)}</td>' for c in l) + '</tr>' for l in t[1:])
        return f'<table><thead><tr>{cab}</tr></thead><tbody>{corpo}</tbody></table>'
    if 'nota' in b:
        return f'<div class="nota">{inl(b["nota"])}</div>'
    if 'h' in b:
        return f'<h3>{inl(b["h"])}</h3>'
    return ''


def ctas():
    itens = []
    for chave, rot in (('CTA_COMUNIDADE_LINK', cfg.get('CTA_COMUNIDADE_NOME', 'Entra na comunidade', obrigatorio=False)),
                       ('CTA_INSTAGRAM_LINK', f'Segue @{IG}' if IG else 'Segue no Instagram'),
                       ('CTA_REUNIAO_LINK', 'Marca uma conversa'), ('CTA_SITE_LINK', 'Visita o site')):
        link = cfg.get(chave, '', obrigatorio=False)
        if link:
            itens.append(f'<a class="cta" href="{_h.escape(link)}"><span>{_h.escape(rot)}</span>'
                         f'<small>{_h.escape(link)}</small></a>')
    return ''.join(itens)


def html(spec):
    fam = '&'.join(f'family={f.replace(" ", "+")}:wght@400;500;600;700' for f in dict.fromkeys([LT, LX]))
    rod = _h.escape(NOME + (f' · @{IG}' if IG else ''))
    pags = [f'''<section class="pagina capa"><div class="capa-in">
<div class="marca">{rod}</div><h1>{inl(spec["titulo"])}</h1>
<p class="sub">{inl(spec.get("subtitulo", ""))}</p><div class="barra"></div></div></section>''']
    total = len(spec['paginas']) + 1 + (1 if spec.get('cta', True) else 0)
    for i, pg in enumerate(spec['paginas'], 2):
        corpo = ''.join(bloco(b) for b in pg.get('blocos', []))
        pags.append(f'<section class="pagina"><h2>{inl(pg.get("titulo", ""))}</h2>{corpo}'
                    f'<footer><span>{rod}</span><span>{i}/{total}</span></footer></section>')
    if spec.get('cta', True):
        pags.append(f'<section class="pagina fim"><h2>{inl(spec.get("cta_titulo", "E agora?"))}</h2>'
                    f'<p>{inl(spec.get("cta_texto", "Se isto te ajudou, há mais de onde veio."))}</p>'
                    f'<div class="ctas">{ctas()}</div><footer><span>{rod}</span><span>{total}/{total}</span></footer></section>')
    return f'''<!doctype html><html lang="pt-PT"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fam}&display=swap">
<style>
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}
:root{{--c:{COR};--c2:{COR2};--lt:"{LT}",sans-serif;--lx:"{LX}",sans-serif}}
body{{margin:0;font-family:var(--lx);color:#1d1d1f;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pagina{{width:210mm;height:296.5mm;padding:22mm 20mm 26mm;position:relative;page-break-after:always;overflow:hidden;background:#fff}}
.capa{{background:var(--c);color:#fff;display:flex;align-items:flex-end}}
.capa-in{{width:100%}}.capa .marca{{position:absolute;top:22mm;left:20mm;font:600 11pt var(--lt);letter-spacing:.06em;opacity:.85}}
h1{{font:700 38pt/1.08 var(--lt);margin:0 0 6mm}}.sub{{font-size:15pt;opacity:.9;margin:0 0 10mm}}
.barra{{width:28mm;height:2.2mm;background:var(--c2)}}
h2{{font:700 22pt/1.15 var(--lt);color:var(--c);margin:0 0 8mm}}h3{{font:600 13pt var(--lt);margin:7mm 0 3mm;color:var(--c)}}
p,li,td,th{{font-size:11pt;line-height:1.55}}ul,ol{{padding-left:6mm}}li{{margin:0 0 2mm}}
ol.passos{{counter-reset:n;list-style:none;padding:0}}ol.passos li{{counter-increment:n;padding-left:11mm;position:relative;margin-bottom:4mm}}
ol.passos li:before{{content:counter(n);position:absolute;left:0;top:-.5mm;width:7.5mm;height:7.5mm;border-radius:50%;background:var(--c);color:#fff;font:600 10pt/7.5mm var(--lt);text-align:center}}
pre{{background:var(--c2);border-left:1.4mm solid var(--c);padding:4mm 5mm;font:10pt/1.5 ui-monospace,Menlo,Consolas,monospace;white-space:pre-wrap;margin:0 0 5mm;border-radius:1.5mm}}
code{{background:var(--c2);padding:0 1mm;border-radius:1mm;font-size:.95em}}
table{{width:100%;border-collapse:collapse;margin:2mm 0 6mm}}th{{text-align:left;background:var(--c);color:#fff;padding:2.5mm 3mm;font-weight:600}}
td{{padding:2.5mm 3mm;border-bottom:.3mm solid #e3e3e6;vertical-align:top}}
.nota{{background:var(--c2);padding:5mm 6mm;border-radius:2mm;margin:4mm 0;font-size:11pt}}
footer{{position:absolute;bottom:12mm;left:20mm;right:20mm;display:flex;justify-content:space-between;font-size:8.5pt;color:#8a8a8e}}
.fim .ctas{{display:flex;flex-direction:column;gap:5mm;margin-top:10mm}}
.cta{{display:block;padding:6mm 7mm;border-radius:3mm;background:var(--c);color:#fff;text-decoration:none}}
.cta span{{display:block;font:600 14pt var(--lt)}}.cta small{{opacity:.85;font-size:9.5pt}}
</style></head><body>{"".join(pags)}</body></html>'''


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec_f = pathlib.Path(sys.argv[1])
    spec = json.loads(spec_f.read_text(encoding='utf-8'))
    html_f = spec_f.with_name('recurso.html')
    html_f.write_text(html(spec), encoding='utf-8')
    pdf = cfg.pdf_de_html(html_f, spec_f.with_name('recurso.pdf'))
    print('pdf:', pdf, f'({pdf.stat().st_size // 1024} KB)')
    if '--previa' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={'width': 794, 'height': 1123})
            pg.goto(html_f.resolve().as_uri(), wait_until='networkidle')
            for i, el in enumerate(pg.query_selector_all('.pagina'), 1):
                f = spec_f.with_name(f'previa_{i}.png')
                el.screenshot(path=str(f))
                print('prévia:', f)
            b.close()


if __name__ == '__main__':
    main()
