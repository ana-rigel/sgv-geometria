# Leitura do teste 32 (a organização aprende o ano): J1 e J2 REPROVADOS. A organização aprendeu, mas aprendeu a seca como normal

**Predição:** PREDICAO_teste32_organizacao_aprende_o_ano.md (1ad8147), antes de rodar. **Instrumento:** teste32.py. **Resultado:** resultados_teste32.json. Dois julgamentos; sem emenda.

| lugar | dias de seca / 2.557 | v0+⋄ fria | v0 crua fria | SPEI-90 | v0 clim. fixa | v0+⋄ morna | ⋄ fria − SPEI (IC 95 %) |
|---|---|---|---|---|---|---|---|
| Sinop | 917 | 0,602 | 0,679 | 0,700 | 0,615 | 0,590 | −0,099 (−0,170; −0,018) |
| Cuiabá | 1.942 | 0,780 | 0,790 | 0,866 | 0,897 | 0,891 | −0,085 (−0,197; +0,050) |
| Barra do Garças | 1.124 | 0,630 | 0,725 | 0,701 | 0,575 | 0,579 | −0,070 (−0,164; +0,024) |
| Alta Floresta | 721 | 0,674 | 0,525 | 0,693 | 0,697 | 0,673 | −0,019 (−0,083; +0,040) |
| Rondonópolis | 1.906 | 0,842 | 0,831 | 0,846 | 0,779 | 0,827 | −0,004 (−0,083; +0,106) |
| *Juara (relatado)* | 573 | 0,746 | 0,653 | 0,753 | 0,755 | 0,746 | −0,006 (−0,145; +0,096) |

**J1, a organização é o que faz a placa ler seca:** ganho de ≥ 0,05 sobre a v0 crua em **1 de 5** (Alta Floresta +0,15). Em Sinop e Barra do Garças a crua é melhor. **Reprovado.**
**J2, a placa sem história empata com o SPEI-90:** diferença ≥ −0,03 em **2 de 5** (Alta Floresta, Rondonópolis). **Reprovado.**

A parte mecânica funcionou. A fração anual dos andares 1 e 2 caiu de 0,54–0,92 sem a organização para 0,01–0,11 com ela, nos seis lugares. A organização removeu o ano com 20 números, como planejado.

Apostas: J1 passa (90 %), errada; J2 passa (50 %), errada; diferença pior em 2019 do que em 2023–25 em ≥ 4 de 5 (60 %), errada (3 de 5); morna a ±0,02 da clim. fixa em ≥ 4 de 5 (75 %), errada (2 de 5). Quatro apostas, quatro erros.

## O que o resultado diz

**1. A placa foi instalada no começo de uma seca regional e aprendeu a seca como normal.** O período de 2019–2025 foi seco em todo o MT testado. O balanço chuva − ET0 ficou abaixo do normal de 2010–2017 em quase todos os anos, e em Cuiabá e Rondonópolis três em cada quatro dias da medida são "seca profunda" pela verdade. A organização fria, começando em 2018, só conheceu esse clima. Ela aprendeu fielmente o que viu:

| lugar | média de chuva − ET0, 2010–17 | média 2018–25 | aprendida pela ⋄ fria |
|---|---|---|---|
| Sinop | +0,82 | −0,19 | −0,19 |
| Cuiabá | −0,23 | −1,50 | −1,50 |
| Rondonópolis | −0,64 | −1,68 | −1,68 |
| Juara | +0,82 | −0,23 | −0,23 |

(mm/dia). A verdade mede a seca contra o normal de 2010–2017; a organização, contra o normal que ela própria viveu. O "acostumar-se com a seca", risco apontado na conversa de 20/10 antes deste teste, aconteceu por inteiro. Não por esquecimento, porque a organização não esquece, mas porque ela **nunca viu outro clima**. Sem história de fora, uma placa instalada em 2018 não tem como saber que 2018–2025 foi seco. Isso não é um defeito da conta; é um limite do que se pode aprender sozinho num lugar e num tempo.

**2. A v0 crua não lia "nada": lia o calendário, e a verdade premia o calendário.** Num período seco, os dias de seca profunda se concentram em certos meses (setembro a dezembro em Sinop e Barra do Garças, fim da estação seca e começo das águas). Uma série que só repete o calendário, sem nenhum dado do tempo daquele ano, tem AUC de 0,61–0,69 em quatro dos cinco lugares de MT (Sinop 0,626, Cuiabá 0,606, Barra 0,650, Rondonópolis 0,694; Alta Floresta 0,462). A crua carrega o ano no R2 e recebe esse prêmio. A organização remove o ano e o perde. O nulo do J1 não era a "placa sem informação" que a conta prévia supunha.

**3. Onde o clima mudou menos, a organização fez o que se esperava.** Em Alta Floresta (a seca mais branda da medida) ela ganhou 0,15 sobre a crua e ficou a 0,02 do SPEI. Em Juara (relatado) ficou a 0,006 do SPEI e 0,09 acima da crua. Esses são os dois lugares com menos dias de seca e sem prêmio do calendário (AUC do calendário 0,46 e 0,54).

## O que fica para a organização ⋄

A ideia não está refutada, mas este teste a confundiu com outra coisa. O que ele mostra:

- **Aprender o ritmo funciona como peça.** Cinco coeficientes removem o ano dos andares 1 e 2 em seis lugares.
- **Aprender o normal só a partir da própria vida é frágil quando a vida começa numa anomalia.** Uma placa precisa nascer sabendo o clima do lugar e aprender devagar a partir dali. A forma mais barata disso também cabe no desenho: os mesmos 5 coeficientes calculados uma vez da reanálise e gravados na placa como ponto de partida (a v0+⋄ morna é quase isso, com 8 anos de experiência própria). Isso troca "sem história de fora" por "5 números de história de fora", não 2.922 dias.
- **A verdade do teste 30 não serve para julgar uma placa que aprende.** Ela é ancorada em 2010–2017 e premia o calendário num período seco. Um julgamento justo para a organização precisaria de uma verdade sem prêmio de calendário (por exemplo, a AUC dentro de cada mês do ano, somada) ou de um período sem mudança de clima.

## Para a lista de defeitos de desenho

43. A conta prévia tratou o ano como ruído para a tarefa ("a v0 crua deve ler a estação, não a seca"), sem calcular a AUC de uma série que só repete o calendário. Num período mais seco que a calibração, a verdade se concentra em certos meses, e o calendário sozinho vale AUC 0,61–0,69 em quatro dos cinco lugares. O nulo do J1 já tinha esse prêmio.
44. A data de instalação fria (01/01/2018) coincidiu com o começo de uma seca regional de sete anos, e a verdade foi ancorada em 2010–2017. O teste juntou duas perguntas, "a organização aprende o ano?" e "uma placa sem história percebe uma mudança de clima?", e a segunda é impossível por construção. Uma conta prévia simples (o balanço médio de 2018–2025 contra o de 2010–2017, que não exige olhar a verdade) teria mostrado o deslocamento.

Placar: 32 testes numerados (o 25 sem resultado). 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32: ambos reprovaram. 44 defeitos, 1 emenda.
