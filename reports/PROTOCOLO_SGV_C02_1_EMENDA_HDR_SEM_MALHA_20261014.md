# SGV-C02.1 — Emenda prospectiva: descritores HDR sem malha (HDR12-ML)

**Data:** 14/10/2026. **Ramo:** `research/c02-1-hdr-sem-malha-20261014`, criado a partir de `research/c02-crossfamily-nonlinear-20261014@58c6b66` (registro do portão V1 bloqueado). **Status:** emenda registrada **antes** de qualquer código, treino, validação ou abertura OOD da C02.1. O protocolo C02 (`PROTOCOLO_SGV_C02_OOD_NAO_LINEAR_20261014.md`) continua valendo em tudo o que esta emenda não altera.

## 1. Por que a emenda existe

O portão V1 da C02 falhou na precisão da geometria (`C02_PORTAO_PRECISAO_V1_FALHOU_20261014.md`): 8 de 28 checagens fora de 10 % entre grades 35³ e 49³, todas em BS35, com variação de volume de até 246 % e HDR50 com 2 voxels.

**Causa mecânica identificada na leitura do código congelado do C01** (`experiments/c01_oraculo_hdr_fisher.py`): `common_bounds` define a caixa da grade como ±5σ de **cada** componente. Em BS35 o GMM3 ajusta componentes de peso ≈ 10⁻³ às observações extremas (caudas com ν = 3,5); a caixa se estende por esses componentes, a grade uniforme fica grossa demais para o núcleo e o HDR50 cai para poucos voxels. Área, volume da malha, contagem de componentes e IoU de voxels herdam esse erro. A falha é do **extrator** (grade + malha), não da densidade ajustada.

## 2. O que muda: o bloco HDR12 é substituído por HDR12-ML

Todos os descritores abaixo são calculados **sem grade, sem voxel e sem malha**. Para cada lado, a região é a mesma do C01: `R_α(p̂) = {x : log p̂(x) ≥ τ_α}`, com τ_α = quantil (1 − α) de log p̂ em `n_cut` amostras de p̂ (como em `hdr_measure`). As integrais de Lebesgue usam amostragem por importância com a própria densidade ajustada; dentro de R_α o peso 1/p̂ é limitado por 1/τ_α, logo a variância é finita.

Para α ∈ {0,50; 0,95} (6 + 6 = 12 variáveis, mesma dimensão do bloco original):

| Variável | Definição | Substitui |
|---|---|---|
| `hdr{α}_center_distance` | ‖c_B − c_A‖, c = centroide **de volume** (medida uniforme) de R_α: c = E_p̂[x·1_R/p̂] / E_p̂[1_R/p̂] | mesmo nome (antes: centro de massa da malha) |
| `hdr{α}_log_volume_ratio` | log V_B − log V_A, V = E_p̂[1_R/p̂] | mesmo nome (antes: volume da malha) |
| `hdr{α}_jaccard_loss` | 1 − V(R_A ∩ R_B) / V(R_A ∪ R_B), volumes por importância com a mistura m = ½(p̂_A + p̂_B) | `voxel_iou_loss` |
| `hdr{α}_shape_tensor_diff` | ‖S_B − S_A‖_F, S = covariância da medida uniforme em R_α (pesos 1/p̂) dividida pelo traço | mesmo nome (antes: covariância dos voxels) |
| `hdr{α}_w2_hdr` | W₂² exato (casamento ótimo) entre as observações de A no seu próprio HDR amostral (as ⌊α·750⌋ de maior p̂_A) e as de B no seu (maior p̂_B), ambas no referencial branqueado pela média e covariância amostrais de A | `log_area_ratio` |
| `hdr{α}_cross_mass_shift` | ½(|Q̂(R_A) − α| + |P̂(R_B) − α|): massa que cada densidade põe na região de alta densidade da outra | `delta_components` |

**Descartados** e por quê: área de superfície e número de componentes conexos exigem reconstrução de superfície ou de topologia; não há estimador sem malha, de custo fixo e com erro controlado, para eles. Não se tenta substituí-los por aproximações.

**Exceção declarada à regra "tudo do mesmo GMM3":** `w2_hdr` usa as **observações** A/B (ordenadas por p̂), como `energy` já fazia na base. É a variável proposta a partir do estudo W-HDR (`research`/`exploracao/u2-rotulador`, `w_hdr/RESULTADO_W-HDR.md`), em que o transporte restrito ao HDR50 foi o melhor detector de mudança de forma, sem malha.

**Consequência para a interpretação:** a C02.1 testa o bloco HDR12-ML, não o HDR12 do C01. O resultado positivo do C01 **não** se transfere a este bloco nem é reforçado ou enfraquecido por ele.

