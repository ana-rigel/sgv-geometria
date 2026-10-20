# Predição do teste 37 (a galáxia no cubo: o laço que segura o modo)

20/10/2026 · escrita antes de rodar · modelo da página "NGC 628 no cubo" (artefato de 20/10), sem mudança na dinâmica · Ana Rigel

## De onde vem

Da conversa de 20/10. A Ana propôs dois cenários sobre 1 Gyr: A, sem acoplamento (K = 0, V = 200 km/s), para medir o enrolamento do disco; B, com travamento parcial (K = 1,2 K_c), e um laço de feedback que corrigisse o andar 2 até a coerência ficar perto do valor real da NGC 628 (C_φ = 0,627). Três correções foram feitas antes do desenho, e a Ana fechou o desenho com elas:

1. Com K = 1,2 K_c, o modelo **trava** em ≈ 0,86 (12 sementes, 20/10); 0,627 aparece perto de K ≈ 1,0 K_c, ou com K ≈ 0,7 K_c escutando o andar 4 semeado.
2. O andar 2 (τ ≈ 67 Myr) não é a memória lenta: foi o pior andar, porque o τ dele é da ordem do enrolamento.
3. Um laço que corrige até 0,627 chega a 0,627 por construção. Por isso há duas versões: o **Laço I**, com alvo, que só responde quanto 𝒢 é preciso; e o **Laço II**, sem alvo, em que 0,627 aparece só no julgamento.

Isto é teste do **modelo ilustrativo**, não da NGC 628. Nenhum resultado aqui é evidência sobre a galáxia.

## O modelo (comum a todos os cenários)

12 anéis, r = 9…14 kpc (igualmente espaçados), m = 5, V = 200 km/s, curva plana, passo de 1 Myr, 1.000 Myr. Fases iniciais θᵢ ~ N(0; 0,15 rad). Turbulência D = 2,5 × 10⁻⁴ rad²/Myr. 100 sementes (semente 37), a mesma sequência de ruído em todos os cenários de uma semente.

```
Δωᵢ = m(V/rᵢ − média) · 1,0227×10⁻³          rad/Myr
Z = (1/N) Σ e^{iθᵢ} = C e^{iψ}
v0 no disco: R₀ = Z,  Rⱼ ← Rⱼ + λⱼ (Rⱼ₋₁ − Rⱼ),  λⱼ = 0,15 · 10^{−(j−1)} /Myr
θᵢ ← θᵢ + Δωᵢ + K |A| sen(arg A − θᵢ) + √(2D) ξᵢ
A = Z (escuta instantânea)  ou  A = Rⱼ (escuta o andar j)
K_c = 2 (max Δω − min Δω)/π ≈ 25,8 mrad/Myr
```

A memória "vazia" nasce com Rⱼ = 0 (a convenção de Juara); a "semeada" nasce com Rⱼ = Z(0).

## Os cenários

**A, sem acoplamento (K = 0).** O enrolamento tem fórmula exata:

  C_A(t) = |(1/N) Σ e^{iΔωᵢ t}| · e^{−σ₀²/2} · e^{−D t},  σ₀ = 0,15.

Conta: abertura de 40,6 mrad/Myr; uma volta inteira entre 9 e 14 kpc em **154,8 Myr**; C < 0,5 a partir de **87,5 Myr**; primeiro mínimo em **142 Myr** (C ≈ 0,15). A simulação serve para verificar o instrumento contra a fórmula.

**B, travamento fixo (K = 1,2 K_c, escuta instantânea).** O cenário como foi pedido, sem laço.

**B-inverso, Laço I (com alvo).** Escuta instantânea; K começa em 0 e é corrigido:

```
C̄ ← C̄ + (C − C̄)/50              (média de 50 Myr)
K ← clip( K + κ (0,627 − C̄), 0, 3 K_c ),   κ = 0,02 K_c por Myr
```

Resultado: K∞/K_c = média de K/K_c entre 600 e 1.000 Myr. Relatado também com escuta no andar 4 semeado.

**B-auto, Laço II (sem alvo).** Os anéis escutam o andar j, com K = 0,8 K_c (abaixo do limiar: sem laço e com escuta instantânea, o disco fica solto, ≈ 0,36). A rigidez do andar escutado é modulada pela tensão entre a memória e o disco:

```
s = |Rⱼ| − C
λⱼ(t) = λⱼ⁰ · exp(−β · max(0, s)),   β = 5
```

Quando o disco perde coerência em relação ao que a memória guarda, a memória endurece e segura a fase antiga. 0,627 não entra no laço. Rodado para j = 2, 3 e 4, com memória vazia e semeada, e sempre com o par β = 0 (o mesmo andar, sem laço) para separar o efeito do laço.

