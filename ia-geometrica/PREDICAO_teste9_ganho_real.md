# Predição do teste 9 (a declaração com ganho real)

18/10/2026 · escrita antes de rodar · corrige os defeitos 14 e 15 do teste 6, e só eles

## Pergunta

No teste 6 a declaração linear acompanhou a cegueira real nos andares 1 e 3 (ρ 0,99 e 0,87) e falhou no 2 por declarar com um corte abrupto onde o filtro é suave, e no 4 por não haver mundo com nada mais lento que a identidade. **Declarando com o ganho real do andar, e com um mundo mais lento que a identidade entre os mundos, a declaração acompanha a cegueira real nos quatro andares?**

## O que muda e o que não muda

- **Declaração com ganho real.** Para o andar j, com entrada e_j (x para j = 1, R_{j−1} para j > 1) e espectro S_e(f) (soma das coordenadas, média removida):

  δ̂_j = Σ_f S_e(f) · (1 − |H_j(f)|²) / Σ_f S_e(f), com |H_j(f)|² = λ_j² / (1 − 2(1 − λ_j) cos 2πf + (1 − λ_j)²),

  o ganho exato de um registro de primeira ordem com ganho λ_j. É o que o andar de fato não representa da sua entrada, frequência a frequência, e continua calculável só com o que a v0 tem (a sua entrada e o seu λ).
- **Quinto mundo, "lento":** AR(1) com τ = 50.000 (φ = 1 − 1/τ) mais ruído branco σ = 0,3. É o único mundo com potência abaixo de f₄ = 2,4 × 10⁻⁵; nele β₄ < 1, e o andar 4 passa a ter o que acompanhar.
- **Tudo o mais igual ao teste 6:** branco, deriva, escada-3, cíclico; N = 130.000; calibração [0, 65.000), medida [65.000, 130.000); 100 sementes; k = 4, λ₁ = 0,15, b = 10; olhar sempre; β_j = E‖x − R_j‖² / Var(x); critério A: ρ_j ≥ 0,7 e acima do envelope de permutação (1.000), nos quatro andares, agora sobre 500 pares (mundo, semente). Relata-se o erro absoluto mediano |δ̂ − β| por andar.
- **Sem hipótese B.** O leitor por reescala foi refutado duas vezes (defeito 16); o próximo leitor é outro teste.

## Apostas

- **Passar: 55 %.** Por andar: 1: 90 % (já passava; o ganho real só pode aproximar o valor), 2: 75 % (o cíclico, que o derrubava, agora declara ≈ 0,66 em vez de 0,999, perto do 0,77 real), 3: 80 %, 4: 55 % (o mundo lento dá variação, mas é um só entre cinco; com N = 2,6 τ a potência do AR(1) de τ = 50.000 está mal realizada, e β₄ pode variar pouco entre sementes e muito entre mundos, o que basta ao Spearman).
- Erro absoluto mediano abaixo de 0,05 nos andares 1–3 (65 %).
- Diferença entre δ̂ e β que restar é **sistemática por mundo** e não aleatória (70 %): β acumula os andares anteriores (o resíduo do andar j contém o que os andares 1 … j−1 também não viram), e δ̂ é sobre a entrada do andar; onde isso pesa, δ̂ fica abaixo de β.

## O que fecha

Passar: a v0 tem uma declaração de cegueira verdadeira nos quatro andares, em cinco mundos, com erro conhecido; é a régua que o OBS-01 pediu, no mundo sintético. Reprovar no 4 só: a identidade é medível, mas precisa de mais mundo lento do que este; não é defeito da declaração. Reprovar no 2 ou 3: o ganho real não era a causa, e a declaração espectral tem outro defeito, a nomear.
