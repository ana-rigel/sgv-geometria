# Leitura do teste 37 (a galáxia no cubo: o laço que segura o modo): J1, J2, J3 e J4 REPROVADOS; J5 PASSOU. O andar 2 não segura sozinho; quem segura perto de 0,627 é a memória lenta semeada, com ou sem laço

**Predição:** PREDICAO_teste37_galaxia_laco.md (62de4b3), antes de escrever o instrumento. **Instrumento:** teste37.py. **Resultado:** resultados_teste37.json. Modelo ilustrativo; 100 sementes; K_c = 25,8 mrad/Myr. Cinco julgamentos; sem emenda. Antes da rodada, o instrumento foi corrigido para calcular K∞ como está na predição (média de K entre 600 e 1.000 Myr por semente, e não o K final).

| | medida | resultado | critério | |
|---|---|---|---|---|
| **J1** o instrumento reproduz o enrolamento (A) | desvio máximo da média simulada contra a fórmula, 0–300 Myr; t em que C < 0,5 | **0,0505** (em t = 282 Myr); **86 Myr** | ≤ 0,05; 87,5 ± 5 | **reprovado** por 0,0005 |
| **J2** o travamento fixo fica na faixa (B, 1,2 K_c) | C̄ 300–1.000, mediana; sementes na faixa | **0,866**; **0** de 100 | ≥ 80 | **reprovado** |
| **J3** o laço com alvo converge (Laço I) | sementes com K∞/K_c em 0,9–1,1 e \|C̄ − 0,627\| ≤ 0,05 | **8** de 100 (K∞/K_c médio 0,916; C̄ 0,554) | ≥ 80 | **reprovado** |
| **J4** o andar 2 segura sozinho (Laço II, vazio, β = 5) | sementes na faixa; efeito sobre β = 0 | **0** de 100; **+0,038** | ≥ 80; ≥ +0,10 | **reprovado** |
| **J5** o andar 2 é o pior (Laço II, semeado, β = 5) | medianas de C̄: andar 2 · 3 · 4 | **0,408** · 0,714 · 0,743 | o 2 menor | **passou** |

Laço II, K = 0,8 K_c, mediana de C̄(300–1.000) e sementes na faixa [0,527; 0,727]:

| andar escutado | nasce | β = 0 | β = 2 | β = 5 | β = 10 |
|---|---|---|---|---|---|
| 2 | vazia | 0,253 · 0 | 0,264 · 0 | 0,297 · 0 | 0,368 · 0 |
| 2 | semeada | 0,326 · 0 | 0,352 · 0 | 0,408 · 2 | **0,575 · 97** |
| 3 | vazia | 0,164 · 0 | 0,164 · 0 | 0,164 · 0 | 0,164 · 0 |
| 3 | semeada | **0,662 · 100** | 0,690 · 98 | 0,714 · 78 | 0,734 · 31 |
| 4 | vazia | 0,156 · 0 | 0,156 · 0 | 0,156 · 0 | 0,156 · 0 |
| 4 | semeada | 0,741 · 17 | 0,742 · 17 | 0,743 · 13 | 0,743 · 13 |

Laço I: K/K_c a cada 100 Myr, média nas sementes: 0 · 0 · 0,42 · 1,10 · 1,67 · 1,64 · 1,18 · 0,76 · 0,71 · 1,01. No andar 4 semeado: K∞/K_c 0,72, C̄ 0,608.

Apostas: J1 (90 %), errada; J2 (5 %), certa a reprovação; J3 (70 %), errada, pelo risco que a própria aposta nomeou (oscilar perto de K_c); J4 (40 %), certa a reprovação; J5 (50 %), certa.

## O que o resultado diz

**1. O enrolamento é o que a fórmula diz, até onde ela vale.** Até 150 Myr, a simulação fica a menos de 0,02 da fórmula exata, e C cai abaixo de 0,5 em 86 Myr nas duas. Depois disso, a fórmula vai a zero e a simulação não: com 12 anéis e fases ruidosas, a média de |Z| tem um piso que a fórmula, que é |média de Z|, não tem. O J1 caiu por 0,0005 em t = 282 Myr, exatamente onde esse piso pesa. A conta prévia ("o ruído entra só por e^{−Dt}") esqueceu que a média do módulo não é o módulo da média.

