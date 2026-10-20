# Leitura do teste 36 (ela aprende com o erro?): J1, J2, J3 e J4 PASSARAM; J5 REPROVADO pelo controle invertido, que estava mal posto. O laço aprende com o erro, e no mundo real acompanhou o atraso da entrada nos seis lugares

**Predição:** PREDICAO_teste36_aprende_com_o_erro.md (09145f4), antes de escrever o instrumento. **Instrumento:** teste36.py. **Resultados:** resultados_teste36.json; diagnostico_teste36.json (depois da rodada, não julgado). η = 0,3; 100 mundos por condição; ruído das anomalias reais de 2010–2017 (48 valores, desvio 13,4 dias). Cinco julgamentos; sem emenda.

| | medida | resultado | critério | |
|---|---|---|---|---|
| **J1** aprende (semente −30 d) | média de \|p₇ − 280\|; mundos mais perto que a semente | **5,6 d**; **100** de 100 | ≤ 10 d; ≥ 90 | **passou** |
| **J2** readapta (degrau +20 d) | mundos com pós − pré ≥ 10 d (mediana 16,7 d) | **82** de 100 | ≥ 80 | **passou** |
| **J3** readapta no mundo real | lugares em que μ andou ≥ +6 d de 2018 a 2025 | **6** de 6 | ≥ 4 | **passou** |
| **J4** não aprende ruído (sem mudança) | deriva média; mundos a menos de 15 d | **−0,45 d**; **100** de 100 | ±3 d; ≥ 95 | **passou** |
| **J5** depende do erro e da ordem | ordem embaralhada: mundos ≥ 10 d (mediana 0,6 d) · erro invertido: mundos com pós − pré < 0 | **12** de 100 · **62** de 100 | ≤ 20 · ≥ 90 | **reprovado** |

Erro absoluto médio por estação, média nos mundos (dias):

| estação | 1 | 2 | 3 | 4 | 5 | 6 | … | 12 | **13** | 14 | 15 | 16 | 17 | … | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A, semente errada | 30 | 24 | 17 | 14 | 13 | 12 | | 12 | 12 | 12 | 13 | 12 | 12 | | 14 |
| B, degrau na 13ª | 11 | 12 | 13 | 11 | 12 | 11 | | 12 | **21** | 16 | 16 | 13 | 14 | | 14 |
| D, ordem embaralhada | 15 | 14 | 15 | 15 | 14 | 13 | | 15 | 14 | 14 | 15 | 16 | 14 | | 15 |

No mundo real (μ₀ = média das entradas de 2010–2017; aprende com 2018–2025):

| lugar | μ₀ (dia do ano) | μ no fim de 2025 | andou |
|---|---|---|---|
| Juara | 272,9 | 284,4 | **+11,5** |
| Sinop | 275,9 | 288,6 | **+12,7** |
| Cuiabá | 279,0 | 303,7 | **+24,7** |
| Barra do Garças | 288,2 | 299,4 | **+11,1** |
| Alta Floresta | 276,4 | 286,5 | **+10,1** |
| Rondonópolis | 287,0 | 310,9 | **+23,9** |

Apostas: J1 (95 %), certa; J2 (80 %), certa, na beira (82 contra 80); J3 (55 %), certa, e com folga (6 de 6, o menor andou 10 d); J4 (85 %), certa; J5 (80 %), **errada**, pela parte invertida.

## Diagnóstico depois da rodada (não julgado)

O laço invertido, μ ← μ − η e, multiplica por 1,3 a cada estação a distância entre μ e a entrada. Na 13ª estação, a explosão vinda do ruído das primeiras já domina tudo: mediana de ≈ 300 dias de distância no mesmo mundo **sem** degrau. O sinal de pós − pré passa a ser o sinal dessa explosão, que é aleatório; daí os 62 de 100. Comparando o mesmo laço invertido nos mesmos ε, com e sem degrau, o efeito do degrau é negativo em **100 de 100** mundos (mediana −56 d). O laço invertido anda para o lado errado sempre; o controle é que media a explosão e não o degrau.

## O que o resultado diz

**1. O laço aprende com o erro, e só com o erro.** As quatro assinaturas apareceram. Partindo 30 dias errado, o erro cai de 30 para o piso do ruído (≈ 12 d) em cinco entradas. Quando o mundo muda 20 dias, o erro sobe para 21 na estação da mudança e volta ao piso em três ou quatro. Sem mudança, nada deriva (−0,45 d). E com as mesmas entradas em ordem embaralhada, a curva de aprendizado some: o erro fica parado em ≈ 15 d, sem queda e sem pico, e a readaptação cai de 82 para 12 de 100. É a ordem dos erros, e não só o seu tamanho, que move o relógio.

**2. No mundo real, ele seguiu o atraso que o calendário não viu.** Nos seis lugares, μ andou de +10 a +25 dias entre 2018 e 2025. Os maiores passos vieram dos anos de entrada muito tardia (2020 e 2023, com erros de +23 a +49 d). É o atraso de ≈ 13 dias do teste 35, agora dentro da v0. Em Cuiabá e Rondonópolis o relógio andou o dobro dos outros, porque lá a entrada atrasou mais; ele não aprendeu um número global, aprendeu o lugar.

**3. A velocidade tem preço.** Com η = 0,1, readapta devagar (30 de 100 no degrau) e quase não sente o embaralhamento; com η = 0,5, readapta mais (86), mas aprende mais do ruído (21 de 100 no embaralhado). Um relógio que aprende de um evento por ano leva três a quatro anos para acompanhar uma mudança, e treme ≈ 6–8 dias em volta do valor certo. Para uma placa, isso é lento; o caminho para aprender mais rápido são eventos mais frequentes.

**4. Isto é o primeiro laço, o menor possível.** A v0 agora muda uma parte da própria forma (μ) pelo que errou. Os λ, a régua e o acoplamento continuam fixos. Este teste não mostra que a v0 aprende a sua forma inteira; mostra que o tipo de aprendizado que faltava funciona quando é posto.

## Para a lista de defeitos de desenho

50. O controle do erro invertido usou um laço instável e julgou pelo sinal de pós − pré. Num laço que diverge, a trajetória depois de 12 estações é dominada pelo ruído amplificado das primeiras, e o sinal mede a direção da explosão, não o efeito do degrau. A conta prévia anotou a divergência ("cresce 1,3 vez por estação") e não tirou a consequência. O controle certo compara o laço invertido com e sem degrau, nos mesmos ε.

Placar: 36 testes numerados (o 25 sem resultado). 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram; 36: J1–J4 passaram, J5 reprovou. 50 defeitos, 1 emenda.
