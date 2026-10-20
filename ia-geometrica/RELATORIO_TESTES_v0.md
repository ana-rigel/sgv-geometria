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

| 30 | **seca silenciosa em Juara** (dados reais de reanálise) | ERA5-Land/ERA5, Juara, 2010–2025, diário; verdade = solo de 28–100 cm ≤ −1 desvio do normal do dia; silencioso = superfície ≥ normal | J1: a v0 (sobre chuva − ET0) acompanha a seca profunda? J2: nos dias silenciosos, melhor que o SPEI? | J1: AUC ≥ 0,80 e IC > 0,5; J2: dif ≥ 0,03 com IC > 0 | J1 70 %, J2 10 % | v0 (R2, τ ≈ 67 d) 0,780; SPEI-90 0,778; silenciosos 0,775 contra 0,781; vincos abaixo do nível simples | **J1 e J2 reprovados** | a v0 é um índice de seca com outro nome; o vinco informa menos que o acumulador; a seca "silenciosa" não é silenciosa para um índice de 3 meses |

Placar: 30 testes numerados (o 25 sem resultado); 26: J1 passou, J2 reprovou; 27, 29, 30: ambos reprovaram; 28: J1 passou, J2 reprovou; 41 defeitos, 1 emenda. Primeiro teste com dados reais do lugar: a v0 empata com o índice padrão de seca.

| 31 | **onde a samambaia quebra** (dez lugares não vistos) | ERA5-Land/ERA5, 2010–2025, diário; v0 sobre solo 28–100 cm, chuva − ET0 (7 d) e VPD; Juara fora (foi onde se viu) | J1: a fração anual cai abaixo de ½ entre os andares 2 e 3 em MT? J2: no Sul nem o andar 2 é anual? | J1: ≥ 4 de 5 em MT; J2: andar 2 < 0,5 em Porto Alegre e Curitiba | J1 80 %, J2 30 % | MT 5/5 entre 2 e 3; Manaus e Belém também; Curitiba e Petrolina sem ano em nenhum andar; Porto Alegre andar 2 = 0,52; andar 3 < 0,3 nos dez | **J1 passou; J2 reprovado (por 0,02)** | a quebra mora onde a estação é forte e some onde não é; o andar 3 é sempre não anual (conta de filtro): o informativo é o andar 1–2 |

Placar: 31 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30: ambos reprovaram; 42 defeitos, 1 emenda. Em seis lugares de MT os andares 1–2 leem a estação e o 3 é o primeiro a ler o clima.

| 32 | **a organização aprende o ano** | ERA5-Land/ERA5, 5 lugares de MT (Juara relatada); organização ⋄ = 5 coeficientes do ano por mínimos quadrados recursivos, fria em 01/01/2018; memória no R2; medida 2019–2025 | J1: a ⋄ faz a placa ler seca (vs. v0 crua)? J2: a placa sem história empata com o SPEI-90 de 8 anos? | J1: ganho ≥ 0,05 em ≥ 4/5; J2: diferença ≥ −0,03 em ≥ 4/5 | J1 90 %, J2 50 % | fração anual dos andares 1–2: 0,54–0,92 → 0,01–0,11; J1 1/5; J2 2/5 (Alta Floresta −0,02, Rondonópolis −0,004); Juara −0,006 | **J1 e J2 reprovados** | a ⋄ remove o ano, mas instalada no começo da seca de 2019–25 aprendeu a seca como normal (Cuiabá: −1,50 mm/d aprendido contra −0,23 de 2010–17); o calendário sozinho vale AUC 0,61–0,69 nessa verdade; a placa precisa nascer com o clima (5 números) e aprender a partir dele |

Placar: 32 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32: ambos reprovaram; 44 defeitos, 1 emenda. Primeira peça da organização ⋄: aprende o ritmo, e o teste mostrou que aprender o normal sozinho depende de quando se nasce.

