# SGV-M27 — Não estacionariedade dos parâmetros (resultados)

Origens válidas: 84 ({'valid': 84}). Agregado por `experiments/m27_nao_estacionariedade.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M27_20261011.md`.

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXLOC | 11% | 8% | 8% | 7% | 18% | 21% | 8% | 10% | 7% | 17% | 27% | 27% |
| HXNOISE | 15% | 8% | 20% | 12% | 25% | 39% | 12% | 19% | 26% | 19% | 38% | 52% |
| HARLMFX | 18% | 14% | 18% | 12% | 20% | 26% | 18% | 21% | 21% | 19% | 30% | 31% |
| BL | 7% | 10% | 11% | 10% | 11% | 15% | 10% | 8% | 11% | 11% | 12% | 14% |

**Primário A (HARLMFX → HXLOC), McNemar unilateral, α=0,0125:**

- vol_5: só HARLMFX 10, só HXLOC 0, p=0.00098 → significativo
- vol_30: só HARLMFX 12, só HXLOC 0, p=0.00024 → significativo
- hsic_5: só HARLMFX 6, só HXLOC 4, p=0.38 → n.s.
- hsic_30: só HARLMFX 5, só HXLOC 2, p=0.23 → n.s.

**Primário B (HXNOISE → HXLOC), McNemar unilateral, α=0,0125:**

- vol_5: só HXNOISE 9, só HXLOC 1, p=0.011 → significativo
- vol_30: só HXNOISE 16, só HXLOC 0, p=1.5e-05 → significativo
- hsic_5: só HXNOISE 10, só HXLOC 1, p=0.0059 → significativo
- hsic_30: só HXNOISE 22, só HXLOC 1, p=2.9e-06 → significativo

**Descritivo: ruído sozinho (HARLMFX → HXNOISE), McNemar unilateral, α=0,0125:**

- vol_5: só HARLMFX 4, só HXNOISE 2, p=0.34 → n.s.
- vol_30: só HARLMFX 5, só HXNOISE 9, p=0.91 → n.s.
- hsic_5: só HARLMFX 2, só HXNOISE 9, p=0.99 → n.s.
- hsic_30: só HARLMFX 0, só HXNOISE 18, p=1 → n.s.

**Leitura pré-registrada: NAO ESTACIONARIEDADE APOIADA em vol_5, vol_30**

**HXLOC pior que BL? (α=0,05/12):**

- m11: só HXLOC 3, só BL 0, p=0.12
- fr_cov: só HXLOC 1, só BL 2, p=0.88
- energy: só HXLOC 0, só BL 2, p=1
- lin_1: só HXLOC 1, só BL 3, p=0.94
- lin_5: só HXLOC 6, só BL 0, p=0.016
- lin_30: só HXLOC 6, só BL 1, p=0.062
- vol_1: só HXLOC 2, só BL 3, p=0.81
- vol_5: só HXLOC 3, só BL 2, p=0.5
- vol_30: só HXLOC 1, só BL 4, p=0.97
- hsic_1: só HXLOC 8, só BL 3, p=0.11
- hsic_5: só HXLOC 14, só BL 1, p=0.00049 **(pior)**
- hsic_30: só HXLOC 12, só BL 1, p=0.0017 **(pior)**

**Veredito pré-registrado: NAO FECHA A LACUNA**

**Dispersão dos parâmetros entre trechos (real × sintético):**

| parâmetro | mediana real | mediana sintético | fração real > sintético | p (sinal) |
|---|---|---|---|---|
| varpers_z | 0.178 | 0.170 | 50% | 0.54 |
| varpers_nu | 0.170 | 0.141 | 64% | 0.0058 |
| c_iota_from_z | 0.023 | 0.021 | 65% | 0.003 |
| ar1_nu | 0.060 | 0.047 | 73% | 2e-05 |
| harpers_nu | 0.141 | 0.118 | 52% | 0.37 |
