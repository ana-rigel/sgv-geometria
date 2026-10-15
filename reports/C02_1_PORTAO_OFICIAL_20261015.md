# SGV-C02.1 — Portão oficial de precisão: PASSA (com o bloco retido no mínimo e uma variável rente ao corte)

**Data:** 15/10/2026.

**Regras:** emenda C02.1 + erratas C02.1a, C02.1b e C02.1c, todas registradas antes de rodar.

**Gerador:** oficial da C02, integrado byte a byte (`vendor/sgv_c02`, zip SHA-256 `4691266c…`, 7 testes originais passam, commit `4dbe66a`).

**Pares:** 35 da partição `calibration`, índice reservado 2.000.000. São as 5 famílias (G3, S5, B3, R7, BS35) × T0–T6, com 750 + 750 observações por par.

**Execução:**
- **Script:** `scripts/c02_1c_portao_oficial.py`, commitado antes de rodar.
- **Julgamento:** rodou uma única vez; o script recusa rodar de novo.
- **Dados:** `reports/c02_1/portao_oficial.json`.
- **Orçamento:** HDR50 ×4 e HDR95 ×16.
- **Por par:** produção, dobro e 5 reajustes por reamostragem.

## Veredito: PASSA

| Critério | Resultado |
|---|---|
| ajustes GMM3 e extrações válidos | 35 / 35 |
| checagens de precisão de Monte Carlo nas variáveis retidas | nenhuma falha em 35 pares |
| bloco retido com ≥ 6 variáveis e ≥ 1 por nível | 6 (5 do HDR50, 1 do HDR95) |

## Confiabilidade frente ao reajuste (regra: ≥ 0,5 nas cinco famílias)

| Variável | G3 | S5 | B3 | R7 | BS35 | |
|---|---|---|---|---|---|---|
| hdr50_center_distance | 0,93 | 0,81 | 0,95 | 0,82 | 0,82 | retida |
| hdr50_log_volume_ratio | 0,94 | 0,84 | 0,95 | 0,95 | 0,90 | retida |
| hdr50_jaccard_loss | 0,96 | 0,96 | 0,95 | 0,96 | **0,29** | sai |
| hdr50_shape_tensor_diff | 0,96 | 0,90 | 0,96 | 0,98 | 0,93 | retida |
| hdr50_w2_hdr | 0,89 | 0,80 | 0,73 | 0,97 | **0,5016** | retida, rente ao corte |
| hdr50_cross_mass_shift | 0,98 | 0,91 | 0,97 | 0,97 | 0,82 | retida |
| hdr95_center_distance | 0,97 | 0,74 | 0,91 | 0,91 | −0,45 | sai |
| hdr95_log_volume_ratio | 0,92 | 0,73 | 0,91 | 0,95 | 0,42 | sai |
| hdr95_jaccard_loss | 0,98 | 0,84 | 0,94 | 0,95 | 0,33 | sai |
| hdr95_shape_tensor_diff | 0,98 | 0,83 | 0,90 | 0,96 | 0,82 | retida |
| hdr95_w2_hdr | 0,95 | 0,93 | 0,87 | 0,97 | −0,04 | sai |
| hdr95_cross_mass_shift | 0,97 | 0,77 | 0,95 | 0,95 | −0,56 | sai |
| envelope_core_delta (secundário) | 0,72 | 0,54 | −0,40 | −0,24 | 0,00 | — |

## Leitura

1. **O extrator sem malha é preciso nas variáveis retidas.**
   - Cobertura, ESS e diferenças entre execuções ficaram dentro dos limites em todos os 35 pares, inclusive no BS35.
   - O orçamento do C02.1c fez o que a projeção indicava.
   - A falha de grade do V1 (HDR50 com 2 voxels, volume variando até 246 %) não existe neste extrator.
2. **A família BS35 decide o bloco.** As quatro famílias sem caudas tão pesadas reteriam praticamente tudo. O BS35 (t com ν = 3,5 e banana) derruba cinco das seis variáveis do HDR95. A causa é o ajuste do GMM3 nas caudas, que muda de reamostra para reamostra. Não é o Monte Carlo.
3. **O bloco é diferente do que o substituto previa.**
   - No substituto entravam o log V e o Jaccard do HDR95.
   - No oficial sai o log V do HDR95 (0,42 no BS35) e entram a forma do HDR95 (0,82) e a forma do HDR50.
   - **Consequência:** a regra de leitura "envelope crescendo mais que o núcleo = caudas" **não** está no bloco que segue para treino. Com caudas ν = 3,5, o volume do HDR95 não é confiável frente ao reajuste.
4. **A passagem depende de uma margem mínima.**
   - A W₂ do HDR50 entrou com 0,5016 no BS35, com corte em 0,5.
   - Essa confiabilidade é estimada com 7 pares × 5 reajustes e tem ruído próprio bem maior que 0,002.
   - Com 0,4984, o bloco teria 5 variáveis e o portão estaria bloqueado.
   - **Pelas regras registradas, o portão passa.** Mas a composição do bloco (e o próprio "≥ 6") é frágil, e isso deve pesar na interpretação de qualquer resultado da C02.1.

## Apostas

- Emenda C02.1, "portão de precisão oficial passa", ~75 %: **acertou**.
- Errata C02.1c, "portão oficial passa com o C02.1c", ~80 %: **acertou**.

## Próximo passo (emenda C02.1, §6.5)

1. Treino e validação: 1.050 e 252 pares, só G3, S5 e B3.
   - Endpoint: `Delta = log_loss(HGB_base14) − log_loss(HGB_base14 + bloco retido de 6)`.
   - Controle de dimensão: 6 projeções aleatórias.
2. Congelamento com hashes.
3. Uma única liberação dos 490 pares OOD (R7 e BS35).

Nada disso foi iniciado.
