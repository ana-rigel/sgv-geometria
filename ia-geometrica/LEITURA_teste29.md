# Leitura do teste 29 (a declaração no sítio) — J1 e J2 REPROVADOS; "subiu nas últimas 6 h" diz mais que a declaração

**Predição:** PREDICAO_teste29_declaracao_no_sitio.md (af5e37a), antes de rodar. **Instrumento:** teste29.py, mesmo commit. **Resultado:** resultados_teste29.json. Dois julgamentos; sem emenda.

| célula (L, C) | cheias | perdidas pelo N3 | AUC declaração v0 (IC 95 %) | AUC subida em L h | AUC fração da subida em L h | declaração média: perdidas / protegidas |
|---|---|---|---|---|---|---|
| **(6, 3), julgada** | 1.867 | 398 | **0,657** (0,634–0,684) | **0,802** | 0,709 | 0,82 / 0,76 |
| (3, 3) | 1.867 | 343 | 0,805 (0,777–0,831) | 0,863 | 0,856 | 0,85 / 0,76 |
| (1, 1) | 1.867 | 241 | 0,637 (0,597–0,678) | 0,721 | 0,822 | 0,80 / 0,77 |

Permutação: quantil 95 % ≈ 0,53 nas três células.

**J1, a declaração separa perdidas de protegidas:** AUC 0,657, acima do acaso com folga, mas abaixo do 0,70 exigido. **Reprovado.**
**J2, a declaração diz mais que "subiu rápido":** a subida nas últimas 6 h tem AUC 0,802; a declaração fica **0,145 abaixo** (IC −0,182 a −0,109). **Reprovado**, com folga.

Apostas: J1 passa (60 %), errada; J2 reprova (85 %), certa, mas a faixa apostada (−0,05 a +0,03) errou feio; declaração média maior nas perdidas (80 %), certa (0,82 contra 0,76); (1, 1) abaixo de (6, 3) (65 %), certa (0,637 contra 0,657).

## O que o resultado diz

A declaração aponta para o lado certo: as cheias perdidas têm declaração maior que as protegidas, nas três células, e a separação está muito acima do acaso. Mas ela está **comprimida**: perdidas 0,82, protegidas 0,76. Quase tudo parece "rápido demais" para o andar 1, e a diferença que importa fica num intervalo estreito.

A razão está na janela, e é um defeito já conhecido. A janela de 48 h tem 49 pontos; a banda mais lenta que ela consegue representar tem período de 49 h, e nessa banda o andar 1 (τ ≈ 7 h, corte em ≈ 42 h de período) já deixa passar só 62 % da potência. **Todas as bandas da janela estão perto ou acima do corte do andar 1**, então toda janela declara cegueira alta. É o defeito 12 de novo ("série menor que o período do andar"): a declaração foi feita para séries muito mais longas que o andar, e aqui eu a apliquei numa janela que tem a mesma escala dele.

Enquanto isso, a medida comum mais tola, quanto o córrego subiu nas últimas 6 horas, separa perdidas de protegidas com AUC 0,80. Ela mede exatamente o que o ato precisa saber (o que aconteceu dentro do tempo do ato), sem espectro e sem janela.

## O que os quatro testes do sítio dizem juntos (26–29)

1. **O sítio cobra, e a resposta é de engenharia** (26, 28): um ato automático e barato com uma regra simples resolve quase tudo.
2. **Como alarme, a v0 não acrescentou nada** (26, 27, 28): empatou onde o problema era difícil e perdeu onde ficou fácil.
3. **Como declaração, ela aponta certo mas fraco** (29), e uma medida simples aponta melhor. A declaração que passou nos testes 16–17 vale para séries longas, onde a pergunta é "que fração deste mundo eu não represento"; para uma cheia, a pergunta é "isto aconteceu dentro do tempo do ato?", e para essa a resposta direta (a subida em L horas) é melhor.

Isso não apaga o que ficou de pé no OBS-01: a régua mede o corte de um observador desconhecido em séries longas. Mas, no sítio, com estes sensores e estes atos, **a v0 não tem função que uma regra simples não cumpra melhor.** O que o sítio pede, pelo que estes testes mostram, é um ato automático, barato e rápido, uma regra simples de chuva e nível e, para o relatório de cada cheia perdida, a frase "subiu tanto em tantas horas".

## Para a lista de defeitos de desenho

40. Declaração aplicada a uma janela da mesma escala do andar (48 h contra τ ≈ 7 h e corte em ≈ 42 h): todas as bandas ficam perto do corte, e a declaração se comprime em 0,76–0,82. É o defeito 12 reaparecendo; a regra dos testes 9 e 16 só discrimina com séries muitas vezes mais longas que o período de corte do andar.

Placar: 29 testes numerados (o 25 sem resultado). 26: J1 passou, J2 reprovou; 27: ambos reprovaram; 28: J1 passou, J2 reprovou; 29: ambos reprovaram. 40 defeitos, 1 emenda.
