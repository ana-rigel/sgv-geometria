# SGV-M18 — Acoplamento dinâmico × memória longa (resultados)

**Somente dados exploratórios.** Gerado por `scripts/m18_agregar.py`; protocolo e apostas congelados antes em `reports/PROTOCOLO_SGV_M18_20261010.md`. Origens consecutivas não são independentes (Wilson otimista).

## 1m (origens: {'valid': 84})

| Nulo | M11 (forma) | Fisher–Rao | Energy (memória) | Fecha a lacuna? |
|---|---|---|---|---|
| MS — 2 escalas, Markov (base M17) | 34.6% [25.1%–45.4%] (28/81) | 44.0% [33.9%–54.7%] (37/84) | 27.4% [19.0%–37.7%] (23/84) | não |
| MSDCC — MS + acoplamento dinâmico (DCC) | 25.9% [17.6%–36.4%] (21/81) | 38.1% [28.4%–48.8%] (32/84) | 29.8% [21.0%–40.2%] (25/84) | não |
| MSLM — MS + memória longa (bloco lento real) | 24.4% [16.2%–34.9%] (19/78) | 35.7% [26.3%–46.4%] (30/84) | 17.9% [11.1%–27.4%] (15/84) | não |
| MSDCCLM — MS + DCC + memória longa | 23.7% [15.5%–34.4%] (18/76) | 31.0% [22.1%–41.5%] (26/84) | 15.5% [9.3%–24.7%] (13/84) | não |
| BL — blocos longos reais (referência) | 10.5% [4.9%–21.1%] (6/57) | 9.5% [4.9%–17.7%] (8/84) | 9.5% [4.9%–17.7%] (8/84) | **sim** |
| N3 — M12 N3 (âncora) | 12.7% [7.0%–21.8%] (10/79) | 16.7% [10.2%–26.1%] (14/84) | 23.8% [16.0%–33.9%] (20/84) | não |

Contrastes pré-registrados (McNemar exato pareado unilateral, α = 0,0125 cada):

| Contraste | A | B | taxa A | taxa B | só A | só B | p | Significativo |
|---|---|---|---|---|---|---|---|---|
| D1_acoplamento_frcov | MS | MSDCC | 44.0% | 38.1% | 7 | 2 | 0.09 | não |
| D1_acoplamento_energy | MS | MSDCC | 27.4% | 29.8% | 1 | 3 | 0.94 | não |
| D2_memoria_longa_frcov | MS | MSLM | 44.0% | 35.7% | 9 | 2 | 0.033 | não |
| D2_memoria_longa_energy | MS | MSLM | 27.4% | 17.9% | 8 | 0 | 0.0039 | sim |

Diagnósticos de ajuste (descritivos):

```
{
 "dcc_a_quartiles": [
  0.006488477800171309,
  0.01391874146461488,
  0.020040406033396675
 ],
 "dcc_b_quartiles": [
  0.9337380771373859,
  0.9641090068817137,
  0.9923385532687821
 ],
 "dcc_nll_gain_quartiles": [
  21.807155854509148,
  33.64648441715927,
  41.271629404645964
 ],
 "dcc_gain_gt_3_fraction": 1.0
}
```

## 1h (origens: {'valid': 18})

| Nulo | M11 (forma) | Fisher–Rao | Energy (memória) | Fecha a lacuna? |
|---|---|---|---|---|
| MS — 2 escalas, Markov (base M17) | 11.8% [3.3%–34.3%] (2/17) | 33.3% [16.3%–56.3%] (6/18) | 44.4% [24.6%–66.3%] (8/18) | não |
| MSDCC — MS + acoplamento dinâmico (DCC) | 12.5% [3.5%–36.0%] (2/16) | 38.9% [20.3%–61.4%] (7/18) | 38.9% [20.3%–61.4%] (7/18) | não |
| MSLM — MS + memória longa (bloco lento real) | 5.9% [1.0%–27.0%] (1/17) | 27.8% [12.5%–50.9%] (5/18) | 33.3% [16.3%–56.3%] (6/18) | não |
| MSDCCLM — MS + DCC + memória longa | 11.8% [3.3%–34.3%] (2/17) | 50.0% [29.0%–71.0%] (9/18) | 33.3% [16.3%–56.3%] (6/18) | não |
| BL — blocos longos reais (referência) | 0.0% [0.0%–20.4%] (0/15) | 16.7% [5.8%–39.2%] (3/18) | 33.3% [16.3%–56.3%] (6/18) | não |
| N3 — M12 N3 (âncora) | 5.9% [1.0%–27.0%] (1/17) | 11.1% [3.1%–32.8%] (2/18) | 44.4% [24.6%–66.3%] (8/18) | não |

Contrastes pré-registrados (McNemar exato pareado unilateral, α = 0,0125 cada):

| Contraste | A | B | taxa A | taxa B | só A | só B | p | Significativo |
|---|---|---|---|---|---|---|---|---|
| D1_acoplamento_frcov | MS | MSDCC | 33.3% | 38.9% | 1 | 2 | 0.88 | não |
| D1_acoplamento_energy | MS | MSDCC | 44.4% | 38.9% | 2 | 1 | 0.5 | não |
| D2_memoria_longa_frcov | MS | MSLM | 33.3% | 27.8% | 1 | 0 | 0.5 | não |
| D2_memoria_longa_energy | MS | MSLM | 44.4% | 33.3% | 2 | 0 | 0.25 | não |

Diagnósticos de ajuste (descritivos):

```
{
 "dcc_a_quartiles": [
  0.004549002377004553,
  0.012057127058506008,
  0.01761380392751018
 ],
 "dcc_b_quartiles": [
  0.8680213640676807,
  0.9080444196164632,
  0.9939092528121564
 ],
 "dcc_nll_gain_quartiles": [
  7.634623988058384,
  13.552147387077436,
  14.85058227345343
 ],
 "dcc_gain_gt_3_fraction": 0.9444444444444444
}
```

