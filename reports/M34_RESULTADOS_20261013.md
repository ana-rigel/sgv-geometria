# SGV-M34 — relatório exploratório
**18 origens BTC 1m, 240 alvos/origem, 5 origens na partição interna final.**

| Modelo | Log loss final |
|---|---:|
| B0 | 2.880154 |
| B0+ | 2.970362 |
| B-GEO | 2.949460 |

B0+ menos B-GEO = +0.020902 nats/transição, mas
B0 menos B-GEO = −0.069306: **não há ganho conjunto**.
Nenhum teste confirmatório, p-valor por candle, ou seleção posterior.

Cinco cenários sintéticos: S1 (ganho geom vs B0+ .00497),
S2 (-.04855), S3 (.00106), S4 geom plantada (+1.02640),
S5 geom redundante (+.04201). Em oito sementes, S5 teve
1/8 ganhos aparentes >.02: controle adversarial NÃO autoriza confirmação.

O SGV-M34 usa como baseline B0 uma regressão logística com estados/memória,
não a parametrização HXLOC completa de M23–M30.
Versão Windows/Linux completa em ZIP entregue na conversa, com
resultados CSV/JSON e testes. GitHub usa adaptador para a integração
histórica M11-I; diferenças numéricas da versão portátil são possíveis.
