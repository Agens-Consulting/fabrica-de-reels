---
name: rever-hooks
description: Reescreve os hooks do banco da fábrica de trial reels com o guia de hooks mais recente (versão 2 - listas com gancho, POV só com afirmação difícil de acreditar, sem condições escondidas), traduzido para o tema da conta. Mantém as legendas que ainda pagam a promessa, reescreve as que não pagam, retira os textos antigos e grava os novos só depois do "sim" da pessoa. Usar quando a pessoa escreve "/rever-hooks", "os hooks estão maus", "os reels não passam das 200 views", "reescreve os hooks", "atualiza os hooks ao guia novo", ou quando o /reels avisa que o banco tem textos do guia antigo.
---

# Rever os hooks do banco

Português de Portugal.

```bash
P="$(cat ~/.fabrica-de-reels/pasta.txt)"; cd "$P"      # se não existir: corre primeiro /fabrica-de-reels:comecar
PY=.venv/bin/python; [ -f .venv/Scripts/python.exe ] && PY=.venv/Scripts/python.exe
export PYTHONUTF8=1
```

Lê primeiro, inteiros: `hooks/como-escrever-hooks-texto.md` (versão 2), `legendas/como-escrever-legendas.md`, `onboarding/perfil.md`, `banco/pesquisa-temas.md`, `banco/recursos.json`, `banco/textos.json`, e a `ficha.md` de cada recurso ativo em `recursos/PALAVRA/`.

## 1. Ver o que está no banco

- Textos com `estado` diferente de `retirado` e sem `"guia": 2`: são os que se reescrevem. **Os `vencedor` ficam** (já provaram), mesmo que sejam do guia antigo.
- Se existirem métricas (`metricas/reels_ultimo.json` ou o último `metricas/ciclos/*/analise.json`), cruza com `fabrica/historico.jsonl`. Mostra à pessoa, numa tabela curta, os 5 melhores e os 5 piores hooks, com views e comentários, e uma linha a dizer o que os piores têm em comum, nos termos do guia (sem gancho, POV de cena, condição, abstrato, esqueleto copiado de outro tema).

## 2. Tradução para hooks

Se `banco/pesquisa-temas.md` não tiver a secção "Tradução para hooks" (secção 4 do guia), escreve-a com o que está no perfil e nos recursos: as 15 a 20 coisas com nome do dia do leitor, quem pára (papel, idade), o que ele quer ter ou evitar, a autoridade do dono da conta e o calendário. Mostra-a em 5 a 8 linhas e pergunta se falta alguma coisa importante (uma pergunta só).

## 3. Escrever os novos

Por cada recurso ativo, 10 textos novos (hook + legenda), pelo processo da secção 14 do guia:
- 8 a 10 listas com gancho, pelo menos 4 ganchos diferentes por recurso; 0 a 2 POV só com uma afirmação difícil de acreditar e verdadeira; nenhuma condição;
- **a legenda paga a promessa do hook novo**: se o hook diz "os únicos 3 brinquedos", a legenda tem os 3. Aproveita a legenda antiga só se já pagar; senão reescreve-a, pelo guia das legendas, com o que o recurso entrega de facto;
- o pedido de comentário no fim, com a palavra do recurso;
- cada texto: `"molde"`, `"gancho"`, `"guia": 2`, `"origem": "rever-hooks AAAA-MM-DD"`, `"estado": "novo"`, ids a seguir ao último do banco;
- MAIÚSCULAS, ≤ 3 linhas de ≤ 22 caracteres, destaque = palavras soltas do hook, sem setas, nunca palavras de `HOOK_PALAVRAS_PROIBIDAS`. Valida as larguras com `fabrica/gerar_reel.py` (`ajustar_tamanho` / `largura_linha` ≤ 900 px).

## 4. Aprovar (uma vez)

Mostra só os hooks, agrupados por recurso, uma linha cada (hook · gancho), com os factos marcados `[CONFIRMAR]` em baixo. Num tema de saúde, de crianças ou de dinheiro, diz em 1 linha que é a pessoa quem garante que cada afirmação é verdade na área dela. Pede o "sim", ou os números dos hooks a cortar ou a mudar. Corrige e mostra só o que mudou.

## 5. Gravar

- Acrescenta os novos a `banco/textos.json`.
- Nos textos antigos reescritos, `"estado": "retirado"` e `"retirado_por": "rever-hooks AAAA-MM-DD"`. Nunca apagues textos: o histórico e a análise precisam deles.
- Se um recurso ativo ficar com menos de 6 textos não retirados, avisa e não retires os antigos desse recurso.
- Os reels que já estão agendados no Zernio não mudam. Os novos hooks entram a partir da próxima corrida diária.
- Se houver B-rolls cortados, gera 1 vídeo de ensaio com um dos hooks novos (`$PY fabrica/gerar_reel.py um --ensaio --texto Hxxx --n 99`) e mostra 2 frames.

## 6. Fecho

Diz, curto: quantos textos novos por recurso, quantos retirados, os ganchos usados e quando a análise de 14 dias vai comparar o guia 1 com o guia 2 (família "Versão do guia de hooks" no relatório).
