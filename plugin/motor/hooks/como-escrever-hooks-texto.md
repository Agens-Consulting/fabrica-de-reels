# Como escrever hooks de texto (tipo A: o texto manda ler a legenda)

Este documento é para quem vai escrever os hooks: uma IA ou uma pessoa que nunca viu este projeto. Lê-o inteiro antes de escrever o primeiro hook. O formato irmão, em que o dono da conta fala para a câmara, está em `como-escrever-hooks-fala.md`. O aspeto visual (letra, cor, posição) é um estilo fixo, está em `estetica-e-posicionamento.md` e não se decide aqui.

Antes de escrever, lê também `../onboarding/perfil.md` (quem é o dono da conta, para quem fala, tom) e `../banco/pesquisa-temas.md` (os temas aprovados). Os exemplos deste guia vêm de uma conta sobre IA para donos de PME em Portugal: servem para mostrar o padrão; troca o tema, as ferramentas e as coisas do dia a dia pelas do público da tua conta.

---

## 1. O que é este formato

Um vídeo de 6 segundos (máximo 8), sem fala, com imagens do dia a dia do dono da conta em fundo e **um único texto fixo no ecrã**. O vídeo não ensina nada. Todo o valor está na legenda: a lista, o prompt, o passo a passo. No fim da legenda há um pedido: "Comenta PALAVRA" e a pessoa recebe um recurso por mensagem.

O hook é esse texto. Tem três trabalhos, por esta ordem:

1. **Parar o dedo.** A pessoa está a fazer scroll e decide em menos de dois segundos.
2. **Escolher quem pára.** Queremos o público da conta (no exemplo: donos de empresas portuguesas), e não queremos curiosos nem público de outro país (ex.: brasileiro).
3. **Abrir uma pergunta que só a legenda responde.** É isto que distingue este formato de todos os outros.

Se o hook fizer os dois primeiros e falhar o terceiro, a pessoa lê, pensa "ok" e continua. O vídeo tem 6 segundos e não há mais nada para ver. O reel só rende se a pessoa abrir a legenda: enquanto lê, o vídeo repete em loop e o tempo de visualização acumula; no fim guarda ou comenta a palavra-chave.

**Como se mede:** comentários com a palavra-chave e guardados por cada 1 000 visualizações. As visualizações sozinhas não chegam.

## 2. Quem vai ler o hook

Os trial reels só são mostrados a **quem não segue a conta**. Isto muda a escrita:

- A pessoa não sabe quem é o dono da conta. O nome dele, o nome da empresa (e qualquer palavra em `HOOK_PALAVRAS_PROIBIDAS` no `.env`) e "a minha empresa" não lhe dizem nada. São palavras que ocupam espaço e não compram atenção.
- Não há contexto anterior. O hook tem de se perceber sozinho, à primeira leitura.
- Não há confiança. Qualquer coisa que soe a anúncio, a guru ou a frase feita é ignorada.

O leitor que queremos é o público da conta, descrito em `../onboarding/perfil.md`. Descreve-o com este grau de pormenor antes de escrever. Exemplo (a conta de IA para PME): dono ou sócio de uma empresa de serviços em Portugal, 38 a 50 anos, 5 a 30 pessoas. Faz orçamentos, propostas, responde a emails e a mensagens de clientes, tem reuniões a mais e tempo a menos. Já ouviu falar de ChatGPT, talvez de Claude, e usa-os pouco ou mal. Está no sofá às 22h a fazer scroll.

O teste que resume tudo: **esta pessoa parava aqui?** Se a resposta não for um sim claro, o hook não serve.

## 3. A regra central: mostrar o quê, esconder o resto

Um hook deste formato mostra **o quê** (o resultado, a situação, a categoria) e esconde **quais**, **como** ou **qual**. A resposta escondida é exatamente o que a legenda entrega.

