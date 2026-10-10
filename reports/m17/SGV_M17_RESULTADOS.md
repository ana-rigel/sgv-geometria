# SGV-M17 — Que tipo de memória o BTC tem? (resultados)

**Somente dados exploratórios.** Gerado por `scripts/m17_agregar.py`; protocolo e apostas congelados antes em `reports/PROTOCOLO_SGV_M17_20261010.md`. Origens consecutivas não são independentes (Wilson otimista).

## 1m (origens: {'fit_failed': 2, 'valid': 82})

| Nulo | M11 (forma) | Fisher–Rao | Energy (memória) | Fecha a lacuna? |
|---|---|---|---|---|
| H2 — HMM 2 estados | 60.0% [49.0%–70.0%] (48/80) | 69.5% [58.9%–78.4%] (57/82) | 81.7% [72.0%–88.6%] (67/82) | não |
| H4 — HMM 4 estados | 36.2% [26.6%–47.2%] (29/80) | 47.6% [37.1%–58.2%] (39/82) | 46.3% [36.0%–57.1%] (38/82) | não |
| MS — 2 escalas, Markov | 30.0% [21.1%–40.8%] (24/80) | 46.3% [36.0%–57.1%] (38/82) | 30.5% [21.6%–41.1%] (25/82) | não |
| MSSM — 2 escalas, semi-Markov | 33.8% [24.3%–44.6%] (27/80) | 45.1% [34.8%–55.9%] (37/82) | 32.9% [23.7%–43.7%] (27/82) | não |
| MSR — 2 escalas, Markov + relógio | 33.8% [24.3%–44.6%] (27/80) | 45.1% [34.8%–55.9%] (37/82) | 30.5% [21.6%–41.1%] (25/82) | não |
| MSSMR — 2 escalas, semi-Markov + relógio | 33.3% [23.9%–44.4%] (26/78) | 48.8% [38.3%–59.4%] (40/82) | 31.7% [22.6%–42.4%] (26/82) | não |
| N3 — M12 N3 (âncora) | 7.8% [3.6%–16.0%] (6/77) | 15.9% [9.5%–25.3%] (13/82) | 26.8% [18.4%–37.3%] (22/82) | não |

Contrastes pré-registrados (régua energy, McNemar exato pareado unilateral, α = 0,01 cada):

| Contraste | A | B | taxa A | taxa B | só A | só B | p | Significativo |
|---|---|---|---|---|---|---|---|---|
| C1_escala_lenta | H4 | MS | 46.3% | 30.5% | 14 | 1 | 0.00049 | sim |
| C2_envelhecimento | MS | MSSM | 30.5% | 32.9% | 2 | 4 | 0.89 | não |
| C3a_relogio_MS | MS | MSR | 30.5% | 30.5% | 6 | 6 | 0.61 | não |
| C3b_relogio_MSSM | MSSM | MSSMR | 32.9% | 31.7% | 7 | 6 | 0.5 | não |
| C4_mais_estados | H2 | H4 | 81.7% | 46.3% | 29 | 0 | 1.9e-09 | sim |

Diagnósticos de ajuste (descritivos):

```
{
 "H4_time_scales_bars_quartiles": [
  0.48974290736660514,
  4.637389207397473,
  14.549677041760912
 ],
 "slow_regime_mean_duration_bars_quartiles": [
  166.6818181818182,
  206.61111111111111,
  263.760101010101
 ],
 "slow_duration_cv_quartiles": [
  0.6881629729082795,
  0.8434065538404019,
  0.9797467783105199
 ],
 "slow_ks_vs_geometric_quartiles": [
  0.17769622725726392,
  0.20986460846120508,
  0.256609737858628
 ],
 "H_converged_fraction": {
  "H2": 1.0,
  "H4": 1.0
 }
}
```

## 1h (origens: {'valid': 18})

| Nulo | M11 (forma) | Fisher–Rao | Energy (memória) | Fecha a lacuna? |
|---|---|---|---|---|
| H2 — HMM 2 estados | 23.5% [9.6%–47.3%] (4/17) | 61.1% [38.6%–79.7%] (11/18) | 83.3% [60.8%–94.2%] (15/18) | não |
| H4 — HMM 4 estados | 11.8% [3.3%–34.3%] (2/17) | 33.3% [16.3%–56.3%] (6/18) | 50.0% [29.0%–71.0%] (9/18) | não |
| MS — 2 escalas, Markov | 17.6% [6.2%–41.0%] (3/17) | 33.3% [16.3%–56.3%] (6/18) | 44.4% [24.6%–66.3%] (8/18) | não |
| MSSM — 2 escalas, semi-Markov | 25.0% [10.2%–49.5%] (4/16) | 55.6% [33.7%–75.4%] (10/18) | 44.4% [24.6%–66.3%] (8/18) | não |
| MSR — 2 escalas, Markov + relógio | 17.6% [6.2%–41.0%] (3/17) | 50.0% [29.0%–71.0%] (9/18) | 38.9% [20.3%–61.4%] (7/18) | não |
| MSSMR — 2 escalas, semi-Markov + relógio | 29.4% [13.3%–53.1%] (5/17) | 44.4% [24.6%–66.3%] (8/18) | 38.9% [20.3%–61.4%] (7/18) | não |
| N3 — M12 N3 (âncora) | 0.0% [0.0%–19.4%] (0/16) | 16.7% [5.8%–39.2%] (3/18) | 44.4% [24.6%–66.3%] (8/18) | não |

Contrastes pré-registrados (régua energy, McNemar exato pareado unilateral, α = 0,01 cada):

| Contraste | A | B | taxa A | taxa B | só A | só B | p | Significativo |
|---|---|---|---|---|---|---|---|---|
| C1_escala_lenta | H4 | MS | 50.0% | 44.4% | 1 | 0 | 0.5 | não |
| C2_envelhecimento | MS | MSSM | 44.4% | 44.4% | 1 | 1 | 0.75 | não |
| C3a_relogio_MS | MS | MSR | 44.4% | 38.9% | 1 | 0 | 0.5 | não |
| C3b_relogio_MSSM | MSSM | MSSMR | 44.4% | 38.9% | 1 | 0 | 0.5 | não |
| C4_mais_estados | H2 | H4 | 83.3% | 50.0% | 6 | 0 | 0.016 | não |

Diagnósticos de ajuste (descritivos):

```
{
 "H4_time_scales_bars_quartiles": [
  0.48897866864012385,
  2.85378290843516,
  6.505888528957653
 ],
 "slow_regime_mean_duration_bars_quartiles": [
  62.08392857142857,
  77.89761904761906,
  88.0875
 ],
 "slow_duration_cv_quartiles": [
  0.48661526534607924,
  0.6217305227922667,
  0.8572424628822546
 ],
 "slow_ks_vs_geometric_quartiles": [
  0.22076009678035757,
  0.2510085847713983,
  0.3104952185036306
 ],
 "H_converged_fraction": {
  "H2": 1.0,
  "H4": 1.0
 }
}
```