## 3. Orçamento numérico (fixo)

`n_cut = 32.000` amostras para τ_α; `n_cover = 32.000` amostras independentes para a cobertura; `n_vol = 32.000` amostras de cada densidade para volume, centroide e forma; `n_jac = 32.000` (16.000 de cada componente da mistura) para o Jaccard; `n_cross = 32.000` para a massa cruzada. Sementes por finalidade com o mesmo esquema SHA-256 do C02.

## 4. Novo portão de precisão (substitui o V1; só partição `calibration`)

Executado sobre os mesmos 35 pares do piloto V1 (5 famílias × T0–T6, índice reservado 2.000.000, mesmo gerador do pacote `SGV_C02_GERADOR_PILOTO_20261014.zip`, SHA-256 `4691266c…`, que **precisa ser integrado ao ramo byte a byte antes do portão oficial**). Para cada par, o extrator roda duas vezes com sementes de Monte Carlo independentes, uma com o orçamento da seção 3 e outra com o dobro. Critérios, todos fixados agora:

| Checagem | Limite |
|---|---|
| Cobertura de τ_α em amostras retidas, A e B, α = 0,50 e 0,95 | \|cobertura − α\| ≤ 0,015 |
| Tamanho amostral efetivo dos pesos 1/p̂ dentro de R_α | ≥ 2.000 |
| `log_volume_ratio` entre as duas execuções | \|Δ\| ≤ 0,05 |
| `center_distance` | \|Δ\| ≤ 0,10 · max(valor, 0,10 · s_A), s_A = √(tr Σ̂_A / 3) |
| `jaccard_loss` | \|Δ\| ≤ 0,02 |
| `shape_tensor_diff` | \|Δ\| ≤ 0,02 |
| `cross_mass_shift` | \|Δ\| ≤ 0,01 |
| `w2_hdr` | finito; idêntico entre execuções (não depende de Monte Carlo) |

**Regra:** o portão passa somente se **todas** as checagens passarem nos 35 pares. Uma falha bloqueia a C02.1, como no V1; não se trocam sementes, não se omitem casos e não se afrouxam limites. Pares com ajuste GMM3 inválido pelas regras do C01 contam como falha.

Um portão **substituto** (gerador local que imita a família BS35 — mistura t ν = 3,5 com banana —, não o gerador oficial) pode ser rodado e publicado como evidência de engenharia, sempre rotulado como tal; ele não substitui o portão oficial.

## 5. O que não muda

Famílias, transformações T0–T6, operador de incômodo, tamanhos (1.050 treino, 252 validação, 490 OOD selados), ajuste GMM3, base14, classificador primário (HistGradientBoosting com os hiperparâmetros da C02), secundários (logística; controle de dimensão com 12 projeções aleatórias da base), gate de validade OOD (≥ 34/35 por estrato), endpoint primário

`Delta = log_loss(HGB_base14) − log_loss(HGB_base14 + HDR12-ML)`, sucesso se `Delta ≥ 0,03` nats/par **e** limite inferior do IC 95 % (bootstrap pareado estratificado, 2.000 réplicas, semente `2026101403`) > 0.

**Secundário pré-especificado, só descritivo:** o mesmo contraste com `HDR10-ML` (sem as duas `w2_hdr`), para separar a contribuição da parte que usa as observações da parte que usa só p̂.

## 6. Ordem obrigatória

1. Esta emenda no GitHub (este commit).
2. Código do extrator + testes analíticos (gaussiana: volume exato do HDR; translação, escala e rotação com valores conhecidos).
3. Integração do gerador oficial C02 ao ramo, byte a byte, com hash conferido.
4. Portão de precisão oficial (seção 4). Se falhar, a C02.1 fica bloqueada e documentada.
5. Só então treino/validação (1.050/252), freeze com hashes e uma única liberação OOD.

## 7. Aposta (Claude, antes de qualquer número)

- Portão de precisão oficial passa: **~75 %** (o modo de falha da grade desaparece; o risco restante é cobertura em caudas pesadas e GMM3 inválido em BS35).
- Endpoint primário (Delta ≥ 0,03 e IC > 0) nas famílias OOD: **~35 %**. No meu estudo W-HDR (validação deixando uma família inteira de fora, floresta aleatória), as medidas geométricas não acrescentaram ao painel de momentos; aqui a base é mais pobre em forma (sem curtose ou cocurtose), o que favorece o bloco HDR, mas as famílias OOD exigem que a forma *generalize*.

## 8. Escopo

Sintético apenas. Nenhum dado de BTC, ETH, SOL, BNB ou humano. C01 encerrado e intocado. Nada aqui implica informação além de p̂, previsão ou efeito econômico.
