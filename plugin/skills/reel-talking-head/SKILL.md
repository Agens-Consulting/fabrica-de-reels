---
name: reel-talking-head
description: Edita e publica os trial reels em que a pessoa fala para a câmara (gravados com espaço por cima da cabeça). Pega no vídeo bruto da pasta RAW da Drive, corta retakes e silêncios, põe zoom alternado, limpa e sobe o som, junta música baixinha, escreve 2 a 3 hooks, mete uma imagem grátis por frase acima da cabeça, legendas simples de 3 palavras, escreve a legenda do post com o recurso certo e publica como trial reel na Zernio. Usar quando chega um vídeo novo à RAW, quando a tarefa automática chama ("trata o vídeo novo da pasta RAW"), ou quando a pessoa diz "edita este talking head", "faz o reel deste vídeo", "publica o vídeo que pus na Drive". Não é para os reels só de texto (a fábrica diária).
---

# Reel talking head (tipo B): do bruto ao publicado

Trabalha na pasta de trabalho da pessoa, em `talking-head/`. Tudo o que é pessoal (chave da Zernio, conta, pastas da Drive, horários) vem do `.env` da raiz da pasta de trabalho.

Os guias editoriais são os mesmos dos Reels de Teste e estão uma pasta acima. São eles que decidem o texto:

| Para | Lê |
|---|---|
| Hook no ecrã | `../hooks/como-escrever-hooks-fala.md` (tipo B) e `../hooks/como-escrever-hooks-texto.md` (secções "Cortar palavras", "Voz e tom", "A bandeira") |
| Aspeto do hook | `../hooks/estetica-e-posicionamento.md` (o script já o aplica) |
| Legenda do post | `../legendas/como-escrever-legendas.md`, **tipo B** |
| Recurso e palavra | `../recursos/README.md`, `../recursos/lista.md`, `../banco/recursos.json`, `../ctas/como-construir-cta.md` |

Lê-os antes do primeiro vídeo de cada sessão. Não repitas aqui o que lá está.

## Regras de edição (fixas)

- **Sem aprovação.** O vídeo entra na RAW e sai publicado. Os ficheiros ficam em `talking-head/publicados/<slug>/`; o bruto passa para a PUBLICADOS da Drive na próxima conversa (passo 10).
- **Cortes:** saem as frases repetidas (fica o **último** take bom), as mal ditas e as mal acabadas, os falsos arranques e as hesitações ("hmm", "pronto", "tipo" soltos). Saem também todos os silêncios: as pausas acima de ~0,15 s cortam-se. Não se corta o fim das palavras e não ficam espaços em branco. Isto está no script, que usa a energia do áudio.
- **Zoom alternado 100% / 108%** em cada corte (script).
- **Som:** redução de ruído leve e depois **sempre +15% de volume**, porque um vídeo mais alto pára o scroll. Fica perto de −13 LUFS, com limitador. A música de fundo vai a **8%**, escolhida das músicas da Drive (`audios/raw/`, script).
- **Hook no topo** durante 5 a 6 s, com o estilo fixo. Depois disso entram as **imagens**.
- **Imagens:** **uma por frase** (muda quando a pessoa muda de frase, não nos cortes dentro da mesma frase). Ficam acima da cabeça, planas, sem cantos arredondados nem efeitos, nem muito grandes nem muito pequenas. Têm de ser impactantes e ligadas ao tema. **Custo zero:** Pixabay, Openverse e Wikimedia Commons.
- **Legendas no vídeo:** Montserrat branca com contorno preto, **3 palavras de cada vez** (menos se as palavras forem grandes), sem itálico nem efeitos, na posição habitual das legendas (80% da altura). Têm de parecer feitas por uma pessoa.
- **2 a 3 variações** por vídeo, só com o hook diferente (e a legenda do post também diferente).
- **Enquadramento mau** (pouco espaço por cima da cabeça): edita-se na mesma, sem alarido.
- **Recurso:** se a pessoa fala de um recurso no vídeo, tem de existir e ser entregue. Se não fala, a legenda oferece um dos recursos ativos que mais tenha a ver com o tema.

## Fluxo

