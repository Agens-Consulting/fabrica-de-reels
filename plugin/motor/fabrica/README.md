# Fábrica de trial reels

Regra de base: **no dia a dia não há IA. Quem faz e publica os vídeos é um script Python.** A IA (Claude) só entra de 14 em 14 dias, para analisar os números e escrever textos novos para o banco.

Nos comandos, `$PY` é o Python do `.venv` da tua pasta de trabalho: `.venv/bin/python` no Mac, `.venv\Scripts\python.exe` no Windows. Tudo o que é pessoal (conta, chave do Zernio, pastas da Drive, fuso, janela de horas) vem do `.env` da pasta de trabalho.

## Quem faz o quê

| Quando | Quem | O quê |
|---|---|---|
| **Todos os dias, 06:00 do `FUSO`** (tarefa agendada `diario`, `fabrica/diario.py`) | Python, sem IA | 1. `videos/sincronizar.py`: B-rolls e músicas novos da Drive (pastas partilhadas por link, lidas com `ferramentas/drive_publico.py`, sem chaves). 2. `videos/cortar.py`: corta os novos nos melhores 8 s. 3. `metricas/recolher.py`: métricas do perfil e de cada reel. 4. `fabrica/gerar_reel.py dia`: escolhe, monta e agenda os reels do dia (dentro de `HORA_INICIO`-`HORA_FIM`) como trial reels MANUAL. Só corre com `FABRICA_LIGADA=sim` no `.env` |
| **De 14 em 14 dias** (tarefa agendada `analise`, `metricas/analise_auto.py`) | Claude Code, sozinho, skill `reels-de-teste:analise-trial-reels` | Relatório com as cores e letras da pessoa (`MARCA_*` do `.env`), famílias que ganham e perdem, marca vencedores e retirados, escreve textos novos, roda os recursos (ficam 3, saem 2), pede B-rolls ao dono da conta e, se houver forma de enviar email, manda-lhe o PDF (`RELATORIO_EMAIL` no `.env`). Só corre sozinho com `AUTOMATICO_CLAUDE=sim`. O primeiro ciclo é 14 dias depois da linha de base |
| **Quando quiseres** | Claude, comando `/reels-de-teste:novo-recurso <ideia, link, vídeo ou ficheiro>` | PDF do recurso, palavra, automação no Zernio e 12 textos para o banco. Entra já se houver menos de 5 recursos ativos; senão fica em espera e entra na próxima análise |

**As tarefas agendadas** criam-se no `/reels-de-teste:comecar` e geres-nas com `$PY ferramentas/agendar.py ligar|desligar|estado` (launchd no Mac, Agendador de Tarefas no Windows).

**Se o computador estiver desligado ou a dormir às 06:00:** a tarefa corre ao acordar, ao ligar e de hora a hora; o trabalho só se faz uma vez por dia (marca `fabrica/.feito-AAAA-MM-DD`) e, se for tarde, agenda só nas horas que faltam até `HORA_FIM`. A análise faz o mesmo: corre logo que o computador ligue depois de passarem 14 dias. Registos: `fabrica/dia.log`, `metricas/analise.log`. Os avisos que precisem de ti ficam em `avisos.txt` e aparecem na conversa seguinte.

## O banco (`../banco/`)

- `textos.json`: cada entrada é um par **hook + legenda**, ligado a um recurso (palavra do CTA). Campos: `id`, `recurso`, `molde`, `hook` (linhas, máx. 3), `seta`, `destaque`, `legenda` (o campo `seta` já não se usa), `criado`, `origem` (novo / reescrito de um antigo), `estado` (novo, vencedor, retirado).
- `recursos.json`: os recursos com automação no Zernio. **O script só usa textos cujo recurso está `ativo`** (máximo 5 ativos).
- O banco é escrito à mão pelo Claude, de 14 em 14 dias, seguindo `../hooks/como-escrever-hooks-texto.md`, `../legendas/como-escrever-legendas.md` e `../ctas/como-construir-cta.md`. O script nunca escreve texto.

