# SGV-C02.1b — Diagnóstico do Jaccard do HDR95: a falha de T1·2 foi sorteio, mas o problema é sistemático

**Data:** 15/10/2026. **Natureza:** diagnóstico, não portão. O veredito do portão substituto C02.1b continua **BLOQUEADO**.
- **Pedido:** a Ana pediu para testar de novo, porque a falha foi pequena (0,0207 contra 0,02).
- **Por que não rerodar o portão:** com as mesmas sementes ele dá o mesmo número. Trocar sementes até passar é proibido pela emenda C02.1 ("não se trocam sementes").
- **O que foi feito:** medi a distribuição da diferença.
- **Script:** `scripts/c02_1b_diagnostico_jaccard95.py`, registrado no commit anterior, antes de rodar.
- **Dados:** `reports/c02_1/diagnostico_jaccard95.json`.

**Desenho:**
- 21 pares do BS35 substituto, com os mesmos ajustes GMM3 do portão.
- 20 repetições por par da medição do Jaccard do HDR95, com sementes independentes (prefixo `diag`), na produção (×4) e no dobro (×8).
- O que se mede é a chance de \|Δ\| > 0,02.

## Resultado

| | valor |
|---|---|
| \|Δ\| mediano (420 medições) | 0,0045 |
| p95 | 0,0175 |
| máximo | 0,0343 |
| medições acima de 0,02 | 2,9 % |
| **BS35·T1·2 (a falha do portão)** | 0 de 20 acima; máximo 0,0198 |

**Pares com chance de falha:**

| Par | P(\|Δ\| > 0,02) |
|---|---|
| T4·2 | **35 %** |
| T5·1 | 10 % |
| T3·0 | 5 % |
| T6·0 | 5 % |
| T6·2 | 5 % |
| os outros 16 | 0 % em 20 |

**Chance de os 21 pares do BS35 passarem juntos:** ~50 % (contagem bruta), ~31 % (suavizada).

## Leitura

1. **A falha específica foi azar.** Em BS35·T1·2, os 0,0207 do portão foram um sorteio de cauda; em 20 repetições o par nunca passou do limite.
2. **O bloqueio não é azar.** Com orçamento ×4, o Jaccard do HDR95 no BS35 fica rente ao limite em alguns pares, sobretudo T4·2, que falha uma vez em três. Rerodar o portão com sementes novas passaria mais ou menos metade das vezes. Um "passou" assim seria sorte, não precisão.
3. **Consequência para o portão oficial:** se o BS35 oficial se comportar como a imitação, as regras vigentes (C02.1 + a + b) dão **~30–50 %** de chance de passar.

## Decisão pendente (da Ana, antes do portão oficial)

A errata C02.1b registrou que seria a última julgada no substituto e que o oficial rodaria com as regras vigentes. Há duas opções:

- **(a) Manter o registrado.** O oficial roda uma vez com ×4, aceitando ~30–50 % de chance de bloqueio.
- **(b) Errata C02.1c antes do portão oficial**, com orçamento ×16 no HDR95.
  - Pela raiz do orçamento, metade do ruído outra vez: o pior par cairia para ~0,017.
  - Custo computacional ~4× no HDR95.
  - Seria um desvio declarado do compromisso do C02.1b, motivado por este diagnóstico, e não por um resultado de classificador.
  - Ela não seria testada antes no substituto, para não repetir o ciclo.
