# Predição do teste 47 (a janela no limite contínuo: uma função de β)

20/10/2026 · escrita antes de calcular · teoria do teste 46 levada a N → ∞ · Ana Rigel

## De onde vem

Do teste 46: a autoconsistência do estado parcialmente travado prevê o fim da janela exatamente e o começo com um viés de campo médio que some com N (≤ 0,01 K_c em 48 anéis). A Ana pediu, em 20/10, para seguir o passo (a): derivar a janela no limite contínuo como função de β, uma propriedade da distribuição de frequências que não dependa da NGC 628.

## A teoria contínua

Anéis distribuídos uniformemente em r ∈ [9, 14] kpc, Ω(r) ∝ r^(β−1), Δω(r) = a (r^(β−1) − média), com a escolhido para a abertura (max − min) da curva plana, de modo que K_c = 2(max − min)/π seja o mesmo para todos os β. As somas do teste 46 viram médias em r:

```
ρ = ⟨ √(1 − x²) · 1[|x| ≤ 1] ⟩_r
0 = ⟨ x · 1[|x| ≤ 1] + (x − sgn(x)√(x² − 1)) · 1[|x| > 1] ⟩_r,     x = (Δω(r) − Ω)/u,  u = K ρ
```

Para cada u, resolve-se a segunda em Ω (escolhendo a raiz de maior ρ), e daí K = u/ρ(u). A curva paramétrica (K, ρ, fração travada) dá, para cada K, o ramo de maior ρ. Quadratura de 2.000 pontos em r; 2.000 valores de u.

- **Fim da janela (K_L):** o menor K com fração travada = 1. Com todos travados, a segunda equação dá Ω = 0 e K_L/K_c = min_{u ≥ max|Δω|} u / [K_c ⟨√(1 − (Δω/u)²)⟩].
- **Começo da janela:** o menor K com fração travada ≥ ½ (a mesma definição dos testes 44 e 46).
- **Largura:** fim − começo, em K/K_c.

Grade de β: −0,6 a +0,9, passo 0,1.

## Conta prévia

- Pelos testes 44 e 46, a largura em N = 48 fica em 0,185 · 0,180 · 0,165 · 0,135 · 0,110 (β = −0,4 … +0,4), e K_L em 1,085 · 1,080 · 1,075 · 1,065 · 1,060. K_L desce com N (de 1,12 em 12 anéis para 1,075 em 48, β = 0); o contínuo deve ficar um pouco abaixo de N = 48.
- Para β → 1, a distribuição tende à uniforme, e no contínuo uniforme a janela é zero (K_L = K_c, travamento direto). A largura deve ir a zero.
- Para β = 0 (curva plana), p(Ω) ∝ Ω^(−2), assimétrica: a janela deve sobreviver no contínuo com largura perto da de N = 48.

## Critérios

**J1, o fim da janela converge:** para β ∈ {−0,4; −0,2; 0; +0,2; +0,4}, |K_L contínuo − K_L de N = 48 (simulação, teste 44)| ≤ **0,02 K_c** nos cinco.

**J2, a largura converge:** |largura contínua − largura de N = 48 (simulação)| ≤ **0,02 K_c** em **≥ 4 dos 5** β.

**J3, a lei de β:** a largura contínua é **estritamente decrescente** em β em toda a grade de −0,6 a +0,9, e em β = +0,9 é **≤ 0,02 K_c**.

**J4, a curva plana sobrevive no contínuo:** em β = 0, a largura contínua é **≥ 0,12 K_c**.

Relatado: K_L(β), começo(β), largura(β), ρ no começo e no fim; a fórmula de K_L comparada com a solução completa.

## Apostas (Claude, antes de calcular)

- **J1: 80 %.**
- **J2: 70 %.** As janelas de N = 48 com β ≤ 0 começam na borda da grade (0,90), então são mínimos; o contínuo pode passar delas.
- **J3: 80 %.**
- **J4: 85 %.**

## O que fecha

- **J3 e J4 passam:** a largura da janela de sincronização parcial é uma função decrescente da inclinação da curva de rotação, que se anula na rotação sólida e não se anula para curvas planas, independente do número de anéis. É a hipótese matemática geral que a Ana pediu, no modelo.
- **J1 e J2 passam:** o limite contínuo reproduz as simulações de 48 anéis, e a teoria pode substituir a simulação para varrer curvas de rotação (a investigação 3).
- **J4 reprova:** a janela da curva plana é efeito de N finito e some no contínuo.

Um julgamento por hipótese; sem emenda. Instrumento: teste47.py, escrito depois do commit desta predição.
