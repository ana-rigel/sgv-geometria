# Leitura contra a previsão registrada (PREDICAO_dimensao_campo.md, commit fba1a41)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38789887269).

## Fluxo (primária desta exploração)

| | jun–jul | ago–set |
|---|---|---|
| Persistência do resíduo (além de ν e log ρ): real | +0,116 | +0,301 |
| Persistência do resíduo: nula VAR + vol agrupada | +0,165 | +0,209 |
| Δ médio / pares com real acima | **−0,049** / 3 de 8 | **+0,092** / 6 de 8 |
| Classificação | **Não há** | **Indício fraco** |
| Persistência de log tr D bruto: real / nula | +0,82 / +0,54 | +0,78 / +0,56 |
| R² de (ν, log ρ): real / nula | 0,77 / 0,51 | 0,68 / 0,53 |

- **Previsões 1 e 2:** as classificações diferem entre os períodos. Pela regra registrada, **"não estável"**.
- **Leitura:** o mapa de tamanho da agitação se repete fortemente de semana a semana: +0,78 a +0,82 no real, contra +0,54 a +0,56 na nula. Volume e raridade explicam a maior parte, 68% a 77%. O que sobra depois deles não se repete de forma estável além da nula.
- **Aposta sobre o R²:** acertou. R² mediano ≥ 0,6 nos dois períodos.
- **Onde morava o resíduo:** o resíduo médio do real se correlaciona com |ι| (+0,47 e +0,55). Antes de ler isso como sinal, rodei uma conferência post hoc em jun–jul, que **não estava prevista**: a mesma correlação aparece nas 5 réplicas da nula (+0,31 a +0,50). É geometria da medida (a dependência radial que o polinômio em log ρ não captura toda ao longo de ι), não mercado. A aposta "|z| ou ι" fica **sem suporte**.

## Original (descritivo, controlado só por log ρ, porque não há eixo de volume)

| | jun–jul | ago–set |
|---|---|---|
| Persistência do resíduo: real / nula | +0,392 / +0,217 | +0,308 / +0,177 |
| Δ médio / pares com real acima | +0,175 / 8 de 8 | +0,131 / 6 de 8 |
| R² de log ρ: real / nula | 0,79 / 0,74 | 0,87 / 0,85 |

- No original sobra geografia além da raridade, e ela se repete mais que na nula nos dois períodos.
- O resíduo médio se correlaciona com |E_norm| (+0,38 e +0,46).
- Não há controle de volume aqui. Isso pode ser a relação volume–volatilidade entrando por E_norm, e não geografia nova.
- Não conferi a nula para |E_norm|.

## Para o programa

- **Fluxo:** o "campo" de tamanho da agitação é, até onde estes quatro meses mostram, essencialmente volume + raridade. Uma geografia 3D estável não apareceu.
- **Testes congelados:** isto não afeta o H-DIF-01 nem o H-FORMA-D-01. Eles testam se o campo antecede amplitude além de controles, não se a geografia é 3D.
