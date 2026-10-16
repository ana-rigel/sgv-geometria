# Leitura: o espectro de escala ζ(q) do BTC (jun–jul e ago–set/2026)

**Predição:** PREDICAO_multifractal.md, congelada em 5ddfb17 antes de rodar. Um julgamento por período.

**Resultados:** resultados/multifractal_{junjul,agoset}.json (jun–jul local; ago–set Actions run 38973183114, agosto e setembro conferidos por SHA-256; outubro não lido).

## Números (ajuste até 240 min; 87.839 retornos de 1 min por período)

| | jun–jul | ago–set |
|---|---|---|
| κ = 2ζ(2) − ζ(4), real | +0,240 | +0,231 |
| κ, envelope M (5 réplicas) | −0,145 a +0,177 | −0,013 a +0,298 |
| κ, envelope embaralhado (5 permutações) | +0,290 a +0,334 | +0,489 a +0,579 |
| H = ζ(2)/2, real | 0,482 | 0,496 |
| κ até 1440 min, real | +0,264 | +0,254 |
| **Classe registrada** | monofractal dentro do ruído | monofractal dentro do ruído |

ζ(q) real, jun–jul: 0,25 · 0,50 · 0,73 · 0,96 · 1,18 · 1,37 · 1,69 para q = 0,5 … 4 (reta qH daria 1,93 em q = 4). Ago–set: 0,25 · 0,49 · 0,74 · 0,99 · 1,23 · 1,44 · 1,75 (reta: 1,98). A curva do real é côncava e estável entre os períodos.

## Veredito pelo critério registrado

**"Monofractal dentro do ruído" nos dois períodos**, porque κ_real ficou abaixo do máximo do embaralhado. O critério vale como foi escrito; a leitura abaixo diz por que ele mede outra coisa do que a predição supôs.

## O que o resultado revelou sobre o instrumento (defeito de desenho, registrado, não consertado)

A predição tratou a série embaralhada como "piso monofractal, κ ≈ 0". Errado: **retornos i.i.d. com caudas gordas produzem κ grande sozinhos.** Em τ = 1 min a distribuição tem curtose alta; ao somar 240 retornos independentes ela vai para a gaussiana (teorema central do limite), então ⟨|r|⁴⟩ cresce com τ mais devagar que a reta e ζ(4) cai. O embaralhado conserva as caudas de 1 min e destrói o agrupamento, e deu κ 0,29–0,58, o maior dos três. Logo κ, como definido, mede **principalmente a gordura das caudas de 1 min e a velocidade de sua gaussianização**, não a cascata de volatilidade. A predição apostou 90 % em "real acima do embaralhado"; saiu o contrário nos dois períodos.

Lido com esse defeito à vista, o ordenamento é informativo e repetiu nos dois períodos:

- **embaralhado > real:** o agrupamento de volatilidade *reduz* a concavidade aparente em vez de aumentá-la, porque mantém os retornos agregados com cauda gorda por mais tempo (um surto de 4 h soma minutos gordos correlacionados, que não gaussianizam). A multifractalidade aparente do BTC de 1 min a 4 h é, nestes dados, **cauda gorda em escala curta mais TCL**, com o agrupamento puxando para o lado monofractal.
- **real > M (jun–jul fora do envelope; ago–set dentro, na parte alta):** o M tem inovações gaussianas condicionais; suas caudas de 1 min são finas e sua gaussianização, rápida. O M reproduz o agrupamento e não reproduz as caudas de 1 min. É o mesmo diagnóstico do R (borda real acima do M) dito pelo espectro.
- H ≈ 0,48–0,50 no real, nos dois períodos: escala difusiva no corpo, como previsto (aposta de 75 %, acertada).

## O que isto fecha e o que não

- Fecha: a concavidade de ζ(q) do BTC entre 1 min e 4 h não exige cascata; caudas gordas i.i.d. produzem mais concavidade do que o real tem. "Multifractal" aqui é uma descrição da cauda, não de uma hierarquia de escalas. Compatível com a leitura do v3 (duas memórias, não infinitas).
- Não fecha: o instrumento certo para separar cascata de cauda compararia o real com uma série de **mesmas caudas de 1 min e sem agrupamento** (o embaralhado já é isso) **e** com uma de **mesmo agrupamento e caudas gaussianas** (o M já é isso), usando uma medida insensível à curtose marginal (por exemplo, o espectro dos retornos padronizados pela volatilidade local, ou a função de partição com q ≤ 2 apenas). Isso seria uma v2 com predição própria; não está pedida e não será rodada por iniciativa minha.
- Em nenhum caso há direção, previsão ou lucro.

## Apostas

| Aposta | Prob. | Saiu |
|---|---|---|
| κ_real > máx embaralhado, dois períodos | 90 % | **não** (o contrário, dois períodos) |
| "Como o M", dois períodos | 45 % | não |
| "Além do M", dois períodos | 35 % | não (classe formal: monofractal) |
| H entre 0,45 e 0,55 | 75 % | sim |
| κ_real entre 0,05 e 0,30 | 65 % | sim (0,24 e 0,23) |

O erro de 90 % é o maior erro de aposta das rodadas de 16/10 e fica registrado como tal: eu não sabia que caudas i.i.d. bastam para uma ζ(q) côncava nesta amostra. Agora sei, e o repositório também.
