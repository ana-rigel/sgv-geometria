# Predição do teste 46 (a janela prevista sem integrar: autoconsistência do estado parcialmente travado)

20/10/2026 · escrita antes de calcular · teoria comparada com as simulações dos testes 41 e 44 · Ana Rigel

## De onde vem

Da decisão da Ana em 20/10 (o "NCG-46"): encerrar a auditoria geométrica e voltar ao eixo rotação diferencial → distribuição de frequências → sincronização parcial → persistência. Das três investigações que ela propôs, esta é a segunda: **existe uma propriedade matemática da distribuição de frequências que preveja a janela sem integrar o sistema por bilhões de anos?** O teste 44 mostrou que a forma da curva de rotação (β) decide a largura da janela, igual em N = 12, 24 e 48. O teste 41 mostrou que, dentro da janela, um aglomerado dos anéis externos trava e os internos deslizam.

## A teoria

Para θ̇ᵢ = Δωᵢ + K r sen(ψ − θᵢ), procura-se um estado em que o aglomerado gira com frequência Ω. Com x_i = (Δω_i − Ω)/(K r):

- anel travado (|x_i| ≤ 1): sen(θ_i − ψ) = x_i, cos(θ_i − ψ) = √(1 − x_i²);
- anel deslizante (|x_i| > 1): média no tempo ⟨cos⟩ = 0, ⟨sen⟩ = x_i − sgn(x_i)√(x_i² − 1).

Autoconsistência (a média de e^{i(θ−ψ)} é r, real):

```
r = (1/N) Σ_travados √(1 − x_i²)
0 = (1/N) [ Σ_travados x_i + Σ_deslizantes (x_i − sgn(x_i)√(x_i² − 1)) ]
```

Para cada K, resolve-se a segunda equação em Ω para cada r de uma grade, e procura-se a raiz de r na primeira; quando há mais de uma, usa-se o **maior r** (o ramo que costuma ser o estável). A teoria entrega r_teo(K), o conjunto de anéis travados e deslizantes, a janela prevista (os K com ≥ N/2 travados e ≥ 1 deslizando) e K_L (todos travados). Nenhuma integração no tempo.

A aproximação trata cada anel deslizante como se o campo médio fosse constante. É exata no limite de N grande; em N finito e no regime caótico (a borda de baixo da janela, teste 41), pode errar.

## A comparação

- **Com o teste 44:** as 15 combinações β ∈ {−0,4; −0,2; 0; +0,2; +0,4} × N ∈ {12, 24, 48}, mesmas frequências (Ω ∝ r^(β−1), reescaladas à abertura da curva plana), mesma grade de K (0,90–1,20, passo 0,005). Da simulação: largura da janela, K_L e mediana de C̄ por K (já no resultados_teste44.json).
- **Quem desliza:** nova simulação, sem ajuste, para N = 12 e os cinco β (condição coerente, 20 Gyr, o mapa do teste 41), registrando a frequência efetiva de cada anel nos K da janela simulada do teste 44. O conjunto de deslizantes simulado (fora do maior aglomerado) é comparado com o da teoria.

## Conta prévia

- K_L sai da mesma autoconsistência do teste 40 (todos travados), que lá deu 1,115 K_c para β = 0, N = 12; a simulação deu 1,12 (grade de 0,005). Deve bater em todos os casos.
- Dentro da janela, a parte de cima é regular (dois anéis deslizando, teste 41) e é onde a teoria deve acertar melhor; a parte de baixo, caótica, é onde deve errar, e é ela que define o começo da janela. Espero a largura prevista um pouco diferente da simulada, mais nos N pequenos.
- O ⟨|Z|⟩ simulado, em N finito, tem as flutuações dos anéis deslizantes, que a teoria média; espero C̄ simulado um pouco acima de r_teo.
- Quem desliza deve ser previsto bem: são os anéis de maior |Δω − Ω|, os internos.

## Critérios

**J1, o travamento total:** |K_L teórico − K_L simulado| ≤ **0,01 K_c** em **≥ 14 das 15** combinações.

**J2, a largura da janela:** |largura teórica − largura simulada| ≤ **0,025 K_c** em **≥ 12 das 15** (as larguras simuladas que começam na borda da grade entram como estão).

**J3, a coerência:** nos K da janela simulada, o erro absoluto médio entre r_teo e a mediana de C̄ simulada é **≤ 0,05**, em **≥ 12 das 15**.

**J4, quem desliza:** em N = 12, nos K da janela simulada dos cinco β, o conjunto de anéis deslizantes da teoria é **igual** ao da simulação em **≥ 80 %** dos pontos.

Relatado: r_teo(K), Ω(K) e os conjuntos de anéis por combinação; o tempo de cálculo da teoria contra o da simulação; onde a teoria erra (borda de baixo ou de cima).

## Apostas (Claude, antes de calcular)

- **J1: 90 %.**
- **J2: 55 %.**
- **J3: 50 %.**
- **J4: 70 %.**

## O que fecha

- **J2, J3 e J4 passam:** a janela de sincronização parcial é uma propriedade calculável da distribuição de frequências; a investigação 3 (curvas de rotação com inclinação variável dentro das incertezas) pode ser varrida pela teoria, sem simulações longas, e a relação entre a geometria da curva e a janela vira uma fórmula, não só um resultado numérico.
- **J1 e J4 passam, J2 reprova:** a teoria prevê o fim da janela e quem desliza, mas não o começo, que fica no regime caótico. A janela teria uma borda calculável e outra que exige simulação.
- **J4 reprova:** quem desliza não é simplesmente quem está mais longe da frequência do aglomerado, e a estrutura radial que o modelo prevê para a galáxia precisa de outra explicação.

Um julgamento por hipótese; sem emenda. Instrumento: teste46.py, escrito depois do commit desta predição.
