# Como escrever hooks de texto (tipo A: o texto manda ler a legenda)

**Versão 2, de 24/11/2026.** Os textos escritos com esta versão levam `"guia": 2` no `banco/textos.json`. O que mudou em relação à versão 1: a **lista passa a ser o molde principal** (8 em cada 10), o POV só entra com uma afirmação difícil de acreditar, a condição escondida sai, e há um passo obrigatório para traduzir o método para o tema da conta (secção 4). Porquê: em 53 trial reels da conta de exemplo, a lista teve 48 comentários, o POV 29 e a condição 0. E numa conta de outro tema, os hooks copiados do exemplo (POV de cenas, condições com "isto") não passaram das 200 views.

Este documento é para quem vai escrever os hooks: uma IA ou uma pessoa que nunca viu este projeto. Lê-o inteiro antes de escrever o primeiro hook. O formato irmão, em que o dono da conta fala para a câmara, está em `como-escrever-hooks-fala.md`. O aspeto visual (letra, cor, posição) é um estilo fixo, está em `estetica-e-posicionamento.md` e não se decide aqui.

Antes de escrever, lê também `../onboarding/perfil.md` (quem é o dono da conta, para quem fala, tom) e `../banco/pesquisa-temas.md` (os temas aprovados).

**Aviso sobre os exemplos.** Há exemplos de duas contas: uma de IA para donos de PME (com números reais) e uma de psicomotricidade para pais (hooks aprovados, ainda sem números). Os exemplos mostram o mecanismo. **Nunca se copia o esqueleto de um exemplo para outro tema**: "pov: o teu concorrente…" ou "…se não fizeres isto" num tema onde ninguém pensa assim dá hooks que ninguém lê.

---

## 1. O que é este formato

Um vídeo de 6 segundos (máximo 8), sem fala, com imagens do dia a dia do dono da conta em fundo e **um único texto fixo no ecrã**. O vídeo não ensina nada. Todo o valor está na legenda: a lista, o passo a passo. No fim da legenda há um pedido: "Comenta PALAVRA" e a pessoa recebe um recurso por mensagem.

O hook é esse texto. Tem três trabalhos, por esta ordem:

1. **Parar o dedo.** A pessoa está a fazer scroll e decide em menos de dois segundos.
2. **Escolher quem pára.** Só o público da conta, e não curiosos nem público de outro país.
3. **Abrir uma pergunta que só a legenda responde.**

Se o hook fizer os dois primeiros e falhar o terceiro, a pessoa lê, pensa "ok" e continua. O reel só rende se a pessoa abrir a legenda: enquanto lê, o vídeo repete em loop e o tempo de visualização acumula; no fim guarda ou comenta a palavra-chave.

**Como se mede:** comentários com a palavra-chave e guardados por cada 1 000 visualizações. Nos trial reels, a taxa de skip decide tudo: os reels que o Instagram deixou de mostrar (menos de 100 views) tinham 80% de skip; os que se espalharam, entre 43% e 56%.

## 2. Quem vai ler o hook

Os trial reels só são mostrados a **quem não segue a conta**:

- A pessoa não sabe quem é o dono da conta. O nome dele, o nome da empresa (e qualquer palavra em `HOOK_PALAVRAS_PROIBIDAS` no `.env`) e "a minha empresa" não lhe dizem nada.
- Não há contexto anterior. O hook tem de se perceber sozinho, à primeira leitura.
- Não há confiança. Qualquer coisa que soe a anúncio, a guru ou a frase feita é ignorada.

O leitor que queremos está em `../onboarding/perfil.md`. Descreve-o com este grau de pormenor antes de escrever:

- *Conta de IA:* dono de uma empresa de serviços em Portugal, 38 a 50 anos, 5 a 30 pessoas. Faz orçamentos e propostas, tem reuniões a mais. Já ouviu falar de ChatGPT e de Claude e usa-os pouco. Está no sofá às 22h.
- *Conta de psicomotricidade:* mãe ou pai de uma criança de 2 a 8 anos. Lida com birras, sapatos, hora de deitar, ecrãs, a letra que não sai. Quer saber se o filho está bem e o que pode fazer em casa. Está no sofá às 22h, com a criança já a dormir.

