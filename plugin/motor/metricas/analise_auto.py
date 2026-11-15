"""Tarefa agendada (criada pelo /comecar): todos os dias às 10:00, ao ligar o computador e de 2 em 2 horas.

Só faz alguma coisa quando passaram 14 dias desde o último ciclo (ou desde a linha de base):
aí chama o Claude Code em modo automático para correr a skill fabrica-de-reels:analise-trial-reels.
A análise só corre se a pessoa autorizou o modo automático no /comecar (AUTOMATICO_CLAUDE=sim no .env).
Antes disso, envia sempre os números do caso de estudo à Agens se já for altura (ferramentas/registo.py ciclo).
"""
import os
import pathlib
import subprocess
import sys
from datetime import date, datetime

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402

CICLO_DIAS = 14
os.chdir(RAIZ)
# caso de estudo: números do Instagram para a Agens de 14 em 14 dias (o próprio script vê se já é altura)
subprocess.run([sys.executable, str(RAIZ / 'ferramentas/registo.py'), 'ciclo'], cwd=RAIZ, timeout=3600)
if cfg.get('AUTOMATICO_CLAUDE', 'nao', obrigatorio=False) != 'sim':
    sys.exit(0)
base = RAIZ / 'metricas/perfil/linha-de-base.json'
pc = RAIZ / 'metricas/ciclos'
ciclos = sorted(p.name for p in pc.glob('20*') if p.is_dir()) if pc.exists() else []
ultimo = date.fromisoformat(ciclos[-1]) if ciclos else (
    date.fromtimestamp(base.stat().st_mtime) if base.exists() else None)
if ultimo and (date.today() - ultimo).days < CICLO_DIAS:
    sys.exit(0)
trinca = RAIZ / 'metricas/.analise-a-correr'
try:
    trinca.mkdir()
except FileExistsError:
    if datetime.now().timestamp() - trinca.stat().st_mtime < 6 * 3600:
        sys.exit(0)
try:
    print(f'=== {datetime.now():%Y-%m-%d %H:%M} análise de 14 dias ===', flush=True)
    r = subprocess.run([cfg.claude_cli(), '-p',
                        f'A pasta de trabalho da Fábrica de Reels é {RAIZ}. Usa a skill fabrica-de-reels:analise-trial-reels '
                        'e corre-a do princípio ao fim, de forma totalmente automática, sem fazer perguntas. '
                        'No fim, resume o que concluíste e o que mudaste.',
                        '--dangerously-skip-permissions'], cwd=RAIZ, timeout=3 * 3600)
    print('saída:', r.returncode, flush=True)
    cfg.notificar('Relatório de 14 dias dos trial reels pronto.' if r.returncode == 0
                  else 'A análise de 14 dias falhou. Escreve /reels no Claude para ver.')
finally:
    trinca.rmdir() if trinca.exists() else None
