# Como escrever hooks de fala (tipo B: o dono da conta fala, o hook só prende)

Este documento é para quem vai escrever os hooks: uma IA ou uma pessoa que nunca viu este projeto. Lê-o inteiro antes de escrever o primeiro hook. O formato irmão, só com texto no ecrã, está em `como-escrever-hooks-texto.md`. O aspeto visual (letra, cor, posição) é um estilo fixo, está em `estetica-e-posicionamento.md` e não se decide aqui.

Antes de escrever, lê também `../onboarding/perfil.md` (quem é o dono da conta, para quem fala, tom) e `../banco/pesquisa-temas.md` (os temas aprovados). Os exemplos em português deste guia vêm de uma conta sobre IA para donos de PME em Portugal: servem para mostrar o padrão; troca o tema, as ferramentas e as coisas do dia a dia pelas do público da tua conta. Na prática, estes vídeos são editados e publicados pela skill `fabrica-de-reels:reel-talking-head` (ver `../talking-head/README.md`), que segue este guia.

---

## 1. O que é este formato

Um vídeo de 30 a 90 segundos em que o dono da conta fala para a câmara e entrega o conteúdo todo: a lista, o método, a demonstração. A legenda é curta. No fim do vídeo há um pedido: "Comenta PALAVRA" e a pessoa recebe um recurso por mensagem.

Aqui o hook não manda ninguém para a legenda. Tem três trabalhos:

1. **Parar o dedo** nos dois primeiros segundos.
2. **Escolher quem pára:** o público da conta (no exemplo, donos de empresas portuguesas).
3. **Prometer uma coisa que só se recebe vendo o vídeo**, e montar a estrutura que segura a pessoa até ao fim.

O hook deste formato tem **três peças que se escrevem juntas**:

- **O texto no ecrã**, que funciona como título.
- **As primeiras frases ditas**, nos primeiros 8 a 10 segundos.
- **A prova visual**, o que se vê nos dois primeiros segundos.

Escrever só o texto do ecrã é entregar um terço do trabalho.

**Como se mede:** quanto tempo as pessoas ficam (tempo médio de visualização e percentagem que chega ao fim), e os comentários com a palavra-chave.

## 2. Quem vai ver

Os trial reels só são mostrados a **quem não segue a conta**:

- A pessoa não sabe quem é o dono da conta. O nome dele, o nome da empresa (e qualquer palavra em `HOOK_PALAVRAS_PROIBIDAS` no `.env`) e "a minha empresa" não lhe dizem nada.
- Não há confiança. O que soar a anúncio ou a guru é ignorado.
- Num teste publicado com 40 trial reels, o formato "especialista a dar um conselho" foi o pior de todos (mediana de 171 views). Por isso o hook nunca se enquadra como "dica": enquadra-se como um caso, um custo, um desafio ou uma situação.

O espectador que queremos é o público da conta, descrito em `../onboarding/perfil.md`, com este grau de pormenor. Exemplo (a conta de IA para PME): dono ou sócio de uma empresa de serviços em Portugal, 38 a 50 anos, 5 a 30 pessoas. Faz orçamentos e propostas, responde a emails e mensagens de clientes, tem reuniões a mais. Usa o ChatGPT pouco ou mal. Está no sofá às 22h.

O teste que resume tudo: **esta pessoa parava aqui, e ficava?**

## 3. As três peças

### 3.1 O texto no ecrã

É um título. Diz o tema e a promessa em poucas palavras, no terço de cima do ecrã.

- **4 a 9 palavras** na linha principal. Limite físico: cerca de 22 caracteres por linha, no máximo 3 linhas; ideal até 55 caracteres.
- **Uma palavra de destaque** (no máximo duas), a amarelo: o número, o resultado ou a ferramenta.
- **Fica no ecrã 3 a 5 segundos** quando a seguir vem um passo a passo. Depois, o mesmo sítio passa a mostrar o ponto em que o vídeo vai ("1) …", "2) …"), um contador ou a ferramenta. Fica o vídeo todo quando é uma situação ou uma promessa única.