O teste que resume tudo: **esta pessoa parava aqui?** Se a resposta não for um sim claro, o hook não serve. "Não é mau" não chega: a maioria dos hooks que falharam não eram maus, eram mornos.

## 3. A regra central: mostrar o quê, esconder o resto

Um hook mostra **o quê** (a categoria, o resultado) e esconde **quais** ou **como**. A resposta escondida é exatamente o que a legenda entrega.

**O teste do "ah, percebi".** Lê o hook como se fosses o leitor. Se conseguires pensar "ah, percebi" sem abrir a legenda, o hook entregou a recompensa e falhou. Se ficares com uma pergunta concreta na cabeça ("quais são?", "será que eu faço isso?"), está certo.

**Sinais de que o hook fechou a pergunta:** termina num aforismo, tem o antes e o depois completos, tem duas frases em que a segunda explica a primeira, ou tem um parêntese que descreve o que está na legenda.

**Mas esconder não chega.** "Faz isto antes de dormir" esconde tudo e não pára ninguém: não há nada a que agarrar. O hook tem de dar uma coisa concreta para agarrar (a secção 5) e esconder só a resposta.

## 4. Antes de escrever: traduzir para o tema da conta

Este passo é obrigatório e escreve-se antes do primeiro hook (guarda-se em `../banco/pesquisa-temas.md`, secção "Tradução para hooks"). Sem ele, a IA cai nos exemplos da conta de IA.

1. **As coisas com nome do dia do leitor.** 15 a 20 substantivos que o leitor vê, compra, diz ou detesta. Objetos, momentos, pessoas, frases.
   - *IA:* plugins, Claude, PowerPoint, Excel, orçamento, proposta, contabilista, email de cliente.
   - *Psicomotricidade:* atacadores, lápis, tesoura, tablet, bicicleta, sapatos, hora de deitar, birra, sentar em W, bicos de pés, prendas de Natal, educadora.
2. **Quem pára.** A palavra que faz o leitor pensar "é para mim": um papel ("dono", "pais"), uma idade ("aos 5 anos", "uma criança de 3 anos") ou uma profissão. Na parentalidade, **a idade da criança é o filtro mais forte**.
3. **O que o leitor quer ter ou evitar.** Na língua dele: "clientes", "tempo", "dinheiro"; "que ele durma", "que não fique para trás", "não gastar em brinquedos que não servem".
4. **A autoridade de quem está por dentro.** O que o dono da conta sabe por profissão e o leitor não: "o que uma psicomotricista nunca deixa o filho fazer", "o que o contabilista agradece".
5. **O calendário.** Momentos do ano em que o tema pesa: Natal e prendas, regresso às aulas, férias, janeiro.

## 5. O molde principal: a lista com número

**8 em cada 10 hooks são listas.** É o molde que funciona em qualquer tema: promete uma coisa finita, escolhida por quem sabe, e põe o leitor a perguntar-se "será que eu faço isto?". É isso que leva a guardar e a comentar. Na conta de exemplo, foi o molde do melhor reel de sempre (4 970 views, 30 comentários, 54 guardados) e de 48 dos 77 comentários.

`[N] + [coisa com nome] + [gancho]`

- **O número** vai de 3 a 7, em algarismo. É quase sempre a palavra de destaque.
- **A coisa** sai da lista da secção 4: um substantivo que se pode apontar. Nunca "dicas", "formas", "estratégias", "segredos" ou "coisas importantes".
- **O gancho** é o que faz parar. **Número + coisa sem gancho é morno**: "3 jogos para crianças" e "5 perguntas que dizem se estás pronto para a IA" não param ninguém (a segunda teve 61 views). Cada lista leva pelo menos um destes seis:

