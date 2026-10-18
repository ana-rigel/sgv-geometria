# Predição do teste 14 (saltos em cachos densos)

18/10/2026 · escrita antes de rodar · corrige o defeito 25 do teste 13, e só ele

## A conta por janela, feita antes

No teste 13 o cacho se renovava a cada salto com probabilidade 1/12 por passo durante 60 passos: a chance de 60 passos sem salto é (11/12)⁶⁰ ≈ 0,5 %, e um cacho só termina depois de ≈ 180 saltos, ≈ 2.000 passos. O "cacho" era um regime do tamanho da janela, e um começava a cada 2.000 passos. Nenhuma janela tinha vários; a afinação era sorteio.

Novo mundo: salto com probabilidade 1/300 fora de cacho; dentro, 1/20 por passo durante 30 passos após cada salto (renovando). Chance de 30 passos sem salto: (19/20)³⁰ ≈ 21 %, logo ≈ 4,7 saltos por cacho e ≈ 140 passos de cacho; intervalo entre cachos ≈ 300. **Por janela de 2.000 passos: ≈ 4,5 cachos, ≈ 21 saltos, ocupação ≈ 32 %.** Amplitude ±12 por coordenada; deriva φ = 0,9, σ = 1. N = 8.000, 100 sementes.

Teto do oráculo (sabe o cacho), por conta: olhar a cada 1 no cacho (32 % do orçamento… excede) → p_q = 2 (16 %) e p_f ≈ 8 (8,5 %): custo de salto cai de ≈ 2 passos de amplitude cheia (periódico 4) para ≈ 1 nos 70 % dos saltos que caem em cacho; o custo de deriva sobe um pouco fora. Como o custo de salto domina (amplitude 12, deriva ≈ 2,5), espero **V_orac entre +8 % e +20 %, com envelope acima de zero** (70 %).

## Instrumento e critério

Os do teste 13 sem mudança: λ₁ pelo mundo; régua de T₀ na calibração; regime com memória (ruptura ≥ 3 na régua liga "cacho" por H passos; H = mediana dos intervalos entre rupturas < 200 na calibração, em [10, 200]); afinação inteira de (p_q, p_f) com pré-filtro analítico pela ocupação da afinação; nulo a cada 4; teto olhar sempre; oráculo com o cacho verdadeiro e afinação própria; medida em [4.000, 8.000); V e V_orac; critério: envelope de V acima de zero, ≥ 95 válidas.

## Apostas

- **Passar: 40 %.** O teto agora existe (aposta acima). O que separa a v0 do oráculo é a régua como gatilho e o H aprendido: a régua calibrada com cachos dentro (defeito 6) tem escala alta, mas saltos de ±12 ainda passam de 3; H deve sair perto de 20 (o intervalo típico entre saltos de um cacho), menor que o cacho (140), e a v0 vai "desligar" o cacho cedo e religar no salto seguinte, o que custa uma olhada lenta por salto. Por isso espero que ela capture metade do oráculo.
- V média entre +3 % e +10 % (55 %); V > 0 em ≥ 85 sementes (55 %); v0 ≥ 50 % do ganho do oráculo (50 %); ≥ 95 válidas (65 %).

## O que fecha

Passar: o ato da v0 vale, e vale onde há reflexividade. Reprovar com oráculo alto e estável e v0 abaixo: a forma vale e o gatilho (régua + H) é o que falta; o próximo conserto é o gatilho. Reprovar com oráculo baixo: a conta por janela ainda está errada, e o erro é meu de novo, registrado.
