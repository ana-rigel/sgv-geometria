# SGV-M25 — Volatilidade multiescala (resultados)

Origens válidas: 84 ({'valid': 84}). Agregado por `experiments/m25_vol_multiescala.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M25_20261011.md`.

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HARLMFV | 16% | 17% | 19% | 13% | 17% | 23% | 19% | 30% | 27% | 19% | 29% | 30% |
| HARLMF | 15% | 20% | 13% | 12% | 21% | 26% | 23% | 29% | 26% | 23% | 31% | 33% |
| BL | 6% | 10% | 11% | 12% | 13% | 13% | 10% | 10% | 10% | 13% | 13% | 15% |

**Primário (HARLMF → HARLMFV, McNemar unilateral, α=0,0167):**

- vol_1: só HARLMF 5, só HARLMFV 2, p=0.23 → n.s.
- vol_5: só HARLMF 6, só HARLMFV 7, p=0.71 → n.s.
- vol_30: só HARLMF 5, só HARLMFV 6, p=0.73 → n.s.

**HARLMFV pior que BL? (α=0,05/12):**

- m11: só HARLMFV 9, só BL 1, p=0.011
- fr_cov: só HARLMFV 6, só BL 0, p=0.016
- energy: só HARLMFV 7, só BL 0, p=0.0078
- lin_1: só HARLMFV 2, só BL 1, p=0.5
- lin_5: só HARLMFV 4, só BL 1, p=0.19
- lin_30: só HARLMFV 9, só BL 1, p=0.011
- vol_1: só HARLMFV 8, só BL 0, p=0.0039 **(pior)**
- vol_5: só HARLMFV 17, só BL 0, p=7.6e-06 **(pior)**
- vol_30: só HARLMFV 15, só BL 0, p=3.1e-05 **(pior)**
- hsic_1: só HARLMFV 5, só BL 0, p=0.031
- hsic_5: só HARLMFV 13, só BL 0, p=0.00012 **(pior)**
- hsic_30: só HARLMFV 12, só BL 0, p=0.00024 **(pior)**

**Veredito pré-registrado: NAO FECHA A LACUNA**

Diagnósticos: {"harch_a1_median_z_iota_nu": [0.11088379488200537, 0.05434149584355988, 0.07028433961294894], "harch_a15_median_z_iota_nu": [0.05726310683322541, 0.0587143162083589, 0.0800224421706082], "harch_a60_median_z_iota_nu": [3.66371427314983e-08, 0.08391013404132874, 0.09915892185931491], "harch_a240_median_z_iota_nu": [6.506922526117687e-07, 0.09318551874279613, 0.10033150467143576], "harch_b_median_z_iota_nu": [0.5234960870573928, 0.5464070468527791, 0.4482448207399351]}
