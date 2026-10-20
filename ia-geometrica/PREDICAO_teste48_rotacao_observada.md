# Predição do teste 48 (investigação 3: a janela com a rotação observada da NGC 628 e a inclinação variando dentro das incertezas)

20/10/2026 · escrita antes de calcular · teoria contínua do teste 47 · dados: Aniyan et al. (2018), MNRAS 476, 1909, Figura 13 · Ana Rigel

## De onde vem

Da terceira investigação proposta pela Ana em 20/10: introduzir curvas de rotação compatíveis com os dados da NGC 628, variando a inclinação radial dentro das incertezas, e ver quais regimes ficam possíveis. Os testes 46 e 47 mostraram que a janela de sincronização parcial é calculável a partir da distribuição de frequências, sem integrar; o teste 47 deu a lei largura ≈ 0,056 (2 − β)^1,6 K_c para curvas em lei de potência. A Ana anexou o artigo de Aniyan et al.; a Figura 13 (anéis inclinados sobre os dados do THINGS) está no PDF como gráfico vetorial, e os pontos foram extraídos exatamente (ngc628/aniyan2018_fig13.json): PA, inclinação com barra de erro e velocidade de rotação (lados que se aproxima e que se afasta, e a média) a cada 5″, até 350″.

## Os dados na zona

A zona estável vai de 254″ a 395″, mas os dados de Aniyan et al. vão só até 350″. O teste usa **254″–350″** (≈ 9,0–12,4 kpc a 7,3 Mpc), com 20 pontos. A curva publicada foi derivada com a inclinação **fixa** em 8,5°. Valores na zona: PA de 25,5° a 9,3°; inclinação entre 5,4° e 12,0°, erros de 0,5° a 1,6°; velocidade de 190 a 182 km/s.

## O cálculo

Trabalhando em segundos de arco (a forma não depende da distância):

- **Inclinação fixa (como publicado):** v(r) = a média dos dois lados, interpolada em 1.000 anéis uniformes de 254″ a 350″; Ω = v/r.
- **Inclinação variando (300 realizações, semente 48):** em cada realização, cada ponto de inclinação recebe um sorteio N(0, erro do ponto) e se ajusta uma reta i(r) por mínimos quadrados ponderados; cada ponto de velocidade recebe N(0, σ_v), com σ_v = metade da diferença entre os dois lados (o erro adotado pelos autores). Daí v_verdadeira(r) = v(r) · sen 8,5° / sen i(r).
- **Para cada curva:** a teoria contínua do teste 47 dá o começo da janela, o fim (K_L), a largura (em K/K_c) e, no meio da janela, o lado travado (rígido) e o lado que desliza. Também o β de um ajuste em lei de potência, para comparar com a lei do teste 47.

O giro de PA não entra: ele muda a fase do m = 1, não a amplitude da rotação, e a frequência de cada anel depende só de v/r.

## Conta prévia (só dos dados de entrada, antes de calcular janelas)

- Com a inclinação fixa, v cai ≈ 4 % de 255″ a 350″: β ≈ ln(182/190)/ln(350/255) ≈ −0,14. Pela lei do teste 47, largura ≈ 0,056 · 2,14^1,6 ≈ **0,19 K_c**.
- A inclinação parece subir para fora (de ~6° em 260–300″ para ~9° em 300–350″). Com δ ln Ω ≈ −cot i · δi, uma subida de ~3° na zona daria β ≈ −0,14 − 0,8 ≈ −0,9 e largura ≈ 0,30 K_c. A incerteza de uma reta em 20 pontos com erros de ~1° é ≈ 0,8° na zona, ou seja, ≈ 0,2 em β.
- Para qualquer curva monótona que cai ou é plana, o lado rígido é o externo (o das frequências mais densas). Uma curva medida com ondulações pode inverter isso localmente.

## Critérios

**J1, a curva publicada segue a lei:** com a inclinação fixa, o β ajustado fica em [−0,3; 0], e a largura calculada diretamente fica a ≤ **0,02 K_c** da lei 0,056 (2 − β)^1,6.

**J2, a inclinação variando alarga a janela:** a largura com i(r) é maior que a da inclinação fixa em **≥ 84 %** das realizações.

**J3, os dados não fixam a janela:** a razão entre os quantis 84 % e 16 % da largura nas realizações é **≥ 1,5**.

**J4, o lado rígido é o externo:** no meio da janela, a borda externa (350″) está travada e a interna (254″) desliza em **≥ 95 %** das realizações.

Relatado: o β e a largura da inclinação fixa; as distribuições de β, largura, começo, K_L e r\* nas realizações; a inclinação ajustada nas pontas da zona.

## Apostas (Claude, antes de calcular)

- **J1: 75 %.** A curva real não é uma lei de potência exata.
- **J2: 70 %.**
- **J3: 50 %.**
- **J4: 90 %.**

## O que fecha

- **J2 passa:** o warp de inclinação medido por Aniyan et al. alarga a janela da NGC 628 em relação à curva publicada com inclinação fixa; a sincronização parcial, no modelo, fica mais fácil, não mais difícil.
- **J3 passa:** com os dados atuais, a largura da janela da NGC 628 não é determinada; o modelo dá uma faixa, e o insumo que falta é uma medida melhor da inclinação na zona (o fator limitante é o de 1° a 8,5°).
- **J4 passa:** a geometria prevista é a do teste 47 (rígido por fora, deslizando por dentro), e o confronto com as velocidades de padrão de Speights et al. (2025), que segundo o colaborador indicam o oposto, fica como o teste decisivo seguinte.

Um julgamento por hipótese; sem emenda. Instrumento: teste48.py, escrito depois do commit desta predição.
