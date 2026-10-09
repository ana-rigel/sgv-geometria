# SGV Operável

**Reescrita consolidada do projeto SGV · v1.0 · Agosto 2026**
Ana Rigel + colaboradores · Regra vigente: *nenhuma vitória não conquistada será anunciada.*

Este pacote substitui integralmente o código legado (`sgv_novo`). Ele implementa a arquitetura do documento `plano-sgv-operavel.md`: um portfólio de três sleeves com gates pré-registrados, contendo apenas o conhecimento que **sobreviveu à auditoria de 08/2026** — e nada do que não sobreviveu.

---

## 1. O que este código sabe (herança validada do SGV legado)

Cada decisão de design tem origem empírica documentada:

| Conhecimento | Evidência | Onde vive no código |
|---|---|---|
| Eventos de ruptura de atividade predizem volatilidade futura | 45.860 candles 1m (p=1,6×10⁻²⁸); 15m (p=2×10⁻¹¹) | `features.burst_event` |
| A repetição do evento (T2/cluster) é o único amplificador robusto | AUC out-of-fold 0,62 com só as flags estruturais | `burst_event` → `t2_start` |
| Momentum é o único sinal direcional que valida | melhor preditor direcional de todo o dataset (auditoria) | `features.momentum_sign` |
| O edge vive em regime de volatilidade elevada | Doc v5 §3.3 (Sharpe −4,79 em lateral calma) | `features.vol_regime` |
| Custos taker destroem o edge; maker é obrigatório | Doc v5 §4.3 (−5,95% vs viável) | `config.CostConfig`, execução maker-only |
| Thresholds absolutos não transferem entre regimes | OITs 0,09–0,30 vs gate 1e-7 nos 24 trades de junho | todos os thresholds são **percentis móveis** |
| Métricas contínuas (sigma, iit, psi, einstein) não validam | AUC 0,517 nos 336 trades; correlações candle-level nulas | **ausência deliberada** — não existem aqui |

### A descoberta da consolidação: o "vácuo" era um burst

Durante a reescrita (06/08/2026), a engenharia reversa do OIT sobre o bar log 15m mostrou que **OIT-baixo corresponde a `vol_ratio` ALTO** (vol curta/vol longa; AUC 0,725) — o evento que o legado chamava de "vácuo/colapso" é, observacionalmente, uma **ruptura de atividade**: volatilidade de curto prazo rompendo acima do seu regime. O detector direto é mais forte que o proxy legado (|fwd 1h| = 0,326% vs 0,238%, p=2×10⁻¹¹, contra 0,311% vs 0,241%, p=8×10⁻⁶ do OIT). A narrativa toroidal invertia o mecanismo; o fenômeno subjacente é clustering de volatilidade — real, documentado na literatura, e agora medido sem intermediário. Um proxy de "secagem" (|ret|×volume baixos) foi testado e **refutado** no mesmo dia: prediz o oposto (vol futura baixa). Registrado aqui conforme a regra de refutações com o mesmo destaque.

## 2. Arquitetura

```
sgv_operavel/
├── config.py            # TODOS os parâmetros, cada um com origem documentada
├── data.py              # carga Binance Vision/CSV, validação, reamostragem
├── features.py          # burst_event, t2, momentum, vol_regime — só o validado
├── backtest.py          # métricas, portfólio, circuit breaker, GATES pré-registrados
└── sleeves/
    ├── trend.py         # Sleeve A (~50%): TSMOM 4h, vol-target, long/flat
    ├── collapse.py      # Sleeve B (~30%): ruptura T2 em 15m, momentum, stop+hold
    └── carry.py         # Sleeve C (~20%): funding carry delta-neutro
run_fase1.py             # pipeline completo da Fase 1 + relatório de gates
```

Princípios de engenharia aplicados: cada sleeve ≤200 linhas; **zero lookahead** (sinal no fechamento de t, fill na abertura de t+1; retornos da Sleeve A medidos open→open no período em que a posição esteve ativa); custos embutidos por padrão; uma posição por vez na Sleeve B; parâmetros da Sleeve A deliberadamente **não otimizados** neste dataset (valores padrão de literatura) para não contaminar o gate.

## 3. Como rodar

```bash
pip install pandas numpy scipy scikit-learn

# Fase 1 — backtest multi-regime + gates
python run_fase1.py --klines caminho/klines/ --funding funding.csv
```

