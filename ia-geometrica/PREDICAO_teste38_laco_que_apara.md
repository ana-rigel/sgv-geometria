# Predição do teste 38 (o laço que apara: autoconsistência e criticidade)

20/10/2026 · escrita antes de rodar · modelo de teste37.py, sem mudança na dinâmica do disco · Ana Rigel

## De onde vem

Da leitura do teste 37 e da conversa que veio depois. No modelo da NGC 628, o andar 3 semeado, **sem laço**, segura o disco em C̄ = 0,662 (K = 0,8 K_c). O Laço II só endurece a memória: o fator exp(−β·max(0, |R| − C)) é sempre ≤ 1, e com a memória semeada a tensão é sempre positiva; por isso ele empurra C **para cima** (0,690 · 0,714 · 0,734 com β = 2, 5, 10). A Ana pediu um laço que **apare**: que possa agir nos dois sentidos, sem receber 0,627 de fora.

Um laço que apara precisa de um critério interno para "demais". Não há critério neutro; este teste põe à prova os dois mais fundamentados:

- **Autoconsistência (Laço III-a):** a memória não deve impor ao disco mais ordem do que ele sustenta. O ponto fixo é |R| = C, a ideia do registro autoconsistente do Paper A.
- **Criticidade (Laço III-b):** o disco deve ficar onde mais flutua, na borda entre soltar e travar. É a forma operacional de "se seguem sem se colar" (conversa de 20/10).

Nos dois, o que se ajusta é a **voz** da memória, g: o acoplamento passa a ser K · g · |Rⱼ| · sen(arg Rⱼ − θᵢ). g pode subir ou descer; λ fica fixo. 0,627 só aparece no julgamento.

Isto é teste do modelo ilustrativo, não da NGC 628.

## O modelo

O do teste 37: 12 anéis, r = 9…14 kpc, m = 5, V = 200 km/s, D = 2,5 × 10⁻⁴ rad²/Myr, fases iniciais N(0; 0,15), 100 sementes, a mesma sequência de ruído em todos os braços de uma semente. Escuta no **andar 3** (λ₃ = 0,0015 /Myr). A duração passa a ser **5.000 Myr**, porque um laço que apara uma memória de τ ≈ 670 Myr precisa de vários τ para chegar a algum lugar. Medida: C̄ entre **3.000 e 5.000 Myr**. g começa em 1 e fica entre 0,05 e 20.

**Laço III-a, autoconsistência:**

  log g ← log g + η_a · (C − |R₃|),  η_a = 0,05 por Myr.

A memória que guarda mais que o disco perde voz; o disco mais coerente que a memória dá voz a ela.

**Laço III-b, criticidade** (busca de extremo da flutuação):

```
g = g₀ · exp(0,2 · sen(2π t / 100))                 sondagem lenta, período 100 Myr
χ = variância de C numa janela exponencial de 50 Myr
G ← G + [(χ − χ̄) · sen(2π t / 100) − G] / 200      gradiente demodulado, média de 200 Myr
log g₀ ← log g₀ + 0,01 · G / (χ̄ + 10⁻⁴)
```

g₀ sobe se aumentar a voz aumenta a flutuação, e desce se a diminui. O laço procura o máximo de χ.

**Braços:** III-a e III-b com o andar 3 **semeado**, em K = 0,7 · 0,8 · 0,9 K_c; os dois com o andar 3 **vazio**, em K = 0,8 K_c; e o andar 3 semeado **sem laço** (g = 1) nos três K, como referência de 5.000 Myr. Faixa da NGC 628: [0,527; 0,727].

## Conta prévia

