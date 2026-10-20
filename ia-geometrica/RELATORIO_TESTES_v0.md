# IA geométrica v0: relatório dos dezessete testes

18/10/2026 · Ana Rigel · consolida PREDICAO_*.md, LEITURA_*.md e resultados_*.json de 17–18/10/2026 · branch `ia-geometrica/v0`

Regras aplicadas em todos: predição escrita e commitada antes de rodar; critério e nulo declarados; 100 sementes; um julgamento por hipótese; nenhuma emenda em nenhum teste (cada defeito foi registrado e virou, no máximo, um teste novo com predição própria). Apostas de Claude escritas antes, erros contados.

## 1. Placar

| | |
|---|---|
| julgamentos | 17 (testes 1–17; o 5, o 6 e o 9 tinham duas hipóteses e o 16/17 compartilham um instrumento) |
| passaram | **2** (16 e 17) |
| reprovaram | 15 (um deles, o 13, inconclusivo além de reprovado) |
| defeitos de desenho nomeados | 28 |
| emendas | 0 |
| apostas de passagem certas | 13 de 17 (as predições apostaram na reprovação em 12 das 15 reprovações e na passagem em 1 das 2 passagens) |

## 2. As três linhas e o estado de cada uma

**A. A v0 como máquina (testes 1–4): filtro.** Com ganhos fixos herdados de março (λ₁ = 0,15, b = 10) a pilha perde de um registro único bem escolhido em todo mundo de deriva; a política de limiar não vale; a régua calibrada com saltos dentro não detecta saltos médios; o ajuste livre por erro de predição não reencontra a escada do mundo. Veredito de 17/10 mantido: como máquina, a v0 é um filtro com andares decorativos.

**B. A política de olhar (testes 2, 7, 10, 11, 12, 13, 14, 15): fechada por cláusula.** Quatro mundos (deriva; deriva com regimes; saltos em cachos esparsos; densos), dois orçamentos (25 %; 5 %), dois registros (λ₁ herdado; do mundo), quatro formas de política (limiar na última tensão; limiar na expectativa; ritmo por regime; ritmo com memória de cacho). A melhor política rende 0–2 % sobre o periódico, e um **oráculo que sabe o regime verdadeiro rende o mesmo** (+1,2 % e +1,8 % nos dois últimos). Para um observador que só olha e lembra, quando olhar quase não importa, porque o custo de não olhar se acumula passo a passo e o periódico já é quase ótimo. O compromisso 3 do projeto (reobservar versus lembrar como o ato que distingue uma mente de um filtro) não se sustentou em mundos de observação pura; a linha de custo segue válida como teoria, não como política.

**C. A declaração de cegueira (testes 5, 6, 9, 16, 17): de pé, com número.** Cinco consertos nomeados antes de cada rodada levaram a correlação entre a cegueira declarada e a real, no andar 1, de 0,16 para 0,999, e no andar 2 de 0,34 para 0,97. Regra completa e testada: **a cegueira de um registro se declara sobre o espectro da sua entrada, pesado por (1 − ganho real do registro), em série mais longa que o registro, e se compõe por produto andar a andar para dar a cegueira sobre o mundo.** Nos quatro andares, em cinco mundos sintéticos com uma a quatro escalas e com algo mais lento que a identidade, a declaração composta acompanha a cegueira real na ordem (ρ 0,999 · 0,967 · 0,976 · 0,913) e no valor (erro mediano 0,020 · 0,007 · 0,006 · 0,023).

**D. A escada pela tensão (testes 4, 8): de pé na escala, pendente na razão.** Ajustar os andares pelo erro de predição acha a escada da predição (λ₁ → 1); ajustar para que as tensões entre andares dividam a potência em partes iguais põe os andares nas constantes de tempo do mundo (λ·τ entre 0,7 e 2,9) e sabe quando não há escada, mas lê razão ≈ 5 num mundo de razão 10, porque os cortes de primeira ordem vazam para os vizinhos. Pendente: andares de corte mais abrupto.

