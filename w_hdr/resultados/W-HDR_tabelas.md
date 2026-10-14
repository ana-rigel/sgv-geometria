## Parte A — taxa de detecção (limiar q95 dos nulos de calibração; 30 alternativas por célula)

| Mecanismo | k | M11-I distância | M11-I |ΔD| | W₂ completo | W₂-HDR | MMD² |
|---|---|---|---|---|---|---|
| translacao | 0.25 | 0.07 | 0.07 | 0.03 | 0.10 | 0.27 |
| translacao | 0.50 | 0.13 | 0.07 | 0.20 | 0.63 | 0.97 |
| translacao | 0.75 | 0.03 | 0.07 | 0.40 | 0.83 | 0.97 |
| translacao | 1.00 | 0.07 | 0.03 | 0.67 | 0.93 | 1.00 |
| escala | 0.25 | 0.07 | 0.07 | 0.17 | 0.13 | 0.33 |
| escala | 0.50 | 0.13 | 0.07 | 0.23 | 0.20 | 0.63 |
| escala | 0.75 | 0.13 | 0.07 | 0.33 | 0.37 | 0.97 |
| escala | 1.00 | 0.10 | 0.07 | 0.47 | 0.70 | 1.00 |
| rotacao | 0.25 | 0.10 | 0.07 | 0.17 | 0.17 | 0.03 |
| rotacao | 0.50 | 0.17 | 0.07 | 0.27 | 0.10 | 0.07 |
| rotacao | 0.75 | 0.17 | 0.07 | 0.23 | 0.27 | 0.23 |
| rotacao | 1.00 | 0.10 | 0.10 | 0.13 | 0.20 | 0.37 |
| bimodal | 0.25 | 0.40 | 0.10 | 0.07 | 0.30 | 0.23 |
| bimodal | 0.50 | 0.20 | 0.03 | 0.03 | 0.23 | 0.10 |
| bimodal | 0.75 | 0.37 | 0.13 | 0.17 | 0.20 | 0.17 |
| bimodal | 1.00 | 0.70 | 0.67 | 0.20 | 0.87 | 0.27 |
| curvatura | 0.25 | 0.10 | 0.10 | 0.13 | 0.10 | 0.13 |
| curvatura | 0.50 | 0.40 | 0.20 | 0.33 | 0.43 | 0.37 |
| curvatura | 0.75 | 0.67 | 0.43 | 0.47 | 0.70 | 0.57 |
| curvatura | 1.00 | 0.77 | 0.53 | 0.53 | 0.87 | 0.67 |
| caudas | 0.25 | 0.10 | 0.10 | 0.10 | 0.07 | 0.03 |
| caudas | 0.50 | 0.10 | 0.07 | 0.13 | 0.03 | 0.10 |
| caudas | 0.75 | 0.10 | 0.07 | 0.33 | 0.10 | 0.27 |
| caudas | 1.00 | 0.20 | 0.07 | 0.73 | 0.27 | 0.80 |

Falso alarme nos nulos de conferência: M11-I distância 11%, M11-I |ΔD| 7%, W₂ completo 11%, W₂-HDR 9%, MMD² 5%
Invalidez do M11-I: nulo 3%, translacao 4%, escala 17%, rotacao 4%, bimodal 3%, curvatura 7%, caudas 8%

## Parte B — rótulo do mecanismo (floresta, deixa uma família de fora; 630 comparações do U2)

| Classe | M11-I | W | convencional | convencional + W | M11-I + W |
|---|---|---|---|---|---|
| nenhum | 0.44 | 0.41 | 0.73 | 0.44 | 0.46 |
| translacao | 0.69 | 0.98 | 0.98 | 0.98 | 0.97 |
| escala | 0.53 | 0.68 | 0.93 | 0.92 | 0.76 |
| rotacao | 0.30 | 0.16 | 0.42 | 0.41 | 0.17 |
| bimodal | 0.24 | 0.30 | 0.22 | 0.29 | 0.21 |
| curvatura | 0.59 | 0.50 | 0.43 | 0.49 | 0.54 |
| caudas | 0.30 | 0.58 | 0.84 | 0.84 | 0.79 |
| **F1 macro** | 0.433 | 0.511 | 0.641 | 0.622 | 0.539 |

W − M11-I: F1 +0.078 (IC +0.018; +0.139); recall bimodal [0.056, -0.078, 0.189], curvatura [-0.089, -0.233, 0.056], caudas [0.278, 0.156, 0.4]

W − convencional: F1 -0.130 (IC -0.167; -0.093); recall bimodal [0.078, -0.022, 0.178], curvatura [0.067, -0.044, 0.178], caudas [-0.267, -0.389, -0.144]

convencional + W − convencional: F1 -0.019 (IC -0.045; +0.007); recall bimodal [0.067, -0.011, 0.156], curvatura [0.056, -0.011, 0.133], caudas [0.0, -0.056, 0.056]

M11-I + W − W: F1 +0.027 (IC -0.001; +0.056); recall bimodal [-0.089, -0.189, 0.011], curvatura [0.044, -0.044, 0.133], caudas [0.211, 0.111, 0.311]