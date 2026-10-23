# Leitura do teste 25 (etapa dois v2) — INCONCLUSIVO pela cláusula: nenhuma rede chegou ao pré-requisito

**Predição:** PREDICAO_teste25_rede_treinada_v2.md (2006a9e), antes de rodar. **Resultado:** resultados_teste25.json. Sem julgamento da régua: a cláusula escrita antes (menos de 6 redes com perda relativa ≤ 0,45 → inconclusivo) foi acionada.

| rede | perda relativa (4.000 passos) | corte mediano | cv | na faixa | ν̂ | D(2×) |
|---|---|---|---|---|---|---|
| 1 | 0,55 | 5,6 × 10⁻² | 0,30 | não | 0,22 | 0,046 |
| 2 | 0,55 | 3,4 × 10⁻³ | 0,15 | sim | 0,43 | 0,085 |
| 3 | 0,66 | 8,5 × 10⁻⁴ | 0,28 | sim | 0,63 | 0,112 |
| 4 | 0,58 | 8,5 × 10⁻⁴ | 0,14 | sim | 0,52 | 0,032 |
| 5 | 0,55 | 7,3 × 10⁻⁴ | 0,22 | sim | 0,54 | 0,054 |
| 6 | 0,63 | 1,5 × 10⁻³ | 0,21 | sim | 0,48 | 0,108 |
| 7 | 0,63 | 7,3 × 10⁻⁴ | 0,22 | sim | 0,60 | 0,139 |
| 8 | 0,60 | 1,6 × 10⁻³ | 0,99 | sim | 0,44 | 0,035 |

**Válidas: 0 de 8** (perda 0,55–0,66; o ótimo linear é 0,31). Apostas: "≥ 6 chegam a 0,45" (60 %): errada. Quadruplicar os passos (1.000 → 4.000) não levou a perda abaixo de 0,55: a RNN tanh de 32 unidades com BPTT em blocos de 2.000 e lr 3e-3 não aprende a separar a escala de 700 passos; o limite é de treino (horizonte de BPTT curto para uma componente de τ = 700, taxa de aprendizado), não de capacidade. Defeito 37: o pré-requisito de treino foi declarado sem antes mostrar que a receita de treino o alcança; a fumaça devia ter ido até o pré-requisito.

**O que a régua disse mesmo assim (relatado, sem valor de julgamento):** 7 de 8 redes com corte na faixa de Wiener e ν̂ entre 0,43 e 0,63 (viraram filtro, ainda que raso), 2 de 8 estáveis a cv < 0,2, 5 de 8 não lineares pelo teste de amplitude. É a mesma leitura do teste 24: a régua vê o filtro que a rede virou e vê quanto faltou.

**O que vem depois, se vier:** uma receita de treino que atinja ≤ 0,45 antes do teste (horizonte de BPTT ≥ 5.000, lr menor com decaimento, ou GRU), demonstrada numa rede antes de ser pré-requisito; depois o teste 25 de novo, com a mesma predição. Até lá, a etapa dois do OBS-01 fica com leitura de pé e sem julgamento.

Vinte e cinco testes, vinte reprovações, quatro passagens, um inconclusivo, trinta e sete defeitos, uma emenda.

---

# Segunda rodada (23/10/2026, Emenda 1) — PASSOU

**Instrumento:** teste25.py com a Emenda 1 (GRU de 32 unidades; estado carregado entre blocos; Adam 3e-3 com cosseno; 1.500 passos). **Resultado:** resultados_teste25_v2.json. Um julgamento.

