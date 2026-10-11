# SGV-M23 — Modelo mínimo do BTC 1m (resultados)

Origens válidas: 84 ({'valid': 84}). Agregado por `experiments/m23_modelo_minimo.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M23_20261011.md`.

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MSAR | 34% | 30% | 31% | 23% | 87% | 73% | 36% | 75% | 45% | 42% | 88% | 77% |
| MSARLM | 28% | 23% | 14% | 13% | 49% | 24% | 23% | 51% | 26% | 31% | 64% | 37% |
| MSDCCLM | 24% | 33% | 17% | 70% | 48% | 24% | 88% | 68% | 36% | 83% | 58% | 33% |
| BL | 11% | 7% | 7% | 10% | 12% | 15% | 10% | 8% | 11% | 12% | 13% | 15% |

**Primário (MSDCCLM → MSARLM, McNemar unilateral, α=0,0167):**

- lin_1: só MSDCCLM 48, só MSARLM 0, p=3.6e-15 → melhora significativa
- vol_1: só MSDCCLM 55, só MSARLM 0, p=2.8e-17 → melhora significativa
- hsic_1: só MSDCCLM 44, só MSARLM 0, p=5.7e-14 → melhora significativa

**MSARLM pior que BL? (α=0,05/12 por estatística)**

- m11: só MSARLM 14, só BL 0, p=6.1e-05 **(pior)**
- fr_cov: só MSARLM 13, só BL 0, p=0.00012 **(pior)**
- energy: só MSARLM 7, só BL 1, p=0.035
- lin_1: só MSARLM 3, só BL 0, p=0.12
- lin_5: só MSARLM 31, só BL 0, p=4.7e-10 **(pior)**
- lin_30: só MSARLM 8, só BL 1, p=0.02
- vol_1: só MSARLM 11, só BL 0, p=0.00049 **(pior)**
- vol_5: só MSARLM 36, só BL 0, p=1.5e-11 **(pior)**
- vol_30: só MSARLM 13, só BL 0, p=0.00012 **(pior)**
- hsic_1: só MSARLM 16, só BL 0, p=1.5e-05 **(pior)**
- hsic_5: só MSARLM 43, só BL 0, p=1.1e-13 **(pior)**
- hsic_30: só MSARLM 18, só BL 0, p=3.8e-06 **(pior)**

**Veredito pré-registrado: NAO FECHA A LACUNA**

Diagnósticos: {"garch_alpha_beta_median": [[0.10153590405154297, 0.6813424588047922], [0.03638559722388657, 0.9370592293011581], [0.039671059265780885, 0.9317696453923547]], "var_spectral_radius_quartiles": [0.2713480293491415, 0.34571479480641365, 0.4300675300586101]}
