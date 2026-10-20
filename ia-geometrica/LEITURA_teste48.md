# Leitura do teste 48 (investigação 3: a rotação observada da NGC 628): J3 e J4 PASSARAM; J1 e J2 REPROVADOS. As ondulações da curva real alargam a janela além da lei; a subida de inclinação de Aniyan et al., tomada ao pé da letra, faria a curva cair mais rápido que a de Kepler, o que um disco em rotação circular não permite

**Predição:** PREDICAO_teste48_rotacao_observada.md (c908b25), antes de calcular. **Instrumento:** teste48.py (e7c84aa). **Resultado:** resultados_teste48.json. **Dados:** Aniyan et al. (2018), Figura 13, extraída dos vetores do PDF (ngc628/aniyan2018_fig13.json); zona 254″–350″ (os dados acabam em 350″). Teoria contínua do teste 47. Quatro julgamentos; sem emenda.

## Inclinação fixa em 8,5° (a curva publicada)

v cai de 190 para 182 km/s, com uma ondulação (179 km/s em 290″, 189 em 305″). β ajustado **−0,067**. Janela calculada diretamente: **0,790–1,049 K_c, largura 0,258**. A lei do teste 47 para esse β dá **0,179**. No meio da janela, os anéis de 263″ para fora estão travados e os internos deslizam.

## Inclinação variando dentro das barras de erro (300 realizações)

| | q16 | mediana | q84 |
|---|---|---|---|
| inclinação ajustada em 254″ | | 6,95° | |
| inclinação ajustada em 350″ | | 10,08° | |
| β da curva corrigida | −1,46 | **−1,21** | −0,94 |
| largura da janela (K/K_c) | 0,243 | **0,321** | 0,404 |
| começo · fim | | 0,757 · 1,081 | |
| r\* no meio da janela | | 263″ | |

| | resultado | critério | |
|---|---|---|---|
| **J1** a curva publicada segue a lei | β −0,067 em [−0,3; 0], mas largura 0,258 contra 0,179 | ≤ 0,02 da lei | **reprovado** |
| **J2** a inclinação variando alarga | 80 % das realizações acima da fixa | ≥ 84 % | **reprovado** (por pouco) |
| **J3** os dados não fixam a janela | q84/q16 = **1,66** | ≥ 1,5 | **passou** |
| **J4** o lado rígido é o externo | **95,7 %** | ≥ 95 % | **passou** |

Apostas: J1 (75 %), errada; J2 (70 %), errada; J3 (50 %), certa; J4 (90 %), certa.

## O que o resultado diz

**1. A forma fina da curva importa, não só a inclinação média.** A curva publicada é quase plana (β = −0,07), mas a janela calculada (0,26 K_c) é 45 % maior que a da lei de potência com o mesmo β. A ondulação de ±5 km/s entre 280″ e 310″ concentra as frequências de vários anéis num intervalo estreito, e a teoria responde a essa concentração. A lei 0,056 (2 − β)^1,6 vale para curvas suaves; para uma curva medida, a janela tem de ser calculada da curva inteira, o que a teoria faz em segundos.

**2. A subida de inclinação de Aniyan et al. não pode ser lida como inclinação pura.** Ajustada às barras de erro, a inclinação sobe de ≈ 7° para ≈ 10° na zona. Se isso fosse só inclinação, a velocidade corrigida cairia como r^−1,2. Nenhum disco em rotação circular cai mais rápido que a lei de Kepler (r^−0,5, toda a massa no centro): r^−1,2 exigiria massa encerrada diminuindo com o raio. Em todas as realizações, β < −0,5. A conclusão é que a variação de inclinação dos anéis inclinados, a 7–10°, está misturada com outra coisa (movimentos não circulares, o próprio warp, a degenerescência entre inclinação e velocidade num disco quase de frente), e foi por isso que os autores fixaram a inclinação em 8,5°. A conta prévia calculou β ≈ −0,9 para a subida de 3° e não percebeu que isso já estava além do limite de Kepler (defeito 64).

**3. O que se pode dizer da NGC 628 no modelo.** As curvas fisicamente admissíveis na zona ficam entre β ≈ −0,5 (o limite de Kepler) e β ≈ 0 (plana, ou a curva publicada com as suas ondulações). Para elas, a janela de sincronização parcial fica entre ≈ 0,18 K_c (lei, curva plana suave) e ≈ 0,26 K_c (curva publicada, com a ondulação), e chegaria a ≈ 0,24 na queda kepleriana suave (lei com β = −0,5). Em todos os casos, como em todas as 300 realizações menos 13, o lado rígido é o externo e quem desliza são os anéis internos da zona.

**4. O fator limitante é a geometria, como o colaborador antecipou.** A janela da NGC 628 não está determinada pelos dados (J3); a dispersão vem quase toda da inclinação, a 1° de incerteza em 8,5°. Uma medida independente da inclinação na zona (por exemplo, da cinemática estelar, ou de um modelo de warp com movimentos não circulares) é o insumo que falta.

## Para a lista de defeitos de desenho

64. A conta prévia transformou a subida de inclinação em β ≈ −0,9 sem checar se esse β é fisicamente admissível. Qualquer β < −0,5 (mais rápido que Kepler) é impossível para rotação circular; o teste deveria ter trazido esse limite como filtro antes, separando as realizações admissíveis das que não são.
65. O J1 supôs que a lei do teste 47, derivada para leis de potência suaves, se aplicaria a uma curva medida com ondulações de ±5 km/s; a conta prévia não estimou o efeito de uma ondulação local na concentração das frequências.

Placar: 48 testes numerados (o 25 sem resultado), mais o teste do ato A. 48: J3, J4 passaram, J1, J2 reprovaram. 65 defeitos nesta numeração, 1 emenda.
