# Predição do teste 11 (ritmo por regime)

18/10/2026 · escrita antes de rodar · corrige os defeitos 21 e 22 do teste 10, e só eles

## Pergunta

No teste 10 a tensão mostrou saber o regime (b_n ≈ 0,65 por 16 passos) e a política de limiar perdeu porque concentra olhadas em rajada. **Uma política que escolhe o ritmo de olhar pelo regime lido, com a mesma fração de olhadas, deixa a memória mais perto do mundo do que um ritmo fixo?**

## O que muda e o que não muda

- **Política de ritmo.** A cada olhada a v0 lê T₀ na régua e decide o regime: quente se T₀ na régua ≥ 0,5, frio caso contrário (limiar fixado antes; na régua, 0 é a mediana da calibração e a escala é q99,5 ÷ 3, e o quente deste mundo tem tensão ≈ 3 vezes a do frio). O regime lido fixa o **período** até a próxima olhada: p_q no quente, p_f no frio. Entre olhadas ela não decide nada: espera o período. Nada de limiar contínuo.
- **Afinação por inteiros.** (p_q, p_f) ∈ {1 … 16}²; na janela de afinação [2.000, 4.000) ficam os pares com fração de olhadas em 25 % ± 2 pp, e entre eles o de menor erro de predição nessa janela. Corrige o defeito 22: a fração é discreta e a busca também.
- **Tudo o mais igual ao teste 10:** mundo quente/frio (φ = 0,9; σ = 1 / 3; blocos geométricos de média 200), N = 8.000, 100 sementes, k = 4, λ₁ = 0,15, b = 10, régua de T₀ em [0, 2.000) olhando sempre, medida em [4.000, 8.000), erro de predição ‖x_t − R₁,t−1‖, nulo periódico a cada 4, teto olhar sempre, V = 1 − e_v0 / e_periódico, validade 25 % ± 3 pp em ≥ 95 sementes.

## Critério (um julgamento)

O dos testes 2, 7 e 10: envelope de V acima de zero nas sementes válidas, e ≥ 95 válidas.

## Apostas

- **Passar: 60 %.** A favor: a informação existe (teste 10), e o ritmo a usa sem concentrar; a afinação inteira deve acertar a faixa. Contra: o critério é o envelope inteiro, e um bloco quente mal lido (a olhada caiu num instante calmo do quente) custa caro numa semente; e λ₁ = 0,15 faz o registro lento o bastante para que mesmo o ritmo certo renda pouco.
- V média entre +2 % e +8 % (55 %); V > 0 em ≥ 90 sementes (70 %); ≥ 95 válidas (80 %).
- (p_q, p_f) mais frequente com p_f ≥ 2 p_q (85 %).

## O que fecha

Passar: a v0 tem, pela primeira vez, um ato que vale alguma coisa: o ritmo de olhar lido do regime. Reprovar com V > 0 na média: a forma está certa e o envelope é estrito; fica reprovado e a leitura dá o tamanho. Reprovar com V ≤ 0: nem o ritmo aproveita a informação, e o gargalo é o registro lento (λ₁), não a política; aí a pergunta volta ao teste 1.