```bash
P="$(cat ~/.reels-de-teste/pasta.txt)"; cd "$P/talking-head"
PY=../.venv/bin/python; [ -f ../.venv/Scripts/python.exe ] && PY=../.venv/Scripts/python.exe
export PYTHONUTF8=1
```
Os guias estão uma pasta acima (`../hooks`, `../legendas`, `../recursos`, `../ctas`, `../banco`). Lê também `../onboarding/perfil.md` (tom e público).

### 1. Entrada
- `$PY scripts/th.py novos` lista os vídeos da RAW ainda por tratar.
- `$PY scripts/th.py baixar <drive_id>` descarrega o vídeo (a RAW está partilhada por link, não precisa de chaves) e devolve o **slug** (`trabalho/<slug>/`).
- Vídeo local, sem Drive: cria `trabalho/<slug>/raw.<ext>` à mão e segue.

### 2. Preparar
`$PY scripts/th.py preparar <slug>` põe o vídeo em 1080x1920 a 30 fps e transcreve palavra a palavra com o Whisper `medium` (pt). O modelo `small` é só para testes. O resultado fica em `transcricao.txt` (`índice:palavra`, com as pausas marcadas `⏸`) e em `palavras.json`.

### 3. O plano (és tu que decides)
Lê o `transcricao.txt` inteiro e escreve `trabalho/<slug>/plano.json`:

```json
{
 "manter": [[0, 41], [57, 130]],
 "correcoes": {"9": "Claude", "1": "vou-te", "2": ""},
 "frases": [
  {"de": 0, "ate": 12, "pesquisa": ["empty office desk night", "tired business owner"]},
  {"de": 13, "ate": 27, "pesquisa": ["overflowing email inbox"]}
 ],
 "hook_dur": 5.5,
 "recurso": "CABULA",
 "hooks": [
  {"molde": "lista", "linhas": ["3 COISAS QUE O", "CLAUDE FAZ NA", "TUA EMPRESA"], "destaque": ["CLAUDE"], "legenda": "…"},
  {"molde": "pov", "linhas": ["…"], "destaque": ["…"], "legenda": "…"}
 ]
}
```

- **`manter`**: intervalos de índices de palavras (inclusivos) que ficam, por ordem. Tudo o resto sai.
  - Repetição: compara as várias tentativas da mesma frase e fica a última completa e bem dita. Se a última for pior (gaguejada, cortada), fica a melhor.
  - Corta frases interrompidas ("A primeira é..." seguido de "A primeira é responder…"), muletas soltas e conversa fora do conteúdo ("espera", "outra vez", "corta").
  - O vídeo tem de fazer sentido de seguida. Lê o texto que fica como se fosse um guião, de uma ponta à outra.
  - O pedido final ("comenta PALAVRA") fica sempre, se a pessoa o disse.
- **`correcoes`**: o texto das legendas é o do Whisper. Corrige nomes ("clode" → "Claude"), palavras com hífen que o Whisper parte ("vou" + "te" → "vou-te" no primeiro índice e `""` no segundo) e erros óbvios. `""` esconde a palavra só na legenda; o corte não muda.
- **`frases`**: blocos de **frase dita**, cada um com `de` e `ate` em índices mantidos e em ordem, e a cobrir todo o vídeo. Cada bloco recebe uma imagem.
  - Frases muito curtas (menos de ~1,5 s) juntam-se à seguinte, para as imagens não piscarem.
  - As frases que acabam durante o hook (os primeiros 5-6 s) não precisam de `pesquisa`.
  - `pesquisa`: 1 a 3 pesquisas **em inglês**, concretas e visuais. Procura o objeto ou a cena, não o conceito: "empty wallet", não "financial loss"; "stack of paper invoices", não "bureaucracy". Para marcas, pessoas e lugares reais vale o nome, porque a Wikimedia tem logótipos e fotos reais.
- **`hook_dur`**: 5 a 6. Se a primeira frase acaba aos 5,8 s, usa 5,8.
- **`hooks`**: 2 ou 3, cada um com um **molde diferente** (lista com número, POV, condição escondida…) para o teste valer.
  - Regras de `como-escrever-hooks-fala.md`: o texto no ecrã é o título do que a pessoa diz. Nunca manda ver a legenda, porque o vídeo é o conteúdo.
  - Máximo 3 linhas, ~18-22 caracteres por linha, em MAIÚSCULAS, com 1 palavra de destaque (2 no máximo).
  - Cortar palavras, nunca as de `HOOK_PALAVRAS_PROIBIDAS`, 🇵🇹 só em alguns (se a conta for portuguesa), POV e listas funcionam.
  - O hook tem de bater com as primeiras frases ditas.
