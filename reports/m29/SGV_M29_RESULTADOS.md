# SGV-M29 — O relógio do volume (resultados)

Origens válidas: 84 ({'valid': 84}); ímpares (teste): 42. Agregado por `experiments/m29_relogio_volume.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M29_20261012.md`.

**Todas as origens:**

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXCLK | 10% | 6% | 7% | 8% | 17% | 21% | 8% | 10% | 6% | 17% | 24% | 21% |
| HXACT | 5% | 5% | 12% | 7% | 18% | 23% | 6% | 11% | 8% | 14% | 25% | 29% |
| BL | 10% | 11% | 8% | 10% | 13% | 13% | 10% | 10% | 10% | 10% | 11% | 13% |

**Só ímpares (teste):**

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXCLK | 10% | 10% | 7% | 10% | 17% | 21% | 10% | 12% | 2% | 19% | 24% | 24% |
| HXACT | 5% | 7% | 10% | 7% | 19% | 21% | 7% | 14% | 10% | 12% | 26% | 31% |
| BL | 12% | 14% | 10% | 10% | 12% | 12% | 10% | 10% | 5% | 10% | 10% | 17% |

**Primário (ímpares, HXACT → HXCLK, McNemar unilateral, α=0,025):**

- hsic_5: só HXACT 2, só HXCLK 1, p=0.5 → n.s.
- hsic_30: só HXACT 4, só HXCLK 1, p=0.19 → n.s.

**HXCLK pior que BL? (84 origens, α=0,05/12):**

- m11: só HXCLK 2, só BL 2, p=0.69
- fr_cov: só HXCLK 0, só BL 4, p=1
- energy: só HXCLK 4, só BL 5, p=0.75
- lin_1: só HXCLK 2, só BL 3, p=0.81
- lin_5: só HXCLK 6, só BL 3, p=0.25
- lin_30: só HXCLK 8, só BL 1, p=0.02
- vol_1: só HXCLK 3, só BL 4, p=0.77
- vol_5: só HXCLK 3, só BL 3, p=0.66
- vol_30: só HXCLK 0, só BL 3, p=1
- hsic_1: só HXCLK 6, só BL 0, p=0.016
- hsic_5: só HXCLK 11, só BL 0, p=0.00049 **(pior)**
- hsic_30: só HXCLK 7, só BL 0, p=0.0078

**Veredito pré-registrado (84): NAO FECHA A LACUNA**
Veredito só nas ímpares: EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)

**Não piorar (HXCLK × HXACT, bilateral, α=0,05/12):**

- m11: só HXCLK 5, só HXACT 1, p=0.22
- fr_cov: só HXCLK 1, só HXACT 0, p=1
- energy: só HXCLK 1, só HXACT 5, p=0.22
- lin_1: só HXCLK 1, só HXACT 0, p=1
- lin_5: só HXCLK 3, só HXACT 4, p=1
- lin_30: só HXCLK 2, só HXACT 3, p=1
- vol_1: só HXCLK 2, só HXACT 0, p=0.5
- vol_5: só HXCLK 5, só HXACT 6, p=1
- vol_30: só HXCLK 2, só HXACT 4, p=0.69
- hsic_1: só HXCLK 3, só HXACT 1, p=0.62

**Mecanismo (descritivo, ímpares):** {"frac_argmax_00_shrunk": 0.8095238095238095, "frac_argmax_00_raw": 0.8095238095238095, "shrink_median": 0.5901650290362994, "frac_shrink_zero": 0.0, "sign_p_argmax_00_majority": 3.438555745560735e-05, "corr_with_even_diag_median": 0.7061208165586621}