| 33 | **organização semeada** | os do 32; ⋄ semeada com 5 coeficientes de 2010–2017 (aprendendo ou congelada); AUC dentro de cada mês; portão: calendário entre 0,40 e 0,60 | J1: a placa semeada empata com o SPEI-90? J2: aprender depois de semeada não atrapalha? | J1: ≥ −0,03 em ≥ 4/5; J2: ≥ −0,02 em ≥ 4/5 | J1 55 %, J2 35 % | portão OK (0,445–0,522); J1 3/5 (Sinop −0,063, Barra −0,074); J2 2/5 (Sinop, Cuiabá, Barra −0,02 a −0,03; AF e Rondonópolis +0,02) | **J1 e J2 reprovados** | onde perde, perde pela memória (até a referência fixa perde do SPEI em Sinop e Barra); aprender custa ≤ 0,03 onde o clima secou; a AUC por mês apaga o trabalho da ⋄; o valor dela só se mede com limiar fixo na régua |

Placar: 33 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33: ambos reprovaram; 45 defeitos, 1 emenda. A organização ⋄ semeada com 5 números guarda o normal quase como 365 médias; o teste do valor dela é um alarme na régua ao longo do ano.

| 34 | **a régua da organização** | andar 3 da v0 sobre o campo do Cérebro de Juara; 100 mundos (permutações dos 16 anos); positivos P(γ) com 𝒢 interno (⋄ guarda o ritmo e o bombeia no andar), γ 0,05–1,00; negativos sem padrão guardado (pura, ruído vermelho, λ × 1,5, esquecimento não linear) | a régua acha organização quando existe e não a inventa? A: sombra passiva (ajustada, nominal, exata); B: silêncio (o mundo perde as estações e mede-se o ciclo que fica) | J1: piso de B ≤ 0,50; J2: piso de A ajustada ≤ 0,50 (detecção ≥ 90/100 acima do q95 dos negativos) | J1 50 %, J2 20 % | B: 85/100 em γ 0,50, 100 em 1,00 (fundo q95 0,22); A ajustada: λ̂ absorve 92 % do 𝒢 (razão 0,077), 11 e 77/100 em 0,50 e 1,00; A nominal: exata (±0,005), 100/100 já em 0,05, mas N2 e N3 dão falso positivo em 100/100 (Θ ≈ 1,0–1,15) | **J1 e J2 reprovados** | com a arquitetura declarada a régua é exata, e chama de organização qualquer desvio dela; ajustada aos dados, lê organização como memória mais curta; o silêncio é específico, mas o fundo de 8 contra 8 anos de clima só deixa ver 𝒢 ≳ 0,5–1; a fase (C_φ) não separa nada |

Placar: 34 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34: ambos reprovaram; 46 defeitos, 1 emenda. A organização de um corpo se mede contra a arquitetura que se declara; observando de fora, só intervindo, e só quando é grande.

| 35 | **o relógio v2** | ERA5-Land/ERA5, Juara + 5 lugares de MT; oscilador de fase que nunca se reinicia, semeado com o laço do ano (2010–17) e acoplado com força K à fase lida no andar 1; K = 0 é o calendário; alvo = entrada das águas (≥ 25 mm em 5 dias sem veranico de 10 dias nos 30 seguintes), previsão em 1º/09 | J1: o relógio antecipa melhor que o calendário? J2: o ótimo fica num K interior (seguir sem se colar)? | J1: EAM(K\*) − EAM(0) ≤ −3 d com IC < 0; J2: mínimo interior ≥ 2 d abaixo dos extremos | J1 25 %, J2 30 % | K\* = 0; EAM 19,4 d (calendário) e crescente com K; fase do mundo no andar 1 com ≈ 40 d de ruído diário; entrada **≈ 13 d mais tarde** em 2018–25 nos 6 lugares (viés −9 a −15,5 d); regra mod 2π saltou um ano em até 6/48 (diagnóstico embrulhado: ainda pior que o calendário) | **J1 e J2 reprovados** | no fim da seca, a fase do campo é ruído para um relógio; o calendário vence; o atraso da entrada não é anunciado pela forma da seca, e só um relógio que aprenda com as entradas vividas (a v1) poderia acompanhá-lo |

