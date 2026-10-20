# Leitura do teste 35 (o relógio v2): J1 e J2 REPROVADOS. O calendário vence em todo K; a entrada das águas atrasou ≈ 13 dias em 2018–2025, e nenhum dos dois viu

**Predição:** PREDICAO_teste35_relogio_v2.md (bb0b920), antes de escrever o instrumento. **Instrumento:** teste35.py. **Resultados:** resultados_teste35.json; diagnostico_teste35.json (depois da rodada, não julgado). Seis lugares de MT, 48 previsões na calibração e 48 na medida. Dois julgamentos; sem emenda.

Erro absoluto médio (EAM, dias), previsão em 1º de setembro:

| K (rad/dia) | 0 | 0,001 | 0,002 | 0,005 | 0,01 | 0,02 | 0,03 | 0,05 | 0,07 | 0,1 | 0,2 | 0,5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calibração 2010–17 | **11,4** | 11,4 | 11,7 | 12,2 | 13,8 | 16,6 | 30,5 | 42,5 | 41,9 | 41,4 | 54,5 | 44,1 |
| medida 2018–25 | **19,4** | 20,3 | 20,9 | 23,5 | 32,8 | 58,9 | 61,9 | 52,6 | 46,8 | 50,6 | 61,4 | 55,6 |

Em 15/08 e em 15/09 a forma é a mesma: mínimo em K = 0 (19,4 nos dois), crescendo com K.

**K\* = 0**: o calendário é o melhor relógio na calibração.
**J1, o relógio antecipa melhor que o calendário:** com K\* = 0, a diferença é zero. **Reprovado.**
**J2, seguir sem se colar:** o mínimo da medida fica em K = 0, na borda da grade. **Reprovado.**

| lugar | EAM calendário | viés calendário (previsto − real) |
|---|---|---|
| Juara | 15,8 | −11,2 |
| Sinop | 14,0 | −9,3 |
| Cuiabá | 25,2 | −13,0 |
| Barra do Garças | 18,7 | −15,5 |
| Alta Floresta | 19,9 | −13,4 |
| Rondonópolis | 22,6 | −14,5 |
| **todos** | **19,4** | **−12,8** |

Todas as 96 entradas foram definidas (nenhum ano sem entrada até 31/12). Desvio-padrão das entradas, todos os anos e lugares: 20,1 dias.

Apostas: J1 passa (25 %), certa a reprovação; J2 passa (30 %), certa a reprovação; EAM do calendário entre 10 e 20 dias (60 %), certa, na borda (19,4); a correlação entre a fase em 1º/09 e a entrada (40 %) **não pôde ser avaliada como registrada**: com K\* = 0, φ − ωt é zero a menos de arredondamento (o +0,349 do resultados_teste35.json é esse arredondamento acompanhando o tempo, e não vale nada). No diagnóstico, com K > 0, ela vai de −0,09 a +0,29 e nunca chega a −0,3: o atraso da estação seca não anuncia atraso da entrada.

## Diagnóstico depois da rodada (não julgado)

A regra de previsão registrada, t₀ + ((φ_entrada − φ) mod 2π)/ω, manda para o ano seguinte toda previsão em que o relógio, em 1º de setembro, já passou da fase de entrada. Isso aconteceu em até 6 das 48 previsões da medida (K = 0,02 e 0,03). Com a fase embrulhada em (−π, π], que deixa o relógio dizer "a entrada já passou", o EAM cai, mas continua acima do calendário em todo K > 0: 20,3 · 20,9 · 23,5 · 26,3 · 35,1 · 34,9 · 33,6 · 32,3 · 31,3 · 31,0 · 31,6. O defeito piorou os números, mas não muda o veredito.

## O que o resultado diz

**1. A fase que o mundo mostra no fim da seca é ruído para um relógio.** A fase lida no andar 1 se espalha com desvio de ≈ 40 dias em torno do calendário, todo dia, em todos os lugares (verificação do instrumento antes da rodada). Em 1º de setembro a estação seca está no seu extremo, onde o laço do ano anda devagar e a fase é a pior de estimar. Qualquer K que faça o relógio escutar isso por algumas semanas traz o ruído para dentro. O calendário, que não escuta nada, erra menos.

**2. A entrada das águas atrasou cerca de duas semanas em 2018–2025, nos seis lugares.** O calendário de 2010–2017 previu cedo demais em todos: de 9 a 15 dias, média de 12,8. Na calibração ele errava 11,4 dias; na medida, 19,4, e a maior parte dessa diferença é o atraso. É o mesmo deslocamento de clima que os testes 32 e 33 viram no balanço chuva − ET0, agora numa data que um agricultor sente. **Nem o calendário nem o relógio o viram**, porque a forma da estação seca em 1º de setembro não o anuncia.

**3. O que o relógio deveria ter aprendido não estava na fase do campo, e sim nas entradas.** Um relógio que ajustasse a sua fase de entrada a cada entrada vivida, devagar e semeado com 2010–2017, teria acompanhado o atraso ano a ano. Isso é exatamente o desenho da v1, um relógio que aprende o seu período e a sua fase com os eventos, e não com o sinal contínuo. A v2 trocou "aprender com os eventos" por "escutar o campo" e perdeu a única informação que funcionava. Essa é uma hipótese para um teste novo, não um resultado.

## Para a lista de defeitos de desenho

47. A regra de previsão com mod 2π transforma um relógio adiantado num erro de um ano. A regra certa embrulha a fase em (−π, π]. O diagnóstico mostra que o veredito não muda, mas os números julgados estão inflados para K ≥ 0,01.
48. A correlação registrada "com K\*" degenera quando K\* = 0 (φ − ωt ≡ 0). Além disso, o sinal escrito na predição (φ(t₀) − ωt₀) contradiz a frase da aposta ("atraso anuncia atraso" pede correlação negativa com esse sinal). A aposta foi lida pelo que a frase diz.
49. A fase do mundo foi tirada só do 1º harmônico do laço, e a previsão foi feita no extremo da estação seca, onde essa fase é a pior. A conta prévia não estimou o ruído de fase em 1º de setembro; a verificação do instrumento (≈ 40 dias de desvio diário) teria mostrado que um K > 0,005 traz mais ruído do que sinal.

Placar: 35 testes numerados (o 25 sem resultado). 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram. 49 defeitos, 1 emenda.
