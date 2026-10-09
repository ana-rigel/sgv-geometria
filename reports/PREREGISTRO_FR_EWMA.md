# Pré-registro H-FR-EWMA: curvatura Fisher–Rao da trajetória gaussiana

**Data:** 09/10/2026 (UTC). **Status:** congelado antes de qualquer resultado desta especificação. O portão exploratório (Etapa 1) roda logo após este commit. O confirmatório (Etapa 2) depende da revisão da Ana.

**Código congelado:**
- `experiments/fisher_rao_ewma.py`, SHA-256 `d6a447e77a3395b685d163ec41646d891fe44f6a3afc881a7b9b5b7928d3ddc6`
- `tests/test_fisher_rao_ewma.py`, SHA-256 `efb8de3d5a43e00a11ef70e0d17ea78426dc08f7b48b5918574284941ba2c7da`

O código só passou por testes sintéticos (geometria com resposta conhecida e causalidade) e por uma checagem mecânica nos dados de exploração (tamanhos e NaN). Nenhuma perda nem métrica de desempenho foi calculada com esta especificação antes deste commit.

## 1. Origem e lugar no plano

- **Experimento gerador:** `experiments/fisher_rao_trajectory.py`. Com janela retangular de 1.500 barras, a curvatura reduziu o MSE do range futuro em 1,44% (1m) e 0,88% (1h) contra o controle com derivadas.
- **Auditoria** (`experiments/fisher_rao_auditoria.py`):
  - com o range passado no modelo, o ganho foi a −0,01% nas duas escalas;
  - 25–35% de log(1+κ) é explicado por |r| recentes e pelo retorno que sai da janela retangular. Chamamos isso de "eco" de 1.500 barras.
- **Lugar no PLANO.md:** o G1 foi reprovado em 1m e 1h, e o plano permite **uma** reformulação, pré-registrada antes de rodar. **Esta é essa reformulação.** Se ela não confirmar, a linha geométrica do `sgv-geometria` fecha.

### Mudanças em relação ao experimento gerador

Foram fixadas por argumento, sem olhar resultado:

1. **EWMA no lugar da janela retangular:** elimina o eco. O span é 1.500, com o mesmo centro de massa da janela original, para isolar o efeito da troca.
2. **Diferenças só para trás:** κ_t é causal por construção, sem deslocamento ad hoc.
3. **Alvo em log:** log do range, como no HAR. O MSE deixa de ser dominado por picos.
4. **Controle forte (M0):** o que derrubou o sinal na auditoria passa a ser obrigatório.

## 2. Hipótese

**H-FR-EWMA.** A curvatura geodésica κ_t da trajetória (μ_t, σ_t) na métrica de Fisher da gaussiana tem informação preditiva fora da amostra sobre o log do range futuro, **além** de volatilidade recente, GARCH, sazonalidade horária, estado (μ, σ) e derivadas da trajetória.

- **H0:** E[d_t] ≤ 0, com d_t = perda(M0) − perda(M1).
- **H1:** E[d_t] > 0.

## 3. Especificação congelada

| Item | Valor |
| --- | --- |
| Ativo / dados | BTCUSDT spot, klines `data.binance.vision` |
| Retorno | r_t = log(close_t / close_{t−1}); NaN quando há lacuna (o estado não atualiza) |
| Estados | EWMA, λ = 1 − 2/1501. μ_t = λμ_{t−1} + (1−λ)r_t; σ²_t = λσ²_{t−1} + (1−λ)(r_t − μ_{t−1})² |
| Métrica | ds² = (dμ² + 2dσ²)/σ² |
| Curvatura | geodésica, velocidade e aceleração por diferenças para trás (t, t−1, t−2); κ² = (\|a\|²\|v\|² − ⟨v,a⟩²)/\|v\|⁶; variável = log(κ + 10⁻¹²) |
| Alvo | log R, com R = log(max high / min low) em t+1..t+h; h = 5 (1m), 4 (1h); exige as h barras contíguas |
| M0 | r_t..r_{t−4}; \|r_t\|..\|r_{t−4}\|; log range da barra t e médias móveis do range (5, 15, 60 em 1m; 4, 24, 168 em 1h); log σ_t; μ_t/σ_t; u/σ, v/σ, du/σ, dv/σ; 23 dummies de hora UTC; log da variância GARCH(1,1) prevista para t+1..t+h |
| M1 | M0 + log κ_t |
| Estimador | ridge λ = 10, variáveis padronizadas no treino, intercepto livre |
| Treino | janela expansiva: tudo antes do início do fold, menos embargo de h + 4 barras |
| GARCH | gaussiano, média zero, parâmetros estimados só antes do primeiro bloco de teste e depois fixos |
| Aquecimento | 4.500 barras no início; ≥ 171 barras contíguas desde a última lacuna (nada atravessa lacuna) |
| Teste | Diebold–Mariano unilateral sobre d_t, variância HAC de Newey–West com lag de 1 dia (1.440 barras em 1m, 24 em 1h) |

