# SGV-M24 — Leitura: HAR + inovações históricas filtradas

**Execução:** GitHub Actions run 38174132978 (44 jobs, todos com sucesso). 81/84 origens válidas (3 falhas de ajuste registradas: um regime lento com menos de 300 linhas no prefixo — não substituídas). Só dados exploratórios. Recontagem independente confere (HARLMF: HSIC_5 26/81, M11 14/79, lin_5 18/81).

## 1. Resultado

| | MSARLM (M23) | HARLM | **HARLMF** | BL |
|---|---|---|---|---|
| M11 (forma) | 33% | 30% | **18%** | 8% |
| Fisher–Rao / energy | 25 / 16% | 21 / 14% | **17 / 15%** | 11 / 10% |
| lin 1/5/30 | 15 / 51 / 22% | 14 / 23 / 28% | **12 / 22 / 27%** | 7 / 14 / 16% |
| vol 1/5/30 | 26 / 52 / 30% | 27 / 28 / 33% | **22 / 25 / 31%** | 9 / 10 / 9% |
| HSIC 1/5/30 | 35 / 60 / 33% | 30 / 43 / 42% | **22 / 32 / 36%** | 11 / 11 / 15% |

- **Primário: sim nas quatro.** A autorregressão por horizontes (HAR) derrubou a dependência no lag de 5 min (lin 51→22%, vol 52→25%, HSIC 60→32%), e as inovações reais derrubaram a forma (M11 33→18%), todos com p < 0,001.
- **As inovações reais são o que conserta a forma:** de HARLM para HARLMF, o M11 cai de 30% para 18% (10×0 discordantes) e a dependência não linear também cai; a dependência linear não muda. A forma não gaussiana do BTC vive nas **inovações**, não na dinâmica.
- **Veredito pré-registrado: "não fecha a lacuna".** O HARLMF ainda é significativamente pior que os blocos reais em 7 de 12 estatísticas: **memória de volatilidade em todas as defasagens** (22–31% contra ~9%), HSIC em todas as defasagens e M11.

## 2. O que falta agora
O que sobra tem um nome: **memória de volatilidade de várias escalas.** O GARCH(1,1) tem uma única escala de persistência; a volatilidade do BTC, como a da dependência linear, tem várias (minutos, horas). O mesmo remédio que funcionou para a média deve funcionar para a variância: **volatilidade heterogênea por horizontes** (HAR na variância, ou GARCH de componentes). É também o que a literatura de volatilidade realizada encontra.

## 3. Trajetória do modelo explícito (1m, alarmes de HSIC no lag 5 / M11)
| Modelo | HSIC_5 | M11 |
|---|---|---|
| 2 escalas Markov (M17) | 80% | 30% |
| + DCC + memória longa (M18) | 58–61% | 24% |
| + VAR(1) + GARCH (M23) | 60–64% | 28–33% |
| **+ HAR + inovações reais (M24)** | **32%** | **18%** |
| Blocos reais (BL) | 11–13% | 8–11% |

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário em lin_5, vol_5, HSIC_5 (70%) | sim | ✅ |
| Primário em M11 (40%) | sim | ✅ (contra a aposta) |
| "Equivalente ao BL" (30%) | não | ✅ (não ocorreu) |
| "Adequação plena" (8%) | não | ✅ (não ocorreu) |
| HSIC_5 entre 15–35% | 32% | ✅ |
