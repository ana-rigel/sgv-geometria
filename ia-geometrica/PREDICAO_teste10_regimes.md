# Predição do teste 10 (a política de expectativa num mundo com regimes)

18/10/2026 · escrita antes de rodar · corrige o defeito 17 dos testes 2 e 7, e só ele

## Pergunta

Nos testes 2 e 7 a política de olhar empatou com o periódico num AR(1), e a leitura do 7 disse por quê: nesse mundo não há momento certo de olhar. **Num mundo em que a tensão vem em blocos (regimes quente e frio persistentes), a política de expectativa, com a mesma fração de olhadas, deixa a memória mais perto do mundo do que olhar em ritmo fixo?**

## O que muda e o que não muda

- **Mundo "quente/frio":** AR(1) com φ = 0,9 cujo desvio do ruído alterna entre σ = 1 (frio) e σ = 3 (quente) em blocos de duração geométrica com média 200 passos, começando frio. É o parente mais simples do que o MSM mediu no BTC (volatilidade em andares persistentes). Nada mais muda no mundo.
- **Tudo o mais igual ao teste 7:** N = 8.000, 100 sementes, k = 4, λ₁ = 0,15, b = 10; régua e expectativa a_n + b_n · T₀ aprendidas em [0, 2.000) olhando sempre; n_max = 16; θ afinado em [2.000, 4.000) para 25 % ± 1 pp; medida em [4.000, 8.000); erro de predição ‖x_t − R₁,t−1‖; nulo periódico a cada 4; teto olhar sempre; V = 1 − e_v0 / e_periódico.

## Critério (um julgamento)

O dos testes 2 e 7: envelope de V acima de zero nas sementes válidas, e fração em 25 % ± 3 pp em ≥ 95 sementes.

## Apostas

- **Passar: 55 %.** A favor: no quente o erro da memória é ≈ 3 vezes o do frio, e a tensão lida diz em que bloco se está (os blocos duram 200 passos; b_n deve ficar alto por muito mais que os 5 passos do teste 7). Uma política que olha mais no quente e menos no frio reduz o erro total com o mesmo orçamento; o periódico não distingue. Contra: o erro está dominado pelo quente de qualquer jeito, e o ganho de redistribuir 25 % de olhadas pode ser pequeno demais para o envelope inteiro ficar acima de zero em 100 sementes; e a afinação de θ com blocos raros pode falhar na faixa (defeito 5).
- V média entre +3 % e +12 % (60 %); V > 0 em ≥ 90 sementes (65 %).
- b_n médio acima de 0,2 até n = 16 (75 %).

## O que fecha

Passar: o único ato da v0 vale alguma coisa, e vale exatamente onde o mundo tem regimes, que é o caso do mercado; o teste 2 estava mal posto como mundo, não como pergunta. Reprovar com V média positiva: idem, com o critério de envelope dizendo que não é consistente; fica reprovado. Reprovar com V ≤ 0: a expectativa linear em T₀ não captura o regime, e a política precisa de uma variável de regime própria, com predição própria.
