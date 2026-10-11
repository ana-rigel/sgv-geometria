# SGV-M26 — Resiliência cruzada da volatilidade (resultados)

Origens válidas: 83 ({'valid': 83, 'fit_failed': 1}). Agregado por `experiments/m26_resiliencia_cruzada.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M26_20261011.md`.

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HARLMFX | 19% | 10% | 16% | 11% | 19% | 22% | 17% | 20% | 23% | 19% | 27% | 31% |
| HARLMFV | 14% | 17% | 13% | 11% | 19% | 25% | 19% | 29% | 28% | 17% | 28% | 30% |
| BL | 9% | 11% | 7% | 10% | 14% | 18% | 10% | 7% | 7% | 8% | 11% | 14% |

**Primário (HARLMFV → HARLMFX, McNemar unilateral, α=0,0167):**

- vol_1: só HARLMFV 3, só HARLMFX 1, p=0.31 → n.s.
- vol_5: só HARLMFV 9, só HARLMFX 2, p=0.033 → n.s.
- vol_30: só HARLMFV 7, só HARLMFX 3, p=0.17 → n.s.

**HARLMFX pior que BL? (α=0,05/12):**

- m11: só HARLMFX 8, só BL 0, p=0.0039 **(pior)**
- fr_cov: só HARLMFX 1, só BL 2, p=0.88
- energy: só HARLMFX 7, só BL 0, p=0.0078
- lin_1: só HARLMFX 2, só BL 1, p=0.5
- lin_5: só HARLMFX 5, só BL 1, p=0.11
- lin_30: só HARLMFX 5, só BL 2, p=0.23
- vol_1: só HARLMFX 6, só BL 0, p=0.016
- vol_5: só HARLMFX 11, só BL 0, p=0.00049 **(pior)**
- vol_30: só HARLMFX 13, só BL 0, p=0.00012 **(pior)**
- hsic_1: só HARLMFX 9, só BL 0, p=0.002 **(pior)**
- hsic_5: só HARLMFX 13, só BL 0, p=0.00012 **(pior)**
- hsic_30: só HARLMFX 14, só BL 0, p=6.1e-05 **(pior)**

**Veredito pré-registrado: NAO FECHA A LACUNA**

**Mecanismo (previsão pré-registrada: termo agressão←retorno negativo):** {"c_iota_from_z_median": -0.04700665767980568, "c_iota_from_z_negative_fraction": 1.0, "sign_test_p_negative": 1.0339757656912846e-25, "c_z_from_nu_median": 0.00971908990364292}
