# Leitura: a nuvem do cubo é torta? (jun–jul e ago–set/2026)

**Predição:** PREDICAO_assimetria_nuvem.md, congelada em a0c1c45 antes de rodar. **Uma tentativa**, como pedido: um julgamento por período, sem segunda rodada.

**Resultados:** resultados/assimetria_nuvem_{junjul,agoset}.json (jun–jul rodado localmente; ago–set pelo Actions, run 38961368892, com agosto e setembro conferidos por SHA-256; outubro não lido).

## Classes (critério registrado: g₁ real fora do envelope das 5 réplicas M em ≥ 2/3 das semanas; "torta" exige o mesmo sinal)

| Eixo | jun–jul (9 semanas) | ago–set (9 semanas) | Repete? |
|---|---|---|---|
| E_norm | simétrica dentro do ruído (fora 3/9) | simétrica dentro do ruído (fora 5/9) | sim: simétrica |
| jerk | **torta sem lado** (fora 6/9) | simétrica dentro do ruído (fora 4/9) | não |
| memory_flux | simétrica dentro do ruído (fora 5/9) | **torta sem lado** (fora 6/9) | não |

**Veredito da exploração:** nenhum eixo é "torta" (mesmo lado) em período algum; as duas excursões "sem lado" não se repetem no mesmo eixo. Pelo critério registrado, **a nuvem é simétrica dentro do que o ruído permite**. A casca HDR50, simétrica por construção, não esconde um terceiro momento com lado.

## Descritivo (medianas semanais)

| | jun–jul real | jun–jul M | ago–set real | ago–set M |
|---|---|---|---|---|
| g₁ E_norm | +0,16 | +0,03 | +0,70 | −0,26 |
| g₁ jerk | −0,06 | −0,02 | +0,09 | −0,06 |
| g₁ memory_flux | +0,10 | +0,03 | −0,08 | 0,00 |
| p⁺ borda E_norm | 0,54 | 0,49 | 0,49 | 0,50 |
| p⁺ borda jerk | 0,51 | 0,49 | 0,49 | 0,51 |
| p⁺ borda memory_flux | 0,57 | 0,52 | 0,46 | 0,52 |

- A fração positiva na borda fica entre 0,46 e 0,57 nos dois períodos, com sinal que troca entre jun–jul e ago–set. Não há lado.
- A nuvem quente (septil superior de w; a predição disse "tercil", o código usa o último corte de NFATIAS = 7) **não** é mais torta que a nuvem inteira: |g₁| quente ≤ |g₁| total em todos os eixos e períodos.
- O envelope M de jerk é estreito em jun–jul (±0,05 a ±0,2) e mais largo em ago–set; a excursão de jun–jul diz mais sobre a largura do envelope que sobre o real. Limitação do instrumento, registrada.
- g₁ semanal de E_norm varia de −2,0 a +4,4 no real e de −5,2 a +3,0 no M: a assimetria de E_norm numa semana é a tendência daquela semana, e o M a reproduz porque herda o caminho de volatilidade e tem AR(1) nos retornos. Como previsto na predição, isso é "torta porque subiu", não informação.

## Apostas

| Aposta | Prob. | Saiu |
|---|---|---|
| E_norm simétrica nos dois períodos | 60 % | sim |
| jerk simétrica nos dois períodos | 75 % | **não** (jun–jul: torta sem lado) |
| memory_flux simétrica nos dois períodos | 55 % | **não** (ago–set: torta sem lado) |
| Algum eixo torta, mesmo lado, dois períodos | 15 % | não (acerto) |
| Nuvem quente mais torta que a fria | 50 % | não |

Dois erros de confiança nas apostas individuais; o resultado agregado (nada com lado) foi o apostado.

## O que isto fecha e o que não

- Fecha a pergunta "a casca simétrica esconde um acúmulo de um lado?": não, dentro do ruído do M, em dois períodos.
- Não testa direção. "Torta antes de subir" continuaria exigindo pré-registro próprio (dezembro, dados de novembro). Nenhum número daqui vira indicador de momentum.
- Não haverá segunda tentativa desta pergunta com estes dados.