**A segunda linha entre parênteses.** Ao contrário do formato só com texto, aqui usa-se e recomenda-se. Está nos reels de referência com mais likes. Vai em letra mais pequena e faz um destes quatro serviços:

| Serviço | Exemplo real |
|---|---|
| Diz para quem é | "How to build a 10/10 schedule **(9-5 edition)**" |
| Diz que é um sistema | "How to systematically stop doomscrolling **(Follow this protocol)**" |
| Promete facilidade ou rapidez | "kill your camera fear in 60 seconds **(or less)**" |
| Promete novidade ou história | "Trial Reel Maxxing **(new method)**" · "Claude FIRED my video editors?! **(So this is what I did)**" |

Em português: "(versão para donos de empresa)", "(segue este protocolo)", "(ou menos)", "(e foi isto que fiz)". Máximo 5 palavras.

### 3.2 As primeiras frases ditas

Quem fala começa **no segundo zero**. Sem "olá", sem nome, sem "hoje vou falar de".

A abertura tem três tempos, e cabe em 8 a 10 segundos. Cada tempo abre uma pergunta nova e nenhum dá a resposta:

1. **Hook.** Diz em voz alta o que está no ecrã, numa frase natural. Até 15 a 18 palavras, 4 a 6 segundos.
2. **"Mas".** Uma frase que complica, levanta a aposta ou responde à dúvida que o espectador ia ter.
3. **Promessa.** O que a pessoa leva se ficar. Liga diretamente ao primeiro ponto.

Abertura real que segue isto quase à letra (Max Hagan, sobre Claude):

> "This morning, I let go of every editor who works at my company… because Claude is doing a better job for a tenth of the price." **(hook)**
> "And I'm such a skeptic. I always ask, is it really that good?" **(a dúvida do espectador)**
> "I'm going to show you exactly how it works. So step one…" **(promessa e entrada no conteúdo)**

A regra de base, num molde para decorar: *"Demorei 7 anos a aprender X. **Mas** não o podes fazer sempre, senão não resulta. **Mas** quando fiz, consegui X, Y, Z."*

**A relação entre o ecrã e a fala.** Nos reels de referência, a primeira frase dita é o texto do ecrã dito por extenso. O ecrã é a versão comprimida:

| Ecrã | Primeira frase dita |
|---|---|
| "You should post every idea." | "You really should just post every idea that pops in your head." |
| "Destroying 6 of your excuses in 60 seconds" | "I'm about to destroy six of your biggest excuses in under 60 seconds." |
| "how to turn Claude into a storytelling coach" | "Here's how I turned Claude into a storytelling coach to get me 70 million views in the last 30 days." |
| "Quanto gasto por mês para manter as minhas apps no ar?" | "Quanto é que eu gasto por mês para manter as minhas apps no ar?" |

Repara no terceiro: a fala repete o ecrã e **acrescenta a prova** ("70 million views in the last 30 days"). É isto que se quer. O ecrã dá o tema; a fala dá o tema mais a razão para acreditar.

**O que a segunda frase pode trazer.** Estes são os recursos que aparecem nas referências. Escolhe um, o que for verdade para o dono da conta:

| Recurso | Exemplo real | Em português |
|---|---|---|
| Resultado próprio com número | "…to get me 70 million views in the last 30 days" | "…e deixei de perder 6 horas por semana com isto" |
| Autoridade emprestada | "This is the same way that McKinsey, Bain, and BCG… run theirs" | "É assim que as consultoras grandes fazem" |
| "Se eu começasse do zero" | "If I woke up tomorrow and lost my ability to lock in, this would be the exact system I would rebuild first" | "Se amanhã abrisse uma empresa do zero, era por aqui que começava" |
| Vantagem de quem começa cedo | "The ones who start right now are the ones who are gonna get rich" | "Quem começar agora fica com a vantagem" |
| Escalada | "…but they become increasingly more effective" | "…e cada um poupa mais tempo do que o anterior" |
| Pedido de guardar | "E vais querer guardar este vídeo." | igual |
| A dúvida do espectador dita em voz alta | "And I'm such a skeptic…" | "Eu também achava que isto era conversa" |

