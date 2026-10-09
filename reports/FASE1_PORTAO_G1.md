# Fase 1 — Julgamento do portão G1 em dado real

**Data:** 09/10/2026 · **Dados:** BTCUSDT spot, período de exploração travado em 08/10/2026 (1m: mai–jul/2026; 1h: 2020–2024) · **Configuração:** fixada antes desta rodada (`PLANO.md`): métrica de Fisher local, grandeza ΔF, gaussianização causal por postos, janela de 1.500, largura de 2× Scott escolhida por D7.

**Veredito: o portão G1 não passa, nem em 1m nem em 1h.** O critério que falha nas duas escalas é o 3, a existência. A média de ΔF no BTC real não se distingue da de séries GARCH ajustadas a ele (p = 0,40 em 1m; p = 0,175 em 1h, com 39 réplicas). Com as coordenadas do SGV (E = v²+a², jerk, memory_flux), a geometria da distribuição de estados do BTC é a de um processo com volatilidade agrupada e caudas pesadas, e nada além disso que este teste consiga ver.

| Critério do G1 | Regra | 1m | 1h | GARCH sintético (calibração) |
| --- | --- | --- | --- | --- |
| 1. Mensurável (D7) | confiabilidade de ΔF ≥ 0,8 | 0,83 ✓ | 0,85 ✓ | 0,77 com 2× ✗ |
| 2. Além da posição (D4) | \|ρ(ΔF, distância ao centro)\| < 0,5 | 0,20 ✓ | 0,23 ✓ | 0,21 com 2× ✓ |
| 3. Existe (D8) | média de ΔF ≠ GARCH ajustado, p ≤ 0,05 | p = 0,40 ✗ | p = 0,175 ✗ | p = 0,25 com 2× ✗ |
| 4. Além da volatilidade (D5) | R² de ΔF pela volatilidade ≤ 0,5 | 0,495 ✓ (no limite) | 0,571 ✗ | 0,65 com 2× ✗ |

Arquivos: `reports/real_1m/` e `reports/real_1h/`.

## O que mais os dados reais mostraram

- **O legado se comporta no BTC real como na calibração** (D1–D3). Em 1m, a curvatura 3D da malha tem mediana de 8,9×10⁴ e chega ao corte de ±10⁶, contra uma curvatura exata de 8×10⁻¹⁰. Com dados reais, ao vivo, o sinal de entrada de uma barra já fechada se inverte em 62% das atualizações em 1m e em 8% em 1h.
- **Não há equação de campo** (D6). Em 1h, o R² de G = κT com κ único fica entre 0,006 e 0,017. Em 1m, o z-score robusto deu um R² de 0,90, mas é efeito de outliers: 1% das barras concentra praticamente toda a soma de G². Sem esse 1%, o R² cai para 0,002. Com a gaussianização por postos, o R² fica em 0,53–0,64, e o sinal de κ por barra continua perto de cara ou coroa (53–59% positivo).
- **O BTC se distingue dos substitutos que destroem o agrupamento de volatilidade**, mas não do GARCH. Contra o IAAFT e o embaralhamento, várias estatísticas ficam no limite de resolução (p = 0,05), entre elas log det F, a autocorrelação de φ e a média de ΔF. Contra o GARCH ajustado, nenhuma estatística de F ou de ΔF fica abaixo de 0,075.

## Observação exploratória (não é resultado)

Entre as 10 estatísticas de D8, uma ficou abaixo de 0,05 contra o GARCH: a **taxa de troca de assinatura da métrica H**, que no BTC é menor que no GARCH. Em 1m é 0,111 contra 0,222 (p = 0,025); em 1h, 0,146 contra 0,207 (p = 0,05). Ela não era a estatística primária e foram feitas 10 comparações. Com correção de Bonferroni, o limiar seria 0,005, e ela não chega perto. Fica anotada como observação nascida da inspeção. Se virar hipótese, precisa ser pré-registrada e julgada em dados que esta rodada não tocou.

## Limites desta rodada (declarados antes de rodar)

- D4, D5 e D6 usaram as últimas 6.000 barras de cada período, e D8 as últimas 4.500. Em 1m isso dá cerca de 3 dias de julho de 2026; em 1h, cerca de 6 meses de 2024. Só D7 cobriu o período inteiro.
- Uma janela curta reduz o poder do critério 3. A regra, porém, foi fixada antes, e a diferença observada é pequena: z = 0,96 em 1m e 1,35 em 1h contra o GARCH.

## Consequência pelo plano

> Se G1 falhar, a geometria destas coordenadas não tem conteúdo próprio. A linha para, ou recebe **uma** reformulação de coordenadas, pré-registrada antes de ser rodada.

A decisão é da Ana.
