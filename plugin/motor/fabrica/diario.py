"""Tarefa agendada diária (criada pelo /comecar: launchd no Mac, Agendador de Tarefas no Windows).

Corre às 06:00, ao ligar o computador e de hora a hora, mas só trabalha uma vez por dia:
descarrega B-rolls/músicas novos, corta-os, recolhe as métricas e agenda os reels do dia.
Se o computador esteve desligado de manhã, faz tudo quando ligar (e agenda só as horas que faltam).
"""
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402

PY = str(cfg.PY)
os.chdir(RAIZ)
hoje = datetime.now(ZoneInfo(cfg.get('FUSO', 'Europe/Lisbon'))).date()
feito = RAIZ / f'fabrica/.feito-{hoje}'
if feito.exists() or cfg.get('FABRICA_LIGADA', 'sim', obrigatorio=False) != 'sim':
    sys.exit(0)
trinca = RAIZ / 'fabrica/.a-correr'
try:
    trinca.mkdir()
except FileExistsError:
    if datetime.now().timestamp() - trinca.stat().st_mtime < 3 * 3600:
        sys.exit(0)                                  # outra execução ainda a correr
try:
    print(f'=== {datetime.now():%Y-%m-%d %H:%M} ===', flush=True)
    for script, log in (('videos/sincronizar.py', 'videos/sincronizar.log'), ('videos/cortar.py', 'videos/cortar.log')):
        with open(log, 'a', encoding='utf-8') as f:
            subprocess.run([PY, script], stdout=f, stderr=f)
    with open('metricas/recolher.log', 'a', encoding='utf-8') as f:   # métricas do perfil e de cada reel
        subprocess.run([PY, 'metricas/recolher.py', 'tudo'], stdout=f, stderr=f)
    r = subprocess.run([PY, 'fabrica/gerar_reel.py', 'dia'])
    if r.returncode == 0:
        feito.touch()
        for f in (RAIZ / 'fabrica').glob('.feito-*'):
            if f.name < f'.feito-{hoje - timedelta(days=7)}':
                f.unlink()
    else:
        cfg.notificar('A fábrica de hoje falhou. Abre o Claude e escreve /reels para ver.')
finally:
    trinca.rmdir() if trinca.exists() else None