- **Sem laço, 5.000 Myr:** |R₃| decai devagar enquanto o disco fica abaixo dele, então o pino enfraquece com o tempo. Os 0,662 de 300–1.000 Myr devem cair em 3.000–5.000; não sei quanto.
- **III-a tem um ponto fixo degenerado.** Num disco estacionário e travado, a memória lenta guarda a média de Z, e |R₃| → C sozinho. Qualquer estado estacionário satisfaz |R₃| = C, então o critério não escolhe um nível: ele só tira a voz enquanto a memória ainda guarda a ordem inicial (|R₃| ≈ 0,9–0,99 > C). Espero que III-a **apare para baixo** e pare onde a memória terminar de decair, num nível que depende de K e da velocidade relativa de g e de |R₃|. Não espero um ponto próprio do laço.
- **III-b procura a borda.** No Kuramoto com 12 anéis, a flutuação de C é máxima na transição entre solto e travado, onde C fica entre ≈ 0,35 e 0,6. Se o laço achar a borda, deve parar aí e, **por ser a borda, num C parecido em qualquer K**, porque g compensa K. O risco é a estimativa de χ com 12 anéis ser ruidosa demais para o gradiente.
- **Vazio:** III-a dá voz quando C > |R₃|, o que acontece no começo (|R₃| ≈ 0). Pode criar uma ordem que se alimenta? Com |R₃| ≈ 0,05–0,1, mesmo g = 20 dá voz efetiva de 0,8 × 20 × 0,08 ≈ 1,3 K_c no limite, então criar é possível em princípio. III-b com memória vazia também pode subir g sem limite natural.

## Critérios

**J1, a autoconsistência apara até a faixa (III-a, semeado, 0,8 K_c):** C̄(3.000–5.000) na faixa em **≥ 80 de 100**.

**J2, a autoconsistência tem um ponto próprio (III-a, semeado):** as medianas de C̄ em 0,7 · 0,8 · 0,9 K_c ficam a ≤ **0,05** umas das outras.

**J3, a criticidade apara até a faixa (III-b, semeado, 0,8 K_c):** C̄(3.000–5.000) na faixa em **≥ 80 de 100**.

**J4, a criticidade tem um ponto próprio (III-b, semeado):** as medianas de C̄ nos três K ficam a ≤ **0,05** umas das outras.

**J5, os laços não criam ordem (III-a e III-b, vazio, 0,8 K_c):** mediana de C̄(3.000–5.000) ≤ **0,25** nos dois.

Relatado: a referência sem laço nos três K; as trajetórias de g, |R₃| e C a cada 250 Myr; a fração de anéis travados; χ médio.

## Apostas (Claude, antes de rodar)

- **J1: 25 %.** A autoconsistência apara para baixo, mas não tem por que parar na faixa.
- **J2: 15 %.** O ponto fixo é degenerado.
- **J3: 35 %.** A borda fica em C ≈ 0,35–0,6; a faixa começa em 0,527.
- **J4: 40 %.** Se o laço achar a borda, deve ser a mesma em qualquer K; se não achar, não.
- **J5: 60 %.** Criar ordem a partir de uma memória vazia é possível em princípio nos dois laços.

## O que fecha

- **J4 passa:** o laço da criticidade leva o disco a um ponto que é dele, e não dos parâmetros. Se esse ponto cair na faixa (J3), a borda do travamento é compatível com 0,627 no modelo, com as ressalvas de sempre para a galáxia. Para a v0, é a primeira regra de auto-organização com um ponto próprio: uma memória que acha sozinha a borda entre seguir e se colar.
- **J2 reprova (esperado):** autoconsistência sozinha não define um nível. "A memória não guarda mais do que o disco sustenta" é condição, não alvo.
- **J5 reprova:** um dos laços cria ordem a partir de quase nada. Isso vira uma pergunta nova: o que ele cria, e quanto do ruído vira estrutura.
- **Todos reprovam:** neste modelo, aparar sem alvo não acontece. A estrutura vem da ordem inicial; a memória a conserva, e os laços só mudam a velocidade com que ela se perde.

Um julgamento por hipótese; sem emenda. Instrumento: teste38.py, escrito depois do commit desta predição.