| Gancho | Como funciona | Conta de IA | Conta de psicomotricidade |
|---|---|---|---|
| **1. Exclusividade** | "os únicos", "só estes": quem sabe corta o ruído por ti | OS ÚNICOS 3 / PLUGINS DO CLAUDE QUE / UM DONO PRECISA (4 970 views) | OS ÚNICOS 3 / BRINQUEDOS QUE UMA / CRIANÇA DE 3 ANOS PRECISA |
| **2. Contra a intuição ou dinheiro** | diz que uma coisa que todos fazem ou compram não serve | — | 5 BRINQUEDOS CAROS / QUE NÃO SERVEM / PARA NADA |
| **3. O hábito do leitor posto em causa** | ataca o que ele faz, nunca quem ele é | 3 ERROS NOS TEUS / ORÇAMENTOS QUE TE / CUSTAM CLIENTES | 3 FRASES QUE DIZES / AO TEU FILHO QUE / PIORAM AS BIRRAS |
| **4. Autoridade de quem está por dentro** | o que um profissional faz, nunca faz ou agradece | 3 PEDIDOS AO CLAUDE / QUE O TEU CONTABILISTA / VAI AGRADECER (2 710 views) | O QUE UMA / PSICOMOTRICISTA NUNCA / DEIXA O FILHO FAZER |
| **5. Idade ou papel como filtro** | o leitor vê-se no hook | 7 PROMPTS DE CLAUDE / PARA DONOS / DE EMPRESA | 4 COISAS QUE O TEU / FILHO DEVE FAZER / SOZINHO AOS 5 ANOS |
| **6. Momento do ano** | o tema pesa agora | 3 PASSOS ANTES / DE JANEIRO (só funciona com coisa concreta: este teve 54 views) | 7 PRENDAS DE NATAL / QUE UMA PSICOMOTRICISTA / DAVA AOS FILHOS |

Os melhores juntam dois ganchos: exclusividade com filtro ("os únicos 3… que um dono precisa"), autoridade com momento do ano ("prendas de Natal que uma psicomotricista dava").

A lista implícita também conta: "O que uma psicomotricista nunca deixa o filho fazer" não tem número, mas promete uma lista e esconde-a.

## 6. O POV: só com uma afirmação difícil de acreditar

**No máximo 2 em cada 10, e só se passar este teste:** quem lê pensa "isso é possível?". Na conta de exemplo, os POV que funcionaram afirmavam todos uma coisa assim:

- POV: UM SÓ COMANDO / DEU AO CLAUDE / 314 SKILLS NOVAS (2 078 views)
- POV: O CLAUDE FAZ O / POWERPOINT E TU / ESCOLHES AS CORES (3 169 views)
- POV: INSTALASTE UM / PLUGIN E O CLAUDE / APRENDEU O TEU NEGÓCIO (1 840 views)

A estrutura: um gesto pequeno com um efeito grande e concreto.

**O POV de cena fica de fora**, porque descreve um momento sem nada de surpreendente: "pov: segunda de manhã e a semana inteira cabe numa página", "pov: a proposta saiu antes do café", "pov: uma bola de ténis acabou com a birra dos sapatos". Ficaram entre 194 e 241 views, e ninguém comentou. O POV de inveja também ("pov: o teu concorrente…"): saiu 3 vezes, com 288, 270 e 91 views.

Se no tema da conta não houver afirmações destas que sejam **verdade**, escrevem-se 10 listas e nenhum POV.

## 7. A condição escondida: já não se usa

"Pagas X e deitas dinheiro fora se não fizeres isto", "não faças X antes de saberes isto". Na versão 1 era um dos três moldes. Nos 9 trial reels da conta de exemplo teve mediana de 245 views, nenhum passou das 610 e **nenhum teve um comentário**. Promete um segredo sem dizer de quê, soa a anúncio e o leitor passa à frente.

