# Hook textual: estética e posicionamento

Estilo fixo, igual para **todos** os Reels de Teste e para todas as contas, seja qual for o vídeo. Não se personaliza: é o estilo que funciona.
O hook textual é o texto queimado por cima do vídeo. A escrita dos hooks fica noutro documento.

---

## 1. Letra

| Parâmetro | Valor |
|---|---|
| Fonte | **Montserrat**, peso **SemiBold** (`FONTE_FICHEIRO` e `FONTE_PESO` no `.env`; por defeito `ferramentas/fontes/Montserrat-Variable.ttf`, variação `SemiBold`) |
| Caixa | **Variável de teste** (sorteada por reel): MAIÚSCULAS ou só a primeira letra maiúscula (com nomes próprios: Claude, ChatGPT, GitHub…). Só minúsculas já se testou e não resultou, por isso não se usa. O banco guarda em MAIÚSCULAS |
| Cor do texto | Branco `#FFFFFF` |
| Contorno | **Preto `#000000`, 3 px** (é o elemento principal de leitura) |
| Sombra | Muito leve: preta, deslocada 2 px para baixo, desfoque ~4 px, opacidade ~35%. Só para descolar do fundo, nunca visível como "sombra" |
| Tamanho | **52 px** num quadro de 1080 px de largura (60 e 62 px ficaram grandes demais). Se uma linha não couber na largura útil, encolhe 2 px de cada vez, até ao mínimo do código (`TAM_MIN`) |
| Entrelinha | Apertada: **1,12 × o tamanho** (linhas juntas, um bloco só) |
| Alinhamento | Centrado horizontalmente |

Referência visual: Montserrat SemiBold branco, uma palavra a amarelo, com **contorno preto em vez de sombra**: em vez de um halo desfocado, contorno nítido + sombra mínima. O código que desenha o hook está em `fabrica/gerar_reel.py` (reels de texto) e `talking-head/scripts/texto.py` (talking heads).

Porquê: é a letra que toda a gente reconhece e lê sem esforço. Branco com contorno preto lê-se em qualquer fundo.

---

## 2. Posição

### Vertical
- O hook fica **centrado na linha a meio entre 3/4 e 4/5 da altura do ecrã, contados a partir de baixo**. Fica na parte de cima do ecrã.
- Em 1080×1920: 3/4 a contar de baixo = y 480 px a contar do topo; 4/5 a contar de baixo = y 384 px. Logo o **centro do bloco do hook fica em y = 432 px** (22,5% da altura, a contar do topo).
- Com 3 linhas a 52 px o bloco ocupa ~y 345 a 519, sempre abaixo dos 220 px de cima que o Instagram reserva (nome da conta, relógio).
- Sem exceções, independentemente do vídeo.
- Para formatos que não sejam 9:16 (ex. 4:5, 1080×1350), aplica-se a mesma proporção: centro em 22,5% da altura (y ≈ 304 px).

### Margem de segurança (moldura)
- Largura útil do hook: **900 px** no máximo (90 px de margem em cada lado). O texto nunca encosta às bordas.
- Na prática, isto dá linhas curtas: ~18-22 caracteres por linha a 52 px.
- Máximo de **3 linhas**. Se precisar de mais, o hook está comprido demais (problema de escrita, não de layout).
- As quebras de linha ficam onde a pessoa pararia de ler, nunca a meio de uma ideia.


---

## 3. Cores de destaque

- **1 palavra-chave por hook, 2 no máximo.** O resto é branco.
- A palavra de destaque tem o mesmo contorno e sombra do resto.
- A cor escolhe-se **automaticamente pelo fundo**, a partir desta paleta curta:

| # | Cor | Hex | Quando |
|---|---|---|---|
| 1 | Amarelo oficial | `#F4EE00` | **Por defeito.** É o amarelo de base do estilo |
| 2 | Amarelo torrado | `#FFC107` | Fundos esverdeados ou muito claros/amarelados, onde o amarelo vibrante se perde |
| 3 | Laranja | `#FF8A00` | Fundos frios (azul, cinzento, ciano) onde dá mais contraste que o amarelo |
| 4 | Ciano | `#00E5FF` | Só quando o fundo é quente e saturado (amarelos, laranjas, vermelhos, madeira) e nenhum dos três anteriores se destaca |

Sobre a paleta: os três primeiros mantêm a identidade "amarela" e cobrem quase todos os casos. O ciano é a válvula de escape para fundos onde nenhum amarelo funciona. A paleta e a ordem estão em `CORES_DESTAQUE` no `.env`, com estes valores por defeito; se se tirar o ciano, o recurso passa a ser o amarelo oficial.

### Como o código escolhe a cor
1. Recolhe a zona do vídeo por trás do hook (a caixa do texto + 40 px à volta) em vários frames ao longo do tempo em que o hook está no ecrã.
2. Calcula a cor média e a luminosidade dessa zona.
3. Para cada cor da paleta, mede o contraste com o fundo (diferença de cor em espaço Lab, ΔE, e diferença de matiz).
4. Escolhe a primeira cor da paleta, por ordem, que passe o limiar de contraste (ΔE ≥ 40 como ponto de partida, a afinar).
5. Se nenhuma passar, usa o **amarelo oficial `#F4EE00`** (o contorno preto garante a leitura na mesma).
6. Regista no log a cor escolhida e o ΔE, para se poder cruzar mais tarde cor de destaque com métricas.

---

## 3.1 Segundo hook (variável de teste)

Texto pequeno por baixo do hook, sempre entre parênteses: "(vê a legenda)", "(está tudo na legenda)", "(lê a legenda até ao fim)", "(o resto está na legenda)".
- Montserrat **Medium Italic**, 40 px, branco, contorno preto de 2 px, 14 px abaixo do bloco do hook.
- Sorteado por reel: **não aparece**, aparece **desde o início** ou aparece **aos 3 s**.
- **Setas (↓, 👇) nunca** (regra de base): por baixo do hook ou não há nada ou há o segundo hook.

## 4. Checklist antes de publicar
- [ ] Montserrat SemiBold, caixa sorteada (MAIÚSCULAS ou só a primeira), branco
- [ ] Contorno preto 3 px, sombra quase invisível
- [ ] Bloco centrado na posição vertical definida
- [ ] Nada fora da largura útil de 900 px
- [ ] Máximo 3 linhas, entrelinha apertada
- [ ] 1 palavra de destaque (2 no máximo), cor escolhida pelo fundo
- [ ] Frame de verificação visto antes do render final