## 3. Tabela dos dezessete

| # | nome | mundo | pergunta | critério | aposta | resultado | veredito | o que ensinou |
|---|---|---|---|---|---|---|---|---|
| 1 | deriva | AR(1), φ ∈ {0; 0,5; 0,9; 0,99} | a pilha rastreia melhor que o melhor registro único? | V > 0 nos φ > 0, crescente, nula em 0 | 55 % | V −0,3 / −10,9 / −56,1 / −92,4 % | reprovado | λ₁ = 0,15 é cego à escala de um passo; um mundo de uma escala não premia uma mente de várias |
| 2 | custo de olhar | deriva φ = 0,9, 25 % de olhadas | olhar pela última tensão ≥ θ bate o periódico? | envelope de V > 0 | 60 → 35 % | V −1,85 % (env −4,3; +0,5) | reprovado | a política dorme cega até n_max; sem expectativa |
| 3 | salto | deriva + teleportes ±8 | regime na régua detecta antes e com menos falsos alarmes que o relativo de março? | ΔFA > 0, Δatraso ≥ 0, Δdet ≥ 0 | 70 % | FA 0,009 vs 33 /1000; detecção 0,20 vs 0,66; atraso 2 vs 2 | reprovado | régua calibrada com saltos dentro só vê saltos maiores que eles; critério sem desconto pelo acaso |
| 4 | escada livre | escada-2/3/4 (τ 7…7000), cíclico | ajuste por erro reencontra a escada? | razões em 7–13 em ≥ 80; cíclico quebra | 50 → 25 % | recupera 1/2/0 de 100; λ·τ 7 · 3,7 · 2,5 · 0; cíclico quebra 100/100 | reprovado (b passou) | o preditor ótimo põe polos na parte MA, não nos φ do mundo; λ₁ → 1 |
| 5 | régua de cegueira | branco, deriva, escada-3, cíclico | a cegueira declarada (sobre a norma da tensão) acompanha a real (A)? serve a um leitor (B)? | ρ ≥ 0,7 nos 4 andares; U > 0 em ≥ 80 por destino | A 55 %, B 40 % | ρ 0,16 · 0,34 · 0,75 · indef.; B explode | A e B reprovados | medir a cegueira sobre o próprio resíduo declara escuridão em toda parte |
| 6 | declaração linear | os de 5, N = 130 k | declaração sobre a entrada do andar (corte abrupto) | os de 5 | A 65 %, B 30 % | ρ 0,993 · 0,404 · 0,870 · −0,11; B explode sem renormalizar | A e B reprovados | sobre a entrada: andar 1 de 0,16 → 0,99; corte abrupto erra onde o filtro é suave; andar 4 sem variação |
| 7 | expectativa | deriva φ = 0,9 | olhar pela tensão esperada a_n + b_n·T bate o periódico? | envelope de V > 0 | 40 % | V +0,13 % (env −3,0; +2,7); b_n → 0,15 em n = 5 | reprovado | num AR(1) a última tensão deixa de informar em 5 passos; a política vira periódica |
| 8 | escada pela tensão | os de 4 | ajuste por partes iguais de potência reencontra a escada? | os de 4 | 30 % | recupera 1/4/1; **λ·τ 0,82 · 1,8 (esc-2), 0,73 · 1,5 · 2,9 (esc-3)**; razões ≈ 5; cíclico quebra e ganha 89/100 | reprovado (b passou) | a tensão lê a escala do mundo; cortes de 1ª ordem vazam e comprimem a razão |
| 9 | ganho real | os de 6 + lento (τ 50 k) | declaração com o ganho real |H_j|² do andar | ρ ≥ 0,7 nos 4 | 55 % | ρ **0,997 · 0,986 · 0,923** · 0,371 | reprovado (3 de 4) | andar 2 consertado (cíclico 0,999 → 0,66 vs 0,77 real); andar 4 diluído: um mundo lento em cinco |
| 10 | expectativa com regimes | AR(1) com σ em blocos (1 / 3, média 200) | a expectativa vale onde há regimes? | envelope de V > 0 | 55 % | V −1,53 %, 48 válidas; b_n ≈ 0,65 até n = 16 | reprovado | a tensão informa o regime; a política de limiar concentra olhadas em rajada, que um registro lento não aproveita |
| 11 | ritmo por regime | o de 10 | o ritmo (p_q, p_f) lido do regime bate o periódico? | envelope de V > 0 | 60 % | V **+0,67 %** (env −0,8; +2,4), V > 0 em 72 | reprovado | primeira média positiva; forma certa; λ₁ = 0,15 segura |
| 12 | ritmo com λ₁ do mundo | o de 10 | idem com λ₁ escolhido na calibração | idem | 50 % | λ₁ 0,94; V +1,19 % (env −2,8; +5,5) | reprovado | teto analítico ≈ 5 % numa deriva: o erro de não olhar cresce como raiz; saber o momento vale pouco |
| 13 | saltos em cachos | deriva + cachos (1/12 por 60 passos) | ritmo lido na régua, com H aprendido, em mundo reflexivo | idem; oráculo como teto | 45 % | V +0,05 %; oráculo +6,9 % com envelope −31 a +37 % | reprovado, inconclusivo | cacho que se renova dura ≈ 2.000 passos: um por janela; afinação ao acaso; o teto tem de ser por janela |
| 14 | cachos densos | cachos de ≈ 140 passos a cada ≈ 300 | idem, conta por janela | idem | 40 % | V +1,31 %; **oráculo +1,19 %** | reprovado | o custo de salto é 8 % do erro; o periódico com 25 % já está perto de olhar sempre |
| 15 | orçamento 5 % | o de 14 | idem com 5 % de olhadas (cláusula: oráculo < 5 % fecha a linha) | idem | 30 % | V +1,82 %; **oráculo +1,80 %**, escolhe quase periódico | reprovado; **linha fechada** | com poucas olhadas, espalhar é ótimo; concentrar no cacho cega o resto |
| 16 | andar da identidade | lento-a/b/c (τ 20 k, 50 k, 100 k), escada-3, cíclico; N = 400 k | a declaração do andar 4 acompanha a real quando há o que declarar? | ρ₄ ≥ 0,7 acima da permutação | 65 % | ρ₄ **+0,746**; andares 1–3: 0,999 · 0,847 · 0,879 | **passou** | a identidade só se mede num mundo que tenha algo mais lento que ela |
| 17 | declaração composta | os de 16 | composta por produto, acerta o valor? | erro mediano ≤ 0,05 nos andares 1–3 | 45 % | erro **0,020 · 0,007 · 0,006** (4: 0,023); ρ 0,999 · 0,967 · 0,976 · 0,913 | **passou** | a composição por produto é a definição exata para a cascata, não aproximação |