## Regras que o script aplica sozinho

- **Duração (variável de teste):** sorteada entre 5, 6, 7 e 8 s, dentro do que o corte do B-roll aguenta. Os B-rolls vêm cortados nos melhores 8 s (`videos/cortar.py`).
- **Texto:** pode repetir dentro dos 14 dias (é preciso repetir para ver padrões), mas não em dias seguidos; quando houver vencedores no banco, 80% das vezes sai um vencedor e 20% um novo; dentro disso, o menos usado.
- **B-roll:** o menos usado; nunca repete o par texto + B-roll; nunca usa B-rolls marcados `fraco` ou `retirado`.
- **Música:** uma das músicas de fundo (`../audios/raw/`, vindas da pasta Músicas da Drive), a menos usada, num trecho ao acaso, com entrada e saída suaves. Os segundos usados ficam em `musica_trecho_s` para se descobrir que trechos de cada música rendem mais (e depois restringir o sorteio a esses).
- **Variações** (`../edicao/variacoes.md`): sorteia 2 ou 3 de T1 zoom, T2 velocidade, T3 brilho, T4 cor. Nunca T5 espelho (há ecrãs e logótipos nos B-rolls).
- **Hook:** estilo fixo de `../hooks/estetica-e-posicionamento.md`; cor de destaque escolhida pelo fundo (ΔE ≥ 40); emoji e bandeira 🇵🇹 vêm de PNG em `assets/`.
- **Variáveis de teste do hook** (sorteadas por reel, guardadas em `hook_variaveis` no histórico para cruzar com as métricas no fim de cada ciclo de 14 dias): caixa (MAIÚSCULAS / só a primeira; POV sempre em maiúsculas; minúsculas saiu), fim do hook (nada / segundo hook desde 0 s / aos 3 s; setas nunca) e o texto do segundo hook, duração, tamanho da letra (52 px). Também ficam guardados a cor de destaque, as variações técnicas, a música e o B-roll.
- **Volume:** 6, 8 ou 10 por dia, em rotação (conta não verificada). Horários **só dentro da janela `HORA_INICIO`-`HORA_FIM` do `.env`, no `FUSO` da conta, nunca fora** (o script recusa), espalhados, com pelo menos 5 min entre reels.
- **Publicação:** sempre `trialParams.graduationStrategy = MANUAL`. Nunca se promove.
- **Registo:** cada reel fica em `historico.jsonl` (texto, B-roll, música, variações, cor, duração, post_id). É daqui que sai a análise de 14 dias. Os vídeos gerados ficam no disco, em `saida/AAAA-MM-DD/` (não vão para a Drive).

## Comandos

```bash
# $PY = Python do .venv da pasta de trabalho
# Mac:     PY=.venv/bin/python
# Windows: .venv\Scripts\python.exe no lugar de $PY
$PY fabrica/gerar_reel.py dia                      # agenda os reels de hoje
$PY fabrica/gerar_reel.py dia --data 2026-11-16    # de outro dia
$PY fabrica/gerar_reel.py dia --ensaio             # gera sem publicar, para ver
$PY fabrica/gerar_reel.py um --ensaio --texto H001 --broll IMG_7502 --caixa frase --fim segundo_3 --n 91
$PY videos/sincronizar.py                          # B-rolls e músicas novos da Drive
$PY videos/cortar.py                               # corta os B-rolls novos
$PY ferramentas/agendar.py estado                  # vê as tarefas agendadas
```

## Notas

- Textos repetem dentro dos 14 dias (só não saem em dias seguidos), para se verem padrões por família.
- Numa conta nova, o banco e os primeiros recursos fazem-se no `/reels-de-teste:comecar` e com o `/reels-de-teste:novo-recurso`; até haver recursos ativos, a fábrica não publica nada.
