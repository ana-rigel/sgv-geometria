# SGV-M31 — Leitura: a forma não acrescenta informação de risco a um baseline forte

**Execução:** GitHub Actions run 38339336194 (resultados em `56cfb47`). Protocolo `reports/PROTOCOLO_SGV_M31_20261012.md` (SHA-256 `eb82e7bb…2a85`) e módulo de engenharia (`f8a27723…2476`) conferidos pelo código antes de baixar os dados. **ETHUSDT 1m 2026-05..09**, um único trecho contínuo (220.320 min, sem lacunas); 14.490 origens, **11.711 avaliadas** (jun–set). Casca válida em 100% das janelas.

## Resultado
| Teste | Comparação | skill | p (HAC, 1 dia) | p (bootstrap) | critério | resultado |
|---|---|---|---|---|---|---|
| **T1** | B1 vs B0 | **−0,07%** | 0,65 | 0,64 | p < 0,05 e skill ≥ 1% | **FALHA** |
| T2 | B1+ vs B0+ | — | — | — | — | não testado (hierarquia) |
| T3 | B2 vs B1+ | — | — | — | — | não testado (hierarquia) |

Descritivos: skill de B1 vs B0 por mês −0,06%, −0,38%, +0,17%, −0,09% (jun a set); B0+ vs B0 +0,03% (a elasticidade móvel também não acrescenta nada).

**Leitura pré-registrada: a forma não acrescenta informação de risco relevante ao baseline forte.** Com o poder medido antes (efeito mínimo detectável ≈ 0,45% de skill a 80%), o resultado é **informativo**: se existe algum ganho, ele é menor que ~0,5%, metade do limiar de relevância. O intervalo do efeito exclui ganhos de 1%: o EP do delta é 0,00064 sobre uma deviança média de 0,381, ou seja, ±0,33% de skill em 2 EP em torno de −0,07%.

## O que isso diz
- O cone, a cintura e a elasticidade volatilidade–volume são estados reais e persistentes da forma (vistos no BTC), mas, **para prever o risco dos próximos 15 min**, a informação deles já está no que um HAR-X sazonal forte usa: volatilidade passada em várias escalas, amplitude, quarticidade, volume, relógio. A geometria descreve o funcionamento; ela não traz informação de risco que a econometria padrão não tenha.
- Como T1 falhou, as perguntas de atribuição (T2) e de geometria intrínseca (T3) não chegam a ser feitas, por desenho. Elas só fariam sentido se houvesse algo a atribuir.

## Apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| T1 passa (12%) | não | ✅ (não ocorreu) |
| T1 e T2 (6%) / T1, T2 e T3 (2%) | não testados | ✅ |
| B0+ melhora o B0 em ≥ 0,5% (30%, descritivo) | não (+0,03%) | ✅ (não ocorreu) |
