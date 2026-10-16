# Previsão registrada antes de calcular (v3): corrigidos os dois defeitos da v2

**Registrada em:** 16/10/2026, depois da leitura da v2 e antes de rodar qualquer coisa com o código novo.

**Pedido da Ana:** "REGISTRE E RODE V3".

**Status:** exploração. Meses abertos. Nada de outubro; nada congelado muda.

**Ramo:** `exploracao/memoria-potencia`, a partir de 13a5ea0.

## As três correções

1. **Grade sem múltiplos de um dia.** Atrasos: 1, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45, 64, 91, 128, 181, 256, 362, 512, 724, 1.024, **1.800, 2.160, 3.600, 5.040, 6.480** min (25 atrasos; os cinco longos são 1,25, 1,5, 2,5, 3,5 e 4,5 dias). Nenhum é múltiplo de 1.440 nem de 10.080.
2. **Dessazonalização por diferença, não por divisão.** a_t = |r_t| − m(h_t), em que m(h) é a **média** de |r| por minuto do dia em maio. A divisão imprimia o inverso do ciclo nos sintéticos que não o tinham; a subtração de uma constante por minuto do dia não altera a autocovariância de uma série sem ciclo e remove a média periódica de uma série com ciclo. (Resíduo de ciclo na variância fica; por isso a grade também evita os múltiplos.)
3. **E2 gerado de uma vez, sem re-ancorar.** Para o período inteiro desde 01/06: ℓ_t = log s_t (caminho real suavizado, 61 min, com o resíduo do AR(1) de retornos ajustado no período inteiro); um só ajuste ℓ_t = c + φ_ℓ ℓ_{t−1} + η; uma só trajetória simulada ℓ*, partindo de ℓ real só no primeiro minuto de 01/06; escala rápida calibrada uma vez no período inteiro; retornos AR(1) com (a, φ) do período inteiro. **10 réplicas**, sementes 6026 a 6035.

Tudo o mais como na v2: três ajustes em log ρ nos atrasos com ρ > 0, AIC, classes com |ΔAIC| > 2 e β em [0,1; 0,6]; M (5 réplicas) só como referência.

## Validação, mais exigente

O E2 precisa sair **"duas exponenciais"** (não apenas fora de "potência") em ≥ 8 das 10 réplicas. Senão: INCONCLUSIVO, e a leitura diz por quê (qual forma o E2 tomou).

## Regra

- **Principal:** classe do real em jun–set (122 dias), se o E2 validar.
- **Estabilidade:** jun–jul e ago–set dão a mesma classe para o real, com E2 validando em ambos.
- **Descritivo:** ρ(τ) real e E2 nos atrasos longos; onde o real descola do envelope E2; θ₁, θ₂; ΔAIC por corte (1,5, 2,5, 3,5, 4,5 dias); c, φ_ℓ, τ_ℓ, Var η e φ_h, Var h ajustados no período inteiro.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| E2 valida em jun–set (≥ 8/10 "duas exponenciais") | ~65 % |
| Real "potência" em jun–set | ~50 % |
| Real "indistinguível" em jun–set | ~35 % |
| Real "duas exponenciais" em jun–set | ~15 % |
| Estável | ~40 % |
| ρ(6.480) do real > 0,03 | ~55 % |
| ρ(6.480) do E2 < 0,02 em ≥ 8 réplicas | ~70 % |
| τ_ℓ do período inteiro entre 5 e 15 h | ~60 % |

## O que confirma e o que não

Como na v2. Se a validação reprovar de novo, o instrumento (ajuste de três formas por AIC numa grade de 25 atrasos) não serve para a pergunta, e ela sai do programa até alguém trazer um método melhor (p. ex. estimador de Hurst/DFA com nulas).
