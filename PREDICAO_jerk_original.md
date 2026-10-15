# Previsão registrada antes de calcular: a sobra do original tem ligação própria com |jerk|?

**Registrada em:** 15/10/2026, a pedido de Ana ("acho bom também testar jerk").

**Status:** exploração, **não** confirmatória. Nada de outubro é lido, e nada congelado muda.

## O que já foi visto

Na rodada anterior (`LEITURA_dimensao_original_nu.md`), descontadas raridade e volume, o resíduo médio do original se correlacionou com |jerk|:

| Período | Correlação |
|---|---|
| jun–jul | +0,15 |
| ago–set | +0,19 |

Isso não foi conferido na nula. No fluxo, um padrão parecido (|ι|) apareceu igual na nula, ou seja, era artefato da medida. A fumaça em maio não imprimiu estatísticas.

## Medida

- **Resíduo:** o mesmo de `explora_dimensao_original_nu.py`, com as mesmas semanas, pontos e nula. É log tr D(p) menos uma cúbica em (ν̄_w(p), log ρ_w(p)). A nula é um VAR(1) em 4 dimensões com volatilidade agrupada, em 5 réplicas.
- **Por semana w:** J_w = Spearman, entre os 1.500 pontos, do resíduo com |jerk(p)|. São 9 semanas por período.
- **Δ_w** = J_w no real − média das 5 réplicas da nula.
- **Descritivo:** a mesma medida com o jerk com sinal.

## Critério, para |jerk|

| Classificação | Condição |
|---|---|
| **Ligação própria com \|jerk\|** | Δ médio ≥ 0,10 e real acima da nula em ≥ 8 de 9 semanas |
| **Indício fraco** | Δ médio > 0 e ≥ 6 de 9 semanas, sem atingir o anterior |
| **Artefato da medida** | o resto, isto é, a nula reproduz o padrão |

Só conta se repetir nos dois períodos. Senão, "não estável".

## Aposta de Claude, antes dos dados

| Classificação | Probabilidade |
|---|---|
| Ligação própria | ~20% |
| Indício fraco | ~25% |
| Artefato | ~55% |

A aposta pesa para artefato porque |ι| no fluxo foi artefato e porque o jerk tem distribuição de caudas pesadas. Mas jerk é uma segunda diferença: um jerk grande indica um solavanco, e um solavanco pode realmente anteceder agitação. Por isso a probabilidade de ligação própria não é desprezível.

## Como roda

- **Jun–jul:** localmente.
- **Ago–set:** `.github/workflows/explora-jerk-original.yml`, disparado pelo push deste ramo.
