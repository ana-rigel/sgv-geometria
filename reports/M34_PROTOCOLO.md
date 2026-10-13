# SGV-M34 — Acoplamento geométrico-dinâmico
**Registro retrospectivo de engenharia/exploração — não é pré-registro confirmatório.** 13/10/2026.

A hipótese testada é o ganho da assinatura M11-I para prever o próximo nó do
estado (z,iota,nu), comparado com B0 e B0+.
Somente BTCUSDT 1m maio–julho/2026, previamente explorado, com SHA-256 e
allowlist; não baixar nem tocar holdouts. Maio fixa a transformação marginal
e os 20 clusters. Cada origem utiliza os 1050 pontos anteriores, duas cascas
de 525 com MESMA âncora maio. Os 240 próximos pontos são alvos,
origens distantes 1500 candles. Separação de grupos 60/20/20 cronológica.
A assinatura se mantém por origem: n estatístico efetivo é número de blocos,
não candles. B0: nó onehot, estado, deslocamento, memória 60 e relógio.
B0+: acrescenta 15 diferenças de médias/covariâncias/variâncias/assimetria.
B-GEO: acrescenta 8 componentes M11-I: centro(3), log-volume, θ/180,
residual triangular 512, ΔD e flag orientação indefinida.
Regressão logística multinomial com C=.1 idêntico, scaler no treino.
Perda é log score do nó seguinte. Exigir melhora contra AMBOS B0 e B0+.
S1–S5 sintéticos verificam poder e falsos ganhos com dados redundantes.
Todos os testes de BTC são exploratórios, inclusive partição interna chamada teste.
Não foi realizada comparação plena com HXLOC M23–M30.
Resultados: B0 2.880154, B0+ 2.970362, B-GEO 2.949460 em cinco blocos
de teste interno entre 18 origens exploratórias. B-GEO NÃO supera B0.
S5 redundante pode produzir ganho positivo espúrio. Não liberar confirmação.
