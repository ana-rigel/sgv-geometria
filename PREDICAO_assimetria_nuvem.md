# Previsão registrada antes de calcular: a nuvem do cubo é torta?

**Registrada em:** 16/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "é só uma tentativa de verificar, nada de insistência", depois da pergunta sobre acúmulo de densidade ou micro-assimetria na casca HDR50. Uma tentativa: um julgamento por período, sem segunda rodada.

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já foram abertos. Nada de outubro é lido; nada congelado muda.

**Ramo:** `exploracao/assimetria-nuvem`, a partir de `painel/replay-4d@5729218`.

## Por que a casca não responde

A casca HDR50 é um elipsoide ajustado à covariância (segundo momento), simétrico por construção. Assimetria de densidade é terceiro momento. Nunca foi medida em nenhuma rodada: todas as medidas anteriores (ext, R, C, s13) são de tamanho ou forma sem sinal.

## Os eixos têm sinal (correção de leitura)

Pelo `input_builder` do sgv_original: **E_norm** = z robusto de (close − EMA₀,₀₅(close))/|EMA|, o preço acima (+) ou abaixo (−) da sua média; **jerk** = Δaceleração = terceira diferença do retorno; **memory_flux** = Δ da E_norm suavizada (EWM α = 0,05), a deriva se abrindo (+) ou fechando (−). Os três são assinados; os três entram.

## Medidas (por semana, na régua de maio, série real e 5 réplicas M)

1. **Assimetria padronizada** g₁ = m₃/m₂^{3/2} de cada eixo, nas barras válidas da semana.
2. **Fração positiva na borda** p⁺ = fração de barras com ext ≥ 3 cujo eixo é positivo, por eixo (50 % = simétrico). Só conta com ≥ 30 barras na borda.
3. **Assimetria por temperatura**: g₁ de cada eixo nas barras do tercil quente de w (Q.quarta/limites), para ver se a nuvem quente é mais torta que a fria.

Séries: real e M (sementes 4026–4030, `gerar_m`). O M tem retornos AR(1) com ruído simétrico e volatilidade sem sinal: é simétrico por construção, até onde a construção das coordenadas (EMA, diferenças, z robusto) não imprima assimetria. Por isso o envelope do M é o "nada" correto: ele contém a assimetria que o instrumento cria sozinho.

## Classificação (por período e por eixo; só vale se repetir em jun–jul e ago–set)

Para cada eixo, em cada semana, g₁ do real é "fora" se está acima do máximo ou abaixo do mínimo das 5 réplicas M naquela semana.

- **"Torta":** g₁ real fora do envelope M em ≥ 2/3 das semanas válidas, **com o mesmo sinal** em todas as semanas fora.
- **"Torta sem lado":** fora em ≥ 2/3 das semanas, mas o sinal muda de semana para semana.
- **"Simétrica dentro do ruído":** senão.

p⁺ e a assimetria por temperatura são descritivas: relatadas, não classificadas.

## O que esta exploração não testa

Direção. Uma nuvem torta pode ser a assinatura de um movimento que já aconteceu (E_norm fica positiva depois de uma subida, por construção). Separar "torta porque subiu" de "torta antes de subir" é teste de direção, exige pré-registro próprio com critério contra o M, e só poderia nascer em dezembro, nos dados de novembro. Nenhum número daqui vira indicador.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| E_norm: "simétrica dentro do ruído" nos dois períodos | ~60 % |
| jerk: "simétrica dentro do ruído" nos dois períodos | ~75 % |
| memory_flux: "simétrica dentro do ruído" nos dois períodos | ~55 % |
| Algum eixo "torta" (mesmo lado) nos dois períodos | ~15 % |
| Nuvem quente mais torta que a fria (|g₁| maior) no real, dois períodos | ~50 % |

A aposta mais baixa é em memory_flux porque a volatilidade do BTC sobe mais rápido do que desce (saltos de aquecimento, resfriamento lento), e a E_norm suavizada pode herdar isso como cauda assimétrica; o M, com volatilidade real mas retornos simétricos, deve herdar parte, não tudo.

## O que confirma e o que não

- **Simétrica nos três:** a casca simétrica não esconde nada; a nuvem é simétrica dentro do que o ruído permite. A pergunta fecha.
- **Torta em algum eixo, mesmo lado, dois períodos:** há estrutura de terceiro momento que o instrumento não cria sozinho. Vira candidata a hipótese; não vira indicador.
- Em nenhum caso há direção, previsão ou lucro.
