# Regras de publicação

Regras de base, iguais para todas as contas. O que é pessoal (conta, fuso, janela de horas) vem do `.env` da tua pasta de trabalho.

## 1. Que reels saem

**Por agora, só o tipo A:** o texto no ecrã e a legenda são o conteúdo. Vídeo de **5 a 8 segundos** (a duração é variável de teste, sorteada por reel) com imagens de fundo, um hook fixo e o valor na legenda. Guias: `../hooks/como-escrever-hooks-texto.md` e `../legendas/como-escrever-legendas.md`.

Os reels em que a pessoa fala para a câmara (tipo B, talking head) seguem um caminho à parte: `../talking-head/README.md` e o guia `../hooks/como-escrever-hooks-fala.md`. Não contam para o volume diário da fábrica.

## 2. Quantos por dia

| Conta | Por dia |
|---|---|
| **Não verificada** (sem o visto azul) | **6 a 10** |
| **Verificada** (com o visto azul) | **10 a 15** |

**Qual se aplica à tua conta:** vem de `INSTAGRAM_VERIFICADA` no `.env` (`nao` por defeito). Uma conta não verificada começa com 6 a 10. Quando a conta tiver o visto azul, muda-se para `sim` e passa-se para 10 a 15.

### Como se escolhe o número dentro do intervalo

Testando, ao longo do tempo:

1. **Varia-se o número de dia para dia** dentro do intervalo. Por exemplo, numa conta não verificada: 6, 8 e 10, em rotação, cada um em dias da semana diferentes, para que o número não fique colado a um dia.
2. **Regista-se por dia:** quantos reels saíram, o alcance total do dia, as views por reel, os comentários com a palavra e os seguidores novos.
3. **Ao fim de 4 semanas**, compara-se a média de cada volume. Duas perguntas:
   - **O alcance total do dia sobe com o número de reels?** Se 10 por dia dá mais alcance total do que 6, compensa.
   - **As views por reel caem quando se publica mais?** Se cada reel passa a ter muito menos views, os reels estão a competir uns com os outros.
4. **Fica o volume mais alto em que o alcance total ainda sobe** sem as views por reel caírem a pique. Continua-se a testar à volta desse número.

Um dia sozinho não diz nada. As conclusões tiram-se no relatório de 14 em 14 dias (`../metricas/README.md`).

## 3. Horários

- **Tudo no fuso da conta** (`FUSO` no `.env`, por defeito `Europe/Lisbon`). O relógio do computador pode estar noutro fuso; agenda-se sempre a pensar na hora do `FUSO`, nunca na do computador.
- **Só dentro da janela de publicação** (`HORA_INICIO` e `HORA_FIM` no `.env`, por defeito 09:00 a 20:30). **Nunca fora:** o script recusa outras horas.
- **Espalhar ao longo do dia**, com pelo menos 5 minutos entre reels (espalhados pelo dia; se o computador ligar tarde, encolhem até 5 min para sair o número do dia).
- **Ir experimentando horários.** Dentro da janela (ex.: 09:00-20:30): manhã, almoço (12h-14h), tarde e fim de tarde (até ao fim da janela). Os horários rodam, e o relatório de 14 dias diz quais as faixas com mais alcance por reel.

## 4. Um trial reel fica trial reel para sempre

- Publica-se sempre com `trialParams.graduationStrategy = "MANUAL"` e **nunca se passa à conta principal**, nem quando corre muito bem.
- **Nunca usar `SS_PERFORMANCE`:** o Instagram promove sozinho o reel que corre bem, e isso não se quer.
- Porquê: o trial reel serve para chegar a quem não segue a conta. Mostrá-lo aos seguidores mistura os dados e polui o feed com testes.

## 5. De onde vem cada reel do dia

A regra para o regime normal:

- **80% reaproveitam** um hook e uma legenda já usados, sobre uma imagem de fundo diferente.
- **20% são novos:** hook novo, legenda nova e, quando for preciso, recurso novo.

Para não cair num erro já visto noutras contas (a mesma legenda até 19 vezes e o aviso de "conteúdo muito parecido"):

- **Reaproveita-se o que ganhou**, não o que calhou. Um hook e uma legenda só voltam se tiverem ficado acima da média no relatório.
- **O mesmo par hook + legenda volta no mínimo 14 dias depois.**
- **Em cada regresso muda** a imagem de fundo, o segundo hook (as primeiras palavras da legenda) e pelo menos 2 alterações técnicas de `../edicao/variacoes.md`.

Isto ainda é uma aposta e vai ser vigiado: se o Instagram voltar a avisar de conteúdo parecido, a fatia reaproveitada desce.

## 6. Antes de publicar

- O recurso existe, está em `../recursos/` e a automação da palavra está ativa.
- O hook e a legenda passaram as listas de verificação dos guias.
- Fica registado: imagem de fundo, áudio, hook, legenda, palavra, alterações de edição, hora, e se é reaproveitado ou novo.

**Quem publica é um script Python, sem IA:** `../fabrica/gerar_reel.py dia` escolhe do banco, monta e agenda os reels do dia. Ver `../fabrica/README.md`.
