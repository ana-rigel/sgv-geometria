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
