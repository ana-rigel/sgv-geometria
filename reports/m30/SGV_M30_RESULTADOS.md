# SGV-M30 — O volume reage ao tamanho dos choques (resultados)

Origens válidas: 84 ({'valid': 84}); ímpares (teste): 42. Agregado por `experiments/m30_volume_reage_choques.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M30_20261012.md`.

**Todas as origens:**

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXFB | 10% | 5% | 5% | 8% | 8% | 13% | 6% | 6% | 6% | 11% | 19% | 18% |
| HXCLK | 9% | 5% | 12% | 8% | 14% | 21% | 7% | 10% | 6% | 17% | 24% | 29% |
| BL | 12% | 10% | 10% | 10% | 13% | 13% | 11% | 8% | 11% | 8% | 10% | 13% |

**Só ímpares (teste):**

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXFB | 10% | 7% | 2% | 12% | 10% | 19% | 10% | 7% | 5% | 14% | 24% | 24% |
| HXCLK | 12% | 5% | 14% | 10% | 14% | 26% | 10% | 10% | 5% | 17% | 24% | 29% |
| BL | 12% | 14% | 7% | 10% | 14% | 14% | 10% | 7% | 7% | 10% | 10% | 17% |

**Mecanismo (ímpares, teste do sinal unilateral):**

- beta_absz_tot: {"predicted": "positive", "median": -0.0976488299352429, "q25": -0.16659044701410178, "q75": -0.06714380831036806, "k_in_predicted_direction": 3, "n": 42, "sign_p": 0.9999999997944542, "supported": false}
- beta_absiota_tot: {"predicted": "negative", "median": -0.18741882354690031, "q25": -0.2478706784577529, "q75": -0.1318511932259871, "k_in_predicted_direction": 40, "n": 42, "sign_p": 2.0554580260068178e-10, "supported": true}
- beta_absnu_tot_descriptive: {"median": 0.08799874586365514, "frac_positive": 0.8333333333333334}
- beta1_absz_descriptive: {"median": 0.08171566646991384, "frac_positive": 1.0, "frac_negative": 0.0}
- beta1_absiota_descriptive: {"median": -0.01168957751494715, "frac_positive": 0.38095238095238093, "frac_negative": 0.6190476190476191}
- beta_shrink_descriptive: {"median": 1.0, "frac_positive": 1.0, "frac_negative": 0.0}

**Primário (ímpares, HXCLK → HXFB, McNemar unilateral, α=0,025):**

- hsic_5: só HXCLK 2, só HXFB 2, p=0.69 → n.s.
- hsic_1: só HXCLK 2, só HXFB 1, p=0.5 → n.s.

**HXFB pior que BL? (84 origens, α=0,05/12):**

- m11: só HXFB 3, só BL 5, p=0.86
- fr_cov: só HXFB 0, só BL 4, p=1
- energy: só HXFB 1, só BL 5, p=0.98
- lin_1: só HXFB 1, só BL 2, p=0.88
- lin_5: só HXFB 0, só BL 4, p=1
- lin_30: só HXFB 4, só BL 4, p=0.64
- vol_1: só HXFB 1, só BL 5, p=0.98
- vol_5: só HXFB 2, só BL 4, p=0.89
- vol_30: só HXFB 0, só BL 4, p=1
- hsic_1: só HXFB 4, só BL 2, p=0.34
- hsic_5: só HXFB 10, só BL 2, p=0.019
- hsic_30: só HXFB 6, só BL 2, p=0.14

**Veredito pré-registrado (84): EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)**
Veredito só nas ímpares: EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)

**Não piorar (HXFB × HXCLK, bilateral, α=0,05/12):**

- m11: só HXFB 4, só HXCLK 3, p=1
- fr_cov: só HXFB 2, só HXCLK 2, p=1
- energy: só HXFB 0, só HXCLK 6, p=0.031
- lin_1: só HXFB 2, só HXCLK 2, p=1
- lin_5: só HXFB 0, só HXCLK 5, p=0.062
- lin_30: só HXFB 0, só HXCLK 7, p=0.016
- vol_1: só HXFB 0, só HXCLK 1, p=1
- vol_5: só HXFB 1, só HXCLK 4, p=0.38
- vol_30: só HXFB 1, só HXCLK 1, p=1
- hsic_30: só HXFB 1, só HXCLK 10, p=0.012
