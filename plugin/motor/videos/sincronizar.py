"""Descarrega da Drive os B-rolls e as músicas novas para videos/raw e audios/raw da pasta de trabalho.

As pastas da Drive (ids DRIVE_PASTA_BROLLS e DRIVE_PASTA_MUSICAS no .env) estão partilhadas por link,
por isso isto corre sozinho, sem chaves (ferramentas/drive_publico.py). Só descarrega o que ainda não está
no registo (por id da Drive). Para cada vídeo novo tira uma miniatura.
  $PY videos/sincronizar.py
"""
import json
import pathlib
import subprocess
import sys
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402
import drive_publico as dp  # noqa: E402

PASTAS = {
    'videos': (cfg.get('DRIVE_PASTA_BROLLS', obrigatorio=False), RAIZ / 'videos', dp.VIDEO),
    'audios': (cfg.get('DRIVE_PASTA_MUSICAS', obrigatorio=False), RAIZ / 'audios', dp.AUDIO),
}


def duracao(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 1)
    except ValueError:
        return None


def main():
    for tipo, (pasta, base, ext) in PASTAS.items():
        if not pasta:
            print(tipo, ': pasta da Drive por configurar no .env'); continue
        raw = base / 'raw'
        raw.mkdir(parents=True, exist_ok=True)
        reg_f = base / 'registo.json'
        reg = json.loads(reg_f.read_text(encoding='utf-8')) if reg_f.exists() else {}
        novos = 0
        try:
            lista = dp.ficheiros(pasta, ext)
        except Exception as ex:
            print(tipo, ': não consegui ler a pasta da Drive:', ex); continue
        for f in lista:
            if f['id'] in reg:
                continue
            destino = raw / f"{f['id'][:8]}_{f['nome']}"
            try:
                dp.baixar(f['id'], destino)
            except Exception as ex:
                print('falhou', f['nome'], ex); continue
            e = {'nome': f['nome'], 'ficheiro': destino.relative_to(RAIZ).as_posix(), 'drive_id': f['id'],
                 'descarregado': datetime.now().isoformat(timespec='seconds'), 'duracao_s': duracao(destino),
                 'estado': 'novo', 'tipo': None, 'notas': ''}
            if tipo == 'videos':
                mini = base / 'miniaturas'
                mini.mkdir(exist_ok=True)
                meio = (e['duracao_s'] or 2) / 2
                m = mini / (destino.stem + '.jpg')
                subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(meio), '-i', str(destino),
                                '-frames:v', '1', '-vf', 'scale=360:-2', str(m)])
                e['miniatura'] = m.relative_to(RAIZ).as_posix()
            reg[f['id']] = e
            reg_f.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding='utf-8')
            novos += 1
            print('novo', tipo, f['nome'])
        print(f'{tipo}: {novos} novos, {len(reg)} no registo')


if __name__ == '__main__':
    main()
