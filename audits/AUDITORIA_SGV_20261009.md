# Auditoria cruzada SGV — hipóteses, causalidade e rota de solução

**Data:** 09/10/2026. **Status:** auditoria de código e de experimentos, com testes próprios isolados. **Não é pré-registro de uma nova estratégia e não altera os vereditos anteriores.**

## Escopo e fontes

Repositórios examinados:

- `ana-rigel/sgv` (`main` legado e ramo `sgv-operavel`);
- `ana-rigel/sgv_runtime` (rotinas ao vivo);
- `ana-rigel/sgv-geometria` (`main`, `experiment/fisher-rao-trajectory`, registros R1/L2 e cópia `operavel/`).

Arquivos principais auditados: `PLANO.md`, `PREREGISTRO_R1.md`, `PREREGISTRO_L2.md`, `reports/R1_PORTAO_G1.md`, `reports/l2/l2_calibracao.json`, `sgvgeo/l2.py`, `operavel/sgv_operavel/{backtest.py,features.py,sleeves/{carry,trend,collapse}.py}`, `operavel/scripts/reproduzir_fase1.py`, `sgv_runtime/sgv_runtime_live.py`, `sgv_runtime/sgv_decision_core_v1.py`, e os relatórios FR-EWMA no ramo experimental.

## 1. Hipóteses e vereditos: não trocar perguntas

| Linha | Pergunta/teste | Resultado documentado | Decisão |
|---|---|---|---|
| C1 | Curvatura da métrica Fisher local sobre coordenadas de preço vs GARCH | p=0,40 (1m), 0,175 (1h) | G1 reprovado |
| R1 | Curvatura sobre preço/fluxo vs nulo SF1 | p=0,25 (1m), 0,10 (1h) | G1' reprovado, programa original encerrado |
| L2 | Velocidade Fisher–Rao no espaço de parâmetros SF1 como precursor de mudança de RV | Poder sintético 0/10 em 1m e 1h | teste sem poder; confirmatório bloqueado |
| FR trajetória, janela 1500 | Geodesic curvature da dinâmica gaussiana como incremento ao range | Vantagem desaparece com controles HAR + GARCH | exploração negativa |
| FR-EWMA | Geodesic curvature de estados gaussianos com EWMA | 1m +0,027% MSE, p=0,208; 1h −0,006%, p=0,653 | exploração negativa |
| Operável | tendência ETH 4h + carry funding | números historicamente reproduzidos | reprodução **não valida** execução real, margem, base ou risco |

**Precisão matemática:** a métrica local KDE-Fisher, o escalar ΔF (diferença de curvaturas), a curvatura geodésica da trajetória gaussiana e a velocidade Fisher–Rao entre modelos são objetos diferentes. Nenhum resultado de uma linha transfere automaticamente para outra.

## 2. Falhas concretas reproduzidas

### F1 — Funding na saída é pago mesmo quando a taxa realizada é negativa

Código original `operavel/sgv_operavel/sleeves/carry.py` recebe `funding_rate_t` da liquidação t e decide `EXIT` sem creditar/debitar esse funding. Se estava short antes da liquidação, o pagamento pertence à posição antiga. O valor realizado só pode orientar a posição **depois** da liquidação.

Auditoria independente `audits/causal_carry_compare.py` executada com funding BTCUSDT e ETHUSDT de 2020-01 a 2026-07, 7.212 pagamentos por símbolo:

| Grandeza | BTC | ETH |
|---|---:|---:|
| Eventos EXIT | 324 | 328 |
| Funding negativo nas liquidações de saída omitido no legado (soma por notional) | -0,01392986 | -0,01916399 |
| Soma cashflows legado | 0,64245828 | 0,79357308 |
| Soma cashflows causal | 0,62852842 | 0,77440909 |
| Composição cashflow legado (modelo simplificado) | +90,0746% | +121,0559% |
| Composição cashflow causal (modelo simplificado) | +87,4444% | +116,8564% |