## 4. Etapas e regras de decisão

### Etapa 1: portão exploratório

Roda só nos dados de exploração (1m: mai–jul/2026; 1h: 2020–2024). O teste é a segunda metade das linhas válidas, em 6 blocos.

- **Passa** numa escala se ganho relativo > 0 **e** p unilateral < 0,10.
- Uma escala que não passa para por aqui e não gasta o período confirmatório.
- **Se nenhuma escala passar, a hipótese é encerrada sem tocar o confirmatório.**

Estes dados já foram usados pelo experimento gerador, na versão retangular. Por isso o portão é um filtro barato, não evidência.

### Etapa 2: confirmatório

Só para as escalas que passarem no portão, e só depois da revisão da Ana registrada em commit.

**Períodos fixados agora:**
- **1m:** ago e set/2026. Out/2026 fica para a réplica prospectiva, junto com nov–dez, como já estava no PLANO.
- **1h:** jan/2025 a set/2026.

**Procedimento:**
- O treino inicial é o período de exploração inteiro. Cada mês do confirmatório é um bloco, treinado com tudo o que veio antes, menos o embargo.
- O GARCH é estimado só com dados de exploração.
- **Rodada única.** Os dados confirmatórios são baixados depois do commit da revisão.
- **Decisão:** correção de Holm entre as m escalas que entrarem, α = 0,05 unilateral. A hipótese é **confirmada** numa escala se ela sobreviver ao Holm.

## 5. Critério de morte e de relevância

- **Morte:**
  - nenhuma escala passa no portão; ou
  - nenhuma escala confirma.

  Nos dois casos a linha geométrica do `sgv-geometria` fecha, sem nova reformulação, como manda o PLANO.
- **Relevância:** confirmado com ganho < 0,5% do MSE vira "real, mas irrelevante" e **não** segue para a Fase 4. Com ganho ≥ 0,5%, segue para um pré-registro novo de utilidade econômica.

## 6. Quem paga e por que continua pagando?

**A resposta é fraca, e está registrada como fraca.**
- **O que a variável faria:** prevê amplitude, não direção. Sozinha, não gera lucro em spot.
- **Canais possíveis:**
  - (a) opções de BTC, se a previsão de volatilidade realizada de curto prazo superar a implícita;
  - (b) dimensionamento de posição e distância de stop no portfólio aprovado, que usa a volatilidade como insumo.
- **Por que continuaria pagando:** nos dois canais, a resposta seria só a de qualquer vantagem informacional em previsão de volatilidade, que costuma ser pequena e se dissipar.

A Ana decidiu seguir conscientemente pelo valor científico. A pergunta volta, obrigatória, na Fase 4.

## 7. Descritivos (não decidem nada)

- Ganho por bloco.
- R² de log κ explicado pelas variáveis de M0, nas linhas de teste.
- Previsões individuais salvas em `reports/FR_EWMA_*_perdas.csv.gz`, para auditoria independente.

## 8. Proibições

- **Nada muda depois do portão:** nem span, nem alvo, nem horizonte, nem controles, nem ridge, nem lag HAC, nem regra de lacunas.
- **Sem escolher escala pelo resultado:** a regra do portão já decide.
- **Sem variantes** (outros spans, outra métrica, κ sem log, modelo não linear) na Etapa 2.
- **Correção de bug** só por emenda datada neste documento. A emenda explica por que não altera a especificação e é feita antes de qualquer número confirmatório.

## 9. Aposta do Claude (antes dos dados, tradição da casa)

- P(passar no portão em ≥ 1 escala) ≈ 25%.
- P(confirmar em ≥ 1 escala) ≈ 8%.
- P(confirmar com ganho ≥ 0,5%) ≈ 3%.

**Raciocínio:** o ingrediente principal de κ é o par (u, v), que é função de r_t e da inovação quadrática. M0 já contém essas variáveis e |r|. O que sobra para κ é uma interação não linear específica entre as três últimas inovações, normalizadas por σ. A favor, há só um sinal fraco: na auditoria, o boosting extraiu algo de κ, mas apenas num modelo mal especificado.
