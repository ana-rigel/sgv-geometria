# RASCUNHO — Pré-registro H-SGV-01: as variáveis de densidade, deslocamento e memória do sgv_original

**Estado: rascunho, NÃO congelado.** Escrito em 15/10/2026, a pedido de Ana: testar as variáveis do `sgv_original` que sobreviveram à varredura de 188 métricas, exceto o espaço original (coordenadas) e o que já está em teste (D(x), log ρ 3D e a forma de D, nos H-DIF-01 e H-FORMA-D-01). O congelamento só ocorre com o OK de Ana, antes de existir o arquivo mensal de outubro.

## 1. O que cada variável mede (código: `vendor/sgv_original` @ ac6b986, `SGVConfig()` padrão, causal)

Todas vivem no plano (E_norm, jerk) do SGV original. E_norm é o z robusto de (close − EMA₀,₀₅(close))/EMA: quanto o preço está esticado acima ou abaixo da sua média recente. jerk é a segunda diferença do retorno de 1 min: o "tranco".

| Variável | Fórmula | Em palavras |
|---|---|---|
| `rho_field` (`phi_field` = −log ρ) | Densidade KDE 2D (banda 0,35, unidades robustas) ajustada nos 7 dias anteriores, reajustada a cada 60 min | **Quão comum é o estado atual**, comparado com a última semana. φ alto = estado raro |
| `terrain_basin_depth` | log ρ − 0,6·\|∇log ρ\| (mesma KDE) | **Quão fundo o estado está num vale de estados comuns**; penaliza estar na encosta |
| `force_cell_n_obs` | Contagem de minutos dos 7 dias anteriores na mesma célula de uma grade 40×40 do plano | **Quantas vezes o mercado esteve "aqui"** na última semana (histograma) |
| `terrain_informational_displacement` | log(1 + Mahalanobis²) entre o estado atual e a média EWMA (α = 0,97, 80 barras) do próprio plano, com a covariância dessa janela | **Quão longe o estado está do seu centro dos últimos ~30 min**, em unidades da dispersão recente: surpresa de curto prazo |
| `mem_e` | EMA₀,₀₅(E_norm) | **Memória do esticamento**: há ~20–40 min o preço vem acima (+) ou abaixo (−) da sua média. Não é o `memory_flux` (que é a variação de `mem_e` e é coordenada do espaço original) |

## 2. Exploração (BTC jun–jul/2026, 8 semanas; `pipeline/explorar_sgv_original.py`)

Desenho idêntico ao do H-FORMA-D-01: alvo log Range dos 5 min seguintes, 1 minuto a cada 5, ρ parcial de Spearman semanal.

- **Controles primários:** σ 10/30/60; HAR 1 dia e 1 semana; retornos 5 e 30 min; log-volume 10 e 60; hora; memória de amplitude 1/5/10/30/60/1.440.
- **Controles secundários:** os primários + log ρ e log tr D do campo do H-DIF-01 (espaço original).

| Variável | ρ̄ primário | Semanas com o sinal | Nula de pipeline | ρ̄ com o campo do H-DIF-01 |
|---|---|---|---|---|
| log `rho_field` | **−0,079** | 8/8 | −0,005 | −0,020 |
| `basin_depth` | −0,078 | 8/8 | −0,006 | −0,020 |
| log(1 + `n_obs`) | −0,079 | 8/8 | −0,009 | −0,023 |
| `informational_displacement` | **+0,031** | 8/8 | −0,004 | −0,030 (inverte) |
| `mem_e` | **−0,027** | 8/8 | −0,003 | −0,020 |

**Correlação entre elas (Spearman):** log ρ, basin e n_obs = 0,98–0,997, ou seja, são a **mesma medida**. O deslocamento tem −0,55 com elas. `mem_e` é independente das outras (|ρ| < 0,04).

**Leituras da exploração:**
1. As três medidas de densidade são uma só construção: raridade no plano (E_norm, jerk). Entram no teste como uma hipótese só, com log ρ como primária.
2. A raridade do SGV é em boa parte a mesma informação do campo do H-DIF-01. Com log ρ e log tr D 3D nos controles, cai de −0,079 para −0,020.
3. O deslocamento informacional, sozinho, aponta "longe do centro recente → mais amplitude". Mas, com a raridade controlada, o sinal se inverte: o que ele carrega de positivo é a própria raridade.
4. `mem_e` é a única que sobra quase inteira com o campo nos controles (−0,027 → −0,020). O sinal é coerente com o efeito alavancagem (depois de quedas, mais amplitude), além dos retornos de 5 e 30 min já controlados.

## 3. Hipóteses (família m = 3, Holm, α = 0,05)

Para cada minuto amostrado, ρ parcial de Spearman com log Range_{t+5}, com os **controles primários**:

- **H-SGV-01a (raridade):** log `rho_field` < 0. Estados comuns na última semana antecedem menos amplitude.
- **H-SGV-01b (deslocamento):** `terrain_informational_displacement` > 0. Estar longe do centro dos últimos ~30 min antecede mais amplitude.
- **H-SGV-01c (memória do esticamento):** `mem_e` < 0. Preço que vem abaixo da média antecede mais amplitude.

**Secundárias (informativas, BH, não entram no veredito):**
- as três com os controles secundários (+ log ρ e log tr D do H-DIF-01);
- basin e n_obs no lugar de log ρ.

## 4. Julgamento

- **Dados:** BTCUSDT 1m de **outubro/2026**, mesmas semanas do H-DIF-01 e do H-FORMA-D-01: 01–08, 08–15, 15–22 e 22–29/10. Agosto e setembro só como aquecimento (os 7 dias da KDE do SGV e as EMAs).
- **Replicação:** novembro/2026, mesmo código, relatada à parte.
- **Estatística:** a do H-FORMA-D-01. Pares de resíduos agrupados das 4 semanas; p por permutação do alvo dentro de cada dia (B = 5.000, semente 20261013), unilateral no sinal registrado; Holm m = 3. Nula de pipeline só para leitura.
- **Dependência:** usa os mesmos minutos do H-DIF-01 e do H-FORMA-D-01. Os vereditos são relatados separadamente.

## 5. Poder (aproximação pelo desvio entre semanas da exploração; não é simulação)

| | Efeito como na exploração | Encolhido 40% | Encolhido 65% |
|---|---|---|---|
| a, raridade | ~100% | ~90% | ~50% |
| b, deslocamento | ~100% | ~85% | ~45% |
| c, memória | ~95% | ~65% | ~30% |

Com o encolhimento típico do programa (40–65%), uma refutação de b ou c não distingue efeito nulo de efeito pequeno. Antes de congelar, isso pode ser trocado por uma simulação igual à do H-FORMA-D-01.

## 6. O que cada resultado significa

- **a confirmada:** a raridade do estado no plano do SGV original antecede amplitude além da volatilidade e da memória de amplitude. É a peça mais antiga do SGV a passar num confirmatório. As secundárias dizem se ela acrescenta algo ao campo do H-DIF-01 (a exploração diz que pouco).
- **b confirmada:** a surpresa de curto prazo carrega amplitude. Pela exploração, deve ser a raridade vista de outro ângulo.
- **c confirmada:** a memória do esticamento carrega uma forma de alavancagem mais lenta que os retornos de 30 min. É a única variável aparentemente independente do campo.
- **Em nenhum caso há direção ou lucro.** Os ganhos esperados são frações de ponto percentual de R².

## 7. Aposta de Claude (antes dos dados)

a ~70%; b ~40%; c ~35%; as três ~15%.
