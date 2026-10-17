# Leitura: a mente geométrica é mais que um filtro? (17/10/2026) — REPROVADA, duas vezes

**Predição:** PREDICAO_mente_geometrica.md (4060037) + Emenda 1 (9f6f91f), registradas antes de cada rodada. **Resultados:** resultados_mente_v1_REPROVADO.json (rodada 1) e resultados_mente.json (rodada 2, Emenda 1). Pela cláusula da Emenda 1, o veredito é final: **os dois experimentos reprovaram pelos critérios registrados.**

## Números da rodada 2 (σ_n = 2,0; 100 sementes; 4.000 passos)

| | W1 (com ritmo) | W0 (sem ritmo) |
|---|---|---|
| Exp. 1: redução de J_salto por M1 vs M0 | +1,5 % | +1,6 % (envelope +0,4 a +4,0) |
| Exp. 1: J_calma de M1 vs M0 | +23,6 % pior | — |
| Exp. 2: J(M2) | 36,9 | 37,6 |
| Exp. 2: melhor lr fixo | 0,95, J = 25,9 (env. 24,9–26,6) | 0,95, J = 26,0 (env. 24,2–27,0) |
| Exp. 2: salto / calma de M2 | 21,3 / 1,56 | 22,4 / 1,52 |
| Exp. 2: salto / calma do fixo 0,95 | 2,0 / 2,39 | 2,1 / 2,39 |

## Veredito

- **Exp. 1 ("aprendeu o ritmo"): reprovado.** M1 não reduz o custo de salto em nenhum dos mundos e piora a calma em 24 %.
- **Exp. 2 ("venceu o dilema"): reprovado.** M2 ganha na calma (1,56 contra 2,39) e perde feio no salto (21 contra 2); o melhor botão fixo vence por 11 pontos nos dois mundos, fora do envelope.

## O que o resultado ensina (diagnóstico, não conserto)

**Exp. 1 tem um segundo defeito de instrumento, encontrado depois da rodada e não corrigido, porque a emenda era a última.** A ordem das operações dentro do passo: o detector vê o salto e zera o relógio (`ultimo_salto = t`) *antes* de a janela ser avaliada; a janela exige `t − ultimo_salto ≥ P̂ − 1`, que no passo do salto vale 0. Logo a plasticidade nunca abre no passo em que o mundo muda; abre, quando abre, no passo seguinte, e por isso o ganho é de 1–2 %. A ideia (abrir a plasticidade no instante previsto) não foi testada; o que foi testado é um relógio que se desarma ao tocar. Fica registrado como defeito para uma v2 futura, com a nota de que precisaria de nova predição.

**Exp. 2 reprovou por uma razão que vale mais que o teste.** Com ruído σ_n = 2,0 e saltos de ~6, o melhor comportamento neste mundo é quase não lembrar (lr = 0,95: copiar o campo e aceitar o ruído). M2, que fecha a plasticidade assim que a surpresa relativa (E_norm) cai, para no meio do caminho depois de um salto: um passo a 0,8 cobre 80 % do salto, E_norm fica negativa, lr cai a 0,05 e os 20 % restantes levam dezenas de passos. A modulação pela surpresa *relativa* é o erro de desenho: surpresa deveria ser medida em termos absolutos (quanto falta para chegar), não em relação ao próprio passado. Mas a lição maior é outra: **neste mundo, reobservar custa menos que lembrar.** O ruído é independente de passo a passo e os saltos são grandes; não há regularidade que a memória possa explorar além do ritmo (que a M1 não conseguiu usar). Uma mente geométrica só pode valer mais que um filtro num mundo onde lembrar paga, isto é, onde o ruído tem estrutura (correlação) ou a reobservação tem custo. O Teste B original não tinha nem uma coisa nem outra; é um mundo em que a inteligência é inútil por construção, e o resultado disse isso com números.

## Apostas

| Aposta | Prob. | Saiu |
|---|---|---|
| M1 reduz J_salto em W1 | 90 % | sim, 1,5 % (tecnicamente; na prática não) |
| "Aprendeu o ritmo" | 60 % | **não** |
| J_calma de M1 piora < 10 % | 70 % | **não** (+24 %) |
| M2 bate o melhor fixo em W1 | 65 % | **não** |
| M2 bate o melhor fixo em W0 | 60 % | **não** |
| Critério completo do exp. 2 | 50 % | **não** |

Cinco erros em seis. A casa valeu lá também: uma mente que parece inteligente num plano de 10 por 10 é fácil de produzir, e esta não foi.

## O que seria preciso (não pedido)

Um mundo em que lembrar paga: ruído correlacionado no tempo (o campo deriva em vez de tremer) ou custo explícito por observação (a mente escolhe quando olhar; cada olhada custa). Com isso, a pergunta "quando reobservar custa menos que lembrar" deixa de ser lição e vira variável, e os dois experimentos ganham um nulo mais honesto do que o melhor botão fixo: o observador que paga para olhar tudo.
