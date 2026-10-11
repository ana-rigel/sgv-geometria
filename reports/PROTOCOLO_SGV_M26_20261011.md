# SGV-M26 — Resiliência da liquidez como volatilidade cruzada (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m26-resiliencia-cruzada` (a partir de `research/m25-volatilidade-multiescala`). **`main` intocada. Só dados exploratórios** (as mesmas 84 origens do 1m).
**Nota de ritmo:** 6º experimento do dia, a pedido explícito da Ana ("Não há o que fazer, precisamos fechar").
**Origem:** diagnóstico exploratório do M25 — o modelo transmite magnitude demais de |retorno|ₜ para |agressão|ₜ₊₁; no BTC real, após um choque de preço, o fluxo do minuto seguinte é mais equilibrado (resiliência da liquidez).
**Antes deste documento:** testes unitários (o ajuste recupera o sinal negativo de um termo cruzado plantado) e o ajuste numa única origem de desenvolvimento, **onde o termo agressão←retorno saiu −0,045**. Declaro isso porque a previsão mecanística abaixo foi formulada depois de ver esse valor numa origem (e o diagnóstico do M25). Nenhum posto do M26 foi visto.

## Modelo
**`HARLMFX`** = o modelo do M25 (regimes lentos + bloco lento real; HAR 1/15/60 na média; inovações reais filtradas), com a variância estimada **nas coordenadas originais** (retorno, agressão, volume), cada uma com
h_j,t = w_j + Σᵢ c_ji·r²ᵢ,ₜ₋₁ + a₁₅,ⱼ·m15ⱼ + a₆₀,ⱼ·m60ⱼ + a₂₄₀,ⱼ·m240ⱼ + bⱼ·hⱼ,ₜ₋₁,
termos próprios ≥ 0, **termos cruzados c_ji (i≠j) livres em sinal**, variância incondicional 1, piso 0,05; quase-verossimilhança no prefixo. As inovações reais são padronizadas por √h (preservam forma e correlação contemporânea).
Referências pareadas: **`HARLMFV`** (M25) e **`BL`**. Mesmas 12 estatísticas, 39 referências, posto conservador, alarme p ≤ 0,05.

## Critérios pré-registrados
1. **Primário:** HARLMFX alarma menos que HARLMFV em `vol_1`, `vol_5`, `vol_30` (McNemar exato pareado, unilateral, α = 0,05/3).
2. **Veredito do HARLMFX:** "adequação plena" / "equivalente ao BL" (nenhuma das 12 significativamente pior, α = 0,05/12) / "não fecha a lacuna".
3. **Mecanismo:** o termo **agressão ← retorno (c_ιz)** é negativo na maioria das origens (teste do sinal unilateral, α = 0,05). Descritivo: termo retorno ← volume.

## Apostas de Claude (antes de qualquer resultado)
| Item | Aposta |
|---|---|
| Mecanismo: c_ιz negativo na maioria das origens (sinal significativo) | ≈ 70% |
| Primário significativo em `vol_1` | ≈ 50% |
| Primário significativo nas três defasagens | ≈ 20% |
| Veredito "equivalente ao BL" | ≈ 25% |
| Veredito "adequação plena" | ≈ 7% |