**O teste do "ah, percebi".** Lê o hook como se fosses o leitor que queremos. Se conseguires pensar "ah, percebi" sem abrir a legenda, o hook entregou a recompensa e falhou. Se ficares com uma pergunta concreta na cabeça ("quais?", "como é que ele faz isso?", "que definições?"), está certo.

Exemplos reais do que funciona, com o que cada um esconde (os dois em português são da conta de exemplo):

| Hook | O que esconde | Resultado |
|---|---|---|
| "psycho things I did to make 370k on Instagram this year and buy my dream house" | as coisas | 473 comentários para 2 604 likes |
| "…these are the hooks [that] brought me 95K followers" | os hooks | 140 comentários para 366 likes |
| "Usar Claude numa empresa é deitar dinheiro fora se não fizeres isto (vê a legenda)" | o "isto" | 4 285 views, o melhor de sempre da conta de exemplo |
| "Não uses Claude na tua empresa antes de saberes isto 👇" | o "isto" | 1 387 views |

Exemplos reais do que falha, e porquê:

| Hook | Problema |
|---|---|
| "Nothing better than meeting the girl of your dreams and it motivates you to be better in life" | Frase completa. Concorda-se e passa-se. 867 likes, **0 comentários** |
| "Pagamos 90€ por mês a uma IA que faz o trabalho de 3 pessoas (o que ela faz ↓)" | Conta a história toda: preço, ferramenta e resultado. O parêntese ainda dá a pista do que falta |
| "Fazia uma proposta num dia. Agora demoro menos que este reel" | Antes e depois completos. Não sobra pergunta |
| "Faturar mais com serviços não é ter mais clientes. É isto." | Soa a frase feita. 36 views |

**Sinais de que o hook fechou a pergunta:** termina num aforismo, tem o antes e o depois com números dos dois lados, tem duas frases em que a segunda explica a primeira, ou tem um parêntese que descreve o que está na legenda.

## 4. Os três moldes

Só se usam estes três. São os que têm provas, nos reels de referência e nos números dos testes que deram origem a este método. Não inventar moldes novos: a regra é insistir no que resulta em vez de variar.

Num lote de 10 hooks: **4 listas, 4 POV, 2 condições.**

### Molde 1: lista com número

`[N] + [coisa concreta] + [o que a coisa dá ou tira]`

A pergunta que fica: **quais?**

- **O número** vai de 3 a 7. Diz à pessoa que o esforço é pequeno e finito. Escreve-se em algarismo e é quase sempre a palavra de destaque.
- **A coisa** é um substantivo que se pode apontar: prompts, definições, automações, tarefas, erros, perguntas. Nunca "dicas", "formas", "estratégias" ou "segredos".
- **O que dá ou tira** é o que faz o dono querer a lista: tempo, clientes, dinheiro, trabalho à mão. Tem de ser coisa do dia dele.

| Certo | Errado | Porquê |
|---|---|---|
| **3 definições** do Claude que tens de mudar hoje | 3 dicas para usar melhor a IA | "dicas" e "IA" são vagos; "definições do Claude" aponta para uma coisa que existe |
| **5 tarefas** que nunca mais vais fazer à mão | 5 tarefas que a IA faz: emails, propostas, faturas… | o segundo dá a lista |
| **3 erros** com IA que te estão a custar clientes | 3 erros comuns na utilização de inteligência artificial | sem consequência, sem "tu" |

### Molde 2: POV

`pov: + [tu] + [uma situação concreta, no presente, que o dono quer viver ou acabou de descobrir]`

A pergunta que fica: **como é que se chega aí?**

- Escreve-se "pov:" em minúsculas, como na internet.
- A situação tem de ter **um detalhe concreto**: um número, um objeto, uma hora, uma pessoa. É o detalhe que a torna verdadeira.
- Mostra o resultado e nunca o mecanismo. "pov: o teu concorrente faz orçamentos em 3 minutos" funciona porque não diz como.
- Dois tipos servem: a situação desejada ("abres o portátil e o trabalho da noite já está feito") e a descoberta ("descobriste o que o Claude faz aos teus emails").
- O POV que aponta o dedo ("pov: és dono e ainda fazes tudo sozinho") fica de fora até haver dados. O único parecido que se publicou nos testes teve 38 views.

