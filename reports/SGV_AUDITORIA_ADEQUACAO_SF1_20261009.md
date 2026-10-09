# SGV — Auditoria de adequação do modelo SF1
**Data:** 09/10/2026 · **Ramo:** `research/auditoria-adequacao-sf1` · **Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37942766303

## Objetivo
Auditar se o mecanismo estatístico SF1 usado como referência de comparação da dinâmica morfológica reproduz propriedades elementares dos observáveis de BTC. **Não** é teste da existência ou utilidade preditiva de uma curvatura. Sua finalidade é determinar se diferenças entre formas reconstruídas do BTC e do SF1 podem ser explicadas por **inadequação do controle**, antes de atribuir significados geométricos adicionais.

## Método e integridade
- SF1 `fit_sf1` ajustado em **2.000 candles anteriores**, em cada origem.
- Janela posterior de **1.500 candles de 1m** ou **1.008 candles de 1h**, sem usar essas observações no ajuste.
- **Oito trajetórias simuladas por origem** usando parâmetros desse ajuste, mais 1.700 candles sintéticos de aquecimento e recomputação idêntica de `flow_coordinates`.
- Janelas prospectivas escolhidas em pontos cronológicos equiespaçados, que podem compartilhar dados; não são inferências independentes.
- Métricas de distribuição e dinâmica: desvios-padrão, quantis 5/95, autocorrelações lag 1/10 de z, iota e nu, autocorrelação de |z|, correlações contemporâneas z–iota, |z|–nu, iota–nu, deslocamento e razão de escalas entre metades.
- Envelopes q10/q90 por **somente oito simulações** são grosseiros, e a fração fora deles **não é um p-valor**. Não houve correção múltipla. Ajustes de GARCH sem convergência são rejeitados.
- BTC exploratório exclusivamente: 1m maio–julho de 2026; 1h janeiro de 2020–dezembro de 2024. Permissão de arquivo e checksums verificados pelo downloader. Períodos confirmatórios reservados permanecem fechados.

## Resultado principal

| Mediana entre janelas | BTC 1m | SF1 1m | BTC 1h | SF1 1h |
|---|---:|---:|---:|---:|
| acf(nu, lag1) | 0,50464 | 0,48331 | 0,72346 | 0,66885 |
| **acf(nu, lag10)** | **0,32068** | **−0,00036** | **0,33863** | **−0,00143** |
| acf(iota, lag1) | 0,12653 | 0,07494 | 0,12174 | 0,16674 |
| acf(abs(z), lag1) | 0,12138 | 0,04951 | 0,18184 | 0,17198 |
| corr(z,iota) | 0,58170 | 0,52769 | 0,50290 | 0,50603 |
| corr(abs(z),nu) | 0,36759 | 0,32608 | 0,47684 | 0,42932 |
| corr(iota,nu) | −0,00512 | 0,03766 | 0,07209 | 0,02160 |

**Cobertura:** 1m = 8 janelas válidas, nenhuma descartada; 1h = 5 válidas, **3 candidatas descartadas por gaps**.

A discrepância mais repetida é autocorrelação da atividade relativa em lag10. Todas as janelas testadas, nas duas escalas, tiveram a observação fora do envelope central q10/q90 simulado de lag10; este fato isolado não é um p-valor de rejeição porque a referência possui apenas oito simulações e janelas dependentes.

## Interpretação mecânica e metodológica

`SF1` modela log-volume `ell_t = b0 + b1 ell_(t-1) + b2 |z_t| + b3 z_t + e2_t`. A coordenada `nu_t` representa log-volume relativo à mediana histórica. A persistência de lag1 é capturada parcialmente, mas a persistência de lag10 foi praticamente nula nos simulados, em contraste com as observações. Isso pode refletir sazonalidade, dependência longa, não estacionariedade, alterações de regime, detalhes da transformação por mediana ou insuficiência do SF1, isolados ou combinados. **Não se identifica qual deles é o mecanismo sem novas ablações.**

A correlação contemporânea preço–fluxo em 1h foi aproximadamente reproduzida (0,503 observado e 0,506 simulado), enquanto a persistência da atividade foi discrepante. Consequentemente, a diferença de Jaccard das HDRs 3D observadas anteriormente (BTC menos estável que SF1) **não deve ser descrita como fenômeno além de fatos estilizados**. É compatível com um controle que subestima heterogeneidade e memória no volume.

O objetivo observacional do SGV **continua válido**: as séries podem ter representação geométrica fiel mesmo que suas relações sejam explicadas por mecanismos comuns. Esta auditoria aponta como melhorar o comparador e as estimativas de precisão.

## Calibração e proteção

- **6 testes automatizados passaram** (integridade de métricas, rejeição de não finitos, gaps, prefixo completo, testes com dados sintéticos).
- Perturbações artificiais no fluxo agressor SOMENTE depois do prefixo mantiveram inalterados ajustes e simulações SF1 com as mesmas sementes, enquanto as estatísticas reais mudaram.
- O workflow executou com sucesso em três jobs: calibração, 1m, 1h.
- Código original preservado, `main` e períodos reservados intocados.

## Limitações

1. Apenas 8 origens 1m e 5 origens 1h válidas, com sobreposições. Não generalizar para a frequência de regimes de mercado.
2. Apenas 8 simulações SF1/origem. Envelopes percentílicos imprecisos.
3. Os períodos 1m e 1h representam durações físicas diferentes, logo comparar níveis de autocorrelação requer cuidado.
4. SF1 aproximado, sem microestrutura, sazonalidade detalhada, mecanismos exógenos ou fluxo de ordens individual.
5. Uma diferença marginal não invalida a qualidade de observação da geometria; somente limita a interpretação do contraste com esse SF1.
6. A escolha de múltiplas métricas é exploratória; não constitui teste confirmatório.

## Próxima etapa metodológica

1. Modelar **sazonalidade e memória de atividade** no controle: fator intradiário/semanal e dinâmica além de lag1, sempre usando apenas histórico anterior.
2. Fazer ablações isoladas: SF1 original; SF1 com correção de sazonalidade; SF1 com dinâmica de atividade estendida; SF1 com ambos. Manter fluxo e preço iguais para localizar o ganho.
3. Auditar qualidade do novo controle em dados não usados na calibração, com simulações suficientes e cobertura por atributo.
4. Somente depois, repetir a comparação de HDR tridimensionais e avaliar se a discrepância morfológica remanescente persiste; independentemente de persistir, SGV continua instrumento de observação.
5. Ampliar janelas reais independentes, sessões de ingestão autorizadas e calibração de erros/latência de streaming.

## Reprodutibilidade

- `experiments/auditoria_adequacao_sf1.py`
- `tests/test_auditoria_adequacao_sf1.py`
- `.github/workflows/auditoria-adequacao-sf1.yml`
- Relatórios JSON por escala, CSV por origem e métrica nos artefatos Actions.
- Execução final: https://github.com/ana-rigel/sgv-geometria/actions/runs/37942766303
