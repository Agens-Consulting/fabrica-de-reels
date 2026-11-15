---
name: analise-trial-reels
description: Análise de 14 em 14 dias da fábrica de trial reels. Recolhe métricas da Zernio, cruza todas as variáveis de cada reel (famílias de hook, caixa, segundo hook, duração, música e trecho, B-roll, cor, hora, volume) com os resultados, escreve o relatório com a estética da pessoa e aplica sozinha as mudanças no banco, nos B-rolls, nas músicas e nos recursos. Corre sozinha pela tarefa agendada (ferramentas/agendar.py). Também dispara em "analisa os trial reels", "relatório da fábrica de reels", "corre a análise de 14 dias".
---

# Análise de 14 dias dos trial reels

Pode correr **sem ninguém a olhar** (tarefa agendada): nesse caso não faças perguntas, decide pelas regras abaixo e deixa tudo escrito. A pessoa lê o relatório e só intervém se discordar.

```bash
P="$(cat ~/.fabrica-de-reels/pasta.txt)"; cd "$P"
PY=.venv/bin/python; [ -f .venv/Scripts/python.exe ] && PY=.venv/Scripts/python.exe
export PYTHONUTF8=1
```
Lê primeiro: `fabrica/README.md`, `metricas/README.md`, `publicacao/regras.md`, `recursos/README.md`, `onboarding/perfil.md`.

## 0. Primeira vez

Se não existir `metricas/perfil/linha-de-base.json`: corre `$PY metricas/recolher.py perfil`, copia a fotografia para `linha-de-base.json` e termina (ainda não há reels para analisar).

## 1. Números

```bash
$PY metricas/recolher.py tudo
$PY metricas/analisar.py --pdf          # ciclo de 14 dias até hoje
```
Saída em `metricas/ciclos/AAAA-MM-DD/` (`analise.json`, `relatorio.html`, `relatorio.pdf`).

## 2. Ler e concluir (o trabalho da IA)

Lê `analise.json` inteiro. Pensa em **famílias e estruturas**, não em reels soltos: que moldes (POV, lista, condição) ganham, que temas, que caixa, que fim de hook, que durações, que trechos de música, que tipos de B-roll, que horas. Um vencedor isolado não chega; uma família com n ≥ 3 e consistente sim. Diz sempre o tamanho da amostra.

Escreve as conclusões no `relatorio.html`, no marcador `<!--CONCLUSOES-->`, no mesmo estilo:
- 3 a 6 conclusões, cada uma com o número que a sustenta;
- a lista de mudanças aplicadas (passo 3);
- o que fica a testar no próximo ciclo;
- o que se precisa da pessoa (B-rolls, músicas, recursos à espera da Drive).
Depois volta a gerar o PDF: `$PY -c "import sys; sys.path.insert(0,'ferramentas'); import config as c; c.pdf_de_html('metricas/ciclos/AAAA-MM-DD/relatorio.html','metricas/ciclos/AAAA-MM-DD/relatorio.pdf')"`.

## 3. Aplicar as mudanças (sozinho)

Só com dados suficientes (≥3 saídas; reels com ≥7 dias). Cada mudança fica em `metricas/ciclos/AAAA-MM-DD/mudancas.md`.

1. **Textos** (`banco/textos.json`): aplica as sugestões de estado (`vencedor`, `retirado`, `a testar`). O gerador dá prioridade aos vencedores (80/20).
2. **Textos novos:** 15 a 30 para os temas ativos, **dentro das famílias que ganharam**, seguindo à letra `hooks/como-escrever-hooks-texto.md`, `legendas/como-escrever-legendas.md` e o que cada recurso entrega (`recursos/PALAVRA/ficha.md`). MAIÚSCULAS, ≤ 3 linhas de ≤ 22 caracteres, destaque = palavras do hook, sem setas, `origem: "ciclo AAAA-MM-DD"`. Valida as larguras com `fabrica/gerar_reel.py` antes de gravar.
3. **B-rolls** (`videos/registo.json`): `estado: "vencedor"` ou `"fraco"` conforme as sugestões. Os fracos deixam de sair.
4. **Músicas** (`audios/registo.json`): `trechos_bons: [[ini, fim], …]` com os baldes de 20 s que ganharam.
5. **Variáveis de teste** (caixa, fim do hook, duração): se uma opção perde com clareza em 2 ciclos seguidos, tira-a da lista em `fabrica/gerar_reel.py` (`CAIXAS`, `FIM_HOOK`, `DURACOES`) e regista porquê. Nunca só com 1 ciclo.
6. **Recursos (regra dos 5):** ordena por comentários por 1 000 views. Ficam os 3 melhores; os 2 piores passam a `ativo: false` e a "Arquivados" em `recursos/lista.md` (a automação na Zernio fica ligada). Entram 2: **primeiro os que estão em espera** e prontos (`espera: true` sem `falta`); se faltarem, escolhe em `banco/pesquisa-temas.md` (secção C) e cria-os com a skill **fabrica-de-reels:novo-recurso** — em modo automático não há ligação à Drive, por isso ficam `espera: true, falta: "drive"` e entram na próxima conversa (o /reels trata disso). No primeiro ciclo só se ordena.
7. **Volume:** compara o alcance do dia com o nº de reels (regra em `publicacao/regras.md`). Só muda `VOLUMES` ao fim de 4 semanas.
8. **Pedido de gravações:** se houver menos de 10 B-rolls `novo`/`vencedor` com corte, ou se um tipo ganhar com clareza, escreve no relatório o pedido: quantos e de que tipo.

## 4. Entregar

O relatório entrega-se em **PDF**.
- **Email (se houver ligação de email nesta sessão):** se `RELATORIO_EMAIL` estiver vazio, procura que ferramentas de email existem (ToolSearch "send email gmail"); descobre o endereço da própria pessoa (o "From" em `in:sent`) e grava `RELATORIO_EMAIL` e `RELATORIO_LIGACAO`. Envia `relatorio.pdf` em anexo só para o próprio dono da conta, assunto `Trial reels · relatório de DD/MM a DD/MM`, corpo curto: seguidores, views do ciclo, 3 conclusões, mudanças, data do próximo. Regista em `email.txt`. Sem ligação de email: não pára; fica o PDF no disco.
- **Drive (se a ligação estiver disponível):** carrega `relatorio.pdf` para `DRIVE_PASTA_RECURSOS` com o nome `AAAA_MM_DD_Relatorio_Trial_Reels.pdf`, **sem** partilha pública; link em `link.txt`.
- Acrescenta uma linha a `metricas/ciclos/indice.md`: data, seguidores, views do ciclo, 3 conclusões.
- Aviso: `$PY -c "import sys; sys.path.insert(0,'ferramentas'); import config as c; c.notificar('Relatório dos trial reels pronto: metricas/ciclos/AAAA-MM-DD/relatorio.pdf')"`.

## Regras fixas (não mudar na análise)

Janela `HORA_INICIO`-`HORA_FIM` do `.env`; trial reels sempre MANUAL, nunca promover; sem setas no ecrã; POV em maiúsculas; letra 52 px; nunca apagar reels publicados.
