# Leitura do teste 7 (a política de expectativa) — REPROVADO (empate)

**Predição:** PREDICAO_teste7_expectativa.md (473a247), antes de rodar. **Resultado:** resultados_teste7.json. Um julgamento; sem emenda.

| | erro de predição médio (medida, 100 sementes) |
|---|---|
| teto: olhar sempre | 1,96 |
| nulo: olhar a cada 4 passos | 2,52 |
| teste 2: olhar pela última tensão, n_max 8 | 2,57 (V −1,85 %) |
| **teste 7: olhar pela tensão esperada, n_max 16** | **2,52 (V +0,13 %)** |

V média **+0,13 %**, envelope −3,0 % a +2,7 %, positiva em 55 de 100 sementes; 100 sementes válidas. Critério: (a) fração ok: sim; (b) envelope acima de zero: **não**. **Reprovado.** Apostas: 40 % em passar (certa a não-passagem); V média entre 0 e +4 % (certa, por pouco); envelope cruzando zero (certa); b_n > 0 em todo n (certa); b_n < 0,2 antes de n = 5 (certa: 0,197 em n = 4).

## O que o resultado diz

A expectativa consertou o defeito do teste 2 (de −1,85 % para +0,13 %) e parou aí: empate com o periódico. A razão está nos b_n: a informação que a última tensão carrega sobre o erro futuro cai de 0,54 (n = 1) para 0,15 (n = 5) e 0,04 (n = 10). Depois de quatro ou cinco passos a tensão esperada é só a_n, que depende de n e de nada mais, e uma política que depende só de n **é** periódica. A v0 com expectativa acorda um pouco antes depois de uma tensão alta e um pouco depois de uma baixa; o ganho disso, num AR(1), é o que a média mostra: nada que o envelope distinga de zero.

Isto não é um defeito do instrumento; é o mundo. Num processo de Markov de um passo, a única coisa que a última observação diz sobre o futuro decai geometricamente, e o custo de não olhar depende quase só do tempo. A política de olhar só poderia ganhar do periódico num mundo em que **o momento certo de olhar varie**: regimes de tensão persistentes (volatilidade que vem em blocos, como o BTC), ou saltos raros cujo sinal precursor a tensão capte. Nos mundos de deriva não há momento certo.

## O que fecha e o que não

- Fecha: em `mundo_deriva`, nenhuma política baseada na tensão (reflexo ou expectativa) ganha do periódico; o teste 2 e o 7 são a mesma resposta. O único ato da v0 não tem onde valer num mundo sem regimes.
- Não fecha: a mesma política num mundo com regimes de tensão persistentes (o mundo "quente/frio": AR(1) cujo σ alterna em blocos geométricos de média 200 passos, parente do MSM). É o mundo em que a expectativa tem o que esperar. Com predição própria.

## Para a lista de defeitos de desenho do projeto

17. O mundo do teste 2 (e deste) não tem momento certo de olhar: um AR(1) é o pior lugar para testar uma política de olhar, e os dois testes mediram isso em vez da política.

Sete testes, sete reprovações, dezessete defeitos. A terceira candidata (escada pela tensão) é o teste 8.
