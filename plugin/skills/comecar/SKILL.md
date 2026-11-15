---
name: comecar
description: Onboarding da Fábrica de Reels. Instala tudo, liga a Zernio e a Google Drive, estuda o perfil de Instagram da pessoa, aprova temas, pede B-rolls e músicas, define a estética dos documentos, cria os primeiros recursos grátis com automação de DM, valida legendas e vídeos de ensaio e liga o piloto automático. Usar quando a pessoa escreve "/comecar", "/recomecar", "começar", "configurar a fábrica de reels", "fazer o onboarding", ou quando outra skill do plugin não encontra a pasta de trabalho (~/.fabrica-de-reels/pasta.txt). Retoma onde ficou se já foi começado.
---

# /comecar — onboarding da Fábrica de Reels

Vais pôr a fábrica de trial reels a funcionar para esta pessoa, do zero até "amanhã começamos a publicar". Português de Portugal, frases curtas, tom de colega. **Faz sozinho tudo o que der para fazer sozinho; pergunta só o que depende dela** (logins, chaves, aprovações, gravar). Usa a ferramenta AskUserQuestion para as escolhas, com a opção recomendada em primeiro lugar.

## Onde está cada coisa

- **Motor do plugin:** `<pasta desta skill>/../../motor` (a mensagem que carregou esta skill diz a "Base directory"). Tem os scripts e os guias.
- **Pasta de trabalho da pessoa:** criada no passo 1; o caminho fica em `~/.fabrica-de-reels/pasta.txt`. Tudo o que é dela vive lá: `.env` (privado), banco de textos, recursos, vídeos, históricos.
- Em todos os comandos, a partir do passo 2:
```bash
P="$(cat ~/.fabrica-de-reels/pasta.txt)"; cd "$P"
PY=.venv/bin/python; [ -f .venv/Scripts/python.exe ] && PY=.venv/Scripts/python.exe
export PYTHONUTF8=1
```
- **Estado do onboarding:** `$P/onboarding/estado.json` (`{"passo_feito": [..], "notas": {...}}`). Atualiza-o no fim de cada passo. **Se já existir, retoma no primeiro passo por fazer** e diz em 1 linha o que já está feito. "/recomecar" = retomar (nunca apagar nada).
- **Escrever no `.env`:** edita a linha `CHAVE=valor` (Edit ou um `sed`/Python curto). **Nunca mostres a chave da Zernio no chat**, nem a repitas.

Lê antes de começar (do motor): `hooks/como-escrever-hooks-texto.md`, `legendas/como-escrever-legendas.md`, `ctas/como-construir-cta.md`, `recursos/README.md`, `publicacao/regras.md`, `fabrica/README.md`. São as regras que fazem os vídeos funcionar. Lê-os à medida que precisas, não todos de uma vez.

## 0. Boas-vindas (1 mensagem)

Explica em 5-6 linhas: o que são trial reels (reels que o Instagram mostra só a quem não te segue, para testar sem estragar o perfil), o que a fábrica faz (todos os dias publica reels de texto sobre B-rolls teus; quando gravas um vídeo a falar, edita-o e publica-o; cada reel oferece um recurso grátis por DM a quem comenta uma palavra; de 14 em 14 dias analisa e melhora sozinha). Diz quanto tempo demora (~45-60 min, dá para parar e retomar com /comecar) e o que vai ser preciso:
- conta de Instagram **profissional** (criador ou empresa);
- conta na **Zernio** (zernio.com) — é ela que publica e responde aos comentários;
- **Google Drive** ligada ao Claude (claude.ai → Definições → Conectores → Google Drive);
- 10 ou mais **B-rolls** (vídeos curtos teus, sem falar) e 3-4 **músicas** sem direitos;
- computador ligado de manhã (Mac ou Windows).

## 1. Pasta de trabalho

AskUserQuestion: onde fica a pasta. Recomendado: `~/FabricaDeReels` (Mac e Windows). No Mac **evita a Secretária e os Documentos** (o macOS bloqueia as tarefas automáticas nessas pastas). Outras opções: "Outra pasta (diz-me qual)".

