# Previsão registrada antes de calcular (MSM v5): quantas escalas sobram depois que o volume absorve o que é dele?

**Registrada em:** 17/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "Sim faça o teste", sobre a proposta de pôr o volume no modelo mantendo o tempo cronológico; esta versão o põe na **equação de observação** (hipótese da mistura de distribuições), não na de transição, pelas razões dadas na conversa (volume é contemporâneo e explica tamanho, não troca de regime; TVTP tem identificação ruim).

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já abertos. Nada de outubro. Um julgamento por período.

**Ramo:** `exploracao/msm` (continuação), a partir de 1b1df3c.

## Modelo

r_t = σ̄ · (v_t / v̄)^δ · (Π_{i=1}^{k} M_{i,t})^{1/2} · ε_t, com ε_t Student-t padronizada (ν), M e transições como na v2, **δ ∈ [0, 1] livre**. δ = 0 recupera a v2; δ = ½ é a mistura de distribuições pura (variância proporcional ao volume). v̄ = volume médio por minuto do período; **piso v_t ≥ 0,01·v̄** para minutos sem volume (declarado). Estimação por verossimilhança (filtro de Hamilton sobre r_t / (v_t/v̄)^δ, com o jacobiano −δ·Σ log(v_t/v̄)); σ̄ perfilado como desvio-padrão da série escalada.

Instrumento herda da v3 (Emenda 2) os limites m₀ ∈ (1,01, 1,95), ν ∈ (2,3, 50), três pontos iniciais e o descarte de soluções com m₀ no teto ou ν no piso. Sem dessazonalização (o volume carrega o ciclo diário; é parte do que se quer medir). Grade **k = 1…4** (comparável à v2; custo). BIC com 5 parâmetros.

## Validação (antes de ler o real)

Sintéticos gerados com o **volume real do período** e δ = 0,5, ν = 4, m₀ = 1,4, b = 25, γ_k = 0,5 (escalas ~2 min, ~50 min, ~21 h), k = 2 (semente 8026) e k = 3 (8027). Válido se k* recuperar o k gerador nos dois **e** δ̂ ficar em 0,5 ± 0,1 nos dois. Senão, INCONCLUSIVO.

## Classificação (por período; só vale se repetir; referência: v2 deu k* = 4 nos dois)

- **"Volume absorve a escada rápida":** k* ≤ 2 e δ̂ > 0,2.
- **"Absorve em parte":** k* = 3 e δ̂ > 0,2.
- **"Hierarquia própria":** k* = 4 (qualquer δ̂).
- **"Volume irrelevante":** δ̂ ≤ 0,2 (qualquer k*).

Descritivos: δ̂; ν̂ contra o da v2 (6,3 e 2,75); escalas 1/γ_i; ΔBIC por degrau contra a v2.

## Limitações declaradas

- v_t é contemporâneo: o modelo é descritivo, não preditivo. A versão com v_{t−1} não é testada aqui.
- Volume de 1 min da Binance spot é um proxy do fluxo total (futuros e outras bolsas ficam fora).
- k ≤ 4: "hierarquia própria" é fronteira, como na v2.
- fail-fast desligado na matriz do Actions (lição da v3).

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Validação passa nos dois períodos | ~65 % |
| δ̂ entre 0,3 e 0,6 nos dois períodos | ~65 % |
| ν̂ maior que o da v2 nos dois períodos (cauda afina com o volume) | ~75 % |
| "Hierarquia própria" (k* = 4) nos dois períodos | ~45 % |
| "Absorve em parte" (k* = 3) em algum período | ~35 % |
| "Volume absorve a escada rápida" (k* ≤ 2) em algum período | ~15 % |
| "Volume irrelevante" em algum período | ~5 % |

## O que confirma e o que não

- **Hierarquia própria com δ̂ ≈ ½ e ν̂ alto:** o volume explica a cauda (mistura de distribuições) mas não a escada; a hierarquia de escalas é dinâmica própria da volatilidade, não ritmo de negociação.
- **Absorve (total ou em parte):** a escada rápida era ritmo de volume; o que resta é regime lento.
- Em nenhum caso há direção, previsão ou lucro.