Placar: 35 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram; 49 defeitos, 1 emenda. O relógio que escuta o campo perde do calendário; o que o mundo de MT mudou estava nas datas de entrada, não na fase da seca.

| 36 | **ela aprende com o erro?** | relógio v1: μ (dia esperado da entrada das águas) corrigido a cada entrada vivida, μ ← μ + 0,3(o − μ); 100 mundos sintéticos com o ruído real das entradas (dp 13,4 d), 24 estações; real: 6 lugares de MT, semente 2010–17, aprende 2018–25 | o laço aprende (semente errada), readapta (degrau; atraso real), não aprende ruído, e depende do erro e da ordem? | J1: \|p₇ − 280\| ≤ 10 d e ≥ 90; J2: pós − pré ≥ 10 d em ≥ 80; J3: μ anda ≥ +6 d em ≥ 4/6; J4: deriva ±3 d e ≥ 95 a < 15 d; J5: embaralhado ≤ 20 e invertido < 0 em ≥ 90 | 95 · 80 · 55 · 85 · 80 % | J1 5,6 d e 100; J2 82 (mediana 16,7 d); J3 **6/6** (+10 a +25 d); J4 −0,45 d e 100; J5 embaralhado 12, invertido **62** (explosão de ≈ 300 d domina; isolado, o degrau dá negativo em 100/100) | **J1–J4 passaram; J5 reprovado** | o primeiro laço de erro da v0 aprende, readapta em 3–4 estações, não deriva, e some quando a ordem dos erros é embaralhada; no real, acompanhou o atraso da entrada nos seis lugares, mais onde atrasou mais |

Placar: 36 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram; 36: J1–J4 passaram, J5 reprovou; 50 defeitos, 1 emenda. A v0 tem o seu primeiro laço de aprendizado com o erro; ele é lento (um evento por ano) e mexe só em μ.

| 36b | **adendo: a previsão real do relógio** | as previsões e entradas reais do 36 (6 lugares de MT, 2019–2025, 42 previsões), sem rodar o laço de novo | o relógio que aprende erra menos que o calendário fixo de 2010–17? | J1: EAM ≤ −2 d com IC < 0 (bootstrap nos anos); J2: melhor em ≥ 4/6 | J1 20 %, J2 55 % | EAM 18,8 contra 20,0 (−1,1 d; IC −3,0; +0,4); 5/6; viés +9,7 contra +16,9 | **J1 reprovado; J2 passou** | aprender tira 43 % do viés e erra menos em 5 de 6 lugares, mas o ganho (≈ 1 d) fica dentro do ruído entre anos; com um evento por ano o relógio persegue os anos extremos (2020, 2023) |

Placar: 36 testes numerados mais o adendo 36b (o 25 sem resultado); 36b: J1 reprovou, J2 passou; 50 defeitos, 1 emenda.

| 37 | **a galáxia no cubo: o laço que segura o modo** | modelo ilustrativo da NGC 628: 12 anéis, m = 5, 200 km/s, Kuramoto, v0 dentro do disco; 100 sementes, 1 Gyr. A: K = 0; B: K = 1,2 K_c; Laço I: K corrigido até C̄ = 0,627; Laço II: K = 0,8 K_c, rigidez do andar escutado modulada por \|R\| − C (sem alvo) | o instrumento reproduz o enrolamento? B fica na faixa da NGC 628? o laço com alvo converge? o andar 2 segura sozinho? o andar 2 é o pior? | J1: desvio ≤ 0,05 e t(C<0,5) = 87,5 ± 5; J2/J4: ≥ 80 na faixa 0,527–0,727 (J4 com efeito ≥ +0,10); J3: K∞/K_c 0,9–1,1 e \|C̄ − 0,627\| ≤ 0,05 em ≥ 80; J5: andar 2 com a menor mediana | 90 · 5 · 70 · 40 · 50 % | A: 0,0505 em 282 Myr (piso de \|Z\|), 86 Myr; B: 0,866, 0/100; Laço I oscila (K/K_c 1,67 → 0,71 → 1,0), 8/100; andar 2 vazio: \|R₂\| só chega a 0,62, C̄ 0,30, 0/100; andar 3 semeado **sem laço**: 0,662, 100/100 | **J1–J4 reprovados; J5 passou** | o andar 2 é lento demais para aprender e rápido demais para segurar; quem segura perto de 0,627 é a memória lenta semeada, com ou sem laço; 0,627 se obtém de muitas formas no modelo, e nenhuma fala da galáxia |