**Faixa da NGC 628:** C̄ entre 300 e 1.000 Myr dentro de **[0,527; 0,727]** (0,627 ± 0,1).

## Conta prévia (das simulações de 20/10, 12 sementes, e do Kuramoto com fase fixa)

- **B fixo:** ≈ 0,86 em 1.000 Myr; fora da faixa.
- **Laço I:** escuta instantânea, C(K) sobe de 0,36 em 0,8 K_c para 0,61 em 1,0 K_c; o laço deve parar em K∞/K_c ≈ 1,0. No andar 4 semeado, perto de 0,7.
- **Laço II, andar 2 vazio:** nos primeiros ≈ 67 Myr, o andar 2 aprende a fase com o disco ainda coerente (|R₂| → ≈ 0,8–0,9). Quando o disco começa a enrolar, s > 0 e a memória endurece, guardando a fase antiga. Vira um pino de fase com força K|R₂| ≈ 0,8 × 0,85 × K_c ≈ 0,68 K_c. Um anel trava num pino fixo se |Δωᵢ| < K|R₂|. Com abertura de ±20,3 mrad/Myr e K|R₂| ≈ 17,5, cerca de três quartos dos anéis travam, o que dá C perto de 0,6–0,7. Mas o pino não é fixo: |R₂| cai devagar se o disco não sustentar, e o equilíbrio pode escorregar para baixo. Sem laço (β = 0), o andar 2 vazio dava ≈ 0,19–0,28 em 0,8 K_c.
- **Laço II, andares 3 e 4:** vazios, aprendem tarde demais (o disco enrola em ≈ 150 Myr) e o laço não tem fase coerente para guardar; semeados, já seguravam sem laço (0,58–0,74 em 0,8 K_c), e o laço só os endurece mais.

## Critérios

**J1, o instrumento reproduz o enrolamento (A):** a média de C nas 100 sementes fica a ≤ **0,05** de C_A(t) em todo t ∈ [0; 300] Myr, e o primeiro t com média < 0,5 fica a ≤ **5 Myr** de 87,5.

**J2, o travamento fixo estabiliza perto da NGC 628 (B):** C̄(300–1.000) na faixa em **≥ 80 de 100**.

**J3, o laço com alvo converge (Laço I, escuta instantânea):** K∞/K_c entre **0,9 e 1,1** e |C̄(600–1.000) − 0,627| ≤ **0,05** em **≥ 80 de 100**.

**J4, o andar 2 segura sozinho (Laço II, andar 2, memória vazia):** C̄(300–1.000) na faixa em **≥ 80 de 100**, e a mediana da diferença para o mesmo andar com β = 0 ≥ **+0,10**.

**J5, o andar 2 é o pior para segurar (Laço II, memória semeada):** entre os andares 2, 3 e 4 com laço, o andar 2 tem a **menor** mediana de C̄(300–1.000).

Relatado: todas as combinações (andar × nascimento × β ∈ {0; 2; 5; 10}); as trajetórias de λⱼ(t) e |Rⱼ|(t); a fração de anéis travados; o Laço I no andar 4 semeado.

## Apostas (Claude, antes de rodar)

- **J1: 90 %.** O ruído entra só pelo fator e^{−Dt}, que a fórmula já tem.
- **J2: 5 %.** A conta põe B em ≈ 0,86.
- **J3: 70 %.** O laço deve convergir; o risco é oscilar perto de K_c, onde C(K) é íngreme.
- **J4: 40 %.** O pino de fase dá ≈ 0,6–0,7 se ficar firme; o risco é |R₂| escorregar e o equilíbrio cair abaixo de 0,527.
- **J5: 50 %.** Com o laço, todos os andares semeados endurecem; a diferença entre eles pode sumir.

## O que fecha

- **J4 passa:** uma memória rápida que endurece quando o disco perde coerência segura o modo na faixa da NGC 628, sem alvo e abaixo do limiar de Kuramoto. Para a v0, é a primeira forma de auto-organização com o andar ajustando a própria rigidez pela tensão. Para a galáxia, é só "compatível com": o modelo nasce coerente em t = 0 (o laço guarda uma ordem inicial que foi suposta), e uma curva de rotação mal declarada também dá 0,63 sem 𝒢 (teste 34).
- **J4 reprova e J3 passa:** segurar 0,627 exige um alvo ou K perto de K_c; uma memória que só endurece não basta.
- **J1 reprova:** o instrumento não reproduz a fórmula exata do enrolamento, e todo o resto fica sem leitura até isso ser entendido.
- **J5 passa ou reprova:** diz se o "pior andar" de 20/10 continua pior quando a memória aprende a endurecer.

Um julgamento por hipótese; sem emenda. Instrumento: teste37.py, escrito depois do commit desta predição.