## 4. Os vinte e oito defeitos de desenho, agrupados

**Herança sem pergunta ao mundo.** 1 (λ₁ = 0,15), 3 e 9 (b = 10, ajuste pelo erro), 6 (régua de maio com saltos dentro), 23 (política sobre registro herdado).
**Mundos mal postos.** 2 (uma escala), 7 (saltos menores que o ruído), 17 (AR(1) sem momento certo), 24 (teto da política não calculado antes), 25 (cachos raros demais para a janela), 26 (orçamento de 25 % deixa o ato sem o que decidir), 27 (o ato como distintivo em mundos de observação pura).
**Política.** 4 (sem expectativa), 5 e 22 (afinação por bissecção em fração discreta), 21 (limiar concentra olhadas).
**Instrumento de leitura.** 3 (mínimos quadrados sem regularização; tratado no 4), 13 (reescala com renormalização), 16 (reescala de pesos, duas vezes refutada), 10 (sigmoide sem faixa).
**Critérios.** 8 (detecção sem desconto pelo acaso), 15 e 19 (correlação num andar sem variação), 20 (duas definições de cegueira usadas como uma), 28 (composta chamada de aproximação).
**Declaração.** 11 (medida sobre o próprio resíduo), 12 (série menor que o período do andar), 14 e 18 (corte abrupto / vazamento de 1ª ordem).