Placar: 37 testes numerados (o 25 sem resultado); 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram; 36: J1–J4 passaram, J5 reprovou; 37: J1–J4 reprovaram, J5 passou; 53 defeitos, 1 emenda.

| ato A | **o laço do ato** (registrado como 37, renomeado: o 37 é da galáxia) | mundo sítio de cheias, 8 anos, L 1 h, C 10; órgão: 36 marcas (θc, θv) sobre a régua fixa, custo descontado (h = 1 ano), age pela de menor custo; córrego assoreia no 5º ano | a ⋄ aprende com a consequência do que faz e readapta quando o mundo muda? | J1 ≤ 1,10 da melhor fixa em ≥ 80; J2 ganho sobre a afinada ≥ 10 % e ≥ +10 pontos sobre o mundo parado; J3 ≤ 1,05 da afinada (total e em ≥ 70); J4 controle sem a mudança ≤ metade | 30 · 85 · 85 · 75 % | J1 35/100 (mediana 1,13); J2 **31,7 %** contra 5,0 %, 80/100; J3 total 0,958 mas 67/100; J4 3,9 %, B < D em 95/100; outro sítio 25,2 % | **J2 e J4 passaram; J1 e J3 reprovados** | primeiro caso em que aprender vale mais que a regra afinada (−32 % depois que o mundo muda), e é o erro certo que ensina; o preço é tremer num mundo parado (pior que a afinada em 1/3 dos mundos); o teste B fica para depois de uma histerese na troca de marca |

Placar do laço do ato: 1 teste; J2 e J4 passaram, J1 e J3 reprovaram; 1 defeito (ato-A-1).

| 38 | **o laço que apara** | modelo do 37, escuta no andar 3, 5.000 Myr, 100 sementes; a voz g da memória se ajusta sem alvo: III-a pela autoconsistência (log g ← log g + 0,05(C − \|R₃\|)); III-b pela criticidade (busca do máximo da flutuação de C, sondagem de 100 Myr); referência g = 1; K = 0,7 · 0,8 · 0,9 K_c; memória semeada e vazia | o laço apara até a faixa da NGC 628? tem um ponto próprio, igual em todo K? cria ordem a partir da memória vazia? | J1/J3: ≥ 80 na faixa (0,8 K_c); J2/J4: medianas a ≤ 0,05 entre os K; J5: vazia ≤ 0,25 nos dois | 25 · 15 · 35 · 40 · 60 % | referência: 0,25 · 0,29 · 0,40 (a ordem semeada se desfaz); III-a: 0,999 em todos os K e na vazia (o piso de \|Z\| faz C − \|R₃\| > 0, g vai ao teto, trava tudo); III-b: g quase parado (1,0 → 1,4), 0,43 · 0,78 · 0,87, sementes divididas entre soltar e travar (7 na faixa) | **J2 passou pela letra; J1, J3, J4, J5 reprovados** | nenhum laço apara sem alvo; a autoconsistência confunde o piso do acaso com ordem e cria estrutura demais; a busca da borda não sai do lugar; a ordem semeada dura ≈ 1–2 Gyr |

Placar: 38 testes numerados (o 25 sem resultado), mais o teste do ato A; 38: J2 passou pela letra, J1, J3, J4, J5 reprovaram; 56 defeitos nesta numeração, 1 emenda.

