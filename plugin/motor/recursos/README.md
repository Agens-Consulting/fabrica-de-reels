# Recursos dos trial reels

Recurso é o que a pessoa recebe por DM quando comenta a palavra: um PDF, um link, um modelo, um prompt. Todos os recursos dos trial reels vivem aqui. Como se escolhe a palavra e se cria a automação está em [../ctas/como-construir-cta.md](../ctas/como-construir-cta.md).

## Onde fica cada recurso

Uma pasta por recurso, com o nome da palavra em maiúsculas:

```
recursos/
  lista.md            ← a lista de todos os recursos, ativos e arquivados
  CABULA/
    recurso.pdf       ← o ficheiro que se entrega (ou recurso.md, .docx…)
    link.txt          ← o link que vai no botão da DM (Drive, site…)
    ficha.md          ← o que é, para que reels serve, a DM usada, o id da automação
  _arquivo/           ← recursos retirados, com as mesmas pastas
```

- **O ficheiro original fica sempre aqui**, mesmo que a entrega seja por um link da Drive. Se o link morrer, o recurso não se perde.
- **Se o recurso é só um link** (um site, uma ferramenta), a pasta tem o `link.txt` e a `ficha.md`.
- **Nada vai para a DM sem estar nesta pasta primeiro.**

## Regra dos 5

Nunca há mais de **5 recursos ativos** ao mesmo tempo nos trial reels.

O ciclo:

1. Começa-se com 5 recursos ativos, cada um com a sua palavra.
2. Cada recurso entra em reels durante um ciclo de **14 dias**, e pelo menos em **5 reels** diferentes. Antes disso não há dados para comparar.
3. No fim do ciclo, ordena-se pelos **comentários com a palavra por cada 1 000 views** dos reels onde entrou. Dividir pelas views é o que torna a comparação justa: um recurso que saiu em reels mais vistos teria sempre mais comentários.
4. **Os 3 melhores ficam. Os 2 piores saem** e são substituídos por 2 recursos novos.
5. Começa novo ciclo.

O que acontece a um recurso que sai:

- Deixa de entrar em reels novos a partir desse dia.
- **A automação fica ligada mais 30 dias**, porque os reels antigos continuam a receber comentários e quem comenta tem de receber o recurso.
- Ao fim dos 30 dias apaga-se a automação (`zernio.py apagar`), move-se a pasta para `_arquivo/` e marca-se como arquivado em [lista.md](lista.md), com os números finais. A palavra fica livre outra vez.

Os recursos novos que entram não têm de ser ideias novas: podem ser versões melhoradas dos 3 que ganharam (mais prompts, outro formato, outro setor).

## O que torna um recurso bom

- **É a continuação do reel.** Quem comentou depois de um reel sobre emails quer uma coisa sobre emails.
- **Usa-se no dia seguinte.** Um prompt para copiar, um modelo para preencher, um passo a passo. Nada de "visão" ou "tendências".
- **Tem valor próprio.** Foi pensado para servir, e nota-se. Uma lista de links solta não é um recurso. Cada ferramenta leva o que faz e quando faz sentido; cada prompt vem pronto a copiar, com um exemplo de resposta; cada modelo vem em branco e pronto a usar.
- **É verdade.** Só se oferece o que o dono da conta usa ou fez de facto.

## Aspeto e formato

**Na estética da pessoa, clara e cuidada.** O recurso tem de parecer que deu trabalho a fazer: limpo, arrumado, fácil de ler na diagonal e bonito de abrir. As cores e as letras são as do dono da conta, definidas no `.env` (`MARCA_COR_PRINCIPAL`, `MARCA_COR_SECUNDARIA`, `MARCA_LETRA_TITULOS`, `MARCA_LETRA_TEXTO`).

- **Ferramenta:** `$PY ferramentas/recurso_pdf.py recursos/PALAVRA/spec.json --previa` (`$PY` = o Python do `.venv` da pasta de trabalho: `.venv/bin/python` no Mac, `.venv\Scripts\python.exe` no Windows). Gera `recursos/PALAVRA/recurso.pdf` em A4 ao alto, com capa, numeração em cada página e a página de CTAs no fim; com `--previa` tira também uma imagem de cada página (`previa_N.png`) para se ver antes de entregar. O formato do `spec.json` (páginas com parágrafos, listas, passos, prompts em bloco de código, tabelas e caixas de destaque) está no topo do próprio script.
- **Visual a ajudar a ler:** tabelas, caixas de destaque, prompts em bloco de código. Pouco texto corrido.
- **Português de Portugal**, com as mesmas regras de voz dos hooks e das legendas.
- **Até 10 MB**, para se carregar para a Drive pelo conector sem problemas.

**3 a 5 páginas, sempre nesta ordem:**

| Página | O que leva |
|---|---|
| 1. Capa | título do recurso (a promessa do reel), uma linha a dizer o que está lá dentro, o nome ou a conta do dono |
| 2 a 4. Conteúdo | 1 a 3 páginas com o valor: os prompts, o passo a passo, a tabela, o modelo |
| Última. CTAs | uma página simples com os pedidos abaixo |

Mais de 5 páginas só se o recurso for mesmo muito específico e o dono da conta concordar. Na dúvida, corta-se.

**A última página: os CTAs da pessoa, sempre os mesmos, por esta ordem.** Só aparecem os que estiverem preenchidos no `.env`:

1. **Entra na comunidade** (`CTA_COMUNIDADE_NOME`, `CTA_COMUNIDADE_LINK`): ex.: um grupo de WhatsApp ou uma newsletter.
2. **Segue no Instagram** (`CTA_INSTAGRAM_LINK`, com o @ de `INSTAGRAM_CONTA`).
3. **Marca uma conversa ou visita o site** (`CTA_REUNIAO_LINK`, `CTA_SITE_LINK`): para quem quer trabalhar com o dono da conta.

Cada CTA leva uma frase curta a dizer o que a pessoa ganha (ex.: "Todas as semanas, o que estou a testar com IA") e o link clicável. A página é simples: poucos blocos, muito espaço em branco, nada mais.

Os links vêm do `.env` (`CTA_*`). Se algum mudar, muda-se lá e os PDFs seguintes já saem com o novo.

## Do ficheiro à DM

1. O recurso faz-se e guarda-se em `recursos/PALAVRA/`: o `spec.json` e o PDF gerado com `$PY ferramentas/recurso_pdf.py recursos/PALAVRA/spec.json --previa`. Veem-se as prévias antes de avançar.
2. O Claude carrega o PDF para a pasta de recursos da Drive (`DRIVE_PASTA_RECURSOS` no `.env`), numa conversa, com o conector "Google Drive" do Claude, com o nome `AAAA_MM_DD_Recurso_PALAVRA.pdf`.
3. Põe-no público ("qualquer pessoa com o link pode ver"), também pelo conector, e fica com o link a pôr no botão da DM. Se a partilha falhar (ou o conector não estiver ligado), não se cria a automação.
4. O link vai para `recursos/PALAVRA/link.txt`.
5. Cria-se a automação (passo 5 de `../ctas/como-construir-cta.md`).

Tudo isto faz-se de uma vez com `/fabrica-de-reels:novo-recurso`.