**Isso NÃO é estimativa de rentabilidade operacional**: o comparador *não* modela diferença spot–perp, marcação a mercado, alavancagem, margem, liquidação, reinvestimento factível, spreads variáveis e custos do capital. Correção de tempo não resolve riscos de carry.

### F2 — Risco da Sleeve B ignorado

`collapse.returns_series(trades,index,risk_frac)` não usa `risk_frac`. O teste sintético prova que o mesmo trade gera exatamente o mesmo retorno com `risk_frac=0.001` e `0.005`, contrariando o orçamento de risco descrito. Referência: `audits/operational_controls.py::risk_sized_returns`. Também falta MTM dentro de cada operação e gestão de exposição agregada; corrigir o multiplicador sozinho não basta para portfólio.

### F3 — Gate anual mais permissivo que o pré-registro

`backtest.gate_report` usa `n_pass >= min(min_years_pass,len(per_year))`. Em duas séries anuais perfeitas aceita dois anos quando o gate pede quatro. Anos parciais podem contar. O teste de regressão comprova; referência `strict_annual_gate` com ≥4 anos completos e cobertura mínima de 95%. Os gates congelados originais não devem ser reescritos retroativamente: reapurar em auditoria e registrar a distinção.

### F4 — Possibilidade de associar observação futura à decisão ao vivo

Em `sgv_runtime/sgv_runtime_live.py::merge_runtime_branches`, `pd.merge_asof(... direction="nearest")` pode fazer um ponto geométrico de t+1 minuto alimentar trader t. O teste prova com um caso de resposta conhecida que `nearest` escolhe o futuro onde `backward` escolhe passado. Corrigir segundo **timestamps de disponibilidade da informação**, não apenas timestamp do candle (abertura/fechamento). É risco potencial demonstrado no operador de junção, não prova de que cada execução histórica vazou.

### F5 — Portfólio e risco de carry

`operavel/reports/fase1_reproducao.json` reproduz cerca de 16,88% anual e Sharpe 2,30 do portfólio. Como a avaliação reproduz o mesmo algoritmo incompleto, `confere=true` é verificação de consistência, **não verificação independente de P&L realizável**. O carry apresenta Sharpe ~13 por tratar a taxa de funding como P&L completo e quase sem oscilação do hedge; não inferir retorno futuro desse número.

## 3. Por que L2 tinha pouca potência: diluição temporal

A cada instante t, a L2 estima parâmetros em A=[t-W,t-W/2) e B=[t-W/2,t), com W=1440 e S=60 (1m), W=1008 e S=24 (1h). A estrutura plantada muda 2S barras antes do salto de volatilidade (120 ou 48 barras). A mudança ocupa apenas pequena parte da metade B no momento em que deveria prever.

Para uma mudança em degrau de amplitude δ e regressão local estável, a média de B − A após ℓ barras é aproximadamente:

`(theta_B − theta_A)/δ ≈ min(2ℓ/W,1)`, antes de a janela A começar a mudar.

No momento do salto:
- 1m: 2*120/1440=**0,1667** da amplitude;
- 1h: 2*48/1008=**0,0952** da amplitude.

Esse é um resultado algébrico para janela/contraste de médias, não uma medição do poder real do SF1 completo. A potência nula documentada na calibração segue válida. Um teste de alerta deve considerar observação do impacto em janelas curtas com falso alarme controlado e tempo de detecção, em vez de esperar que uma divergência global entre duas meias-janelas antecipe um evento raro.

## 4. Comparação sintética adicional, com seus limites

Código `audits/early_flow_detector_synthetic.py`: regressão de fluxo simulada, mudança abrupta forte a 120 barras do salto de volatilidade; comparação de escore GLR em janela curta 60 barras com contraste do bloco de impacto em duas meias-janelas 1440; limiares de 99,5% estimados em 30 séries nulas independentes, testados em 40 nulos e 40 alternativas independentes.

