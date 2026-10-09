# SGV-M5 — Resultados da Validação Conjunta do SF1

**Data:** 2026-10-09. **Ramo:** `research/m5-validacao-conjunta-sf1`. **Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37956362999. **Estado:** calibração e dois replays encerrados com sucesso, seis testes automatizados aprovados. Nenhuma modificação da `main`; amostras confirmatórias reservadas não utilizadas.

## Pergunta e critérios
Comparamos quatro geradores de volume sobre mesmos caminhos sintéticos de retorno e desequilíbrio `iota`: SF1 original, memória (lags 1/2/5/10), sazonalidade diária (primeiro harmônico) e ambos.

Regra principal pré-registrada: média entre quatro erros absolutos normalizados de `acf(nu,1)`, `acf(nu,10)`, `std(nu)` e `corr(|z|,nu)`, com escalas `[.15,.15,.25,.15]`. Escolha apenas entre variantes que reduzam a perda pareada mediana frente ao SF1 e não piorem erro mediano ACF1 mais que 0,04 ponto. Essa ponderação é escolha instrumental; **não** é p-value nem inferência de causalidade.

Cada origem: fit no prefixo passado (1m 5000 barras, 1h 2000), comparação com janela posterior (1m 1500, 1h 1008). 8 origens sem gaps por escala, selecionadas determinística e uniformemente das elegíveis. 8 simulações independentes por origem/variante (trajetórias base compartilhadas). Sazonalidade requer três ciclos diários completos e pelo menos 1500 amostras efetivas, **não um requisito arbitrário de 3000 candles**. 1h agora foi avaliado com sazonalidade de fato.

## Resultado BTCUSDT 1m — exploração

| Variante | Perda conjunta mediana | Erro ACF(nu,1) | Erro ACF(nu,10) | Erro corr(abs(z),nu) |
|---|---:|---:|---:|---:|
| SF1 original | 0,866115 | 0,040080 | 0,351904 | 0,073309 |
| + Memória | 0,421757 | 0,048114 | 0,073531 | 0,062396 |
| + Sazonalidade | 0,781316 | 0,036899 | 0,283297 | 0,074393 |
| **+ Memória e sazonalidade** | **0,405507** | 0,045646 | **0,058665** | 0,062735 |

8 origens avaliadas, nenhuma rejeitada. Memória e modelo combinado melhoraram a perda pareada frente ao SF1 nas 8/8 origens. Vencedor pelo critério pré-definido: **ambos**. Redução da perda conjunta mediana frente ao original: ~53,2%.

## Resultado BTCUSDT 1h — exploração

| Variante | Perda conjunta mediana | Erro ACF(nu,1) | Erro ACF(nu,10) | Erro corr(abs(z),nu) |
|---|---:|---:|---:|---:|
| SF1 original | 0,736594 | 0,061892 | 0,224530 | **0,064511** |
| + Memória | 0,413765 | 0,057235 | 0,087621 | 0,094425 |
| + Sazonalidade | 0,779912 | 0,046849 | 0,274479 | 0,087059 |
| **+ Memória e sazonalidade** | **0,377724** | **0,045200** | **0,071770** | 0,079053 |

8 origens avaliadas, nenhuma rejeitada. Memória e modelo combinado melhoraram a perda pareada em 8/8 origens. Vencedor pelo critério pré-definido: **ambos**. Redução da perda conjunta mediana frente ao original: ~48,7%.

Note-se que o modelo combinado tem erro de correlação `corr(|z|,nu)` ligeiramente pior do que o original na escala de 1h. A melhora é **conjunta segundo uma função de perda escolhida**, não melhoria uniforme de todas as métricas.

## Testes e limites
- 6 testes automatizados aprovados antes da leitura de resultados reais: ajuste sazonal no 1h, invariância do ajuste ante perturbações futuras, ciclos completos, rejeição de gaps, estabilidade da regressão e regra de aceitação multi-métrica.
- Mesmas trajetórias sintéticas de **preço e desequilíbrio relativo de agressão** em cada variante; o volume e o número **absoluto** de unidades compradas pelo agressor são modificados com a nova série de volume.
- Resíduos de volume das variantes estendidas não preservam obrigatoriamente a mesma dependência conjunta residual volume–fluxo da base SF1, embora `iota` e preços por trajetória sejam invariantes.
- Apenas 8 simulações por origem, 8 origens por escala e experimentação repetida nos períodos exploratórios; uma validação posterior independente continua necessária.
- A função de perda tem pesos instrumentalmente fixados; pode beneficiar alguma família de métricas em detrimento de outras, e não compara dependências não lineares completas, quantis extremos ou mudança de regime.
- Ganho de fidelidade marginal **não** autoriza concluir reprodução correta da morfologia 3D, existência de tensão, fluxo causal, predição ou lei geométrica intrínseca.

## Próxima decisão técnica
O modelo combinado é o **melhor candidato exploratório para o controle nulo**, em ambas as escalas. Antes de retornar ao contraste das isosuperfícies HDR, devemos calibrar as inovações conjuntas fluxo–volume e testar a reprodução de caudas, regimes, autocorrelações adicionais e variabilidade temporal com amostras futuras sob pré-registro. O SGV continua válido como instrumento de geometria observacional mesmo que essas formas sejam plenamente explicáveis por indicadores e dependências convencionais.

## Reprodutibilidade
- Protocolo: `reports/PROTOCOLO_SGV_M5_20261009.md`
- Código: `experiments/m5_validacao_conjunta_sf1.py`
- Testes: `tests/test_m5_validacao_conjunta_sf1.py`
- Workflow: `.github/workflows/m5-validacao-conjunta-sf1.yml`
- Artefatos Actions: `M5-sintetico`, `M5-BTC-1m`, `M5-BTC-1h`.
- Execução: https://github.com/ana-rigel/sgv-geometria/actions/runs/37956362999.
