# SGV-M4 — Controle SF1 com memória e sazonalidade (09/10/2026)

## Objetivo e fronteira
Melhorar a adequação de um **simulador nulo**, sem tentar descobrir lei geométrica, trading alpha, estresse ou causalidade. A auditoria SF1 anterior identificou diferença de `acf(nu,lag10)`: 1m BTC 0,321 vs SF1 ~0; 1h BTC 0,339 vs SF1 ~0.

## Ablações congeladas
- **SF1 original** inalterado: GARCH-t para preço, dinâmica original de fluxo e volume AR(1) com inovações pares.
- **SF1+M**: mesmo caminho de preço e fluxo, substituir somente dinâmica de `ell=log(volume)` por regressão com defasagens 1,2,5,10 e `|z|,z`, ajustada a prefixo apenas.
- **SF1+S**: mesma dinâmica lag1, com harmônicos de relógio diário `sin/cos(2π clock / 24h)` ajustados ao prefixo.
- **SF1+M+S**: juntar ambos.
- Se o prefixo não contém ao menos três ciclos diários completos e 3.000 candles, marcar S indisponível, **sem fingir melhoria**.

Os três modelos alterados mantêm exatamente o **mesmo caminho sintético de preço e agressão** do SF1 original, e o mesmo fluxo base de sementes entre variantes. As inovações do volume são reamostradas exclusivamente dos resíduos ajustados ao prefixo; coeficientes defasados recebem regularização e limite conservador de magnitude para evitar explosões. Sazonalidade usa *timestamps efetivos*, não índices arbitrários de candle.

## Protocolo exploratório
- BTCUSDT spot 1m: maio–julho/2026, prefixo 5.000 candles e janela posterior 1.500.
- BTCUSDT spot 1h: janeiro/2020–dezembro/2024, prefixo 2.000 candles e janela posterior 1.008.
- Quatro origens equiespaçadas entre candidatas, **apenas segmentos completos, contínuos, sem gaps**.
- Quatro simulações por origem e variante, com 1.700 barras de aquecimento. Comparar mesmas métricas de `flow_coordinates`: `acf(nu,1)`, `acf(nu,10)`, `acf(iota,1)`, `corr(z,iota)`, `corr(abs(z),nu)`, `std(nu)`, `acf(abs(z),1)`.
- Critério de melhoria: **erro absoluto de acf(nu,lag10) menor que no SF1 original sem degradar fortemente acf(nu,lag1)**; exigir leitura conjunta das métricas. Este primeiro piloto não é avaliação confirmatória.
- Registrar para cada origem métricas observadas, mediana simulada, erros por variante e descarte de fit sem convergência ou de gaps.
- Dados protegidos por allowlist/checksum; `main` e período confirmatório intactos.

## Restrições de interpretação
Ajustar sazonalidade dentro do prefixo não prova que seja estável no futuro; limitações de 4 simulações e 4 origens impedem inferência estatística. Correções de volume não garantem reproduzir correlações de fluxo e volatilidade, apesar de manter os caminhos de preço e agressão idênticos por construção. O SF1 aprimorado não torna a métrica SGV curvatura intrínseca nem demonstra um mecanismo de mercado inédito.
