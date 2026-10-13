# SGV-M34 — Engenharia: deformações da casca (M8–M11) como variáveis causais

**Ramo:** `research/m34-engenharia-deformacoes`. **`main` intocada. Nenhum dado novo, nenhum desempenho preditivo de G ou E calculado.** Só BTC 1m mai–jul/2026 (já gasto) e sintético. Pedido: auditoria do M33 (issue #5).

## 1. Variáveis (`experiments/m34_deformacoes.py`)
Na origem t, **só** a janela [t−1499, t] (a janela original do M11 no 1m) → `split_historical` (âncora de 30% + metades A e B) → instrumentos originais, sem alteração.

| Grupo geométrico G | instrumento | Grupo econométrico E (mesma capacidade, mesmas metades) |
|---|---|---|
| `trans` deslocamento do centro | M8 `motion` | `dmean` variação da média (norma) |
| `dlogvol` expansão log(V_B/V_A) | M8 | `dlogdet` variação do log-det da covariância |
| `rot` rotação no quociente SO(3)/D2 | M9 | `dcorr_zi`, `dcorr_zn`, `dcorr_in` |
| `rot_ok` orientação identificável | M9 | `dlogsd_z`, `dlogsd_i`, `dlogsd_n` |
| `m11` deformação residual (ICP, ponto–triângulo) | M11 | `energy` distância de energia A–B |
| `jacc` Jaccard das regiões HDR50 | M3/M10 | `dkurt` variação média da curtose |
| `saddle_b`, `dsaddle` área em sela atual e variação | M1/M32 | |
| `kmed_b`, `dkmed` mediana da curvatura e variação | M1 | |

Falha de malha ou ICP → G inválido na origem (registrado, nunca imputado). 4 testes aprovados: deslocamento e expansão conhecidos são detectados; metades transformadas reduzem o Jaccard; só a janela até t é usada; capacidade 10 = 10.

## 2. Custo e validade (1.079 origens amostradas, 1 a cada 8)
- **1,13 s por origem** → ~2,7 h de CPU por trimestre (exige lotes no Actions).
- **97,8% válidas** (23 malhas inválidas, 1 falha de ICP).

## 3. Confiabilidade (bootstrap em blocos de 15 min dentro de cada metade; 40 origens × 8 réplicas)
Confiabilidade = 1 − variância do ruído de estimação / variância total ao longo do tempo.

| G | conf. | E | conf. |
|---|---|---|---|
| trans | 0,76 | dmean | 0,82 |
| dlogvol | 0,72 | dlogdet | 0,74 |
| jacc | 0,80 | energy | 0,84 |
| kmed_b | 0,69 | dlogsd_i / dlogsd_n | 0,88 / 0,78 |
| saddle_b | 0,47 | dkurt | 0,57 |
| dkmed | 0,38 | dcorr (3) | 0,48–0,53 |
| rot_ok | 0,36 | **dlogsd_z** | **< 0 (ruído)** |
| m11 | 0,32 | | |
| dsaddle | 0,20 | | |
| **rot** | **≈ 0 (ruído)** | | |

## 4. Redundância (correlação máxima de cada G com algum E; sem alvo)
`trans` 0,97 (≈ `dmean`), `dlogvol` 0,96 (≈ `dlogdet`), `jacc` 0,89 (≈ `energy`), `dkmed` 0,65, `kmed_b` 0,43, `m11` 0,19, `dsaddle` 0,18, `saddle_b` 0,09, `rot`/`rot_ok` < 0,1.
**Leitura:** deslocamento, expansão e Jaccard são, na prática, mudanças de momentos. Só M11, curvatura e orientação carregam algo distinto, e são justamente as **menos confiáveis**.

## 5. Regularização (só placebos e sinal plantado; `reports/m34/ridge_grupo.json`)
Com ridge 100 em tudo, 10 placebos pioram o baseline em ~1%. Ridge forte em tudo piora o próprio baseline (deviança 0,346 → 0,352 com 1000). **Ridge separado: 100 no B0, R no grupo novo:**

| R do grupo | penalidade de 10 placebos | ganho retido de 1 sinal plantado entre 10 |
|---|---|---|
| 100 | 1,04% | 0,56% |
| **1000** | **0,30%** | **0,72%** |
| 3000 | 0,09% | 0,46% |
| 10000 | 0,01% | 0,19% |

**Escolha: R = 1000 para o grupo novo** (melhor retenção de sinal, penalidade baixa).

## 6. Desenho proposto para o pré-registro (NÃO congelado; decisão da Ana)
Critérios sem alvo: tirar a variável de ruído puro de cada grupo (`rot` em G, `dlogsd_z` em E) → **G9 e E9**, capacidade igual.
1. **Primário:** B0 + G9 contra B0 (a geometria das deformações acrescenta algo?). Critério: p < 0,05 com HAC de 1 dia **e** de 1 semana, e skill ≥ 0,5%.
2. **Atribuição (hierárquico):** B0 + E9 + G9 contra B0 + E9 (geometria além dos momentos, com a mesma capacidade).
3. **Descritivo:** B0 + G9 contra B0 + E9 (não aninhado, mesma capacidade).
4. Ridge 100 no B0 e 1000 no grupo; treino de 14 dias; elegibilidade só pelo passado; origens com G inválido fora dos contrastes que usam G.
5. **Dados:** uma amostra **nova e nunca vista** (escolha da Ana). Custo: ~3,5–4 h de CPU para 5 meses → 20 lotes no Actions.

**Aposta antecipada (antes de qualquer dado):** primário ~6%; atribuição ~3%. As variáveis que poderiam carregar algo novo são as de menor confiabilidade, e as confiáveis repetem os momentos.
