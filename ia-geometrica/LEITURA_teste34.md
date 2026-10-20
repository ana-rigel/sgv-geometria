# Leitura do teste 34 (a régua da organização): J1 e J2 REPROVADOS. Com a arquitetura declarada a régua é exata; sem ela, ou é cega, ou é fraca

**Predição:** PREDICAO_teste34_regua_da_organizacao.md (8e4d4fe), antes de escrever o instrumento. **Instrumento:** teste34.py. **Resultado:** resultados_teste34.json. 100 mundos (permutações dos 16 anos de Juara, semente 34). Dois julgamentos; sem emenda.

| corpo | Θ ajustada, mediana [q05; q95] | Θ nominal | Θ exato | λ̂ / λ₃ | R do silêncio, mediana [q05; q95] |
|---|---|---|---|---|---|
| N0 v0 pura | 0,000 [0,000; 0,000] | 0,000 | 0 | 1,000 | 0,098 [0,043; 0,221] |
| N1 ruído vermelho | +0,035 [−0,069; +0,159] | +0,019 | 0 | 0,990 | 0,115 [0,058; 0,236] |
| N2 memória mais curta | 0,000 [0,000; 0,000] | **+1,149** | 0 | 1,500 | 0,094 [0,043; 0,215] |
| N3 esquecimento não linear | +0,013 [−0,128; +0,152] | **+1,004** | 0 | 1,422 | 0,049 [0,024; 0,125] |
| P(0,05) | +0,010 [+0,003; +0,018] | +0,135 | 0,135 | 1,045 | 0,108 [0,052; 0,213] |
| P(0,10) | +0,020 [+0,006; +0,035] | +0,264 | 0,265 | 1,089 | 0,117 [0,066; 0,213] |
| P(0,25) | +0,048 [+0,015; +0,082] | +0,621 | 0,623 | 1,223 | 0,171 [0,123; 0,240] |
| P(0,50) | +0,090 [+0,033; +0,147] | +1,133 | 1,138 | 1,444 | 0,244 [0,208; 0,295] |
| P(1,00) | +0,165 [+0,079; +0,253] | +1,947 | 1,956 | 1,878 | 0,345 [0,318; 0,386] |

Limiares (quantil 95 % dos negativos): régua A ajustada 0,127; régua B 0,219; régua A nominal (só N0 e N1) 0,073.

| régua | detecções em 100: γ = 0,05 · 0,10 · 0,25 · 0,50 · 1,00 | piso |
|---|---|---|
| A, sombra ajustada | 0 · 0 · 0 · 11 · 77 | nenhum na grade |
| B, silêncio | 5 · 5 · 13 · **85** · 100 | 1,00 |
| A, sombra nominal | 100 · 100 · 100 · 100 · 100 | 0,05 |

**J1, a régua do silêncio acha organização moderada (piso ≤ 0,50):** P(0,50) passou do limiar em **85 de 100**, contra 90 pedidos. Piso = 1,00. **Reprovado.**
**J2, a sombra ajustada acha organização moderada (piso ≤ 0,50):** 11 de 100 em γ = 0,50 e 77 em γ = 1,00. Sem piso. **Reprovado.**

Apostas: J1 passa (50 %), errada, por 5 mundos; J2 passa (20 %), certa a reprovação; Θ_ajustada / Θ_exato em P(0,25) entre 0,05 e 0,35 (70 %), certa (0,077); com a sombra nominal, N2 acima do limiar em ≥ 90 (90 %), certa (100); N3 em ≥ 50 (60 %), certa (100).

A conta prévia acertou a forma e quase todos os números: Θ_exato 0,14 · 0,27 · 0,64 · 1,17 · 2,00 previstos contra 0,135 · 0,265 · 0,623 · 1,138 · 1,956; R dos positivos 0,13 · 0,22 · 0,33 contra 0,17 · 0,24 · 0,35; θ*_B perto de 0,2 contra 0,219; N2 nominal 1,2 contra 1,15. Errou para menos a absorção: previu que a sombra ajustada veria 1/5 do 𝒢 e ela viu 1/13 (0,077), em todo γ.

