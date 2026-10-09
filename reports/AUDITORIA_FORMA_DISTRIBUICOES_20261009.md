# SGV — Forma das distribuições e geometria da dependência: execução exploratória

**Data:** 2026-10-09. **Ramo:** `research/forma-distribuicoes`. **Escopo:** observação matemática de informação pública projetada em três coordenadas; NÃO busca previsão do preço nem comprovação de leis geométricas.

**Fontes:** BTCUSDT spot, klines de exploração com SHA-256 verificado (1m 2026-05 a 2026-07; 1h 2020-01 a 2024-12). **Não foram lidos períodos confirmatórios reservados.** Os replays são causais na disponibilidade de cada fotografia fechada, mas não são captura de WebSocket ao vivo.

## Questão

1. A distribuição conjunta de X=(z, iota, nu), retorno normalizado, fluxo agressor e atividade relativa, pode ser descrita por um único elipsoide gaussiano?
2. Se não, trata-se apenas de caudas/marginais não gaussianas, ou há estrutura especial nas **dependências conjuntas** após equalizar cada marginal?
3. A forma é mensurável em dados reais, com estabilidade entre janelas temporais disjuntas?

**Importante:** Fisher de localização para uma distribuição gaussiana de covariância fixa é `g=Sigma^-1`. A métrica é constante no espaço de médias, portanto sua curvatura intrínseca nesse espaço é nula. O contorno elipsoidal da densidade `(x-mu)' Sigma^-1 (x-mu)=c²` é outra coisa, não um tensor de Riemann encontrado no mercado.

## Procedimento 1 — Forma bruta

Com 70% iniciais da janela de dados, ajustou-se:
- Normal multivariada (um elipsoide).
- Student-t multivariada (uma família de contornos elipsoidais com caudas mais pesadas).
- Mistura de 2 gaussianas (família que pode capturar formas não elipsoidais).
- KDE gaussiano com largura fixa (também permite formas mais gerais).

Os 30% finais (cronologicamente posteriores **dentro da janela histórica já fechada**) receberam log densidades calculadas exclusivamente dos 70% iniciais. As janelas de avaliação são disjuntas (sem reaproveitamento de candles entre suas validações). O diagnóstico é observacional. Não se calcula alvo futuro do preço. Variáveis são padronizadas pelo treino; Student-t tem ν selecionado exclusivamente nos dados de treino; hiperparâmetros fixados no código exploratório, não otimizados pelo resultado do BTC.

### Resultados reais: ganho de logscore médio em nats por observação sobre a normal

| Estatística | 1m | 1h |
|---|---:|---:|
| Janelas válidas | 87 | 31 |
| Janela em candles | 1500 | 1008 |
| Avaliações por janela | 450 | 303 |
| Student-t | **+0,113218** | **+0,272742** |
| Mistura2 | +0,084213 | +0,242072 |
| KDE | +0,111021 | +0,215782 |
| KDE − Student-t | −0,002197 | −0,056960 |
| IC95% bootstrap blocos (KDE − Student-t) | [−0,0291; +0,0642] | [−0,2622; +0,0524] |
| ν Student-t mediano selecionado | 10 | 6 |

A Student-t ganhou da normal em ~93% (1m) e 100% (1h) das janelas. Sua melhora é robusta no bootstrap **exploratório**, mas não prova por si mesma contornos não elipsoidais. A Student-t continua com superfícies de mesma densidade elipsoidais. Nenhuma comparação KDE-vs-Student acima tem IC95% integralmente positivo.

## Procedimento 2 — Isolar a dependência

Para cada janela, estimar os quantis *de cada coordenada* apenas no treino; aplicar a ambos os blocos um mapa monotonamente crescente `z_j=Phi^-1(F_{j,treino}(x_j))`. Isso remove na amostra de treino marginais grosseiramente diferentes (assimetrias, caudas univariadas, `iota` limitado). Em seguida, repetir os quatro estimadores e os logscore sobre os scores transformados.

Diferenças de logscore entre os modelos **preservam comparabilidade** (o jacobiano da mesma transformação cancelaria entre os modelos). Valores fora dos extremos do treino foram truncados na transformação — ponto cego para caudas/extremos; deve ser revisitado.

Aqui o modelo normal é uma **aproximação por cópula gaussiana** com marginais normalizadas. Uma mistura de gaussianas nos scores permite dependências que um único elipsoide/cópula gaussiana não representa.

### Resultados reais: ganho de logscore sobre normal em coordenadas de marginais equalizadas

| Estatística | 1m | 1h |
|---|---:|---:|
| Janelas válidas | 87 | 31 |
| Student-t | +0,002141 | +0,008815 |
| Mistura2 | **+0,059745** | **+0,125522** |
| KDE | +0,014114 | +0,075217 |
| IC95% bootstrap blocos (Mistura2 − normal) | **[+0,050916; +0,070381]** | **[+0,104905; +0,144413]** |
| Proporção de janelas com Mistura2 superior | 90,8% | 93,5% |
| KDE − Student-t | +0,011973 | +0,066402 |
| IC95% bootstrap blocos (KDE − Student-t) | [−0,0124; +0,0386] | [+0,0344; +0,0807] |
| Separação mediana dos centros da Mistura2 | 2,03 | 1,94 |
| Fração com separação de centros ≥4 + componentes ≥15% | 0 | 0 |
| Fração mediana de validação com extrapolação das marginais | 0,67% | 1,32% |

