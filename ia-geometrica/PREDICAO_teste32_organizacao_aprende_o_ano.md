# Predição do teste 32 (a organização aprende o ano)

20/10/2026 · escrita antes de rodar · instrumento v0.py sem mudança nos andares · Ana Rigel

## De onde vem

Da conversa de 20/10 sobre o terceiro corpo. Na v0, o campo ∘ e a memória □ estão construídos; a organização ⋄ não. Nada na v0 aprende: os andares seguem o mundo e a régua é calibrada uma vez. No Teste B (17/10) a organização guardava uma **posição**, e o diagnóstico daquele dia foi que ela deveria guardar **regularidade**. O experimento do relógio, que tentou isso, reprovou com um defeito de instrumento, e a ideia ficou sem teste.

O teste 31 mostrou onde está a regularidade do sítio: em Mato Grosso, o ano domina os andares 1 e 2 (fração anual de 0,57 a 0,90) e some no 3. A leitura do 31 terminou recomendando alimentar a placa com o desvio do normal de cada época. O teste 30 já fez isso, mas com uma **climatologia fixa** de 365 dias, tirada de 8 anos de reanálise baixados de fora (2010–2017). Uma placa instalada hoje no sítio não tem esses 8 anos.

**Pergunta.** Uma organização que aprende o ano sozinha, on-line, sem história de fora e com poucos números, entrega à memória um desvio do normal tão útil quanto o índice padrão que precisa de 8 anos de clima baixados?

## A organização ⋄ (a peça nova)

Para cada grandeza de entrada, a organização mantém o ciclo do ano como cinco coeficientes sobre a base φ(t) = [1, sen ωt, cos ωt, sen 2ωt, cos 2ωt], com ω = 2π/365,25 por dia. Ela aprende por **mínimos quadrados recursivos sem esquecimento**: cada dia pesa 1/n, de modo que um ano seco nunca vira "normal" além do seu peso no total. Ela começa **fria** (coeficientes zero; matriz inicial 10³·I).

A cada dia, a organização **prevê antes de olhar**: u_t = x_t − φ(t)·β_{t−1}. Só depois atualiza β com x_t. A memória recebe u_t. A organização ocupa 20 números por grandeza (5 coeficientes e os 15 da matriz simétrica 5×5). A climatologia fixa do teste 30 ocupa 365 médias e foi calculada com 2.922 dias de fora.

Os andares da v0 não mudam: λ₁ = 0,15, b = 10, passo de 1 dia (τ ≈ 7 d, 67 d, 1,8 ano, 18 anos), começando em zero.

## Dados, verdade e lugares

- **Dados:** ERA5-Land e ERA5 via Open-Meteo, diários. Juara: era5land_juara_horario.csv.gz. Os cinco de MT: clima/dados/lugares (Sinop, Cuiabá, Barra do Garças, Alta Floresta, Rondonópolis).
- **Verdade (a mesma do teste 30):** anomalia padronizada da umidade de 28–100 cm por dia do ano, com média e desvio de 2010–2017 suavizados em 31 dias. Dia de seca profunda: anomalia ≤ −1.
- **Entrada:** chuva − ET0 do dia, a mesma do teste 30.
- **Julgamento** nos cinco lugares de MT. Neles nunca se calculou uma AUC de seca: o teste 31 olhou só a fração anual. **Juara** é relatada sem julgar, porque o teste 30 já usou os seus dados.

## As séries comparadas (todas lidas no andar 2, R2, sem escolha nova)

O R2 foi a leitura que a calibração do teste 30 escolheu. Fixá-lo aqui evita uma bifurcação de escolhas.

| nome | o que é | história de fora |
|---|---|---|
| **v0+⋄ fria** | organização e memória começando do zero em 01/01/2018 (a placa instalada naquele dia) | nenhuma |
| v0 crua fria | memória sem organização, sobre chuva − ET0 bruta, começando em 01/01/2018 | nenhuma |
| **SPEI-90** (nulo) | soma de 90 dias da anomalia de chuva − ET0, padronizada por dia do ano; climatologia de 2010–2017 | 8 anos |
| v0 clim. fixa | a v0 do teste 30 (anomalia pela climatologia de 2010–2017) | 8 anos |
| v0+⋄ morna | organização e memória começando em 01/01/2010 | nenhuma, mas com 8 anos de experiência própria |