`--klines` aceita um CSV único ou um diretório de dumps mensais da Binance Vision (menor timeframe disponível; o pipeline reamostra para 15m e 4h). `--funding` é opcional; sem ele a Sleeve C fica inativa e isso é reportado. O relatório sai em `fase1_report.json` com o veredito de cada gate.

**Dados necessários (Fase 0, pendência da Ana):** klines 1m ou 15m de BTCUSDT (e depois ETHUSDT) de 2019→2026, e funding rates do perpétuo BTCUSDT — ambos em `data.binance.vision`, gratuitos.

## 4. Gates pré-registrados (não editar após ver resultados)

Codificados em `config.GateConfig` e avaliados por `backtest.gate_report`, por sleeve: Sharpe OOS ≥ 0,8 em ≥ 4 dos 5 anos; edge médio bruto ≥ 3× o custo round-trip (sleeves de trade); drawdown máximo ≤ 20%; nenhum trimestre respondendo por > 60% do retorno total. Sleeve reprovada é descartada ou reformulada — nunca ajustada até passar. O circuit breaker de DD 10% (`backtest.circuit_breaker`) é aplicado no portfólio combinado.

## 5. Backlog de hipóteses (Plano §5) — status

| Hipótese | Status | Como testar |
|---|---|---|
| H-N1 burst multi-TF simultâneo | pendente | flag em `burst_event` com df 1h |
| H-N2 filtro horário 00–06 UTC | **campo pronto** (`CollapseConfig.block_hours_utc`), desligado até validar | ligar só na Fase 1 com 5 anos |
| H-N3 funding como viés direcional | pendente | cruzar série de funding com `entries` |
| H-N4 sizing por z-score do burst | pendente | `vol_ratio/thr` já sai do detector |
| H-N5 IIT≥0,30 / qualidade_tf | registrar-antes-de-filtrar (protocolo do colaborador) | colunas no log da Fase 2 |
| H-N6 ETH como segundo livro | pendente | mesmo pipeline, dados ETH |

## 6. Smoke test (06/08/2026)

Rodado sobre os 45.859 candles reais do bar log legado (52 dias, abr–mai/2026): pipeline íntegro ponta a ponta; Sleeve B com 19 trades (0,37/dia — cadência prevista no plano), WR 52,6%, edge≈custo. **Este recorte é curto demais para qualquer conclusão de performance** — os gates exigem 5 anos por construção; o smoke test valida tubulação e cadência, nada mais.

## 7. Governança e CHANGELOG

Todo parâmetro novo ou alterado exige: data, autor, amostra de origem e entrada abaixo. Resultado bom demais (WR>75% sustentado, Sharpe>3) dispara auditoria de bug/lookahead antes de qualquer comemoração.

- **2026-10-09 · Reconstrução e congelamento para a Fase 2** — Pacote reconstruído arquivo a arquivo a partir da conversa "VALIDAÇÃO SGV" (criação em 06/08 + as duas correções aplicadas antes da Fase 1: leitor de funding do carry passa a ignorar `funding_interval_hours`; Sleeve B em 1h com stop −1,2%). Atenção: o zip `sgv-operavel-v1.zip` baixado em 06/08 é ANTERIOR à correção do leitor de funding — não usar. Reprodução dos números da Fase 1 em `reports/` (workflow `reproduzir-fase1`).
- **2026-08-07 · Veredito definitivo do carry** — Funding completo (7.212 períodos/símbolo, 2020→2026-07, cobertura 100%; "gaps" da leva anterior eram zips truncados de download). Sleeve C APROVADA em BTC e ETH nos gates. Auditoria "bom demais" mantida: modelo ignora risco de base/margem; e o prêmio DECAI no tempo — funding anualizado por ano (BTC): 2020: 17%, 2021: 31%, 2022: 4%, 2023: 8%, 2024: 12%, 2025: 5%, 2026: 2%. Expectativa forward registrada: ponta baixa da faixa. Portfólio Fase 2 congelado: tendência-ETH 50% + carry BTC 25% + carry ETH 25% → 6,6 anos: +17,0%/ano, Sharpe 2,32, maxDD 8,8%; anos recentes: 2025 +8,2%, 2026 −0,3%. Expectativa forward oficial: **8–12%/ano**.
- **2026-08-06 · v1.0** — Reescrita consolidada completa. Detector migrado de proxy "secagem" (refutado no mesmo dia) para `vol_ratio > p90` móvel (validado, p=2×10⁻¹¹). Semântica T2 definida como confirmação em-run (`t2_start`). Gates da Fase 1 congelados conforme plano §4.

*Nota: pesquisa e engenharia, não aconselhamento financeiro.*
