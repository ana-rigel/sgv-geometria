# Protocolo RB-01: régua bruta para as cascas HDR50/HDR95 sob caudas pesadas

**Registrado em 15/10/2026, antes do código e de qualquer resultado.** Ramo `research/regua-bruta-caudas`, criado a partir de `confirmatorio/H-CASCA-01-ltc@a0bbfc3` (traz `vendor/u031`, `vendor/m11i` e `vendor/sgv_original`). Decisão de Ana em 15/10/2026: "registre e comece".

**Só dados sintéticos.** Nenhum dado de mercado é lido nesta etapa. BTC jun–jul/2026 entra só numa etapa posterior, com autorização própria. Outubro e novembro/2026 do BTC (reservados ao H-DIF-01 e ao H-FORMA-D-01) e XRP/LTC jun–set/2026 (gastos no H-CAUDA-01 e no H-CASCA-01) não são tocados em nenhuma etapa desta linha.

## 1. Por que

A régua que o painel usa nas escalas brutas (`cascas_btc.py` de Ana, modos `flow_raw` e `orig_raw`; reproduzida em `pipeline/confirmatorio_casca.py`) nunca foi calibrada. M8–M11 calibraram as cascas só no espaço gaussianizado e só no HDR50. Problemas já conhecidos na régua bruta:

1. O HDR50 vem de `build_shell` do M11-I sem mudança (grade 25³, extensão ±3,5, exige massa da grade entre 0,95 e 1,05). Só o HDR95 foi alargado (61³, ±10). No LTC, 15 % das janelas caíram por cobertura do HDR50.
2. HDR50 e HDR95 são cortes do mesmo GMM2. No portão oficial do C02.1, sob caudas t(ν = 3,5), o volume do HDR95 teve confiabilidade 0,42 frente ao reajuste.
3. Os limiares vêm da massa acumulada na grade, método que mostrou viés nos casos de caudas (PAINEL, turno 118).

## 2. Pergunta

Qual construção de casca, na escala bruta, (a) acerta a massa nominal, (b) não descarta janelas, (c) é estável frente ao reajuste e (d) recupera as transformações plantadas, em particular separa **caudas** de **expansão**, quando as distribuições têm caudas pesadas?

## 3. Candidatos (todos medidos sem malha)

A região é sempre R_α = {x : p̂(x) ≥ τ̂_α}. Volume, centro e forma de R_α são estimados por amostragem de importância com a própria p̂ (método do C02.1). Muda só o modelo p̂ e a regra do limiar τ̂.

| | Modelo p̂ | Limiar τ̂ | Regras de invalidez |
|---|---|---|---|
| **A, atual** | GMM2 do `build_shell` (full, reg 1e-4, n_init 2, semente 20261009) | HDR50: grade 25³ ±3,5; HDR95: grade 61³ ±10; massa acumulada na grade, como no vendor | As do vendor: cobertura da grade fora de [0,95; 1,05] (HDR50) ou [0,99; 1,01] (HDR95); limiar tocando a borda |
| **B** | O mesmo GMM2 | Hyndman: quantil (1 − α) de log p̂ em 32.000 amostras de p̂ | Região vazia |
| **C** | GMM3 (full, reg 1e-4, n_init 2, mesma semente) | Hyndman | Região vazia |
| **D** | Mistura de 2 t multivariadas (EM; ν comum escolhido por verossimilhança em {2,5; 3; 4; 6; 10; 30}) | Hyndman | Região vazia ou EM sem convergir |
| **E** | KDE gaussiana (largura de Scott) | Hyndman | Região vazia |

## 4. Gerador sintético

**Famílias** (densidade verdadeira com log p conhecido; todas com covariância anisotrópica de autovalores distintos e eixos girados):

| | Família |
|---|---|
| F0 | Gaussiana (controle) |
| F1 | t multivariada, ν = 5 |
| F2 | t multivariada, ν = 3,5 |
| F3 | t multivariada, ν = 3 |
| F4 | Marginais Johnson SU assimétricas e de cauda pesada, misturadas por uma matriz linear fixa |
| F5 | Mistura de duas t (ν = 4) separadas (bimodal pesada) |