## 5. O que fica para o OBS-01

Quatro cláusulas, todas com número:

1. A cegueira de um registro se mede sobre a **entrada** do registro, não sobre o seu erro (teste 5 → 6: ρ 0,16 → 0,99 no andar 1).
2. Pesa-se por **1 − ganho real** do registro, não por um corte em frequência (teste 6 → 9: andar 2 de 0,40 → 0,99; cíclico 0,999 → 0,66 contra 0,77 real).
3. A série tem de ser **mais longa que a constante de tempo** do registro medido, e o mundo tem de ter algo mais lento que ele, senão a declaração é verdadeira e vazia (testes 9 → 16: andar 4 de 0,37 → 0,75).
4. A cegueira sobre o **mundo** é a composta por produto das cegueiras sobre as entradas (teste 17: erro 0,13–0,15 → 0,006–0,02).

E uma limitação explícita: tudo isso é a v0 declarando a cegueira **de si mesma**, com ganhos que ela conhece. O OBS-01 quer a cegueira de um observador cujos ganhos ninguém conhece.

## 6. O que vem depois, se vier

Um por vez, cada um com predição própria:

1. **A v0 como régua sobre outro observador** (primeiro passo fora do sintético puro): ela recebe a saída de um registro de ganho desconhecido, estima o ganho a partir da relação entrada–saída e declara a cegueira dele; critério contra a cegueira real desse registro.
2. **Escada pela tensão com andares de corte abrupto** (dois registros de 1ª ordem em cascata por andar, ou pesagem pelo ganho real), para ver se a razão deixa de ser comprimida.
3. Só depois dos dois: fluxos reais, o BTC entre eles, depois de 3/11 e 1/12, com a escada lida pela tensão e a cegueira declarada por andar.

Fora do escopo, confirmado pelos testes: política de olhar (fechada), uso em trading.

## 7. Adendo: teste 18 (a régua sobre outro observador)

| # | nome | mundo | pergunta | critério | aposta | resultado | veredito | o que ensinou |
|---|---|---|---|---|---|---|---|---|
| 18 | régua sobre outro | escada-3 (julgado), deriva (relatado); seis Ω de forma desconhecida | vendo x e y, a v0 acha o corte de Ω e a sua cegueira? | corte ±30 % em ≥ 80 por Ω; erro de cegueira ≤ 0,05 por Ω | 50 % | corte **600/600**; cegueira 0,043 · 0,046 · 0,065 · 0,087 · 0,092 · 0,046 | reprovado em (b) | não ver (1 − \|H\|²) e errar (\|1 − H\|²) diferem para quem atrasa; declarar as duas |

Quinta cláusula para o OBS-01: **cegueira e erro são grandezas diferentes para um observador que atrasa; a régua declara as duas, com nome.** Placar: 18 testes, 16 reprovações, 2 passagens, 30 defeitos.

| 19 | não ver e errar | os de 18 | do mesmo Ĥ, a régua acerta "não ver" (1 − \|H\|²) e "errar" (\|1 − H\|²)? | ambos ≤ 0,05 por Ω em escada-3 | 65 % | não ver ≤ 0,001 nos 12; errar 0,007–0,056 (deriva ≤ 0,003) | reprovado por 0,006 | o sinal de ε − ν mede a ordem do observador |

Placar: 19 testes, 17 reprovações, 2 passagens, 31 defeitos.

| 20 | andares de 2ª ordem | os de 8 | com andares abruptos, a escada pela tensão lê a razão do mundo? | os de 8 | 35 % | razões 5,5 · 6,1 (esc-3), 4,5 · 4,3 · 53 (esc-4), 37 (esc-2); λ₁·τ₁ 0,8–1,1; cíclico ganha 79/100 | reprovado | a compressão vem também do critério de partes iguais, que tem vários mínimos |

