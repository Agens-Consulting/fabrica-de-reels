# Como construir um CTA

Serve para os dois tipos de reel: só com texto e com o dono da conta a falar para a câmara.

Nos comandos, `$PY` é o Python do `.venv` da tua pasta de trabalho (`.venv/bin/python` no Mac, `.venv\Scripts\python.exe` no Windows). A conta e a chave do Zernio vêm do `.env` (`INSTAGRAM_CONTA`, `ZERNIO_API_KEY`).

Neste projeto, **o CTA é a palavra** que a pessoa comenta para receber um recurso. Quando alguém a comenta, uma automação do Zernio manda-lhe uma DM com o recurso e responde ao comentário em público. O ManyChat já não se usa.

O processo tem duas partes. Primeiro escolhe-se o recurso e a palavra, e cria-se a automação. Depois escreve-se a frase que pede o comentário.

---

## Parte 1: recurso, palavra e automação

Começa-se sempre pelo recurso, nunca pela palavra.

### Passo 1. Escolher o recurso

Abre a lista de recursos em [../recursos/lista.md](../recursos/lista.md) e escolhe o que a pessoa vai receber.

**Nunca há mais de 5 recursos ativos ao mesmo tempo.** Se já há 5, escolhe-se um deles. Só entra um recurso novo quando sai um, no fim de cada ciclo de 14 dias (ver [../recursos/README.md](../recursos/README.md)).

O recurso tem de ser a continuação natural do reel:
- Se o hook promete "7 prompts", o recurso são os 7 prompts, ou mais prompts do mesmo género.
- Se o vídeo mostra como responder a emails com o Claude, o recurso é o guia ou o modelo desse processo.

Se nenhum recurso da lista serve e há lugar, cria-se um novo:
- o ficheiro (PDF, modelo, prompt) ou o link fica na pasta `../recursos/PALAVRA/`, com `link.txt` e `ficha.md`;
- acrescenta-se à lista antes de avançar.

Nada vai para a DM sem estar primeiro na pasta de recursos.

### Passo 2. O recurso já tem palavra?

**Sim:** reaproveita-se essa palavra. Não se cria automação nova, porque a que existe já dispara em qualquer publicação da conta. Salta para a parte 2.

**Não:** escolhe-se uma palavra nova (passo 3).

### Passo 3. Escolher uma palavra nova

A palavra tem de cumprir quatro regras. Se falhar uma, volta-se ao início do passo 3 e escolhe-se outra.

1. **Única.** Não pode estar a ser usada noutra automação de nenhuma conta ligada à tua chave do Zernio (se geres várias contas, vale para todas). Só se repete noutra conta se entregar exatamente o mesmo recurso (o script pede então `--mesmo-recurso`).
2. **Rara.** A automação vale para a conta inteira: dispara em qualquer comentário de qualquer publicação que tenha a palavra. Uma palavra que as pessoas escrevem por acaso ("IA", "quero", "top", "obrigado") dispara sem parar. O script recusa estas palavras:
   - qualquer palavra com menos de 4 letras;
   - as palavras da lista COMUNS (ver nota abaixo).
3. **Ligada ao recurso.** Quem lê a palavra percebe o que vai receber, ou fica curioso. ICEBERG, BLUEPRINT e ROADMAP funcionam. XPTO2 não funciona.
4. **Fácil de escrever no telemóvel.** Uma palavra só, sem números se possível, sem hífens. Acentos são aceites porque a automação tolera erros de escrita, mas na dúvida usar a versão sem acento.

**Nota sobre a lista COMUNS:** algumas palavras que parecem óbvias para reels de IA estão nela e não podem ser usadas. Exemplos: PROMPT, PROMPTS, CLAUDE, CHATGPT, TAREFAS, GUIA, VIDEO, AGENTE, AUTOMAÇÃO, LISTA, PLANO, MODELO. A lista completa está em `ferramentas/zernio.py`, na variável `COMUNS`.

Como fugir delas sem perder a ligação ao tema:

| Em vez de | Usar, por exemplo |
|---|---|
| PROMPTS | PROMPTEIRO, CABULA, RECEITAS |
| TAREFAS | DELEGAR, PILOTO |
| CLAUDE | CLAUDINHO, MANUALCLAUDE |
| GUIA | MAPA, ATALHO |

### Passo 4. Confirmar que a palavra está livre

Antes de criar, confirma-se nas automações ativas de todas as contas da tua chave do Zernio:

```bash
$PY ferramentas/zernio.py mapa
```

Este comando atualiza `ctas/automacoes-mapa.md` com todas as palavras em uso. Se a palavra lá estiver, volta-se ao passo 3.

Não é preciso confiar só nesta verificação manual: o script de criação também recusa palavras repetidas ou comuns.

### Passo 5. Criar a automação no Zernio

Regra: **nada se promete que não exista, e tudo o que se promete sai sozinho**.

**Antes da automação, o recurso tem de ter link público.** O PDF está em `../recursos/PALAVRA/`, foi carregado pelo Claude para a pasta de recursos da Drive (`DRIVE_PASTA_RECURSOS`), com o conector "Google Drive" do Claude, e partilhado como "qualquer pessoa com o link pode ver" (ver "Do ficheiro à DM" em `../recursos/README.md`). Se a partilha falhar, não se cria a automação.

**Como funciona por baixo:** a automação é uma regra comentário → DM do próprio Zernio (`POST /v1/comment-automations`). Corre nos servidores do Zernio, por isso dispara mesmo com o teu computador desligado. Os trial reels saem na conta **@<INSTAGRAM_CONTA>** (do `.env`), ligada à chave `ZERNIO_API_KEY`.

