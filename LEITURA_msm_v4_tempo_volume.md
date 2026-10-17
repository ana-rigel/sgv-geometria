# Leitura: MSM no relógio de volume (v4), jun–jul e ago–set/2026 — INCONCLUSIVO

**Predição:** PREDICAO_msm_v4_tempo_volume.md + Emenda 1, registradas antes de cada rodada. **Rodadas:** Actions 38997729029 (reprovou validação; logs *_INCONCLUSIVO_emenda1.log) e 39000509434 (Emenda 1; reprovou de novo). Pela cláusula da Emenda 1, **a v4 encerra INCONCLUSIVA**: o real não recebe classe.

## Por que o instrumento reprovou

| Validação | jun–jul | ago–set |
|---|---|---|
| sintético k = 2 (2, 17 barras) | k* = 2 | k* = 2 |
| sintético k = 3 (2, 17, 145 barras) | k* = 4 (BIC k3/k4/k5: −282439/−282442/−282442) | k* = 5 (−305818/−305821/−305821) |

Com ~26 mil barras (contra 87 mil minutos), as diferenças de BIC entre k = 3, 4 e 5 ficam em ±3, abaixo do ruído do otimizador: o instrumento não resolve k ≥ 3 nesta amostra. É limite de amostra, não de modelo; a mesma validação passou com 87 mil observações (v2, v3).

## Descritivos (registrados como observação, sem veredito)

| | jun–jul | ago–set |
|---|---|---|
| barras | 25.658 (3,4 min em média; 24 % de 1 min) | 26.679 (3,3 min; 24 %) |
| ν no relógio de volume (k = 5) | **10,9** | **12,9** |
| ν no relógio de tempo (v2, k = 4) | 6,3 | 2,75 |
| ΔBIC por degrau (real) | 519 / 228 / 38 / 34 | 715 / 211 / 117 / 27 |
| ΔBIC por degrau (v2, tempo, 87 mil obs.) | 5192 / 1828 / 908 | 7969 / 4241 / 2456 |

Duas observações, com a ressalva de que nada aqui foi validado:

1. **A cauda afina muito no relógio de volume** (ν de 6,3 → 10,9 e de 2,75 → 12,9). É a previsão de Clark (1973) e Ané–Geman (2000): boa parte da cauda gorda de 1 minuto é ritmo de negociação; medida em volume, a inovação se aproxima da gaussiana. Era a aposta de 70 % da predição e teria acertado nos dois períodos.
2. **Os ganhos de BIC além de k = 3 encolhem** (dezenas, contra centenas a milhares no tempo), mas com um terço das observações e um instrumento que não resolve k ≥ 3, isso não distingue "escada encolheu" de "amostra curta".

## O que seria preciso

Barras de volume mais finas (dados de trades ou klines de segundos, para quebrar o piso de 1 minuto) e um período mais longo, para ter ≥ 80 mil barras com o mesmo V\*. Não está pedido; fica como item aberto.

Em nenhum caso há direção, previsão ou lucro.
