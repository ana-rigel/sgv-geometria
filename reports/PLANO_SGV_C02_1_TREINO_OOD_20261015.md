# SGV-C02.1 — Plano congelado de treino, validação e liberação OOD

**Data:** 15/10/2026. **Ramo:** `research/c02-1-hdr-sem-malha-20261014`.

**Quando foi registrado:** depois do portão oficial (PASSA, commit `db3c975`) e da autorização da Ana para seguir. Antes de gerar qualquer par de treino, validação ou OOD.

**Base:** detalha a execução do protocolo C02 (§ Coleta, Modelos, Portões 3–7) com as mudanças da emenda C02.1 e das erratas C02.1a/b/c. Onde este plano e aqueles documentos coincidem, valem aqueles. Aqui só se fixa o que eles deixam em aberto.

## 1. Pares

| Partição | Famílias | Classes | Réplicas | Pares |
|---|---|---|---|---|
| `training` | G3, S5, B3 | T0–T6 | 0–49 | 1.050 |
| `validation` | G3, S5, B3 | T0–T6 | 0–11 | 252 |
| `ood_test` | R7, BS35 | T0–T6 | 0–34 | 490 |

**Geração:** `pair_samples(família, classe, réplica, split=…)` do gerador oficial (`vendor/sgv_c02`, sem alteração), com 750 + 750 observações. As sementes vêm do `seed_for` do gerador, e a partição faz parte da chave SHA-256. Por isso treino, validação, calibração e OOD são disjuntos por construção.

**Liberação da OOD:** o `seed_for` oficial recusa `ood_test`. Na liberação única, o executor substitui **só** essa função, em memória, por outra com a fórmula idêntica:

```
int.from_bytes(sha256(f'C02|2026101402|{split}|{família}|{classe}|{réplica}|{finalidade}').digest()[:8], 'big')
```

- Ela aceita `ood_test` apenas para R7 e BS35 e mantém as outras recusas.
- `pair_samples` roda inalterado.
- Nenhum par `ood_test` é gerado antes do commit de congelamento (§6).

## 2. Medidas por par (mesmas em todas as partições)

**Sementes do extrator:** a partir de s = `seed_for(split, família, classe, réplica, 'c02_1|extrator')`. Daí, `subseed(s, finalidade)` para `fitA`, `fitB`, `entropy`, `fr_ambient` e `ml`, no mesmo esquema do portão oficial.

**Ajuste:** GMM3 do C01 (`estimate_gmm`: 3 componentes, `n_init` 3, `reg_covar` 1e-4, `tol` 1e-4, `max_iter` 300).

**Base 14:** as definições do C01 (`baseline_features`), com MC de **32.000**, como fixa o protocolo C02:
- `delta_mu_0..2` e seis `delta_cov_ij`;
- `logdet_cov_delta`;
- `entropy_delta`;
- `fr_cov`;
- `fr_ambient`;
- `energy` (dos dados A/B).

**Bloco HDR (primário):** as **6 variáveis retidas no portão oficial**:
- `hdr50_center_distance`, `hdr50_log_volume_ratio`, `hdr50_shape_tensor_diff`, `hdr50_w2_hdr`, `hdr50_cross_mass_shift`;
- `hdr95_shape_tensor_diff`.

Elas vêm do extrator HDR12-ML com o orçamento do C02.1c (HDR50 ×4, HDR95 ×16, scale 1). As 12 variáveis são calculadas e guardadas, mas só as 6 entram no braço primário.

**Secundário:** `envelope_core_delta`.

**Par inválido:** é inválido se qualquer ajuste ou extração falhar (regras fail-closed do C01 e do C02.1). Ele é registrado com o motivo e excluído, sem imputação e sem reposição.
- **Treino e validação:** os inválidos são só relatados.
- **OOD:** vale o gate do protocolo, com pelo menos **34 de 35** válidos em cada um dos 14 estratos família × classe. Abaixo disso, o resultado é **INCONCLUSIVO**.

## 3. Modelos (ajustados só nos 1.050 de treino; a validação nunca entra em ajuste)

**Primário:** `HistGradientBoostingClassifier(learning_rate=0.06, max_iter=180, max_leaf_nodes=15, l2_regularization=1.0, early_stopping=False, random_state=20261014)`, em dois braços:
- **base14:** 14 variáveis;
- **base14 + HDR6:** 20 variáveis.

**Secundários (só leitura):**
- `StandardScaler + LogisticRegression(C=1, solver='lbfgs', max_iter=2000)` nos dois braços;
- **controle de dimensão:** HGB em base14 + 6 projeções lineares aleatórias da base14 padronizada.
  - Média e desvio vêm do treino.
  - Matriz 14×6 normal padrão, com semente = 8 primeiros bytes de sha256('C02|2026101402|projecoes');
- **HDR sem W₂:** HGB em base14 + as 5 retidas sem `hdr50_w2_hdr` (o "HDR10-ML" da emenda, restrito ao bloco retido);
- **envelope:** HGB em base14 + HDR6 + `envelope_core_delta`, contra base14 + HDR6.

## 4. Validação (descritiva, sem alterar nada)

Na validação se relatam, para cada braço:
- log-loss média;
- balanced accuracy;
- macro-F1;
- log-loss por família e classe.

Nenhum número da validação altera código, variáveis, hiperparâmetros ou critérios.

## 5. Endpoint primário e julgamento (OOD, único)

**Perda por par:** ℓ = −log p̂(classe verdadeira), com p̂ limitado a [1e-15, 1].

**Endpoint:** `Delta` = média, sobre os pares OOD válidos, de ℓ(base14) − ℓ(base14 + HDR6).

**Intervalo:** IC 95 % por bootstrap pareado e estratificado nos 14 estratos família × classe.
- Reamostragem com reposição dentro de cada estrato, com o tamanho válido do estrato.
- 2.000 réplicas, semente `2026101403`, percentis 2,5 e 97,5.

**Sucesso:** `Delta ≥ 0,03` nats/par **e** limite inferior do IC > 0. Caso contrário, **falha**, e a C02 se encerra sem otimizar as mesmas 490 observações.

**Secundários (só leitura):**
- tudo da §4, na OOD e por família;
- os contrastes da §3;
- Brier multiclasse e ECE em 10 faixas da probabilidade máxima.

## 6. Ordem

1. Este plano (commit).
2. Código de extração e checagem oracular.
   - O gate 1 do protocolo é refeito: para cada família, distância de energia entre A e B em T0 e em T3, com 3 pares de calibração na réplica 2.000.100+.
   - T3 precisa ficar acima de T0 em todas as famílias, inclusive R7.
3. Extração de treino e validação, ajuste dos modelos e relatório descritivo da validação.
4. **Congelamento:** commit com hashes do código, das features de treino, das versões (sklearn, numpy) e dos modelos serializados.
5. **Liberação única da OOD:** extração dos 490 pares, gate de validade, endpoint e secundários, publicados como saírem.

## 7. Aposta

Mantém-se a aposta registrada na emenda C02.1: **~35 %** de sucesso do endpoint primário. O bloco retido é só do núcleo (HDR50) mais a forma do HDR95, e o BS35 é justamente a família que derrubou o HDR95. A generalização da forma para famílias novas é o risco principal.
