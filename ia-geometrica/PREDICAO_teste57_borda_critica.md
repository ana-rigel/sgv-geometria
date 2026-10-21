# Predição do teste 57 (a hipótese do regime crítico, de novo: o relógio do andar 2 funciona melhor na borda do travamento?)

21/10/2026 · escrita antes de calcular no dado real, com o piloto sintético rodado antes (regra proposta depois do teste 52) · relógio do andar 2 dos testes 52–53 · 6 lugares de MT · Ana Rigel

## De onde vem

A hipótese da ideia original dos três corpos, como a Ana a formulou: **"a mente estaria no regime crítico do acoplamento"**. Ela perdeu a âncora quando o 0,627 da NGC 628 se revelou ruído do feixe (teste 43) e nunca foi testada de novo. A Ana pediu para testá-la outra vez.

Agora há um sistema em que ela pode ser posta à prova sem a galáxia: o relógio do andar 2 (testes 52–53). Ele tem um acoplamento com o mundo (ε) e uma borda conhecida, o travamento. Um relógio de frequência natural ω₀, forçado por um ritmo de frequência Ω e amplitude A, trava se εA/2 ≥ |ω₀ − Ω|. A borda é, portanto,

  **ε_c = 2|λ₂ − Ω| / A₂**,

calculada por lugar com o A₂ da calibração (2010–2017). Em Juara, A₂ = 0,876 e ε_c = 0,0050. Os testes 52–53 usaram ε = 0,01 ≈ 2 ε_c.

**A hipótese, posta como pergunta mensurável:** o relógio serve melhor perto da borda do que longe dela?
- Muito abaixo, ele não trava e não aprende o ano.
- Muito acima, ele trava, mas é escravo do ruído do campo. É o que derrubou a fase ouvindo no teste 53: em 1/09, ela variava 13–49 dias entre anos.

O mecanismo prevê um ótimo interior: o ruído de fase de um relógio travado cresce com ε, e abaixo da borda ele não pega o ano. Se o ótimo cair na borda, a hipótese do regime crítico ganha a sua primeira evidência concreta. Se cair longe, ela perde.

## O instrumento

Igual ao braço F do teste 53, variando só ε:
- relógio do andar 2 ouvindo o campo de 2010 a 2025, aprendendo com o erro contra o mundo (η_w = ε/365, a regra do 52), 20 inícios (semente 51);
- fase esperada da entrada ψ: média circular nas entradas de 2010–2017, depois o laço η = 0,3;
- previsão em 1/09 com diferença embrulhada; mediana dos 20 inícios; 42 previsões (2019–2025).

**Grade:** ε/ε_c ∈ {0,2; 0,3; 0,4; 0,5; 0,7; 1; 1,5; 2; 3; 5; 10}, com o ε_c de cada lugar.

**Medidas por ponto da grade:**
- **EAM das águas,** nas 42 previsões;
- **espalhamento da fase em 1/09** (desvio padrão entre 2018 e 2025 do desvio da fase contra o calendário, em dias; mediana dos lugares);
- ω₂ ao fim de 2017.

## O piloto (rodado antes desta predição; só dados da calibração de Juara)

Dois mundos sintéticos com o ano do andar 2 de Juara:
- ruído AR(1);
- **os resíduos reais de 2010–2017 em blocos de um ano, embaralhados**, que guardam a estação seca e os anos anômalos. Este é o segundo piloto que propus depois do teste 52.

| ε/ε_c | 0,2 | 0,3 | 0,4 | 0,5 | 0,7 | 1 | 1,5 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AR(1): dp da fase (d) | 46 | 19 | 16 | 13 | **4** | **5** | 6 | 7 | 9 | 12 | 16 |
| anos embaralhados: dp da fase (d) | 39 | 15 | 11 | **6** | **6** | **6** | 7 | 8 | 9 | 14 | 22 |
| anos embaralhados: ω₂/Ω, fim 2017 | 0,90 | 1,02 | 1,03 | 1,02 | 0,98 | 0,98 | 0,97 | 0,97 | 0,96 | 0,95 | 0,93 |

**Leitura do piloto:**
- Os dois mundos põem o mínimo do ruído de fase em **0,5–1 ε_c**, subindo dos dois lados.
- Abaixo de 0,3 ε_c, o relógio não pega o ano.
- Acima de 3 ε_c, o ruído cresce e a frequência aprendida fica mais longe do ano.
- O aprendizado leva o relógio a travar um pouco abaixo da borda estática: a 0,3–0,5 ε_c, ele pega o ano pelo arrasto do aprendizado.

## Critérios

**J1, o ótimo está na borda.** O ε da grade com o menor EAM das águas (as 42 previsões juntas) está entre **0,5 e 2 ε_c**.

**J2, o ótimo é interior e marcado.** EAM(ε*) ≤ min(EAM(0,2 ε_c), EAM(10 ε_c)) − **5** dias.

**J3, o mecanismo.** O espalhamento da fase em 1/09 (mediana dos lugares) tem o seu mínimo da grade entre **0,5 e 2 ε_c**.

**J4, na borda exata ele serve.** Sem escolher o ε pelo resultado: EAM no próprio ε = ε_c ≤ **20,0** dias (o calendário fixo do 36b).

Relatado: as três medidas em toda a grade e por lugar; o EAM em 2 ε_c (onde estavam o 52 e o 53) contra o 36,5 do 53; o ε_c de cada lugar.

## Apostas (Claude, antes de calcular)

- **J1: 55 %.**
- **J2: 50 %.**
- **J3: 65 %.**
- **J4: 30 %.** O ruído de fase de 6 dias do piloto é menor que o espalhamento das entradas (16–23 dias). Ainda assim, ouvindo o campo, o teste 53 viu deslizes de ≈ 100 dias que o piloto não tem.

## O que fecha

- **J1–J3 passam:** primeira evidência concreta para a hipótese do regime crítico, com o mecanismo nomeado. Perto da borda, o relógio aprende o mundo sem virar escravo do ruído dele; longe, ou não aprende ou é sacudido. A hipótese deixa de ser sobre um número da galáxia e passa a ser sobre um princípio de projeto: **acoplar o relógio ao mundo no limite do travamento.**
- **J3 passa e J1 reprova:** o mecanismo existe, mas o ruído da fase não é o que decide a previsão das águas (que o teste 53 viu não ter informação do ano). A borda é ótima para o relógio, não para a tarefa.
- **J1 e J3 reprovam:** a hipótese do regime crítico perde no único sistema em que conseguimos testá-la limpa.
- **J4** diz se a borda resolve o fracasso do braço F do teste 53.

Um julgamento por hipótese; sem emenda. Instrumento: teste57.py, escrito depois do commit desta predição; o piloto (piloto57 dentro dele) é rerrodado com sementes fixas.