Hooks POV aprovados na conta de exemplo, para apanhar o tom:

- pov: os teus concorrentes ainda fazem orçamentos à mão e tu demoras 3 minutos
- pov: abres o portátil de manhã e o trabalho da noite anterior já está feito
- pov: o teu cliente pergunta como fazes tudo tão rápido e tu não sabes se deves contar

Estão compridos para a regra de hoje. Servem pelo tom e pelo detalhe, não pelo tamanho.

### Molde 3: condição escondida

`[ferramenta com nome] + [consequência] + se não fizeres isto / antes de saberes isto`

A pergunta que fica: **o que é "isto"?**

É o molde com os melhores números da conta de exemplo (4 285, 1 533 e 1 387 views). Tem duas regras que não se podem falhar:

- **A ferramenta tem nome.** "Claude", "ChatGPT", "Claude Code". Com "ferramenta de IA" em vez do nome, o mesmo molde fez 17 a 48 views.
- **Máximo 2 em cada 10 hooks, e nunca dois parecidos em 14 dias.** Quando se publicaram variantes quase iguais ("antes de saberes isto" e "antes de fazeres isto"), o Instagram avisou que a conta publicava conteúdo muito parecido.

A versão com comparação também rendeu: "pov: tens uma empresa e percebeste que ChatGPT é muito melhor que Claude (a menos que faças isto)" fez 1 794 views. Junta o POV com a condição.

## 5. Cortar palavras

Cada palavra tem de ganhar o lugar. É uma regra de base e os reels de referência confirmam: os hooks de texto têm quase todos entre 3 e 11 palavras.

**Alvo: 6 a 9 palavras. Máximo: 11.**

Há também um limite físico. Com a letra definida, cabem cerca de 22 caracteres por linha e 3 linhas. **Ideal: até 55 caracteres com espaços. Máximo absoluto: 80**, e aí a letra já encolhe.

Como cortar, por esta ordem:

1. **Tira quem ninguém conhece:** "na [nome da empresa]", "na minha empresa", "eu e a minha equipa".
2. **Tira a segunda frase.** Se o hook funciona sem ela, ela sai. Quase sempre é a segunda frase que entrega a recompensa.
3. **Tira os enchimentos:** "todos os dias", "realmente", "simplesmente", "de forma", "que eu uso".
4. **Troca expressões por palavras:** "donos de empresa" em vez de "todas as pessoas que têm um negócio".
5. **Faz o teste palavra a palavra.** Tira uma palavra de cada vez. Se o hook continua a parar o dedo e a pergunta continua aberta, a palavra estava a mais.

| Antes | Depois |
|---|---|
| 7 prompts de Claude que uso todas as semanas na minha empresa (copia da legenda ↓) | **7 prompts** de Claude para donos de empresa |
| As únicas 2 ferramentas de IA que pago na minha empresa (e o que faço com cada uma) | As únicas **2 ferramentas** de IA que pago |
| Se abrisse uma empresa amanhã, eram estas as 4 automações do dia 1 (por esta ordem) | **4 automações** que punha no dia 1 de qualquer negócio |

**O que nunca se corta:** o número, o nome da ferramenta e o detalhe concreto. São eles que fazem parar. Um hook curto e vago é pior do que um hook comprido e concreto.

**Palavras simples.** Um estudo de 2024 com quase 30 mil testes de títulos (Washington Post e Upworthy) mostrou que ganham as palavras comuns e as frases curtas. Entre "utilizar" e "usar", é "usar". Entre "implementar" e "pôr", é "pôr".

