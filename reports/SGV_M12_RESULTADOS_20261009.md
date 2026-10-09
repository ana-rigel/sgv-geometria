# SGV-M12 — Resultados dos nulos temporais com memória, sazonalidade e regimes

**Data:** 09/10/2026. **Ramo isolado:** `research/m12-nulos-regimes-temporais`. **Execução final:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37977210206 — calibração, BTC 1m e BTC 1h concluídos com sucesso. **7 testes automatizados aprovados**. Nenhum acesso aos meses confirmatórios nem alteração da `main`.

## Pergunta científica

A distância geométrica M11 entre duas cascas HDR50 excede variações geradas por controles temporais que reproduzem, em diferentes graus, atividade persistente, sazonalidade de volume, agrupamento de volatilidade e estados de regime? O resultado M11 (0/2 em 1m vs 2/2 em 1h acima de um nulo pooled simples) sobrevive ao aperfeiçoamento dos nulos?

**Resposta descritiva:** a contagem de janelas acima dos quantis **dependeu muito** da especificação do nulo. Os modelos temporais mais realistas de certos atributos reduziram ou alteraram alertas, mas **nenhum dos quatro foi demonstrado adequado para a distribuição conjunta e os regimes do BTC**. O experimento permanece exploratório, sem inferência de tensão de mercado, lei física, causalidade ou trading.

## Método

**Somente BTC spot exploratório:** 1m maio–julho/2026; 1h 2020–2024. Quatro origens cronológicas não sobrepostas e contínuas por escala. Prefixos de treino **5000 candles para 1m e 3500 para 1h**, fotografia posterior 1500/1008. Todas as estatísticas e catálogos temporais são ajustados somente ao prefixo. A âncora de postos das coordenadas é determinada no primeiro 30% de cada fotografia; os dois segmentos restantes são comparados com mesma transformação. Medição M11: casca HDR50 GMM2 em grade 35³, alinhamento por ICP multistart e distância simétrica determinística dos pontos de quadratura aos triângulos opostos (512 pontos). As distâncias dos modelos nulos são reconstruídas com o mesmo procedimento.

**Quatro nulos:** `N0` bootstrap estacionário em blocos curtos, `N1` SF1-M5 com GARCH-t, memória e harmônico diário, `N2` blocos conjuntos de `z,iota,nu` condicionados a estado e horário de seis horas com blocos curtos, `N3` idem com blocos longos. Estados são definidos por intensidade anterior de `|z|` e atividade `nu`, transições históricas com suavização de Laplace. **Essas regras são heurísticas, não um regime-switching validado.**

Comprimentos: 1m 15/60 candles, 1h 12/36 candles. Seis trajetórias sintéticas por modelo e origem. Um indicador `observada > q90` só é calculado se existirem ao menos quatro trajetórias válidas, mas com seis não é um p-valor nem estabelece taxa de falso positivo.

A adequação temporal dos nulos foi avaliada por erros absolutos medianos em `acf(nu,1)`, `acf(nu,10)`, `acf(|z|,1)`, `std(nu)`, `corr(iota,nu)` e perfil horário de quatro faixas de seis horas. A distância geométrica sozinha não decide fidelidade do simulador.

## Calibração e qualidade

**7 testes aprovados**: estados persistentes plantados, reamostragem determinística, preservação das tuplas conjuntas em blocos, faixas horárias, seleção de linhas do histórico, controles de histórico irregular e ausência de quantis falsos quando não há origens. No controle sintético, a matriz estimada de transições entre estados foi `[[0,8;0,2],[0,2;0,8]]`, e 25 de 25 blocos selecionados respeitaram a faixa horária sem fallback.

Todos os 8 replays de origem foram válidos e todos os quatro modelos produziram seis geometrias válidas por origem, totalizando **192 geometrias sintéticas** para as duas escalas: `4 origens × 4 nulos × 6 trajetórias × 2 timeframes`. Esse é o número de realizações de nulidade geométrica, não o de janelas independentes de BTC.

## BTC 1 minuto — quatro origens válidas

| Modelo | Acima q90 de seis simulações | Erro mediano ACF(nu,1) | Erro ACF(nu,10) | Erro corr(iota,nu) | Erro perfil horário |
|---|---:|---:|---:|---:|---:|
| N0, blocos estacionários | 1/4 | 0,0720 | 0,2403 | **0,0378** | 0,5030 |
| N1, SF1-M5 | 3/4 | 0,0610 | 0,0497 | 0,0463 | 0,4470 |
| N2, regime curto | 2/4 | 0,0437 | 0,2174 | 0,0598 | **0,4276** |
| N3, regime longo | 2/4 | **0,0366** | **0,0470** | 0,0458 | 0,4285 |

