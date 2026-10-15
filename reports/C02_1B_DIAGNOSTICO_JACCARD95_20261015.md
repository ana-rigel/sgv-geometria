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

## Segundo diagnóstico: o portão inteiro com 10 conjuntos de sementes

**Origem e registro:**
- Este diagnóstico foi registrado primeiro, no commit `f3c4d5d`, numa execução deste mesmo pedido que foi interrompida quando o ambiente reiniciou.
- Na retomada, eu não o vi e fiz o diagnóstico acima.
- Rodei este depois, sem alteração: o script ficou no commit `28fe1d8`, e o registro é `PROTOCOLO_SGV_C02_1B_DIAGNOSTICO_SEMENTES_20261014.md`.

**Desenho:** o mesmo par de execuções do portão, com produção HDR50 ×1 e HDR95 ×4 e comparação com o dobro, nos 42 pares (G3 e BS35). Variam 10 conjuntos novos de sementes de Monte Carlo. Ficam fixos o ajuste, o conjunto retido e os limites.

| Conjunto | Portão | Falhas |
|---|---|---|
| 1, 4, 5, 6, 9, 10 | passaria | — |
| 2 | bloqueado | BS35·T4·2 Jaccard HDR95 (0,0205) |
| 3 | bloqueado | **G3**·T6·0 centro HDR50 |
| 7 | bloqueado | BS35·T4·2 Jaccard HDR95 (0,0285) e log V HDR95 |
| 8 | bloqueado | BS35·T0·1 Jaccard **HDR50**; BS35·T3·0 log V HDR95 |

**4 de 10 conjuntos bloqueiam.** Pelo critério registrado antes de rodar (≥ 3 em 10), a falha é **frequente**. A aposta registrada era de ~35 %.

## Leitura conjunta

1. **O portão, como está desenhado, é quase um sorteio.** Com o extrator funcionando como esperado, um conjunto de sementes passa ~60 % das vezes.
2. **A causa é estrutural.** São dezenas de checagens por par em 42 pares, cada uma com limite fixo perto do percentil 97–99 do próprio ruído. Com tantas checagens, alguma tende a passar do limite por acaso.
3. **O BS35·T4·2 é o caso mais frágil,** mas não o único:
   - 2 das 5 falhas não são do HDR95: centro do HDR50 no **G3**, a família de caudas leves, e Jaccard do HDR50 no BS35;
   - aumentar só o orçamento do HDR95 não resolveria tudo.

## Decisão pendente (da Ana, antes do portão oficial)

A errata C02.1b registrou que seria a última julgada no substituto e que o oficial rodaria com as regras vigentes.

**Correção da versão anterior deste relatório:** a opção (b) original propunha só ×16 no HDR95. O segundo diagnóstico mostra que isso não basta.

As opções passam a ser três:

- **(a) Manter o registrado.** O oficial roda uma vez com as regras C02.1 + a + b, com chance de ~50–60 % de passar se o oficial se comportar como a imitação.
- **(b) Errata C02.1c só de orçamento,** antes do oficial: HDR95 ×16 e HDR50 ×4.
  - Pela raiz do orçamento, o ruído cai pela metade nos dois níveis.
  - Custo computacional ~4×.
  - Fica dentro da filosofia do portão atual.
- **(c) Errata C02.1c de desenho do portão.** Em vez de "nenhuma checagem acima do limite em nenhum par", o portão passaria a julgar a **taxa** de checagens acima do limite contra um teto fixado agora, por exemplo ≤ 1 % por variável e família.
  - Isso enfrenta a multiplicidade de frente.
  - É uma mudança de filosofia, e precisaria ser registrada com cuidado.

Nas três opções, o portão oficial roda uma única vez, e nenhuma é testada antes no substituto.
