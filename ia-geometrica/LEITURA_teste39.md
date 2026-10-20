# Leitura do teste 39 (a ordem líquida): J1, J2, J3 e J4 REPROVADOS. O piso certo não salva a autoconsistência: o ponto fixo dela é instável do lado da ordem, e o braço "não cria" estava mal posto desde o teste 38

**Predição:** PREDICAO_teste39_ordem_liquida.md (6ce0122), antes de escrever o instrumento. **Instrumento:** teste39.py. **Resultado:** resultados_teste39.json. Modelo do teste 38; 100 sementes; 5.000 Myr; C̄ em 3.000–5.000 Myr. Quatro julgamentos; sem emenda.

Mediana de C̄ · sementes na faixa [0,527; 0,727] · sementes que levaram g ao teto (tempo mediano):

| braço | 0,7 K_c | 0,8 K_c | 0,9 K_c |
|---|---|---|---|
| referência (g = 1, semeada) | 0,252 · 0 | 0,288 · 0 | 0,414 · 0 |
| cortada, semeada | 0,895 · 24 · 97 (3.309 Myr) | 0,900 · 23 · 98 (3.293) | 0,911 · 28 · 99 (3.295) |
| sem corte, semeada | 0,433 · 11 · 58 (3.585) | 0,531 · 14 · 62 (3.560) | 0,517 · 14 · 61 (3.558) |
| cortada, vazia | | 0,999 · 0 · 100 (**73 Myr**) | |
| sem corte, vazia | | 0,999 · 0 · 100 (**64 Myr**) | |

Trajetória (média nas sementes, sem corte, semeada, 0,8 K_c), em Myr: 0 → g 1,00 · |R₃| 0,99 · C 0,99; 1.000 → 0,05 · 0,32 · 0,19; 2.000 → 0,36 · 0,14 · 0,29; 3.000 → 4,26 · 0,16 · 0,41; 4.000 → 8,68 · 0,34 · 0,58.

| | resultado | critério | |
|---|---|---|---|
| **J1** cortada não cria (vazia) | 0,999 | ≤ 0,31 | **reprovado** |
| **J2** sem corte não cria (vazia) | 0,999 | ≤ 0,31 | **reprovado** |
| **J3** sem corte apara até a faixa (semeada, 0,8 K_c) | 14 de 100 | ≥ 80 | **reprovado** |
| **J4** sem corte tem ponto próprio acima do caos | espalhamento 0,098; mínimo 0,433 | ≤ 0,05 e ≥ 0,40 | **reprovado** |

Apostas: J1 (35 %), certa a reprovação, mas pela razão errada (ver item 1); J2 (85 %), errada; J3 (10 %), certa a reprovação; J4 (10 %), certa a reprovação.

## O que o resultado diz

**1. O braço "não cria" testava outra coisa, desde o teste 38.** O disco nasce coerente (fases N(0; 0,15), C = 0,99). Uma memória vazia diante de um disco ordenado tem ordem líquida negativa ou zero, e a do disco é ≈ 0,99. O laço lê "o disco tem ordem, a memória não" e dá voz enquanto a memória aprende a fase inicial: g chega ao teto em 64–73 Myr, nos dois sabores, e o disco nunca se solta. Isso **preserva a ordem de nascença**; não a cria do caos. No teste 38, a memória vazia do III-a fez o mesmo (g = 20 já em 1.000 Myr), e a leitura 38 errou ao atribuir isso ao piso do acaso (item 2 daquela leitura vale para a memória semeada, não para a vazia). Para testar "criar ordem do caos", o disco tem de nascer com fases sorteadas.

**2. O corte reintroduz o falso positivo, como previsto.** Semeada, a voz cai ao piso (g = 0,05 em 1.000 Myr), o disco se solta, e depois o viés de +0,057 do corte faz g subir: teto em ≈ 3,3 Gyr em 97–99 de 100 sementes, e C ≈ 0,9. A conta prévia dizia ≈ 2 Gyr depois de o disco se soltar; foi isso.

**3. Sem corte, a regra é instável do lado da ordem.** O viés estático some, como a conta prévia mediu, mas a voz volta a subir mesmo assim. Em 2.000 Myr, a memória ainda guarda um resto da ordem inicial (|R₃| = 0,14, acima do piso de 0,088). Qualquer voz dada a esse resto alinha um pouco o disco, e o disco responde mais rápido do que a memória acompanha. A ordem líquida do disco fica um pouco acima da da memória enquanto a ordem cresce, e g sobe mais. É um laço de reforço: o ponto fixo "ordem do disco = ordem da memória" é **instável** do lado ordenado. Em 5 Gyr, 58–62 % das sementes já chegaram ao teto, e as outras estão subindo. Os C̄ ≈ 0,43–0,53 são a média de um disco a caminho do travamento, não um nível.

**4. A autoconsistência sai da lista de regras que aparam.** Com o piso errado (teste 38), ela travava pelo acaso; com o piso certo e cortado, trava mais devagar; com o piso certo e sem corte, trava por instabilidade. Nas três formas, ela é um **amplificador**: dá voz a qualquer ordem que a memória ainda tenha, e o disco devolve mais ordem do que recebeu. "A memória não guarda mais ordem que o disco sustenta" é uma condição de equilíbrio, mas o equilíbrio não se segura.

**5. O que fica para um laço que apare.** Ele precisa de uma força que **cresça contra** a ordem, e não a favor: um termo que puna a voz quando o disco fica mais ordenado do que a memória justifica, com uma escala de tempo mais lenta que a resposta do disco. É a condição de estabilidade que faltou nos testes 37 a 39, e é um desenho novo.

## Para a lista de defeitos de desenho

57. O braço de memória vazia (J5 do teste 38; J1 e J2 deste) começou com o disco coerente. Memória vazia diante de disco ordenado não é caos; o braço mediu a preservação da ordem de nascença. A leitura 38 generalizou o mecanismo do piso para a memória vazia, onde g foi direto ao teto em < 100 Myr. O braço certo sorteia as fases iniciais do disco.
58. A conta prévia mediu o viés da ordem líquida num disco com K = 0, sem o laço. Com o laço ligado, o disco responde à voz mais rápido do que a memória acompanha, e qualquer ordem residual da memória acima do piso é amplificada. A instabilidade do ponto fixo era dinâmica, e a conta estática não podia vê-la; uma análise de estabilidade do par (g, C) em torno do ponto fixo teria mostrado o sinal positivo da realimentação.

Placar: 39 testes numerados (o 25 sem resultado), mais o teste do ato A. 39: J1–J4 reprovados. 58 defeitos nesta numeração, 1 emenda.
