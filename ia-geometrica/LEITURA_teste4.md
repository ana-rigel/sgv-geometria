# Leitura do teste 4 (escada livre) — REPROVADO

**Predição:** PREDICAO_teste4.md (e8c8cc6), antes de rodar. **Resultado:** resultados_teste4.json. Um julgamento; sem emenda. (A primeira rodada foi interrompida por mim por engano depois dos três mundos-escada; a segunda, idêntica e determinística, é a que fica.)

| mundo | recupera a escada (razões em 7–13) | alguma razão fora | livre ganha da fixa | λ ajustado (médio) | λ_j · τ_j (mediano) |
|---|---|---|---|---|---|
| escada-2 (τ 7, 70) | **1/100** | 99 | 100 | 0,997 · 0,047 | 7,0 · 3,2 |
| escada-3 (τ 7, 70, 700) | **2/100** | 98 | 100 | 0,994 · 0,197 · 0,011 | 7,0 · 3,7 · 2,5 |
| escada-4 (τ 7 … 7000) | **0/100** | 100 | 100 | 0,982 · 0,330 · 0,024 · 0,001 | 7,0 · 4,4 · 4,5 · 0,0 |
| cíclico (período 300) | 0/100 | **100** | **100** | 0,051 · 0,028 · 0,016 · 0,004 | — |

Critério: (a) escadas recuperadas em ≥ 80 sementes em cada mundo-escada: **não** (1, 2, 0); (b) cíclico com razão fora da progressão e livre melhor que fixa em ≥ 80: **sim** (100 e 100). **Reprovado.** Apostas: 25 % em passar (certa a não-passagem); (a) por mundo 45/30/20 % (certas as três não-passagens); (b) 65 % (certa); livre ≤ fixa em todos (certa).

## O que o resultado diz

A escada é da mente, não do mundo, **no sentido em que este teste pergunta**. Deixados livres, os ganhos não vão para as constantes de tempo do mundo (λ_j · τ_j seria 1): o primeiro andar vai a λ₁ ≈ 1 em todos os mundos-escada (λ₁ · τ₁ = 7 é λ₁ saturado em 1, isto é, "copie o mundo", a mesma lição dos testes de 17/10 e do teste 1), e os demais se espalham com razões ≈ 20, não 10, em posições que servem à predição e não à escada. No escada-4, o quarto andar foi a zero (o otimizador o desligou: um andar de 7.000 passos não ajuda a prever o próximo passo e custa condicionamento).

A razão foi nomeada antes de rodar e o resultado é compatível com ela: a soma de k AR(1) é um ARMA(k, k−1), e o melhor preditor linear de um passo põe os seus polos nas raízes da parte MA, não nos φ_j. Um ajuste por erro de predição mede a escada **da predição**, e essa escada não é a do mundo. Então o teste 4 tem dois significados possíveis, e a leitura não consegue separá-los por completo: ou a v0 não reencontra a escada do mundo, ou o critério "minimize o erro de predição" é incapaz de reencontrá-la mesmo quando ela existe. O λ_j · τ_j fala a favor da segunda: os andares de cima ficam em frações regulares (≈ 3–4 vezes mais rápidos que a constante do mundo), um padrão da predição ótima, não ruído.

No cíclico a v0 fez o que a predição esperava: quebrou a progressão (razões 1,1; 1,2; 6) e concentrou três andares em torno de λ ≈ 0,02–0,05 (2π/300 ≈ 0,021), isto é, pôs quase toda a memória na escala do mundo. É a única parte do teste 4 que passou, e é a parte que diz que a v0 **sabe quando não há escada**.

## O que fecha e o que não

- Fecha: com a escada fixa b = 10 a v0 projeta a própria samambaia na tempestade (o livre ganha da fixa em 400 de 400 rodadas); e o ajuste por predição não reencontra as constantes de tempo do mundo em mundos que as têm.
- Não fecha: se um critério que **não** seja predição (por exemplo, maximizar a independência entre as tensões dos andares, ou o colapso C_j entre pares) reencontraria a escada do mundo. Esse é um teste diferente, e é o que a v0 deveria ter perguntado: a tensão é o objeto, não o erro (compromisso 1 do projeto), mas o teste 4 ajustou pelo erro.

## Para a lista de defeitos de desenho do projeto

9. Teste 4 ajusta os andares pelo erro de predição, contrariando o compromisso 1 do próprio projeto (a tensão é o objeto). O critério que mediria "a escada do mundo" ainda não foi escrito.
10. Parametrização por sigmoide sem limite: λ₁ satura em 1 e λ₄ vai a zero com avisos numéricos; o ajuste deveria ter faixa declarada.

Quatro testes, quatro reprovações, dez defeitos nomeados. A leitura consolidada está em LEITURA_v0.md.
