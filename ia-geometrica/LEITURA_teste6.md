# Leitura do teste 6 (a declaração linear) — A REPROVADO (2 de 4 andares passam), B REPROVADO

**Predição:** PREDICAO_teste6_declaracao_linear.md (6fe28f9), antes de rodar. **Instrumento:** teste6.py (laço reorganizado por semente para caber na memória, sem mudança de definição). **Resultado:** resultados_teste6.json. Dois julgamentos; sem emenda.

## O que a v0 declara agora e o que é verdade

| mundo | δ̂ linear (andares 1–4) | β real (andares 1–4) |
|---|---|---|
| branco | 0,95 · 0,94 · 0,93 · 0,96 | 0,78 · 1,00 · 1,00 · 1,00 |
| deriva | 0,39 · 0,85 · 0,93 · 0,96 | 0,33 · 0,95 · 1,01 · 1,00 |
| escada-3 | 0,20 · 0,39 · 0,64 · 0,91 | 0,17 · 0,56 · 0,88 · 1,01 |
| cíclico | 0,02 · 1,00 · 1,00 · 1,00 | 0,03 · 0,77 · 1,07 · 1,00 |

Compare com o teste 5, onde o andar 1 declarava 0,85–0,95 em todos os mundos: agora declara 0,02 no cíclico e 0,95 no branco, e a verdade é 0,03 e 0,78.

## Hipótese A

| andar | ρ (δ̂, β) | envelope de permutação | erro absoluto mediano | veredito |
|---|---|---|---|---|
| 1 | **+0,993** | −0,15 a +0,17 | 0,042 | sim |
| 2 | +0,404 | −0,13 a +0,18 | 0,136 | não |
| 3 | **+0,870** | −0,13 a +0,22 | 0,076 | sim |
| 4 | −0,108 | −0,20 a +0,14 | 0,037 | não |

**Reprovado** pelo critério (quatro andares). Apostas: 65 % em passar, errada; por andar 75/70/65/50 %: certas em 1, 3 e 4, errada em 2.

Os dois andares que reprovam reprovam por motivos diferentes, e os dois estavam nomeados na predição:

- **Andar 2, corte abrupto contra corte suave.** No cíclico a declaração diz 0,999 (a senoide, em 1/300 = 0,0033, está acima do corte f₂ = 0,0024, logo "não vejo") e a verdade é 0,77: um filtro de primeira ordem com corte em 0,0024 ainda deixa passar um terço da potência em 0,0033. A declaração conta potência acima de uma frequência; a cegueira real pesa cada frequência pelo ganho do filtro. Onde o mundo tem potência perto do corte de um andar, a declaração abrupta erra, e erra para o lado de "mais cega".
- **Andar 4, sem variação para correlacionar.** β₄ é 1,00 em todos os mundos (nenhum tem potência abaixo de f₄ = 2,4 × 10⁻⁵, períodos acima de 42.000 passos) e o erro absoluto é 0,037: a declaração está **certa** no valor e não há ordem a acompanhar. O critério de correlação não cabe num andar em que o mundo não varia; é um defeito do critério (nomeado antes como risco), não da declaração.

## Hipótese B

| destino | sem declaração | com (reescala sem renormalizar) | teto | U > 0 em |
|---|---|---|---|---|
| branco | 1,303 | **1,253** | 1,253 | 100 |
| escada-3 | 1,107 | 2,265 | 1,021 | 0 |
| cíclico | 0,593 | 2,000 | 0,391 | 0 |

**Reprovado.** Apostas: 30 % em passar (certa a não-passagem); por destino 50/35/25 %: certa no branco (agora com 100 de 100 e exatamente o teto), certas as outras duas. Sem renormalização a reescala não explode mais (envelope −270 % contra −3.839 % no teste 5), mas continua a destruir o leitor onde a declaração diz "este andar enxerga pouco" e o peso treinado era negativo: reescalar um peso negativo por uma visibilidade pequena o aproxima de zero, e o leitor perde a correção que esse peso fazia. O teto mostra o mesmo de antes: há muito a ganhar (0,391 contra 0,593 no cíclico), e reescalar peso não é a forma.

## O que fecha e o que não

- Fecha: a regra do teste 5 ("mede-se sobre a entrada, não sobre o erro") é verdadeira e grande: ρ foi de 0,16 para 0,99 no andar 1 e de 0,75 para 0,87 no andar 3 só com essa mudança. Fecha também que a reescala de pesos, com ou sem renormalização, não é um leitor que aproveite a declaração.
- Não fecha: uma declaração que use o **ganho real** do andar, δ̂_j = ∫ S_entrada(f) · (1 − |H_j(f)|²) df / ∫ S_entrada, em vez do corte abrupto. É exata para o filtro que a v0 é, continua calculável só com o que ela tem, e deve consertar o andar 2. Nem fecha o andar 4: precisa de mundos com potência abaixo de f₄ para haver o que correlacionar, isto é, de um mundo com uma componente mais lenta que a identidade.

## Para a lista de defeitos de desenho do projeto

14. Declaração com corte abrupto onde o filtro é de primeira ordem: erra onde o mundo tem potência perto do corte, sempre para "mais cega".
15. Critério de correlação num andar em que a cegueira real não varia entre mundos: indefinido por construção; o andar 4 precisa de um mundo com componente mais lenta que ele.
16. Leitor por reescala de pesos: refutado duas vezes; o próximo leitor escolhe o andar, não reescala o peso.

## Ao OBS-01

Duas regras com número agora: a cegueira se mede sobre a entrada do registro (teste 5 → 6: ρ 0,16 → 0,99), e se declara com o ganho real do registro, não com um corte (andar 2: 0,999 declarado contra 0,77 real). E uma regra sobre o próprio protocolo: para medir a cegueira do registro mais lento de um observador é preciso um mundo que tenha alguma coisa mais lenta que ele; senão a declaração é verdadeira e vazia.