## O que o resultado diz

**1. Com a arquitetura declarada, a régua é exata e fina.** A sombra nominal reproduz a verdade a 0,005 em todos os γ e detecta um 𝒢 de 5 % em 100 de 100 mundos. Para a própria v0, cuja arquitetura nós escrevemos, isso basta: um ⋄ que segure o ciclo no andar 3 seria medido com precisão.

**2. Mas a sombra nominal chama de organização qualquer desvio da arquitetura.** Uma memória 50 % mais curta (N2) e um esquecimento não linear sem nenhum padrão guardado (N3) dão Θ ≈ 1,0–1,15, o tamanho de um 𝒢 entre 0,4 e 0,5, em 100 de 100 mundos. A régua mede "mais ciclo do que a arquitetura declarada deixaria", e não "padrão guardado". As duas coisas só coincidem quando a declaração está certa.

**3. Ajustar a sombra aos próprios dados engole a organização.** Um reforço do ciclo em fase com a entrada é, para um registro de 1ª ordem ajustado, uma memória mais curta: λ̂ sobe para 1,22 λ₃ em P(0,25), e a sombra passa a carregar 92 % do excesso. Sobra 1/13 do 𝒢, abaixo do ruído dos negativos até γ = 0,5. Um observador que só olha e ajusta não distingue organização de memória.

**4. Intervir distingue, mas fraco, por causa do próprio clima.** No silêncio, nenhum negativo engana a régua B: N2 e N3 ficam no mesmo fundo de N0, e N3 até abaixo. Ela é específica. O fundo, porém, é alto (R ≈ 0,10, q95 = 0,22) e vem do que a conta prévia apontou: a climatologia de 8 anos não é o clima dos outros 8, e a diferença entre as duas metades sobra coerente e passa pela cascata como ciclo. Um 𝒢 que some 50 % ao ciclo fica no limite (85 de 100); um de 100 % aparece sempre.

**5. A fase não ajuda aqui.** A diferença de C_φ entre corpo e sombra ficou entre −0,003 e +0,007 em todos os corpos. As estações de Juara já chegam com C_φ ≈ 0,98, e o 𝒢 injetado reforça em fase. O índice η da galáxia, que mede fase, não separaria nada neste mundo.

## O que isso significa

- **Para a v0 e o ⋄:** medir com a sombra nominal, e só depois de verificar que o resto da placa é exatamente o declarado (λ certos, andares lineares). Uma diferença de λ de 50 % vale tanto quanto um 𝒢 de 0,5.
- **Para o OBS-01:** numa IA alheia, cuja arquitetura não se conhece, a organização não aparece observando. Só aparece intervindo na entrada (o silêncio), e só se for grande, a menos que a intervenção tenha um fundo menor que o de um clima real.
- **Para a NGC 628:** o Z = 82 é uma leitura de sombra nominal, porque o modelo passivo foi declarado. Este teste dá a forma precisa da ressalva escrita na nota: com sombra declarada, uma física passiva mal especificada produz excesso do mesmo tamanho de uma organização, e numa galáxia não se pode fazer o silêncio. O excesso mostra que o modelo passivo não basta, e não mostra que há organização.

## Para a lista de defeitos de desenho

46. A conta prévia pôs o piso da régua B em γ ≈ 0,5, e a grade pulou de 0,50 para 1,00. O J1 caiu por 85 contra 90 exatamente no ponto previsto, sem um γ entre 0,5 e 1,0 para dizer onde o piso fica. Onde a conta prévia aponta a beira, a grade precisa ser fina ali.

Placar: 34 testes numerados (o 25 sem resultado). 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34: ambos reprovaram. 46 defeitos, 1 emenda.
