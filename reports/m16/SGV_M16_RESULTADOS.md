# SGV-M16 — Três réguas sobre os nulos N0–N3 no BTC exploratório (resultados)

**Somente dados exploratórios** (1m mai–jul/2026; 1h 2020–2024). Gerado por `scripts/m16_agregar.py`; protocolo e apostas congelados antes em `reports/PROTOCOLO_SGV_M16_20261010.md`.

Alarme = observado acima de ≥38 das 39 referências (nominal 5%; sob família correta ajustada o M11 dá ~7%, M14/M15). **Origens consecutivas não são independentes: os intervalos de Wilson são otimistas.**

## 1m  (origens: {'valid': 84})

| Nulo | M11 (forma) | Fisher–Rao cov. | Energy | Classificação pré-registrada |
|---|---|---|---|---|
| N0_stationary | 29.3% [20.5%–39.9%] (24/82) | 42.9% [32.8%–53.5%] (36/84) | 72.6% [62.3%–81.0%] (61/84) | **falta memoria/massa (energy > m11)** (m11>E p=1; E>m11 p=3.9e-08) |
| N1_SF1_M5 | 36.6% [27.0%–47.4%] (30/82) | 53.6% [43.0%–63.8%] (45/84) | 34.5% [25.2%–45.2%] (29/84) | **inadequado, tipo indefinido** (m11>E p=0.43; E>m11 p=0.71) |
| N2_regime_short | 18.5% [11.6%–28.3%] (15/81) | 25.0% [17.0%–35.2%] (21/84) | 46.4% [36.2%–57.0%] (39/84) | **falta memoria/massa (energy > m11)** (m11>E p=1; E>m11 p=5.8e-05) |
| N3_regime_long | 10.3% [5.3%–19.0%] (8/78) | 17.9% [11.1%–27.4%] (15/84) | 23.8% [16.0%–33.9%] (20/84) | **inadequado, tipo indefinido** (m11>E p=0.99; E>m11 p=0.026) |

Postos em 8 faixas de 5 posições (faixa 1 = observado no topo; plano ≈ adequado):

- `N0_stationary | m11`: [41, 12, 11, 5, 3, 4, 3, 3] (PIT médio 0.25)
- `N0_stationary | fr_cov`: [50, 12, 5, 6, 5, 2, 2, 2] (PIT médio 0.20)
- `N0_stationary | energy`: [70, 5, 0, 4, 3, 1, 0, 1] (PIT médio 0.10)
- `N1_SF1_M5 | m11`: [38, 14, 13, 4, 4, 6, 1, 2] (PIT médio 0.23)
- `N1_SF1_M5 | fr_cov`: [60, 7, 9, 3, 1, 2, 1, 1] (PIT médio 0.15)
- `N1_SF1_M5 | energy`: [42, 10, 6, 7, 4, 4, 5, 6] (PIT médio 0.28)
- `N2_regime_short | m11`: [21, 15, 5, 14, 7, 7, 5, 7] (PIT médio 0.39)
- `N2_regime_short | fr_cov`: [34, 8, 6, 11, 9, 5, 7, 4] (PIT médio 0.34)
- `N2_regime_short | energy`: [49, 8, 4, 4, 5, 4, 2, 8] (PIT médio 0.26)
- `N3_regime_long | m11`: [16, 11, 5, 13, 8, 6, 8, 11] (PIT médio 0.47)
- `N3_regime_long | fr_cov`: [18, 12, 10, 7, 8, 9, 13, 7] (PIT médio 0.44)
- `N3_regime_long | energy`: [35, 8, 7, 13, 4, 5, 6, 6] (PIT médio 0.33)

## 1h  (origens: {'valid': 18})

