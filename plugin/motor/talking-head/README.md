# Reels talking head

Trial reels em que o dono da conta fala para a câmara. Grava (de preferência na rua), com espaço por cima da cabeça, e carrega o vídeo para a pasta RAW da Drive. O Claude edita e publica tudo sozinho. Projeto isolado: tudo o que usa está nesta pasta.

## Como se usa
1. Grava o vídeo com espaço por cima da cabeça.
2. No telemóvel: Galeria → Partilhar → **Drive** → a tua pasta **RAW** dos talking heads (a que o `/reels-de-teste:comecar` criou; o id está em `DRIVE_PASTA_TALKING_HEAD_RAW` no `.env`) → Carregar.
3. Mais nada. Quando o vídeo estiver publicado, as variantes e as legendas ficam no disco, em **`talking-head/publicados/<slug>/`**, e o vídeo bruto passa da RAW para a pasta **PUBLICADOS** da Drive.

## O que acontece
A tarefa agendada `vigia` corre `scripts/th.py vigiar` de 15 em 15 minutos. A pasta RAW está partilhada por link (só leitura), por isso o script vê os vídeos novos sem chaves (`../ferramentas/drive_publico.py`). Quando há um vídeo novo, chama o Claude com a skill `reels-de-teste:reel-talking-head`, que segue estes passos:

**descarregar → transcrever → plano (cortes, frases, hooks, legenda, recurso) → imagens grátis → render das 2-3 variantes → verificar → publicar como trial reel MANUAL → arquivar**

O arquivo na Drive (mover o bruto da RAW para PUBLICADOS) é feito pelo Claude numa conversa, com o conector "Google Drive" do Claude. Se o Claude correu sozinho e não teve acesso ao conector, o bruto fica na RAW e é movido na conversa seguinte (`scripts/th.py por-arquivar` lista os que faltam). O vigia só chama o Claude com `AUTOMATICO_CLAUDE=sim` no `.env`.

## Pastas
| | |
|---|---|
| `scripts/th.py` | o motor (corte, áudio, camadas, publicação, vigia) |
| `scripts/texto.py` | hook, legendas e imagem no ecrã |
| `scripts/servicos.py` | Drive (leitura por link), Zernio e bancos de imagens |
| `../audios/raw/` | músicas de fundo (a 8%), vindas da pasta Músicas da Drive |
| `assets/` | emoji (as fontes estão em `../ferramentas/fontes/`) |
| `trabalho/<slug>/` | cada vídeo: bruto, transcrição, plano, candidatas, saída |
| `publicados/<slug>/` | as variantes publicadas e as legendas |
| `estado.json` | que vídeos da RAW já foram tratados |
| `historico.jsonl` | cada publicação, para cruzar com as métricas |
| `../.env` | tudo o que é pessoal e privado (chaves, conta, pastas da Drive, marca) — é o `.env` da raiz da pasta de trabalho |

## Comandos
Corre a partir de `talking-head/`, com `$PY` = o Python do `.venv` da pasta de trabalho (`../.venv/bin/python` no Mac, `..\.venv\Scripts\python.exe` no Windows).
```bash
$PY scripts/th.py novos            # vídeos na RAW ainda por tratar
$PY scripts/th.py por-arquivar     # brutos já publicados que ainda estão na RAW
```

## Ligar e desligar o automático
A partir da raiz da pasta de trabalho:
```bash
$PY ferramentas/agendar.py ligar      # cria as tarefas agendadas (inclui o vigia)
$PY ferramentas/agendar.py desligar
$PY ferramentas/agendar.py estado
```
Usa o launchd no Mac e o Agendador de Tarefas no Windows. Só funciona com o computador ligado e com sessão iniciada.