Não se escreve. Os textos antigos com `molde: "condicao"` reescrevem-se com `/rever-hooks`.

## 8. Cortar palavras

**Alvo: 6 a 9 palavras. Máximo: 11.** Cabem cerca de 22 caracteres por linha e 3 linhas. **Ideal: até 55 caracteres com espaços. Máximo absoluto: 80**, e aí a letra já encolhe.

Como cortar, por esta ordem:

1. **Tira quem ninguém conhece:** "na [nome da empresa]", "na minha empresa", "eu e a minha equipa".
2. **Tira a segunda frase.** Quase sempre é ela que entrega a recompensa.
3. **Tira os enchimentos:** "todos os dias", "realmente", "simplesmente", "de forma".
4. **Troca expressões por palavras:** "pais" em vez de "todas as pessoas que têm filhos pequenos".
5. **Faz o teste palavra a palavra.** Tira uma palavra de cada vez. Se o hook continua a parar o dedo, a palavra estava a mais.

**O que nunca se corta:** o número, a coisa com nome, o filtro (idade, papel) e o gancho. Um hook curto e vago é pior do que um hook comprido e concreto.

**Palavras simples.** Entre "utilizar" e "usar", é "usar". Entre "desenvolvimento motor" e "mexer-se", é quase sempre a segunda.

## 9. Ser concreto

Na conta de exemplo, os temas concretos (plugins, skills, ferramentas com nome) deram 5 dos 6 reels que mais se espalharam. Os abstratos ("estás pronto para a IA", "a tarefa que te come um dia por semana") deram 4 dos 9 reels abaixo das 100 views e 0 comentários em 12.

- **Diz o nome da coisa**, nunca a categoria: "Claude" e não "uma ferramenta de IA"; "atacadores" e não "autonomia".
- **Usa números:** idades, minutos, quantidades.
- **Palavras proibidas por serem vagas:** produtividade, eficiência, otimizar, transformação, potenciar, soluções, o futuro, revolucionar, desenvolvimento integral, bem-estar, equilíbrio.

## 10. Voz e tom

- **Fala-se para o leitor ("tu") ou o dono da conta fala ("eu").** Nunca uma terceira pessoa vaga: "a maior parte das empresas…" e "muitas crianças…" renderam mal.
- **Português de Portugal**, se a conta for portuguesa: "tu", "telemóvel", "ecrã". Nada de "você", "tela", "celular".
- **Tom de quem sabe por dentro e mostra**, não de quem dá lições.
- **O negativo ataca o hábito, nunca a pessoa.** "3 frases que dizes ao teu filho que pioram as birras" serve. "Estás a estragar o teu filho" não serve.
- **Nunca "não é X, é Y".** É o tique mais reconhecível de texto feito por IA.
- **Sem travessões, sem três adjetivos seguidos, sem pontos de exclamação.**

**Temas de saúde e de crianças.** Não se escrevem hooks que ensinem a diagnosticar ("sinais de que o teu filho tem atraso"): o medo rende pouco nos dados que temos, põe em risco a credibilidade de quem é profissional e o Instagram limita conteúdo de saúde alarmista. Se o dono da conta quiser testar "sinais", o tom é de quem tranquiliza e são no máximo 1 em cada 10.

## 11. A bandeira 🇵🇹

Para contas que falam para Portugal: diz ao leitor que o vídeo é para ele e afasta o público brasileiro.

- **3 ou 4 em cada 10 hooks**, no fim da última linha. Nunca se escreve a palavra "Portugal".
- **Encaixa melhor** quando o hook fala de um grupo ("donos de empresa", "pais") ou de dinheiro.
- Não está provado que conte para o algoritmo. O português de Portugal e os euros também filtram.

## 12. A segunda linha

Por baixo do hook o script põe, ou não, um segundo hook entre parênteses ("(vê a legenda)", "(está tudo na legenda)"). **Setas (↓, 👇) no ecrã nunca.** Quem escreve o hook não escreve esta linha.

