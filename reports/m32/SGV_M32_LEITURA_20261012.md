# SGV-M32 — Leitura: a curvatura da casca não acrescenta informação de risco

**Execução:** GitHub Actions run 38343219606 (resultados em `c6a6f21`). Protocolo `reports/PROTOCOLO_SGV_M32_20261012.md` (SHA-256 `42eb0212…eaba0`) e os dois módulos conferidos pelo código antes de baixar o SOL. **SOLUSDT 1m 2026-05..09**, um único trecho contínuo (220.320 min); 14.491 origens elegíveis (elegibilidade só pelo passado), casca válida em **100%**; **11.711 avaliadas** (jun–set).

## Resultado
| | valor |
|---|---|
| skill da casca (B1S vs B1) | **+0,02%** |
| p (HAC 1 dia / 1 semana) | 0,45 / 0,43 |
| IC 95% do skill (HAC 1 dia) | −0,20% a +0,23% |
| IC 95% do skill (HAC 1 semana) | −0,16% a +0,19% |
| bootstrap (1 dia / 1 semana) | p = 0,44 / 0,41 |
| por mês (jun, jul, ago, set) | −0,07%, −0,24%, +0,14%, +0,20% |

**Primário: FALHA.** O ganho é zero, e o intervalo de 95% fica inteiro abaixo do limiar de 0,5% nas duas escalas de dependência. Pelo poder com ganho plantado (~60% para 0,8% com menos origens), um efeito de 0,5% ainda poderia escapar, mas o **intervalo observado** exclui 0,25% ou mais.

**Contexto (descritivo):** neste ativo, cone e cintura também não melhoram o B0 (−0,23%), repetindo o T1 do M31 no ETH.

## Leitura
Agora com a variável **nativa da casca** (área em sela da HDR50, curvatura analítica), testada como hipótese própria em ativo nunca visto: a geometria da casca **não acrescenta informação à previsão do risco de 15 min** além de um baseline econométrico forte que já tem as estatísticas condicionais da forma. Escopo: SOL 1m jun–set/2026, este horizonte, este baseline.
Junto com M31 (ETH) e H-DOM (BTC), fecha o ciclo: a forma descreve o funcionamento; não traz informação adicional nem de **direção** nem de **risco de curto prazo**.

## Aposta de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário passa (~5%) | não | ✅ (não ocorreu) |
| Skill pontual > 0 (~45%) | sim (+0,02%, praticamente zero) | — (moeda) |
