# Predição do teste 52 (o erro contra o mundo: cada relógio de andar aprende o ritmo que lhe chega, e o andar do ano guarda o ano quando a v0 deixa de olhar?)

21/10/2026 · escrita antes de simular no dado real · mesmo campo, lugares e relógios do teste 51 · Ana Rigel

## De onde vem

No teste 51, os relógios acoplados entre si, aprendendo com o próprio erro (ω ← ω + η(Δφ − ω)), convergiram para um consenso de ≈ 157 dias. Era a média das frequências próprias deles: persistente no silêncio, igual no mundo sem estações e surdo ao ano. No teste 36, o erro era medido contra o mundo e a v0 aprendeu o mundo. A Ana pediu para continuar pelas duas saídas que a leitura apontou: medir o erro contra o mundo e desacoplar os relógios.

**As duas saídas são a mesma regra quando os relógios estão desacoplados.** Com K = 0, o passo realizado é Δφ_j = ω_j − ε s_j sen φ_j. A regra do teste 51 vira então

  ω_j ← ω_j − (ηε) s_j sen φ_j,

que é a regra dos osciladores de frequência adaptativa: a frequência só muda pelo torque que o mundo exerce. O que falhou no teste 51 foi o acoplamento, não a regra. Este teste usa a **regra do mundo** (o torque da forçante, η_w = ε/365):
- **braço A:** relógios desacoplados (K = 0), onde ela coincide com a do teste 51;
- **braço B:** relógios acoplados (K = 0,1), onde ela difere, porque o acoplamento passa a mover a fase sem ensinar a frequência.

## O modelo

Tudo como no teste 51: campo, cascata da v0 intacta, s_j, frequências naturais ω_j(0) = λ_j, ε = 0,01, 20 fases iniciais (semente 51), silêncio (s = 0) a partir de 1/1/2018, nulo sem estações. A diferença está só na atualização da frequência, a cada dia:

  φ_j ← φ_j + ω_j − ε s_j sen φ_j + K · Im(Z e^{−iφ_j}),  ω_j ← ω_j − η_w s_j sen φ_j (com a fase do início do passo),  η_w = ε/365.

## A teoria (sem simular)

**Um relógio forçado, com frequência adaptativa.**
- Travado, sen(atraso) = (ω − Ω)/F com F = εA/2. Então dω/dt ≈ −(η_w/ε)(ω − Ω): converge ao ano com constante de tempo ε/η_w = **365 dias**.
- O andar 2 trava (|λ₂ − Ω| = 0,0022 < F₂ = 0,0044) e deve aprender o ano em 1–2 anos.
- **Os outros andares estão fora do alcance do ano.** Para quem desliza, o torque médio é ≈ η_w·(A/2)/(2x), com x = (ω − Ω)/F:
  - andar 1 (x ≈ 20): 0,1 % do caminho em 8 anos;
  - andares 3 e 4 (x ≈ −41 e −4.000): nada.

  Cada andar guarda o seu ritmo. É a cegueira declarada da v0, agora em forma de ritmo: o andar 3 não ouve o ano, então não o aprende.
- **No silêncio,** sem forçante e sem acoplamento, cada relógio gira na frequência aprendida. O andar 2 guarda o ano; sem aprendizado, volta aos 419 dias.
- **No nulo,** o andar 2 só recebe torque de ruído e anda à toa perto de 419 dias.

**Conferência numa simulação curta antes dos critérios** (a falta do teste 51, defeito 71). Num **mundo sintético** com o ano de cada andar (A_j e δ_j de Juara na calibração) mais ruído AR(1) com o desvio do resíduo real, 20 inícios, medianas:

| braço | condição | ω_j/Ω ao fim de 2017 (andares 1–4) | período no silêncio, andar 2 |
|---|---|---|---|
| A, K = 0 | com ano | 8,57 · **0,978** · 0,119 · 0,005 | **373,6 d** |
| A, K = 0, η = 0 | com ano | 8,72 · 0,872 · 0,087 · 0,009 | 418,9 d |
| A, K = 0 | sem ano | 8,66 · 0,811 · 0,082 · 0,009 | 450,6 d |
| B, K = 0,1 | com ano | 8,44 · 1,236 · 0,010 · 0,008 | 353,7 d |
| B, K = 0,1 | sem ano | 8,72 · 0,877 · 0,079 · 0,009 | 406,3 d |

**Leituras do sintético:**
- No braço A, o andar 2 aprende o ano a 2 % e o guarda no silêncio a 2,3 %. O andar 3 é puxado 37 % acima da própria frequência, mas fica a 88 % de distância do ano; os andares 1 e 4 não se movem para o ano.
- No braço B, o aglomerado acoplado gira a 354 dias no silêncio (−3 %), mas as frequências individuais ficam espalhadas (o andar 2 em 1,24 Ω). Ele chega perto do ano sem que nenhum relógio o tenha aprendido sozinho, e é frágil (com K = 0,02, 407 e 1.560 dias).

## Critérios (dado real, 6 lugares; um lugar conta se a mediana dos 20 inícios satisfaz)

**J1, o andar 2 aprende o ano (A).** ω₂ ao fim de 2017 a ≤ **5 %** de Ω, em **≥ 5 de 6** lugares.

**J2, cada um dos outros guarda o seu ritmo (A).** ω₁, ω₃ e ω₄ ao fim de 2017 a mais de **50 %** de Ω, em **≥ 5 de 6** lugares.

**J3, o ano sobrevive ao silêncio (A).** Período realizado do andar 2 em 2018–2025:
- com aprendizado: a ≤ **5 %** de 365,25 dias, em ≥ 5 de 6;
- sem aprendizado: a mais de 5 % de 365,25 dias, em ≥ 5 de 6.

**J4, o ano vem do mundo (A, nulo; só conta se o J1 passar — correção do defeito 72).** No mundo sem estações, ω₂ ao fim de 2017 a mais de **10 %** de Ω, em ≥ 5 de 6.

**J5, o acoplamento com a regra do mundo (B).** Período do aglomerado (andar 2) no silêncio a ≤ **5 %** de 365,25 dias, **e** no nulo a mais de 10 %, em **≥ 5 de 6** lugares.

Relatado: todas as frequências aprendidas e realizadas; o tempo até o andar 2 entrar em ±5 % de Ω; a deriva no silêncio em dias por ano contra o calendário.

## Apostas (Claude, antes de simular no dado real)

- **J1: 75 %.**
- **J2: 80 %.** O andar 3 já se moveu 37 % no sintético; no real, com variação entre anos, pode se mover mais.
- **J3: 70 %.**
- **J4: 85 %.**
- **J5: 35 %.** Frágil no sintético.

## O que fecha

- **J1–J4 passam:** a v0 com um relógio por andar, aprendendo com o erro medido contra o mundo, aprende o ritmo do mundo **só no andar cuja escala o contém** e o guarda quando para de olhar. Os outros andares guardam as próprias escalas. A organização então é por andar, não por consenso, e a escada da v0 sobrevive. Junto com o teste 51: o que decide se ela aprende o mundo ou a si mesma é contra o que o erro é medido.
- **J1 passa e J3 reprova:** ela segue o ano enquanto olha, mas não o guarda; aprender a frequência não bastou para virar memória.
- **J1 reprova:** no dado real, o ano não chega ao andar 2 com força suficiente para ser aprendido em 8 anos.
- **J5:** diz se acoplar os andares, com o erro contra o mundo, ainda serve ou só atrapalha.

Um julgamento por hipótese; sem emenda. Instrumento: teste52.py, escrito depois do commit desta predição. O piloto sintético está em teste52.py (função `piloto`) e é rerrodado e relatado junto.