| rede | perda relativa | válida (≤ 0,45) | corte mediano | cv | na faixa | ν̂ | ε̂ | D(2×) | sem treino: corte |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0,336 | sim | 7,3 × 10⁻⁴ | 0,09 | sim | 0,71 | 0,57 | 0,073 | 8,0 × 10⁻² |
| 2 | 0,421 | sim | 6,1 × 10⁻⁴ | 0,09 | **não** (abaixo por 15 %) | 0,70 | 0,50 | 0,045 | 1,0 × 10⁻¹ |
| 3 | 0,463 | não | 1,1 × 10⁻³ | 0,10 | sim | 0,64 | 0,47 | 0,140 | 5,8 × 10⁻² |
| 4 | 0,396 | sim | 1,1 × 10⁻³ | 0,12 | sim | 0,64 | 0,43 | 0,012 | 1,4 × 10⁻¹ |
| 5 | 0,374 | sim | 8,5 × 10⁻⁴ | 0,09 | sim | 0,68 | 0,49 | 0,048 | 8,4 × 10⁻² |
| 6 | 0,419 | sim | 1,3 × 10⁻³ | 0,06 | sim | 0,60 | 0,45 | 0,106 | 7,3 × 10⁻² |
| 7 | 0,452 | não | 8,5 × 10⁻⁴ | 0,09 | sim | 0,66 | 0,48 | 0,084 | 5,6 × 10⁻² |
| 8 | 0,385 | sim | 8,5 × 10⁻⁴ | 0,00 | sim | 0,67 | 0,45 | 0,068 | 6,5 × 10⁻² |

**Válidas: 6 de 8** (redes 3 e 7 ficaram a 0,46 e 0,45, por um fio). Entre as válidas, estáveis e na faixa: **5 de 6** (exigido 5). **Passou.** Quinta passagem do projeto; a etapa dois do OBS-01 está feita em rede pequena. Apostas: ≥ 6 chegam ao pré-requisito (60 %): certa, no limite; passar dado que chegam (65 %): certa; D(2×) > 0,05 em ≥ 5 das válidas (60 %): certa (4 das 6 válidas, 5 das 8 — errada pela contagem estrita; registrada como errada).

## O que o resultado diz

**Oito redes treinadas separadamente, com pesos que a régua não conhece, convergiram para o mesmo observador, e a régua o leu igual nas oito:** corte entre 6 × 10⁻⁴ e 1,3 × 10⁻³ (período de 750 a 1.600 passos, em torno da constante de tempo da componente que a tarefa pede, 700), com cv ≤ 0,12 entre cinco mundos novos, "não ver" entre 0,60 e 0,71 (barram dois terços do mundo: o lento é um terço da potência, e é o que deixam passar), "errar" entre 0,43 e 0,57. Sem treino, o corte das mesmas redes está em 0,06–0,14: o treino o move cem vezes, até a escala da tarefa, e a régua vê isso rede a rede. A rede 2 reprovou "na faixa" por 15 % abaixo da borda inferior, com cv 0,09: é a mais lenta das oito, não uma instável; a faixa de Wiener com folga 2× é uma convenção, e ela caiu fora dela por pouco.

Não linearidade: D(2×) entre 0,012 e 0,14; cinco de oito acima do limiar, com a rede 4 quase linear (0,012) e a 3 bem não linear (0,14). As cláusulas valem por amplitude, e a régua declara em qual.

A diferença entre a primeira e a segunda rodada é só a receita de treino (defeito 37): com redes que aprenderam, a régua passa com folga no critério de estabilidade (8 de 8 com cv < 0,2) e com uma exceção de borda no de faixa. A leitura do teste 24 estava certa: a régua lê quanto a rede aprendeu; faltava a rede aprender.

## O que fecha e o que não

- Fecha: a régua lê um observador treinado por gradiente, sem acesso aos pesos, com corte estável entre mundos e coerente com a tarefa, e declara regime e não linearidade. Etapa dois do OBS-01: feita em rede pequena (GRU 32).
- Não fecha: a etapa três, um modelo de pesos abertos lido camada a camada (a cegueira composta por profundidade), e a quatro, um modelo fechado por API com a série embutida em texto e a resolução limitada pelo contexto.

Vinte e cinco testes julgados (um deles duas vezes), vinte reprovações, **cinco passagens**, trinta e sete defeitos, duas emendas (23 e 25, ambas de instrumento).
