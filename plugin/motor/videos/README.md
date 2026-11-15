# Imagens de fundo (vídeos raw)

## De onde vêm

1. **O dono da conta guarda os vídeos raw na pasta B-rolls da Drive** (a que o `/fabrica-de-reels:comecar` criou; o id está em `DRIVE_PASTA_BROLLS` no `.env`). A pasta está partilhada como "qualquer pessoa com o link pode ver", por isso os scripts leem-na sem chaves (`../ferramentas/drive_publico.py`).
2. **Uma vez por dia, a tarefa automática** (`videos/sincronizar.py`, chamada pela fábrica diária) vê se há vídeos novos nessa pasta. Se houver, descarrega-os para `videos/raw/`. Se não houver, não faz nada. O mesmo para as músicas da pasta Músicas (`DRIVE_PASTA_MUSICAS`), que vão para `audios/raw/`.
3. **Cada vídeo descarregado entra no registo** (`registo.json`) com: nome, data, duração, tipo de imagem (ex.: carro, secretária, rua, café) e estado (novo, a testar, vencedor, retirado).

## Durante quanto tempo se usa cada um

Enquanto os números deixarem. No relatório de 14 em 14 dias (`../metricas/README.md`) decide-se:
- quais continuam;
- quais passam a ser usados menos ou saem;
- **que tipo de vídeos é preciso gravar a mais**. O pedido ao dono da conta parte do Claude, com base nos que ganharam.

Ponto de partida: 1/3 dos reels do dia com imagens novas (em teste), 2/3 com imagens já validadas.

## O que serve como imagem de fundo

Vídeos de pelo menos 6 segundos, verticais, sem texto nem pessoas a falar para a câmara, com o dono da conta no dia a dia: a trabalhar ao computador, no carro, a andar na rua, a preparar um café, a escrever, numa reunião. Para cada situação, um grande plano, um plano médio e um plano aberto. Nada de cenários demasiado luxuosos, que parecem falsos.

A parte de cima do ecrã (onde fica o hook, à volta de y = 432 em 1920) deve ser calma o suficiente para o texto se ler.

## Cortes de 8 segundos

Os reels têm **5, 6, 7 ou 8 segundos** (variável de teste). Cada B-roll é cortado uma vez nos seus melhores 8 s por `cortar.py` (sem IA: mede nitidez, estabilidade e se a zona do hook está calma). Os cortes ficam no disco, em `videos/cortados/` (não voltam para a Drive). O gerador diário só usa cortes.

## Notas

- Quantos mais B-rolls na pasta, menos o mesmo fundo se repete.
- Se aparecerem vídeos que não sirvam (com texto, a falar para a câmara, tremidos), marcam-se como `retirado` no registo.
