# SGV-M20b — Leitura científica do teste de dependência além da segunda ordem

**Data:** 11/10/2026. **Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38159625258
**Ramo:** `research/m20b-dependencia-alem-segunda-ordem`.
**Status:** 8/8 testes aprovados; piloto e execução integral concluídos; TODOS os portões do ensaio INTEGRAL satisfeitos.
**Artefato:** `SGV-M20b-ensaio-sintetico` (ID 11709374819); contém `piloto.json` e `resultados_sinteticos.json` com limiares, contagens e intervalos de Wilson.
**Fonte dos números:** saída do job sintético, resumo por grupo e estatística auditável no log.

## 1. Por que este experimento difere de M20a

M20a demonstrou que marginais estacionárias podem esconder rotação temporal,
mas a covariância cruzada defasada convencional detectou 100% das rotações.
M20b constrói outro limite de identificabilidade: duas cadeias Markov
estacionárias têm **as mesmas distribuições marginais e as mesmas
autocovariâncias lineares em TODOS os atrasos**, além de memórias de
quadrados e valores absolutos nulas, embora possuam transições não lineares.

A primeira coordenada em H+ e H- segue
K_eta(y|x)=phi(y)[1+eta h(x)h(y)],
h(x)=sin(2x)-2exp(-3/2)sin(x), eta=±0.43.
As outras coordenadas são ruídos gaussianos independentes.
O nulo tem eta=0 e é iid. A amostragem por rejeição usa envelope
que garante positividade da probabilidade de aceitação.
A cadeia foi inicializada exatamente na distribuição estacionária N(0,1).

E_phi[h]=E_phi[xh]=E_phi[x²h]=E_phi[|x|h]=0.
Por isso: E[X_t]=0, Var(X_t)=1, Cov(X_t,X_(t+k))=0,
Cov(|X_t|,|X_(t+k)|)=0, Cov(X_t²,X_(t+k)²)=0, k>=1.
O acoplamento q_eta(x,y)=phi(x)phi(y)[1+eta h(x)h(y)]
depende de eta, apesar das mesmas marginais.
É simétrico em x,y: **os H± são REVERSÍVEIS**, não correntes circulatórias.

## 2. Plano efetivamente realizado

N=1800 observações por série; 280 séries sob nulo para limiares;
200 séries de avaliação INDEPENDENTES por cenário:
null, hidden_plus, hidden_minus, volatility_memory.
A definição dos geradores, estatísticas, tamanho, seed e portões constava
do protocolo antes da primeira execução do Github Actions.
O piloto usou N=450, 16 séries calibradoras e 16 por grupo; NÃO serviu
para ajustar parâmetros, e seus portões de poder G3 falharam (resultado
esperável em tamanho muito menor; não ocultar).

## 3. Taxas observadas (numeradores / 200; percentuais)

| Estatística | Nulo | H+ | H- | Memória vol. |
|---|---:|---:|---:|---:|
| Fourier-HSIC (dependência não linear, primário) | 10/200=5,0% | **191/200=95,5%** | **192/200=96,0%** | 200/200=100,0% |
| Covariância linear lag1 | 17/200=8,5% | 13/200=6,5% | 13/200=6,5% | 31/200=15,5% |
| Covariância de |X| lag1 | 8/200=4,0% | 5/200=2,5% | 8/200=4,0% | **200/200=100,0%** |
| Covariância de X² lag1 | 8/200=4,0% | 7/200=3,5% | 5/200=2,5% | **200/200=100,0%** |
| Dependência de sinais lag1 | 8/200=4,0% | 33/200=16,5% | 40/200=20,0% | 15/200=7,5% |
| Momento Hermite H3 lag1 | 7/200=3,5% | 110/200=55,0% | 96/200=48,0% | 104/200=52,0% |
| Oráculo h lag1 | 6/200=3,0% | **200/200=100,0%** | **200/200=100,0%** | 8/200=4,0% |
| Deslocamento média entre metades | 8/200=4,0% | 6/200=3,0% | 10/200=5,0% | 14/200=7,0% |
| Diferença variância entre metades | 7/200=3,5% | 6/200=3,0% | 6/200=3,0% | 40/200=20,0% |

Limiar unilateral empírico por estatística: quantil 95%, método `higher`
na calibração nula; alarme estritamente acima. O arquivo JSON registra
cada limiar e Wilson 95%. **Não** são experimentos de predição, P&L ou
significância confirmatória do BTC.

## 4. Julgamento contra os critérios congelados

- G1 ortogonalidade, estacionariedade e kernel positivo: **PASSOU**.
- G2 Fourier-HSIC falso alarme <=10%: **PASSOU (5%)**.
- G3 Fourier-HSIC poder >=80% em H+ e H-: **PASSOU (95,5%; 96,0%)**.
- G4 comparadores lag_cov, lag_abs, lag_square <=15% em H±:
  **PASSOU** (todos <=6,5%).
- G5 dependência de |X| detecta memória de volatilidade >=75%:
  **PASSOU (100%)**.
- G6 estatística oráculo h detecta H± >=80%:
  **PASSOU (100%)**.

## 5. O avanço geométrico e o seu limite

A trajetória de distribuições marginais é constante em H+/H-/N0, e
ainda assim as leis conjuntas q_eta(x_t,x_(t+1)) são distintas.
Logo, a observação somente de p_t — mesmo sem qualquer erro de estimação —
é insuficiente para reconstituir o tipo de dependência temporal.

**O ganho científico deste teste é demonstrar essa não identificabilidade
com controles lineares e de volatilidade casados.**
Não há demonstração de propriedade geométrica nova, porque:
- Fourier-HSIC é um detector convencional de dependência não linear;
- `oracle_h` tem conhecimento exato da função do mecanismo;
- sinais e momentos H3 convencionais também detectam parte da estrutura;
- escolhida de antemão a coordenada 0, não há busca de direção desconhecida;
- H± são REVERSÍVEIS, sem fluxo temporal antissimétrico;
- uma distribuição conjunta q não identifica unicamente uma causalidade física;
- apenas um gerador sintético foi considerado; não sabemos transferibilidade;
- a calibração assume o nulo conhecido, sem ajuste prefix-only aninhado;
- as demais estatísticas não têm correção de multiplicidade.

## 6. A próxima hipótese, ainda NÃO testada

M20c: geometria de acoplamentos condicionais (por exemplo Sinkhorn/OT em pares
ou distribuições condicionais) contra Fourier-HSIC, distance covariance,
MMD, CUSUM sobre embeddings e modelos estatísticos ajustados ao passado.
Impor cenários onde a direção e a forma da dependência são desconhecidas
ao detector, com prefix-only calibration e geradores heterogêneos.
Antes de BTC, exigir um benefício mensurável como robustez/poder em
distribuições não gaussianas, ou declarar equivalência a estatística clássica.
Não reaproveitar o período confirmatório do M19.
