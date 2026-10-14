# SGV-U2 — o vetor M11-I rotula o mecanismo de uma mudança melhor que um painel convencional?

**Registrado em 13/10/2026, antes de qualquer execução do código abaixo.** Exclusivamente sintético; sem dados de mercado.
Continuação do SGV-U01 (Ana Rigel), que mostrou que o M11-I não é detector superior. Aqui a pergunta é a U2 do relatório: *explicar*.

## Desenho

- **Famílias geradoras (3):** latente 3D padronizado — F1 gaussiano; F2 t de Student com 6 g.l.; F3 assimétrico (lognormal centrado e padronizado por eixo, σ = 0,5). Observado = latente · Lᵀ + m, com covariância aleatória por réplica (autovalores U[0,5; 2], rotação aleatória) e m aleatória.
- **Mecanismos (7 classes)**, cada um aplicado a uma amostra nova B₀ da mesma família da amostra A:
  - `nenhum`: B = B₀.
  - `translacao`: B = B₀ + δ·σ_u·u, u unitário aleatório, δ ~ U[0,25; 0,5], σ_u = desvio de A na direção u.
  - `escala`: B = m̂ + s·(B₀ − m̂), s ~ U[1,15; 1,30] ou 1/s (½ cada).
  - `rotacao`: B = m̂ + (B₀ − m̂)·Rᵀ, eixo aleatório, ângulo U[20°; 40°].
  - `bimodal`: no latente, a projeção numa direção aleatória vira a·sinal + √(1−a²)·ruído, a ~ U[0,75; 0,90].
  - `curvatura`: no latente, z ← z + c·((z·v₁)² − 1)/√2 · v₂, c ~ U[0,5; 0,8].
  - `caudas`: no latente, cada ponto é multiplicado por 2,5 com probabilidade 0,10.
  - Nas três classes de forma, B é depois transformado linearmente para ter a média e a covariância **amostrais de B₀** (não de A): Δmédia e ΔCov ficam com o ruído amostral da classe `nenhum`, e não iguais a zero — sem vazamento de rótulo por "momento exatamente igual".
- **Tamanho:** N = 750 por amostra; 30 réplicas por família × 7 classes = 630 comparações.
- **M11-I:** `build_shell` + `signature` do instrumento histórico (SHA 15ee5a5d…), grade 25³, entradas em **ordem lexicográfica canônica**, semente compartilhada por réplica.

## Painéis (as mesmas comparações para os dois)

- **M11-I (5 variáveis, como proposto):** `translation_norm`, `delta_log_volume`, `theta_deg` (nulo → 0 e indicador de θ não identificável), `distance_512`, ΔD binário (1 se ΔD > 0,01).
- **Convencional forte (11 variáveis):** no referencial branqueado de A: ‖Δmédia‖; os 3 log-autovalores generalizados de Cov_B em relação a Cov_A (ordenados); ângulo entre os autovetores principais; 3 diferenças de curtose por eixo (ordenadas); ‖Δcoassimetria‖ e ‖Δcocurtose‖ (normas de Frobenius dos tensores de 3ª e 4ª ordem); MMD² RBF (banda pela mediana em A).
- **Combinado:** os dois juntos — mede se o M11-I acrescenta algo ao convencional.
- **Sensibilidade (não entra nas apostas):** M11-I com ΔD contínuo em vez de binário.

## Classificação e validação

- Mesmo classificador para os três painéis: floresta aleatória (500 árvores, semente fixa) e, como segundo, regressão logística multinomial com padronização.
- **Validação deixando uma família inteira de fora:** treina em duas famílias, testa na terceira; repete para as três e agrega.
- Métricas: sensibilidade (recall) por classe, F1 macro, matriz de confusão. IC de 95% por bootstrap das réplicas (2.000). "Empate" = |Δrecall| < 0,05.

## Apostas de Claude (antes de rodar), com a floresta aleatória

| Classe | Aposta: recall M11-I vs convencional |
|---|---|
| translacao | empate ou M11-I pior |
| escala | empate ou M11-I pior |
| rotacao | M11-I pior (θ é nulo quando a orientação não é identificável) |
| bimodal | M11-I ligeiramente melhor (ΔD) |
| curvatura | M11-I ligeiramente melhor (ΔD + resíduo) |
| caudas | M11-I pior (HDR50 não vê fora dela) |
| nenhum | empate |

- F1 macro: convencional > M11-I. Combinado ≈ convencional (ganho < 0,03).
- Se der isso: o lugar honesto do SGV é "rotulador de forma" (não convexidade), não detector nem classificador geral.
- Se o M11-I não ganhar nem em bimodal/curvatura: nem isso — a assinatura vira só visualização.
