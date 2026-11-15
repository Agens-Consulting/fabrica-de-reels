---
name: reels
description: Painel da Fábrica de Reels - mostra o estado (o que saiu hoje, o que está agendado, tarefas automáticas, avisos), resolve o que ficou à espera da pessoa (recursos por carregar na Drive, talking heads por arquivar), atualiza o motor depois de uma atualização do plugin e liga/desliga o piloto automático. Usar quando a pessoa escreve "/reels", "como estão os reels", "o que saiu hoje", "há avisos?", "atualiza a fábrica de reels", "desliga os reels", "liga os reels".
---

# /reels — painel

```bash
P="$(cat ~/.fabrica-de-reels/pasta.txt 2>/dev/null)"   # vazio → ainda não há onboarding: segue a skill fabrica-de-reels:comecar
cd "$P"
PY=.venv/bin/python; [ -f .venv/Scripts/python.exe ] && PY=.venv/Scripts/python.exe
export PYTHONUTF8=1
```
Se não existir `~/.fabrica-de-reels/acesso.json` com `"ok": true`, para aqui e segue a skill fabrica-de-reels:comecar (pede o código de acesso).

Se `onboarding/estado.json` não disser que o onboarding acabou, diz em que passo ficou e oferece continuar com /fabrica-de-reels:comecar.

## 1. Atualizar o motor (sempre, em silêncio)

O plugin pode ter sido atualizado. Corre `python3 "<pasta desta skill>/../../motor/ferramentas/instalar.py" "$P" --sem-modelos` (no Windows, `py -3.12` ou o `$PY`). Só substitui scripts e guias; nunca toca no `.env`, no banco, nos recursos nem nos históricos, e acrescenta ao `.env` chaves novas que apareçam. Se der erro, mostra-o.

## 2. Estado (uma mensagem curta)

- **Avisos:** lê `avisos.txt`; mostra os que ainda não foram tratados.
- **Hoje:** reels de hoje em `fabrica/historico.jsonl` (hora, hook) e talking heads em `talking-head/historico.jsonl`.
- **Agendado:** `$PY ferramentas/zernio_posts.py posts --estado scheduled` (quantos e até quando).
- **Tarefas automáticas:** `$PY ferramentas/agendar.py estado` + últimas linhas de `registos/diario.log`, `registos/vigia.log`, `registos/analise.log` (só se houver erros, mostra-os).
- **Banco:** nº de textos por estado, recursos ativos/em espera, B-rolls com corte.
- **Próxima análise:** 14 dias depois do último `metricas/ciclos/*`.

## 3. Resolver o que está à espera

Faz sem perguntar, se a ligação Google Drive estiver disponível (ToolSearch `select:mcp__claude_ai_Google_Drive__create_file,mcp__claude_ai_Google_Drive__share_file,mcp__claude_ai_Google_Drive__update_file,mcp__claude_ai_Google_Drive__search_files`):
1. **Recursos com `falta: "drive"`** em `banco/recursos.json`: carrega o PDF e cria a automação (skill fabrica-de-reels:novo-recurso, passos 5 e 7).
2. **Talking heads "à espera de recurso"** (`talking-head/estado.json`): depois do passo 1, publica-os (skill fabrica-de-reels:reel-talking-head, passo 8).
3. **Brutos por arquivar:** skill fabrica-de-reels:reel-talking-head, passo 10.
Depois limpa de `avisos.txt` as linhas resolvidas (guarda-as em `registos/avisos-resolvidos.txt`).

## 4. Ligar / desligar

- "desliga" → `$PY ferramentas/agendar.py desligar` (e `FABRICA_LIGADA=nao`).
- "liga" → confirma com AskUserQuestion se o Claude pode trabalhar sozinho (`AUTOMATICO_CLAUDE`), depois `FABRICA_LIGADA=sim` e `$PY ferramentas/agendar.py ligar`.
- Mudou de computador ou de pasta → corre o instalador para a pasta nova e `agendar.py ligar` outra vez.