| Nulo | M11 (forma) | Fisher–Rao cov. | Energy | Classificação pré-registrada |
|---|---|---|---|---|
| N0_stationary | 17.6% [6.2%–41.0%] (3/17) | 27.8% [12.5%–50.9%] (5/18) | 55.6% [33.7%–75.4%] (10/18) | **inadequado, tipo indefinido** (m11>E p=1; E>m11 p=0.035) |
| N1_SF1_M5 | 6.7% [1.2%–29.8%] (1/15) | 17.6% [6.2%–41.0%] (3/17) | 29.4% [13.3%–53.1%] (5/17) | **inadequado, tipo indefinido** (m11>E p=1; E>m11 p=0.062) |
| N2_regime_short | 11.8% [3.3%–34.3%] (2/17) | 22.2% [9.0%–45.2%] (4/18) | 55.6% [33.7%–75.4%] (10/18) | **inadequado, tipo indefinido** (m11>E p=1; E>m11 p=0.02) |
| N3_regime_long | 6.2% [1.1%–28.3%] (1/16) | 11.1% [3.1%–32.8%] (2/18) | 38.9% [20.3%–61.4%] (7/18) | **inadequado, tipo indefinido** (m11>E p=1; E>m11 p=0.062) |

Postos em 8 faixas de 5 posições (faixa 1 = observado no topo; plano ≈ adequado):

- `N0_stationary | m11`: [4, 1, 2, 1, 3, 4, 1, 1] (PIT médio 0.46)
- `N0_stationary | fr_cov`: [8, 5, 0, 1, 1, 1, 1, 1] (PIT médio 0.28)
- `N0_stationary | energy`: [13, 1, 2, 0, 0, 0, 1, 1] (PIT médio 0.18)
- `N1_SF1_M5 | m11`: [1, 1, 0, 2, 3, 2, 3, 3] (PIT médio 0.64)
- `N1_SF1_M5 | fr_cov`: [5, 2, 4, 1, 2, 2, 0, 1] (PIT médio 0.35)
- `N1_SF1_M5 | energy`: [10, 1, 2, 1, 0, 1, 2, 0] (PIT médio 0.25)
- `N2_regime_short | m11`: [3, 2, 3, 2, 3, 1, 2, 1] (PIT médio 0.44)
- `N2_regime_short | fr_cov`: [8, 3, 3, 1, 0, 2, 1, 0] (PIT médio 0.27)
- `N2_regime_short | energy`: [11, 3, 1, 1, 0, 0, 2, 0] (PIT médio 0.18)
- `N3_regime_long | m11`: [2, 2, 1, 2, 1, 3, 3, 2] (PIT médio 0.54)
- `N3_regime_long | fr_cov`: [6, 1, 2, 3, 3, 0, 2, 1] (PIT médio 0.40)
- `N3_regime_long | energy`: [10, 3, 1, 0, 2, 0, 2, 0] (PIT médio 0.25)

## Linha do tempo dos alarmes (exploração descritiva, sem teste)

