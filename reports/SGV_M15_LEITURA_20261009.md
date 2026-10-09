# SGV-M15 — Leitura dos resultados contra o pré-registro

**Execução:** GitHub Actions run 38000239869 (122 jobs, todos com sucesso; piloto aprovado). 1000 ensaios externos (500 HMM, 500 VAR), zero falhas de ajuste, ≤6 medições M11 inválidas por cenário. Tabelas completas: `reports/m15/SGV_M15_RESULTADOS.md`; dados brutos de cada ensaio: `reports/m15/shards/`. Contagens conferidas por recontagem independente a partir das referências brutas.
**Bônus de integridade:** os 82 artefatos do M14 (run 37988651089) foram preservados em `reports/m14_artefatos/`; a tabela oficial confere com a relatada (6,20 / 7,30 / 57,60 / 16,20%).

## 1. O instrumento se reproduz
| Cenário (M11) | M14 | M15 (verdades novas) |
|---|---|---|
| HMM→HMM | 7,3% | 6,9% [5,0–9,4] |
| HMM→VAR | 57,6% | 60,2% [55,8–64,4] |
| HMM→blocos 15 | 16,2% | 16,0% [13,0–19,5] |

## 2. Respostas às perguntas pré-registradas
| | Resultado | Leitura pré-acordada |
|---|---|---|
| **Q1 persistência** | GMM_IID 37,2% vs HMM 6,9% (150×0 discordantes, p≈7e-46) | **A persistência dos regimes pesa — e muito.** |
| **Q2 forma** | VAR 60,2% vs GMM_IID 37,2% (p≈1e-26) | **A forma conjunta também pesa.** |
| **Q3 dose** | B15 16,0% → B60 8,4% → B150 8,7% (B15>B150, p≈6e-8) | Blocos ≥ ~60 (≥ tempo de correlação do estado, ~47) já se aproximam do HMM correto; platô. |
| **Q4 M11 vs Fisher–Rao cov.** | Significativo em VAR (60,2 vs 19,0%) e GMM_IID (37,2 vs 23,6%); não em B15/B60 | Ver regra de calibração abaixo. |
| **Q5 M11 vs energy** | Significativo só em VAR (60,2 vs 45,2%); energy **maior** que M11 em GMM_IID (67,8 vs 37,2), B15 (30,0 vs 16,0), B60 (12,2 vs 8,4) | **As cascas carregam informação além da energy distance para erro de forma**; para erro de persistência, a energy distance é mais sensível. |

**Regra dos 2 p.p. (Q4), aplicada à letra:** calibração do `fr_cov` vs `m11` — HMM→HMM 6,2 vs 6,9% (diferença 0,7 p.p., ok); **VAR→VAR 3,0 vs 6,2% (3,2 p.p., acima do limite)**. Pelo protocolo, a vantagem do M11 sobre o Fisher–Rao recebe o rótulo **"possivelmente afetada por calibração diferente"**. Comentário não pré-registrado: a diferença de tamanho (3 p.p., e no cenário VAR-verdade) dificilmente explica uma diferença de poder de 41 p.p. no cenário HMM-verdade, onde a calibração dos dois é equivalente — mas o rótulo formal fica como está.
Para Q5: energy 7,2% (HMM→HMM) e 4,4% (VAR→VAR) vs m11 6,9% e 6,2% — dentro dos 2 p.p.; a vantagem do M11 no cenário VAR vale sem ressalva.

## 3. O achado principal: as três réguas são complementares — e juntas diagnosticam
| Nulo que falta… | M11 (forma registrada) | Fisher–Rao cov. (2ª ordem) | Energy (distribuição inteira) |
|---|---|---|---|
| …**forma** (VAR, unimodal) | **60%** | 19% | 45% |
| …**persistência** (GMM_IID) | 37% | 24% | **68%** |
| …persistência longa (B15) | 16% | 19% | **30%** |

Mecanismo coerente com a construção do M11: ele **centra, escala e registra por rotação** as cascas antes de medir — portanto descarta deslocamentos e dilatações de massa e fica com a *forma*. A energy distance vê tudo, inclusive a massa migrando entre regimes (o efeito típico de persistência). A covariância vê só a 2ª ordem e é a menos sensível nos dois casos.
**Consequência:** o padrão (M11, FR, energy) funciona como **assinatura do tipo de inadequação** — M11 ≫ energy aponta erro de forma; energy ≫ M11 aponta erro de memória/persistência. É exatamente o passo "o auditor diz *o que* está errado".

## 4. Correções ao que dissemos depois do M14
- A leitura "a geometria responde mais à forma do que à persistência" (minha e do colaborador) **estava errada**: os blocos de 15 alarmaram pouco porque preservam persistência *parcial*, não só a forma. Sem memória alguma (GMM_IID), o alarme vai a 37%.
- Decomposição aproximada do excesso do VAR no M11: ~30 p.p. por falta de persistência (GMM_IID − HMM) + ~23 p.p. por forma errada (VAR − GMM_IID).

## 5. Placar das apostas de Claude (registradas no protocolo)
| Aposta | Resultado | |
|---|---|---|
| HMM→HMM 5–10% | 6,9% | ✅ |
| GMM_IID 8–20% | 37,2% | ❌ (subestimei a persistência) |
| P(Q1)≈55% | significativo | ✅ direção |
| VAR 50–65%; P(Q2)≈90% | 60,2%; significativo | ✅ |
| B15 12–20, B60 7–13, B150 5–10; P(Q3)≈75% | 16,0 / 8,4 / 8,7; significativo | ✅ |
| fr_cov ≥ M11 em HMM→VAR (60%) | 19,0% vs 60,2% | ❌ |
| P(≥1 Q4)≈25% | ocorreu | ❌ contra a aposta |
| P(≥1 Q5)≈20% | ocorreu | ❌ contra a aposta |
| fr_cov calibrado em VAR→VAR (70%) | 3,0% [1,8–4,9] — conservador | ❌ |

Eu esperava que a geometria das cascas fosse redundante com a covariância. **Os dados disseram o contrário**: para erros de forma, as cascas veem muito mais.

## 6. Limites (inalterados)
Mundo sintético de misturas gaussianas; "forma" aqui é sobretudo bimodalidade. Nada se transfere automaticamente ao BTC. O M11 segue ligeiramente liberal sob o HMM correto (6,9%; histograma de postos com leve excesso nas posições 1–2); o Fisher–Rao é ligeiramente conservador no VAR→VAR.

## 7. Próximo passo sugerido
Aplicar o **trio** (M11, Fisher–Rao, energy) aos nulos N0–N3 do BTC **exploratório**, lendo o *padrão* em vez de um alarme isolado — com R maior que 19 para não depender do limiar de 5%, e com a liberalidade de ~2 p.p. do M11 descontada.
