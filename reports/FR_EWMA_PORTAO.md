# H-FR-EWMA — resultado do portão exploratório

**Data:** 09/10/2026 (UTC). **Pré-registro:** `reports/PREREGISTRO_FR_EWMA.md`, commit `00bb4b3`, congelado antes desta rodada; código idêntico ao congelado (SHA-256 `d6a447e7…`).

**Veredito: o portão NÃO PASSA em 1m nem em 1h.** Pela regra do pré-registro (§4–5), a hipótese está encerrada **sem tocar o período confirmatório**, e a linha geométrica do `sgv-geometria` fecha (era a reformulação única permitida pelo PLANO após o G1).

| | 1m (mai–jul/2026) | 1h (2020–2024) |
| --- | --- | --- |
| Linhas de teste | 63.987 | 18.856 |
| MSE M0 → M1 (log range) | 0,32575 → 0,32566 | 0,25894 → 0,25896 |
| Ganho relativo de M1 | +0,027% | −0,006% |
| DM (HAC, lag 1 dia) | t = 0,81, p = 0,21 | t = −0,39, p = 0,65 |
| Blocos com ganho > 0 | 4 de 6 (−0,10% a +0,10%) | 3 de 6 (−0,05% a +0,02%) |
| Regra (ganho > 0 e p < 0,10) | ✗ | ✗ |

Arquivos: `FR_EWMA_EXPLORACAO_{1m,1h}.json` e as previsões individuais em `FR_EWMA_EXPLORACAO_{1m,1h}_perdas.csv.gz`.

## Verificações de sanidade (depois do veredito; não alteram a decisão)

- O controle funciona: R² fora da amostra de M0 = 0,493 (1m) e 0,458 (1h); M1 dá o mesmo até a 4ª casa.
- A variável não é degenerada: log κ vai de ~2,8–3,1 (p5) a ~7,5–7,6 (p95).
- **Sem controle nenhum, log κ já não se relaciona com o alvo**: correlação de postos com o log range futuro = −0,007 (1m) e −0,003 (1h).
- Com R² de 0,33 (1m) e 0,48 (1h), log κ é em boa parte explicado pelas variáveis de M0.

## Leitura

Retirado o eco da janela retangular, a curvatura Fisher–Rao da trajetória gaussiana não carrega informação sobre a amplitude futura, nem bruta nem incremental. O ganho do experimento gerador vinha de volatilidade recente e do retorno que saía da janela 1.500 barras antes, não da geometria. Aposta do Claude registrada antes: 25% de passar no portão; não passou.

## O que fica preservado

O período confirmatório (1m a partir de ago/2026; 1h a partir de jan/2025) **continua virgem** e disponível para hipóteses independentes já anotadas: por exemplo, a taxa de troca de assinatura da métrica H, do relatório do G1, que precisaria do próprio pré-registro.