| 39 | **a ordem líquida** | o III-a do 38 com C e \|R₃\| descontados do piso do acaso de cada um (disco 0,257; andar 3 0,088, medido com K = 0); cortada (max(0, ·)) e sem corte; 5.000 Myr, 100 sementes | descontar o piso impede a autoconsistência de criar ordem? com o piso certo, ela apara até a faixa ou acha um ponto próprio acima do caos? | J1/J2: memória vazia ≤ 0,31; J3: ≥ 80 na faixa (sem corte, 0,8 K_c); J4: medianas a ≤ 0,05 entre os K e ≥ 0,40 | 35 · 85 · 10 · 10 % | vazia: g ao teto em 64–73 Myr nos dois sabores (o disco nasce coerente: o braço mede preservação, não criação); cortada semeada: teto em ≈ 3,3 Gyr (viés +0,057), C ≈ 0,9; sem corte semeada: teto em 58–62 % das sementes, C̄ 0,43–0,53 subindo | **J1–J4 reprovados** | o ponto fixo da autoconsistência é instável do lado da ordem: o disco responde mais rápido que a memória e devolve mais ordem do que recebe; a regra é um amplificador, e sai da lista das que aparam |

Placar: 39 testes numerados (o 25 sem resultado), mais o teste do ato A; 39: J1–J4 reprovados; 58 defeitos nesta numeração, 1 emenda.

| 40 | **40-A: os ramos de equilíbrio do disco** (análise pedida pelo colaborador) | disco de 12 anéis do 37, sem memória e sem controlador; equilíbrios travados pela autoconsistência de Kuramoto; jacobiano no referencial girante; média de C no tempo abaixo do travamento (K/K_c 0,50–1,60, coerente e sorteado, com e sem ruído) | 0,627 é um equilíbrio? o ramo travado é estável? a faixa da NGC 628 pede ajuste fino? há histerese? | J1: C_L ≥ 0,70; J2: ramo estável e selas instáveis; J3: janela < 0,10 K_c; J4: diferença coerente − sorteado > 0,2 | 80 · 95 · 60 · 50 % | K_L = 1,115 K_c, C_L = 0,808 (sela-nó; abaixo, nenhum equilíbrio); **todo estado travado tem C ≥ 0,791**, com qualquer acoplamento a uma fase comum; faixa só como regime em movimento em 0,96–1,03 K_c (0,08 K_c; 0,11 com ruído); relaxação ≈ 380 Myr perto do limiar; histerese máx 0,15 | **J1, J2, J3 passaram; J4 reprovou** | neste disco não há equilíbrio intermediário a estabilizar: o limite de 0,79 é geométrico; o que resta a um controlador é segurar um regime numa janela de 8 % de K_c, onde o disco responde em centenas de Myr |

Placar: 40 testes numerados (o 25 sem resultado), mais o teste do ato A; 40: J1–J3 passaram, J4 reprovou; 58 defeitos nesta numeração, 1 emenda.

| 41 | **41-B/C/D: o atlas dos regimes em movimento** | disco de 12 anéis sem memória nem controlador; 20 Gyr, 21 condições iniciais, K/K_c 0,90–1,12 (passo 0,005); frequência efetiva de cada anel, aglomerado travado, maior expoente de Lyapunov; janela em N = 8, 12, 16, 24 | a média persiste? é sincronização parcial? é caos de fase? um só atrator? a janela estreita com N? | J1: deriva ≤ 0,02 em ≥ 80 %; J2: aglomerado ≥ 6 e ≥ 1 escorregando em ≥ 80 %; J3: λ > 5×10⁻⁴ em ≥ 50 %; J4: espalhamento ≤ 0,03 em ≥ 80 %; J5: largura estritamente decrescente | 70 · 55 · 55 · 70 · 55 % | janela 0,970–1,035 K_c; 0,990–1,035: 10 travados + 2 internos escorregando, λ ≈ 0, C̄ 0,68–0,72, independente do início; 0,970–0,985: 7–9 + 3–5, caótico, espalhamento 0,03–0,08; **C̄ = 0,627 em 0,975 K_c, na borda caótica**; larguras 0,105 · 0,075 · 0,065 · 0,065 | **J1, J2 passaram; J3, J4, J5 reprovaram** | a faixa da NGC 628 é um regime persistente de sincronização parcial (anéis internos escorregando); a janela tem ≈ 6–7 % de K_c e não estreita além de N = 16; 0,627 fica na fronteira entre o regime caótico e o regular |

