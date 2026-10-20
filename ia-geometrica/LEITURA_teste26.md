# Leitura do teste 26 (o mundo sítio) — J1 PASSOU, J2 REPROVADO; o teto é grande e é da previsão, não do córrego

**Predição:** PREDICAO_teste26_mundo_sitio.md (069771d), antes de rodar. **Instrumento:** sitio.py, teste26.py (o mesmo commit). **Resultado:** resultados_teste26.json. Dois julgamentos; sem emenda.

| anos 3–4, soma de 100 sementes | custo | cheias perdidas (de 1.867) | chamadas |
|---|---|---|---|
| nunca chamar | 186.700 | 1.867 | 0 |
| N1, sensor comum (nível) | 182.790 | 1.185 | 6.429 |
| N2, nível ou subida | 181.910 | 1.135 | 6.841 |
| **v0** (surpresa ou vinco, afinada) | 184.530 | 1.323 | 5.223 |
| v0 crua (ruptura na régua, sem afinação) | 194.190 | 1.743 | 1.989 |
| oráculo (sabe o futuro) | **17.970** | 0 | 1.797 |

**J1, o mundo tem teto:** V_orac mediano **90,3 %**, acima de 5 % nas 100 sementes. **Passou.**
**J2, a v0 vê o que o sensor comum não vê:** custo total da v0 **1,4 % maior** que o de N2; mais barata em 43 sementes (9 empates). **Reprovado.**

Apostas: J1 passa (90 %), certa; J2 reprova (85 %), certa, e a v0 caiu na faixa apostada (−10 % a +5 % de N2); v0 bate N1 em ≥ 10 % (60 %), **errada** (−1,0 %); N2 bate N1 em ≥ 10 % (65 %), **errada** (+0,5 %); v0 crua com menos da metade do que a afinada captura (60 %), indefinida, porque a afinada não capturou nada; nenhuma política causal passa de 70 % do teto (75 %), certa, e de um jeito que eu não imaginei: **nenhuma passou de 1 %**.

## O que o resultado diz

O sítio cobra, como a Ana disse e a predição apostou: quem soubesse o futuro gastaria um décimo do que gasta quem nunca chama. É o mundo que faltou aos quinze testes de política, e o teto que lá era de 2 % aqui é de 90 %.

Mas ninguém que só olha o córrego alcança esse teto. Nem o alarme comum, nem o bem feito, nem a v0: os três ficam colados em "nunca chamar". As afinações mostram por quê. Em 18 de 100 sementes o melhor limiar de nível era não chamar nunca; nas outras, o limiar desce para 0,7–0,85 m, e a política passa a chamar quase a chuvosa inteira (≈ 32 chamadas por semente por ano) para salvar um terço das cheias. Paga em viagens o que economiza em perdas.

A causa está no mundo, e uma conta descritiva feita depois do julgamento (sem avaliar política nenhuma) mostra o tamanho dela. Do primeiro sinal até a cheia, sobra pouco tempo:

| a partir de | tempo mediano até a cheia | cheias com ≥ 6 h de aviso |
|---|---|---|
| início da chuva | 4 h | 31 % |
| subida ≥ 0,10 m em 3 h | 3 h | 22 % |
| nível ≥ 0,9 m | 4 h | 43 % (mas 0,9 m também acontece sem cheia) |

O ato leva 6 h para valer. Neste córrego a cheia chega, na mediana, 3 a 4 horas depois do primeiro sinal. O sensor do córrego enxerga a cheia tarde demais para o ato, e isso vale para qualquer leitura dele: é **cegueira do sensor, não da política**. O teto de 90 % pertence a quem prevê a chuva, não a quem observa o rio.

## O que isso significa para a IA geométrica no sítio

1. **O ato vale no sítio.** A frase do teste 15 está confirmada pelo outro lado: em mundo de observação pura, decidir quase não importa; em mundo com consequência, importa muito. A linha de política, fechada por cláusula nos mundos sintéticos, está reaberta na forma "quando chamar".
2. **A v0 como alarme de córrego é a taxa de subida com outro nome.** Ela empata com o sensor comum bem feito, como foi apostado. O que ela teria de próprio não está no alarme.
3. **O que falta não é uma mente melhor; é antecedência.** As saídas, cada uma com predição própria antes:
   - **um segundo sensor, a chuva** (ou um sensor rio acima): dá horas que o córrego não dá; a medida acima diz que o início da chuva já antecipa 6 h em 31 % das cheias, contra 22 % da subida;
   - **um ato mais rápido** (L de 1–2 h: uma comporta ou bomba acionada à distância em vez de uma viagem);
   - **a declaração**: a v0 dizer, a cada cheia perdida, "esta subiu mais rápido do que eu e o ato conseguimos ver". É a parte da v0 que ficou de pé nos testes 16–17, e é a que um alarme comum não faz.

## Para a lista de defeitos de desenho

37. O tempo do ato (L = 6 h) foi escolhido sem medir antes o tempo de aviso que o mundo dá (mediana 3–4 h). O teto do oráculo foi calculado; o **teto causal** (o que um observador do córrego pode alcançar) não. É o defeito 24 de novo, numa forma nova: calcular antes não só o que o oráculo ganha, mas o que o sensor permite ver a tempo.

Placar: 26 testes numerados (o 25 ficou sem resultado registrado: a rodada em segundo plano não deixou JSON no repositório). No 26, J1 passou e J2 reprovou. 37 defeitos, 1 emenda.