Em 1m, memória longa por blocos N3 aproximou a atividade nos lags 1 e 10 melhor que N2, e ficou próxima/superior ao N1 conforme atributo. As seleções N2/N3 tiveram 100% de faixas de relógio compatíveis nesta amostra, sem fallback. Essa coincidência de horário **não** valida a adequação da sazonalidade resultante.

A contagem de distâncias acima de q90 varia de 1/4 (N0) a 3/4 (N1), sem evidência de controle nulo universal. Observadas foram `0,03832;0,07203;0,07351;0,06991`.

## BTC 1 hora — quatro origens válidas

| Modelo | Acima q90 de seis simulações | Erro mediano ACF(nu,1) | Erro ACF(nu,10) | Erro corr(iota,nu) | Erro perfil horário |
|---|---:|---:|---:|---:|---:|
| N0, blocos estacionários | 3/4 | 0,1080 | 0,2772 | **0,0516** | 0,2935 |
| N1, SF1-M5 | 2/4 | 0,0880 | **0,0529** | 0,1245 | **0,1892** |
| N2, regime curto | 2/4 | 0,1060 | 0,3073 | 0,0636 | 0,2126 |
| N3, regime longo | 1/4 | **0,0728** | 0,1481 | 0,0526 | 0,2300 |

Em 1h, N1 reproduziu melhor memória longa de atividade e perfil horário, mas piorou a dependência `corr(iota,nu)` em relação aos demais. N3 reproduziu melhor lag 1 e reduziu a contagem de distâncias acima de q90 de 3/4 (N0) para 1/4. **Não significa que a real geometria deixou de mudar:** esse nulo produz uma distribuição diferente de movimentos sintéticos e ainda tem adequação parcial.

Valores observados: `0,11435;0,11234;0,05766;0,06677`.

## O que as comparações sustentam

**Sustentado como evidência instrumental:**
- O controle sintético verifica a implementação de catálogo de regimes e horários; todos os dados são gerados após calibração restrita ao prefixo e submetidos à mesma rotina geométrica que a observação.
- A variabilidade da distância geométrica depende fortemente da família do nulo.
- A memória longa melhora em comparação a blocos curtos em vários indicadores, mas o modelo estatístico adequado não é único em métricas distintas.
- Não se pode interpretar ultrapassagem de q90 sem auditoria de adequação multivariada do nulo.

**Não demonstrado:**
- Preservação rigorosa de dependência longa, duração real de regimes, transições não estacionárias, ordem verdadeira dos eventos extremos, dependência de livro de ofertas, ou distribuição de caudas da dinâmica de BTC.
- Taxa estatística de falso positivo, intervalos de confiança calibrados, estabilidade entre épocas/câmbios de mercado, vantagem preditiva, causalidade da agressão ou tensão financeira.
- Um estado geométrico Fisher–Rao intrínseco: as cascas são isodensidades extrínsecas em `(z,iota,nu)` gaussianizado.
- Significância estatística a partir de q90 com **seis** trajetórias, quatro origens e várias famílias comparadas.

### Próximo passo para M13

1. Aumentar substancialmente o número de origens e replicações, separando calibração, seleção de família e avaliação independente dentro do conjunto exploratório, sem abrir confirmação.
2. Medir persistência de regimes e caudas conjuntas, duração dos estados e erros condicionais de atividade/volatilidade, em especial as regiões em que N1 e N3 falham de modo diferente.
3. Testar múltiplos comprimentos de bloco e granularidades de horário, preferindo princípios de mínima complexidade e evitando escolher parâmetros para maximizar separação das formas reais.
4. Calibrar formalmente alarmes com nulos de regime criados a partir de geradores sintéticos conhecidos, antes de falar em excedência do ruído do estimador.
5. Se nulos permanecerem inadequados, manter o SGV como instrumento **descritivo** e não atribuir excepcionalidade a curvas ou formas observadas.

## Reprodução

- Protocolo: `reports/PROTOCOLO_SGV_M12_20261009.md`
- Implementação: `experiments/m12_nulos_regimes_temporais.py`
- Testes: `tests/test_m12_nulos_regimes_temporais.py`
- Workflow: `.github/workflows/m12-nulos-regimes-temporais.yml`
- JSON e CSV individuais disponibilizados nos artefatos GitHub Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37977210206.