O "se eu começasse do zero" aparece em três dos reels com mais likes (327 772, 84 625 e 195, este último num tema genérico). A escalada e o pedido de guardar dão à pessoa um motivo para ficar até ao fim.

### 3.3 A prova visual

O que se vê nos dois primeiros segundos, ao mesmo tempo que o texto e a fala. Nos reels de referência quase nunca é só uma cara:

- um **cronómetro** a contar ("…in 60 seconds");
- um **contador de custos** a subir a amarelo ("Quanto gasto por mês…");
- o **portátil virado para a câmara** a fazer de slide, com os passos numerados;
- **prints de resultados** reais por baixo do texto;
- a **ferramenta aberta** no ecrã;
- **cartões com perguntas** ("Você não sabe nada de marketing" seguido de um teste).

Cada hook entregue diz qual é a prova visual. Se não houver nenhuma possível, o hook é mais fraco do que parece.

## 4. Os moldes

Insiste-se no que resulta em vez de variar. Num lote de 10 hooks: **4 listas, 3 "como", 2 POV, 1 afirmação com prova.**

### Molde 1: lista com número

`[N] + [coisa concreta] + [o que dá ou tira]`, muitas vezes com um prazo.

- "Vou destruir **5 desculpas** para não usares IA (em 60 segundos)"
- "**5 coisas** que queria saber antes de usar IA no negócio"
- Referências: "Destroying 6 of your excuses in 60 seconds" (87 740 likes), "5 plugins obrigatórios para quem usa claude code" (800 comentários para 751 likes), "10/10 neuroscience habits to make you disgustingly well spoken" (74 988 likes).

A lista dá ao vídeo uma estrutura que segura: a pessoa sabe quantos faltam. O número do hook tem de ser o número de pontos do vídeo.

### Molde 2: "como"

`Como + [resultado concreto que o espectador quer]` + segunda linha entre parênteses.

- "Como pôr o Claude a responder aos teus **emails** (segue este protocolo)"
- "Como fazer uma reunião de equipa em **15 minutos**"
- Referências: "How to systematically lock in (Follow this protocol every time)" (327 772 likes, o mais alto de todos), "how to turn Claude into a storytelling coach" (16 886 comentários), "How to Run a 10/10 Exec Meeting" (8 587 comentários), "Como construir uma app que consegues monetizar" (português, 690 comentários).

O "como" sozinho é fraco ("Como usar IA"). Fica forte com um resultado que se pode ver ("responder aos teus emails") ou com uma palavra de sistema ("protocolo", "10/10", "passo a passo").

### Molde 3: POV

`pov: + [tu] + [situação concreta que o espectador quer viver ou acabou de descobrir]`

- "pov: tens uma IA a trabalhar **enquanto dormes**"
- Referência: "Pov: You found the best LinkedIn hack of all time" (3 026 comentários para 2 567 likes).

No vídeo, quem fala mostra a situação a acontecer. O POV sem demonstração fica vazio.

### Molde 4: afirmação com prova

Uma frase curta e forte, seguida logo de uma prova ou de um teste. Máximo 1 em cada 10.

- "Em **5 anos** todas as PME vão fazer isto" (referência: "In 5 yrs everybody will be doing this", 83 867 comentários)
- "Aposto que usas mal o **ChatGPT**", seguido de "Faz este teste. Três perguntas." (referência: "Você não sabe nada de marketing", 86 805 likes, seguido de cartões com perguntas)
- "Quanto pago por mês em **IA**" (referência: "Quanto gasto por mês para manter as minhas apps no ar?", português, 2 393 likes)

O negativo só funciona quando vem colado a um teste ou a uma prova. Sozinho, é um insulto.

## 5. Cortar palavras

