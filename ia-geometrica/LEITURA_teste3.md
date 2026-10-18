# Leitura do teste 3 (salto sobre deriva) — REPROVADO

**Predição:** PREDICAO_teste3.md (eb76003), antes de rodar. **Resultado:** resultados_teste3.json. Um julgamento; sem emenda.

| detector | atraso mediano | falsos alarmes / 1.000 passos | detecção (saltos vistos em ≤ 20 passos) |
|---|---|---|---|
| régua (v0) | 2,07 | **0,009** | **0,20** |
| relativo (março) | 2,00 | **33,1** | **0,66** |

Critério: (a) envelope de ΔFA acima de zero: **sim** (29,6 a 37,1); (b) Δatraso ≥ 0 em todas e mediana > 0: **não** (envelope −4 a 0, mediana 0: empate); (c) Δdetecção ≥ 0 em ≥ 95 sementes: **não** (em 0 sementes). **Reprovado.** Apostas: 70 % em passar, errada; 75 % em (b), errada; FA do relativo > 20 (certa); FA da régua < 2 (certa); detecção da régua ≥ 0,95 (errada, e por muito).

## O que o resultado diz

Os dois detectores erram de maneiras opostas, e o critério pedia que a régua ganhasse nas duas.

O relativo é o que a mente de março era: dispara a cada 30 passos em média, porque 15 % de variação da tensão acontece o tempo todo num AR(1). A sua "detecção" de 66 % é em boa parte sorte: um detector que entra em ruptura ao acaso a 33 por 1.000 passos cai dentro de uma janela de 20 passos depois do salto com probabilidade 1 − e^{−0,66} ≈ 0,48 sem olhar o salto. O critério (c) não descontou isso: defeito de critério, registrado.

A régua é silenciosa e precisa, mas cega aos saltos médios. A razão está na calibração: a janela [0, 2.000) contém ≈ 10 saltos, e o quantil 99,5 de |T₀ − mediana| é definido por eles. Ruptura ≥ 3 na régua exige T₀ ≥ mediana + q99,5, isto é, um salto do tamanho dos maiores saltos da calibração. Com amplitude uniforme ±8 por coordenada, a maioria dos saltos é menor do que isso e muitos (módulo < 3) nem se distinguem do ruído de um mundo cujo desvio estacionário é 2,3 por coordenada. A régua de maio tem o mesmo desenho e a mesma propriedade: ela mede surpresa **em relação às caudas que já viu**, e não vê o que é menor que elas. No BTC isso era o que queríamos (a borda como objeto raro); aqui é o que faz perder.

O atraso empatou em 2 (o mínimo com histerese 3), como a predição temia.

## O que fecha e o que não

- Fecha: sobre esta tensão, com esta régua e este critério, o regime na régua não é um detector de saltos melhor que o relativo; é um detector **diferente**: quase sem falso alarme, quase sem sensibilidade. A lição do cubo não generalizou na forma "detecta antes e melhor"; generalizou na forma "não grita à toa", que é só metade.
- Não fecha: se uma régua calibrada **sem** os saltos (ou com a mediana e a escala robusta do corpo, MAD em vez de q99,5) detectaria os saltos médios mantendo o silêncio. Isso é um instrumento diferente e um teste diferente.

## Para a lista de defeitos de desenho do projeto

6. Régua calibrada numa janela com saltos: a escala vira o tamanho dos saltos, e o detector só vê o que é maior que eles. A régua de maio tem o mesmo desenho; no BTC é uma escolha, aqui foi um erro.
7. Mundo com saltos de amplitude uniforme desde zero: metade dos "saltos" é menor que o ruído estacionário e não é salto para nenhum observador.
8. Critério de detecção sem desconto pelo acaso: um detector que dispara ao acaso ganha detecção de graça.

Três testes, três reprovações, oito defeitos nomeados. O teste 4 segue conforme o projeto.