**Medida:** 2019–2025 (2.557 dias). O ano de 2018 é o aquecimento da placa fria. AUC diária com escore = −série, positivo = dia de seca profunda. Intervalos por bootstrap em blocos de 90 dias (1.000 reamostras, semente 32).

## Conta prévia (lição dos defeitos 41 e 42)

- **Sem organização, o ano domina o R2.** O ganho da cascata no período de 365 dias é ≈ 0,99 no andar 1 e ≈ 0,66 no andar 2, então cerca de dois terços da amplitude anual de chuva − ET0 chegam ao R2. A v0 crua deve ler a estação, não a seca. O J1 é quase mecânico, e a aposta reflete isso.
- **O J2 não é mecânico.** Depois de um ano, o erro de cada coeficiente da organização é da ordem de σ·√(2/365) ≈ 0,07σ, onde σ é o desvio diário de chuva − ET0. A flutuação genuína do R2 é da ordem de σ/√133 ≈ 0,09σ, porque o R2 tem ≈ 133 dias efetivos. Os dois são parecidos. Além disso, o ano de 2018 tem a sua própria anomalia, que a organização vai tomar como normal no começo. O erro cai com √n ao longo de 2019–2025. A AUC não muda com um deslocamento constante, mas muda com um deslocamento que **anda no tempo**, e o da organização anda enquanto ela aprende.

## Critérios (dois julgamentos)

**J1, a organização é o que faz a placa ler seca:** AUC(v0+⋄ fria) − AUC(v0 crua fria) **≥ 0,05** em **≥ 4 dos 5** lugares de MT.

**J2, a placa sem história empata com o índice que precisa de 8 anos** (o critério da Ana para a placa, de 20/10: não ser melhor, rodar gastando menos e off-line): AUC(v0+⋄ fria) − AUC(SPEI-90) **≥ −0,03** em **≥ 4 dos 5** lugares de MT.

Relatado sem julgamento: Juara; v0 clim. fixa; v0+⋄ morna; a diferença por ano entre v0+⋄ fria e SPEI-90 (para ver se a placa melhora ao aprender); a fração anual dos andares 1 e 2 com e sem organização (a ponte com o teste 31).

## Apostas (Claude, antes de rodar)

- **J1 passa: 90 %.** Pela conta prévia.
- **J2 passa: 50 %.** Contra: o primeiro ano é um ano só, e a verdade é medida contra a climatologia de 2010–2017, a mesma que o SPEI usa. A favor: a AUC só pune o deslocamento que muda no tempo, e esse encolhe com √n.
- **A diferença v0+⋄ fria − SPEI-90 é pior em 2019 do que em 2023–2025 em ≥ 4 de 5 lugares: 60 %.** É a assinatura de que a organização aprende.
- **v0+⋄ morna fica a ±0,02 da v0 clim. fixa em ≥ 4 de 5 lugares: 75 %.** Com 8 anos, os cinco coeficientes devem fazer o que fazem as 365 médias.

## O que fecha

- **J1 e J2 passam:** a organização ⋄ é o primeiro corpo da v0 que aprende alguma coisa, o ano do lugar, e isso basta para uma placa sem história ler a seca profunda como o índice público. Na placa, a peça cabe em 20 números por sensor.
- **J1 passa, J2 reprova:** a organização é necessária mas aprende devagar. A leitura por ano dirá em quanto tempo ela chega ao índice, e esse tempo vira o requisito de instalação (por exemplo, "a placa só declara seca depois do ano N").
- **J1 reprova:** a conta prévia estava errada, e o ano não atrapalha o R2 como se pensava. Isso pede leitura antes de qualquer outro passo.

Isto ainda não é o laço de consequência (aprender com o erro de um ato). É o degrau anterior: aprender o ritmo do mundo.
