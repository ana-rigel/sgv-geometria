# Predição do teste 1 (deriva): a pilha de registros rastreia melhor que o melhor registro único?

**Registrada em:** 17/10/2026, antes de rodar. Detalha a linha 1 da tabela de PROJETO_v0.md.

## Precisão de desenho, registrada antes de rodar

Na arquitetura v0 o andar 1 não depende dos andares acima; sozinho, ele é um registro único com λ = 0,15. Logo "a pilha rastreia melhor" exige uma **leitura** que use os andares. Definição: a previsão da pilha um passo à frente é x̂_t = Σ_j w_j · R_{j,t−1}, com os pesos w ajustados por mínimos quadrados num **segmento de calibração** (primeiros 2.000 passos) e avaliados **fora dele** (passos 2.001 a 6.000). O nulo recebe o mesmo tratamento: um registro único com ganho λ e leitura escalar x̂_t = a · R_{t−1}, com a ajustado no mesmo segmento. O melhor λ do nulo é escolhido na grade {0,05; 0,10; …; 0,95} **pelo erro fora da calibração** (escolha generosa com o nulo). Rastrear = prever o próximo passo; usar R_t para "prever" x_t seria trivial.

## Mundo e parâmetros

- Campo: AR(1) em ℝ², x_t = φ·x_{t−1} + ε_t, ε ~ N(0, 1), φ ∈ {0; 0,5; 0,9; 0,99}. n = 6.000 passos. 100 sementes (1000–1099).
- v0: k = 4, λ₁ = 0,15, b = 10 (fixos). Olha sempre (o custo é do teste 2).
- Erro = média de ‖x_t − x̂_t‖ nos passos 2.001–6.000.
- Vantagem relativa V(φ) = 1 − erro_v0 / erro_melhor_único, por semente; relata-se a média e o envelope (mín–máx) das 100 sementes.

## Critério (como registrado no projeto, agora com números)

- **Passa** se: (a) V(φ) média > 0 em φ = 0,5, 0,9 e 0,99; (b) V cresce monotonicamente nos quatro pontos (V(0) < V(0,5) < V(0,9) < V(0,99)); (c) em φ = 0 a vantagem é nula: |V(0) média| < 2 %.
- **Reprova** se qualquer um dos três falhar. Sem emendas de parâmetro depois de ver o resultado; só defeito de instrumento (código que não faz o que a predição diz), registrado.

## Apostas

| Aposta | Probabilidade |
|---|---|
| Teste passa (a, b e c) | 55 % |
| (a) V > 0 nos três φ > 0 | 70 % |
| (b) monotônica | 60 % |
| (c) nula em φ = 0 | 85 % |
| V(0,99) entre 2 % e 15 % | 50 % |

Por que não mais: para um AR(1), o previsor ótimo é φ·x_{t−1}, e um registro único com λ alto já chega perto dele; o que a pilha pode acrescentar é pouco e vem da soma de escalas. Se a vantagem for grande, desconfio do instrumento antes de comemorar.