Cortar não é escrever em telegrama. A frase tem de continuar a soar a alguém a falar.

## 6. Ser concreto

O tema "Claude e IA no negócio" teve uma mediana de 259 views na conta de exemplo. Os temas genéricos ("faturar mais", "ter mais tempo") ficaram entre 59 e 81. Nos reels de referência passa-se o mesmo: o mesmo criador teve 2 443 likes num vídeo sobre trial reels e 195 num sobre marca pessoal.

- **Diz o nome da ferramenta (ou da coisa):** no exemplo, Claude, ChatGPT, Claude Code. "IA" sozinho só quando não há ferramenta em causa. Noutro tema, o mesmo: o nome concreto em vez da categoria.
- **Usa as coisas do dia do leitor:** no exemplo, orçamentos, propostas, emails, faturas, reuniões, mensagens de clientes, a folha de Excel, o WhatsApp.
- **Usa números:** 3 minutos, 5 tarefas, 90€ por mês.
- **Palavras proibidas por serem vagas:** produtividade, eficiência, otimizar, transformação digital, potenciar, soluções, o futuro, revolucionar.

## 7. Voz e tom

- **Quem fala é o dono da conta ("eu") ou fala-se para o leitor ("tu").** Nunca uma terceira pessoa: "o cliente faturava 300k" e "a maior parte das empresas…" foram rejeitados ou renderam mal.
- **Português de Portugal.** "Tu", "empresa", "equipa", "ecrã", "telemóvel". Nada de "você", "time", "tela", "usuário".
- **Tom de quem descobriu uma coisa e a mostra.** Não de quem sabe mais do que o leitor.
- **O negativo ataca o hábito, nunca a pessoa.** "3 erros com IA que te estão a custar clientes" serve. "Não tens uma empresa, tens um emprego" não serve.
- **Verbos que se dizem.** "Vou destruir", "aqui está", "isto é o que faço". Não "destruo", "conto como", "mostro-te".
- **Nunca "não é X, é Y".** É o tique mais reconhecível de texto feito por IA, e quem lê deteta-o à primeira.
- **Sem travessões, sem três adjetivos seguidos, sem pontos de exclamação.**

Tudo o que soe a guru, vendedor, anúncio de televisão ou frase motivacional do LinkedIn sai.

## 8. A bandeira 🇵🇹

Para contas que falam para Portugal. Serve para filtrar: diz ao algoritmo e à pessoa que o vídeo é para Portugal, e afasta o público brasileiro. Nos números dos testes, 3 dos 10 melhores reels tinham "em Portugal" no hook.

- **Usa-se em alguns hooks, não em todos:** 3 ou 4 em cada 10.
- **Nunca se escreve a palavra "Portugal".** Só a bandeira.
- **Fica no fim da última linha.**
- **Onde encaixa melhor:** quando o hook fala de um grupo ("donos de empresa", "PME") ou de concorrência. Num POV íntimo pode ficar de fora.
- **O que não se sabe:** não há dados públicos sobre o efeito de uma bandeira num hook. É um sinal para quem lê; não está provado que conte para o algoritmo. O português de Portugal e os valores em euros também filtram, por isso valem para todos os hooks, com ou sem bandeira.

## 9. A segunda linha

Por baixo do hook pode ir uma linha pequena. Só há duas hipóteses válidas:

- **Apontar para a legenda:** só com o segundo hook entre parênteses ("(vê a legenda)", "(está tudo na legenda)"…), que o script põe ou não, sozinho. **Setas (↓, 👇) no ecrã nunca** (regra de base do estilo fixo). Quem escreve o hook não escreve esta linha.
- **Aumentar a pergunta:** "(a 2.ª é a que ninguém muda)", "(a menos que faças isto)".

**Nunca uma linha que descreva o que está na legenda:** "(o que ela faz)", "(e as horas que poupei)", "(passo a passo)". Isso é dar a pista.

