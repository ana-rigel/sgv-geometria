# SGV-M15 — Forma × persistência, e a geometria contra comparadores simples (pré-registro)

**Data:** 09/10/2026. **Ramo:** `research/m15-forma-persistencia-comparadores` (a partir de `research/m14-calibracao-aninhada-nulos@7f55022`). **`main` intocada. Nenhum dado BTC é lido** — nem exploratório, nem confirmatório.
**Autoria:** desenho de Claude a pedido da Ana, depois de ler os resultados do M14 (VAR→VAR 6,2%; HMM→HMM 7,3%; HMM→VAR 57,6%; HMM→blocos15 16,2%).
**Este documento é commitado antes do código que executa o experimento; nenhum resultado M15 foi visto.** (Só se mediu o tempo de 1 ensaio com semente de desenvolvimento diferente da semente registrada, sem inspecionar postos.)

## Perguntas

1. **Persistência:** com a forma conjunta certa e sem memória, quanto o M11 ainda alarma? (contraste com o HMM correto)
2. **Forma:** quanto do alarme do VAR vem só de ele ter a forma errada (gaussiana unimodal vs mistura)?
3. **Dose:** a taxa cai quando o bloco do bootstrap se aproxima/ultrapassa a duração dos regimes (tempo integrado de correlação do estado ≈ 47 passos)?
4. **A geometria das cascas diz algo além da covariância?** M11 contra a distância de Fisher–Rao entre covariâncias das metades.
5. **…e além de uma distância distribucional genérica?** M11 contra a energy distance entre metades.

## Desenho (congelado)

- **Verdade principal:** o mesmo Markov de 2 regimes do M14 (`truth_hmm`, parâmetros idênticos), prefixo 2000 + janela 1500. **500 ensaios externos**, semente base `2026101015` via `SeedSequence([base, verdade, ensaio, papel, nulo, k])`.
- **Seis nulos, todos ajustados só no prefixo do mesmo ensaio**, cada um com 19 referências, e **a mesma janela observada** ranqueada contra todos (contrastes pareados):

| Nulo | Forma conjunta | Persistência | Papel |
|---|---|---|---|
| `HMM` (2 estados, cov. completa; = M14) | certa | certa | referência calibrada |
| `GMM_IID` (mistura gaussiana 2 comp., IID) | certa | nenhuma | **isola persistência** |
| `VAR` (VAR(1) gaussiano; = M14) | errada | parcial (linear) | **isola forma** (vs GMM_IID) |
| `B15`, `B60`, `B150` (blocos circulares do prefixo) | exata (linhas reais) | até L | **dose** |

- **Controle de calibração dos comparadores:** verdade `VAR` com nulo `VAR`, 500 ensaios.
- **Três estatísticas nas MESMAS metades gaussianizadas** (`split_historical`, idêntico a M11/M14) de cada trajetória:
  - `m11`: distância HDR50 do M11, inalterada (512 pontos);
  - `fr_cov`: distância de Fisher–Rao entre N(0,Σ₁) e N(0,Σ₂) = √(½ Σ log² λᵢ(Σ₁⁻¹Σ₂)) — geometria da informação intrínseca, invariante a mapas lineares;
  - `energy`: energy distance amostral entre as metades.
- **Alarme:** posto de Monte Carlo `p_rank=(1+#(ref≥obs))/20 ≤ 0,05` (observado acima das 19 referências), como no M14. Estatística inválida é registrada como inválida, nunca substituída; o contraste pareado usa só ensaios válidos nos dois braços.
- **Execução:** GitHub Actions — testes + piloto (2 HMM + 2 VAR, portão de engenharia: tudo válido, alarmes não inspecionados) → 100 shards HMM × 5 ensaios + 20 shards VAR × 25 → agregação que falha fechada se faltar qualquer ID → commit automático de todos os JSON e tabelas na branch.

## Testes e critérios (congelados)

McNemar exato pareado, **unilateral** (A alarma mais que B):

| Código | A | B | α |
|---|---|---|---|
| Q1 persistência | GMM_IID / m11 | HMM / m11 | 0,05 |
| Q2 forma | VAR / m11 | GMM_IID / m11 | 0,05 |
| Q3 dose | B15 / m11 | B150 / m11 | 0,05 |
| Q4 (×4) | m11 | fr_cov, nos nulos VAR, GMM_IID, B15, B60 | 0,0125 cada (Bonferroni) |
| Q5 (×4) | m11 | energy, nos mesmos 4 nulos | 0,0125 cada |

**Leituras pré-acordadas:**
- Q1 significativo → "a persistência dos regimes pesa no M11 neste gerador". Não significativo → "efeito de persistência não detectado com n=500" (não "ausente").
- Q2 significativo → "a forma da distribuição conjunta pesa no M11".
- **"As cascas carregam informação além da covariância (neste gerador)"** só se ≥1 contraste Q4 for significativo **e** a taxa do `fr_cov` nos cenários corretos (HMM→HMM, VAR→VAR) não estiver mais de 2 p.p. abaixo da do `m11` (senão a vantagem pode ser só calibração diferente — rotular como tal).
- Idem para Q5 com a energy distance.
- Se o `fr_cov` ou a `energy` alarmarem **mais** que o M11 (visível nas colunas "só A / só B"), registrar sem teste formal: o comparador barato é pelo menos tão sensível.
- Reprodução do M14: as taxas M11 de HMM→HMM, HMM→VAR e HMM→B15 devem cair perto dos intervalos do M14; desvio grande = investigar instrumento antes de interpretar.

## Apostas de Claude (antes de qualquer resultado)

| Item | Aposta |
|---|---|
| HMM→HMM, M11 | 5–10% (reproduz o 7,3%) |
| HMM→GMM_IID, M11 | 8–20%; **P(Q1 significativo) ≈ 55%** |
| HMM→VAR, M11 | 50–65%; **P(Q2 significativo) ≈ 90%** |
| Blocos, M11 | B15 12–20%, B60 7–13%, B150 5–10%; **P(Q3 significativo) ≈ 75%** |
| fr_cov em HMM→VAR | ≥ M11 com P ≈ 60% |
| **P(≥1 Q4 significativo)** — cascas além da covariância | **≈ 25%** |
| **P(≥1 Q5 significativo)** — cascas além da energy distance | **≈ 20%** |
| fr_cov calibrado em VAR→VAR (Wilson contém 5%) | ≈ 70% |

Raciocínio: as verdades sintéticas são misturas gaussianas; quando a ocupação dos regimes muda entre as metades, a covariância muda junto, então o comparador de 2ª ordem deve capturar a maior parte do sinal. O M11 só ganharia onde a deformação é de forma sem mudança de covariância — possível na bimodalidade, mas não espero que domine.

## Limites declarados

- Mundo sintético de misturas gaussianas: "forma além da covariância" aqui é essencialmente bimodalidade; caudas, assimetrias e não-linearidades reais do BTC não estão representadas. **Nada se transfere automaticamente ao BTC.**
- O tamanho de cada estatística sob nulo correto é medido, não assumido; R=19 não permite limiares mais finos que 5%.
- Comparar sensibilidade entre estatísticas só é justo com calibrações parecidas — por isso a regra dos 2 p.p.