Placar: 41 testes numerados (o 25 sem resultado), mais o teste do ato A; 41: J1, J2 passaram, J3–J5 reprovaram; 58 defeitos nesta numeração, 1 emenda.

| 42 | **42-A: a memória das interações e a largura da janela** (forma do colaborador) | mapa do 41 com θ ← θ + Δω + K[(1 − α)S + αq], q ← q + (S − q)/τ; malha α {0,25…1} × τ {30…1.000 Myr}, seleção em 10 condições, julgamento em outras 10; escala N = 16, 24; controle com frequências uniformes (N = 12–48) | a memória sem alvo alarga a janela da faixa ≥ 1,5 ×, de forma robusta, em escala, mantendo sincronização parcial? a janela uniforme estreita com N? | J1: α = 0 reproduz o 41; J2: ≥ 1,5 ×; J3: espalhamento ≤ 0,03 em ≥ 80 %; J4: ≥ 1,5 × em N 16 e 24; J5: parcial em ≥ 80 %; J6: uniforme estritamente decrescente | 95 · 45 · 65 · 40 · 60 · 70 % | célula α 0,75, τ 100; seleção 0,110 → validação **0,080 vs 0,060 (1,33 ×)**; janela sobe para 1,03–1,125, patamar C ≈ 0,68–0,69, K_L > 1,2; borda de baixo caótica (10/16) e multiestável; N 16 e 24: razões 0,64 e 0,73; **uniforme: janela ≈ 0 já em N = 12**, K_L → K_c | **J1, J5 passaram; J2, J3, J4, J6 reprovaram** | a memória das interações alarga pouco, só em disco pequeno, e acrescenta caos; a janela de sincronização parcial vem da forma da distribuição de frequências (Ω ∝ 1/r), não de N: o Caminho B tem alvo na curva de rotação |

Placar: 42 testes numerados (o 25 sem resultado), mais o teste do ato A; 42: J1, J5 passaram, J2, J3, J4, J6 reprovaram; 60 defeitos nesta numeração, 1 emenda.

| 43 | **43-0: o sinal do m = 5 sobrevive ao feixe?** (auditoria do preprint) | THINGS NGC 628 MOM1 NA e RO; pipeline do preprint sem mudança; passo 1 reprodução; passo 2 anéis da largura do feixe (0,42 kpc NA, 11 anéis), bootstrap por blocos de 12″, 300 mapas de ruído convolvidos com o feixe, coerência de todos os modos | a amplitude e a coerência de fase do m = 5 resistem à correlação do feixe? a coerência é própria do m = 5? | J1: Z ≥ 3; J2: IC por blocos acima do baseline; J3: ⟨A₅⟩ > q99 do ruído; J4: C_φ,5 > q95 do ruído; J5: C_φ,5 o maior de n = 3–10 | 75 · 90 · 90 · 70 · 40 % | reprodução: A₅ e C_φ batem, Z (5,06 contra 4,10), RO e vazamento (−0,68 contra +0,165) não; feixe: ⟨A₅⟩ 1,51, IC [1,43; 1,61], ruído q99 0,38, Z 3,96; C_φ,5 0,628 contra q95 0,640; modos 10, 2, 6 e 4 mais coerentes | **J1, J2, J3 passaram; J4, J5 reprovaram** | a amplitude do m = 5 é real; a coerência de fase (o 0,627 usado nos testes 37–42 e na nota de síntese) não se distingue do ruído do feixe e não é própria do m = 5; o preprint precisa de versão 2 |

Placar: 43 testes numerados (o 25 sem resultado), mais o teste do ato A; 43: J1–J3 passaram, J4, J5 reprovaram; 61 defeitos nesta numeração, 1 emenda.
