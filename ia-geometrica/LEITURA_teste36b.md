# Leitura do teste 36b (adendo ao 36): J1 REPROVADO, J2 PASSOU (5 de 6). O relógio corrige quase metade do viés, mas o ganho no erro é pequeno

**Predição:** PREDICAO_teste36b_previsao_real.md (3e7a0a3), antes da conta. **Instrumento:** teste36b.py. **Resultado:** resultados_teste36b.json. Dois julgamentos; sem emenda.

Erro = entrada − previsão (positivo: as águas entraram mais tarde que o previsto). 2019–2025, 7 anos por lugar.

| lugar | EAM relógio | EAM calendário | viés relógio | viés calendário |
|---|---|---|---|---|
| Juara | **15,8** | 17,3 | +6,3 | +13,7 |
| Sinop | **12,8** | 14,5 | +7,6 | +12,3 |
| Cuiabá | **23,1** | 25,6 | +15,0 | +18,1 |
| Barra do Garças | **18,4** | 19,7 | +6,9 | +19,3 |
| Alta Floresta | **21,1** | 21,2 | +6,6 | +17,1 |
| Rondonópolis | 21,9 | **21,6** | +15,8 | +21,0 |
| **total (42)** | **18,8** | 20,0 | **+9,7** | +16,9 |

Diferença no EAM por ano (relógio − calendário, média nos lugares): 2019 +0,7 · 2020 +0,9 · 2021 −2,8 · 2022 −3,2 · 2023 −5,3 · 2024 +0,7 · 2025 +0,9.

**J1, prevê melhor:** EAM −1,1 dia (IC −3,0; +0,4). Não chega a −2 e o intervalo inclui zero. **Reprovado.**
**J2, prevê melhor por lugar:** relógio melhor em **5 de 6** (todos, exceto Rondonópolis, por 0,3 d). **Passou.**

Apostas: J1 passa (20 %), certa a reprovação; diferença ≤ −2 d (50 %), errada (−1,1); J2 passa (55 %), certa; viés do relógio menor (85 %), certa (+9,7 contra +16,9).

## O que o resultado diz

**1. O aprendizado é real, e a direção está certa.** Nas mesmas 42 previsões, o relógio tirou **43 %** do viés do calendário (de +16,9 para +9,7 dias). Errou menos em cinco dos seis lugares, e no sexto empatou. É a resposta prática que o 36 não dava: aprender deixou a previsão menos atrasada que não aprender, em quase todo lugar.

**2. O ganho é pequeno porque o ano é mais barulhento que o atraso.** O atraso médio (≈ 17 d no calendário) tem a mesma ordem do espalhamento entre anos (σ ≈ 15–20 d). A conta prévia esperava ganho de 1 a 4 dias; veio 1,1. Com sete anos, o intervalo não fecha.

**3. A curva por ano mostra o laço trabalhando, e o preço dele.** Nos dois primeiros anos o relógio ainda está no calendário e não ganha nada. De 2021 a 2023, depois de aprender com a entrada muito tardia de 2020, ele ganha de 3 a 5 dias. Em 2024 e 2025 volta a perder um pouco, porque correu atrás do extremo de 2023 e passou a esperar tarde demais. O atraso não chegou como um degrau limpo: veio concentrado em anos extremos (2020 e 2023), e um laço que aprende com um evento por ano persegue os extremos.

**4. Sobra viés (+9,7 d) porque um evento por ano é pouco.** A placa precisaria de mais anos para encostar no atraso, ou de mais eventos por ano. É a mesma conclusão da leitura do 36 e a razão do desenho do laço do ato.

## O que fecha para o 36

O J3 do 36 ("μ andou") agora tem a contraparte prática. O relógio que aprende **prevê com menos viés e erra menos em 5 de 6 lugares** que o calendário. A vantagem média é de ≈ 1 dia, ainda dentro do ruído de sete anos. Ele é melhor que não aprender, mas por pouco.

Placar: 36 testes numerados mais o adendo 36b (o 25 sem resultado). 36b: J1 reprovou, J2 passou. 50 defeitos, 1 emenda. Nenhum defeito novo: a conta prévia acertou a ordem do ganho e o porquê.
