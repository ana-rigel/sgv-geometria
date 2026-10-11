# SGV-M21b — Dependência temporal no BTC 1m exploratório (resultados)

Origens válidas: 84 ({'valid': 84}). Gerado por `scripts/m21b_agregar.py`; protocolo em `reports/PROTOCOLO_SGV_M21b_20261011.md`.

| Nulo | lin_1 | lin_5 | lin_30 | vol_1 | vol_5 | vol_30 | hsic_1 | hsic_5 | hsic_30 |
|---|---|---|---|---|---|---|---|---|---|
| MS | 84.5% | 73.8% | 71.4% | 96.4% | 81.0% | 52.4% | 83.3% | 79.8% | 77.4% |
| MSDCCLM | 73.8% | 42.9% | 25.0% | 88.1% | 65.5% | 33.3% | 81.0% | 60.7% | 36.9% |
| BL | 10.7% | 14.3% | 13.1% | 9.5% | 7.1% | 9.5% | 9.5% | 10.7% | 15.5% |

| Contraste | só A | só B | p | sig. (α=0,0167) |
|---|---|---|---|---|
| P1_param_vs_BL_hsic_1 | 60 | 0 | 8.7e-19 | sim |
| P2_hsic_beyond_vol_1 | 3 | 9 | 0.98 | não |
| P2_hsic_beyond_lin_1 | 6 | 0 | 0.016 | sim |
| P1_param_vs_BL_hsic_5 | 42 | 0 | 2.3e-13 | sim |
| P2_hsic_beyond_vol_5 | 6 | 10 | 0.89 | não |
| P2_hsic_beyond_lin_5 | 15 | 0 | 3.1e-05 | sim |
| P1_param_vs_BL_hsic_30 | 18 | 0 | 3.8e-06 | sim |
| P2_hsic_beyond_vol_30 | 13 | 10 | 0.34 | não |
| P2_hsic_beyond_lin_30 | 10 | 0 | 0.00098 | sim |

**Veredito pré-registrado por defasagem:**

- lag 1: **dependencia nao reproduzida, compativel com memoria de volatilidade** (sanidade BL: ok)
- lag 5: **dependencia nao reproduzida, compativel com memoria de volatilidade** (sanidade BL: ok)
- lag 30: **dependencia nao reproduzida, compativel com memoria de volatilidade** (sanidade BL: FALHOU)
