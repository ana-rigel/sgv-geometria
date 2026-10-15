# Pré-registro H-CAUDA-01 — o campo de agitação nos extremos antecipa a amplitude, num ativo nunca visto

**Registrado em 14/10/2026, antes do código confirmatório e antes de qualquer download de dados do ativo.** Ramo `confirmatorio/H-CAUDA-01-xrp`, criado a partir de `confirmatorio/H-DIF-01@174a0bb` (aproveita o código congelado do `sgv_original` e do M11-I em `vendor/`). O H-DIF-01 continua congelado e não é alterado.

## Origem da hipótese

Exploração em BTCUSDT jun–jul/2026 (ramo `exploracao/campo-regua-caudas`, `campo_caudas/RESULTADO_CAMPO_CAUDAS.md`, já corrigido). No espaço original, na régua de caudas da Ana, o campo de agitação D(x) estimado de forma localmente linear e avaliado nos minutos da faixa extrema 3 ≤ max|xⱼ| < 5 teve ρ parcial com a amplitude dos 5 minutos seguintes de **+0,125** (um minuto por bloco de 5 min do relógio, 616 janelas), contra +0,028 na nula de pipeline, com subida monotônica por quintil de D. A estimativa inicial de +0,21 era a mais favorável de cinco subamostras e foi corrigida; a faixa foi escolhida entre seis depois de ver os dados. Por isso o teste vai para um ativo e um período nunca usados.

## Dados

- **Ativo:** XRPUSDT spot, klines de 1 minuto da Binance (`data.binance.vision`, SHA-256 conferido pelos arquivos `.CHECKSUM`). Nenhum commit ou arquivo do repositório usa XRP até esta data.
- **Âncora da régua:** maio/2026 (só para mediana e escala; nenhum resultado é medido em maio).
- **Julgamento:** 01/06/2026 a 30/09/2026 (122 dias). Semanas de 7 dias a partir de 01/06; a semana k usa o campo estimado na semana k−1; a primeira semana julgada é 08–15/06; a última semana incompleta (< 5 dias) fica de fora.

## Definições congeladas

- **Coordenadas brutas:** E_norm e jerk de `build_btc_90d_input_sgv` com `SGVConfig()` padrão (`vendor/sgv_original`, ac6b986); memory_flux = E_norm.ewm(α = 0,05, adjust = False).mean().diff(). O nome da função diz BTC, mas ela só usa OHLCV.
- **Régua de caudas (Ana, `cascas_btc.py`, `orig_raw`):** por coordenada, (x − mediana de maio) / (q99,5 de |x − mediana| em maio / 3), linear.
- **Faixa:** minutos com 3 ≤ max|xⱼ| < 5. **Amostra:** de cada bloco de 5 minutos do relógio (timestamp // 5 min), o primeiro minuto da faixa, se houver.
- **D(x):** k = 200 vizinhos (cKDTree) entre os pontos da semana anterior; núcleo tricúbico no raio do 200.º vizinho; regressão localmente linear do passo s sobre [1, x − x₀]; D = traço da covariância ponderada dos resíduos × 1/(1 − 4/ESS), ESS = (Σw)²/Σw²; log ρ = −3·log(raio do 200.º vizinho).
- **Alvo:** log(max high − min low dos 5 minutos seguintes).
- **Controles:** log σ dos retornos de 10, 30 e 60 min; log σ de 1 dia e 1 semana; retornos somados de 5 e 30 min; log-volume médio de 10 e 60 min; dummies de hora UTC; log ρ.
- **Estatística:** ρ de Spearman entre os postos de log D e de log Range, cada um residualizado (MQO) nos controles, sobre todas as janelas das semanas julgadas.

## Hipótese e julgamento (único)

**H-CAUDA-01:** ρ_parcial > 0.

- **p primário:** permutação do alvo residualizado dentro de cada dia (5.000 réplicas, semente 20261014), unilateral.
- **Confirmada** se p < 0,05 **e** ρ ≥ 0,05. Caso contrário, não confirmada. Sem segunda tentativa com outro ativo, faixa, k ou período.
- **Validade:** pelo menos 600 janelas; abaixo disso, INCONCLUSIVO.
- **Secundários (só leitura):** nula de pipeline (retornos, sombras e volume permutados dentro de cada dia a partir de junho, mesma régua com a mesma âncora, semente 2026); ρ por mês; ρ por quintil de D; ρ com todos os minutos da faixa.

## Ensaio de paridade

Antes de baixar o XRP, o mesmo script roda em BTCUSDT jun–jul (modo `--paridade-btc`, mesmo conjunto de semanas da exploração) e precisa reproduzir o +0,125 da exploração com diferença < 0,005.

## Poder e aposta (antes dos dados)

Se o XRP tiver a mesma fração de minutos na faixa que o BTC (~1,4 %), serão ~1.500 janelas e o erro-padrão de ρ, ~0,03–0,04 considerando a dependência dentro dos dias. Com o efeito verdadeiro de 0,10, o poder é de ~80 %; com 0,06, de ~45 %.

**Aposta de Claude: ~35 %** de confirmação. A exploração foi pequena, a faixa foi escolhida a posteriori e a primeira estimativa estava inflada; o efeito verdadeiro, se existir, provavelmente está mais perto de 0,06 que de 0,12.
