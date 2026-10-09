# SGV — Protocolo de observação real em streaming

**09/10/2026.** Código novo preservado em `research/streaming-real-observacional`, sem modificar `main`. Objetivo: distinguir viabilidade de processamento em replay sintético da observação efetiva de dados transmitidos em tempo real.

## Fonte, isolamento e tempo
- ETHUSDT spot, feed público WebSocket `ethusdt@kline_1m`. Não consome BTC nem suas amostras confirmatórias reservadas.
- REST Spot `/api/v3/time` e `/api/v3/klines` servem para inicialização e auditoria após o evento.
- Bootstrap usa apenas candles já encerrados ao tempo informado pelo servidor. O horário REST e o relógio do runner não são intercambiáveis sem estimar erro.
- Receber `k.x=true` é requisito para processar um candle; `k.x=false` nunca atualiza estado.
- `asof_ms=open_ms+60_000` designa o instante teórico de fechamento. O instante real de disponibilidade da mensagem é `received_ms`, registrado separadamente.
- Se a transmissão tiver gap, o observador zera os históricos e não emite falsa continuidade. Não faz interpolação.
- Conferência REST **depois** do evento verifica close/volume/taker buy com tolerância de ponto flutuante; a conferência não realimenta o modelo.

## Instrumento
`ClosedCandleObserver` com W=120 pontos de `X_t=(z, iota, nu)`. O bootstrap aquece retornos e volumes e fornece amostras suficientes para atualizar `mu_t`, `Sigma_t` e `g_t=Sigma_t^-1` ao fechamento.

## Portão do teste curto de conectividade
- ≥ 2 candles reais fechados em até 220 segundos;
- uma fotografia por candle;
- todos os candles coincidem com REST posterior;
- zero gap no intervalo ao vivo.

Se algum critério falhar, classificar como inconclusivo/falho e examinar o motivo. Não converter falha de API/rede em refutação geométrica.

## Métricas
- `event_minus_close_ms=event_ms-(open_ms+60000)`, atraso do evento informado pela exchange;
- `receipt_minus_event_ms=received_ms-event_ms`, atraso aparente dependente de sincronização dos relógios;
- `receipt_minus_close_ms=received_ms-(open_ms+60000)`, idade aparente do candle no recebimento;
- `processing_ms`, custo de atualização local.

Esses números não equivalem a garantia de latência ponta a ponta. O cálculo pode ser inferior a 1 ms e a publicação chegar com segundos de atraso.

## Validação a seguir
- Sessões independentes ≥24h e reinicializações em horário variável, hospedagem estável e registro de *heartbeats*; GitHub Actions é ambiente de testes efêmeros, não coletor sempre ligado.
- Traçar taxa de perda, `p50,p95,p99` de latência, drift de relógios (medidas servidor-REST), divergência REST, fração do tempo com fotografia válida, estabilidade de `mu,Σ`, intervalos de confiança.
- Comparar fotografias do feed em diferentes janelas e com dados agregados de trades; diferenciar *observabilidade* de estabilidade morfológica e causalidade de informação.
- Para estudar forma não gaussiana real, considerar a mistura de distribuições e controle por gaussianização marginal, já validados exploratoriamente em `research/forma-distribuicoes`.

**Julgamento do experimento presente somente após ler JSON do Actions, incluindo eventuais erros.**