Placar: 20 testes, 18 reprovações, 2 passagens, 32 defeitos.

| 21 | descorrelação entre fatias | os de 8 | com outro critério de tensão, a escada lê a razão? (cláusula: reprovando, a linha fecha) | os de 8 | 30 % | andares esvaziados (λ·τ 0,01–0,09) em 100/100 nas escadas 2 e 3; razões sem sentido; cíclico perde da fixa | reprovado; **linha fechada** | a escada do mundo é legível pela tensão em escala, não em razão |

**Placar final de 18/10: 21 testes, 19 reprovações, 2 passagens, 33 defeitos, nenhuma emenda.** Linhas: máquina (filtro), política (fechada), escada (fechada: escala sim, razão não), declaração de cegueira (de pé), régua sobre outro observador (de pé, vendo a entrada).

| 22 | OBS-01 etapa um: RNN sintética | escada-3, 1-D; rede de 32 unidades, vazamentos 0,003–0,3, lida por projeção; linear / tanh 0,1 / tanh 3 | a régua mede uma rede como mede um filtro, e declara quando sai do regime linear? | corte ±30 % em ≥ 80; ν e ε a ≤ 0,05 (rede linear) | 60 % | linear: 97/100, 0,003, 0,013; tanh 0,1: 84/100; tanh 3: 29/100, ν a 0,11, cobertura 0,91 | **passou** (linear) | coerência não detecta saturação; medir em duas amplitudes |

Placar: 22 testes, 19 reprovações, 3 passagens, 34 defeitos.

| 23 | teste de amplitude | os de 22, + ruído 0,05 na saída | a diferença de Ĥ entre duas amplitudes separa linear de não linear? | linear D(3) < 0,05 em ≥ 95; tanh D(3) > 0,05 em ≥ 95 | 70 % | linear 0,006 (95 abaixo); tanh 0,75 (100 acima), 81 já a 0,3 | **passou** (Emenda 1: estimador com a entrada efetiva) | a régua, sendo o mundo, pergunta à rede se é linear |

Placar: 23 testes, 19 reprovações, 4 passagens, 35 defeitos, 1 emenda. OBS-01 etapa um completa.

| 24 | OBS-01 etapa dois: rede treinada | 20 RNN tanh (PyTorch) treinadas a ler a componente lenta da escada-3; 5 mundos de avaliação | sobre uma rede treinada, a régua dá corte estável e coerente com a tarefa? | cv do corte < 0,2 e corte na faixa de Wiener em ≥ 16/20 | 55 % | 9/20 estáveis, 13/20 na faixa; perdas 0,47–0,73 (ótimo 0,31); D(2×) > 0,05 em 15 | reprovado | a régua lê quanto a rede aprendeu; o treino precisa ser pré-requisito |

Placar: 24 testes, 20 reprovações, 4 passagens, 36 defeitos, 1 emenda.

| 25 | OBS-01 etapa dois v2 | 8 RNN treinadas até perda ≤ 0,45 | a do 24, com treino como pré-requisito | ≥ 5/6, 6/7 ou 7/8 válidas estáveis e na faixa | 65 % dado treino | **sem resultado registrado** (a rodada em segundo plano de 18/10 não deixou JSON) | — | a repetir, com a mesma predição |
| 26 | **mundo sítio** | chuva sazonal, córrego (τ 8 h e 30 dias), cheia a 1,2 m; chamar custa 10, cheia sem proteção 100, ato vale 6 h depois | J1: o mundo tem teto? J2: a v0 bate o alarme comum (nível ou subida)? | J1: V_orac mediano ≥ 20 % e > 5 % em ≥ 95; J2: total ≥ 10 % abaixo de N2 e mais barata em ≥ 60 | J1 90 %, J2 15 % | V_orac **90,3 %** (100/100); v0 −1,4 % vs N2 (43 de 100); todas as causais coladas em "nunca" | **J1 passou; J2 reprovado** | o ato vale no sítio; o córrego avisa tarde (3–4 h) para um ato de 6 h; o teto é da previsão de chuva, não do observador do rio |

