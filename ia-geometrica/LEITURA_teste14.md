# Leitura do teste 14 (saltos em cachos densos) — REPROVADO, e o teto é baixo

**Predição:** PREDICAO_teste14_cachos_densos.md (38dc601), antes de rodar. **Resultado:** resultados_teste14.json. Um julgamento; sem emenda.

| | erro de predição médio (medida) |
|---|---|
| teto 1: olhar sempre | 1,38 |
| nulo: a cada 4 | 2,07 |
| teto 2: oráculo (sabe o cacho) | V_orac **+1,19 %**, envelope −9,8 % a +6,7 %, positiva em 63 |
| v0: ritmo lido na régua, H aprendido | V **+1,31 %**, envelope −2,5 % a +5,8 %, positiva em 69 de 96 válidas |

Mundo como projetado: 49 saltos por janela de medida, ocupação de cacho 19 %, H aprendido 22 (o intervalo típico entre saltos de um cacho). Pares mais frequentes: v0 (3, 4) e (2, 4); oráculo (3, 4). Critério: (a) válidas ≥ 95: sim (96); (b) envelope acima de zero: **não**. **Reprovado.** Apostas: V_orac entre +8 e +20 % com envelope acima de zero, **errada**; passar 40 %, certa a não-passagem; V entre +3 e +10 %, errada; v0 ≥ 50 % do oráculo, certa (captura mediana 0,53; e a v0 até empata com o oráculo na média, o que diz que o oráculo não tem mais o que dar).

## O que o resultado diz

A conta por janela acertou o mundo (cachos, saltos e ocupação saíram como previstos) e errou o teto pelo mesmo motivo de sempre, agora visível: eu disse "o custo de salto domina" e não domina. Um salto custa alguns passos de amplitude cheia **uma vez**; a deriva custa **todo passo**. Com 49 saltos em 4.000 passos e atraso médio de ≈ 1,5 passo até a próxima olhada do periódico, o custo de salto é ≈ 0,17 por passo contra um erro total de 2,07: 8 %. A melhor redistribuição de olhadas poupa um quarto disso: teto ≈ 2 %. O oráculo achou 1,2 %, a v0 1,3 %.

Há um teto acima de todos os tetos, que eu devia ter escrito no teste 2: com 25 % de olhadas, o periódico já erra só 50 % mais que olhar sempre (2,07 contra 1,38). Toda a política de olhar disputa esse 0,7, e só a parte dele que depende **de quando** se olha, que é pequena em qualquer mundo onde o erro de não olhar cresce passo a passo. O ato "quando olhar" só pode valer muito quando olhar é **raro** (orçamento de 5 %, não de 25 %), porque aí cada olhada tem muito a escolher, ou quando o mundo pune um passo cego com algo maior que uma amplitude.

## O que fecha e o que não

- Fecha, para a linha de política inteira (testes 2, 7, 10, 11, 12, 13, 14): com orçamento de 25 % e registro que copia o mundo, a política de olhar rende ≈ 1 % sobre o periódico em deriva, deriva com regimes e saltos em cachos, e o teto de oráculo é ≈ 2 % no melhor deles. A forma (ritmo por regime lido na régua) captura metade a tudo desse teto. **Não é a v0 que não sabe quando olhar; é que, nesses mundos e nesse orçamento, saber vale 1 %.**
- Não fecha: a mesma política com orçamento de 5 % (periódico a cada 20), onde o custo de não olhar é 4 vezes maior e a escolha do momento pesa mais. É o último teste que eu faria nesta linha; se o teto de oráculo lá for < 5 %, a linha fecha de vez.

## Para a lista de defeitos de desenho do projeto

26. Orçamento de 25 % de olhadas em todos os testes de política: o periódico já está perto do teto, e o ato só pode valer pouco. O orçamento devia ter sido escolhido para que o ato tivesse o que decidir.

Catorze testes, catorze reprovações, vinte e seis defeitos.
