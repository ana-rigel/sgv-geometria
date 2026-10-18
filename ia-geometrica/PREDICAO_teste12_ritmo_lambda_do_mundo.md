# Predição do teste 12 (ritmo por regime com λ₁ perguntado ao mundo)

18/10/2026 · escrita antes de rodar · corrige o defeito 23 (e o 1) no teste 11, e só ele

## Pergunta

O teste 11 achou a forma certa de política (ritmo por regime: V +0,67 %, única com média positiva) sobre um registro lento demais para o ganho aparecer. **Com λ₁ escolhido na calibração pelo próprio mundo, o ritmo por regime, com a mesma fração de olhadas, deixa a memória mais perto do mundo do que o ritmo fixo?**

## O que muda e o que não muda

- **λ₁ pelo mundo.** Na janela de calibração [0, 2.000), olhando sempre, escolhe-se λ₁ na grade {0,05; 0,10; …; 0,95} que minimiza o erro de predição ‖x_t − R₁,t−1‖ (o mesmo nulo que ganhou o teste 1). Os andares 2–4 seguem com b = 10 a partir desse λ₁ (não entram na política; ficam para a régua e para a identidade). Régua, regime e ritmos são calibrados **sobre esse registro**. O mesmo λ₁ serve às três políticas (ritmo, periódico, sempre): o teste é da política, com o registro em pé de igualdade.
- **Tudo o mais igual ao teste 11:** mundo quente/frio, N = 8.000, 100 sementes, limiar de regime 0,5 na régua, afinação inteira de (p_q, p_f) com pré-filtro analítico e faixa 25 % ± 2 pp, medida em [4.000, 8.000), nulo a cada 4, teto olhar sempre, validade ± 3 pp em ≥ 95 sementes, critério do envelope.

## Apostas

- **Passar: 50 %.** A favor: com λ₁ ≈ 0,9 (o que o teste 1 achou para φ = 0,9) a memória copia o mundo a cada olhada e o erro entre olhadas cresce com o tempo sem olhar; aí olhar a cada 2 no quente e a cada 8 no frio faz diferença de verdade, e o ganho deve subir para a casa dos 5–10 %. Contra: o envelope inteiro acima de zero em 100 sementes é estrito, e sementes com blocos atípicos (um bloco quente longo na medida, poucos na afinação) podem dar V < 0; a leitura de regime numa olhada só erra às vezes.
- λ₁ escolhido ≥ 0,7 em ≥ 90 sementes (85 %).
- V média entre +4 % e +12 % (55 %); V > 0 em ≥ 90 sementes (60 %); par mais frequente com p_f ≥ 2 p_q (70 %).

## O que fecha

Passar: a v0 tem um ato que vale: o ritmo de olhar lido do regime, sobre um registro que acompanha o mundo. E fecha a conta do defeito 1: a herança de março segurou a política em quatro testes. Reprovar com V bem positiva: a política vale e o critério é mais duro que ela; fica. Reprovar com V ≈ 0: a informação de regime não se converte em erro menor nem com o registro certo, e a política de olhar da v0 precisa de outra ideia.
