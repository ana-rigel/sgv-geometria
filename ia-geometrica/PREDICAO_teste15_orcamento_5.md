# Predição do teste 15 (ritmo por regime com orçamento de 5 %)

18/10/2026 · escrita antes de rodar · corrige o defeito 26 do teste 14, e só ele · último teste da linha de política

## Pergunta

Com 25 % de olhadas o periódico já erra só 50 % mais que olhar sempre, e toda política disputa uma fração disso: teto ≈ 2 % no melhor mundo (teste 14). **Com 5 % de olhadas, no mesmo mundo de cachos densos, o ritmo por regime lido na régua deixa a memória mais perto do mundo do que olhar a cada 20?**

## A conta por janela, antes

Mundo do teste 14 (49 saltos por janela de medida, ocupação de cacho ≈ 19 %, 79 % dos saltos em cacho). Periódico a cada 20: atraso médio até a próxima olhada ≈ 10 passos, a amplitude cheia (≈ 9) por salto: custo de salto ≈ 49 × 10 × 9 / 4.000 ≈ 1,1 por passo; custo de deriva com memória de até 20 passos ≈ 2,5–3 por passo. Fatia do salto no erro: ≈ 25–30 %, três vezes a do teste 14. O orçamento é apertado: 0,19/p_q + 0,81/p_f = 0,05 obriga, por exemplo, (4, 60) ou (5, 50); no cacho o atraso cai de 10 para 2, fora sobe de 10 para 25–30. Custo de salto com (4, 60): 0,79 × 2 + 0,21 × 30 ≈ 7,9 contra 10: 21 % de economia na fatia de 25–30 %: **teto do oráculo ≈ +5 a +8 %**, mais o que a deriva perder fora do cacho (que é contra). Aposto V_orac entre +3 % e +9 % (55 %), com envelope cruzando zero (60 %).

## Instrumento

O do teste 14 com: alvo de 5 % ± 0,5 pp na afinação (validade ± 1 pp em ≥ 95 sementes); nulo periódico a cada 20; grade p_q ∈ {1 … 20}, p_f ∈ {10, 12, … , 120}, pré-filtro analítico ± 1,5 pp pela ocupação da afinação; λ₁ pelo mundo; régua e H como antes; medida em [4.000, 8.000). Oráculo com o cacho verdadeiro e afinação própria.

## Critério (um julgamento)

Envelope de V acima de zero nas sementes válidas, ≥ 95 válidas.

## Apostas

- **Passar: 30 %.** O teto existe e é maior, mas o envelope inteiro acima de zero em 100 sementes com 49 saltos por janela é exigente; e com 5 % de olhadas a v0 lê a régua 200 vezes por janela, vendo um salto de ±12 só se a olhada cair depois dele e antes de o cacho acabar: o H de 22 passos aprendido no 25 % não serve aqui (com olhadas a cada 60 fora do cacho, a v0 raramente **vê** o começo do cacho a tempo). Espero que a v0 capture menos de metade do oráculo (60 %).
- V média entre +1 % e +5 % (50 %).
- **Cláusula de fechamento, escrita antes:** se V_orac médio < 5 %, a linha de política fecha, e a v0 fica registrada como um observador cujo ato de olhar vale pouco em todos os mundos testados, por estrutura dos mundos, não da política.

## O que fecha

Passar: o ato vale quando olhar é raro, e a política de ritmo é a forma. Reprovar com oráculo ≥ 5 % e v0 abaixo: a forma vale e o gatilho não vê o cacho a tempo com poucas olhadas; é o limite de um observador que só sabe do mundo quando paga. Reprovar com oráculo < 5 %: a linha fecha pela cláusula.
