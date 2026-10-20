# Predição do teste 27 (o mundo sítio com a chuva como segundo sensor)

19/10/2026 · escrita antes de rodar · Ana Rigel · corrige a causa lida no teste 26 (o córrego avisa tarde), e só ela

## Pergunta

No teste 26 o sítio cobrou (teto de 90 %), mas nenhuma política que só olha o córrego passou de 1 % dele: do primeiro sinal no córrego até a cheia sobram 3–4 h, e o ato leva 6. **Um pluviômetro compra a antecedência que o córrego não dá? E, com os dois sensores, a v0 vê o que um alarme comum de chuva e nível não vê?**

## O que é igual ao teste 26

O mundo (sitio.py, `mundo_sitio` sem mudança), as sementes 1000–1099, os 4 anos (1–2 régua e afinação; 3–4 medida), a cheia a 1,2 m, C = 10, D = 100, L = 6 h, P = 48 h, o refratário de 48 h. Os custos de N2, da v0 só-córrego, de "nunca" e do oráculo são lidos de resultados_teste26.json, porque o mundo é o mesmo.

## O que muda: o pluviômetro

A chuva de cada hora, arredondada a 0,2 mm (báscula; sem sorteio, para o mundo ficar idêntico ao do 26).

## O teto da chuva, calculado antes (defeito 37)

Limite de quem vê cada chuva começar **e sabe, no início, se aquela chuva vai virar cheia**: chama no início de cada episódio que precede uma cheia. Não é política; é o máximo que o pluviômetro permite com 6 h de ato. Nas sementes de desenho 5000–5009 (fora do teste), anos 3–4:

| | custo | abaixo de "nunca" |
|---|---|---|
| nunca | 17.400 | — |
| **teto da chuva** | 10.400 | **40,2 %** (perde 85 de 174 cheias: as que vêm menos de 6 h depois de a chuva começar) |
| oráculo | 1.670 | 90,4 % |

Então, mesmo sabendo qual chuva vira cheia, o pluviômetro alcança menos da metade do que o oráculo alcança. Uma política real não sabe qual chuva vira cheia e fica abaixo disso.

## As políticas (afinadas nos anos 1–2, medidas nos anos 3–4)

Cada família escolhe, na afinação, entre duas formas: **OU** (A ≥ a ou B ≥ b) e **E** (A ≥ a e B ≥ b); ±∞ desliga uma leitura.

| | A | B | grade |
|---|---|---|---|
| **N3, alarme comum de chuva e nível** | chuva nas últimas 3 h (1…40 mm) | nível lido (0,60…1,40 m) | 41 × 42 × 2 formas |
| **v0 com dois sensores** | surpresa da chuva na régua (uma v0 sobre o pluviômetro, 0,25…8) | vinco do córrego na régua (a v0 do teste 26, −2…8) | 33 × 42 × 2 formas |
| v0 crua (relatada) | surpresa da chuva ≥ 3 | ou vinco ≥ 3 | nenhuma afinação |
| N2 do teste 26 (só córrego) | nível ou subida | | relida |

A forma **E** é onde a v0 poderia mostrar algo próprio: a cheia é chuva forte **sobre base alta**, e o vinco é exatamente "o quanto o córrego está acima da própria identidade". Mas N3 tem o mesmo recurso com o nível absoluto.

## Critérios (dois julgamentos)

**J1, a chuva compra antecedência:** custo total de N3 **≥ 10 % menor** que o de N2 (só córrego) e N3 mais barata em **≥ 60 sementes**.

**J2, a v0 vê o que o alarme comum de dois sensores não vê:** custo total da v0 com dois sensores **≥ 10 % menor** que o de N3 e mais barata em **≥ 60 sementes**.

Relatado: fração do teto da chuva que cada política captura, (nunca − política) / (nunca − teto da chuva); formas escolhidas; v0 crua; perdas e chamadas.

## Apostas (Claude, antes de rodar)

- **J1 passa: 45 %.** O teto da chuva está 40 % abaixo de "nunca"; N2 ficou 2,6 % abaixo. Se N3 capturar um quarto a um terço do teto da chuva, fica 8–14 % abaixo de N2, em cima da linha. O que pesa contra: na chuvosa começa uma chuva a cada ≈ 2 dias, e sem saber qual vira cheia o alarme paga muitas viagens.
- **N3 captura menos da metade do teto da chuva: 80 %.**
- **N3 escolhe a forma E na maioria das sementes: 55 %.** Chuva forte sozinha chama demais; chuva com córrego já alto separa melhor.
- **J2 passa: 15 %.** O vinco é nível relativo e N3 lê nível absoluto, e a cheia é absoluta. Espero a v0 entre −8 % e +5 % de N3.
- **v0 crua pior que N3: 85 %.**

## O que fecha

- **J1 passa, J2 reprova:** a chuva compra antecedência, como a leitura do 26 disse; a v0 continua sendo um alarme como os outros. O teste seguinte é o ato mais rápido (L de 1–2 h) ou a declaração das cheias perdidas.
- **J1 reprova:** nem a chuva basta com um ato de 6 h, porque não se sabe no início qual chuva vira cheia; o que o sítio pede é um ato mais rápido ou previsão de chuva de fora (meteorologia), não mais sensores locais.
- **J2 passa:** a combinação de surpresa da chuva com vinco do córrego vê algo que chuva e nível absolutos não dão; o teste seguinte isola qual leitura ganhou.
