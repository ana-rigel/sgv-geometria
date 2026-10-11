# SGV-M24 — HAR + inovações históricas filtradas (resultados)

Origens válidas: 81 ({'fit_failed': 3, 'valid': 81}). Agregado por `experiments/m24_har_fhs.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M24_20261011.md`.

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HARLM | 30% | 21% | 14% | 14% | 23% | 28% | 27% | 28% | 33% | 30% | 43% | 42% |
| HARLMF | 18% | 17% | 15% | 12% | 22% | 27% | 22% | 25% | 31% | 22% | 32% | 36% |
| MSARLM | 33% | 25% | 16% | 15% | 51% | 22% | 26% | 52% | 30% | 35% | 60% | 33% |
| BL | 8% | 11% | 10% | 7% | 14% | 16% | 9% | 10% | 9% | 11% | 11% | 15% |

**Primário (MSARLM → HARLMF, McNemar unilateral, α=0,0125):**

- lin_5: só MSARLM 23, só HARLMF 0, p=1.2e-07 → melhora significativa
- vol_5: só MSARLM 22, só HARLMF 0, p=2.4e-07 → melhora significativa
- hsic_5: só MSARLM 23, só HARLMF 0, p=1.2e-07 → melhora significativa
- m11: só MSARLM 12, só HARLMF 0, p=0.00024 → melhora significativa

**HARLMF pior que BL? (α=0,05/12):**

- m11: só HARLMF 8, só BL 0, p=0.0039 **(pior)**
- fr_cov: só HARLMF 5, só BL 0, p=0.031
- energy: só HARLMF 5, só BL 1, p=0.11
- lin_1: só HARLMF 5, só BL 1, p=0.11
- lin_5: só HARLMF 8, só BL 1, p=0.02
- lin_30: só HARLMF 10, só BL 1, p=0.0059
- vol_1: só HARLMF 11, só BL 0, p=0.00049 **(pior)**
- vol_5: só HARLMF 12, só BL 0, p=0.00024 **(pior)**
- vol_30: só HARLMF 18, só BL 0, p=3.8e-06 **(pior)**
- hsic_1: só HARLMF 9, só BL 0, p=0.002 **(pior)**
- hsic_5: só HARLMF 17, só BL 0, p=7.6e-06 **(pior)**
- hsic_30: só HARLMF 17, só BL 0, p=7.6e-06 **(pior)**

**Efeito das inovações reais (HARLM → HARLMF), descritivo:**

- m11: só HARLM 10, só HARLMF 0, p=0.00098
- fr_cov: só HARLM 4, só HARLMF 1, p=0.19
- energy: só HARLM 1, só HARLMF 2, p=0.88
- lin_1: só HARLM 1, só HARLMF 0, p=0.5
- lin_5: só HARLM 2, só HARLMF 1, p=0.5
- lin_30: só HARLM 2, só HARLMF 1, p=0.5
- vol_1: só HARLM 5, só HARLMF 1, p=0.11
- vol_5: só HARLM 4, só HARLMF 1, p=0.19
- vol_30: só HARLM 5, só HARLMF 3, p=0.36
- hsic_1: só HARLM 6, só HARLMF 0, p=0.016
- hsic_5: só HARLM 9, só HARLMF 0, p=0.002
- hsic_30: só HARLM 6, só HARLMF 1, p=0.062

**Veredito pré-registrado: NAO FECHA A LACUNA**

Diagnósticos: {"z_excess_kurtosis_median": [-0.0664709776048551, 0.1659068516419988, 0.5556371022582423], "companion_radius_quartiles": [0.9771728804834431, 0.9809645601081438, 0.9837311130697106], "shrink_applied_fraction": 0.0}