## 13. O hook nunca se escreve sozinho

Um hook é uma promessa, e a legenda é o pagamento. Escrevem-se juntos:

- **A recompensa:** se o hook diz "os únicos 3 brinquedos", a legenda tem os 3, com o porquê de cada um.
- **A palavra-chave:** escolhe-se pelo processo de `../ctas/como-construir-cta.md`. A ligação ao hook faz-se pelo tema, não pela palavra igual.
- **O pedido de comentário vai no fim da legenda.** Quando se pôs cedo, os guardados caíram para metade.
- **Só se promete o que existe.** Cada número, idade e facto tem de ser verdade para o dono da conta, e num tema de saúde tem de ser verdade clínica. O que não estiver confirmado leva a marca `[CONFIRMAR]` e não vai para o banco sem o "sim" do dono.

## 14. Como produzir um lote

**O que tens de ter antes de começar** (se faltar, pede; não inventes):

1. A tradução para hooks (secção 4).
2. O tema e a recompensa: o que a legenda vai entregar.
3. Factos reais do dono da conta sobre esse tema.
4. A lista dos hooks publicados nos últimos 14 dias.

**Passos:**

1. Escreve a recompensa numa frase.
2. Escreve 20 listas em bruto, pelo menos 3 por gancho. Se o tema tiver afirmações difíceis de acreditar e verdadeiras, escreve também 4 POV.
3. Corta as palavras (secção 8).
4. Passa cada um pela lista de verificação (secção 15). O que falhar um ponto sai.
5. Faz o teste da pessoa no sofá: lê os que sobram como se estivesses a fazer scroll, em voz alta, depressa. Os que não te fazem parar saem, mesmo que cumpram as regras.
6. Compara com os últimos 14 dias. Se dois diferem só numa palavra ou num número, fica um.
7. Escolhe os 10 melhores: 8 a 10 listas, com pelo menos 4 ganchos diferentes; 0 a 2 POV.

**Formato de entrega**, uma linha por hook:

| Campo | Conteúdo |
|---|---|
| Hook | o texto, com as quebras marcadas com " / " |
| Destaque | a palavra (no máximo duas) que fica a cor |
| Molde | lista ou POV |
| Gancho | exclusividade, contra a intuição, hábito, autoridade, filtro ou momento do ano |
| Pergunta que fica | "quais?", "será que eu faço isto?" |
| Recompensa | o que a legenda entrega |
| Palavra-chave | a palavra do pedido de comentário |
| A confirmar | factos por validar com o dono da conta |

No `banco/textos.json` cada texto leva `"molde"`, `"gancho"` e `"guia": 2`.

**Quebras de linha:** 2 ou 3 linhas, partidas onde a pessoa faria uma pausa. Nunca separar o número da coisa ("7 / prompts") nem deixar uma palavra sozinha na última linha.

## 15. Lista de verificação

Um hook só é entregue se passar todos os pontos.

1. **Pára?** O leitor no sofá às 22h parava aqui. "Não é mau" é um não.
2. **É uma lista com gancho**, ou um POV com uma afirmação difícil de acreditar?
3. **Tem uma coisa com nome** da lista da secção 4?
4. **Diz para quem é** (papel ou idade), ou é óbvio pela coisa?
5. **Pergunta aberta?** Não consigo dizer "ah, percebi" sem abrir a legenda.
6. **Tem 11 palavras ou menos e cabe em 80 caracteres?**
7. **Fala "tu" ou "eu"?** Sem terceira pessoa vaga, sem o nome da empresa.
8. **É verdade?** Os números e factos estão confirmados ou marcados.
9. **Soa a pessoa?** Lido em voz alta não soa a anúncio nem a guru, não tem "não é X, é Y".
10. **Não é um esqueleto copiado** de um exemplo de outro tema.
11. **É diferente dos últimos 14 dias** e a legenda paga a promessa.

## 16. Exemplos

