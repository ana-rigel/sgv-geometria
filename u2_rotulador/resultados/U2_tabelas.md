
### floresta

| Classe | M11-I | convencional | combinado | M11-I − conv (IC 95%) |
|---|---|---|---|---|
| nenhum | 0.44 | 0.73 | 0.68 | -0.29 (-0.41; -0.17) |
| translacao | 0.69 | 0.98 | 0.98 | -0.29 (-0.39; -0.19) |
| escala | 0.53 | 0.93 | 0.91 | -0.40 (-0.51; -0.29) |
| rotacao | 0.30 | 0.42 | 0.41 | -0.12 (-0.27; +0.01) |
| bimodal | 0.24 | 0.22 | 0.27 | +0.02 (-0.09; +0.14) |
| curvatura | 0.59 | 0.43 | 0.41 | +0.16 (+0.02; +0.29) |
| caudas | 0.30 | 0.84 | 0.78 | -0.54 (-0.66; -0.43) |
| **F1 macro** | 0.433 | 0.641 | 0.632 | -0.208 (-0.264; -0.155) |

Combinado − convencional, F1 macro: -0.009 (-0.031; +0.014). M11-I com ΔD contínuo: F1 0.476.

Confusão M11-I (linhas = verdade, colunas = previsto, ordem nenhum, translacao, escala, rotacao, bimodal, curvatura, caudas):

```
nenhum       40  10   8  20   1  11   0
translacao    2  62  10   5   0  11   0
escala        1   2  48   1   2  13  23
rotacao      25   8  11  27   2  17   0
bimodal      11  14  11   5  22  27   0
curvatura     2  10   8   3   7  53   7
caudas        4   3  39   0   0  17  27
```

Confusão convencional (linhas = verdade, colunas = previsto, ordem nenhum, translacao, escala, rotacao, bimodal, curvatura, caudas):

```
nenhum       66   0   2   5   5   9   3
translacao    2  88   0   0   0   0   0
escala        1   0  84   2   0   0   3
rotacao      31   0   3  38   3  15   0
bimodal      47   0   3   5  20  13   2
curvatura    20   0   0   5   6  39  20
caudas        1   0   1   0   0  12  76
```

### logistica

| Classe | M11-I | convencional | combinado | M11-I − conv (IC 95%) |
|---|---|---|---|---|
| nenhum | 0.53 | 0.57 | 0.53 | -0.03 (-0.16; +0.08) |
| translacao | 0.73 | 0.96 | 0.97 | -0.22 (-0.32; -0.11) |
| escala | 0.30 | 0.82 | 0.81 | -0.52 (-0.64; -0.39) |
| rotacao | 0.18 | 0.52 | 0.49 | -0.34 (-0.47; -0.23) |
| bimodal | 0.24 | 0.22 | 0.27 | +0.02 (-0.06; +0.11) |
| curvatura | 0.34 | 0.51 | 0.73 | -0.17 (-0.30; -0.03) |
| caudas | 0.46 | 0.81 | 0.80 | -0.36 (-0.48; -0.23) |
| **F1 macro** | 0.398 | 0.628 | 0.655 | -0.230 (-0.264; -0.194) |

Combinado − convencional, F1 macro: +0.027 (-0.001; +0.055). M11-I com ΔD contínuo: F1 0.435.

Confusão M11-I (linhas = verdade, colunas = previsto, ordem nenhum, translacao, escala, rotacao, bimodal, curvatura, caudas):

```
nenhum       48   3  10  11   0  17   1
translacao    1  66  10   2   0  10   1
escala        8   2  27   0   9  11  33
rotacao      35   6  13  16   2  17   1
bimodal      10   5  18   5  22  29   1
curvatura     6   5  25   9   7  31   7
caudas        1   2  28   1   1  16  41
```

Confusão convencional (linhas = verdade, colunas = previsto, ordem nenhum, translacao, escala, rotacao, bimodal, curvatura, caudas):

```
nenhum       51   0   0  14  19   2   4
translacao    2  86   0   0   2   0   0
escala        0   0  74   3   8   1   4
rotacao      21   0   0  47   5  17   0
bimodal      38   0   9   7  20  15   1
curvatura    11   0   3   2  12  46  16
caudas        5   0   0   2   0  10  73
```