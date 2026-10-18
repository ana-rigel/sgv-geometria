# Leitura do teste 24 (OBS-01, etapa dois: a rede treinada) — REPROVADO; as redes aprenderam pouco e a régua disse isso

**Predição:** PREDICAO_teste24_rede_treinada.md (c96c3ee, com nota de fumaça antes da rodada). **Resultado:** resultados_teste24.json. Um julgamento; sem emenda.

| | |
|---|---|
| redes com corte estável entre 5 mundos (cv < 0,2) | **9/20** (critério 16) |
| redes com corte mediano na faixa de Wiener [1/1.400, 1/35] | **13/20** (critério 16) |
| as duas | 7/20 (redes 2, 3, 4, 7, 10, 13, 19) |
| D(2×) > 0,05 | 15/20 |
| rede sem treino com corte fora da faixa | 17/20 |
| perda relativa final das redes | 0,47 a 0,73 (o filtro de Wiener ótimo dá **0,31**) |

**Reprovado** em (a) e (b). Apostas: 55 % em passar, certa a não-passagem; "≥ 5 redes aprendem só parte e ficam fora da faixa" (certa: 7 fora); D(2×) > 0,05 em ≥ 10 (certa: 15); sem treino fora da faixa em ≥ 15 (certa: 17).

## O que o resultado diz

As redes aprenderam pouco. Com 1.000 passos de otimização a perda relativa ficou entre 0,47 e 0,73, contra 0,31 do filtro linear ótimo: nenhuma chegou perto da tarefa. E a régua **leu exatamente isso**, rede a rede:

- As sete redes que passaram nos dois critérios são as que viraram passa-baixa de verdade: "não ver" entre 0,46 e 0,62 (barram metade do mundo, que é o que a tarefa pede: o lento é um terço da potência), corte entre 7 × 10⁻⁴ e 2 × 10⁻³, estável entre mundos.
- As redes 1, 5, 6, 9, 14 ficaram copiadoras ou quase (ν̂ 0,09–0,32, ε̂ ≤ 0,05): a régua devolve corte alto, instável ou indefinido, porque não há corte num observador que deixa passar tudo. Isso não é falha da régua; é a leitura certa de um observador que não aprendeu.
- A rede 17 é o caso estranho: ν̂ 0,03 e corte em 0,43 ciclos/passo, com D(0,5×) de 0,18: uma rede quase linear por fora e instável por dentro, o que a régua marcou pela amplitude.

O treino move o corte: sem treino, 17 de 20 redes têm corte fora da faixa; com treino, 13 entram. A régua vê o treino acontecer, e vê quanto faltou. E 15 das 20 redes treinadas são não lineares pelo teste de amplitude (D(2×) > 0,05), o que confirma que, num modelo treinado, as cláusulas 1–5 valem por amplitude.

Por que reprovou, então: o critério pedia 16 de 20 e as redes não chegaram lá porque eu as treinei pouco, por custo de máquina (20 redes × 1.000 passos ≈ 50 minutos aqui). Defeito de desenho, meu: a predição fixou a faixa da tarefa e não fixou o quanto a rede precisava ter aprendido para o teste valer; a nota de fumaça viu o problema e escolheu um compromisso que não bastou.

## O que fecha e o que não

- Fecha: sobre uma rede treinada, sem conhecer os pesos, a régua dá corte, "não ver", "errar" e regime, e os números acompanham o que a rede de fato aprendeu: filtro onde virou filtro, indefinido onde ficou copiadora. A etapa dois tem a sua **leitura** de pé, e não o seu critério.
- Não fecha: o mesmo teste com redes treinadas até perto do ótimo (perda relativa ≤ 0,4, declarada antes como condição de validade da rede), com menos redes e mais passos. É o teste 25, se houver tempo de máquina; a predição deve incluir a condição de treino como pré-requisito, não como aposta.

## Para a lista de defeitos de desenho do projeto

36. Teste de régua sobre rede treinada sem condição de treino declarada: redes que não aprenderam entram no critério e reprovam a régua por algo que não é dela. A condição (perda relativa ≤ limiar) tem de ser pré-requisito.

Vinte e quatro testes, vinte reprovações, quatro passagens, trinta e seis defeitos, uma emenda.