**Bons** (os números são da conta de IA; os de psicomotricidade foram aprovados e ainda não têm números):

| Hook | Molde e gancho | Porque passa |
|---|---|---|
| OS ÚNICOS 3 / PLUGINS DO CLAUDE QUE / UM DONO PRECISA 🇵🇹 | lista, exclusividade + filtro | 4 970 views, 30 comentários |
| 3 PEDIDOS AO CLAUDE / QUE O TEU CONTABILISTA / VAI AGRADECER 🇵🇹 | lista, autoridade | 2 710 views; põe uma pessoa do mundo do leitor a validar |
| POV: UM SÓ COMANDO / DEU AO CLAUDE / 314 SKILLS NOVAS | POV, difícil de acreditar | 2 078 views; gesto pequeno, efeito enorme |
| OS ÚNICOS 3 / BRINQUEDOS QUE UMA / CRIANÇA DE 3 ANOS PRECISA | lista, exclusividade + idade | o especialista corta o excesso de brinquedos |
| 5 BRINQUEDOS CAROS / QUE NÃO SERVEM / PARA NADA | lista, contra a intuição + dinheiro | o leitor pensa logo nos que comprou |
| 3 FRASES QUE DIZES / AO TEU FILHO QUE / PIORAM AS BIRRAS | lista, hábito | "será que eu digo isto?" |
| O QUE UMA / PSICOMOTRICISTA NUNCA / DEIXA O FILHO FAZER | lista implícita, autoridade | o que só quem está por dentro sabe |
| 7 PRENDAS DE NATAL / QUE UMA PSICOMOTRICISTA / DAVA AOS FILHOS | lista, autoridade + momento do ano | só em novembro e dezembro |

**Maus:**

| Hook | Porque falha |
|---|---|
| 5 PERGUNTAS QUE / DIZEM SE ESTÁS / PRONTO PARA A IA | lista sem gancho e abstrata: 61 views |
| PAGAS O CLAUDE E / DEITAS DINHEIRO FORA / SE NÃO INSTALARES ISTO | condição: 54 views, 0 comentários |
| POV: SEGUNDA DE MANHÃ / E A SEMANA INTEIRA / CABE NUMA PÁGINA | POV de cena, nada de surpreendente: 200 views |
| POV: UMA BOLA DE TÉNIS / ACABOU COM A BIRRA / DOS SAPATOS | POV de cena noutro tema: ninguém pára |
| NÃO DÊS O TABLET / AO TEU FILHO ANTES / DE SABERES ISTO | esqueleto da conta de IA copiado para outro tema |
| 3 JOGOS PARA / CRIANÇAS | número + coisa, sem gancho nem filtro |
| A MAIOR PARTE DAS / CRIANÇAS NÃO BRINCA / O SUFICIENTE | terceira pessoa vaga, sem pergunta |
| 5 FORMAS DE POTENCIAR / O DESENVOLVIMENTO / DO TEU FILHO | "formas" e "potenciar": vago do princípio ao fim |

## 17. O que ainda não se sabe

As regras vêm de 53 trial reels de uma conta (novembro de 2026), de 114 reels anteriores da mesma conta, de 36 reels de referência e do feedback de quem usa o método. Ainda são apostas:

- **Que gancho rende mais em cada tema.** O campo `gancho` existe para a análise de 14 dias o medir.
- **Se a lista funciona igual fora da IA.** É a hipótese mais forte que temos, ainda sem números de outra conta.
- **Curto ou comprido.** Os dois reels de referência deste formato com mais comentários têm 16 e 21 palavras. Vale a pena testar o mesmo tema com 7 e com 14.

**Como ler resultados:** o mesmo hook já fez 1 387 views numa vez e 31 noutra. Um hook só se julga depois de sair 3 vezes; um gancho ou um molde, depois de 10. Numa conta destas, a mediana anda nas 250 views e o que faz crescer são as exceções, cerca de 1 reel em cada 10. Por isso o volume diário importa tanto como o hook.
