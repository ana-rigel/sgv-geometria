# Predição do teste 36 (ela aprende com o erro?)

20/10/2026 · escrita antes de rodar · entradas das águas de teste35.py, sem mudança · Ana Rigel

## De onde vem

Da conversa de 20/10, depois do teste 35. A Ana corrigiu a pergunta: **não é se a v0 faz melhor que outra coisa, é se ela aprende com o erro.** A v0 de hoje não aprende, por construção: nenhuma linha do código usa o erro para mudar alguma coisa. Os λ são fixos, a régua é calibrada uma vez, e o ⋄ dos testes 32 e 33 aprende o normal, mas faria a mesma conta se estivesse errando tudo. O teste tem duas partes: dar à v0 um laço de erro e verificar que é o erro que muda a forma dela.

O laço escolhido é o do **relógio v1** (Experimento 1 do Teste B), que aprendia com os **eventos**. A leitura do teste 35 apontou para ele: a entrada das águas atrasou ≈ 13 dias em 2018–2025, e só um relógio que aprendesse com as entradas vividas poderia acompanhar isso.

Nenhum julgamento deste teste compara com o calendário ou com outro método.

## O laço

O relógio guarda μ, o dia do ano em que espera a entrada das águas. Antes de cada estação, a previsão é μ. Quando a entrada acontece no dia o, o erro é e = o − μ, e o relógio corrige

  μ ← μ + η · e,  η = 0,3 (fixado aqui, um valor só).

É a menor organização que aprende com o erro: ela muda a própria forma (μ) pelo que errou, e só por isso.

## Mundos

**Sintéticos (100 por condição, semente 36):** 24 estações. A entrada é o = 280 + ε (+ Δ a partir da 13ª estação, quando houver degrau). Os ε são sorteados com reposição das anomalias reais de 2010–2017: a entrada de cada ano menos a média do lugar, nos seis lugares de MT do teste 35 (48 valores). O ruído é o do mundo real; a mudança é conhecida.

| condição | semente μ₀ | degrau Δ | laço |
|---|---|---|---|
| A, semente errada | 250 (−30 d) | 0 | e = o − μ |
| B, degrau | 280 | +20 d da 13ª estação em diante | e = o − μ |
| C, sem mudança | 280 | 0 | e = o − μ |
| D, ordem embaralhada | 280 | o mesmo mundo de B | as entradas de B em ordem sorteada, e = o_π − μ |
| E, erro invertido | 280 | o mesmo mundo de B | μ ← μ − η e |

p_y é a previsão para a estação y (μ antes de ver a entrada y). No degrau: pré = média de p₁₁, p₁₂, p₁₃ (antes de qualquer entrada deslocada); pós = média de p₁₇, p₁₈, p₁₉ (depois de 4 a 6 entradas deslocadas).

**Real:** os seis lugares do teste 35, mesma definição de entrada. Semente μ₀ = média das entradas de 2010–2017 do lugar (o calendário do teste 35); o laço aprende com 2018–2025, oito entradas.

## Conta prévia (σ ≈ 15–20 dias, o espalhamento das entradas)

- Sem ruído, o laço remove a fração 1 − 0,7ⁿ de um erro de semente em n estações: 88 % em 6.
- Com ruído, μ fica tremendo em torno do valor certo com desvio σ·√(η/(2 − η)) ≈ 0,42σ ≈ 6–8 dias.
- No degrau, pós − pré tem média 20 · (1 − média de 0,7⁴, 0,7⁵, 0,7⁶) ≈ 16,6 d e desvio ≈ 8 d.
- No real, se o atraso de ≈ 13 d for estável, μ anda 13 · (1 − 0,7⁸) ≈ 12 d em oito entradas, com desvio ≈ 8 d por lugar.
- Na ordem embaralhada, o relógio vê as mesmas entradas, mas o degrau se espalha pelo tempo: pós − pré tem média ≈ 0 e desvio ≈ 8–9 d.
- Com o erro invertido, μ − o cresce 1,3 vez por estação: o laço diverge, e no degrau anda para o lado errado.

## Critérios

**J1, aprende (A):** depois de 6 entradas, a média nos mundos de |p₇ − 280| ≤ **10 d**, e |p₇ − 280| < 30 d (mais perto que a semente) em **≥ 90 de 100**.

**J2, readapta (B):** pós − pré ≥ **10 d** (metade do degrau) em **≥ 80 de 100**.

**J3, readapta no mundo real:** μ depois da entrada de 2025 menos μ₀ ≥ **+6 d** (metade do atraso) em **≥ 4 dos 6** lugares.

**J4, não aprende ruído (C):** a média nos mundos de (média de p₂₂, p₂₃, p₂₄ − 280) fica entre **−3 e +3 d**, e |média de p₂₂–p₂₄ − 280| < 15 d em **≥ 95 de 100**.

**J5, depende do erro e da ordem (D e E):** na ordem embaralhada, pós − pré ≥ 10 d em **≤ 20 de 100** (contra ≥ 80 de B); com o erro invertido, pós − pré < 0 em **≥ 90 de 100**.

Relatado: as curvas de erro por estação (média nos mundos) de A, B, C, D e E; os mesmos números para η ∈ {0,1; 0,2; 0,5}; no real, μ ano a ano por lugar e o erro de cada previsão.

## Apostas (Claude, antes de rodar)

- **J1: 95 %.** É aritmética com ruído.
- **J2: 80 %.** Pela conta, P(pós − pré ≥ 10 d) ≈ 0,8 por mundo: a aposta está na beira.
- **J3: 55 %.** Oito entradas e σ real ≈ 20 d; o atraso do teste 35 pode não ser estável em todos os lugares.
- **J4: 85 %.**
- **J5: 80 %.** A parte invertida é quase certa; a embaralhada fica perto de 10–15 de 100.

## O que fecha

- **J1, J2, J4 e J5 passam:** o laço está ligado do jeito certo e aprende com o erro, não com outra coisa. A v0 ganha a primeira peça de organização que muda a própria forma pelo que errou. O J3 diz se oito anos do mundo real bastam para ver isso.
- **J3 reprova com os outros passando:** o laço funciona, mas no mundo real oito eventos com σ ≈ 20 d não bastam para separar o atraso do ruído. Aprender com eventos anuais é lento por natureza; o próximo passo pede eventos mais frequentes (a régua da v0 dispara rupturas muitas vezes por ano).
- **J5 reprova:** o que parecia aprendizado não depende da ordem do erro; o laço está mal posto.

Isto **não** mostra que a v0 aprende a sua forma inteira (λ, K, a régua). É o primeiro laço, o menor possível. Um julgamento por hipótese; sem emenda. Instrumento: teste36.py, escrito depois do commit desta predição.