| Indicador | Score curto | Contraste longo do bloco |
|---|---:|---:|
| Falsos alarmes por avaliação no nulo | 0,83% | 0,67% |
| Episódios com alarme ANTES de mudança da volatilidade | 100% | 97,5% |

**Interpretação disciplinada:** o score curto é um candidato operacionalmente simples, mas **não ganhou vantagem robusta nesse cenário artificial forte**: o contraste longo também detectou quase tudo. Esses resultados NÃO contradizem a potência nula da L2 completa: aqui a estatística, o gerador, as variáveis e o alvo são diferentes. A comparação apenas demonstra que um experimento centrado em atraso e taxa de alarme é implementável. Não demonstra uma nova descoberta de mercado ou que Fisher–Rao acrescente algo ao impacto direto.

## 5. Solução técnica — prioridade e critérios antes da próxima execução

**Prioridade A: consertar integridade operacional SEM atribuir nova performance.**

1. Recalcular cashflow no timestamp correto; o resultado de funding de t paga a posição anterior a t, só orienta a próxima.
2. Simular duas pernas spot/perp e marcar exposição, lucro/prejuízo, base, margem e liquidação durante a operação; estimar custos reais maker/taker, indisponibilidade de execução e capital imobilizado. Comparar com funding simples e buy/hold sob mesmo risco.
3. Aplicar sizing explícito por operação, alocação entre sleeves e drawdown intratrade; aprovar somente gates em anos completos, sem relaxamento automático de 4/5 anos.
4. Trocar joins temporais ambíguos por junções backward com atraso de publicação calculado, falhar fechado se faltarem candles ou features.
5. Reexecutar o backtest com ancoragem temporal rigorosa, paper trading independente e desligamento dos componentes anteriores que não validaram. **Atenção:** o período histórico do portfólio já foi examinado; serve para auditoria e desenvolvimento, não novo holdout puro.

**Prioridade B: hipóteses científicas novas, separadas das encerradas.**

Investigar **mudança na lei condicional de impacto do fluxo** com escore sequencial ou GLR, comparando diretamente com CUSUM, variação de volatilidade recente, HAR, GARCH e regressões de fluxo usuais. Alvo primário sugerido: detecção precoce de transição de volatilidade com limite fixo de falsos alarmes por dia, horizonte de antecipação e latência máximos, em vez de correlacionar velocidade geométrica com `|log(RV_futura/RV_anterior)|`. Testar primeiro simulações de efeitos **fracos e de vários comprimentos**, inclusive nulo com sazonalidade e heterocedasticidade, para calibrar sensibilidade/especificidade. Só então considerar pré-registro independente, ativo/momento reservado distinto, correção para busca múltipla, ablação (o indicador precisa superar fluxo bruto).

Nenhuma variável de geometria antiga deve voltar ao sistema de produção por conveniência. Preferir variáveis diretamente observáveis que passam em ablações.

## 6. Evidências reproduzíveis e limites

- Branch isolada: `audit/sgv-integridade-20261009`, sem mudanças em `main`.
- Workflow `.github/workflows/auditoria-sgv-integridade.yml`.
- Primeira auditoria, run `37918262028`: cinco testes sintéticos aprovados e BTC/ETH funding real processados.
- Última execução, run `37918811256`: **oito testes sintéticos aprovados**, comparação do funding em ambos os ativos e experimento GLR sintético concluídos com sucesso.
- Artefatos incluem JSON da auditoria por ativo e do teste sintético.
- Não houve exploração dos períodos confirmatórios reservados das hipóteses de curvatura.

## Veredito

**Não há evidência atual de uma lei geométrica independente com poder preditivo robusto. Há, porém, um caminho verificável para um SGV mais correto:** distinguir detecção de fluxo de geometria, testar antecipação com alarmes condicionais causais, e reconstruir a mensuração de P&L e risco antes de chamar uma estratégia de operável.

A solução é **validar causa, tempo, controle e custo**, não adicionar mais camadas matemáticas sem poder discriminativo.
