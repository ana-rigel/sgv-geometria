# SGV-M7 — Reprodução da dinâmica de não convexidade HDR50 (protocolo pré-execução)

**Data:** 2026-10-09 · **Ramo:** `research/m7-dinamica-hdr50-validacao`. Código em ramo isolado, sem mudanças na `main`. Só BTC exploratório autorizado (spot 1m maio–julho/2026 e spot 1h 2020–2024).

## Questão
A observação do M6 — menor erro de variação de não convexidade `ΔD` no M6 acoplado versus M5 independente em quatro janelas — persiste sob maior número de origens e réplicas? Ela acompanha também a reprodução do nível absoluto `D_b` e do déficit de convexidade? **Não** se busca um oscilador de tensão ou alpha.

## Comparadores e definição
- SF1 original, M5 com memória+sazonalidade e resíduos de volume independentes, M6 com memória+sazonalidade e inovação de volume condicional a resíduos de fluxo, 16 estratos.
- Mesmos parâmetros e fluxos de preço/`iota` por origem e semente nos três modelos. Ajustes somente no prefixo cronológico anterior; observação futura não altera o ajuste.
- Cada fotografia HDR50 usa a mesma transformação marginal ancorada nos primeiros 30% da janela, congelada para suas duas metades subsequentes (35/35). Estimador GMM2, grade 35³ no cubo de scores, Hessiana tangencial analítica. Portas: superfície fechada, sem truncamento e cobertura da grade suficiente.
- `D_a,D_b, ΔD=D_b-D_a, C_b` (déficit convex hull); diferenças **absolutas** da mediana das simulações para a observação real. Primeiro critério, erro de `ΔD`. Segundo, erro de `D_b`. Terceiro, erro de `C_b`.
- **Seis origens** determinísticas equiespaçadas dentre segmentos completos e disjuntos em cada escala e **quatro simulações pareadas por origem** e modelo, com 1700 barras de burn-in. As simulações não contam como réplicas independentes do mercado; análise pareada por origem.
- Duas origens predefinidas (primeira e última) recebem **12 replicações bootstrap em blocos** da fotografia real em cada metade, com comprimento 15 candles (1m) e 12 (1h); quantis 10/50/90 são **diagnósticos de reamostragem, não intervalos calibrados**.
- Duas origens predefinidas (primeira e última) recebem checagem HDR50 em grade 49³ versus 35³ apenas para dados reais; registrar alterações D, C e gates de qualidade.
- Relatar número de origens em que M6 supera M5 por erro `ΔD` e `D_b`, medianas das diferenças pareadas, concordância de sinal e todos os descartes. Se ≥2/6 das origens não tiverem pares válidos, **não haverá vencedor**; dado inválido permanece inválido, sem substituição.
- Se a amostra empírica for insuficiente para inferir generalização, reportar **piloto exploratório** independentemente da diferença numérica. Nenhum p-valor confirmatório.

## Salvaguardas
O simulador SF1-M5/M6 não é um nulo comprovadamente adequado em dependências de atividade, volume e caudas. O resultado M6 em quatro janelas pode desaparecer na extensão. A massa HDR é condicionada ao cubo; movimentos são de densidade estimada em coordenadas gaussianizadas, não curvatura Fisher–Rao intrínseca, transporte material, causalidade informacional ou tensão do mercado. Mais simulações são necessárias depois desta prova operacional.

## Artefatos
`experiments/m7_dinamica_hdr50_validacao.py`; `tests/test_m7_dinamica_hdr50_validacao.py`; `.github/workflows/m7-dinamica-hdr50-validacao.yml`; relatórios `reports/SGV_M7_*.json` e CSV individuais.
