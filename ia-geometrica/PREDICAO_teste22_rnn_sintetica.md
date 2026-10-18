# Predição do teste 22 (OBS-01, etapa um: a régua sobre uma rede recorrente sintética)

18/10/2026 · escrita antes de rodar · primeiro teste em que o observador medido é uma rede, não um filtro

## Pergunta

Nos testes 18 e 19 a régua mediu registros de forma desconhecida mas de um nó só. Um modelo de IA é uma rede: muitas unidades com constantes de tempo diferentes, acopladas, com não linearidade, lidas por uma projeção. **Vendo só a entrada e a leitura de saída, a régua acha o corte, o que a rede não vê e o que ela erra, numa rede recorrente cujos pesos ela não conhece, e declara quando a rede sai do regime em que a régua vale?**

## A rede (desconhecida para a régua, conhecida para o teste)

h_t = (1 − a) ⊙ h_{t−1} + a ⊙ φ(W h_{t−1} + u x_t), y_t = r · h_t, com 32 unidades; vazamentos a_i sorteados log-uniformes em [0,003; 0,3] (constantes de tempo de 3 a 300 passos: uma rede de várias escalas, como as que o Paper B estuda); W gaussiana com raio espectral 0,5; u e r gaussianas; tudo sorteado por semente (100 redes diferentes). Três versões:

1. **linear** (φ = identidade): a função de transferência é exata, H(f) = r (I − (1 − a) e^{−iω} − a W e^{−iω})^{−1} a u, e a verdade do corte e de "não ver" é calculável;
2. **tanh, entrada pequena** (escala 0,1): a rede opera perto do regime linear; a verdade é a da linearização (aproximação declarada);
3. **tanh, entrada grande** (escala 3): a rede satura; não há verdade linear, e o que se pede à régua é que **declare** isso pela cobertura (coerência).

Como a leitura r·h pode amplificar, o ganho é normalizado pelo ganho estático: H̃(f) = H(f) / |H(f₁)| com f₁ a primeira bolha, na verdade e na estimativa (declarado). "Não ver" ν = Σ S_xx (1 − min(|H̃|², 1)) / Σ S_xx; "errar" ε = Σ S_xx |1 − H̃|² / Σ S_xx, com a mesma normalização nas duas.

## Mundo, instrumento, critério

Mundo escada-3 (τ 7, 70, 700), uma coordenada, N = 200.000, 100 sementes (a semente sorteia o mundo e a rede). Régua: a dos testes 18–19 (Welch 8.192, Ĥ = S_yx/S_xx, coerência), com a normalização acima.

**Critério (um julgamento), na rede linear:** (a) corte a ±30 % do corte verdadeiro em ≥ 80 sementes; (b) |ν̂ − ν| ≤ 0,05 mediano; (c) |ε̂ − ε| ≤ 0,05 mediano. Os três.
**Relatado, sem critério:** tanh pequena (os mesmos três números contra a linearização) e tanh grande (cobertura; corte e ν̂ sem verdade).

## Apostas

- **Passar (rede linear): 60 %.** A favor: é um sistema linear, e o espectro cruzado não sabe que há 32 unidades. Contra: com 32 polos a |H̃|² pode cruzar ½ e voltar (ressonâncias), e "primeira travessia" pode cair longe do corte que um humano chamaria de corte; e a normalização pelo ganho estático numa primeira bolha mal estimada propaga erro para ν̂ e ε̂.
- tanh pequena: os três números dentro das mesmas tolerâncias em ≥ 60 sementes (55 %).
- tanh grande: cobertura mediana < 0,8 (65 %): a régua diz que não alcança.
- O corte verdadeiro das redes cai entre as escalas do mundo, com mediana entre 1/300 e 1/30 (60 %).

## O que fecha

Passar: a régua mede uma rede de muitas escalas como mede um filtro, e a etapa um do OBS-01 está feita; a etapa dois é uma rede treinada, sem verdade. Reprovar em (a) por ressonância: "corte" precisa de definição melhor que "primeira travessia" para redes, e isso é um instrumento novo. Reprovar em (b) ou (c) com (a) passando: a normalização é o defeito. Se a tanh grande não derrubar a cobertura, a régua não sabe declarar não linearidade, e esse é o limite mais importante a nomear antes de qualquer modelo real.