| Intervalo | Origem | Janela | Alarmes (nulo: réguas) |
|---|---|---|---|
| 1m | 0 | 2026-05-04T11:20 → 2026-05-05T12:19 | N0_stationary: energy; N2_regime_short: energy |
| 1m | 1 | 2026-05-05T12:20 → 2026-05-06T13:19 | — |
| 1m | 2 | 2026-05-06T13:20 → 2026-05-07T14:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: energy; N3_regime_long: energy |
| 1m | 3 | 2026-05-07T14:20 → 2026-05-08T15:19 | N0_stationary: m11,energy; N1_SF1_M5: m11 |
| 1m | 4 | 2026-05-08T15:20 → 2026-05-09T16:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11; N3_regime_long: m11,fr_cov |
| 1m | 5 | 2026-05-09T16:20 → 2026-05-10T17:19 | N0_stationary: energy |
| 1m | 6 | 2026-05-10T17:20 → 2026-05-11T18:19 | — |
| 1m | 7 | 2026-05-11T18:20 → 2026-05-12T19:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: m11,fr_cov |
| 1m | 8 | 2026-05-12T19:20 → 2026-05-13T20:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
| 1m | 9 | 2026-05-13T20:20 → 2026-05-14T21:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov,energy |
| 1m | 10 | 2026-05-14T21:20 → 2026-05-15T22:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov,energy |
| 1m | 11 | 2026-05-15T22:20 → 2026-05-16T23:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: m11,fr_cov,energy; N3_regime_long: m11,fr_cov,energy |
| 1m | 12 | 2026-05-16T23:20 → 2026-05-18T00:19 | N1_SF1_M5: m11 |
| 1m | 13 | 2026-05-18T00:20 → 2026-05-19T01:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: energy; N2_regime_short: energy; N3_regime_long: energy |
| 1m | 14 | 2026-05-19T01:20 → 2026-05-20T02:19 | N0_stationary: energy; N2_regime_short: energy |
| 1m | 15 | 2026-05-20T02:20 → 2026-05-21T03:19 | N0_stationary: energy |
| 1m | 16 | 2026-05-21T03:20 → 2026-05-22T04:19 | N0_stationary: energy; N1_SF1_M5: energy; N2_regime_short: energy; N3_regime_long: energy |
| 1m | 17 | 2026-05-22T04:20 → 2026-05-23T05:19 | N0_stationary: energy |
| 1m | 18 | 2026-05-23T05:20 → 2026-05-24T06:19 | N0_stationary: energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: energy |
| 1m | 19 | 2026-05-24T06:20 → 2026-05-25T07:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov; N2_regime_short: fr_cov; N3_regime_long: fr_cov |
| 1m | 20 | 2026-05-25T07:20 → 2026-05-26T08:19 | N0_stationary: energy |
| 1m | 21 | 2026-05-26T08:20 → 2026-05-27T09:19 | N0_stationary: energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: m11,energy; N3_regime_long: energy |
| 1m | 22 | 2026-05-27T09:20 → 2026-05-28T10:19 | N0_stationary: m11,fr_cov; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11 |
| 1m | 23 | 2026-05-28T10:20 → 2026-05-29T11:19 | N0_stationary: m11,fr_cov; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11,fr_cov; N3_regime_long: m11,fr_cov |
| 1m | 24 | 2026-05-29T11:20 → 2026-05-30T12:19 | N0_stationary: m11,energy; N1_SF1_M5: m11,energy |
| 1m | 25 | 2026-05-30T12:20 → 2026-05-31T13:19 | N1_SF1_M5: m11 |
| 1m | 26 | 2026-05-31T13:20 → 2026-06-01T14:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov |
| 1m | 27 | 2026-06-01T14:20 → 2026-06-02T15:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov |
| 1m | 28 | 2026-06-02T15:20 → 2026-06-03T16:19 | N0_stationary: energy |
| 1m | 29 | 2026-06-03T16:20 → 2026-06-04T17:19 | N0_stationary: energy |
| 1m | 30 | 2026-06-04T17:20 → 2026-06-05T18:19 | N0_stationary: m11,energy; N1_SF1_M5: m11; N2_regime_short: m11,energy; N3_regime_long: m11 |
| 1m | 31 | 2026-06-05T18:20 → 2026-06-06T19:19 | — |
| 1m | 32 | 2026-06-06T19:20 → 2026-06-07T20:19 | N0_stationary: energy |
| 1m | 33 | 2026-06-07T20:20 → 2026-06-08T21:19 | — |
| 1m | 34 | 2026-06-08T21:20 → 2026-06-09T22:19 | N0_stationary: energy; N1_SF1_M5: fr_cov; N2_regime_short: fr_cov |
| 1m | 35 | 2026-06-09T22:20 → 2026-06-10T23:19 | N0_stationary: m11; N1_SF1_M5: m11; N2_regime_short: m11 |
| 1m | 36 | 2026-06-10T23:20 → 2026-06-12T00:19 | N1_SF1_M5: m11 |
| 1m | 37 | 2026-06-12T00:20 → 2026-06-13T01:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov |
| 1m | 38 | 2026-06-13T01:20 → 2026-06-14T02:19 | N0_stationary: fr_cov |
| 1m | 39 | 2026-06-14T02:20 → 2026-06-15T03:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11 |
| 1m | 40 | 2026-06-15T03:20 → 2026-06-16T04:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: energy; N3_regime_long: energy |
| 1m | 41 | 2026-06-16T04:20 → 2026-06-17T05:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov |
| 1m | 42 | 2026-06-17T05:20 → 2026-06-18T06:19 | N0_stationary: m11,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: m11,energy; N3_regime_long: m11 |
| 1m | 43 | 2026-06-18T06:20 → 2026-06-19T07:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov,energy |
| 1m | 44 | 2026-06-19T07:20 → 2026-06-20T08:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov; N2_regime_short: fr_cov |
| 1m | 45 | 2026-06-20T08:20 → 2026-06-21T09:19 | N1_SF1_M5: fr_cov |
| 1m | 46 | 2026-06-21T09:20 → 2026-06-22T10:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11,fr_cov,energy; N3_regime_long: m11,fr_cov |
| 1m | 47 | 2026-06-22T10:20 → 2026-06-23T11:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
| 1m | 48 | 2026-06-23T11:20 → 2026-06-24T12:19 | — |
| 1m | 49 | 2026-06-24T12:20 → 2026-06-25T13:19 | — |
| 1m | 50 | 2026-06-25T13:20 → 2026-06-26T14:19 | — |
| 1m | 51 | 2026-06-26T14:20 → 2026-06-27T15:19 | N0_stationary: energy |
| 1m | 52 | 2026-06-27T15:20 → 2026-06-28T16:19 | N0_stationary: fr_cov; N1_SF1_M5: fr_cov |
| 1m | 53 | 2026-06-28T16:20 → 2026-06-29T17:19 | N0_stationary: m11 |
| 1m | 54 | 2026-06-29T17:20 → 2026-06-30T18:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov; N2_regime_short: energy |
| 1m | 55 | 2026-06-30T18:20 → 2026-07-01T19:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: energy |
| 1m | 56 | 2026-07-01T19:20 → 2026-07-02T20:19 | — |
| 1m | 57 | 2026-07-02T20:20 → 2026-07-03T21:19 | N1_SF1_M5: fr_cov |
| 1m | 58 | 2026-07-03T21:20 → 2026-07-04T22:19 | N0_stationary: energy; N1_SF1_M5: energy; N2_regime_short: energy |
| 1m | 59 | 2026-07-04T22:20 → 2026-07-05T23:19 | N0_stationary: m11,energy; N1_SF1_M5: m11; N2_regime_short: m11,energy |
| 1m | 60 | 2026-07-05T23:20 → 2026-07-07T00:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,energy; N2_regime_short: energy; N3_regime_long: energy |
| 1m | 61 | 2026-07-07T00:20 → 2026-07-08T01:19 | N0_stationary: m11,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: energy |
| 1m | 62 | 2026-07-08T01:20 → 2026-07-09T02:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov,energy |
| 1m | 63 | 2026-07-09T02:20 → 2026-07-10T03:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov |
| 1m | 64 | 2026-07-10T03:20 → 2026-07-11T04:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov,energy |
| 1m | 65 | 2026-07-11T04:20 → 2026-07-12T05:19 | N0_stationary: m11; N1_SF1_M5: m11 |
| 1m | 66 | 2026-07-12T05:20 → 2026-07-13T06:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy |
| 1m | 67 | 2026-07-13T06:20 → 2026-07-14T07:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
| 1m | 68 | 2026-07-14T07:20 → 2026-07-15T08:19 | N1_SF1_M5: fr_cov |
| 1m | 69 | 2026-07-15T08:20 → 2026-07-16T09:19 | — |
| 1m | 70 | 2026-07-16T09:20 → 2026-07-17T10:19 | N0_stationary: m11,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: m11,energy; N3_regime_long: energy |
| 1m | 71 | 2026-07-17T10:20 → 2026-07-18T11:19 | N0_stationary: energy |
| 1m | 72 | 2026-07-18T11:20 → 2026-07-19T12:19 | — |
| 1m | 73 | 2026-07-19T12:20 → 2026-07-20T13:19 | N0_stationary: energy |
| 1m | 74 | 2026-07-20T13:20 → 2026-07-21T14:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov; N2_regime_short: energy |
| 1m | 75 | 2026-07-21T14:20 → 2026-07-22T15:19 | N0_stationary: m11,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: m11,energy; N3_regime_long: m11,energy |
| 1m | 76 | 2026-07-22T15:20 → 2026-07-23T16:19 | N0_stationary: energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: energy; N3_regime_long: energy |
| 1m | 77 | 2026-07-23T16:20 → 2026-07-24T17:19 | N0_stationary: energy |
| 1m | 78 | 2026-07-24T17:20 → 2026-07-25T18:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11,fr_cov; N3_regime_long: m11,fr_cov |
| 1m | 79 | 2026-07-25T18:20 → 2026-07-26T19:19 | N0_stationary: energy; N2_regime_short: energy |
| 1m | 80 | 2026-07-26T19:20 → 2026-07-27T20:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov; N2_regime_short: m11,energy |
| 1m | 81 | 2026-07-27T20:20 → 2026-07-28T21:19 | N0_stationary: energy; N1_SF1_M5: fr_cov; N2_regime_short: energy |
| 1m | 82 | 2026-07-28T21:20 → 2026-07-29T22:19 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: fr_cov,energy |
| 1m | 83 | 2026-07-29T22:20 → 2026-07-30T23:19 | N0_stationary: fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
| 1h | 0 | 2022-03-30T02:00 → 2022-05-11T01:00 | N0_stationary: m11,fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
| 1h | 1 | 2022-05-11T02:00 → 2022-06-22T01:00 | N0_stationary: energy; N1_SF1_M5: energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
| 1h | 2 | 2022-06-22T02:00 → 2022-08-03T01:00 | N0_stationary: fr_cov |
| 1h | 3 | 2022-08-03T02:00 → 2022-09-14T01:00 | N0_stationary: energy; N2_regime_short: energy |
| 1h | 4 | 2022-09-14T02:00 → 2022-10-26T01:00 | N0_stationary: energy; N2_regime_short: energy; N3_regime_long: energy |
| 1h | 5 | 2022-10-26T02:00 → 2022-12-07T01:00 | N0_stationary: m11,fr_cov; N1_SF1_M5: fr_cov; N2_regime_short: m11,fr_cov; N3_regime_long: fr_cov |
| 1h | 6 | 2022-12-07T02:00 → 2023-01-18T01:00 | N0_stationary: energy; N1_SF1_M5: energy; N2_regime_short: energy; N3_regime_long: energy |
| 1h | 7 | 2023-01-18T02:00 → 2023-03-01T01:00 | — |
| 1h | 8 | 2023-09-27T03:00 → 2023-11-08T02:00 | — |
| 1h | 9 | 2023-11-08T03:00 → 2023-12-20T02:00 | — |
| 1h | 10 | 2023-12-20T03:00 → 2024-01-31T02:00 | N0_stationary: m11,fr_cov,energy; N1_SF1_M5: m11,fr_cov,energy; N2_regime_short: m11,energy; N3_regime_long: m11,fr_cov,energy |
| 1h | 11 | 2024-01-31T03:00 → 2024-03-13T02:00 | N0_stationary: energy; N1_SF1_M5: energy; N2_regime_short: energy |
| 1h | 12 | 2024-03-13T03:00 → 2024-04-24T02:00 | — |
| 1h | 13 | 2024-04-24T03:00 → 2024-06-05T02:00 | — |
| 1h | 14 | 2024-06-05T03:00 → 2024-07-17T02:00 | N0_stationary: energy; N2_regime_short: energy |
| 1h | 15 | 2024-07-17T03:00 → 2024-08-28T02:00 | N0_stationary: energy; N2_regime_short: energy; N3_regime_long: energy |
| 1h | 16 | 2024-08-28T03:00 → 2024-10-09T02:00 | — |
| 1h | 17 | 2024-10-09T03:00 → 2024-11-20T02:00 | N0_stationary: fr_cov,energy; N1_SF1_M5: fr_cov,energy; N2_regime_short: fr_cov,energy; N3_regime_long: energy |