```bash
$PY ferramentas/zernio.py criar @<INSTAGRAM_CONTA> \
  --palavra PALAVRA \
  --dm "<1 a 2 frases na voz do dono da conta, a entregar o recurso>" \
  --botao-texto "<máx. 20 caracteres>" \
  --botao-link <link público da Drive> \
  --nome "PALAVRA · [recurso] (trial reels DD/MM)" \
  --ref "trial reels 2.0" \
  --ensaio
```

- **Primeiro corre-se com `--ensaio`** e lê-se o pedido que o script mostra. Se estiver bem, corre-se outra vez sem `--ensaio`.
- **Conta inteira, sem `--post-id`.** A automação dispara em qualquer publicação da conta onde comentem a palavra, e também se alguém mandar a palavra por DM. É o que se quer nos trial reels: a mesma palavra serve vários reels e as variações do mesmo vídeo. (Com `--post-id` ficaria presa a um só post agendado; com `--platform-post-id`, a um post já publicado. Só uma regra por post.)
- **A DM:** 1 a 2 frases na voz do dono da conta, na primeira pessoa, máximo 640 caracteres com botão. Exemplo: "Aqui tens a cábula com os 7 prompts. Diz-me qual usaste primeiro 👇"
- **O botão:** até 20 caracteres ("Abrir a cábula"). Os cliques no botão contam-se sozinhos.
- **A resposta pública ao comentário vai sempre**, posta pelo script: 40 segundos depois da DM, com uma de seis frases a rodar ("Enviado 📩…", "Feito: está nas tuas mensagens"). Comentários sem resposta tiram engagement (regra de base).
- **O script recusa** palavras com menos de 4 letras, palavras comuns e palavras já usadas. Nesse caso, volta-se ao passo 3 e corrige-se o CTA.
- **Registo:** cada criação fica em `ctas/automacoes-instagram.jsonc`; o mapa de todas as contas atualiza-se com `zernio.py mapa`.

**Alternativa sem terminal:** a automação também se pode criar à mão no painel do Zernio. Mas o script é o caminho por defeito, porque valida a palavra e regista.

**Mudar ou retirar uma automação:** não se edita; apaga-se e cria-se de novo.

```bash
$PY ferramentas/zernio.py listar @<INSTAGRAM_CONTA>     # ver ids
$PY ferramentas/zernio.py apagar @<INSTAGRAM_CONTA> <id>
```

Um recurso que sai na rotação dos 5 fica com a automação ligada mais 30 dias antes de ser apagado (ver `../recursos/README.md`).

No fim, atualiza-se [../recursos/lista.md](../recursos/lista.md) e a `ficha.md` do recurso: palavra, id da automação, DM usada e data de entrada.

**Nunca se publica um reel com "Comenta PALAVRA" sem a automação já estar ativa.** Quem comenta e não recebe nada não volta.

---

## Parte 2: a frase que pede o comentário

Como esta frase encaixa no resto da legenda está em [../legendas/como-escrever-legendas.md](../legendas/como-escrever-legendas.md).

A forma base é:

> **Se queres [o recurso, dito pelo que dá à pessoa], comenta PALAVRA.**

Exemplos:
- "Se queres os 7 prompts prontos a copiar, comenta CABULA."
- "Se queres o guia para pôr o Claude a responder aos teus emails, comenta ATALHO."
- "Se queres o modelo de proposta que uso, comenta BLUEPRINT."

### Regras da frase

- **O recurso diz-se pelo que dá, não pelo formato.** "Os 7 prompts prontos a copiar" e não "o PDF". "O passo a passo para responder a emails em 10 minutos" e não "o guia".
- **A palavra vai em MAIÚSCULAS.** Destaca-se na legenda e ninguém tem dúvidas sobre o que escrever.
- **Uma só palavra e um só pedido por reel.** Nunca "comenta X ou segue para Y".
- **O "se queres" vem antes do "comenta".** Primeiro a pessoa sabe o que ganha, depois o que tem de fazer.
- **Nunca "link na bio".** O pedido é sempre um comentário.

### Onde vai, conforme o tipo de reel

**Só texto no ecrã** (o valor está na legenda):
- A frase vai **no fim da legenda**, depois de entregar o valor.
- Quando se põe no início, os guardados caem para metade (visto em análises anteriores).
- O recurso tem de ser **mais** do que a legenda já deu: mais prompts, a versão completa, o modelo editável. Se a legenda já entregou tudo, não há razão para comentar.

**O dono da conta a falar** (o valor está no vídeo):
- Quem fala **diz a frase no fim do vídeo**, nos últimos 3 a 5 segundos.
- A mesma frase **repete-se no fim da legenda**, por escrito.
- Pode ser mencionada a meio quando é natural, como num reel de referência em que a palavra ("ouro") foi dita a meio e teve 690 comentários. Mas nunca nos primeiros 3 segundos: aí o lugar é do hook.

---

## Resumo

1. Escolher o recurso na lista de recursos (no máximo 5 ativos; o ficheiro ou link tem de estar na pasta `recursos/`).
2. Se o recurso já tem palavra, usá-la e saltar para o passo 6.
3. Se não tem, escolher uma palavra nova, rara, única e ligada ao recurso.
4. Confirmar no mapa que está livre; se não estiver, voltar ao passo 3.
5. Criar a automação no Zernio (primeiro com `--ensaio`) e atualizar a lista de recursos.
6. Escrever "Se queres [recurso], comenta PALAVRA" e pô-la no sítio certo para o tipo de reel.
