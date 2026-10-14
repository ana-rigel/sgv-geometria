# SGV-C02.1a — Errata prospectiva da emenda C02.1

**Data:** 14/10/2026. **Ramo:** `research/c02-1-hdr-sem-malha-20261014`. **Registrada antes de qualquer alteração de código** posterior ao portão substituto (`C02_1_PORTAO_SUBSTITUTO_20261014.md`, commit `7135a0b`) e antes do gerador oficial, de qualquer treino, validação ou OOD. Altera somente o que está escrito aqui; o resto da emenda C02.1 e do protocolo C02 continua valendo.

## Motivo

O portão substituto mostrou duas causas de falha:
- **(a) desenho do portão:** o limite de `center_distance` (10 % do valor) ficou abaixo do ruído de Monte Carlo do próprio extrator, inclusive em geradores de caudas leves; o limite de log V (0,05) era mais apertado que o do V1 (10 %) sem justificativa;
- **(b) mal-condicionamento do HDR95 com caudas pesadas:** volume, centroide e forma do HDR95 oscilam de amostra para amostra porque o **ajuste** do GMM3 nas caudas oscila (no substituto do BS35 sem nenhuma mudança, "envelope − núcleo" chegou a −0,53); o portão C02.1 media só o Monte Carlo e não via essa fonte.

Acrescenta-se uma observação de contexto (achados da Ana, 14/10): a separação entre caudas e expansão depende do envelope (HDR95), não do núcleo; e transformações por postos apagam caudas. A C02/C02.1 não usa transformação por postos em nenhuma etapa, e esta errata torna isso uma regra.

## Mudança 1 — limites do portão de precisão (causa a)

| Checagem | C02.1 | C02.1a |
|---|---|---|
| `center_distance` | \|Δ\| ≤ 0,10·max(valor, 0,10·s_A) | \|Δ\| ≤ max(0,10·valor, **0,05·s_A**) |
| `log_volume_ratio` | \|Δ\| ≤ 0,05 | \|Δ\| ≤ **log 1,10 = 0,0953** (o critério de 10 % do V1) |

As demais checagens (cobertura 0,015; ESS ≥ 2.000; Jaccard 0,02; forma 0,02; massa cruzada 0,01; `w2_hdr` determinístico) ficam iguais.

## Mudança 2 — variabilidade do ajuste e regra de retenção (causa b)

Para cada par de calibração, além da execução principal, **5 reajustes por reamostragem**: A e B são reamostrados com reposição (750 de 750, semente própria por réplica), o GMM3 é reajustado com as regras do C01 e o HDR12-ML é recalculado (orçamento ×1). Para cada família F e variável k:

- ruído do ajuste = média, sobre os pares de F, da variância de k entre os 5 reajustes;
- variância total = variância de k entre os pares de F (execução principal, todas as transformações);
- **confiabilidade** = 1 − ruído / total.

**Regra de retenção, fixada agora:** uma variável entra no bloco HDR da C02.1a somente se tiver confiabilidade ≥ 0,5 **em todas as cinco famílias** (G3, S5, B3, R7, BS35, partição `calibration`). Uma variável retirada sai para todas as famílias, no treino, na validação e no OOD. A regra usa só a calibração e as transformações conhecidas do gerador; não usa desempenho de classificador.

**Portão C02.1a passa** se, nos 35 pares de calibração: (i) todas as checagens de precisão de Monte Carlo (com os limites da mudança 1) passarem nas variáveis retidas; (ii) a checagem de ESS passar nos níveis cujas variáveis de medida uniforme (volume, centroide, forma) forem retidas; (iii) a cobertura passar em todos os níveis; (iv) o bloco retido tiver pelo menos 6 variáveis e pelo menos uma de cada nível (HDR50 e HDR95). Caso contrário, a C02.1a fica bloqueada.

O endpoint primário passa a ser `Delta = log_loss(HGB_base14) − log_loss(HGB_base14 + HDR-ML retido)`, com os mesmos critérios (Δ ≥ 0,03 nats/par e limite inferior do IC 95 % > 0). O controle de dimensão usa o mesmo número de projeções aleatórias que o bloco retido.

## Mudança 3 — detector de caudas sem densidade estimada (secundário pré-especificado)

`envelope_core_delta` = t_B − t_A, com t_X = log(q₉₅(r_X) / q₅₀(r_X)), r_X = raio de Mahalanobis das observações de X na média e covariância amostrais **da própria X**. É a regra "envelope crescendo mais que o núcleo = caudas" calculada direto nos pontos: invariante a translação, escala e transformação linear, sem GMM, sem malha, sem postos.

Para não confundir a atribuição ao HDR (a base14 não tem nenhuma medida de caudas), ele **não** entra no endpoint primário. Contraste secundário pré-especificado, só descritivo: `base14 + HDR-ML retido + envelope_core_delta` contra `base14 + HDR-ML retido`, e a sua confiabilidade é relatada pela mesma regra.

## Mudança 4 — regra explícita

Nenhuma etapa da C02/C02.1a usa transformação por postos, gaussianização ou qualquer reescala não linear das observações. Os branqueamentos usados (`w2_hdr`, `envelope_core_delta`) são lineares.

## Aposta (Claude, antes de rerodar o substituto)

- Retidas: as seis do HDR50, e do HDR95 apenas `jaccard_loss`, `cross_mass_shift` e `w2_hdr`; saem volume, centroide e forma do HDR95. Bloco de ~9 variáveis. **~60 %**.
- Portão C02.1a passa no substituto: **~55 %** (o risco restante é a forma do HDR50 no BS35, que já oscilou até 0,125 no Monte Carlo).
- `envelope_core_delta` com confiabilidade ≥ 0,5 em ambas as famílias substitutas: **~70 %**.
