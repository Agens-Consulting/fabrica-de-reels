"""Instala ou atualiza a pasta de trabalho dos Reels de Teste (Mac e Windows). Só usa a biblioteca padrão.

    python3 <plugin>/motor/ferramentas/instalar.py <pasta de trabalho> [--sem-modelos]

1. Copia o motor (scripts e guias) do plugin para a pasta. Nunca apaga nem substitui dados da pessoa:
   .env, banco/, recursos/, históricos, registos, vídeos e músicas.
2. Cria os ficheiros iniciais que faltem (.env a partir do .env.exemplo, banco vazio…).
3. Garante o ffmpeg (Mac: Homebrew; Windows: winget) e cria o .venv com as bibliotecas.
4. Descarrega o Chromium do Playwright (PDFs) e o modelo medium do Whisper (~1,5 GB).
5. Grava o caminho da pasta em ~/.reels-de-teste/pasta.txt (é assim que as skills a encontram).
No fim imprime uma linha JSON com o estado de cada passo.
"""
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys

MOTOR = pathlib.Path(__file__).resolve().parent.parent
WINDOWS = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'
PONTEIRO = pathlib.Path.home() / '.reels-de-teste' / 'pasta.txt'
PACOTES = ['pillow', 'numpy', 'openai-whisper', 'playwright', 'yt-dlp']
# ficheiros e pastas que são dados da pessoa: nunca se substituem
DADOS = ('.env', 'banco/', 'recursos/', 'ctas/automacoes', 'fabrica/historico.jsonl', 'fabrica/saida/',
         'talking-head/estado.json', 'talking-head/historico.jsonl', 'talking-head/trabalho/',
         'talking-head/publicados/', 'videos/raw/', 'videos/cortados/', 'videos/miniaturas/', 'videos/registo.json',
         'audios/', 'metricas/ciclos/', 'metricas/perfil/', 'metricas/reels', 'registos/', 'onboarding/', 'avisos.txt')
MODELOS_INICIAIS = {'banco/textos.json': '[]\n', 'banco/recursos.json': '[]\n', 'avisos.txt': '',
                    'recursos/lista.md': '# Recursos\n\n## Ativos\n\n## Em espera\n\n## Arquivados\n'}


def passo(nome, ok, info=''):
    print(('OK   ' if ok else 'FALTA ') + nome + (f' · {info}' if info else ''), flush=True)
    return {'ok': bool(ok), 'info': info}


def copiar_motor(dest):
    n = 0
    for f in MOTOR.rglob('*'):
        rel = f.relative_to(MOTOR).as_posix()
        if f.is_dir() or '__pycache__' in rel or rel.startswith('_modelos/'):
            continue
        alvo = dest / rel
        if any(rel == d or rel.startswith(d) for d in DADOS) and alvo.exists() and f.name != 'README.md':
            continue
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, alvo)
        n += 1
    for rel, conteudo in MODELOS_INICIAIS.items():
        alvo = dest / rel
        if not alvo.exists():
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(conteudo, encoding='utf-8')
    env = dest / '.env'
    if not env.exists():
        shutil.copy2(MOTOR / '.env.exemplo', env)
    else:   # acrescenta chaves novas do exemplo, sem tocar nas que existem
        tem = {l.split('=', 1)[0].strip() for l in env.read_text(encoding='utf-8').splitlines() if '=' in l}
        novas = [l for l in (MOTOR / '.env.exemplo').read_text(encoding='utf-8').splitlines()
                 if '=' in l and not l.lstrip().startswith('#') and l.split('=', 1)[0].strip() not in tem]
        if novas:
            with open(env, 'a', encoding='utf-8') as fh:
                fh.write('\n' + '\n'.join(novas) + '\n')
    if not WINDOWS:
        os.chmod(env, 0o600)
    for d in ('videos/raw', 'audios/raw', 'registos', 'onboarding', 'talking-head/trabalho'):
        (dest / d).mkdir(parents=True, exist_ok=True)
    return n


def versao_ffmpeg(exe):
    try:
        out = subprocess.run([exe, '-version'], capture_output=True, text=True, timeout=30).stdout
        m = re.search(r'ffmpeg version n?(\d+)', out)
        return int(m.group(1)) if m else 99   # builds "git-…" contam como recentes
    except Exception:
        return 0


