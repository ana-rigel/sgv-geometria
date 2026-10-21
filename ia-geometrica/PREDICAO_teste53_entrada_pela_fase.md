# Predição do teste 53 (a entrada das águas lida na fase de um ritmo aprendido: o relógio do andar 2 substitui o calendário escrito?)

21/10/2026 · escrita antes de calcular · relógio do andar 2 do teste 52 (braço A) + laço do relógio v1 do teste 36 · 6 lugares de MT · Ana Rigel

## De onde vem

O teste 52 mostrou que o relógio do andar 2, aprendendo com o erro contra o mundo, aprende o ano e o guarda quando a v0 para de olhar. O relógio v1 (testes 36 e 36b) aprende o dia esperado da entrada das águas, μ ← μ + 0,3(o − μ), mas sobre um calendário escrito: o dia do ano. A Ana pediu para ligar os dois. A entrada passa a ser esperada numa **fase** do ritmo aprendido, e não num dia do calendário.

## As previsões comparadas (2019–2025, 6 lugares, 42 previsões, as mesmas do 36b)

O erro é entrada − previsão: positivo quer dizer que as águas entraram mais tarde que o previsto.

- **C, calendário fixo:** μ₀ = média do dia da entrada em 2010–2017 (36b: EAM 20,0 d).
- **V1, relógio v1:** μ aprendido a partir de 2018, η = 0,3 (36b: EAM 18,8 d, viés +9,7 d).
- **F, fase aprendida, olhando:**
  - φ₂ e ω₂ são o relógio do andar 2 do teste 52, braço A, olhando o campo todo dia de 2010 a 2025, com os mesmos 20 inícios.
  - ψ₀ = média circular de φ₂ nos dias das entradas de 2010–2017.
  - Depois de cada entrada vivida, a partir de 2018: ψ ← ψ + 0,3 · emb(φ₂(entrada) − ψ), onde emb é a diferença embrulhada em (−π, π].
  - A previsão do ano y é feita em 1/09: t₀ + emb(ψ − φ₂(t₀))/ω₂(t₀). A diferença embrulhada evita o salto de um ano que estragou o teste 35.
  - Mediana das 20 previsões (uma por início).
- **F0, fase fixa, olhando:** F com ψ = ψ₀, sem aprender. Pergunta se o ritmo, sozinho, carrega o atraso do ano.
- **S, fase aprendida, em silêncio:** o relógio para de ouvir o campo a partir de 1/1/2018 (o silêncio do teste 52). A v0 só olha o mundo uma vez por ano, na entrada das águas, e aprende ψ com ela.

## Conta prévia (do que já se sabe, sem calcular as previsões)

- **F:** travado no ano, o relógio tem fase quase fixa em relação ao calendário. F deve ficar perto de V1, com diferenças vindas das anomalias de fase do ano. O teste 35 achou que a fase lida no andar 1 no fim da seca é ruído e que o atraso não é anunciado pela forma da seca. O andar 2 integra meses, mas não há razão forte para esperar informação nova: **F0 ≈ C** e **F ≈ V1**, ± 1–2 dias.
- **S:** no silêncio, o relógio atrasa 3 a 8,5 dias por ano (teste 52; média ≈ 5,5).
  - A fase das entradas, lida nele, cai 5,5 dias por ano. Um laço com η = 0,3, seguindo uma rampa, fica para trás em regime em ≈ 5,5 · 0,7/0,3 ≈ 13 dias.
  - Mas o relógio atrasado também cruza ψ mais tarde, o que compensa parte disso. O sinal e o tamanho do erro que sobra não são óbvios.
  - Espero S pior que V1 em alguns dias.

## Critérios

**J1, o ritmo aprendido substitui o calendário sem perda.** EAM(F) ≤ EAM(V1) + **1,0** dia nas 42 previsões.

**J2, o ritmo carrega informação além do calendário.** EAM(F0) ≤ EAM(C) − **2,0** dias, com o intervalo de 95 % (bootstrap por ano, 10.000, semente 53) inteiro abaixo de zero.

**J3, com uma olhada por ano basta.** EAM(S) ≤ EAM(V1) + **3,0** dias.

Relatado: EAM e viés por braço e por lugar; a diferença por ano; o espalhamento das previsões entre os 20 inícios.

## Apostas (Claude, antes de calcular)

- **J1: 65 %.**
- **J2: 15 %.**
- **J3: 40 %.**

## O que fecha

- **J1 passa:** a v0 prevê a entrada das águas tão bem quanto o relógio v1, sem que o calendário esteja escrito nela; o ano que ela usa é o que aprendeu do mundo.
- **J2 passa:** a fase do andar 2 anuncia parte do atraso do ano, o que o teste 35 não conseguiu com o andar 1. **J2 reprova:** o ritmo aprendido é um calendário aprendido, não um preditor da anomalia do ano.
- **J3 passa:** com uma olhada por ano, a memória do ritmo mais a correção pelo erro sustentam a previsão. É o "olhar custa" da v0 em forma prática. **J3 reprova:** o atraso do relógio em silêncio acumula mais rápido do que uma olhada por ano consegue corrigir.

Um julgamento por hipótese; sem emenda. Instrumento: teste53.py, escrito depois do commit desta predição.