**Achado exploratório central:** depois de neutralizar as formas marginais, a mistura captura estruturas conjuntas de dependência com ganho sistemático e IC95% positivo em ambas as escalas. Em 1h, KDE também supera Student-t nesse espaço de scores. Isso é compatível com dependência não gaussianamente elipsoidal nos observáveis, não com a prova de curvatura física, manifold único, topologia especial ou fluxo causal de informação.

A separação dos centros NÃO satisfaz critério simples de multimodalidade bem resolvida; pode tratar-se de componentes com covariâncias diferentes, assimetria, mistura de regimes, não linearidade ou diferenças locais sem dois picos. A presença de um modelo de mistura melhor ajustado **não é prova de dois modos**.

## Calibração sintética, casos de resposta conhecida

- Normal verdadeira: normal melhor que complexos (penalizados no heldout).
- Student-t com ν=4: Student-t melhora a normal em +0,3413 nat/obs nos dados brutos; após normalizar marginais, ganho residual de Student-t apenas +0,0163, compatível com dependência de caudas.
- Mistura de duas concentrações bem separadas: Mistura2 melhora muito a normal na escala bruta (+0,9591). Após normalizar marginais essa vantagem cai fortemente: exemplo isolado +0,0175, ilustrando que parte relevante da aparência de mistura está nas marginais.
- Dependência curvada `y≈z²`: KDE/ mistura ganham na escala bruta, mostrando capacidade do instrumento de distinguir forma não elipsoidal conhecida.
- Controles independentes com marginais pesadas ou assimétricas, após a transformação: o modelo normal em geral vence, reduzindo falso diagnóstico de dependência especial.
- Testes matemáticos/causais: **10 aprovados** para forma bruta, **5 aprovados** para controle por marginais.

## Limites que impedem afirmação mais forte

1. **Fotografia parcial.** Temos apenas OHLCV/taker buy dos candles, sem livro de ordens, cancelamentos, notícias, posicionamento ou outros fluxos.
2. **Não estacionariedade.** A janela pode misturar dois regimes cronológicos. Isso é parte de uma fotografia histórica de intervalo, mas não implica que a distribuição instantânea tenha duas concentrações simultâneas. Estimar superfícies condicionadas ao regime/tempo e comparar com agregação é imprescindível.
3. **Modelo de mistura.** O ganho de logscore comprova melhor aproximação dentro das famílias escolhidas, não a existência de regiões geométricas descontínuas ou de dois picos.
4. **Calibração das marginais.** ECDF empírica do treino e clipping de valores além dos extremos reduzem sensibilidade às caudas. Testar CDF contínua, tratamento de empates e validação temporal mais curta.
5. **Dependência do estimador.** KDE usa largura fixa; não houve busca de hiperparâmetros. Student-t ν discretizado. As comparações são exploratórias, não prova de ranking universal.
6. **Incerteza.** IC95% bootstrap por blocos de janelas disjuntas de comprimento 4, 1600 réplicas, não corrige múltiplas pesquisas/modelos. Não é prova confirmatória independente.
7. **Temporalidade.** A cada t, a representação geométrica deve ser construída somente com observações publicadas até t. Correlação contemporânea não indica causalidade ou direção de transmissão de informação.
8. **Objeto matemático.** Uma superfície de nível de densidade estimada e a geometria intrínseca de um manifold estatístico são conceitos relacionados, mas distintos.

## Julgamento e próximos testes (ainda NÃO executados)

- **Forma gaussiana bruta única suficiente?** Não para a fidelidade de densidade desses dados exploratórios.
- **Distribuição elipsoidal com caudas pesadas resolve tudo?** No espaço bruto, é competitiva, mas ao equalizar marginais a dependência exige modelo mais flexível para pontuação ótima.
- **Evidência de dependência não gaussiana?** SIM, exploratória e consistente nas duas escalas, após correção marginal.
- **Dois modos separados?** NÃO demonstrado.
- **Topologia / curvatura intrínseca especial?** NÃO testada; não há motivo para afirmá-la.
- **Fotografia estável no sentido de cada pequena alteração de estado?** INDETERMINADO; falta estimar incerteza entre reamostragens e janelas mais curtas.
- **Próximo teste apropriado:** estimar superfícies de densidade e regiões de alto nível de probabilidade a partir da mistura e KDE, estudar conectividade e número de modos contra bootstrap de blocos, testar sub-janelas sem mistura temporal, e replicar sob relógio causal de eventos de mercado. A implementação tem de distinguir forma da amostra de forma de seu fluxo ao longo do tempo.

## Reprodutibilidade

Código:
- `experiments/teste_forma_distribuicoes.py`
- `experiments/teste_forma_dependencia.py`

Testes:
- `tests/test_forma_distribuicoes.py`
- `tests/test_forma_dependencia.py`

Execuções:
- forma bruta: https://github.com/ana-rigel/sgv-geometria/actions/runs/37923329929 (sucesso);
- forma da dependência: https://github.com/ana-rigel/sgv-geometria/actions/runs/37923864022 (sucesso).

Cada execução carrega os CSV por janela e relatórios JSON em artefatos de Actions. A `main` e as linhas científicas encerradas foram mantidas intactas.
