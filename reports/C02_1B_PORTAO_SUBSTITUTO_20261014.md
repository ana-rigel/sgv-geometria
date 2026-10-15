# SGV-C02.1b — Portão substituto com orçamento ×4 no HDR95: bloqueado por uma checagem (Jaccard HDR95, 0,0207 > 0,02)

**Data:** 14/10/2026. **Natureza:** engenharia. **Não** é o portão oficial: o gerador é o substituto, não o da C02.
- **Errata registrada antes do código:** `PROTOCOLO_SGV_C02_1B_ERRATA_20261014.md` (commit `7eb5322`).
- **Script:** `scripts/c02_1b_portao_substituto.py`, idêntico ao do C02.1a exceto `hdr95_budget=4`.
- **Dados:** `reports/c02_1/portao_substituto_b.json`.
- **Amostra:** 42 pares (G3 e BS35 substitutos × T0–T6 × 3 réplicas), nenhum ajuste de GMM3 inválido.
- **Testes do extrator:** 13 passam. O novo teste confirma que o HDR50 fica idêntico bit a bit e que o ESS do HDR95 sobe ~4×.

## Retenção (regra do C02.1a, recalculada com o novo orçamento)

O conjunto retido é o **mesmo do C02.1a, com 7 variáveis**: HDR50 center, log V, Jaccard e massa cruzada; HDR95 log V, Jaccard e massa cruzada.

As confiabilidades do BS35 mudaram pouco:
- HDR95 log V: 0,71 → 0,69;
- HDR95 Jaccard: 0,68 → 0,66;
- HDR95 centro: 0,30 → 0,32;
- HDR95 forma: 0,24 → 0,16.

Isso confirma que o limite das variáveis que saem é o ruído do **ajuste** do GMM3 nas caudas, não o Monte Carlo.

## Precisão de Monte Carlo no HDR95

| | C02.1a (×1) | C02.1b (×4) |
|---|---|---|
| \|Δ Jaccard\| mediano, BS35 | 0,0096 | 0,0054 |
| \|Δ Jaccard\| p90, BS35 | 0,0188 | 0,0126 |
| \|Δ Jaccard\| máximo, BS35 | 0,0295 | **0,0207** |
| \|Δ Jaccard\| máximo, G3 | 0,0169 | 0,0101 |
| ESS mínimo do HDR95, BS35 | 1.624 | **6.711** |
| checagens com falha | 4 | **1** |

## Veredito do portão substituto: BLOQUEADO

A única falha é BS35·T1·réplica 2, Jaccard do HDR95: 0,4432 (×4) contra 0,4639 (×8), |Δ| = 0,0207, limite 0,02.

O ESS e as outras 41 checagens de Jaccard passaram. O ruído típico caiu como previsto, mas a cauda da distribuição das diferenças caiu menos que a raiz do orçamento. O Jaccard por importância na mistura tem pesos de cauda pesada no BS35. A falha fica registrada como está: o limite não é afrouxado e o caso não é omitido.

## Apostas (registradas na errata)

- Portão substituto passa, ~70 %: **errou**, por 0,0007.
- Conjunto retido igual ao do C02.1a, ~60 %: **acertou**.

## O que vem agora (regra registrada no C02.1b)

Esta foi a **última errata julgada no gerador substituto**. Não haverá C02.1c sobre a imitação.

O portão que conta é o **oficial**:
- gerador `SGV_C02_GERADOR_PILOTO_20261014.zip` (SHA-256 `4691266c…`) integrado ao ramo byte a byte;
- 35 pares de calibração;
- regras C02.1 + C02.1a + C02.1b;
- julgado uma única vez.

O pacote do gerador ainda não está no repositório nem nesta sessão e depende da Ana.

**Leitura de risco:** no substituto, o BS35 deixa o Jaccard do HDR95 rente ao limite em ~1 caso de 21. Se o BS35 oficial se comportar como a imitação, a chance de passar no oficial fica em torno de **50 %**.