**No texto do ecrã**, cada palavra tem de ganhar o lugar:

1. **Tira quem ninguém conhece:** "na [nome da empresa]", "na minha empresa".
2. **Tira os enchimentos:** "todos os dias", "realmente", "de forma".
3. **Faz o teste palavra a palavra:** tira uma de cada vez; se o título continua a parar, ela estava a mais.
4. **Nunca cortes o número, o nome da ferramenta nem o detalhe concreto.** Um título curto e vago é pior do que um comprido e concreto.

| Antes | Depois |
|---|---|
| Quanto pago por mês em IA na minha empresa | Quanto pago por mês em **IA** |
| A IA que trabalha na minha empresa enquanto eu durmo | pov: tens uma IA a trabalhar **enquanto dormes** |
| Como fazer uma reunião de equipa de 15 minutos com IA | Reuniões de equipa em **15 minutos** |

**Na fala**, a regra é outra. Corta-se a introdução e a repetição, mas a frase tem de soar a pessoa a falar. "Vou destruir 5 desculpas" diz-se; "Destruo 5 desculpas" não se diz. Uma frase dita aguenta mais palavras do que uma frase escrita.

**Palavras simples**, no ecrã e na fala: "usar" e não "utilizar", "pôr" e não "implementar".

## 6. Ser concreto

O tema "Claude e IA no negócio" teve uma mediana de 259 views na conta de exemplo; os temas genéricos ficaram entre 59 e 81. Nas referências, o mesmo criador teve 2 443 likes num vídeo sobre trial reels e 195 num sobre marca pessoal, com o mesmo cenário e a mesma abertura.

- **Diz o nome da ferramenta (ou da coisa):** no exemplo, Claude, ChatGPT, Claude Code.
- **Usa as coisas do dia do espectador:** no exemplo, orçamentos, propostas, emails, faturas, reuniões, mensagens de clientes.
- **Usa números:** 15 minutos, 5 desculpas, 60 segundos, 90€ por mês.
- **Palavras proibidas por serem vagas:** produtividade, eficiência, otimizar, transformação digital, potenciar, soluções, o futuro, revolucionar.

## 7. Voz e tom

- **Quem fala é o dono da conta ("eu") ou fala-se para o espectador ("tu").** Nunca uma terceira pessoa a fazer de protagonista ("um cliente meu faturava…").
- **Português de Portugal.** "Tu", "empresa", "equipa", "ecrã". Nada de "você", "time", "tela".
- **Tom de quem descobriu uma coisa e a mostra.** Não de quem sabe mais.
- **O negativo ataca o hábito, nunca a pessoa**, e vem com teste ou prova.
- **Frases que fluem ditas em voz alta.** Servem: "Aqui está como", "Isto é o que eu fiz", "Vou destruir", "Deixa-me explicar". Não servem: "Conto como", "Mostro-te", "Digo tudo".
- **Nunca "não é X, é Y".** É o tique mais reconhecível de texto feito por IA. A abertura do Max Hagan tem um ("It's not just good, it's scarily good"): a estrutura dele copia-se, essa frase não.
- **Sem três adjetivos seguidos, sem perguntas retóricas em série.**

Lê a abertura em voz alta. Se tropeças, se há um som duro a meio ou se parece lida de um papel, reescreve.

## 8. A bandeira 🇵🇹

Para contas que falam para Portugal. Serve para filtrar: diz à pessoa que o vídeo é para Portugal e afasta o público brasileiro.

- **Usa-se em alguns hooks, não em todos:** 3 ou 4 em cada 10.
- **Nunca se escreve a palavra "Portugal" no ecrã.** Só a bandeira, no fim da última linha do título.
- **Na fala, pode-se dizer "em Portugal"** quando for natural. O sotaque já faz parte do filtro.
- Não há dados públicos sobre o efeito da bandeira. É um sinal para quem lê, e mede-se nos resultados da conta.

## 9. O hook é um contrato com o vídeo

