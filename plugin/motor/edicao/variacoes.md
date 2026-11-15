# Variações obrigatórias de um vídeo raw

Regra: **cada vez que um vídeo raw sai como trial reel, sai diferente.** Nunca o mesmo ficheiro, hook ou legenda duas vezes. Repetir é o que dá o aviso "conteúdo muito parecido" do Instagram.

Fontes: dois reels de referência sobre trial reels, DfucBRuIg39 (saul media: 173 trial reels, 4,05M views, 6 568 seguidores em 8 semanas "sem conteúdo novo") e DffB0MjpwWq (Sam Gaudet).

## Por cada nova variação

**Sempre (os dois concordam):**
1. **Hook de texto novo no ecrã.** É a alteração que mais pesa e a única que serve também de teste: cada variação = um hook diferente sobre o mesmo corpo.
2. **Legenda nova.** Pode manter a palavra-chave, mas nunca o mesmo texto.
3. **Capa nova** (outro frame ou cartão).

**Mais 2 ou 3 alterações técnicas, rodando entre elas:**

| # | Alteração | Valor | ffmpeg (referência) |
|---|---|---|---|
| T1 | Zoom in | 1-3 % (1.01 a 1.03) | `scale=iw*1.02:-2,crop=1080:1920` |
| T2 | Velocidade | 0,97× a 1,05× | `setpts=PTS/1.03` + `atempo=1.03` |
| T3 | Brilho | ±2-4 % | `eq=brightness=0.03` |
| T4 | Cor | mais quente ou mais fria, subtil | `colorbalance=rs=0.04:bs=-0.03` |
| T5 | Espelhar | horizontal | `hflip` (**não** usar se houver texto, logótipos ou ecrãs filmados) |
| T6 | Cortar | 0,3-1 s ao início e/ou ao fim, ou trocar o CTA final | `-ss 0.5 -to <fim-0.5>` |
| T7 | Áudio | outra música de fundo ou outro volume | mistura nova |

## Divergência entre as fontes

- **saul:** as alterações técnicas (T1-T7) bastam para não parecer duplicado.
- **Sam:** velocidade e música "já não chegam". O que funciona é mudar o **texto no ecrã com a ferramenta nativa do Instagram** ao publicar.
- **Neste sistema:** publica-se pela API do Zernio, por isso não há ferramenta nativa. O texto vai queimado no vídeo, o que muda os píxeis do ficheiro na mesma. Fazem-se as duas coisas: hook novo + 2-3 técnicas.
- **Sam, extra:** publicar o mesmo vídeo uma vez como trial reel e outra no feed principal, em vez de passar o trial a público. Testar.

## Volume (referência, não meta)

- saul: ~3 trial reels por dia.
- Sam: 5-6 por dia, reciclando os 30 vídeos com mais views dos últimos 90 dias.

## Registo

Cada variação publicada fica com: vídeo raw de origem, hook, alterações técnicas usadas (ex.: `T1+T4+T6`), legenda e palavra-chave. Sem isto não dá para saber o que ganhou.
