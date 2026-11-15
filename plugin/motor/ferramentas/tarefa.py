"""Ponto de entrada das tarefas agendadas (Mac: launchd; Windows: Agendador de Tarefas).

    <python do .venv> ferramentas/tarefa.py diario|analise|vigia

Põe o ambiente certo (UTF-8, PATH com ffmpeg e claude), escreve o registo em registos/<tarefa>.log e corre
o script da tarefa. No Windows, nada abre janelas.
"""
import os
import pathlib
import runpy
import subprocess
import sys
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = {'diario': 'fabrica/diario.py', 'analise': 'metricas/analise_auto.py',
           'vigia': ('talking-head/scripts/th.py', 'vigiar')}

os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
extra = [str(pathlib.Path.home() / '.local/bin'), '/opt/homebrew/bin', '/usr/local/bin',
         str(pathlib.Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft/WinGet/Links'),
         str(pathlib.Path(os.environ.get('APPDATA', '')) / 'npm')]
os.environ['PATH'] = os.pathsep.join([os.environ.get('PATH', '')] + [p for p in extra if p and os.path.isdir(p)])

if os.name == 'nt':   # sem janelas de consola em nada do que se lança daqui
    _init = subprocess.Popen.__init__

    def _sem_janela(self, *a, **k):
        k.setdefault('creationflags', 0x08000000)  # CREATE_NO_WINDOW
        _init(self, *a, **k)
    subprocess.Popen.__init__ = _sem_janela


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SCRIPTS:
        sys.exit(__doc__)
    nome = sys.argv[1]
    logs = RAIZ / 'registos'
    logs.mkdir(exist_ok=True)
    log = open(logs / f'{nome}.log', 'a', encoding='utf-8', buffering=1)
    for fd in (1, 2):   # também apanha o que os subprocessos escrevem
        try:
            os.dup2(log.fileno(), fd)
        except OSError:
            pass
    sys.stdout = sys.stderr = log
    print(f'--- {datetime.now():%Y-%m-%d %H:%M:%S} {nome}')
    alvo = SCRIPTS[nome]
    script, args = (alvo, []) if isinstance(alvo, str) else (alvo[0], list(alvo[1:]))
    os.chdir(RAIZ)
    sys.path.insert(0, str((RAIZ / script).parent))
    sys.argv = [str(RAIZ / script)] + args
    try:
        runpy.run_path(str(RAIZ / script), run_name='__main__')
    except SystemExit as e:
        if e.code not in (0, None):
            print('saída:', e.code)
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