def achar_ffmpeg():
    cands = [shutil.which('ffmpeg'), '/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg',
             str(pathlib.Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft/WinGet/Links/ffmpeg.exe')]
    for c in cands:
        if c and pathlib.Path(c).exists():
            return c
    return None


def garantir_ffmpeg():
    f = achar_ffmpeg()
    if f and versao_ffmpeg(f) >= 7:
        return passo('ffmpeg', True, f)
    if MAC and shutil.which('brew'):
        subprocess.run(['brew', 'install', 'ffmpeg'] if not f else ['brew', 'upgrade', 'ffmpeg'])
    elif WINDOWS and shutil.which('winget'):
        subprocess.run(['winget', 'install', '--id', 'Gyan.FFmpeg', '-e', '--accept-source-agreements',
                        '--accept-package-agreements'])
    f = achar_ffmpeg()
    if f and versao_ffmpeg(f) >= 7:
        return passo('ffmpeg', True, f + ' (instalado agora; se o terminal não o encontrar, reinicia o Claude Code)')
    dica = ('instala o Homebrew (https://brew.sh) e corre: brew install ffmpeg' if MAC else
            'corre no PowerShell: winget install --id Gyan.FFmpeg -e' if WINDOWS else 'instala o ffmpeg 7 ou mais recente')
    return passo('ffmpeg', False, dica)


def python_bom():
    """Um Python 3.10–3.12 (o Whisper e o Torch ainda não gostam do 3.13+)."""
    cands = []
    if WINDOWS:
        for v in ('3.12', '3.11', '3.10'):
            cands.append(['py', f'-{v}'])
    cands += [[sys.executable], ['python3.12'], ['python3.11'], ['python3.10'], ['python3'], ['python']]
    for c in cands:
        try:
            out = subprocess.run(c + ['-c', 'import sys;print(sys.version_info[:2])'], capture_output=True,
                                 text=True, timeout=30).stdout.strip()
            m = re.match(r'\((\d+), (\d+)\)', out)
            if m and (3, 10) <= (int(m.group(1)), int(m.group(2))) <= (3, 12):
                return c
        except Exception:
            continue
    return None


def garantir_venv(dest):
    py = dest / ('.venv/Scripts/python.exe' if WINDOWS else '.venv/bin/python')
    if not py.exists():
        base = python_bom()
        if not base:
            if MAC and shutil.which('brew'):
                subprocess.run(['brew', 'install', 'python@3.12'])
            elif WINDOWS and shutil.which('winget'):
                subprocess.run(['winget', 'install', '--id', 'Python.Python.3.12', '-e', '--accept-source-agreements',
                                '--accept-package-agreements'])
            base = python_bom()
        if not base:
            return passo('python', False, 'instala o Python 3.12 (python.org) e volta a correr o /comecar'), None
        subprocess.run(base + ['-m', 'venv', str(dest / '.venv')], check=True)
    r = subprocess.run([str(py), '-m', 'pip', 'install', '-q', '--upgrade', 'pip'] , capture_output=True)
    r = subprocess.run([str(py), '-m', 'pip', 'install', '-q'] + PACOTES, capture_output=True, text=True)
    if r.returncode != 0:
        return passo('bibliotecas', False, (r.stderr or r.stdout)[-400:]), py
    return passo('python e bibliotecas', True, str(py)), py


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dest = pathlib.Path(os.path.expanduser(sys.argv[1])).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    estado = {'pasta': str(dest)}
    estado['motor'] = passo('motor copiado', True, f'{copiar_motor(dest)} ficheiros')
    PONTEIRO.parent.mkdir(parents=True, exist_ok=True)
    PONTEIRO.write_text(str(dest), encoding='utf-8')
    if WINDOWS:   # acentos e emojis certos em todos os scripts
        subprocess.run(['setx', 'PYTHONUTF8', '1'], capture_output=True)
    estado['ffmpeg'] = garantir_ffmpeg()
    estado['python'], py = garantir_venv(dest)
    if py and estado['python']['ok']:
        r = subprocess.run([str(py), '-m', 'playwright', 'install', 'chromium'], capture_output=True, text=True)
        estado['chromium'] = passo('Chromium (PDFs)', r.returncode == 0, '' if r.returncode == 0 else r.stderr[-300:])
        if '--sem-modelos' not in sys.argv:
            mod = dest / 'ferramentas/modelos-whisper'
            mod.mkdir(parents=True, exist_ok=True)
            r = subprocess.run([str(py), '-c', f'import whisper; whisper.load_model("medium", download_root=r"{mod}")'],
                               capture_output=True, text=True)
            estado['whisper'] = passo('modelo Whisper medium', r.returncode == 0,
                                      '' if r.returncode == 0 else r.stderr[-300:])
    print('ESTADO ' + json.dumps(estado, ensure_ascii=False))


if __name__ == '__main__':
    main()
