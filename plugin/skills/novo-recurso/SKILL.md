---
name: novo-recurso
description: Cria um recurso grátis novo para os trial reels a partir de uma ideia, um link, um vídeo ou um ficheiro, e trata de tudo o que vem com ele - o PDF com a estética da pessoa, a palavra do CTA, a automação de DM na Zernio, a pasta em recursos/ e 12 hooks + legendas para o banco da fábrica. Usar quando a pessoa escreve "/novo-recurso", "cria um recurso sobre…", "novo recurso a partir deste link/vídeo", "tenho uma ideia para um recurso", "faz hooks e legendas sobre isto". Também usada pelo /comecar para os primeiros recursos.
---

# Novo recurso

Entrada: o que vier depois do comando (ideia em texto, link, caminho de um ficheiro, link de um reel). Português de Portugal.

```bash
P="$(cat ~/.fabrica-de-reels/pasta.txt)"; cd "$P"      # se não existir: corre primeiro /fabrica-de-reels:comecar
PY=.venv/bin/python; [ -f .venv/Scripts/python.exe ] && PY=.venv/Scripts/python.exe
export PYTHONUTF8=1
```
Conta, chave da Zernio, pasta dos recursos na Drive, links dos CTAs e estética estão no `.env` (nunca o mostres).

Lê primeiro: `recursos/README.md`, `recursos/lista.md`, `ctas/como-construir-cta.md`, `hooks/como-escrever-hooks-texto.md`, `legendas/como-escrever-legendas.md`, `banco/recursos.json`, `banco/pesquisa-temas.md`, `onboarding/perfil.md` (tom e público).

## 1. Perceber a matéria-prima

- **Ideia em texto:** se for vaga, no máximo 2 perguntas (para quem é, o que a pessoa consegue fazer depois). Se der para avançar, avança.
- **Link:** lê com WebFetch. Se for de outra pessoa, o recurso é **nosso**, escrito de novo e melhor, nunca uma cópia; cita a fonte se usar dados dela.
- **Vídeo ou reel:** transcreve (`yt-dlp` do `.venv` + `whisper` do `.venv`, modelo `small`, `--model_dir ferramentas/modelos-whisper`) e lê frames com o ffmpeg.
- **Ficheiro (PDF, doc):** lê-o.
- Verifica os factos (nomes, comandos, preços, números) nas fontes oficiais. Nada inventado, nada de números pessoais que a pessoa não tenha dado.

## 2. Resumir e confirmar (uma vez só)

Mostra, curto: título, o que entrega em 3-5 páginas (tópicos), a palavra proposta e 3 hooks de exemplo. Os 3 hooks de exemplo já seguem o guia de hooks (versão 2: listas com gancho). Espera o "sim" ou as correções. Depois disto só voltas a perguntar uma vez, para aprovar os 12 hooks (passo 6). (Se vieres do /comecar com o recurso já aprovado, salta este passo.)

## 3. Palavra do CTA

Regras de `ctas/como-construir-cta.md`: rara, ≥ 4 letras, sem acentos nem cedilhas, não comum, nunca usada na conta. Confirma:
```bash
$PY -c "import sys; sys.path.insert(0,'ferramentas'); import zernio as z; print('PALAVRA' in z.COMUNS)"
$PY ferramentas/zernio.py mapa && grep -i PALAVRA ctas/automacoes-mapa.md
```
Se o tema já tiver recurso e palavra, reaproveita.

## 4. O PDF

Escreve `recursos/PALAVRA/spec.json` (formato no topo de `ferramentas/recurso_pdf.py`: capa, 1-3 páginas de conteúdo com valor real — prompts em `code`, passos, tabelas, notas — e a página final de CTAs com os links `CTA_*` do `.env`). Gera e revê:
```bash
$PY ferramentas/recurso_pdf.py recursos/PALAVRA/spec.json --previa
```
Vê **cada** `previa_N.png` com o Read: nada cortado no fundo da página (se transbordar, divide em duas páginas), nada de texto em inglês por engano, CTAs certos. Escreve `recursos/PALAVRA/ficha.md` (o que é, páginas, fontes, data, de onde veio a ideia). O PDF tem de ficar abaixo de 10 MB.

**Recurso que é só um link** (uma ferramenta, um site): vai sempre à fonte oficial, abre-a com WebFetch e confirma que é o que se promete (nome, o que faz, preço). Grava `link.txt` e `ficha.md`; não há PDF.

## 5. Drive e automação

