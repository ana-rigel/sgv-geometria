# SGV-M33 — Leitura: o T3 original também falha

**Execução:** GitHub Actions run 38383886563 (resultados em `54b40d6`). Protocolo `reports/PROTOCOLO_SGV_M33_20261013.md` (SHA-256 `277884d0…8754f`) e os três módulos conferidos pelo código antes de baixar o BNB. **BNBUSDT 1m 2026-05..09**, um trecho contínuo (220.320 min); 14.491 origens elegíveis (só pelo passado), casca válida em 100%; **11.711 avaliadas** (jun–set).

## Resultado (primário)
| | valor |
|---|---|
| skill B2 (com curvatura) vs B1+ (forma + elasticidade) | **−0,08%** |
| p (HAC 1 dia / 1 semana) | 0,86 / 0,90 |
| IC 95% do skill (HAC 1 dia) | −0,21% a +0,06% |
| IC 95% do skill (HAC 1 semana) | −0,19% a +0,04% |
| bootstrap (1 dia / 1 semana) | p = 0,86 / 0,90 |
| por mês (jun, jul, ago, set) | +0,04%, −0,10%, −0,16%, −0,06% |

**FALHA.** A curvatura não melhora — piora levemente — o modelo que já tem forma e elasticidade. O limite superior do intervalo (+0,06%) exclui até ganhos minúsculos.

## Descritivo de contexto (sem teste; não é achado)
No BNB, B1+ (forma + elasticidade) ficou **+0,50%** acima do B0, e B2 +0,42%. Isso **não foi testado** e contrasta com os outros ativos: no ETH, a forma sozinha deu −0,07% e a elasticidade +0,03% contra o B0; no SOL, a forma deu −0,23%. Um número descritivo, num terceiro ativo, sem correção e com sinal inconsistente entre ativos, **não vira hipótese** sem uma pergunta nova e uma amostra nova.

## Leitura
Com M32 (SOL, curvatura vs forma) e M33 (BNB, curvatura vs forma + elasticidade — o T3 original), a curvatura da casca foi testada duas vezes, em dois ativos nunca vistos, em especificações pré-registradas: **zero ganho nas duas** (+0,02% e −0,08%). A geometria intrínseca da casca não acrescenta informação à previsão do risco de 15 min.

## Aposta de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário passa (~4%) | não | ✅ (não ocorreu) |