**2. K = 1,2 K_c trava, como a conta prévia disse.** 0,866 em todas as sementes, todos os anéis travados. Não há "travamento parcial" em 1,2 K_c neste modelo.

**3. O laço com alvo encontra o K certo em média, mas oscila.** K sobe até 1,67 K_c, cai até 0,71 K_c e volta a 1,0 em 1 Gyr. O K médio (0,916 K_c) está na faixa prevista, mas em cada semente o laço ainda está balançando: a média de 50 Myr chega atrasada a um disco que leva ≈ 100 Myr para responder, e perto de K_c a resposta é íngreme. O que se aprende continua sendo o que se queria aprender: no modelo, segurar 0,627 com escuta instantânea exige K ≈ K_c; com a memória lenta semeada, ≈ 0,72 K_c.

**4. O andar 2 não segura sozinho, e a razão é de tempo.** A conta prévia supôs que o andar 2 vazio aprenderia a fase com o disco ainda coerente e chegaria a |R₂| ≈ 0,8–0,9. Ele chegou a **0,62** em 100 Myr e depois desceu (0,55; 0,45; 0,37…), porque o disco perde metade da coerência em 86 Myr, antes de uma memória de 67 Myr terminar de aprender. O pino de fase ficou com força ≈ 0,8 × 0,62 ≈ 0,5 K_c, abaixo do ≈ 0,79 K_c que um pino fixo precisa para prender a maioria dos anéis. O laço endurece a memória (λ cai para 0,55–0,77 do valor de base), mas endurece uma memória que guardou pouco.

**5. Quem segura perto de 0,627 é a memória lenta que nasce sabendo.** O andar 3 semeado, **sem laço nenhum**, fica em 0,662 com 100 de 100 sementes na faixa. O laço só o endurece mais e o empurra para cima da faixa (β = 10: 0,734, 31 de 100). O andar 4 semeado segura acima da faixa (0,74). Vazios, os dois são inúteis (0,16): aprendem tarde demais. O andar 2 só entra na faixa semeado e com o laço mais forte (β = 10: 0,575, 97 de 100). É a lição do teste 33 e do teste 36, agora no disco: **a organização que segura precisa nascer sabendo**, e o que importa é a escala da memória contra a escala do enrolamento.

**6. Para a NGC 628, nada muda.** No modelo, 0,627 pode ser obtido de várias formas: K ≈ K_c, memória lenta semeada sem laço, andar 2 semeado com laço forte, ou (teste 34) uma curva de rotação mal declarada sem 𝒢 nenhum. O modelo não distingue entre elas, e a galáxia também não.

## Para a lista de defeitos de desenho

51. O J1 comparou a média de |Z| simulada com |média de Z| da fórmula. Com 12 anéis e fases ruidosas, |Z| tem um piso positivo, e a diferença cresce onde a fórmula se aproxima de zero (depois de ≈ 200 Myr). O critério deveria usar a fórmula só até o primeiro mínimo, ou um Monte Carlo do enrolamento sem acoplamento.
52. O Laço I foi desenhado sem calcular a estabilidade do controlador: a média de 50 Myr e o ganho κ = 0,02 K_c/Myr, contra um disco que responde em ≈ 100 Myr e uma curva C(K) íngreme perto de K_c, dão oscilação. A aposta nomeou o risco e o critério não o considerou.
53. A conta prévia do J4 supôs |R₂| ≈ 0,8–0,9 sem calcular quanto uma memória de 67 Myr, nascendo vazia, consegue aprender de um sinal que perde metade da coerência em 86 Myr. A conta (|R₂| máximo ≈ 0,6) mostraria que o pino ficaria abaixo do limiar.

Placar: 37 testes numerados (o 25 sem resultado). 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram; 36: J1–J4 passaram, J5 reprovou; 37: J1–J4 reprovaram, J5 passou. 53 defeitos, 1 emenda.
