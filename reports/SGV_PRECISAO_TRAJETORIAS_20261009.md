# SGV — Precisão observacional e trajetórias: auditoria exploratória de 09/10/2026

**Ramo:** `research/precisao-trajetorias`. **Finalidade:** medir erro de fotografia e variações entre estados, sem previsão de preço e sem lei geométrica pressuposta. `main` intacta.

## Pergunta operacional

Uma representação `F_t=(mu_t,Sigma_t)` das coordenadas observadas `(z,iota,nu)` muda entre janelas fechadas mais do que se esperaria sob flutuação amostral estacionária local? E como isso varia com o tamanho da janela?

## Metodologia

- Dados BTCUSDT spot, **apenas exploratórios**, Binance Vision com download de klines e checksum. 1m maio–julho/2026; 1h 2020–2024. Os períodos confirmatórios antigos não foram lidos.
- Cada fotografia cobre janela W DISJUNTA (1m W=600 ou 300, 1h W=168 ou 336). Não usa retornos futuros. Gaps, NaNs ou covariância degenerada quebram segmento ou desabilitam foto.
- Distância de **Bhattacharyya** entre os dois ajustes gaussianos consecutivos, sensível tanto a deslocamento da média quanto mudança de dispersão/covariância. Não mede transferências causais.
- Comprimento **quadrático Fisher no ponto médio**, como aproximação local entre distribuições; **não** é comprimento de geodésica exata.
- Intervalo de 95% para `rho(z,iota)` por bootstrap circular em blocos dentro de cada janela.
- Nulo exploratório: combinar observações de duas janelas adjacentes A|B e ressorteá-las com blocos circulares (L=15 barras no 1m; L=12 no 1h) para construir pares artificiais sob hipótese de mesma lei local. 399 replicações e p=(1+quantidade de distâncias nulas >= observada)/400. O pool pode misturar regimes; a dependência entre blocos maiores que L não é preservada. Os 95% e p-valores são **nominais**, sem correção de múltiplas comparações.

## Calibração sintética antes de BTC real

40 pares estacionários AR(0,35), estrutura de covariância invariável: 3/40 = **7,5%** de falsos alarmes nominais 5%.
40 pares com inversão artificial de correlação (+0,75/-0,75 nas inovações): 40/40 = **100%** de detecção. A alternativa é forte; não inferir sensibilidade a mudanças pequenas nem calibração correta com série real heterocedástica. Testes unitários: 8 aprovados.

## Resultados exploratórios do BTC

| Métrica | 1m W=600 | 1m W=300 | 1h W=168 | 1h W=336 |
|---|---:|---:|---:|---:|
| Estados completos | 220 | 440 | 251 | 121 |
| Comparações entre estados adjacentes válidos | 219 | 439 | 237 | 109 |
| Segmentos temporais sem lacunas | 1 | 1 | 14 | 12 |
| Mudanças acima do nulo local nominal 95% | 126 (57,5%) | 220 (50,1%) | 41 (17,3%) | 28 (25,7%) |
| Distância Bhattacharyya mediana | 0,04017 | 0,05372 | 0,05057 | 0,03782 |
| Limiar local p95 de ruído mediano | 0,02697 | 0,04880 | 0,09725 | 0,05183 |
| Mediana largura IC95 da correlação `rho(z,iota)` | 0,1040 | 0,1363 | 0,1984 | 0,1478 |
| Pares com IC95 de rho não sobrepostos | 4,11% | 2,05% | 2,95% | 1,83% |

A relação entre a taxa de mudança conjunta e a raridade de intervalos de correlação não sobrepostos é **compatível** com mudanças de média e covariância que `rho(z,iota)` isoladamente não identifica. Mas essa diferença não permite afirmar, sem ablações, que as mudanças são independentes de volatilidade/atividade conhecidas. O contraste de IC que não se sobrepõem é conservador e não equivale ao p-valor da distância conjunta.

No 1m W=600, 126 de 219 pares ultrapassam o limiar local exploratório. No 1h W=168, 41 de 237 pares. Com janela maior 1h, cresce a fração detectada, enquanto a largura mediana do IC da correlação cai. A escala de cada janela difere: 600 minutos vs 168 horas, e não são horizontes diretamente comparáveis.

## Diagnóstico e interpretação

**O que foi demonstrado:**
1. A representação geométrica `(mu,Sigma)` pode ser construída em múltiplas escalas com dados conhecidos até cada fechamento de candle.
2. O instrumento gera um caminho de estados datados e uma distância objetiva entre estados adjacentes.
3. A incerteza estatística depende da janela; reduzir W torna intervalos de correlação mais largos (1m) e pode amplificar mudanças de ruído.
4. Sob nulo artificial AR estável, taxa de falso alarme observada 7,5% (40 pares) e não calibrada rigorosamente; sob alternativa forte, sinal detectado em todos os pares.

**O que NÃO se conclui:**
- Não se provou uma curvatura riemanniana não nula ou topologia particular.
- Não se identificou direção causal de fluxo de informação ou previsão de retornos.
- Um limiar superado entre duas janelas não é uma nova estrutura do mercado comprovada: a distribuição da estatística depende do nulo escolhido, do bloco e de sazonalidade/heterocedasticidade.
- O bootstrap circula a série combinada A|B e aplica um nulo local de estacionariedade que pode falhar no mercado. Uma sequência de p nominais <0,05 **não** deve ser chamada de descobertas confirmadas.
- As comparações adjacentes compartilham uma janela (A-B, B-C), criando dependência entre testes; sem múltiplos ajustes, os percentuais de alertas são apenas diagnóstico de sensibilidade, não proporção real de transições.

## Próxima etapa proposta e critérios

**Objetivo 1:** saber que aspectos do retrato estão mudando. Executar ablações separadas:
- apenas médias (mu);
- apenas escalas/diagonal de Sigma;
- apenas correlações/covariâncias normalizadas;
- distância completa Bhattacharyya;
- marginais transformadas por ranks de treino para estudar mudança da dependência além de caudas.

**Objetivo 2:** calibrar a detecção sob nulos mais realistas preservando efeito calendário, clusters de volatilidade e autocorrelação de volume/fluxo (surrogates com bloco variável L, simulações de GARCH/t/SF1 e reamostragens em regimes localmente estacionários). Para cada método reportar falsos alarmes POR HORA e cobertura real, não só por comparação.

**Objetivo 3:** testar a estabilidade entre janelas, escalas, ativos e sessões REST independentes. O teste real anterior teve somente dois candles de ETHUSDT sob REST polling. Isso confirma execução curta, não precisão temporal de longo prazo.

**Objetivo 4:** investigar evolução das formas não gaussianas já identificadas no ramo `research/forma-distribuicoes`, mantendo a distinção entre superfície de nível da densidade e métrica estatística intrínseca.

## Reprodutibilidade

- Código: `experiments/precisao_trajetorias.py`
- Testes: `tests/test_precisao_trajetorias.py`
- Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37926824965 (três jobs aprovados).
- Artefatos: `sgv-trajetorias-calibracao`, `sgv-trajetorias-1m`, `sgv-trajetorias-1h`; JSON com agregados e CSV com estados/todos os pares, intervalos e estatísticas.

**Veredito:** o SGV já produz trajetórias de fotografias e dispõe de um instrumento inicial para expressar a precisão da medida e sua variação por escala. Ainda falta calibrar o ruído contra nulos de mercado adequados antes de afirmar que determinada mudança geométrica tem significado distinto de indicadores e flutuação amostral.
