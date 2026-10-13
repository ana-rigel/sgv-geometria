# SGV M31-G0 — Resultado da auditoria causal de engenharia

**Status:** engenharia concluída, NÃO houve hipótese científica M31-G testada.
**Run:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38336025801
**Branch:** `research/m31g0-engenharia-causal` (base M30, `main` não alterada).
**Artefato:** [SGV-M31G0-causal-engineering-only](https://github.com/ana-rigel/sgv-geometria/actions/runs/38336025801/artifacts/11784372457).
**Protocolo de engenharia:** `reports/M31G0_ENGENHARIA_PLANO.md`.
**Código:** `experiments/m31g0_features_causais.py`, `tests/test_m31g0_features_causais.py`.

## 1. O que foi feito

Duas medidas **PROVISÓRIAS** sobre janela histórica de 360 candles:
- `cone_log_proxy_t = log(sd(z|nu >= q_2/3) / sd(z|nu <= q_1/3))`.
- `waist_proxy_t = P(|iota| <= 0.1 | nu >= q_2/3)`.
- `cone_log_x_nu_proxy_t = cone_log_proxy_t * nu_t`.

E um baseline de **engenharia** B0: HAR-X com log RV das últimas
15/60/240/1440 barras, médias móveis do volume, |iota_t|,
nu_t, seno/cosseno da hora, seno/cosseno do dia e dummies da
semana; B1 inclui 3 proxies adicionais. Regressores ajustados
via ridge de parâmetro 1 fixo e 672 últimas origens cujo
RV_15 **já terminou em t**, com smearing de resíduos do treino
para passar de log RV ao nível positivo de variância. B0
**NÃO é o benchmark forte congelado sugerido pelo colaborador**,
porque ainda não utiliza perfil sazonal empírico estimado nos
últimos sete dias nem uma comparação sistemática com alternativas
econométricas competitivas. Nenhum score preditivo foi medido
ou usado para escolher variáveis.

Alvo construído: `RV_15(t) = Σ_(j=1)^15 (log(close_(t+j)/close_(t+j-1)))²`,
somente para labels cujo prazo `t+15` já havia transcorrido
dentro do treino. Origem temporal a cada 15 minutos UTC,
com candles fechados e histórico íntegro. `nu` requer 1500
barras anteriores e as features de forma exigem mais 360;
não se usa um valor de rótulo ainda desconhecido na previsão.

## 2. Resultados verificados no GitHub Actions

| Checagem | Sintético | BTCUSDT spot 1m mai–jul/2026 |
|---|---:|---:|
| Candles carregados | 17.000 | **132.480** |
| Origens de 15 min possíveis | 1.134 | **8.832** |
| Origens com features causais após warmup | 1.009 | **8.707** |
| Cobertura sobre origens brutas | 88,9771% | **98,5847%** |
| Primeira origem válida (UTC) | 02/05 07:15 | **02/05/2026 07:15** |
| Última origem válida (UTC) | 12/05 19:15 | **31/07/2026 23:45** |
| Tempo de cálculo das features | 0,1966 s | **1,6599 s** |
| Previsões de engenharia realizadas | 8 | **32** |
| Tempo dos ajustes B0+B1 nessas origens | 0,0356 s | **0,1415 s** |
| Rótulos futuros indisponíveis no fim | 1 | **1** |

Todos os **10 testes unitários passaram** (1,98 s), cobrindo:
- cálculo exato de RV futura e regra de maturação;
- invariância de features em t após modificação de preços,
  volume e agressão em t+1 e além;
- invariância dos forecasts ao modificar rótulos que ainda não
  amadureceram em t;
- detecção de gaps, duplicatas, OHLCV inválido e restrição de período;
- comportamento das proxies sob variação controlada;
- equivalência da diferença de QLIKE e QLIKE-deviança;
- invariância da deviança à mudança de unidades de RV;
- forecasts positivos e smearing causal;
- ausência deliberada de p-values, P&L e métricas de vitória.

**Distribuições das proxies no BTC (DESCRITIVAS, NÃO efeito futuro):**
- `cone_log_proxy` mediana **0,813385**,
  percentis 5–95: **0,492775 a 1,394275**,
  amplitude **0,09779 a 2,395185**.
- `waist_proxy` mediana **0,108333**,
  percentis 5–95: **0,05 a 0,208333**,
  amplitude **0,008333 a 0,6**.

As 125 origens ausentes em relação às 8832 possíveis são
consistentes com o aquecimento histórico de 1500+360 barras;
não foi identificado outro bloqueio neste conjunto. Não
generalizar essa cobertura a períodos com gaps ou outros
ativos.

## 3. Interpretação precisa

**Comprovado nesta engenharia:**
1. É possível montar duas estatísticas condicionais com janela de
   6h usando apenas o histórico de BTC 1m já conhecido até t;
2. O pipeline é computacionalmente econômico para o conjunto
   exploratório e produz dados sem lacunas aparentes após o warmup;
3. O baseline e sua versão acrescida podem gerar previsões positivas
   sem acessar os próximos 15 retornos ao ajustar em t.

**NÃO comprovado:**
- que as proxies são as medidas exatas de "cone" e "cintura"
  anteriormente obtidas pelo colaborador;
- que tenham valor preditivo adicional a B0 ou B0+;
- que B0 seja a econometria competitiva mais forte;
- que exista vantagem geométrica intrínseca, causalidade do
  mercado ou oportunidade operacional;
- que as estimativas mantenham poder, cobertura ou calibração em
  séries externas como ETH 1m.

O pipeline não calculou scores de QLIKE, intervalos
de confiança de habilidade preditiva, p-values ou
rentabilidade. Não usou nenhum dado reservado.

## 4. Pendência prioritária ao colaborador

Solicitar **branch, SHA, arquivo e fórmulas** da investigação de
"abertura do cone 2,1×, persistência 0,51" e "cintura em episódios".
Esclarecer se os achados são baseados em densidade observacional
GMM2/HDR, estatísticas de estratificação de z/nu/iota ou ambos,
e como lidar com janelas 360 vs 1500 candles.

Até a recuperação do instrumento original, as medidas
aqui são apenas **proxies condicionais não geométricas**.
Se a medida original depender de densidade HDR, um ganho
de proxy não poderia ser creditado à curvatura/forma.
Se não houver medida original reprodutível, rebatizar a
hipótese como "condicionamento de volatilidade ao volume"
e usar comparador HAR-X comum, sem alegar originalidade.

## 5. Próxima etapa de engenharia, SEM holdout

Implementar o B0+ competitivo com interação RV×volume e
concentração de fluxo e o B0 sazonal de perfis históricos
estimados só no passado; medir custo e cobertura sem escolher
configuração por QLIKE exploratória. Executar power/coverage
sintético com melhoria plantada e erro temporal persistente;
somente então solicitar parecer de congelamento do pré-registro
M31-G. Não tocar ETH 1m nem BTC out–dez/2026.
