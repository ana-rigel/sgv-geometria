# Leitura do teste 31 (onde a samambaia quebra) — J1 PASSOU (5 de 5); J2 REPROVADO por Porto Alegre (0,52)

**Predição:** PREDICAO_teste31_quebra_da_samambaia.md (5c766df), antes do download. **Dados:** clima/dados/lugares (run 39411823766; 5.844 dias completos em cada lugar). **Instrumento:** teste31.py. **Resultado:** resultados_teste31.json. Dois julgamentos; sem emenda.

| lugar | campo | andar 1 | andar 2 | andar 3 | andar 4 | quebra |
|---|---|---|---|---|---|---|
| Sinop | 0,72 | 0,82 | 0,87 | 0,19 | 0,00 | entre 2 e 3 |
| Cuiabá | 0,49 | 0,60 | 0,57 | 0,03 | 0,00 | entre 2 e 3 |
| Barra do Garças | 0,58 | 0,70 | 0,82 | 0,14 | 0,00 | entre 2 e 3 |
| Alta Floresta | 0,75 | 0,84 | 0,90 | 0,28 | 0,00 | entre 2 e 3 |
| Rondonópolis | 0,55 | 0,68 | 0,72 | 0,05 | 0,00 | entre 2 e 3 |
| Porto Alegre | 0,33 | 0,46 | **0,52** | 0,04 | 0,00 | antes do andar 1* |
| Curitiba | 0,05 | 0,09 | **0,15** | 0,01 | 0,00 | antes do andar 1 |
| Petrolina | 0,16 | 0,22 | 0,20 | 0,01 | 0,00 | antes do andar 1 |
| Manaus | 0,49 | 0,60 | 0,59 | 0,05 | 0,00 | entre 2 e 3 |
| Belém | 0,67 | 0,77 | 0,81 | 0,19 | 0,00 | entre 2 e 3 |

Fração anual = parte do movimento de cada andar explicada pelo ciclo do ano. *Em Porto Alegre o andar 1 fica abaixo de ½ e o andar 2 passa um pouco acima; a regra registrada classifica pelo andar 1.

**J1, a quebra de Juara se repete em Mato Grosso:** entre os andares 2 e 3 nos **5 de 5** lugares. **Passou.**
**J2, no Sul nem o andar 2 é dominado pelo ano:** Curitiba 0,15, sim; **Porto Alegre 0,52**, não. **Reprovado**, por 0,02.

Apostas: J1 passa (80 %), certa; J2 passa (30 %), certa a reprovação, e pela razão escrita (o ar marca o inverno em Porto Alegre); Manaus ou Belém com quebra antes do andar 2 (55 %), errada: os dois quebram entre 2 e 3, como MT; Petrolina com o menor andar 3 (50 %), certa por pouco (0,007 contra 0,009 de Curitiba).

## O que o resultado diz

**A quebra mora onde está a estação forte.** Os cinco lugares de MT, Manaus e Belém têm estação marcada de águas e seca, e em todos o ano domina os andares 1 e 2 e some no 3. Em Curitiba e Petrolina o ano não domina nenhum andar: no primeiro porque a chuva se espalha pelo ano; no segundo porque os anos são muito diferentes entre si. Porto Alegre fica no meio, perto de ½ nos dois andares de baixo.

Então a samambaia quebra **onde o mundo tem a sua escala**, e a quebra muda de lugar quando o mundo muda: em sete lugares com o ano forte, entre 2 e 3; em dois lugares sem ele, antes de qualquer andar. O critério J2 pediu uma coisa mais estreita (o andar 2 do Sul abaixo de ½) e Porto Alegre ficou por 0,02 do outro lado.

**A parte que eu disse não ser trivial era quase trivial.** O andar 3 ficou abaixo de 0,3 em **todos os dez** lugares, inclusive os de estação mais forte. Na predição eu escrevi que o andar 3 poderia continuar anual num lugar de estação forte e anos parecidos; nenhum lugar do Brasil testado chegou perto. Com τ = 667 dias, o andar 3 recebe só ≈ 6 % da amplitude anual, e qualquer variação entre anos o domina. O que de fato distingue os lugares é o lado de baixo da quebra: se o ano domina os andares 1 e 2. A pergunta informativa era "este lugar tem estação forte?", e a escada a responde pelo andar 1–2, não pelo 3.

## O que isso significa para a placa

Para uma placa em qualquer lugar de MT, a leitura fica firme em seis lugares diferentes (Juara e os cinco do teste): **os andares 1 e 2 leem a estação; o andar 3 é o primeiro que lê o clima.** Por isso, alimentar a placa com o desvio do normal de cada época libera os andares 1 e 2 para ler o que interessa (uma semana ou dois meses fora do normal), em vez de reaprender o calendário todo ano. E o andar 3 é o que deve ser olhado para tendências de anos, como a descida de Juara para o lado seco entre 2021 e 2024.

## Para a lista de defeitos de desenho

42. A predição afirmou que o lado de cima da quebra (o andar 3 deixar de ser anual) dependia do mundo, sem calcular antes a fração anual esperada do andar 3 para um ano puro somado a uma variação entre anos realista. A conta (≈ 6 % da amplitude anual passa ao andar 3) mostraria que só um lugar quase sem variação entre anos manteria o andar 3 anual. O J1 continua válido como réplica em MT; a parte informativa estava no andar 1–2.

Placar: 31 testes numerados (o 25 sem resultado). 26: J1 passou, J2 reprovou; 27, 29, 30: ambos reprovaram; 28: J1 passou, J2 reprovou; 31: J1 passou, J2 reprovou. 42 defeitos, 1 emenda.
