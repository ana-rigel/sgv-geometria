# Leitura do teste 9 (a declaração com ganho real) — REPROVADO (3 de 4 andares passam)

**Predição:** PREDICAO_teste9_ganho_real.md (0d68e4f), antes de rodar. **Resultado:** resultados_teste9.json. Um julgamento; sem emenda.

| andar | ρ (δ̂, β), 500 pares | envelope de permutação | erro absoluto mediano | veredito |
|---|---|---|---|---|
| 1 | **+0,997** | −0,15 a +0,16 | 0,032 | sim |
| 2 | **+0,986** | −0,15 a +0,15 | 0,151 | sim |
| 3 | **+0,923** | −0,12 a +0,16 | 0,114 | sim |
| 4 | +0,371 | −0,13 a +0,16 | 0,083 | não |

**Reprovado** pelo critério (quatro andares). Apostas: 55 % em passar (certa a não-passagem); por andar 90/75/80/55 %: certas as três passagens, errada a do 4; erro mediano < 0,05 nos andares 1–3 (errada: 0,03, 0,15, 0,11); diferença sistemática por mundo com δ̂ < β (certa; ver abaixo).

| mundo | δ̂ ganho real (1–4) | β real (1–4) |
|---|---|---|
| branco | 0,92 · 0,92 · 0,90 · 0,92 | 0,78 · 1,00 · 1,00 · 1,00 |
| deriva | 0,39 · 0,80 · 0,90 · 0,92 | 0,33 · 0,95 · 1,01 · 1,00 |
| escada-3 | 0,20 · 0,39 · 0,62 · 0,87 | 0,17 · 0,56 · 0,88 · 1,01 |
| cíclico | 0,03 · **0,66** · 1,00 · 1,00 | 0,03 · **0,77** · 1,07 · 1,00 |
| lento | 0,22 · 0,03 · 0,07 · **0,51** | 0,19 · 0,25 · 0,29 · **0,60** |

## O que o resultado diz

O ganho real consertou o andar 2 exatamente onde a predição disse: no cíclico a declaração passou de 0,999 (teste 6) para 0,66, e a verdade é 0,77. Com isso o andar 2 foi de ρ 0,40 para 0,99, e o andar 3 de 0,87 para 0,92. A sequência 5 → 6 → 9 no andar 1 é 0,16 → 0,99 → 0,997; no andar 2, 0,34 → 0,40 → 0,99. Cada conserto foi nomeado antes e fez o que devia.

O andar 4 reprovou por diluição, não por erro: no mundo lento ele declara 0,51 e a verdade é 0,60 (ordem certa, valor perto); nos outros quatro mundos β₄ é 1,00 ± ruído e δ̂₄ varia de 0,87 a 1,00, e nesses 400 pares a correlação de postos é só ruído contra ruído. Um mundo lento entre cinco não basta para o Spearman; a predição apostou 55 % e perdeu por isso. O erro absoluto mediano do andar 4 é 0,083, menor que o dos andares 2 e 3.

A diferença sistemática que a predição anunciou apareceu: nos andares 2 e 3, δ̂ fica **abaixo** de β (0,80 contra 0,95; 0,62 contra 0,88), porque β é o resíduo do andar sobre o **mundo** (acumula o que os andares anteriores também não viram) e δ̂ é sobre a **entrada** do andar. São duas perguntas diferentes: "quanto da minha entrada eu não vejo" e "quanto do mundo eu não vejo". A v0 responde à primeira; o auditor mede a segunda; e a segunda é a composição das primeiras (1 − β_j ≈ Π (1 − δ̂_i) em primeira aproximação, se as bandas fossem disjuntas). Isso não é defeito; é a definição certa a escolher antes do próximo teste, e fica escrito.

## O que fecha e o que não

- Fecha: a v0 tem uma declaração de cegueira verdadeira na ordem nos andares 1–3, em cinco mundos, com a regra completa: sobre a entrada, com o ganho real. Fecha também que o andar 4 declara certo onde há o que declarar (lento) e que o critério não cabe onde não há.
- Não fecha: o andar 4 com mundos suficientes (três ou mais mundos com potência abaixo de f₄, com N ≥ 10 τ); e a declaração **composta** (sobre o mundo, 1 − Π(1 − δ̂_i)) contra β no valor, não só na ordem.

## Para a lista de defeitos de desenho do projeto

19. Um mundo lento entre cinco: o andar 4 tem variação real em 100 pares e ruído em 400; o Spearman dilui. O critério do andar mais lento precisa de mundos onde a identidade varia, na maioria.
20. Duas definições de cegueira (sobre a entrada; sobre o mundo) usadas como se fossem uma; a composta é a comparável a β.

Nove testes, nove reprovações, vinte defeitos. Ao OBS-01: a régua de cegueira, no mundo sintético, é esta: **espectro da entrada do registro, pesado por (1 − ganho real), em série mais longa que o registro, composta andar a andar quando se quer a cegueira sobre o mundo.** Três das quatro cláusulas já foram testadas e sustentam número.
