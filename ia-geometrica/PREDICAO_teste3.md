# Predição do teste 3 (salto sobre deriva)

18/10/2026 · escrita antes de rodar · instrumento v0.py (c79df9a) · testes 1 e 2 reprovados (LEITURA_teste1.md, LEITURA_teste2.md)

## Pergunta

A lição do cubo foi: medir a surpresa contra uma régua fixa, não contra o próprio passado. A mente de março media E_norm = (T − EMA_T)/EMA_T e, depois de um salto, declarava calma enquanto ainda estava longe do mundo. **O regime na régua detecta um salto do mundo antes e com menos falsos alarmes do que o regime relativo de março, sobre a mesma tensão?**

## Mundo

`mundo_salto(φ = 0,9, d = 2, média entre saltos 200 passos, amplitude uniforme ±8 por coordenada)`, N = 10.000 passos, 100 sementes (1000–1099). Janela [0, 2.000) calibra a régua (com os saltos que lá caírem, como a régua de maio incluiu as caudas de maio); medida em [2.000, 10.000). Em média ≈ 40 saltos por semente na medida.

## Instrumento

- Observador olhando sempre, k = 4, λ₁ = 0,15, b = 10. A tensão julgada é T₀ = ‖x_t − R₁,t−1‖, a mesma para os dois detectores.
- Detector régua: T₀ lido na régua (mediana, q99,5 ÷ 3 da calibração); ruptura ≥ 3, histerese de 3 passos (`v0.regime`).
- Detector relativo (nulo): E = (T₀ − EMA_{0,08})/EMA; ruptura se E > 0,15, estável se E < −0,12, histerese 3 (`v0.regime_relativo`, a mente de março).
- Salto detectado: o detector entra em ruptura em algum t ∈ [s, s + 20] (W = 20); atraso = t − s; só a primeira entrada conta. Falso alarme: uma entrada em ruptura fora de todas as janelas [s, s + 20]. Taxa por 1.000 passos. Detecção: fração dos saltos detectados.
- Por semente: Δatraso = mediana(atraso relativo) − mediana(atraso régua); ΔFA = FA relativo − FA régua; Δdet = det régua − det relativo.

## Critério (um julgamento)

Passa se, nas 100 sementes: (a) o envelope de ΔFA está inteiro acima de zero; (b) o envelope de Δatraso está inteiro em ≥ 0 e a sua mediana entre sementes é > 0; (c) Δdet ≥ 0 em ≥ 95 sementes. Os três.

## Apostas

- Passar: **70 %** (mantida do projeto). O relativo dispara com qualquer variação de 15 % da tensão, e num AR(1) isso acontece o tempo todo: muitos falsos alarmes. No atraso os dois devem ser próximos (histerese 3 em ambos), por isso (b) pede ≥ 0 e não > 0 por semente; é a parte com mais risco de empate (aposto 75 % em (b)).
- Falsos alarmes do relativo acima de 20 por 1.000 passos (60 %); da régua abaixo de 2 por 1.000 (60 %).
- Detecção da régua ≥ 0,95 (80 %).

## O que fecha

Reprovar: a lição do cubo (régua, não passado) não generaliza para fora do BTC, e a v0 perde a sua justificativa para herdar a régua de maio. Passar: a régua fixa é uma propriedade do observador que vale fora do mercado; um dos três compromissos da v0 fica de pé.
