# SGV — Fotografia informacional: teste de observabilidade
**Data:** 09/10/2026. **Ramo:** `research/fotografia-informacional`.
**Tipo:** validação do instrumento descritivo, sem objetivo de previsão ou de novidade informacional.
**Fonte:** BTCUSDT spot, klines exploratórios da Binance Vision; períodos confirmatórios de C1/R1/FR-EWMA mantidos reservados.

## Pergunta
A representação geométrica de X=(retorno normalizado, fluxo agressor, atividade relativa) é calculável causalmente, reage a mudanças verificáveis na estrutura dessas séries e pode ser atualizada a cada fechamento de candle? Não se exige superar indicadores convencionais.

## Definição
No fechamento de t, parâmetros `mu_t` e `Sigma_t` são estimados sobre W barras sem lacunas; métrica de Fisher da família de localização gaussiana (com Sigma fixa) `g_t = Sigma_t^-1`. A distância de Bhattacharyya compara aproximações gaussianas de duas janelas não sobrepostas. Isso representa somente a projeção dos observáveis em X — não a totalidade das informações do mercado.

## Resposta conhecida e invariância
- Gerador sintético: correlação preço/fluxo passa de +0,738226 para −0,727151 após mudança de regime com variâncias de z próximas (0,984 e 0,904).
- Distância entre regimes = 0,390421.
- Erro de invariância da distância sob mesma transformação afim nos dois estados: 4,44e-16.
- Limite negativo deliberado: correlação linear ~0,007 quando dependência quadrática ~0,995 — a fotografia gaussiana não detecta toda dependência não linear.

## Replays causais com dados reais

| Métrica | BTC spot 1 minuto | BTC spot 1 hora |
|---|---:|---:|
| Janela W | 600 barras | 168 barras |
| Intervalo entre retratos resumidos | 60 barras | 24 barras |
| Retratos emitidos | 2194 | 1707 |
| Correlação preço–fluxo (p5, mediana, p95) | (0,477; 0,573; 0,634) | (0,341; 0,491; 0,620) |
| Correlação atividade–fluxo (mediana) | +0,0008 | +0,0592 |
| Distância Bhattacharyya entre janelas disjuntas (mediana) | 0,0394 | 0,0482 |
| Condicionamento da covariância (mediana) | 8,55 | 217,21 |
| Confiabilidade par/ímpar (Spearman da correlação preço–fluxo) | **0,421** | **0,339** |

**Interpretação:** matrizes finitas positivas e séries datadas foram produzidas a partir de candles fechados. A correlação contemporânea esperada preço/fluxo é capturada. Entretanto, a baixa concordância por metades exige intervalos de incerteza e estudos da compensação precisão/atraso ANTES de chamar diferenças pequenas de mudança do estado informacional. Condicionamento depende das unidades de coordenadas e não é uma medida isolada de qualidade científica.

## Streaming incremental e desempenho
`experiments/stream_fotografia.py`: interface `ClosedCandleObserver.on_closed_bar(open_ms,available_ms,close,volume,taker_buy)`. Rejeita candle parcial; timestamps fora de ordem falham; lacunas zeram estado; atualiza X causalmente e calcula Fisher a partir do histórico recente. Os testes de equivalência com o lote comparam média, matriz de covariância, correlação e timestamps.

- GitHub Actions: **13 testes passaram**.
- Benchmark sintético: 6000 candles de 1m, 5101 fotos emitidas após aquecimento.
- Tempo de processamento por candle: mediana **0,3365 ms**, p99 **0,4044 ms** no GitHub Actions.
- Esses números **não incluem** ingestão WebSocket, latência de fechamento/publicação da exchange, envio de dados, persistência, falha de rede ou operação contínua em produção.

**Limite de atualidade:** o replay histórico exporta subamostras horárias/diárias para análise; a classe incremental é capaz de emitir a cada candle fechado, mas ainda precisa ser conectada a fonte live e testada em execução real.

## Julgamento observacional

1. É matematicamente possível e o código produz fotos consistentes de estatísticas de preço, volume e fluxo agressor: **SIM**.
2. O retrato identifica relações contrastantes conhecidas em experimento controlado: **SIM, no gerador sintético**.
3. Foi reconstruído sem acesso ao futuro e o núcleo incremental reproduz o lote: **SIM nos testes**.
4. Já é uma fotografia robusta e precisa de todas as mudanças reais no BTC: **NÃO DEMONSTRADO; confiabilidade por subamostras ainda modesta**.
5. Já está medindo continuamente os dados da Binance live: **NÃO; somente replay e benchmark sintético**.
6. Supera indicadores existentes ou prevê o futuro: **NÃO TESTADO NESTE PROGRAMA, NEM EXIGIDO**.

## Continuação legítima: geometria dos fluxos

- Primeiro, medir o erro estatístico `Sigma_t` e `mu_t`, robustez a W e a dados de eventos, por bootstrap por blocos e controle de gaps.
- Construir a trajetória de distribuições `t -> (mu_t,Sigma_t)`, com a métrica de Fisher da família gaussiana **completa**: `ds²=dmuᵀ Sigma⁻¹ dmu + 1/2 tr(Sigma⁻¹ dSigma Sigma⁻¹ dSigma)`.
- Em seguida, incluir livro de ofertas, spread, profundidade, agressões individuais e cancelamentos, com relógios causais.
- Para **direção do fluxo informacional** empregar defasagens, informação mútua condicional/entropia de transferência, controlando causas comuns. A covariância no mesmo candle não estabelece transferência causal.
- Somente estudar curvaturas/singularidades após validar se a trajetória de estados é estimável de maneira precisa e invariante à escolha de coordenadas.

Fonte de execução inicial dos replays reais: https://github.com/ana-rigel/sgv-geometria/actions/runs/37920389588
Fonte benchmark streaming e testes: https://github.com/ana-rigel/sgv-geometria/actions/runs/37920833779
