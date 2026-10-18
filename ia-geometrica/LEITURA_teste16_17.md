# Leitura dos testes 16 (o andar da identidade) e 17 (a declaração composta) — 16 PASSOU, 17 PASSOU

**Predições:** PREDICAO_teste16_17_identidade_e_composta.md (877fb9c), antes de rodar. **Resultado:** resultados_teste16_17.json. Dois julgamentos; sem emenda. São as duas primeiras passagens do projeto, em dezessete julgamentos, e as duas estão dentro do escopo em que foram escritas: mundos sintéticos, instrumento fixo (k = 4, λ₁ = 0,15, b = 10), olhar sempre, 100 sementes.

## O que a v0 declara e o que é verdade (médias por mundo; andares 1–4)

| mundo | δ̂ simples (entrada, ganho real) | β real (mundo) |
|---|---|---|
| lento-a (τ 20.000, σ_b 0,3) | 0,10 · 0,01 · 0,04 · 0,31 | 0,08 · 0,11 · 0,15 · 0,45 |
| lento-b (τ 50.000, σ_b 0,3) | 0,13 · 0,02 · 0,03 · 0,23 | 0,11 · 0,15 · 0,17 · 0,36 |
| lento-c (τ 100.000, σ_b 1,0) | 0,65 · 0,17 · 0,04 · 0,21 | 0,56 · 0,71 · 0,72 · 0,76 |
| escada-3 | 0,19 · 0,38 · 0,60 · 0,85 | 0,16 · 0,55 · 0,86 · 1,01 |
| cíclico | 0,03 · 0,66 · 1,00 · 1,00 | 0,03 · 0,77 · 1,07 · 1,00 |

## Teste 16

| andar | ρ (δ̂ simples, β), 500 pares | envelope de permutação | |δ̂ − β| mediano |
|---|---|---|---|
| 1 | +0,999 | −0,17 a +0,15 | 0,020 |
| 2 | +0,847 | −0,17 a +0,14 | 0,133 |
| 3 | +0,879 | −0,12 a +0,16 | 0,146 |
| **4** | **+0,746** | −0,14 a +0,15 | 0,150 |

Critério (ρ₄ ≥ 0,7 e acima do envelope): **passa.** Aposta 65 %, certa. Com três mundos em cinco mais lentos que a identidade, e com valores distintos de β₄ entre eles (0,36 a 0,76), a declaração do andar 4 acompanha a ordem da cegueira real. O erro no valor (0,15) é o mesmo dos andares 2 e 3: é o efeito da entrada contra o mundo que o teste 17 trata.

## Teste 17

| andar | |δ̂ composta − β| mediano | (simples) | viés mediano | ρ (composta, β) |
|---|---|---|---|---|
| 1 | 0,020 | 0,020 | +0,020 | +0,999 |
| 2 | **0,007** | 0,133 | −0,007 | +0,967 |
| 3 | **0,006** | 0,146 | −0,005 | +0,976 |
| 4 (relatado) | 0,023 | 0,150 | −0,007 | +0,913 |

Critério (erro mediano ≤ 0,05 nos andares 1–3): **passa.** Aposta 45 %, errada para o lado bom; "erro entre 0,05 e 0,10 nos andares 2 e 3", errada: deu 0,007 e 0,006. A composição por produto, que eu chamei de aproximação, é quase exata aqui: o viés mediano é de meio centésimo. E no andar 4, sem critério, a composta leva ρ de 0,75 para 0,91 e o erro de 0,15 para 0,02.

A razão de a aproximação ser tão boa, vista depois: a cascata de registros é uma cascata de filtros, e a fração do mundo que o andar j não representa é 1 − Π|H_i|² integrado sobre o espectro; compor as frações **declaradas** (cada uma já integrada sobre a entrada do andar, que é o mundo filtrado pelos anteriores) reproduz essa integral exatamente, porque a entrada do andar j já carrega os ganhos dos andares 1 … j−1. Não é coincidência; é a definição certa, e eu a tinha chamado de aproximação por cautela.

## O que fecha

- A v0 tem, nos quatro andares, uma declaração de cegueira **verdadeira na ordem** (ρ 0,999 · 0,847 · 0,879 · 0,746 na simples; 0,999 · 0,967 · 0,976 · 0,913 na composta) e **certa no valor** (erro mediano ≤ 0,023 em todos os andares na composta), em cinco mundos sintéticos com espectros de uma, duas, três e quatro escalas e com algo mais lento que a identidade. É a régua de cegueira que o OBS-01 pediu, no sintético, com a sua regra completa e testada: **espectro da entrada do registro, pesado por (1 − ganho real do registro), em série mais longa que o registro, composta por produto andar a andar.**
- O que não fecha, e vale dizer no mesmo parágrafo: isto é a v0 declarando a cegueira **de si mesma**, com ganhos que ela conhece. O OBS-01 quer a cegueira de um observador cujos ganhos ninguém conhece (um modelo de IA). O passo seguinte é o instrumento como régua **sobre outro observador**: a v0 recebe a saída de um registro desconhecido e estima a cegueira dele; isso é um teste novo, com predição própria, e é o primeiro que sai do sintético puro.

## Para a lista de defeitos de desenho do projeto

28. A composta foi registrada como "aproximação declarada" quando é a definição exata para a cascata; a cautela custou um teste a mais. Fica como lição de método, não como defeito do instrumento.

Dezessete testes, quinze reprovações, **duas passagens**, vinte e oito defeitos. A linha da declaração está de pé com número.
