# Métricas e relatório de 14 em 14 dias

Esta é a base do método, tirada do playbook dos trial reels. Vai sendo aprofundada à medida que os ciclos de 14 dias trazem dados da tua conta.

Nos comandos, `$PY` é o Python do `.venv` da tua pasta de trabalho (`.venv/bin/python` no Mac, `.venv\Scripts\python.exe` no Windows).

## As métricas do playbook

Cada métrica avalia uma peça diferente do reel:

| Métrica | O que avalia |
|---|---|
| **Guardados** | o valor da legenda |
| **Partilhas** | o hook |
| **Comentários** (com a palavra) | o CTA e o recurso |
| **Seguidores novos** | o reel inteiro a funcionar em conjunto |
| **Alcance** | confirma que os outros números contam (com 30 views, nada é conclusivo) |

**Para comparar reels entre si, divide-se pelo alcance:** guardados, partilhas, comentários e seguidores por cada 1 000 contas alcançadas. Sem isto, ganha sempre o reel que calhou ser mais distribuído.

Se o Zernio devolver também tempo médio de visualização, taxa de skip e taxa de conclusão, guardam-se: dizem se o vídeo de 6 s (máximo 8) está a repetir em loop enquanto a pessoa lê.

## Regras de análise (do playbook)

1. **Só se analisa um reel 7 dias depois de sair.** Antes disso o Instagram ainda está a distribuí-lo.
2. **Vencedor:** na primeira semana faz-se a média. A partir daí, é vencedor o reel que bate a média da semana anterior.
3. **Um hook ou uma imagem de fundo só se julgam depois de saírem pelo menos 3 vezes.** O mesmo hook já fez 1 387 views numa vez e 31 noutra.

## O que se regista por reel

Data e hora, imagem de fundo, áudio, hook (e o molde), legenda (e o segundo hook), palavra e recurso, alterações de edição, se é reaproveitado ou novo; e, aos 7 dias, alcance, views, guardados, partilhas, comentários, seguidores novos e, se houver, o tempo médio de visualização.

Por dia: número de reels publicados e alcance total (para o teste do volume em `../publicacao/regras.md`).

Fonte: a API do Zernio. **Os trial reels devolvem estatísticas** (`GET /analytics?postId=…`: views, alcance, gostos, comentários, partilhas, guardados, skip rate, tempo médio de visualização; `follows` vem vazio). Perfil: `GET /accounts/follower-stats` (seguidores e histórico diário) e `GET /analytics/instagram/account-insights` (views, alcance, visitas ao perfil e interações dos últimos 30 dias, com até 48 h de atraso).

## Recolha (automática, todos os dias)

`$PY metricas/recolher.py tudo` corre todos os dias com a publicação (`fabrica/diario.py`):
- `metricas/perfil/AAAA-MM-DD.json`: fotografia do perfil.
- `metricas/reels/AAAA-MM-DD.jsonl` e `metricas/reels_ultimo.json`: métricas de cada trial reel.

**Linha de base:** `metricas/perfil/linha-de-base.json`, a fotografia do perfil tirada no arranque (`/fabrica-de-reels:comecar`), antes do primeiro trial reel: seguidores e, nos últimos 30 dias, views, alcance e visitas ao perfil. Cada ciclo compara com isto para medir quanto do crescimento veio dos trial reels. Numa conta nova, a primeira coisa que corre é esta fotografia (`$PY metricas/recolher.py perfil`). Não há relatório à parte da linha de base: é só esta fotografia.

## Relatório de 14 em 14 dias (automático)

O ciclo é de **14 dias** e corre **sozinho**: a tarefa agendada `analise` (`metricas/analise_auto.py`, criada com `$PY ferramentas/agendar.py ligar`; launchd no Mac, Agendador de Tarefas no Windows) chama o Claude Code com a skill `fabrica-de-reels:analise-trial-reels`. Só corre sozinha com `AUTOMATICO_CLAUDE=sim` no `.env`; sem isso, corre-se a skill à mão numa conversa. O primeiro ciclo é 14 dias depois da linha de base. Análise por **famílias** (moldes, temas, caixa, fim do hook, duração, música e trecho, B-roll, hora), não só reel a reel.

De 14 em 14 dias sai um relatório com **as melhorias que se vão aplicar no mês seguinte, e quem as aplica é o Claude, sozinho.** O dono da conta lê e só intervém se discordar.

Melhorias típicas:

- **Imagens de fundo:** retirar as que ficam abaixo da média, usar menos as fracas, usar mais as vencedoras. **Pedir ao dono da conta que grave mais**, dizendo de que tipo, com base nas que ganharam (ex.: "precisamos de mais 10 no carro, à noite").
- **Áudios:** o mesmo raciocínio.
- **Hooks:** que moldes e ângulos ganharam; o que deixa de se usar.
- **Legendas:** que segundos hooks e que estruturas dão mais guardados.
- **Recursos:** o resumo dos ciclos de 14 dias (os 5 ativos, quem ficou, quem saiu).
- **Volume e horários:** o que os dados dizem sobre quantos reels por dia e em que faixas horárias.
- **A divisão 80/20** entre reaproveitados e novos: mantém-se, ou ajusta-se.

Formato: relatório/dashboard com as **cores e letras da pessoa** (`MARCA_*` do `.env`), em HTML e PDF, gerado por `$PY metricas/analisar.py --pdf`. Guarda-se em `metricas/ciclos/AAAA-MM-DD/` (`analise.json`, `relatorio.html`, `relatorio.pdf`).

**Entrega: PDF por email, se for possível.** O relatório chega ao dono da conta em **PDF** (nunca HTML), anexado a um email para o próprio endereço, o de `RELATORIO_EMAIL` no `.env`, pela ligação de email indicada em `RELATORIO_LIGACAO` (ex.: o conector Gmail do Claude). Na primeira corrida, se estes campos estiverem vazios, a skill vê que ligações de email existem e, se houver uma, grava-a. Cada envio fica registado em `metricas/ciclos/AAAA-MM-DD/email.txt`.

**Sem email:** o envio é opcional. Se não houver forma de enviar (nenhuma ligação, ou o Claude correu sozinho sem acesso a ela), o relatório fica só em `metricas/ciclos/AAAA-MM-DD/` e aparece um aviso (notificação no computador e em `avisos.txt`, mostrado na conversa seguinte) a dizer onde está. Para passar a receber por email, liga o Gmail no Claude (claude.ai → Definições → Conectores → Gmail).
