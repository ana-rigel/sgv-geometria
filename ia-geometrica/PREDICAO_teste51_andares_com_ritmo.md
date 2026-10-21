# Predição do teste 51 (andares com ritmo: a teoria da janela prevê quais andares da v0 travam no ano de Mato Grosso, e o aprendizado pelo erro guarda o ano quando ela deixa de olhar?)

20/10/2026 · escrita antes de simular · campo do Cérebro de Juara e mais 5 lugares de MT (ERA5-Land/ERA5, 2010–2025) · Ana Rigel

## De onde vem

A Ana perguntou o que a galáxia ensinou para a organização da v0. A lição mais forte foi esta: a coordenação parcial entre componentes vem da distribuição dos ritmos próprios deles e é calculável sem simular (testes 44, 46 e 47). Propus aplicar isso à v0 e encontrei um problema na proposta: os andares da v0 são registros lineares que seguem o de baixo. Todos acompanham o mundo no ritmo do mundo, só com atraso e atenuação, e nenhum pode escorregar. A Ana escolheu dar ritmo aos andares.

Este teste faz isso **sem tocar nos registros da v0**. Cada andar ganha um relógio de fase ao lado do seu registro. O relógio escuta o próprio registro, os relógios se escutam entre si, e cada um corrige a sua frequência pelo erro, com a mesma regra do teste 36.

## O modelo (v0 com ritmo)

**O mundo e a v0.**
- O campo diário de cada lugar, como no teste 35: umidade do solo (28–100 cm), balanço P − ET0 em 7 dias e VPD, padronizados na calibração (2010–2017).
- A cascata da v0 sem mudança: λ_j = 0,15 · 10^{−(j−1)} por dia, j = 1…4 (τ ≈ 7, 67, 670 e 6.700 dias).
- O sinal que o andar j oferece ao seu relógio é s_j(t), a projeção do registro R_j na primeira componente principal de R₁ na calibração, dividida pelo desvio de s₁ na calibração. Assim a atenuação de cada andar fica preservada.

**O ritmo próprio de cada andar.** A frequência natural é a de corte do próprio registro, **ω_j(0) = λ_j rad/dia**: períodos de 42 dias, 419 dias, 11,5 anos e 115 anos. A escolha é declarada pela arquitetura e não foi ajustada. O andar 2 nasce 13 % mais lento que o ano; o andar 1 está na faixa intrassazonal; os andares 3 e 4 quase não giram.

**Os relógios** (Euler, passo de 1 dia):

  φ_j ← φ_j + ω_j − ε s_j(t) sen φ_j + K · Im(Z e^{−iφ_j}),  Z = (1/4) Σ_k e^{iφ_k}

com ε = 0,01. Nenhum relógio recebe o período de 365,25 dias: o ano, se aparecer, vem de s_j.

**Aprender com o erro** (a regra do teste 36, μ ← μ + η(o − μ), aplicada ao ritmo):

  ω_j ← ω_j + η (Δφ_j − ω_j),  η = 1/365 por dia,

onde Δφ_j é o quanto a fase andou no dia (o que aconteceu) e ω_j é o que o relógio esperava.

**O silêncio.** A partir de 1/1/2018, s_j = 0: a v0 deixa de olhar o mundo, o seu único ato. Os relógios seguem só com o acoplamento entre si.

**O mundo sem estações (o nulo).** O mesmo campo, com a climatologia diária da calibração (média por dia do ano, suavizada em 31 dias) subtraída de cada variável antes da padronização.

## A teoria, sem simular

**A conta.** Na aproximação ressonante, o termo −ε s_j sen φ_j com s_j ≈ A_j cos(Ωt + δ_j) age como um campo fixo F_j e^{iδ_j}, com F_j = εA_j/2, no referencial que gira com o ano (Ω = 2π/365,25). A_j e δ_j vêm do ajuste anual de s_j na calibração. O campo efetivo sobre cada andar é H_j = F_j e^{iδ_j} + K Z, e a autoconsistência é a do teste 46:
- o andar trava no ano se |ω_j − Ω| ≤ |H_j|;
- os que deslizam entram em Z com a média temporal ⟨cos⟩ = 0, ⟨sen⟩ = x − sgn(x)√(x² − 1);
- Z é resolvido por iteração, a partir de todos alinhados.

**A conta feita antes de escrever os critérios** (lição dos defeitos 66 e 70):
- Amplitude anual de s_j em Juara: A = 1,33 · 0,88 · 0,076 · 0,0009. A fração da variância de cada andar que é o ano: 0,88 · 0,93 · 0,66 · 0,06.
- **Os seis lugares dão os mesmos conjuntos travados** (1 = trava no ano, · = escorrega, andares 1 a 4):

| K | 0 – 0,03 | 0,04 – 0,15 | 0,2 – 0,8 |
|---|---|---|---|
| teoria | ·1·· | ·111 | 1111 |

