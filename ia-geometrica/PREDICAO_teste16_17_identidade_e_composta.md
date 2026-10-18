# Predições dos testes 16 (o andar da identidade) e 17 (a declaração composta)

18/10/2026 · escritas antes de rodar · corrigem os defeitos 19 e 20 do teste 9 · um instrumento, dois julgamentos

## Teste 16: o andar 4 declara certo quando há o que declarar?

No teste 9 a declaração com ganho real passou nos andares 1–3 (ρ ≥ 0,92) e o andar 4 ficou em 0,37 porque só um mundo em cinco tinha potência abaixo do seu corte: 100 pares com variação real, 400 com ruído. **Com a maioria dos mundos mais lenta que a identidade, a declaração do andar 4 acompanha a sua cegueira real?**

**Mundos** (N = 400.000; calibração [0, 200.000), medida [200.000, 400.000); 100 sementes; k = 4, λ₁ = 0,15, b = 10; olhar sempre):

- lento-a: AR(1) τ = 20.000 + branco σ = 0,3;
- lento-b: AR(1) τ = 50.000 + branco σ = 0,3;
- lento-c: AR(1) τ = 100.000 + branco σ = 1,0 (mais ruído: β₄ maior);
- escada-3 (τ 7, 70, 700) e cíclico (período 300): os dois sem nada abaixo de f₄, para que β₄ ≈ 1 também apareça.

Três mundos em cinco com β₄ < 1, e com valores diferentes entre si (τ e σ de ruído diferentes). N = 400.000 ≥ 4 τ do mais lento e ≈ 10 períodos do andar 4.

**Declaração:** a do teste 9 (sobre a entrada do andar, com o ganho real). **Cegueira real:** β_j = E‖x − R_j‖² / Var(x) na medida.

**Critério 16 (um julgamento):** ρ Spearman entre δ̂₄ e β₄ nos 500 pares ≥ 0,7 e acima do envelope de permutação. Relata-se também ρ dos andares 1–3 (sem critério: já julgados no 9).

**Apostas:** passar **65 %**. A favor: no único mundo lento do teste 9 a declaração ficou a 0,09 da verdade na ordem certa; com três mundos lentos distintos a variação é real. Contra: com τ = 100.000 e N = 400.000 a potência de baixa frequência é mal realizada e β₄ varia muito entre sementes do mesmo mundo, o que ajuda o Spearman se δ̂ acompanhar e atrapalha se não.

## Teste 17: a declaração composta acerta o valor?

A declaração de cada andar é sobre a sua **entrada**; a cegueira real β é sobre o **mundo**, e acumula o que os andares anteriores também não viram. No teste 9 isso apareceu como δ̂ < β nos andares 2 e 3 (0,80 contra 0,95; 0,62 contra 0,88). **Composta andar a andar, a declaração acerta a cegueira real no valor, e não só na ordem?**

**Declaração composta:** δ̂^c_j = 1 − Π_{i ≤ j} (1 − δ̂_i), com δ̂_i a declaração com ganho real de cada andar sobre a sua entrada. É a fração do mundo que o andar j não representa se cada andar só deixasse passar o que o seu ganho deixa; aproximação declarada (supõe que as bandas vistas se compõem como produto, exato para filtros em cascata e sinais cuja potência se distribui como o produto dos ganhos, aproximado em geral).

**Critério 17 (um julgamento):** erro absoluto mediano |δ̂^c_j − β_j| nos 500 pares ≤ 0,05 nos andares 1, 2 e 3 (o 4 relatado, sem critério: a sua composta com β ≈ 1 em dois mundos é trivial). Comparação relatada: o erro da declaração **não** composta nos mesmos pares (0,03; 0,15; 0,11 no teste 9).

**Apostas:** passar **45 %**. A favor: a composição é exata para a cascata de filtros se a potência se distribuir por bandas disjuntas. Contra: as bandas de primeira ordem vazam (defeitos 14 e 18, o mesmo corte suave), e a composta por produto subestima a cegueira nas bandas sobrepostas: espero δ̂^c ainda abaixo de β nos andares 2 e 3, com erro entre 0,05 e 0,10 (50 %). Andar 1: passa (90 %: composta = simples).

## O que fecha

16 passa: a identidade da v0 tem uma declaração de cegueira verdadeira, e a régua de cegueira vale nos quatro andares. 17 passa: a régua acerta o valor, não só a ordem, e o OBS-01 ganha uma medida absoluta. 17 reprova com erro sistemático para baixo: a composta por produto é a aproximação errada e a leitura dirá quanto; o conserto (compor pelos ganhos, não pelas frações) é outro teste.