- **`legenda`** (por hook): guia tipo B, 40 a 120 palavras. Abre com o segundo hook (a ideia principal numa frase), depois a lista do vídeo em títulos e no fim "Se queres …, comenta PALAVRA." **Cada variante leva uma legenda diferente**: no mínimo, o segundo hook e a ordem das frases mudam. Nunca a mesma legenda duas vezes.
- **`recurso`**: a palavra (ver passo 4).

### 4. Recurso e palavra
1. **A pessoa diz "comenta X" no vídeo?** Confirma em `../banco/recursos.json`:
   - Se X existe e está ativo, usa-o.
   - Se X existe mas não tem automação, ou se não existe, **cria-o** (passo 5).
   - Se o que disse soa a uma palavra que existe ("cábula" → CABULA), usa a existente.
2. **Fala de um recurso sem palavra** ("deixo-vos o guia", "tenho um ficheiro com isto")? Escolhe uma palavra nova seguindo `../ctas/como-construir-cta.md` (rara, 4+ letras, fora da lista COMUNS) e cria o recurso.
3. **Não fala de recurso nenhum?** Escolhe, dos ativos em `../banco/recursos.json`, o mais ligado ao tema. A legenda faz a ponte e o pedido.

### 5. Criar um recurso (só quando o vídeo o promete)
**Se a pessoa prometeu, cria-se sempre**, mesmo que isso passe os 5 ativos.

**Primeiro, percebe o que prometeu.** Muitas vezes não é um PDF, é um link: "deixo-vos o site", "a ferramenta chama-se X", "o repositório está no GitHub".
- **Recurso que é um link:**
  1. Encontra-o com pesquisa na web e vai sempre à **fonte oficial**: o site da própria ferramenta, a página oficial do GitHub, a documentação. Nunca um agregador, uma cópia, um link de afiliado, um encurtador ou um download direto de um site qualquer.
  2. **Confirma que o link abre e que é o que a pessoa disse**: abre-o com WebFetch e lê a página. Compara o nome, o que faz e o preço (se disse grátis, tem de ser grátis).
  3. Se houver dúvida sobre qual é a coisa certa (dois produtos com o mesmo nome, ou o nome foi dito mal), escolhe o que bate com o contexto do vídeo e escreve o porquê em `notas.md`.
  4. Se não encontrares uma fonte de confiança, **não inventes**. Faz um PDF curto com o que explicou no vídeo e a forma de lá chegar.
  5. Um link sozinho vai direto no botão da DM, com `link.txt` e `ficha.md` na pasta. Se forem vários links (por exemplo "as 5 ferramentas"), faz um PDF com cada uma: o que faz, quando usar e o link oficial.
- **Recurso que é um documento** (guia, prompts, modelo): segue a skill **reels-de-teste:novo-recurso** a partir do passo 3 (palavra, PDF com `ferramentas/recurso_pdf.py`, Drive, automação, registo em `../banco/recursos.json` com `origem: "talking-head"`). Tem de ser a continuação do que a pessoa disse no vídeo. Se isto passar os 5 ativos, cria-o na mesma e deixa nota em `trabalho/<slug>/notas.md`.
- **Em modo automático não há ligação à Drive**, por isso não dá para carregar um PDF novo. Nesse caso: prepara tudo (plano, render, PDF em `../recursos/PALAVRA/`), **não publiques**, marca `"estado": "a espera de recurso"` em `estado.json` para esse drive_id e escreve em `../avisos.txt`: "O vídeo <nome> está pronto mas o recurso PALAVRA precisa de ti: abre o Claude e escreve /reels". Recursos que são só um link não precisam da Drive: esses fazem-se em modo automático.

Nada se publica com um pedido de comentário sem a automação dessa palavra estar ativa.