- **O que o hook promete, o vídeo entrega.** "5 desculpas" são 5 desculpas. "Em 60 segundos" são 60 segundos, com o cronómetro à vista.
- **O hook escolhe a estrutura que segura:** lista numerada visível, cronómetro, contador, escalada, série ("Dia 1/30"). Cada hook entregue diz qual é.
- **O pedido de comentário vai no fim**, dito por quem fala e escrito na legenda. Quando se pôs cedo, os guardados caíram para metade. A palavra-chave escolhe-se pelo processo de `../ctas/como-construir-cta.md`: rara, única e ligada ao tema. Título com "emails", pedido "Se queres o guia para pôr o Claude a responder aos teus emails, comenta ATALHO".
- **Só se promete o que existe.** Cada número e cada facto têm de ser verdade para o dono da conta. O que não estiver confirmado leva a marca `[CONFIRMAR]`.

## 10. Como produzir um lote

**O que tens de ter antes de começar.** Se faltar, pede. Não inventes.

1. O tema e o que o vídeo entrega, ponto por ponto.
2. Factos reais do dono da conta sobre esse tema: números, ferramentas, o que fez (vêm de `../onboarding/perfil.md`, da própria gravação ou pergunta-se).
3. A lista dos hooks publicados nos últimos 14 dias.

**Passos:**

1. Escreve numa frase o que a pessoa leva se vir o vídeo até ao fim.
2. Escolhe o molde e a estrutura que segura.
3. Escreve o título do ecrã e corta as palavras.
4. Escreve os três tempos da fala. Lê em voz alta.
5. Decide a prova visual dos dois primeiros segundos.
6. Passa pela lista de verificação (secção 11).
7. Compara com os últimos 14 dias. Se dois diferem só numa palavra, fica um.

**Vários hooks para o mesmo vídeo.** O mesmo vídeo pode sair várias vezes com um título de ecrã diferente (ver `../edicao/variacoes.md`). A fala já está gravada, por isso o título novo tem de continuar a bater certo com a primeira frase dita. Muda-se o ângulo: lista em vez de "como", outra palavra de destaque, outro parêntese. Trocar uma palavra por um sinónimo é um clone, não uma variação.

**Formato de entrega**, por cada hook:

| Campo | Conteúdo |
|---|---|
| Ecrã, linha 1 | o título, com as quebras de linha marcadas com " / " |
| Ecrã, linha 2 | o parêntese, ou nenhum |
| Destaque | a palavra (no máximo duas) a amarelo |
| Bandeira | sim ou não |
| Molde | lista, como, POV ou afirmação com prova |
| Fala 1: hook | a primeira frase dita |
| Fala 2: "mas" | a frase que levanta a aposta |
| Fala 3: promessa | a frase que liga ao primeiro ponto |
| Prova visual | o que se vê nos dois primeiros segundos |
| Estrutura que segura | lista, cronómetro, contador, escalada, série |
| Palavra-chave | a palavra do pedido final |
| A confirmar | factos ou números por validar com o dono da conta |

## 11. Lista de verificação

Um hook só é entregue se passar todos os pontos.

1. **Pára e fica?** O espectador que queremos, no sofá às 22h, parava aqui e queria ver o resto.
2. **Estão as três peças?** Título, três tempos de fala e prova visual.
3. **É um dos quatro moldes?**
4. **O título tem 9 palavras ou menos**, e o parêntese 5 ou menos?
5. **A primeira frase dita começa no segundo zero** e bate certo com o título?
6. **A segunda frase acrescenta alguma coisa** (prova, aposta, dúvida do espectador) em vez de repetir?
7. **Nenhum dos três tempos entrega a resposta?**
8. **É concreto?** Nome de ferramenta, número ou coisa do dia do espectador.
9. **Fala "eu" ou "tu"?** Sem o nome da empresa, sem "a minha empresa".
10. **É verdade?** Números e factos confirmados ou marcados.
11. **Diz-se bem em voz alta?** Sem tropeços, sem tom de guru, sem "não é X, é Y".
12. **O vídeo entrega exatamente o que o hook promete?**
13. **É diferente dos últimos 14 dias?**

