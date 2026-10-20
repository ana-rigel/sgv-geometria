# Predição do teste 31 (onde a samambaia quebra)

20/10/2026 · escrita antes de baixar os dados dos lugares · Ana Rigel

## De onde vem

Da página "Cérebro de Juara" e de uma exploração feita sobre ela, em Juara, 2010–2025, depois do teste 30: a v0 (λ₁ = 0,15, b = 10, um passo por dia; τ ≈ 7 d, 67 d, 1,8 ano, 18 anos) lendo três grandezas padronizadas (água no solo 28–100 cm, chuva − ET0 em média de 7 dias, VPD). A fração do movimento de cada andar explicada pelo ciclo anual foi, por componente: andar 1 0,76–0,85; andar 2 0,87–0,90; **andar 3 0,16–0,34**; andar 4 ≈ 0. A estação mora entre os andares 2 e 3: o ano (365 d) cai no vão entre τ = 67 d e τ = 667 d.

Isso foi visto, não testado. **Juara fica fora do julgamento.** A hipótese é a frase do projeto de 17/10: *onde o mundo tem uma escala própria, a samambaia fica cega, e a cegueira tem lugar marcado*; o lugar marcado é onde a fração anual cai.

## O que não é trivial

A posição do vão é aritmética de filtro: um registro de 1ª ordem com τ = 667 d deixa passar ≈ 9 % da amplitude anual, e o andar 3 recebe ≈ 6 % depois da cascata. Se o andar 3 é ou não dominado pelo ano depende do **mundo**: de quanta variação entre anos (clima) existe comparada a esses 6 % da estação. Um lugar com estação forte e anos parecidos pode ter o andar 3 ainda anual; um lugar com estação fraca pode ter até o andar 2 não anual.

## Os lugares (fixados aqui, antes de qualquer download)

Cinco em Mato Grosso, o mesmo regime de Juara (réplica): **Sinop, Cuiabá, Barra do Garças, Alta Floresta, Rondonópolis**. Cinco de contraste: **Porto Alegre e Curitiba** (subtropical, chuva distribuída no ano), **Petrolina** (semiárido, anos muito diferentes entre si), **Manaus e Belém** (equatorial). Coordenadas no script baixar_lugares.py. Dados: ERA5-Land (solo, VPD) e ERA5 (chuva, ET0) via Open-Meteo, 2010–2025, agregados por dia.

## Medida

Para cada lugar, o mesmo instrumento da página: padronização pela calibração 2010–2017; andares começando no normal (0); **fração anual** de cada andar = 1 − variância residual / variância, somadas nas três componentes, após ajustar o 1º e o 2º harmônicos do ano, em 2012–2025 (dois anos de aquecimento fora). **Quebra:** o primeiro par de andares (j, j+1) com fração ≥ 0,5 em j e < 0,5 em j+1; "antes do andar 1" se o andar 1 já está abaixo de 0,5; "sem quebra" se nenhum andar cair.

## Critérios (dois julgamentos)

**J1, a quebra de Juara se repete em Mato Grosso:** quebra entre os andares 2 e 3 em **≥ 4 dos 5** lugares de MT.

**J2, a quebra muda de lugar onde o mundo muda:** em **Porto Alegre e Curitiba**, a fração anual do **andar 2** fica **abaixo de 0,5** (a estação não domina nem a escala de dois meses).

Relatado sem julgamento: Petrolina, Manaus, Belém; a fração anual do próprio campo.

## Apostas (Claude, antes do download)

- **J1 passa: 80 %.** Todo o MT tem a mesma alternância de águas e seca, forte e regular.
- **J2 passa: 30 %.** Contra: o VPD acompanha a temperatura, e o inverno do Sul é marcado; o ano pode dominar o andar 2 pelo ar mesmo com a chuva distribuída. A favor: o solo e o balanço no Sul têm pouca estação.
- Manaus e Belém: quebra entre 1 e 2 ou antes do andar 1 em pelo menos um dos dois (55 %).
- Petrolina: andar 3 com a menor fração anual dos dez (50 %), pelos anos de seca e de chuva muito diferentes.

## O que fecha

- **J1 passa:** a quebra entre 2 e 3 é a assinatura do clima de MT na escada da v0; para uma placa em MT, os andares 1–2 leem a estação e o 3 é o primeiro a ler o clima (o que recomenda alimentar a placa com desvios do normal, item 3 dos insights).
- **J2 passa:** a quebra se move com o mundo; o lugar dela mede a escala dominante de cada clima, como a frase do projeto dizia.
- **J1 reprova:** a quebra de Juara era do ponto, não do regime; volta a ser só observação.