Placar: 26 testes numerados (o 25 sem resultado), no 26 J1 passou e J2 reprovou; 37 defeitos, 1 emenda. A linha de política reabre no sítio na forma "quando chamar"; o próximo passo pede antecedência (sensor de chuva ou ato mais rápido), não uma mente melhor.

| 27 | **sítio com chuva** | o mundo do 26 + pluviômetro (0,2 mm); teto da chuva calculado antes (40 % abaixo de "nunca" no desenho) | J1: a chuva compra antecedência sobre o córrego? J2: a v0 (surpresa da chuva + vinco do córrego) bate o alarme de chuva e nível? | J1: N3 ≥ 10 % abaixo de N2 e em ≥ 60; J2: v0 ≥ 10 % abaixo de N3 e em ≥ 60 | J1 45 %, J2 15 % | N3 −0,4 % vs N2 (37); v0 +0,9 % vs N3 (56); fração do teto da chuva: N3 6,6 %, v0 9,3 % | **J1 e J2 reprovados** | 76 chuvas/ano, 5,2 % viram cheia protegível; com C/D = 0,1 o ato só se paga acima de 10 %: o gargalo é o preço e a demora do ato, não o sensor |

Placar: 27 testes numerados (o 25 sem resultado); 26: J1 passou, J2 reprovou; 27: J1 e J2 reprovaram; 38 defeitos, 1 emenda. No sítio, a v0 é um alarme como os outros; nenhum sensor local faz um ato de 6 h e custo 10 se pagar.

| 28 | **sítio com ato automático** | o mundo do 27; ato em 1 h e custo 1; mapa L ∈ {1,3,6} × C ∈ {1,3,10} | J1: um alarme comum resolve o sítio? J2: a v0 bate esse alarme? | J1: N3 ≥ 70 % do teto e abaixo de "nunca" em ≥ 95; J2: v0 ≥ 10 % abaixo de N3 e em ≥ 60 | J1 85 %, J2 15 % | N3 85,6 % do teto (100/100); "cada chuva" 89,3 % sem afinação; v0 dois sensores 79,6 %, +39 % de custo vs N3 (34) | **J1 passou; J2 reprovado** | com ato barato, ficar protegido a estação inteira resolve até com 6 h de demora; com ato caro, só a rapidez salva; o sítio é problema de engenharia, e a v0 não acrescenta ao alarme |

Placar: 28 testes numerados (o 25 sem resultado); 26: J1 passou, J2 reprovou; 27: ambos reprovaram; 28: J1 passou, J2 reprovou; 39 defeitos, 1 emenda. No sítio, a v0 como alarme não acrescenta nada a uma regra de chuva e nível; a declaração de cegueira ainda não foi testada lá.

| 29 | **declaração no sítio** | o mundo do 28; ato (6 h, custo 3); verdade = cheia perdida ou protegida pelo alarme comum | J1: a declaração do andar 1 na janela de 48 h separa perdidas de protegidas? J2: melhor que "subiu em L h"? | J1: AUC ≥ 0,70 e IC acima da permutação; J2: diferença ≥ 0,03 com IC > 0 | J1 60 %, J2 15 % | AUC 0,657 (perm q95 0,53); subida em 6 h 0,802; diferença −0,145 | **J1 e J2 reprovados** | a declaração aponta certo mas comprimida (0,82 contra 0,76): janela da escala do andar (defeito 12 de novo); a subida em L h diz o que o ato precisa |

Placar: 29 testes numerados (o 25 sem resultado); 26: J1 passou, J2 reprovou; 27: ambos reprovaram; 28: J1 passou, J2 reprovou; 29: ambos reprovaram; 40 defeitos, 1 emenda. No sítio, nem como alarme nem como declaração a v0 cumpre uma função que uma regra simples não cumpra melhor; o que o sítio pede é um ato automático, barato e rápido, com uma regra simples de chuva e nível.
