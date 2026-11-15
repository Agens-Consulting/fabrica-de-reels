"""Corta cada B-roll do registo nos seus melhores 8 segundos (até 8; o gerador corta depois para 5, 6, 7 ou 8) (sem IA, só medidas da imagem).

Para cada B-roll (estado diferente de fraco/retirado, com pelo menos 5 s):
  - tira 5 frames por segundo em ponto pequeno;
  - mede em cada frame: nitidez (bordas na imagem inteira), agitação (diferença para o frame anterior)
    e confusão na zona do hook (bordas na faixa y 15-32% do ecrã, onde fica o texto);
  - escolhe a janela de 6 s com melhor pontuação: nítida, movimento estável (sem solavancos de câmara),
    zona do hook calma; evita o primeiro e o último 0,3 s (arranques e paragens da gravação).
  - exporta em 1080x1920, sem som: videos/cortados/<nome>_6s.mp4
  - grava no registo (videos/registo.json) o campo "corte": {ficheiro, inicio_s, duracao_s, pontuacao}.

Uso: $PY videos/cortar.py [--refazer]
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageFilter, ImageStat

RAIZ = pathlib.Path(__file__).resolve().parent.parent
REG = RAIZ / 'videos/registo.json'
OUT = RAIZ / 'videos/cortados'
JANELA, FPS, MARGEM = 8.0, 5, 0.3   # 8 s desde 14/11: a duração do reel é variável de teste (5-8 s)
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402


def duracao(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def medidas(src):
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(src), '-vf',
                        f'fps={FPS},scale=180:320:force_original_aspect_ratio=increase,crop=180:320,format=gray',
                        f'{t}/%05d.png'], check=True)
        fr = sorted(pathlib.Path(t).glob('*.png'))
        out, ant = [], None
        for f in fr:
            im = Image.open(f).convert('L')
            bordas = im.filter(ImageFilter.FIND_EDGES)
            nit = ImageStat.Stat(bordas).mean[0]
            topo = ImageStat.Stat(bordas.crop((10, int(320 * 0.15), 170, int(320 * 0.32)))).mean[0]
            mov = ImageStat.Stat(ImageChops.difference(im, ant)).mean[0] if ant else 0.0
            out.append((nit, topo, mov))
            ant = im
    return out


def melhor_janela(m, dur):
    n = int(JANELA * FPS)
    i0, i1 = int(MARGEM * FPS), len(m) - int(MARGEM * FPS) - n
    if i1 < i0:                                     # vídeo curto: usa tudo menos as margens
        return (MARGEM if dur - 2 * MARGEM >= 5 else 0.0), 0.0
    melhor = None
    for i in range(i0, i1 + 1):
        w = m[i:i + n]
        nit = sum(x[0] for x in w) / n
        topo = sum(x[1] for x in w) / n
        movs = [x[2] for x in w[1:]]
        media = sum(movs) / len(movs)
        solavanco = max(movs) - media              # picos de agitação = câmara a abanar ou corte brusco
        p = nit - 0.6 * topo - 0.8 * solavanco - 0.3 * abs(media - 3)
        if melhor is None or p > melhor[1]:
            melhor = (i / FPS, p)
    return round(melhor[0], 2), round(melhor[1], 2)


def cortar(src, ini, dur, dst):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(ini), '-t', str(dur), '-i', str(src), '-an',
                    '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', str(dst)], check=True)


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--refazer', action='store_true')
    a = a.parse_args()
    OUT.mkdir(exist_ok=True)
    reg = json.loads(REG.read_text(encoding='utf-8'))
    feitos = []
    for k, v in sorted(reg.items(), key=lambda kv: kv[1]['nome']):
        if v.get('estado') in ('fraco', 'retirado') or (v.get('duracao_s') or 0) < 5:
            continue
        dst = OUT / (pathlib.Path(v['ficheiro']).stem + f'_{int(JANELA)}s.mp4')
        if dst.exists() and v.get('corte', {}).get('ficheiro') == dst.relative_to(RAIZ).as_posix() and not a.refazer:
            feitos.append(dst); continue
        src = RAIZ / v['ficheiro']
        dur = duracao(src)
        ini, pont = melhor_janela(medidas(src), dur)
        cortar(src, ini, min(JANELA, dur - ini - (MARGEM if dur - ini > JANELA else 0)), dst)
        v['corte'] = {'ficheiro': dst.relative_to(RAIZ).as_posix(), 'inicio_s': ini,
                      'duracao_s': round(duracao(dst), 2), 'pontuacao': pont}
        REG.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding='utf-8')
        feitos.append(dst)
        print(v['nome'], v['corte'])
    print(f'{len(feitos)} cortes em {OUT.relative_to(RAIZ)}')


if __name__ == '__main__':
    main()
