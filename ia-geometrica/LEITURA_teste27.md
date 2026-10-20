# Leitura do teste 27 (a chuva como segundo sensor) — J1 e J2 REPROVADOS; o gargalo é o preço do ato, não o sensor

**Predição:** PREDICAO_teste27_chuva.md (5190643), antes de rodar. **Instrumento:** teste27.py e sitio.py (pluviômetro, episódios, teto da chuva), mesmo commit. **Resultado:** resultados_teste27.json. Dois julgamentos; sem emenda.

| anos 3–4, soma de 100 sementes | custo | fração do teto da chuva |
|---|---|---|
| nunca chamar | 186.700 | 0 |
| N2, só córrego (teste 26) | 181.910 | 7,7 % |
| **N3, alarme de chuva e nível** | 182.590 | 6,6 % |
| **v0 com dois sensores** | 180.970 | 9,3 % |
| v0 crua | 187.430 | −1,2 % |
| teto da chuva (sabe qual chuva vira cheia) | 124.770 | 100 % |
| oráculo | 17.970 | — |

**J1, a chuva compra antecedência:** N3 **0,4 % mais cara** que N2; mais barata em 37 sementes. **Reprovado.**
**J2, a v0 vê o que o alarme de dois sensores não vê:** v0 **0,9 % mais barata** que N3; mais barata em 56 (5 empates). Abaixo dos 10 % e das 60 sementes. **Reprovado.**

Apostas: J1 passa (45 %), errada; N3 com menos da metade do teto da chuva (80 %), certa (6,6 %); N3 escolhe a forma E na maioria (55 %), errada (OU em 67); J2 reprova (85 %), certa, e a v0 caiu na faixa apostada (+0,9 %, dentro de −8 a +5 %); v0 crua pior que N3 (85 %), certa.

## O que o resultado diz

O pluviômetro **tem** antecedência para vender: quem soubesse qual chuva vira cheia ficaria 33 % abaixo de "nunca" (o teto da chuva nas sementes do teste). Nenhuma política real comprou mais que um décimo disso, com ou sem v0. A antecedência existe; o que falta é saber, no começo da chuva, qual chuva é.

Uma conta do mundo, feita depois do julgamento e sem política nenhuma, mostra a razão inteira:

- cada semente tem **76 episódios de chuva por ano**;
- **13,6 %** deles viram cheia;
- só **5,2 %** viram cheia que ainda dá para proteger (a cheia chega ≥ 6 h depois de a chuva começar).

Chamar custa 10 e a cheia custa 100: uma chamada só se paga se mais de **10 %** das chamadas forem para uma cheia protegível. Chamar a cada chuva acerta 5,2 %, metade do necessário. Para valer a pena, o sinal do início da chuva teria de **dobrar a precisão** — distinguir, na primeira hora, a chuva que vira cheia da que não vira. Nem a intensidade da chuva, nem o nível do córrego, nem o vinco fazem isso o bastante. A v0 ficou um pouco à frente (9,3 % contra 6,6 % do teto), mas um pouco não é o que o critério pediu.

Esta conta poderia ter sido feita antes. É o defeito 37 uma segunda vez: calculei o teto (o que se ganha sabendo tudo), mas não o **ponto de equilíbrio** (a precisão mínima que um sinal precisa ter para o ato se pagar).

## O que isso significa para o sítio

O sítio cobra (teste 26), mas, com um ato que custa um décimo da perda e leva 6 h, **nenhum sensor local faz o ato se pagar**: nem o córrego, nem a chuva, nem a v0 lendo os dois. O gargalo não é ver; é o **preço e a demora do ato**. Há duas alavancas, e as duas mudam a conta acima, não a IA:

1. **Um ato mais rápido** (comporta ou bomba acionada à distância, L de 1–2 h): mais cheias ficam protegíveis, e a precisão de que o sinal precisa cai.
2. **Um ato mais barato** (automático, sem viagem: C de 10 para 1–2): o ponto de equilíbrio desce de 10 % para 1–2 %, e então até "chamar a cada chuva forte" passa a valer.

Uma terceira, de fora: **previsão meteorológica**, que avisa antes de a chuva começar. Ela não é sensor do sítio; é o oráculo parcial que o mundo vende.

A v0, nos testes 26 e 27, fez o que um alarme bem afinado faz, nem mais nem menos. Se ela tem algo de próprio no sítio, deve estar onde esteve em todos os testes: na **declaração** (dizer, em cada cheia perdida, que ela veio mais rápido do que o sensor e o ato conseguem ver), não no alarme.

## Para a lista de defeitos de desenho

38. Ponto de equilíbrio do ato não calculado antes: com C/D = 0,1, um sinal só se paga com precisão > 10 % sobre cheias protegíveis, e a taxa-base no início da chuva é 5,2 %. A conta, de uma linha, previa a reprovação de J1. Regra para os próximos testes do sítio: calcular antes **o teto, o teto causal e o ponto de equilíbrio**.

Placar: 27 testes numerados (o 25 sem resultado). No 26, J1 passou e J2 reprovou; no 27, J1 e J2 reprovaram. 38 defeitos, 1 emenda.
