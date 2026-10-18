# Predição do teste 13 (ritmo por regime num mundo de saltos em cachos)

18/10/2026 · escrita antes de rodar · muda o mundo da política (defeito 24), e só isso

## Pergunta

Em mundos de deriva a política de olhar tem teto de ≈ 5 % e a v0 achou 1,2 %. O ato de olhar só pode valer onde não olhar custa de uma vez. **Num mundo de saltos que vêm em cachos, o ritmo por regime, lido na régua, com a mesma fração de olhadas, deixa a memória mais perto do mundo do que o ritmo fixo?**

## Por que "em cachos" e não saltos soltos

Saltos sem memória (geométricos, como no teste 3) não têm momento certo: nenhuma política bate o periódico, porque o próximo salto é igualmente provável em qualquer passo. Isso é o teto zero, e seria repetir o defeito 24. Saltos em cachos têm: depois de um salto, outros vêm; quem viu um deve olhar mais por um tempo. É o parente mais simples do que o mercado tem (Hawkes: a reflexividade do MSM e da borda do SGV).

## Mundo

"Saltos em cachos": deriva φ = 0,9 (σ = 1) mais teleportes de amplitude uniforme ±12 por coordenada. Probabilidade de salto por passo: 1/2.000 fora de cacho; 1/12 nos 60 passos seguintes a um salto (cada salto renova os 60). N = 8.000, 100 sementes, começa fora de cacho.

## Instrumento

- λ₁ pelo mundo (grade, como no teste 12); andares 2–4 com b = 10; régua de T₀ na calibração [0, 2.000) olhando sempre.
- **Regime com memória.** A cada olhada a v0 lê T₀ na régua. Se ≥ 3 (ruptura na régua da v0), entra em "cacho" por H passos; H é aprendido na calibração como a mediana do intervalo entre leituras de ruptura consecutivas que distam menos de 200 passos (se nenhuma, H = 60), limitado a [10, 200]. Em cacho o ritmo é p_q; fora, p_f. Sem limiar contínuo.
- Afinação inteira de (p_q, p_f) ∈ {1 … 16}² em [2.000, 4.000) para 25 % ± 2 pp com pré-filtro analítico (ocupação de cacho estimada na própria afinação), medida em [4.000, 8.000). Validade ± 3 pp em ≥ 95 sementes.
- Nulo: periódico a cada 4. Teto 1: olhar sempre. **Teto 2 (oráculo): a mesma política de ritmo com o estado de cacho verdadeiro do mundo**, mesmo orçamento; é o máximo que a forma "ritmo por regime" pode render neste mundo, e a distância entre a v0 e o oráculo é o que a régua perde como gatilho.
- Erro de predição ‖x_t − R₁,t−1‖; V = 1 − e_v0 / e_periódico; V_orac idem para o oráculo.

## Critério (um julgamento)

Envelope de V acima de zero nas sementes válidas, e ≥ 95 válidas. O oráculo não entra no critério; entra na leitura.

## Apostas

- **Teto do oráculo, calculado antes:** com ≈ 60 % dos saltos dentro de cachos que ocupam ≈ 10–15 % do tempo, p_q = 1 ou 2 no cacho e p_f ≈ 5 fora, o custo dos saltos cai de ≈ 2 passos de amplitude cheia (periódico) para ≈ 0,5–1 no cacho; como o custo de salto domina o erro (amplitude 12 contra deriva de 2–3), espero **V_orac entre +10 % e +25 %** (60 %).
- **Passar: 45 %.** A favor: há teto de verdade, e a régua vê saltos de ±12 (muito acima da escala q99,5 ÷ 3 de um mundo quase sem saltos na calibração). Contra: a régua é calibrada **com** os saltos da calibração dentro (defeito 6), e se cair um cacho em [0, 2.000) a escala sobe e a ruptura vira rara; H aprendido numa calibração com poucos cachos é ruidoso; e o envelope inteiro em 100 sementes é estrito num mundo onde uma semente pode ter um cacho longo na medida e nenhum na afinação.
- V média entre +4 % e +15 % (55 %); V > 0 em ≥ 85 sementes (60 %); v0 captura ≥ 50 % do ganho do oráculo (50 %).

## O que fecha

Passar: a v0 tem um ato que vale, e vale onde o mundo tem reflexividade: o lugar do mercado. Reprovar com V > 0 e oráculo alto: a forma vale e a régua como gatilho a segura (teste 3 de novo); o próximo conserto é a régua, não a política. Reprovar com oráculo baixo: o mundo não tinha o teto que eu calculei, e o erro é meu, de conta, registrado.