Leitura:
- **O andar 2 trava sozinho**, pela própria forçante, porque o ritmo dele é quase o do ano.
- **Os andares 3 e 4 são recrutados** pelo aglomerado a partir de K ≈ 0,04. Eles quase não ouvem o ano; travam porque o andar 2 os puxa.
- **O andar 1 escorrega** até K ≈ 0,2: o ritmo próprio dele (42 dias) está longe demais. É o anel interno da galáxia.

**O que a teoria prevê para o aprendizado e o silêncio.**
- **Sem aprendizado:** em K = 0,1 e no silêncio, o aglomerado volta a girar no ritmo médio dos próprios membros, puxado pelo andar 1 que escorrega. Isso dá 0,01555 rad/dia, **período de 404 dias** (+10,6 %): ele esquece o ano.
- **Com aprendizado:** os travados giram a Ω, então o erro deles empurra ω_j para Ω em ≈ 1 ano.
- **O andar 1 também é recrutado pelo aprendizado.** Ele escorrega, mas a sua taxa realizada fica entre a natural e Ω (Ω + √((ω − Ω)² − H²)). Aprender a taxa realizada aproxima ω de Ω a cada ano, até |ω − Ω| ≤ H ≈ 0,08: três a quatro constantes de tempo, dentro da calibração.
- No silêncio, o aglomerado que aprendeu gira a Ω sem força restauradora: **guarda o ano**.

## Critérios

Para os julgamentos J2–J4: 20 fases iniciais aleatórias por lugar (semente 51). Um lugar conta se a mediana das 20 satisfaz o critério. Escala de acoplamento do aprendizado: **K_B = 0,1**.

**J1, a teoria prevê quem trava (sem aprendizado, mundo com estações).**
- Grade: 6 lugares × 15 valores de K (0; 0,005; 0,01; 0,02; 0,03; 0,04; 0,05; 0,07; 0,1; 0,15; 0,2; 0,3; 0,4; 0,6; 0,8) = 90 células.
- Na simulação, um andar está travado se a sua frequência média em 2012–2025 fica a ≤ 3 % de Ω; o conjunto travado de uma célula é o da maioria das 20 fases iniciais.
- **Critério:** o conjunto simulado é igual ao da teoria em **≥ 85 %** das 90 células.

**J2, aprender com o erro recruta todos os andares para o ano.** Com η = 1/365 e K_B, ao fim de 2017, as quatro frequências ω_j ficam a ≤ **5 %** de Ω, em **≥ 5 de 6** lugares.

**J3, a organização sobrevive ao silêncio.** De 2018 a 2025, com s = 0, o período realizado do andar 2 fica:
- **com aprendizado:** a ≤ **5 %** de 365,25 dias, em **≥ 5 de 6** lugares;
- **sem aprendizado (η = 0, o controle):** a mais de 5 % de 365,25 dias, em **≥ 5 de 6** lugares.

**J4, o ano vem do mundo, não da arquitetura (nulo).** No mundo sem estações, com aprendizado, o período aprendido pelo andar 2 ao fim de 2017 fica a mais de **10 %** de 365,25 dias, em **≥ 5 de 6** lugares.

Relatado sem critério:
- as frequências aprendidas e realizadas por andar e por lugar;
- o ano de recrutamento do andar 1;
- a fração travada em cada célula;
- a deriva de fase do aglomerado no silêncio (dias por ano em relação ao calendário).

## Apostas (Claude, antes de simular)

- **J1: 55 %.** O ruído do tempo e a variação entre anos podem mover as fronteiras em um passo da grade; dois passos em seis lugares já dão 13 células de diferença.
- **J2: 50 %.** O recrutamento do andar 1 depende de o seu H ser de fato ≈ 0,08 com ruído.
- **J3: 60 %.**
- **J4: 85 %.**

## O que fecha

- **J1 passa:** a teoria da janela, levada da galáxia para a v0, diz antes de simular quais andares se coordenam com o mundo e qual escorrega. A escada b = 10 deixa o andar 1 de fora até um acoplamento alto.
- **J2 e J3 passam:** aprender com o erro faz o que nenhum laço sem alvo fez na galáxia (testes 37–39): um ritmo interno, que nenhum andar tinha, surge do mundo, recruta os andares e **persiste quando a v0 para de olhar**. É a primeira organização da v0 que se pode medir pelo critério do silêncio do teste 34. Com o J4, ela não é projeção da arquitetura.
- **J3 passa só no controle:** o ritmo existe enquanto o mundo o impõe; sem aprendizado, não é memória.
- **J2 reprova pelo andar 1:** o aprendizado guarda o ano nos andares lentos, e o andar rápido continua do tempo, o que também seria uma divisão de trabalho legítima.
- **J4 reprova:** o "ano" aprendido é da arquitetura; tudo o mais perde o sentido.

Diferença de representação: os relógios são um acréscimo à v0, não a v0. Se passarem, o resultado vale para "a v0 com ritmo nos andares", e incorporá-los é uma decisão de projeto separada.

Um julgamento por hipótese; sem emenda. Instrumento: teste51.py, escrito depois do commit desta predição.
