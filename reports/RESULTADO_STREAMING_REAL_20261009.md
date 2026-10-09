# SGV — Resultado da validação inicial com dados reais atualizados

**Data:** 09/10/2026. **Ramo:** `research/streaming-real-observacional`.
**Ativo:** ETHUSDT spot público. **BTC confirmatório reservado NÃO utilizado**.
**Objetivo:** validar a operacionalização de fotografias geométricas atualizadas a cada candle fechado, SEM prever preço e SEM obter retorno financeiro.

## Implementação, protocolos e dados

- Observador original: `experiments/stream_fotografia.py` (usa X=(z,iota,nu), média, Sigma, Fisher de localização `Sigma^-1`).
- Primeiro meio de ingestão: Binance Spot WebSocket `ethusdt@kline_1m` com `k.x=true`. Executado pelo Actions `37925338169`. **INCONCLUSIVO — HTTP 451 por restrição geográfica imposta pela origem do feed.** Nenhum evento WebSocket fechado foi recebido. REST de aquecimento funcionou com 699 candles.
- Segundo meio, diferente do primeiro: Binance public REST `data-api.binance.vision`, polling a cada 5 segundos, consultando `/api/v3/time` e `/api/v3/klines`. Executado pelo Actions `37925614258`. **PASSOU** segundo os critérios de curta duração previamente declarados.
- Mesmo serviço REST fornece também a reconsulta posterior de cada candle; isto é uma verificação de reprodutibilidade **intra-fonte**, não verificação independente de provedores.

## Resultado do teste REST real

`reports/STREAM_REAL_REST_ETHUSDT.json` como artefato da execução `37925614258`:

| Grandeza | Valor |
|---|---:|
| Candles históricos REST para aquecimento | 699 |
| Candles novos efetivamente observados | 2 |
| Fotografias emitidas | 2 |
| Reconsultas REST coincidentes | 2/2 |
| Gaps observados na janela | 0 |
| Consultas periódicas | 18 |
| Candles parciais explicitamente descartados | 17 |
| Erros registrados | 0 |
| Duração da sessão | 109,55 s |
| Tempo entre fechamento teórico e recebimento local | 1.092 ms e 3.017 ms |
| Mediana das idades aparentes ao receber o candle | 2.054,5 ms |
| Tempo de processamento geométrico | 0,519858 ms e 0,464783 ms |
| Mediana de processamento geométrico | 0,492321 ms |
| rho(preço, fluxo) nas duas fotos | 0,528211 e 0,461394 |
| Condicionamento da métrica nas duas fotos | 13,31 e 19,67 |

Não interpretar diferença de `rho` entre duas fotos como transição de regime: cada `rho` resulta de uma janela de 120 pontos e as duas janelas se sobrepõem quase inteiramente. A variação pode refletir uma observação entrando e outra saindo. A precisão de inferência não foi medida.

O relógio do runner e o relógio da Binance não são sincronizados matematicamente com precisão de milissegundos. A medição via tempo do servidor a partir de REST foi 469 ms e 2.327 ms depois do fechamento teórico. A diferença para a idade no relógio local inclui efeito do tráfego/latência e possível diferença de relógios. **Não é p95/p99 de produção e não caracteriza latência da conexão WebSocket.**

## Qual afirmação foi validada?

**SIM:** a arquitetura consegue atualizar `mu, Sigma, g=Sigma^-1` a partir de dados de uma exchange que chegam depois do fechamento de um candle real, respeitando o relógio causal, em um teste limitado de dois candles. Dados parciais são excluídos e a fotografia é computacionalmente rápida.

**NÃO DEMONSTRADO:** recebimento real via WebSocket no runner (HTTP 451); operação por 24h/7d; confiabilidade de forma, incerteza de `Sigma`, existência de dois modos, fidelidade de topologia, direção de fluxo de informação, estabilidade estatística e informação preditiva.

## Próximo portão de engenharia — ainda não executado

1. Executar coletor sem restrição de origem por 24h (somente onde permitido pelo provedor) e mensurar centenas de candles fechados; registrar frequência de gaps, latência p50/p95/p99 e falhas de reconexão.
2. Enquanto a fonte WebSocket estiver restrita, ampliar auditorias REST autorizadas como modalidade distinta, com persistência append-only e reinícios independentes.
3. Reavaliar as fotografias com bootstrap em blocos para cada janela; comparar nível de ruído de estimativa com as distâncias entre estados.
4. A partir das formas/ dependências descobertas em `research/forma-distribuicoes`, calcular geometrias de superfícies de nível condicionais ao tempo e comparar contra distribuição de referência da mesma janela, SEM chamar mistura com duas componentes de "duas regiões" antes de teste de modos.

## Fontes para conferência
- WebSocket bloqueado: https://github.com/ana-rigel/sgv-geometria/actions/runs/37925338169
- REST polling bem-sucedido: https://github.com/ana-rigel/sgv-geometria/actions/runs/37925614258
- Protocolos: `reports/PROTOCOLO_STREAMING_OBSERVACIONAL.md`
- Scripts: `experiments/validar_stream_real.py` e `experiments/validar_polling_real.py`
- Testes unitários: `tests/test_validar_stream_real.py`, `tests/test_validar_polling_real.py`; os workflows passaram em ambos os conjuntos.

Esta etapa não alterou `main` e não leu o período BTC reservado.
