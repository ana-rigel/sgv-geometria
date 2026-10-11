# SGV-M23 — Leitura: o modelo mínimo do BTC 1m

**Execução:** GitHub Actions run 38172516995 (44 jobs, todos com sucesso; 84/84 origens válidas). Só dados exploratórios. Contagens conferidas por recontagem independente (MSARLM: lin_1 11/84, vol_1 19/84, M11 23/82).

## 1. Resultado

| Estatística | MSDCCLM (antes) | **MSARLM (modelo mínimo)** | BL (blocos reais) |
|---|---|---|---|
| lin_1 / vol_1 / HSIC_1 | 70 / 88 / 83% | **13 / 23 / 31%** | 10 / 10 / 12% |
| lin_5 / vol_5 / HSIC_5 | 48 / 68 / 58% | **49 / 51 / 64%** | 12 / 8 / 13% |
| lin_30 / vol_30 / HSIC_30 | 24 / 36 / 33% | **24 / 26 / 37%** | 15 / 11 / 15% |
| M11 / Fisher–Rao / energy | 24 / 33 / 17% | **28 / 23 / 14%** | 11 / 7 / 7% |

- **Primário: sim, a peça faltante funciona.** No lag 1, autorregressão + GARCH derrubam os alarmes de dependência linear (70→13%), de volatilidade (88→23%) e não linear (83→31%), todos com p < 10⁻¹³.
- **Veredito pré-registrado: "não fecha a lacuna".** O modelo mínimo ainda perde para os blocos reais em 9 das 12 estatísticas, sobretudo no **lag 5** (49–64%) e nas réguas de forma (M11) e covariância (Fisher–Rao).
- A **memória longa real** continua essencial: sem ela (MSAR), a dependência no lag 5 vai a 75–88%.

## 2. O que isso diz sobre o funcionamento

1. **A memória do BTC no 1m tem pelo menos três escalas.** Um VAR(1) captura a escala de **~1 minuto** (raio espectral mediano 0,35); o regime lento e o bloco real capturam as **horas**; mas sobra uma escala **intermediária, de vários minutos**, que nenhum dos dois cobre. É a mesma escala de **~14 minutos** que apareceu na autocorrelação do volume antes do M17. O GARCH estimado mostra o mesmo: volatilidade do volume e da agressão com persistência alta (β ≈ 0,93–0,94).
2. **A forma conjunta real continua não gaussiana** (M11 28% vs 11% do BL): emissões gaussianas condicionais não bastam para a forma do corpo.
3. O acoplamento (Fisher–Rao) melhorou (33→23%), mas também não chega ao BL.

## 3. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário nas três (75%) | sim | ✅ |
| lin_1 entre 10–25% | 13% | ✅ |
| vol_1 entre 15–40% | 23% | ✅ |
| "Adequação plena" (7%) | não | ✅ (não ocorreu) |
| "Equivalente ao BL" (25%) | não | ✅ (não ocorreu) |
| Maior perda para o BL: M11 45% / energy 30% / lag longo 25% | a maior perda foi na dependência de **lag intermediário (5 min)** — categoria que eu não previ | ❌ |

## 4. Próximo passo natural
A peça seguinte também é convencional: **memória heterogênea por horizontes** (o modelo HAR de Corsi, 2009, usado para volatilidade realizada) — autorregressão sobre médias de 1 min, ~15 min e ~1 h — no lugar do VAR(1), mantendo regimes lentos, GARCH e o bloco lento real. Ele ataca diretamente a escala intermediária que faltou. A forma não gaussiana (M11) pede, separadamente, inovações de cauda pesada ou cópula empírica.
