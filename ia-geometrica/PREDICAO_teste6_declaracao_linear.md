# Predição do teste 6 (a declaração linear)

18/10/2026 · escrita antes de rodar · corrige os defeitos 11 e 12 do teste 5, e só eles

## Pergunta

O teste 5 mostrou que a v0, medindo a cegueira sobre o próprio resíduo, declara escuridão em toda parte. A candidata nomeada lá: **declarar sobre o que o andar recebe, não sobre o que deixou passar.** Com essa declaração, ela acompanha a cegueira real (A)? E serve a um leitor (B)?

## O que muda e o que não muda

- **Declaração nova (linear).** Para o andar j, δ̂_j = fração da potência (soma das d coordenadas, média removida) da sua **entrada** acima de f_j = λ_j / 2π. A entrada do andar 1 é o próprio x (o que a v0 vê, olhando sempre); a do andar j é R_{j−1}. É ainda calculada só com o que a v0 tem.
- **Série longa.** N = 130.000 (≥ 3 × 2π/λ₄ ≈ 126.000), calibração [0, 65.000), medida [65.000, 130.000). Corrige o defeito 12.
- **Tudo o mais igual ao teste 5:** mesmos quatro mundos, 100 sementes, k = 4, λ₁ = 0,15, b = 10, olhar sempre, β_j = E‖x − R_j‖² / Var(x) na medida, critério A (ρ ≥ 0,7 e acima do envelope de permutação, nos quatro andares).
- **Leitor B.** O de teste 5 com o defeito 13 removido: w'_j = w_j · (1 − δ̂_j^dest) / (1 − δ̂_j^treino), **sem renormalização**. Mesmo treino (deriva), mesmos destinos, mesmo critério (U > 0 em ≥ 80 sementes em cada destino), mesmo teto.

## Apostas

- **A: 65 %.** A declaração linear e β são agora quase a mesma integral: β_j é a potência de x filtrada por |1 − H_1 ⋯ H_j|², δ̂_j é a potência da entrada acima de f_j. Diferem por o corte ser abrupto na declaração e suave (primeira ordem) na realidade, e por β acumular os andares anteriores. Por andar: 1: 75 %, 2: 70 %, 3: 65 %, 4: 50 % (no andar 4, β ≈ 1 em quase todo mundo e varia pouco; ρ pode ser baixo por falta de variação, não por erro).
- **B: 30 %.** Sem renormalização a reescala não explode, mas continua heurística e positiva. Por destino: branco 50 %, escada-3 35 %, cíclico 25 %.

## O que fecha

A passa: a v0 tem uma declaração de cegueira verdadeira na ordem, e o OBS-01 ganha a regra "mede-se sobre a entrada". A reprova: o problema não era só o resíduo, e a declaração espectral de primeira ordem não é régua. B segue como está: se reprovar com A passando, o leitor é o defeito, e o próximo leitor escolhe andar em vez de reescalar peso.
