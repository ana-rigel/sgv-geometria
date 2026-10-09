# SGV-M14 — Calibração aninhada dos alarmes geométricos

**Experimento sintético, sem abrir dados BTC.** Geradores conhecidos fixos, prefixo reestimado em cada ensaio externo. As 20 trajetórias de cada ensaio passam pelo mesmo instrumento M11.

| Verdade → nulo ajustado | Ensaios válidos | Alarmes | Taxa | IC Wilson 95% | Falhas |
|---|---:|---:|---:|---|---:|
| VAR_fit | 500/500 | 31 | 6.20% | [4.40%, 8.67%] | 0 |
| HMM_fit | 493/500 | 36 | 7.30% | [5.32%, 9.94%] | 7 |
| HMM_to_VAR | 500/500 | 288 | 57.60% | [53.23%, 61.86%] | 0 |
| HMM_to_blocks | 500/500 | 81 | 16.20% | [13.23%, 19.69%] | 0 |

A taxa estimada depende desta família geradora, sua calibração por prefixo, inicialização e erro de estimação GMM/ICP. Modelos errados não possuem garantias de nível nominal. Nenhuma excedência no BTC implica tensão financeira por si só.

**Falhas:** em cada cenário ver SGV_M14_AGREGADO.json, que informa quantos ensaios foram descartados e limites de taxa sem assumir comportamento benigno dessas falhas.

**Integridade:** exatamente 500 IDs independentes por cenário, 20 shards disjuntos de 25 ensaios; nenhum uso de main ou meses confirmatórios.
