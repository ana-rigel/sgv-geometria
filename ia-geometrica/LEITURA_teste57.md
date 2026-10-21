# Leitura do teste 57 (a hipótese do regime crítico, de novo): J1, J2 e J3 PASSARAM; J4 REPROVADO. O relógio do andar 2 funciona melhor perto da borda do travamento (0,7 ε_c), pelos dois critérios e pelo mecanismo previsto; mas nem na borda a fase ouvida chega ao calendário

**Predição:** PREDICAO_teste57_borda_critica.md (adf59ee), antes de calcular, com o piloto de dois mundos rodado antes. **Instrumento:** teste57.py. **Resultado:** resultados_teste57.json. O piloto refeito no instrumento reproduziu a tabela da predição número a número. Quatro julgamentos; sem emenda.

## Resultados (6 lugares; ε_c = 0,0050–0,0054)

| ε/ε_c | 0,2 | 0,3 | 0,4 | 0,5 | **0,7** | 1 | 1,5 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EAM das águas (42 previsões, d) | 49,4 | 46,0 | 33,6 | 28,4 | **24,5** | 26,1 | 31,3 | 37,7 | 66,7 | 371,6 | 98,0 |
| dp da fase em 1/09 (mediana, d) | 39 | 19 | 18 | 15 | **10** | 11 | 16 | 19 | 24 | 27 | 24 |

Por lugar, o mínimo do EAM fica em 0,7 ε_c em Juara, Sinop, Cuiabá e Barra do Garças, empatado entre 0,5 e 0,7 em Rondonópolis, e em 5 ε_c em Alta Floresta (21 contra 26 a 0,7). O mínimo do espalhamento da fase fica em 0,7–1 ε_c nos seis lugares. Em Cuiabá e Rondonópolis, acima de 2 ε_c, a fase escorrega e o EAM explode (97 a 1.526 dias).

| | resultado | critério | |
|---|---|---|---|
| **J1** o ótimo do EAM está na borda | **0,7 ε_c** | 0,5–2 ε_c | **passou** |
| **J2** interior e marcado | 24,5 contra min(49,4; 98,0) | ≤ −5 d | **passou** (−24,9) |
| **J3** o mínimo do ruído de fase está na borda | **0,7 ε_c** | 0,5–2 ε_c | **passou** |
| **J4** na borda exata, ≤ calendário | 26,1 contra 20,0 | | **reprovado** |

Apostas: J1 (55 %), J2 (50 %) e J3 (65 %) certas; J4 (30 %) certa a reprovação.

**Piloto contra o real:** o piloto pôs o mínimo do ruído de fase em 0,5–1 ε_c, e o real deu 0,7–1. Ele acertou o lugar e errou o nível: 6 dias no piloto contra 10–11 no real, e 17–19 em Cuiabá e Rondonópolis. O piloto só usou Juara.

## O que o resultado diz

**1. A hipótese do regime crítico ganhou a sua primeira evidência limpa.** No único sistema em que pôde ser testada sem o número da galáxia, o melhor acoplamento com o mundo ficou perto da borda do travamento, pelos dois critérios e pelo mecanismo nomeado antes:
- **abaixo da borda,** o relógio não pega o ano (EAM 46–49 dias a 0,2–0,3 ε_c);
- **acima dela,** ele trava, mas é escravo do ruído do campo: o espalhamento da fase sobe de 10 para 24–27 dias e, onde o ano é irregular, ele escorrega;
- **perto da borda,** ele aprende o ano e o ruído entra com o menor peso.

A frase da ideia original vira um princípio de projeto testado: **acoplar o relógio ao mundo no limite do travamento.**

**2. O ótimo fica um pouco abaixo da borda estática (0,7 ε_c), e o piloto já mostrava isso.** Com o aprendizado da frequência, o relógio pega o ano por arrasto antes de a forçante sozinha conseguir travá-lo. A borda dinâmica (quem aprende) fica abaixo da estática (quem trava sem aprender).

**3. O que isso não é.** O mecanismo é o compromisso clássico de qualquer laço de fase (PLL): banda estreita demais não captura o sinal, banda larga demais deixa entrar o ruído. É "crítico" no sentido de ficar na fronteira entre travar e não travar, que é o sentido da hipótese. Não é evidência de nenhuma propriedade especial além dessa, nem diz nada sobre a galáxia ou sobre uma "mente". A afirmação que o teste sustenta é: **para um relógio que aprende com o erro contra o mundo, o melhor acoplamento está na borda do travamento.**

**4. Nem na borda a fase ouvida chega ao calendário (J4).** O melhor EAM (24,5) fica acima do calendário fixo (20,0) e do relógio v1 (18,8), e nenhum lugar bate o próprio calendário. A borda tira o relógio do desastre do teste 53 (37,7 a 2 ε_c, ≈ o 36,5 de lá), mas não cria informação: a fase em 1/09 não sabe do atraso das águas (correlação −0,07, explicação do teste 53). **A borda é ótima para o relógio, não para a tarefa.** Para a tarefa, o teto continua sendo o que o campo local contém.

**5. Os testes 52–53 estavam a 2 ε_c**, onde o ruído de fase já é o dobro do mínimo. Com 0,7 ε_c, a sentinela e os relógios dos testes 54–56 teriam a fase menos sacudida. Isso vale como sugestão para o 56, onde o acoplamento forte (ε = 0,4 no dia) foi parte do problema.

## Para a lista de defeitos de desenho

83. O piloto usou só Juara. Os lugares onde a fase escorrega (Cuiabá e Rondonópolis) têm ruído de fase 1,7 vez maior e explodem acima de 2 ε_c. Um piloto com o lugar mais difícil teria dado o nível certo. A regra do piloto deve incluir o pior caso da calibração, não só o lugar de referência.

Placar: 57 testes numerados (o 25 sem resultado), mais o teste do ato A. 57: J1, J2 e J3 passaram, J4 reprovou. 83 defeitos nesta numeração, 1 emenda.
