# SGV-C02.1a — Portão substituto com variabilidade do ajuste: bloqueado por orçamento de Monte Carlo no HDR95

**Data:** 14/10/2026. **Natureza:** engenharia; **não** é o portão oficial (gerador substituto, não o oficial da C02). Errata registrada antes deste código: `PROTOCOLO_SGV_C02_1A_ERRATA_20261014.md` (commit `ba40067`). Script: `scripts/c02_1a_portao_substituto.py`; dados: `reports/c02_1/portao_substituto_a.json`. 42 pares (G3 e BS35 substitutos × T0–T6 × 3 réplicas); por par, execução ×1 e ×2 e 5 reajustes do GMM3 em reamostras. Nenhum ajuste de GMM3 inválido. 12 testes do extrator passam.

## Confiabilidade frente à variabilidade do ajuste (regra: ≥ 0,5 nas duas famílias)

| Variável | G3 | BS35 | |
|---|---|---|---|
| hdr50_center_distance | 0,96 | 0,90 | retida |
| hdr50_log_volume_ratio | 0,94 | 0,82 | retida |
| hdr50_jaccard_loss | 0,98 | 0,87 | retida |
| hdr50_shape_tensor_diff | 0,97 | 0,45 | sai |
| hdr50_w2_hdr | 0,97 | **−0,61** | sai |
| hdr50_cross_mass_shift | 0,98 | 0,74 | retida |
| hdr95_center_distance | 0,96 | 0,30 | sai |
| hdr95_log_volume_ratio | 0,94 | 0,71 | retida |
| hdr95_jaccard_loss | 0,97 | 0,68 | retida |
| hdr95_shape_tensor_diff | 0,98 | 0,24 | sai |
| hdr95_w2_hdr | 0,98 | **−0,64** | sai |
| hdr95_cross_mass_shift | 0,99 | 0,79 | retida |
| envelope_core_delta (secundário) | −0,16 | 0,08 | — |

Bloco retido: **7 variáveis** (4 do HDR50, 3 do HDR95), atendendo ao mínimo de 6 com os dois níveis.

## Veredito do portão: BLOQUEADO

Quatro checagens falham, todas no HDR95 do BS35 e todas de **orçamento de Monte Carlo**, não de instabilidade da medida:

| Par | Falha | Valor | Limite |
|---|---|---|---|
| BS35·T0·1 | \|Δ\| Jaccard HDR95 | 0,0214 | 0,02 |
| BS35·T6·0 | \|Δ\| Jaccard HDR95 | 0,0295 | 0,02 |
| BS35·T3·0 | ESS HDR95, orçamento ×1 | 1.648 | 2.000 (com ×2: 3.464) |
| BS35·T4·2 | ESS HDR95, orçamento ×1 | 1.624–1.725 | 2.000 (com ×2: 3.276–3.782) |

## Apostas (registradas na errata)

- Retidas "as seis do HDR50 e do HDR95 só Jaccard, massa cruzada e W₂", ~60 %: **errou**. O log-volume do HDR95 ficou (0,71) e as duas W₂ saíram.
- Portão passa no substituto, ~55 %: **errou** (falha por orçamento).
- `envelope_core_delta` confiável, ~70 %: **errou** (≈ 0 nas duas famílias).

## Leitura

1. **O W₂-HDR, que eu propus, não aguenta caudas pesadas.** Confiabilidade −0,6 no BS35: reamostrar observações com caudas ν = 3,5 duplica pontos extremos, e o W₂ ao quadrado é dominado por eles. A vantagem que ele teve no W-HDR (famílias gaussiana, t₆ e assimétrica leve) não se estende a ν = 3,5.
2. **O volume do HDR95 é mais robusto ao reajuste do que o centro e a forma.** Isso preserva a regra de leitura "envelope crescendo mais que o núcleo = caudas" no bloco (hdr50 e hdr95 log-volume retidos).
3. **O detector de caudas nos pontos não discrimina neste substituto.** Só a T6 é "cauda" (5 % num modo distante), e o quociente de quantis de raio varia mais entre reamostras do que entre as transformações.
4. **A barreira que sobra é custo computacional, não geometria:** dobrar o orçamento do HDR95 já levaria o ESS acima de 2.000; o Jaccard pede cerca de ×4 para que o ruído caia à metade (0,0295 → ~0,015).

## Próximo passo possível (decisão da Ana)

Errata C02.1b, uma única mudança: orçamento ×4 apenas no HDR95 (128.000 amostras para limiar, cobertura, volume, Jaccard e massa cruzada), registrada antes de rerodar. **Ressalva sobre caminhos bifurcados:** cada errata está sendo registrada antes da execução, e nenhuma usa desempenho de classificador; mas iterar erratas sobre o mesmo substituto até passar é ajustar o instrumento a um gerador de imitação. Por isso o portão que conta continua sendo o **oficial**, com o gerador da C02 integrado byte a byte, julgado uma única vez pelas regras vigentes no momento.