1. Carrega o PDF para a pasta `DRIVE_PASTA_RECURSOS` pela ligação Google Drive do Claude: `mcp__claude_ai_Google_Drive__create_file` com `title: "AAAA_MM_DD_Recurso_PALAVRA.pdf"`, `parentId`, `contentMimeType: application/pdf`, `disableConversionToGoogleType: true` e `base64Content: "sha256:<sha256 do ficheiro>:<caminho absoluto com />"` (calcula o sha256 com `$PY -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" recursos/PALAVRA/recurso.pdf`). Se a ferramenta não estiver carregada, usa ToolSearch `select:mcp__claude_ai_Google_Drive__create_file,mcp__claude_ai_Google_Drive__share_file`. Sem ligação Google Drive (por ex. em modo automático) **não se cria o recurso**: deixa tudo pronto em `recursos/PALAVRA/`, marca `espera: true, falta: "drive"` em `banco/recursos.json` e escreve um aviso em `avisos.txt`.
2. Partilha esse ficheiro por link: `share_file` com `permissionId: "anyoneWithLink"`, `role: "reader"`. O link (`https://drive.google.com/file/d/<id>/view`) vai para `recursos/PALAVRA/link.txt`.
3. Cria a automação (primeiro em ensaio, lê o pedido, depois a sério). A DM tem 1-2 frases na voz da pessoa:
```bash
$PY ferramentas/zernio.py criar @<INSTAGRAM_CONTA> --palavra PALAVRA --dm "…" --botao-texto "…" --botao-link "<link>" --nome "PALAVRA · … (trial reels DD/MM)" --ref "trial reels" --ensaio
```
Se a partilha falhar, não se cria a automação. **Nada se publica a pedir um comentário sem a automação dessa palavra ativa.**

## 6. Os 12 textos para o banco

12 pares hook + legenda para `banco/textos.json` (estrutura em `fabrica/README.md`), seguindo à letra `hooks/como-escrever-hooks-texto.md` (versão 2):
- se `banco/pesquisa-temas.md` ainda não tiver a secção "Tradução para hooks" (secção 4 do guia), escreve-a primeiro e mostra-a à pessoa em 5 linhas;
- **10 a 12 listas, cada uma com um gancho** (exclusividade, contra a intuição, hábito, autoridade, filtro de idade ou papel, momento do ano), com pelo menos 4 ganchos diferentes; **0 a 2 POV**, só com uma afirmação difícil de acreditar e verdadeira; **nenhuma condição** ("…se não fizeres isto"); bandeira 🇵🇹 em 4 se a conta for portuguesa;
- nunca copiar o esqueleto de um exemplo do guia que seja de outro tema; faz o teste da pessoa no sofá (passo 5 da secção 14) e corta os mornos;
- cada texto leva `"molde"`, `"gancho"` e `"guia": 2`;
- antes de gravar, mostra os 12 hooks à pessoa (só os hooks, uma linha cada, com o que está `[CONFIRMAR]`) e pede o "sim": é ela que garante que cada facto é verdade na área dela;
- hooks em MAIÚSCULAS, ≤ 3 linhas de ≤ 22 caracteres, destaque = palavras soltas que existem no hook, sem setas, nunca com palavras de `HOOK_PALAVRAS_PROIBIDAS`;
- cada legenda só promete o que o recurso tem (faz a lista das promessas e confere com o PDF), acaba em "Se queres …, comenta PALAVRA.";
- nenhum trecho de mais de 80 caracteres igual a outra legenda do banco;
- se o banco já tiver famílias vencedoras (estado `vencedor`, ver o último `metricas/ciclos/*/analise.json`), escreve mais dentro dessas famílias;
- ids a seguir ao último do banco; `origem: "novo-recurso AAAA-MM-DD"`, `estado: "novo"`.
Valida as larguras com o renderizador antes de gravar (`fabrica/gerar_reel.py`: `ajustar_tamanho` / `largura_linha` ≤ 900 px). Se houver B-rolls cortados, gera 1 vídeo de ensaio (`$PY fabrica/gerar_reel.py um --ensaio --texto Hxxx --n 99`) e mostra 2 frames.

## 7. Ativar ou pôr em espera (regra dos 5)

Em `banco/recursos.json` entra `{recurso, titulo, link, automacao_id, entrou, ativo}`:
- **Menos de 5 ativos:** `ativo: true` — entra já na rotação diária.
- **Já há 5:** `ativo: false, espera: true` — entra na próxima análise de 14 dias. Se a pessoa disser "quero já", troca pelo ativo com menos comentários por 1 000 views e regista em `recursos/lista.md`.
Atualiza `recursos/lista.md` (ativos, em espera, arquivados).

## 8. Fecho

Diz, curto: palavra, link do PDF, nº de textos, se ficou ativo ou em espera, e o vídeo de ensaio.
