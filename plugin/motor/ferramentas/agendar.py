"""Liga, desliga ou mostra as tarefas automáticas, em Mac (launchd) ou Windows (Agendador de Tarefas).

    $PY ferramentas/agendar.py ligar      # cria/atualiza as 3 tarefas
    $PY ferramentas/agendar.py desligar
    $PY ferramentas/agendar.py estado

Tarefas (todas correm ferramentas/tarefa.py com o Python do .venv):
  diario  — às 06:00 e de hora a hora (só trabalha 1 vez por dia): B-rolls, métricas, reels do dia
  analise — de 2 em 2 horas (só trabalha de 14 em 14 dias): análise e relatório (Claude)
  vigia   — de 15 em 15 minutos: vídeo novo na RAW → edita e publica (Claude)
"""
import json
import os
import pathlib
import platform
import plistlib
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'ferramentas'))
import config as cfg  # noqa: E402

TAREFA = RAIZ / 'ferramentas' / 'tarefa.py'
NOMES = {'diario': 3600, 'analise': 7200, 'vigia': 900}   # intervalo em segundos
SISTEMA = platform.system()
ROTULO = 'pt.reelsdeteste.'


def _python_sem_janela():
    if cfg.WINDOWS:
        p = cfg.venv_bin('pythonw')
        return p if p.exists() else cfg.PY
    return cfg.PY


# --- Mac ----------------------------------------------------------------------------------------------
def _plist(nome):
    return pathlib.Path.home() / 'Library/LaunchAgents' / f'{ROTULO}{nome}.plist'


def mac_ligar():
    caminho = os.pathsep.join(dict.fromkeys(
        [str(pathlib.Path(shutil.which('claude') or '/usr/local/bin/claude').parent),
         str(pathlib.Path(shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg').parent),
         '/opt/homebrew/bin', '/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin']))
    for nome, seg in NOMES.items():
        d = {'Label': ROTULO + nome, 'ProgramArguments': [str(cfg.PY), str(TAREFA), nome],
             'WorkingDirectory': str(RAIZ), 'RunAtLoad': True, 'StartInterval': seg,
             'EnvironmentVariables': {'PATH': caminho, 'PYTHONUTF8': '1', 'HOME': str(pathlib.Path.home())},
             'StandardOutPath': str(RAIZ / 'registos' / f'{nome}.launchd.log'),
             'StandardErrorPath': str(RAIZ / 'registos' / f'{nome}.launchd.log')}
        if nome == 'diario':
            d['StartCalendarInterval'] = {'Hour': 6, 'Minute': 0}
        (RAIZ / 'registos').mkdir(exist_ok=True)
        p = _plist(nome)
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['launchctl', 'unload', str(p)], capture_output=True)
        p.write_bytes(plistlib.dumps(d))
        subprocess.run(['launchctl', 'load', str(p)], check=True)
        print('ligada:', ROTULO + nome)


def mac_desligar():
    for nome in NOMES:
        p = _plist(nome)
        if p.exists():
            subprocess.run(['launchctl', 'unload', str(p)], capture_output=True)
            p.unlink()
            print('desligada:', ROTULO + nome)


def mac_estado():
    out = subprocess.run(['launchctl', 'list'], capture_output=True, text=True).stdout
    return {n: (ROTULO + n) in out for n in NOMES}


# --- Windows ------------------------------------------------------------------------------------------
def _tn(nome):
    return f'ReelsDeTeste\\{nome}'


def win_ligar():
    py = _python_sem_janela()
    for nome, seg in NOMES.items():
        tr = f'"{py}" "{TAREFA}" {nome}'
        cmd = ['schtasks', '/Create', '/F', '/TN', _tn(nome), '/TR', tr, '/SC', 'MINUTE', '/MO', str(seg // 60)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f'Não consegui criar a tarefa {nome}: {r.stderr or r.stdout}')
        if nome == 'diario':   # também às 06:00 e ao iniciar sessão
            subprocess.run(['schtasks', '/Create', '/F', '/TN', _tn('diario-0600'), '/TR', tr, '/SC', 'DAILY',
                            '/ST', '06:00'], capture_output=True)
            subprocess.run(['schtasks', '/Create', '/F', '/TN', _tn('diario-login'), '/TR', tr, '/SC', 'ONLOGON'],
                           capture_output=True)
        print('ligada:', _tn(nome))


def win_desligar():
    for nome in list(NOMES) + ['diario-0600', 'diario-login']:
        r = subprocess.run(['schtasks', '/Delete', '/F', '/TN', _tn(nome)], capture_output=True)
        if r.returncode == 0:
            print('desligada:', _tn(nome))


def win_estado():
    return {n: subprocess.run(['schtasks', '/Query', '/TN', _tn(n)], capture_output=True).returncode == 0 for n in NOMES}


def main():
    acao = sys.argv[1] if len(sys.argv) > 1 else 'estado'
    if SISTEMA == 'Darwin':
        f = {'ligar': mac_ligar, 'desligar': mac_desligar, 'estado': lambda: print(json.dumps(mac_estado()))}
    elif SISTEMA == 'Windows':
        f = {'ligar': win_ligar, 'desligar': win_desligar, 'estado': lambda: print(json.dumps(win_estado()))}
    else:
        sys.exit('Sistema não suportado para tarefas automáticas (só Mac e Windows).')
    if acao not in f:
        sys.exit(__doc__)
    f[acao]()


if __name__ == '__main__':
    main()
