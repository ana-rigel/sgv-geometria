# SGV-M28 — A atividade governa a escala (resultados)

Origens válidas: 84 ({'valid': 84}); ímpares (teste): 42. Agregado por `experiments/m28_atividade_escala.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M28_20261011.md`.

**Todas as origens:**

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXACT | 9% | 6% | 11% | 11% | 15% | 18% | 6% | 12% | 7% | 17% | 25% | 27% |
| HXLOC | 11% | 10% | 11% | 11% | 17% | 24% | 7% | 11% | 7% | 13% | 26% | 31% |
| BL | 10% | 10% | 8% | 13% | 13% | 15% | 10% | 12% | 10% | 11% | 13% | 15% |

**Só ímpares (teste):**

| Nulo | m11 | fr_cov | energy | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HXACT | 10% | 10% | 14% | 12% | 19% | 21% | 10% | 19% | 5% | 21% | 29% | 33% |
| HXLOC | 10% | 14% | 10% | 12% | 14% | 24% | 10% | 12% | 7% | 14% | 26% | 31% |
| BL | 12% | 14% | 7% | 14% | 12% | 14% | 10% | 12% | 7% | 14% | 14% | 19% |

**Mecanismo (ímpares, teste do sinal unilateral):**

- gamma_iota: {"predicted": "negative", "median": -0.08441747512087071, "q25": -0.09898950626685829, "q75": -0.07116966624228578, "k_in_predicted_direction": 42, "n": 42, "sign_p": 2.2737367544323206e-13, "supported": true}
- gamma_z: {"predicted": "positive", "median": 0.043498806645350344, "q25": 0.02591504920038147, "q75": 0.060475640628427876, "k_in_predicted_direction": 41, "n": 42, "sign_p": 9.777068044058979e-12, "supported": true}
- gamma_nu_descriptive: {"median": -0.06831679649812716, "frac_positive": 0.0}

**Primário (ímpares, HXLOC → HXACT, McNemar unilateral, α=0,025):**

- hsic_5: só HXLOC 1, só HXACT 2, p=0.88 → n.s.
- hsic_30: só HXLOC 1, só HXACT 2, p=0.88 → n.s.

**HXACT pior que BL? (84 origens, α=0,05/12):**

- m11: só HXACT 2, só BL 3, p=0.81
- fr_cov: só HXACT 0, só BL 3, p=1
- energy: só HXACT 4, só BL 2, p=0.34
- lin_1: só HXACT 1, só BL 3, p=0.94
- lin_5: só HXACT 6, só BL 4, p=0.38
- lin_30: só HXACT 6, só BL 4, p=0.38
- vol_1: só HXACT 0, só BL 3, p=1
- vol_5: só HXACT 4, só BL 4, p=0.64
- vol_30: só HXACT 2, só BL 4, p=0.89
- hsic_1: só HXACT 6, só BL 1, p=0.062
- hsic_5: só HXACT 11, só BL 1, p=0.0032 **(pior)**
- hsic_30: só HXACT 11, só BL 1, p=0.0032 **(pior)**

**Veredito pré-registrado (84): NAO FECHA A LACUNA**
Veredito só nas ímpares: EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)

**Não piorar (HXACT × HXLOC, bilateral, α=0,05/12):**

- m11: só HXACT 1, só HXLOC 3, p=0.62
- fr_cov: só HXACT 0, só HXLOC 3, p=0.25
- energy: só HXACT 2, só HXLOC 2, p=1
- lin_1: só HXACT 2, só HXLOC 2, p=1
- lin_5: só HXACT 3, só HXLOC 4, p=1
- lin_30: só HXACT 1, só HXLOC 6, p=0.12
- vol_1: só HXACT 0, só HXLOC 1, p=1
- vol_5: só HXACT 5, só HXLOC 4, p=1
- vol_30: só HXACT 2, só HXLOC 2, p=1
- hsic_1: só HXACT 4, só HXLOC 1, p=0.38