## 10. O hook nunca se escreve sozinho

Um hook deste formato é uma promessa, e a legenda é o pagamento. Escrevem-se juntos:

- **A recompensa:** o que a legenda entrega, numa frase. Se o hook diz "7 prompts", a legenda tem 7 prompts.
- **A palavra-chave:** escolhe-se e cria-se pelo processo de `../ctas/como-construir-cta.md`. Tem de ser rara e única: palavras como PROMPTS, CLAUDE ou TAREFAS são recusadas pelo Zernio. Por isso a ligação ao hook faz-se pelo tema, não pela palavra igual: hook com "7 prompts", legenda a abrir com "PROMPTS ↓", pedido "Se queres os 7 prompts prontos a copiar, comenta CABULA".
- **O pedido de comentário vai no fim da legenda.** Quando se pôs cedo, os guardados caíram para metade.
- **Só se promete o que existe.** Cada número e cada facto têm de ser verdade para o dono da conta. O que não estiver confirmado leva a marca `[CONFIRMAR]`. Um cenário inventado ("mandei mensagem às 22h e acordei com 3 propostas") soa a anúncio e foi rejeitado.

## 11. Como produzir um lote

**O que tens de ter antes de começar.** Se faltar alguma destas coisas, pede-a. Não inventes.

1. O tema e a recompensa: o que a legenda vai entregar.
2. Factos reais do dono da conta sobre esse tema: números, ferramentas, o que fez (vêm de `../onboarding/perfil.md` ou pergunta-se).
3. A lista dos hooks publicados nos últimos 14 dias.

**Passos:**

1. Escreve a recompensa numa frase. Exemplo: "os 7 prompts que o dono da conta usa para preparar reuniões, propostas e emails".
2. Escreve a pergunta que o leitor tem de ficar a fazer. Exemplo: "quais são os 7?".
3. Escreve 15 a 20 hooks em bruto, pelos três moldes.
4. Corta as palavras (secção 5).
5. Passa cada um pela lista de verificação (secção 12). O que falhar um ponto sai ou é reescrito.
6. Compara com os hooks dos últimos 14 dias. Se dois diferem só numa palavra ou num número, fica um.
7. Escolhe os 10 melhores com a divisão 4 listas, 4 POV, 2 condições, e a bandeira em 3 ou 4.

**Vários hooks para o mesmo vídeo.** Cada vez que o mesmo vídeo volta a sair, leva um hook novo (ver `../edicao/variacoes.md`). Uma variação nova muda de molde ou de ângulo. Trocar "saberes" por "fazeres" não é uma variação: é um clone.

**Formato de entrega**, uma linha por hook:

| Campo | Conteúdo |
|---|---|
| Hook | o texto, já com as quebras de linha marcadas com " / " |
| Destaque | a palavra (no máximo duas) que fica a amarelo |
| Segunda linha | não se escreve: o script sorteia nada ou um segundo hook entre parênteses; setas nunca |
| Bandeira | sim ou não |
| Molde | lista, POV ou condição |
| Pergunta que fica | "quais?", "como?", "o que é isto?" |
| Recompensa | o que a legenda entrega |
| Palavra-chave | a palavra do pedido de comentário |
| A confirmar | factos ou números por validar com o dono da conta |
| Palavras e caracteres | a contagem |

**Quebras de linha:** 2 ou 3 linhas, partidas onde a pessoa faria uma pausa a ler. Nunca separar o número da coisa ("7 / prompts") nem deixar uma palavra sozinha na última linha.

## 12. Lista de verificação

Um hook só é entregue se passar todos os pontos.