## 12. Exemplos completos

Servem para mostrar o padrão. Não copiar a estrutura palavra por palavra.

**Bons** (da conta de exemplo):

| Ecrã | Fala (hook → "mas" → promessa) | Prova visual | Segura com |
|---|---|---|---|
| Vou destruir **5 desculpas** para não usares IA / (em 60 segundos) | "Vou destruir cinco desculpas para não usares IA na tua empresa. Tens 60 segundos. Desculpa número um…" | cronómetro no portátil | cronómetro e contagem |
| Quanto pago por mês em **IA** 🇵🇹 | "Vou mostrar-te exatamente quanto pago em IA por mês. Mas o número que interessa só aparece no fim. Começo pela mais cara." | contador a subir, a amarelo | contador até ao total |
| Como pôr o Claude a responder aos teus **emails** / (segue este protocolo) | "Isto é o que eu fiz para deixar de responder a emails. Mas só funciona se fizeres o passo dois. Passo um…" | caixa de entrada aberta | passos numerados |
| Aposto que usas mal o **ChatGPT** | "Faz este teste. São três perguntas. Se falhares uma, estás a perder tempo todos os dias. Primeira…" | cartão com a pergunta 1 | o teste |
| pov: tens uma IA a trabalhar **enquanto dormes** | "Isto foi feito às três da manhã. Mas ninguém estava acordado. Aqui está o que ela fez esta noite." | ecrã com as tarefas e as horas | lista das tarefas |

**Maus:**

| Ecrã e fala | Porque falha |
|---|---|
| "Dicas de IA para empresas" · "Olá, eu sou o [nome] e hoje trago-vos 3 dicas…" | apresentação, "dicas", nada concreto; perde a pessoa antes do segundo 3 |
| "Como usar a IA" · "A inteligência artificial está a mudar o mundo dos negócios." | vago; a frase podia ser de qualquer pessoa |
| "A [nome da empresa] automatizou 80% dos processos" · "Na [nome da empresa], automatizámos…" | protagonista que ninguém conhece |
| "Não tens uma empresa, tens um emprego" · "E a culpa é tua." | insulto sem prova, "não é X, é Y", tom de guru |
| "5 automações para PME" · "A primeira é os emails, a segunda as faturas, a terceira…" tudo nos primeiros 6 segundos | entrega a lista de rajada; não sobra motivo para ficar |
| "Poupa 10 horas por semana" · "Com este método revolucionário…" | soa a anúncio; "revolucionário" é palavra vazia |

## 13. O que ainda não se sabe

Estas regras vêm de três fontes: os números dos testes que deram origem a este método (114 reels de uma conta, quase todos só com texto), 36 reels de referência escolhidos a dedo (só com likes e comentários, de contas maiores e noutras línguas) e o feedback direto do dono dessa conta. Para este formato, as referências pesam mais, porque há poucos dados próprios de vídeos falados. Na tua conta, os ciclos de 14 dias vão confirmando ou corrigindo. Apostas por confirmar:

- **A fala repete o título ou diz outra coisa?** Nas referências repete. Uma pesquisa em vídeos do Hormozi mostra o contrário: o ecrã diz a dor, a fala dá o contexto. Testar as duas.
- **Título 3 a 5 segundos ou o vídeo todo.**
- **Com ou sem parêntese.**
- **Negativo com teste ou positivo**, para o mesmo tema.
- **Bandeira no fim ou no início.**
- **Duração:** as referências com mais likes têm 50 a 95 segundos, mas o tempo médio de visualização dos reels antigos da conta de exemplo era 5,4 segundos.

Um aviso sobre como ler resultados: o mesmo hook já fez 1 387 views numa publicação e 31 noutra. **Um hook só se julga depois de sair pelo menos 3 vezes.**

Quando houver dados novos, este documento é atualizado: o que ganhar passa a regra, o que perder sai.
