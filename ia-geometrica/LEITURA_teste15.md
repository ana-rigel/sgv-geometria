# Leitura do teste 15 (orçamento de 5 %) — REPROVADO; a linha de política fecha pela cláusula

**Predição:** PREDICAO_teste15_orcamento_5.md (136953e), antes de rodar. **Instrumento:** teste15.py (6c80e91: laço enxuto só com o andar 1, que é o único que a política e o erro leem, e sementes em dois processos; a primeira rodada foi interrompida pelo limite de tempo sem produzir resultado). **Resultado:** resultados_teste15.json. Um julgamento; sem emenda.

| | medida (100 sementes, 5 % de olhadas) |
|---|---|
| teto 1: olhar sempre | — |
| nulo: a cada 20 | — |
| teto 2: oráculo (sabe o cacho) | V_orac **+1,80 %**, envelope −13,2 % a +11,2 %, positiva em 67 |
| v0: ritmo lido na régua | V **+1,82 %**, envelope −5,6 % a +9,3 %, positiva em 73 de 97 válidas |

Par mais frequente da v0 (11, 20); **do oráculo, (20, 18) e (10, 24)**: quase periódico. Critério: (a) válidas ≥ 95: sim; (b) envelope acima de zero: **não**. **Reprovado.** Apostas: V_orac entre +3 e +9 %, errada (1,8 %); passar 30 %, certa a não-passagem; V entre +1 e +5 %, certa; v0 < metade do oráculo, errada (captura mediana 0,55, e na média empata).

**Cláusula de fechamento, escrita antes:** V_orac médio < 5 % → a linha de política fecha.

## O que o resultado diz

O oráculo, que sabe exatamente quando o mundo está em cacho, escolhe olhar **quase em ritmo fixo** (20 no cacho, 18 fora). Com 5 % de olhadas, concentrar no cacho obriga a deixar o resto do mundo cego por 60 passos ou mais, e a deriva cobra mais do que os saltos devolvem. O orçamento apertado não dá à política mais o que decidir, como eu apostei; dá menos: a melhor alocação de poucas olhadas é espalhá-las. Minha conta errou de novo pelo mesmo lado: subestimei o custo de deriva fora do cacho.

A v0 empatou com o oráculo (1,82 % contra 1,80 %), o que repete o teste 14: a régua como gatilho e o H aprendido entregam tudo que há para entregar; o que não há é teto.

## O que a linha inteira diz (testes 2, 7, 10, 11, 12, 13, 14, 15)

Oito testes, quatro mundos (deriva; deriva com regimes; saltos em cachos esparsos; densos), dois orçamentos (25 %; 5 %), dois registros (λ₁ herdado; do mundo), quatro formas de política (limiar na última tensão; limiar na expectativa; ritmo por regime; ritmo com memória de cacho). Resultado uniforme: a melhor política rende 0–2 % sobre o periódico, e o oráculo que sabe tudo rende o mesmo. **O ato de decidir quando olhar vale pouco em todo mundo em que o custo de não olhar se acumula passo a passo, porque o periódico já é quase ótimo nesses mundos.** O ato só poderia valer onde não olhar custa de uma vez e muito (um mundo onde um passo cego custa mais que a amplitude: ação com consequência, não só erro de memória), e esse mundo não está no escopo da v0, que não age.

Isso não é uma derrota da v0; é uma propriedade dos mundos de observação pura. Para um observador que só olha e lembra, **quando** olhar quase não importa; **com que rigidez** lembrar (testes 1, 12) e **o que declarar** sobre o que não vê (testes 6, 9) importam muito mais. O projeto de 17/10 apostou no ato como o que distingue uma mente de um filtro; os testes dizem que a distinção está na declaração, não no ato.

## Para a lista de defeitos de desenho do projeto

27. O compromisso 3 do projeto ("reobservar versus lembrar como decisão") foi posto como o ato que distingue a v0; em mundos de observação pura ele distingue pouco. A linha "reobservar versus lembrar" segue válida como teoria de custo; como política de um observador que não age, rende ≤ 2 %.

Quinze testes, quinze reprovações, vinte e sete defeitos. A linha de política está fechada.