1. **Pára?** O leitor que queremos, no sofá às 22h, parava aqui.
2. **Pergunta aberta?** Não consigo dizer "ah, percebi" sem abrir a legenda.
3. **É um dos três moldes?**
4. **Tem 11 palavras ou menos e cabe em 80 caracteres?**
5. **Sobrevive ao teste palavra a palavra?** Não há nenhuma palavra que possa sair.
6. **É concreto?** Tem um nome de ferramenta, um número ou uma coisa do dia do leitor.
7. **Fala "eu" ou "tu"?** Sem terceira pessoa, sem o nome da empresa, sem "a minha empresa".
8. **É verdade?** Os números e factos estão confirmados ou marcados.
9. **Soa a pessoa?** Lido em voz alta não tropeça, não soa a anúncio nem a guru, não tem "não é X, é Y".
10. **É diferente dos últimos 14 dias?**
11. **A legenda paga a promessa** e a palavra-chave é a palavra do hook.

## 13. Exemplos

Servem para mostrar o padrão. Não copiar a estrutura palavra por palavra: dez hooks com o mesmo esqueleto são dez clones.

**Bons** (da conta de exemplo):

| Hook | Molde | Porque passa |
|---|---|---|
| **7 prompts** de Claude para donos de empresa 🇵🇹 | lista | número, ferramenta com nome, diz para quem é; fica "quais?" |
| **3 definições** do Claude que tens de mudar hoje | lista | coisa que se pode apontar, urgência, "tu" |
| **5 tarefas** que nunca mais vais fazer à mão | lista | fala de trabalho que o dono detesta; fica "quais?" |
| pov: o teu concorrente faz orçamentos em **3 minutos** 🇵🇹 | POV | detalhe concreto, medo de ficar para trás; fica "como?" |
| pov: abres o portátil e o trabalho da noite **já está feito** | POV | situação desejada, sem mecanismo |
| pov: descobriste o que o Claude faz aos teus **emails** | POV | descoberta; esconde o "o quê" |
| Não uses Claude na tua empresa antes de **mudares isto** 👇 | condição | ferramenta com nome; fica "o que é isto?" |

**Maus:**

| Hook | Porque falha |
|---|---|
| 5 formas de usar a IA para aumentar a produtividade do teu negócio | vago do princípio ao fim; podia ser de qualquer conta |
| A maior parte das empresas não sabe usar IA por causa disto | terceira pessoa, sem voz; este molde foi repetido 12 vezes e estragou a conta de exemplo |
| Poupei 12 horas por semana com 3 automações: emails, faturas e relatórios | entrega tudo |
| Não és dono de uma empresa, és empregado dela | "não é X, é Y", tom de guru |
| Na [nome da empresa] usamos o Claude para tudo e os resultados são incríveis | fala de quem ninguém conhece, sem pergunta, com adjetivo vazio |
| O futuro das PME passa pela inteligência artificial | frase de conferência; ninguém pára |

## 14. O que ainda não se sabe

Estas regras vêm de três fontes, por ordem de confiança: os números dos testes que deram origem a este método (114 reels de uma conta), 36 reels de referência escolhidos a dedo (só com likes e comentários, de contas maiores e noutras línguas) e o feedback direto do dono dessa conta. Na tua conta, os ciclos de 14 dias vão confirmando ou corrigindo. Algumas coisas ainda são apostas:

- **Seta, emoji ou "(vê a legenda)":** qual rende mais.
- **Bandeira no fim ou no início** do hook.
- **Com ou sem segunda linha.**
- **Negativo ou positivo** para o mesmo tema.
- **Curto ou comprido.** A regra de base é cortar. Mas os dois reels de referência deste formato com mais comentários têm 16 e 21 palavras, cheias de números. Vale a pena testar o mesmo tema com 7 palavras e com 14.

Um aviso sobre como ler resultados: o mesmo hook ("Não uses Claude na tua empresa antes de saberes isto") fez 1 387 views numa publicação e 31 noutra. **Um hook só se julga depois de sair pelo menos 3 vezes**, com vídeos diferentes.

Quando houver dados novos, este documento é atualizado: o que ganhar passa a regra, o que perder sai.