**Régua.** Antes de qualquer janela, uma amostra-âncora de 40.000 pontos de A define a régua `orig_raw` de Ana: (x − mediana) / (q99,5 de |x − mediana| / 3), por eixo. Todas as janelas daquela família passam por essa mesma régua linear, como maio no BTC. A régua `flow_raw` (1,4826·MAD) é aplicada como secundária, só para medir a invalidez do candidato A.

**Transformações A → B** (definidas na densidade verdadeira; a verdade de cada par é calculada da própria densidade):

| Caso | B |
|---|---|
| nulo | a mesma distribuição de A, amostra independente |
| translação | A deslocada 0,5 desvio-padrão numa direção fixa |
| expansão | A escalada ×1,25 em torno do centro |
| rotação | A girada 30° |
| anisotropia | um eixo de A escalado ×1,4 |
| caudas ε | (1 − ε)·A + ε·(A escalada ×3), ε ∈ {0,05; 0,10; 0,20} |

**Tamanho.** Janelas de n = 1.500 pontos (as de 1.500 min do painel). 8 pares independentes por família × caso: 6 × 8 × 8 = 384 pares. Confiabilidade: 1 par por família × caso, 5 reajustes por janela, cada um sobre uma reamostragem com reposição da janela.

**Verdade.** τ_α, volume, centro e forma verdadeiros por amostragem de importância com a densidade verdadeira (200.000 pontos). A massa verdadeira da região estimada, P_true(R̂_α), com 20.000 pontos da distribuição verdadeira.

## 5. Medidas

Por janela: τ̂, massa interna P_p̂(R̂_α), massa verdadeira P_true(R̂_α), log V, centro e forma (tensor normalizado pelo traço), para α = 0,50 e 0,95.

Por par: Δlog V50, Δlog V95, a **feature de caudas** f = (Δlog V95 − Δlog V50)/3 (a do painel), distância entre centros do HDR50.

## 6. Portões (por família; um candidato é aprovado só se passa em todos, nas seis famílias)

| | Portão | Critério |
|---|---|---|
| G1 | Precisão numérica | mediana de \|P_p̂(R̂_α) − α\| ≤ 0,5 pp e p95 ≤ 1,0 pp, nos dois níveis |
| G2 | Validade | no máximo 2 % de janelas inválidas |
| G3 | Fidelidade | mediana de \|P_true(R̂_α) − α\| ≤ 2,0 pp no HDR50 e ≤ 1,0 pp no HDR95 |
| G4 | Confiabilidade frente ao reajuste | ICC ≥ 0,80 para Δlog V50, Δlog V95 e f (variância entre pares contra variância entre reajustes) |
| G5 | Recuperação | ρ de Spearman(f̂, f verdadeira) ≥ 0,80 sobre os pares da família; e AUC de f̂ separando caudas (ε = 0,10 e 0,20) de expansão ≥ 0,90 |

**Decisão.** Entre os aprovados, a régua escolhida é a de menor mediana de |P_true(R̂_95) − 0,95| somada nas famílias. Se nenhum for aprovado, a linha para aqui, sem dado de mercado, com o relatório de cada portão; nenhum limiar é afrouxado depois de ver os resultados. Qualquer mudança de desenho antes da execução entra como emenda datada neste arquivo.

## 7. Depois (fora deste protocolo)

Se houver régua aprovada: paridade no BTC jun–jul/2026 (exploração) contra os números do painel, e medida de quanto as conclusões de caudas mudam com a régua corrigida. Isso só roda com autorização de Ana e com protocolo próprio.

## 8. Apostas de Claude (antes de qualquer código)

| | Aprovado em todos os portões |
|---|---|
| A, atual | ~2 % (deve cair em G2 e G4 nas famílias pesadas) |
| B, GMM2 + Hyndman | ~15 % (passa G1/G2, deve cair em G3/G4 com ν ≤ 3,5) |
| C, GMM3 + Hyndman | ~20 % |
| D, mistura de t | ~45 % |
| E, KDE | ~10 % (deve cair em G3 no HDR95: núcleo gaussiano tem cauda curta) |
| Pelo menos um | ~55 % |
