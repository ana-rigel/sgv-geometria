# SGV-M25 — Leitura: volatilidade multiescala

**Execução:** GitHub Actions run 38175488263 (44 jobs, todos com sucesso; 84/84 origens válidas). Só dados exploratórios.

## 1. Resultado pré-registrado
| | HARLMF (M24) | **HARLMFV (M25)** | BL |
|---|---|---|---|
| vol 1/5/30 | 23 / 29 / 26% | **19 / 30 / 27%** | 10 / 10 / 10% |
| HSIC 1/5/30 | 23 / 31 / 33% | 19 / 29 / 30% | 13 / 13 / 15% |
| M11 / Fisher–Rao / energy | 15 / 20 / 13% | 16 / 17 / 19% | 6 / 10 / 11% |

- **Primário: não.** A variância heterogênea por horizontes (1/15/60/240 min) **não** reduziu os alarmes de volatilidade (vol_1 p=0,23; vol_5 p=0,71; vol_30 p=0,73), embora o ajuste tenha usado de fato as escalas longas (pesos medianos de 60 e 240 min ≈ 0,08–0,10 para agressão e volume).
- **Veredito: "não fecha a lacuna"** — pior que o BL em vol 1/5/30 e HSIC 5/30.
- **A hipótese "falta volatilidade multiescala por coordenada" fica refutada** nesta forma.

## 2. Diagnóstico exploratório (não pré-registrado): onde está o descompasso
A estatística `vol_k` é uma matriz 3×3 (|coordenada no tempo t| × |coordenada no tempo t+k|). Comparando entrada por entrada, em 21 origens, observado contra 39 referências do HARLMFV (`scripts/m25_diag_vol_cruzada.py`):
- **lag 1, |retorno|ₜ → |agressão|ₜ₊₁: fora das referências em 95% das origens** (nominal ~10%). Em 11 de 11 origens checadas quanto ao sinal (`scripts/m25_diag_vol_cruzada_sinal.py`), o valor **real ficou abaixo de todas as referências**.
- Em menor grau: |volume|ₜ → |retorno|ₜ₊₁ acima do modelo (36%); |agressão|ₜ → |retorno|ₜ₊₁ abaixo (36%).

**Leitura:** o modelo transmite magnitude demais de um choque de preço para o desequilíbrio de agressão do minuto seguinte. **No BTC real, depois de um movimento grande de preço, o fluxo de agressão do minuto seguinte é mais equilibrado do que a persistência prevê.** É a assinatura de **resiliência da liquidez**: depois do choque, o outro lado entra e o livro se recompõe. O volume, por sua vez, antecipa a magnitude do próximo retorno mais do que o modelo prevê. São mecanismos **cruzados e assimétricos entre as coordenadas**, não a persistência de cada uma isolada.

## 3. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário nas três defasagens (45%) | não | ✅ (não ocorreu) |
| Primário ao menos em vol_30 (60%) | não | ❌ |
| "Equivalente ao BL" (30%) | não | ✅ (não ocorreu) |
| "Adequação plena" (8%) | não | ✅ (não ocorreu) |
| HSIC ainda pior que o BL em alguma defasagem (60%) | sim | ✅ |

## 4. Próximo passo (outro dia)
Pré-registrar e testar um termo explícito de **resiliência**: a magnitude do desequilíbrio de agressão em t+1 depende **negativamente** de |retorno|ₜ (além da própria persistência), e a variância do retorno em t+1 depende do volume em t. Se esse mecanismo cruzado fechar o resíduo de volatilidade, a descrição do BTC no 1m terá todas as peças nomeadas.
