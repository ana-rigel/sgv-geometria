# SGV — Decomposição geométrica das mudanças informacionais
**Data:** 09/10/2026. **Ramo:** `research/decomposicao-geometrica`. **Status:** execução exploratória com 10 testes matemáticos aprovados e jobs BTC 1m/1h concluídos. `main` intacta.

## Problema observacional
Decompor diferenças entre duas fotografias fechadas `F=(mu,Sigma)` de `X=(retorno normalizado, desequilíbrio agressor, atividade relativa)`, separando mudança média, mudança de escala e mudança de estrutura de correlações. Isto NÃO é previsão, lei física nem identificação causal de fluxos.

## Matemática verificável

A divergência Bhattacharyya entre duas Gaussianas admite decomposição **exata** em parcelas não negativas:

`DB = M + C`

`M = (mu1-mu0)' * inv((Sigma0+Sigma1)/2) * (mu1-mu0)/8`

`C = logdet((Sigma0+Sigma1)/2)/2 - (logdet(Sigma0)+logdet(Sigma1))/4`

Com `Sigma = D R D`, a parcela C envolve interação entre dispersões D e correlações R; NÃO existe atribuição aditiva intrínseca única para esse par de fatores. O instrumento calcula (a) dois diagnósticos não negativos separadamente, alterando só D ou só R em um contrafactual; e (b) atribuições **Shapley convencionadas**, que podem ser negativas, mas que satisfazem exatamente `C=Share_Escala+Share_Correlação`.

A distância Bhattacharyya total permanece invariante a transformações afins invertíveis aplicadas às duas distribuições. A decomposição escala/correlação NÃO é invariante a uma rotação arbitrária das coordenadas; sua interpretação exige coordenadas semanticamente fixas. Não inferir “causa” de parcelas de distância.

## Procedimento

- BTCUSDT spot, somente arquivos exploratórios permitidos: 1m maio–julho/2026; 1h janeiro/2020–dezembro/2024.
- Fotografias em janelas **disjuntas** W=600 e W=300 no 1m, W=168 e W=336 no 1h; comparação apenas de segmentos sem gaps.
- 399 reamostragens em blocos circulares da série A|B combinada; comprimentos 15 (1m) e 12 (1h); valores p NOMINAIS de um nulo de mesma lei local, com estacionariedade suposta.
- Para cada transição e cada parcela, distância medida, limiar nulo p95, p nominal e efeitos em correlação e log-escalas, gravados no CSV do respectivo cenário.
- Calibração sintética com quatro cenários: estacionário; deslocamento da média; mudança isolada da dispersão de z; mudança de correlação com sinal invertido. 32 pares em cada cenário, W=360, 199 reamostragens. Os componentes corretos detectaram 100% das mudanças artificiais fortes; falsa detecção estacionária (distância completa) = 6,25% (2/32). Conclusão de poder exclusiva desses geradores.

## Resultados reais — janelas principais

| Estatística | 1m (W=600) | 1h (W=168) |
|---|---:|---:|
| Estados fotografados | 220 | 251 |
| Pares temporais válidos | 219 | 237 |
| Distância total acima do limiar nulo p95 | 128 (58,4%) | 40 (16,9%) |
| Somatório de distância explicado pela média | **68,7%** | **50,4%** |
| Atribuição Shapley de escala | **22,5%** | **35,1%** |
| Atribuição Shapley de correlação | **8,8%** | **14,5%** |
| Componente média acima do limiar exploratório | 70,3% | 28,7% |
| Escala isolada acima do limiar exploratório | 20,1% | 4,2% |
| Correlação isolada acima do limiar exploratório | 23,7% | 4,6% |

**Não interpretar parcela Shapley como taxa causal ou informação nova independente.** As fatias somam 100% por CONSTRUÇÃO e podem incluir interações. O percentual de tempo acima do limiar depende do bootstrap e de suas suposições, não é a taxa de fenômenos confirmados.

### Sensibilidade da janela (diagnóstico secundário)

| Estatística | 1m W=300 | 1h W=336 |
|---|---:|---:|
| Estados | 440 | 121 |
| Pares válidos | 439 | 109 |
| Distância completa acima do p95 | 50,1% | 26,6% |
| Participação da média | 65,0% | 61,4% |
| Escala Shapley | 25,7% | 27,7% |
| Correlação Shapley | 9,3% | 10,9% |
| Correlação isolada acima do p95 | 14,4% | 4,6% |

Essa sensibilidade ao tamanho W é parte do instrumento. O algoritmo não determina uma “forma única instantânea”; reconstrói a distribuição observável condicionada à janela, ao sistema de coordenadas e aos dados disponíveis.

## Leitura científica

1. **Predominância de deslocamento da média (nesse objeto gaussiano):** 68,7% em 1m e 50,4% em 1h da distância acumulada advieram da mudança em mu, usando a convenção definida.
2. **A dependência existe e muda:** a componente de correlação não é nula; porém sua parcela atribuída é menor do que média+escala, e as mudanças acima do ruído nominal são mais raras, especialmente em 1h.
3. **Atenção a interpretação de 1m vs 1h:** W=600 minutos e W=168 horas cobrem períodos físicos muito diferentes; comparação é metodológica, não prova de comportamento causal multiescala.
4. **Há dois problemas matemáticos diferentes:** mudança das estatísticas gaussianas e estrutura **não gaussiana** (misturas/copulas) encontrada nos trabalhos anteriores. A decomposição presente cobre somente o primeiro. Não refuta nem confirma a segunda.
5. **Próximo experimento apropriado:** manter fixas as marginais por transformação treinada em histórico anterior, e examinar transformações de cópulas/densidades condicionais em blocos causais. Testar robustez por janelas, modelos de volatilidade/sazonalidade, e bootstrap sob nulos SF1/GARCH, além de observação REST por sessões independentes. Só com essa triangulação faz sentido descrever formas geométricas de informação mais complexas.

## Limites obrigatórios

- Bootstrap do pool de A|B pode borrar regimes e assumir uma estacionariedade inexistente; blocos fixos 15/12 não garantem preservação da dependência longa. Valores p nominais, sem correção múltipla.
- Testes adjacentes (A–B e B–C) compartilham B: fracções não são eventos independentes.
- Parâmetros são amostrais, dependem da janela e do modelo gaussiano; nem o tensor `Sigma^-1` nem as fatias de distância são uma lei física.
- Correlação contemporânea não implica transmissão direcional/casual de informação entre mercados.
- O instrumento atual não contém order book, cancelamentos, informação privada, nem um sistema WebSocket vivo validado. A observação REST anterior cobriu somente dois candles.
- Não foram usados períodos confirmatórios reservados.

## Reprodução

- `experiments/decompor_geometria.py`: cálculo vetorizado, atribuição, geração de controles, execução histórica
- `tests/test_decompor_geometria.py`: 10 testes, inclusive identidade, resposta conhecida, invariância total e validação numérica de bootstrap
- GitHub Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37928674346 (três jobs concluídos com sucesso).
- Artefatos `sgvia-decomp-calibracao`, `sgvia-decomp-1m`, `sgvia-decomp-1h` com relatórios JSON e CSV de cada transição.
