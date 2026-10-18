# Leitura do teste 12 (ritmo por regime com λ₁ do mundo) — REPROVADO (V +1,2 % na média)

**Predição:** PREDICAO_teste12_ritmo_lambda_do_mundo.md (4ef3ce1), antes de rodar. **Resultado:** resultados_teste12.json. Um julgamento; sem emenda.

| | erro de predição médio (medida) |
|---|---|
| teto: olhar sempre | 2,63 |
| nulo: a cada 4 | 3,86 |
| v0: ritmo por regime, λ₁ do mundo | 3,81 |

λ₁ escolhido: 0,94 em média, ≥ 0,7 em 100 sementes (o registro copia o mundo, como no teste 1). V média **+1,19 %**, envelope −2,8 % a +5,5 %, positiva em 56 de 95 válidas; par mais frequente (3, 5). Critério: (a) válidas ≥ 95: sim (95, no limite); (b) envelope acima de zero: **não**. **Reprovado.** Apostas: 50 % em passar, errada; λ₁ ≥ 0,7 em ≥ 90, certa; V entre +4 e +12 %, errada; V > 0 em ≥ 90, errada; p_f ≥ 2 p_q, errada.

## O que o resultado diz

O registro certo dobrou o ganho (0,67 % → 1,19 %) e não o levou à casa dos 5–10 % que a predição esperava. Fazendo a conta que eu devia ter feito antes de apostar: numa deriva φ = 0,9, o erro de uma memória congelada por n passos cresce como √(2(1 − 0,9ⁿ)), isto é, rápido no começo e devagar depois (0,45 em n = 1; 0,66 em n = 4; 0,83 em n = 8). O custo médio de olhar a cada p passos é a média disso até p; com ocupação ½/½ e σ quente = 3 σ frio, o periódico (4, 4) custa ∝ 1,32 e o melhor ritmo na faixa de 25 %, (3, 5), custa 1,255: **teto analítico de ≈ 5 %**, e (3, 6), que também cabe, dá 3,5 %. A política achou 1,2 %: metade do teto, o resto perdido em leituras erradas de regime (uma olhada só decide o ritmo até a próxima) e na afinação em janela curta.

A conclusão é sobre o mundo, não sobre a política: **saber o momento certo de olhar vale pouco quando o erro de não olhar cresce como raiz.** Em mundos de deriva, lembrar envelhece devagar, e redistribuir olhadas rende pouco por construção. O ato da v0 só pode valer muito em mundos onde não olhar custa de uma vez: saltos (o mundo do teste 3), onde cada passo sem olhar depois de um salto custa a amplitude inteira. Isso fecha a família "deriva" para a política: três mundos (deriva, deriva com regimes, com λ₁ certo), sempre ≤ 1,2 %, sempre abaixo de um teto que a própria estrutura do mundo impõe.

## O que fecha e o que não

- Fecha: em mundos de deriva, com ou sem regimes, com registro herdado ou do mundo, a política de olhar da v0 rende no máximo ≈ 1 % sobre o periódico, contra um teto analítico de ≈ 5 %. A forma (ritmo por regime) é a certa; o lugar é o errado.
- Não fecha: a política num mundo de saltos sobre deriva, onde o custo de não olhar é uma amplitude e não uma raiz, com o regime lido na régua (teste 3 mostrou que a régua é silenciosa e só vê saltos grandes: o teste de política lá é também um teste da régua como gatilho).

## Para a lista de defeitos de desenho do projeto

24. Quatro testes de política (2, 7, 10, 11) e este em mundos onde o teto da política é ≈ 5 %: o teto devia ter sido calculado antes do primeiro, e o mundo escolhido para que valesse a pena medir.

Doze testes, doze reprovações, vinte e quatro defeitos.