## 2. Instalar (em segundo plano)

Descobre o Python do sistema (`python3`, ou no Windows `py -3.12` / `python`). Se não houver nenhum: Mac → `brew install python@3.12` (se não houver Homebrew, manda instalar de https://brew.sh); Windows → `winget install --id Python.Python.3.12 -e`. Depois corre **em segundo plano** (demora 5-15 min e descarrega ~3 GB):
```bash
python3 "<motor>/ferramentas/instalar.py" "<pasta escolhida>"
```
Enquanto corre, segue para o passo 3. No fim lê a linha `ESTADO {...}`: cada passo tem de estar `ok`. Se faltar o ffmpeg ou o Python, mostra a dica que o instalador deu e ajuda a resolver; depois volta a correr o instalador (é seguro repetir).

## 3. Quem és

Pergunta (texto livre, numa só mensagem): nome como queres que apareça nos documentos, @ do Instagram, se a conta é verificada, e em 2 frases o que fazes e para quem. Grava `NOME_PESSOA`, `INSTAGRAM_CONTA`, `INSTAGRAM_VERIFICADA`, `CTA_INSTAGRAM_LINK=https://instagram.com/<conta>`.

## 4. Zernio

Passo a passo (numerado, curto):
1. Cria conta em https://zernio.com e escolhe um plano que inclua Instagram e automações de comentários.
2. **Connect account → Instagram**: faz login com o Facebook/Instagram da conta profissional e dá todas as permissões pedidas.
3. **Settings → API Keys → Create key**. Copia a chave e cola-a aqui.
Grava `ZERNIO_API_KEY`. Testa: `$PY ferramentas/zernio_posts.py contas` → encontra a linha `instagram <conta>` e grava `ZERNIO_ACCOUNT_ID`. Se a conta não aparecer, a ligação do Instagram na Zernio falhou: pede para repetir o passo 2. Confirma também que as automações respondem: `$PY ferramentas/zernio.py listar @<conta>`.

## 5. Estudar o perfil e aprovar temas

Faz tu a pesquisa, sem perguntar:
- `$PY metricas/recolher.py perfil` (seguidores e totais de 30 dias) e `$PY metricas/recolher.py publicacoes` (últimas 50 publicações com legenda e números, em `metricas/perfil/publicacoes.json`; a Zernio pode demorar uns minutos a sincronizar uma conta acabada de ligar — se vier vazio, espera 2-3 min e repete). Copia `metricas/perfil/<hoje>.json` para `metricas/perfil/linha-de-base.json` (é a fotografia de partida).
- Lê as legendas dos posts com mais alcance; WebSearch pelo nome e pelo @ (site, LinkedIn, entrevistas).
- Escreve `onboarding/perfil.md`: quem é, para quem fala, temas que já resultam (com números), tom, o que a diferencia.

Mostra em ~10 linhas o que percebeste e propõe **6 a 10 temas** para os trial reels: cada um com 1 linha (porquê, para quem) e 1 exemplo de hook. Os trial reels são para **não seguidores**: temas largos o suficiente para atrair gente nova, mas ligados ao que ela vende/faz. AskUserQuestion multiSelect com os temas (até 4 por pergunta; faz 2-3 perguntas se precisares) + convida a acrescentar os dela em "Other". Escreve `banco/pesquisa-temas.md` com os temas aprovados (secção A: aprovados, B: ângulos e exemplos, C: ideias de recursos por tema). Grava em `HOOK_PALAVRAS_PROIBIDAS` palavras que ela não quer nos hooks (pergunta: o nome da empresa, por ex.).

## 6. Google Drive

1. Confirma que a ligação existe: ToolSearch `select:mcp__claude_ai_Google_Drive__create_file,mcp__claude_ai_Google_Drive__share_file,mcp__claude_ai_Google_Drive__search_files`. Se não vier: pede para ligar em claude.ai → Definições → Conectores → **Google Drive**, e depois reiniciar o Claude Code e escrever /comecar (retoma aqui).
2. AskUserQuestion: onde criar a pasta "Fábrica de Reels" — "Na raiz da minha Drive (recomendado)" / "Dentro de uma pasta que vou indicar". Se indicar, encontra-a com `search_files` (`title contains '...' and mimeType = 'application/vnd.google-apps.folder'`).
3. Cria (create_file com `contentMimeType: application/vnd.google-apps.folder`): `Fábrica de Reels` e lá dentro `1. RAW (vídeos a falar)`, `2. PUBLICADOS`, `3. B-rolls`, `4. Músicas`, `5. Recursos`.
4. Partilha **por link, só leitura** (share_file com `permissionId: "anyoneWithLink"`, `role: "reader"`) as pastas **RAW, B-rolls e Músicas**. Explica numa frase porquê: é assim que o computador as lê sozinho, sem chaves; só quem tiver o link (impossível de adivinhar) consegue ver, e são vídeos que vão ser publicados na mesma. A pasta "Fábrica de Reels", a PUBLICADOS e a Recursos não se partilham (os PDFs de recursos partilham-se um a um).
5. Grava os ids: `DRIVE_PASTA_RAIZ`, `DRIVE_PASTA_TALKING_HEAD_RAW`, `DRIVE_PASTA_TALKING_HEAD_PUBLICADOS`, `DRIVE_PASTA_BROLLS`, `DRIVE_PASTA_MUSICAS`, `DRIVE_PASTA_RECURSOS`.
6. Testa: `$PY ferramentas/drive_publico.py listar <id da pasta B-rolls>` tem de responder `[]` sem erro.
7. Telemóvel: diz-lhe para instalar a app **Google Drive** e, para mandar um vídeo: Galeria → Partilhar → Drive → escolher a pasta.

## 7. B-rolls

Explica: B-roll = vídeo curto **teu**, sem falar, 5 a 20 s, vertical, de coisas do teu dia a dia de trabalho. É o fundo dos reels de texto. Lê `referencias/brolls.md` e manda a lista de sugestões **adaptada aos temas e à profissão dela** (10-15 ideias concretas, com o enquadramento). Pede para gravar/escolher e carregar na pasta `3. B-rolls`.

AskUserQuestion: "Já carregaste os B-rolls?" — "Sim, já estão na pasta" / "Faço isso depois, segue" / "Tenho dúvidas". Quando disser que sim: `$PY videos/sincronizar.py` e `$PY videos/cortar.py`, e conta quantos há (`videos/registo.json`). **Menos de 10:** diz quantos faltam e de que tipo (manda de novo as sugestões que faltam) — a fábrica liga mesmo assim, mas avisa que com poucos B-rolls os reels repetem fundo. Vê 3-4 miniaturas (`videos/miniaturas/`) e preenche `tipo` e `notas` no registo.

## 8. Músicas

Pede 3 a 4 músicas **sem direitos de autor** (ex.: Biblioteca de áudio do YouTube, Pixabay Music), calmas, sem voz, em MP3, na pasta `4. Músicas`. Vão a 8% de volume, só para não haver silêncio. Depois: `$PY videos/sincronizar.py` e confirma `audios/registo.json`.

## 9. Estética dos documentos

Explica: **os hooks dos vídeos têm sempre o mesmo estilo** (Montserrat, branco com contorno, destaque amarelo/laranja/azul pelo fundo) porque é o que funciona e não se mexe. A estética que vais escolher agora é a dos **documentos**: os recursos grátis em PDF e os relatórios.

AskUserQuestion: "Já tens uma estética definida (cores e tipos de letra)?" — "Sim, tenho cores e letras" / "Tenho um site, vai lá buscar" / "Não, sugere-me". Se tiver: pede a cor principal, a secundária (clara) e as letras (títulos e texto; têm de existir no Google Fonts, senão escolhe a mais parecida e diz qual). Se tiver site: WebFetch e tira as cores/letras do CSS. Se não: propõe 2-3 combinações ligadas ao tema dela. Grava `MARCA_COR_PRINCIPAL`, `MARCA_COR_SECUNDARIA`, `MARCA_LETRA_TITULOS`, `MARCA_LETRA_TEXTO`.

Pergunta também (texto livre, tudo opcional) os links para a última página dos recursos: comunidade (nome + link), site, link para marcar conversa. Grava `CTA_*`.

## 10. Os primeiros recursos (3)

Propõe 3 recursos grátis (1 por tema aprovado, os mais fortes), cada um com título, o que entrega em 3-5 páginas, e a palavra do CTA (regras de `ctas/como-construir-cta.md`: rara, ≥4 letras, sem acentos). AskUserQuestion para aprovar/trocar. Depois, para cada um, segue a skill **fabrica-de-reels:novo-recurso** a partir do passo 3 (palavra, PDF com `ferramentas/recurso_pdf.py`, revisão das prévias, Drive, automação na Zernio, 12 textos para o banco). Ficam todos `ativo: true`. No fim tens ≥36 textos no banco.

## 11. Validar com a pessoa

1. **Legendas:** mostra 3 pares hook + legenda do banco (de recursos diferentes). Pergunta se o tom é o dela; corrige o que disser e aplica a correção a todo o banco (e regista em `onboarding/perfil.md` → "Tom", para as próximas).
2. **Vídeos de ensaio:** se houver B-rolls cortados e músicas, gera 2-3: `$PY fabrica/gerar_reel.py um --ensaio --texto <id> --n 9N` (N = 1, 2, 3). Tira 3 frames de cada (`ffmpeg -ss 1 / 3 / 5 -frames:v 1`) e mostra-os com o Read; diz onde está o MP4 para ela abrir. Pergunta se está bem.
3. **Talking heads:** explica como gravar (vertical, espaço livre por cima da cabeça para o texto e as imagens, falar direto para a câmara, pode enganar-se e repetir — o Claude corta) e como enviar (Drive → `1. RAW`). Se no vídeo prometer um recurso ("comenta X"), o Claude cria-o.

## 12. Piloto automático

Explica em 4 linhas e pede autorização explícita com AskUserQuestion:
- **Fábrica diária** (sem IA): às 06:00 descarrega B-rolls novos, recolhe números e agenda os reels do dia como trial reels, só entre `HORA_INICIO` e `HORA_FIM`.
- **Vigia da RAW** e **análise de 14 dias** (com o Claude): quando aparece um vídeo na RAW, o Claude edita-o e publica-o sozinho; de 14 em 14 dias analisa os números e melhora o banco. Para isso o Claude corre **sem pedir autorização a cada passo** (`--dangerously-skip-permissions`), dentro da pasta de trabalho. Usa o plano Claude da pessoa.
Opções: "Ligar tudo (recomendado)" / "Só a fábrica diária, sem o Claude sozinho" / "Ainda não".
- Tudo → `FABRICA_LIGADA=sim`, `AUTOMATICO_CLAUDE=sim`. Só fábrica → `FABRICA_LIGADA=sim`, `AUTOMATICO_CLAUDE=nao`.
- Depois: `$PY ferramentas/agendar.py ligar` e `$PY ferramentas/agendar.py estado` (as 3 a `true`). No Windows, se o schtasks falhar, mostra o erro e sugere abrir o Claude Code como administrador só para este passo.
Lembra: o computador tem de estar ligado (pode estar a dormir; corre ao acordar) e com sessão iniciada.

## 13. Fecho

Agenda um primeiro teste já: `$PY fabrica/gerar_reel.py dia --ensaio` (mostra os horários e textos que sairiam). Escreve `onboarding/resumo.md` (o que ficou configurado, temas, recursos e palavras, B-rolls, o que falta). Marca o onboarding como feito no `estado.json`.

Mensagem final, curta: "Está pronto. Amanhã às <HORA_INICIO> sai o primeiro reel." + o que ela faz daqui para a frente (gravar B-rolls quando puder, mandar talking heads para a RAW, escrever /reels para ver o estado, /fabrica-de-reels:novo-recurso para um recurso novo) + o que ainda falta, se faltar alguma coisa (B-rolls, músicas, links de CTA).