### 6. Imagens
1. `$PY scripts/th.py imagens <slug>` procura até 9 candidatas por frase e gera `candidatos/folha_NN.jpg`, uma grelha numerada.
2. **Vê cada folha** com o Read e escolhe a mais impactante e ligada à frase. O que conta:
   - uma ideia clara à primeira vista, sem texto pequeno ilegível;
   - nada de banco de imagens genérico (pessoas a apertar mãos, gráficos de setas);
   - nada de marcas d'água, de imagens que contradigam o que se diz, de concorrentes em destaque nem de pessoas reconhecíveis fora de contexto.
3. Põe `"escolha": N` em cada frase do `plano.json`.
4. Se nenhuma serve, muda as `pesquisa` dessa frase e corre `imagens <slug> --refazer`. Se mesmo assim não houver, tira a `pesquisa` e essa frase fica sem imagem.

### 7. Render e verificação
`$PY scripts/th.py render <slug>` gera `saida/vN.mp4`, `vN_capa.jpg`, `vN_legenda.txt` e `vN_verificacao.jpg` (8 frames).

Antes de publicar, confere:
- **Vê cada `vN_verificacao.jpg`:**
  - o hook está legível e dentro da moldura;
  - as imagens estão acima da cabeça e não tapam a cara (se tapam muito, desce `IMG_MAX_H` em `scripts/texto.py` e volta ao render);
  - as legendas não tapam a cara e estão bem escritas.
- **Revê os cortes:** transcreve `saida/v1.mp4` com o Whisper `small` e lê o texto seguido. Não pode haver frases repetidas nem palavras comidas. Mede as pausas com `ffmpeg -af silencedetect=n=-40dB:d=0.2`; não deve sobrar nenhuma acima de 0,2 s.
- **Mede o volume:** `ebur128` deve dar perto de −13 LUFS integrado.
- Se algo falhar, corrige o `plano.json` (ou as constantes no topo de `th.py`) e volta ao render.

### 8. Publicar
`$PY scripts/th.py publicar <slug>` faz três coisas:
- agenda cada variante como **trial reel MANUAL** na Zernio (conta do `.env`). Nunca se promove. A primeira sai daqui a ~30 min e as outras com 3 h entre elas, só entre `HORA_INICIO` e `HORA_FIM` (o que não couber passa para o início do dia seguinte);
- copia as variantes, capas e legendas para `publicados/<slug>/`;
- escreve o `historico.jsonl` (hook, molde, recurso, música, cor de destaque…), que serve para cruzar com as métricas.

Usa `--ensaio` para ver os horários sem publicar.

### 9. Fecho
Escreve em `trabalho/<slug>/notas.md`, em 3 a 5 linhas, o que se cortou, as variantes, o recurso e qualquer coisa estranha.

### 10. Arquivar na Drive (só em conversa)
Se a ligação Google Drive estiver disponível: `$PY scripts/th.py por-arquivar` lista os brutos já publicados que ainda estão na RAW. Para cada um: cria (se não existir) a pasta `<slug>` dentro de `DRIVE_PASTA_TALKING_HEAD_PUBLICADOS`, move o bruto para lá com `mcp__claude_ai_Google_Drive__update_file` (`parentId`), carrega as legendas (`vN_legenda.txt`, como texto) e corre `$PY scripts/th.py arquivado <drive_id>`. Os MP4 editados ficam no disco (a ligação só carrega até 10 MB).

## Automático
A tarefa `vigia` (`ferramentas/agendar.py`) corre `scripts/th.py vigiar` de 15 em 15 minutos, dentro do horário. Se houver um vídeo novo na RAW e `AUTOMATICO_CLAUDE=sim`, chama `claude -p` com esta skill e grava o log em `trabalho/_logs/`. Um trinco impede que dois vídeos se tratem ao mesmo tempo.

## Afinar
As regras numéricas estão no topo de `scripts/th.py`: `GAP_JUNTA`, `PAD_*`, `ZOOMS`, `HOOK_DUR`, `IMG_*`, `VOL_MUSICA`, `GANHO_VOZ`, `PALAVRAS_LEG`, `CHARS_LEG`. As posições estão em `scripts/texto.py`: `CENTRO_LEG`, `IMG_*` e as do hook. Quando a pessoa corrigir alguma coisa, muda a constante na pasta de trabalho e regista o porquê em `../onboarding/perfil.md`.
