# SGV-M2 — Resultado da Não Convexidade e Discrepância Condicional

**Data:** 2026-10-09. **Status:** execução exploratória concluída. **Ramo:** `research/m2-nao-convexidade-tensao`; `main` intacta. **Execução GitHub Actions:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37947839176.

## Pergunta
Há não convexidade quantificável nas superfícies HDR de `p(z,iota,nu)`? As **mudanças** dessa geometria acompanham **mudanças** da discrepância do retorno padronizado em relação a um modelo condicional contemporâneo de fluxo agressor e atividade?

A primeira pergunta é geométrica e a segunda é uma hipótese econômica exploratória **separada**. Não existe inferência de causalidade, previsão de preço ou lei física.

## Procedimento

- Hessiana **projetada no plano tangente** à superfície implícita da densidade GMM2, não autovalores brutos de Hessiana 3D.
- Curvatura de Gauss `K=k1*k2` e índice adimensional `D=(1/A)∫ max(0,-K)r² dA`, com `r=(3V/4π)^(1/3)`.
- Indicadores complementares: proporção de área com `Kr²<-0.1` e déficit do invólucro convexo `1-V/V(hull)`.
- Normal gaussiana 3D como controle: curvatura K não negativa de superfície elipsoidal, inclusive quando discretização triangular dá artefatos.
- Modelo de discrepância `z ~ 1+iota+nu` ajustado só aos primeiros 30% da janela, antes das duas metades seguintes. As métricas observacionais da discrepância são RMSE dos resíduos normalizados pelo desvio-padrão de treino; não representam preço futuro.
- Compare `delta D` e `delta RMSE` dentro de cada janela, Spearman **descritivo** em até 10 janelas históricas selecionadas equiespaçadamente.
- Janelas W=1500 candles (1m) e W=1008 (1h), sem sobreposição entre candidatas e sem gaps; coordenadas `z,iota,nu` calculadas apenas com dados disponíveis até cada candle fechado.
- Somente BTCUSDT spot EXPLORATÓRIO: maio–julho 2026 no 1m; 2020–2024 no 1h. Proteção por allowlist de arquivos e downloader checksum. Nenhum período confirmatório utilizado.
- Bootstrap circular em blocos fixos, 8 replicações em duas janelas por escala, **apenas sondagem de engenharia**, sem precisão suficiente para intervalos de confiança científicos.

## Resultado real

| Indicador | BTC 1m | BTC 1h |
|---|---:|---:|
| Janelas avaliadas | 10/87 elegíveis | 10/31 elegíveis |
| HDR25: intensidade negativa mediana GMM2 | 0,12753 | 0,16350 |
| HDR50: intensidade negativa mediana GMM2 | **0,13636** | **0,20487** |
| HDR75: intensidade negativa mediana GMM2 | 0,14700 | 0,23938 |
| HDR25: déficit convexo mediano GMM2 | 9,60% | 14,94% |
| HDR50: déficit convexo mediano GMM2 | **6,75%** | **13,19%** |
| HDR75: déficit convexo mediano GMM2 | 5,28% | 11,73% |
| Referência gaussiana: intensidade K negativa | **0** em todas HDRs | **0** em todas HDRs |
| Validade GMM HDR25/HDR50 | 10/10 | 10/10 |
| Validade GMM HDR75 | 10/10 | 9/10 |
| Correlação de Spearman entre delta índice HDR50 e delta discrepância | **+0,0909** | **−0,1758** |

**Leitura central:** os descritores geométricos fornecem evidência exploratória de não convexidade do contorno da **densidade ajustada** em BTC, medível tanto por curvatura negativa projetada quanto por déficit do invólucro convexo. A associação com discrepância condicional de preço e fluxo é **fraca e de sinais opostos** nas duas escalas. Não há, neste piloto, justificativa para denominar o índice geométrico de 'estresse' ou 'tensão financeira'. A pequena amostra e a ausência de controles de confusão impedem concluir ausência universal de associação.

## Calibração e execução

**6 testes automatizados aprovados** antes dos replays. Entre eles: gaussiana elipsoidal `D≈0`, modelo condicional ajustado exclusivamente no trecho anterior, mudança somente futura sem repintar métrica anterior, rejeição de janelas curtas e ausência de associação alegada em dados degenerados. Três trabalhos do Actions — sintético, BTC 1m, BTC 1h — terminaram com sucesso.

## Cautelas e próximos passos

1. Posição, escala e não convexidade são específicas da representação no espaço de scores gaussianizados e do ajuste de mistura. Não representam tensão física, deformação de material ou curvatura intrínseca Fisher–Rao.
2. A curvatura gaussiana analítica negativa está calculada sobre a **isosuperfície da distribuição estimada**, não sobre amostras individuais de ordens; GMM2 tem maior flexibilidade que gaussiana, por isso é necessário controlar sobreajuste por réplica e bootstrap.
3. Amostra de 10 janelas por escala; correlações não têm poder e calibração para sustentarem uma conclusão geral.
4. O modelo contemporâneo de discrepância `z~iota+nu` é apenas controle simples. Ajustes alternativos não lineares, heterocedasticidade e padrões sazonais podem explicar diferenças.
5. O SF1 anterior falhou em reproduzir memória longa da atividade; ainda precisamos melhorá-lo antes de interpretar mudanças geométricas como fenômenos que escapam a fatos estilizados comuns.
6. O próximo experimento deve aumentar replicações e número de janelas, auditar estabilidade de `D` e déficit convexo em grade 35³/49³/61³, usar nulos sintéticos com regimes e volume persistente, e controlar a discrepância por volatilidade/regime. Somente então decidir se faz sentido propor indicador de tensão informacional.
7. Medição por GitHub Actions em replay histórico não equivale a operação contínua em streaming real.

## Referências reprodutíveis
- Protocolo: `reports/PROTOCOLO_SGV_M2_20261009.md`.
- Implementação: `experiments/m2_nao_convexidade_tensao.py`.
- Testes: `tests/test_m2_nao_convexidade_tensao.py`.
- Workflow: `.github/workflows/m2-nao-convexidade-tensao.yml`.
- JSON agregados e CSV completos nos artefatos do GitHub Actions.
- Execução: https://github.com/ana-rigel/sgv-geometria/actions/runs/37947839176.
