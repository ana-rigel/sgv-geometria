# E-FLX-02 — resultado (13/10/2026)

Pré-registro `PREREGISTRO_E-FLX-02.md` (ad4261c) antes do código; código e workflow antes dos resultados; execução no Actions (run 38503779969), 10 dias de jun–jul/2026, latência 250 ms, custo 20 bp por ida e volta. Intervalos: bootstrap por dia.

## R1 — rompimento só com fluxo a favor

**O filtro não tem o que filtrar.** Em 96 % dos rompimentos (1.350 de máxima/mínima de 15 min, 619 de 60 min) o fluxo dos 5 s anteriores já está a favor, com mediana de 0,94 (quase todo o volume agressor no sentido do rompimento). É mecânico: o preço de negócio só imprime nova máxima quando alguém compra a mercado e consome o ask. O "rompimento por vácuo, sem agressão" existe em 4 % dos casos (53 e 23 eventos).

| L = 60 min | a favor (n = 596) | contra (n = 23) | diferença (IC 95 %) |
|---|---|---|---|
| 5 s | +0,44 bp | +0,14 bp | +0,30 (−0,71; +1,20) |
| 60 s | +0,58 | +2,57 | −1,99 (−5,24; +0,98) |
| 15 min | +1,22 | +11,05 | −9,83 (−22,1; +0,9) |
| 60 min | −0,01 | +5,61 | −5,62 (−17,3; +6,1) |
| rompimento falso em 5 min | 46,5 % | 47,8 % | −1,4 pp (−23,5; +17,4) |

Com L = 15 min o quadro é o mesmo. Nenhuma diferença tem IC fora do zero; as estimativas pontuais, quando grandes, são **contra** o filtro (o grupo "contra" anda mais), mas com 23–53 eventos isso é ruído. A estratégia de rompimento em si tem vantagem bruta de +0,2 a +1,6 bp: líquido de −18 a −20 bp, com ou sem filtro.

Apostas: líquido negativo nos dois grupos — acertou. Diferença ≥ 60 s com IC contendo 0 — acertou, mas as estimativas pontuais passaram de 1 bp por falta de eventos "contra". Fluxo a favor melhor a 5 s — inconclusivo (L60 +0,30; L15 −0,56, ambos com IC no zero). Rompimento falso < 5 pp — acertou em L60, não em L15 (−11,6 pp, IC −24,9; +2,3).

## R3 — abortar se não andou em 15–30 s e o fluxo sumiu

- Aborta-se 24–35 % das operações.
- A condição de aborto **não prevê** o resto da operação: |ρ| ≤ 0,03 em todas as 28 combinações.
- Sem vantagem (q = 0,50): abortar = segurar (diferenças de −0,1 a +0,2 bp).
- Com vantagem plantada, abortar **perde sempre**, com IC inteiro abaixo de zero:

| H | vantagem plantada | segurar | abortar (τ = 15 s) | perda |
|---|---|---|---|---|
| 15 min, q = 0,60 | +3,9 bp | −16,1 | −17,2 | −1,0 (−1,3; −0,8) |
| 15 min, q = 0,75 | +8,0 | −12,0 | −14,5 | −2,5 (−3,1; −2,0) |
| 60 min, q = 0,60 | +7,4 | −12,6 | −15,1 | −2,5 (−3,5; −1,5) |
| 60 min, q = 0,75 | +16,1 | −3,9 | −9,6 | −5,8 (−7,4; −4,5) |

A perda é ≈ a fração abortada × a vantagem (26–36 % da vantagem): o aborto joga fora a vantagem das operações cortadas sem escolher as piores. V1 e V2 dão o mesmo número — a tese de horas não se revela nos primeiros segundos. Sobre rompimentos reais (sem vantagem), abortar ≈ segurar.

Apostas: condição não prevê o resto — acertou (|ρ| ≤ 0,03; o limite registrado era 0,02, passou por pouco em 4 combinações). q = 0,50 sem diferença — acertou. Abortar perde com vantagem — acertou; tamanho ≈ 1/3, não os ~40 % apostados; V1 perder menos que V2 — errou (iguais).

## Leitura

As duas regras não funcionam. A R1 não seleciona nada, porque rompimento e fluxo a favor são quase a mesma coisa nos dados de negócio. A R3 corta, ao acaso, cerca de um terço das operações e com elas um terço da vantagem da estratégia. O único uso do fluxo de segundos que sobrevive é o do E-FLX-01: escolher o segundo da execução, valendo 0,2–0,4 bp.
