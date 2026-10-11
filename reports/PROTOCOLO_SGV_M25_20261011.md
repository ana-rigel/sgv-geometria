# SGV-M25 — Memória de volatilidade multiescala (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m25-volatilidade-multiescala` (a partir de `research/m24-har-fhs`). **`main` intocada. Só dados exploratórios** (as mesmas 84 origens do 1m).
**Nota de ritmo:** 5º experimento do dia, a pedido explícito da Ana ("já que falta pouco vamos continuar").
**Pergunta sobre o BTC:** o que sobrou no M24 — memória de volatilidade em todas as defasagens — é **volatilidade com várias escalas de persistência**? Se for, trocar o GARCH(1,1) por uma variância heterogênea por horizontes deve fechar (ou quase fechar) a lacuna.
**Antes deste documento:** testes unitários e o ajuste numa única origem (engenharia: pesos distribuídos entre 15, 60 e 240 min; simulação finita). Nenhum posto do M25 foi visto.

## Modelo
**`HARLMFV`** = o HARLMF do M24 (regimes lentos + bloco lento real; HAR 1/15/60 min na média; inovações reais filtradas) com a variância de cada coordenada branqueada dada por
h_t = w + a₁·u²_{t−1} + a₁₅·média(u², 15 min) + a₆₀·média(u², 60 min) + a₂₄₀·média(u², 240 min) + b·h_{t−1},
com variância incondicional 1 e parâmetros não negativos, por quase-verossimilhança no prefixo (tipo HARCH). As inovações reais são padronizadas por essa variância.
Referências pareadas: **`HARLMF`** (M24) e **`BL`**. Mesmas 12 estatísticas, 39 referências, posto conservador, alarme p ≤ 0,05.

## Critérios pré-registrados
1. **Primário:** HARLMFV alarma menos que HARLMF em `vol_1`, `vol_5`, `vol_30` (McNemar exato pareado, unilateral, α = 0,05/3 cada).
2. **Veredito do HARLMFV:** "adequação plena" (nenhuma das 12 com Wilson inferior > 7%) / senão "equivalente ao BL" (em nenhuma das 12 significativamente pior que o BL, α = 0,05/12) / senão "não fecha a lacuna".

## Ressalvas
As mesmas do M24. Além disso, o BL serve de referência, mas é levemente liberal: "equivalente ao BL" é o objetivo prático, não uma prova de calibração.

## Apostas de Claude (antes de qualquer resultado)
| Item | Aposta |
|---|---|
| Primário significativo nas três defasagens | ≈ 45% |
| Primário significativo em pelo menos `vol_30` | ≈ 60% |
| Veredito "equivalente ao BL" | ≈ 30% |
| Veredito "adequação plena" | ≈ 8% |
| HSIC continua pior que o BL em alguma defasagem | ≈ 60% |
