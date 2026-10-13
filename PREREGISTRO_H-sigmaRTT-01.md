# Pré-registro H-σRTT-01 — excesso de giro da régua no espaço original do SGV

**Registrado em:** 13/10/2026, antes de qualquer acesso a dados de agosto de 2026 em diante.
**Status:** congelado. A abertura do período reservado depende do OK de Ana (ver seção 9).

## 1. De onde vem

Na exploração (BTCUSDT 1m, junho–julho/2026), no espaço (E_norm, jerk, memory_flux) do sgv_original, o giro σ da régua RTT do mercado real ficou acima de três versões sem a ordem real dos retornos. Médias diárias do ensaio deste mesmo script:

| Comparação | Diferença média por dia (D) | p unilateral | Dias com real acima |
|---|---|---|---|
| Real − sinais sorteados (K = 20) | +0,0217 | < 0,0001 | 80% |
| Real − dia tocado de trás para frente | +0,0095 | 0,005 | 57% |
| Real − pipeline (minutos permutados no dia, K = 20) | +0,0147 | 0,0002 | — |

Esses números foram obtidos depois de olhar os dados e de várias comparações no mesmo período. Por isso são só a origem da hipótese, não evidência dela.

## 2. Pergunta

O giro que a régua mede no espaço original vem só do agrupamento de volatilidade e das fórmulas do SGV, ou a sequência real de retornos carrega mais estrutura, e uma estrutura com direção no tempo?

## 3. Hipóteses (família confirmatória, m = 2)

- **H1 (além da vol):** σ real > σ com os sinais dos retornos sorteados (mesmos |retornos|, mesma ordem, mesmo agrupamento de vol). Previsão: D > 0.
- **H2 (flecha do tempo):** σ real > σ do mesmo dia com os retornos tocados de trás para frente. Previsão: D > 0.

## 4. Dados

- BTCUSDT spot 1m, arquivos mensais de `data.binance.vision`, conferidos pelo SHA-256 publicado (`.CHECKSUM`).
- **Calibração (fixa, já usada):** maio/2026, para a âncora de gaussianização e os 20 nós da régua.
- **Histórico (aquecimento, não julgado):** junho–julho/2026.
- **Julgamento:** 01/08/2026 a 30/09/2026, 61 dias. Nada de outubro em diante é carregado.
- Se os arquivos tiverem buracos ou duplicatas, o script para sem calcular σ. Qualquer regra para tratá-los precisa ser registrada como emenda antes da execução seguinte.

## 5. Medida (congelada)

Tudo está em `pipeline/confirmatorio_sigma.py`:

- **Coordenadas:** sgv_original ac6b986. E_norm do construtor do input (z robusto causal de (close − EMA₀,₀₅)/EMA), jerk = Δ² do retorno, memory_flux = Δ EMA₀,₀₅(E_norm).
- **Gaussianização:** por postos, com âncora de maio.
- **Régua:** 20 nós (KMeans, random_state = 0) ajustados em maio; janela de 1.440 minutos; produção de entropia σ com pseudocontagem a = 0,5. Valor diário = média dos σ minuto a minuto do dia.
- **Nulas:**
  - Sinais sorteados: K = 20.
  - Dia invertido: 1, determinística.
  - Pipeline: K = 20, descritiva.
  - Todas só nos dias julgados; o histórico fica real.
- **Semente:** 20261013.

| Arquivo | SHA-256 |
|---|---|
| `pipeline/confirmatorio_sigma.py` | `a6250960240ab345007d1600e84d1d394dc9e6f1f209b8cb5d1900be376a5799` |
| `pipeline/sgv_rtt_operator.py` | `006700154add11497c50c0b31e6d21a9d7886139a421a1c39aa06f28a58ac03c` |
| `vendor/sgv_original/sgv/input_builder.py` | `aee0e17903f142788aa0fdfdbd4d386cf40df8e874307a334f1313a819155cdc` |
| `vendor/m11i/sgv_m11i/instrument.py` | `15ee5a5dba7f9354a6006c8bb271e517a7cb77e19e7907c72ec09f21a4f18226` |
| todos os `.py` de `vendor/` concatenados em ordem | `04f85410c6fcc52c35689f01f8cb558c8fd59b53a2358cb2ea8cf2ae598e6232` |

## 6. Estatística e decisão

- Para cada dia d: e_d = σ_real,d − referência_d. D = média dos e_d.
- **p unilateral (D > 0):** bootstrap circular em blocos de 3 dias, B = 20.000, sobre a série centrada. Os blocos levam em conta a dependência entre dias vizinhos, que compartilham a janela de 1.440 minutos.
- **Correção:** Holm com m = 2 e α familiar = 0,05. O menor p é comparado com 0,025 e, se passar, o outro com 0,05.
- O resultado vale como sair: sem reanálise, sem trocar parâmetros, sem mudar o período.

## 7. Poder (estimado na exploração)

| | Efeito igual ao observado | 2/3 do efeito | 1/2 | 1/3 |
|---|---|---|---|---|
| H1 (sinais) | ≈ 100% | 90% | 68% | 36% |
| H2 (invertido) | 68% | 37% | 23% | 13% |

H1 está bem coberta. **H2 tem pouco poder:** se for refutada, o resultado não distingue "não existe" de "existe, mas é pequeno". Esta ressalva é parte do registro.

## 8. O que cada resultado significa

- **H1 confirmada:** a sequência de direções dos retornos tem estrutura que o agrupamento de vol não explica, e as fórmulas do SGV a convertem em giro. Isso não mostra geometria própria do mercado e não diz nada sobre lucro.
- **H2 confirmada:** a sequência de retornos tem assimetria temporal visível através do espaço do SGV. Há candidatos conhecidos na literatura (efeito alavancagem, efeito Zumbach: retornos passados influenciam a vol futura mais do que o contrário). Antes de alegar algo novo, seria preciso uma nula que já incluísse esses efeitos.
- **H1 refutada:** encerra a linha "excesso de σ" no espaço original. O giro que sobra é o das fórmulas e da vol.
- **H2 refutada:** inconclusiva, pela seção 7.
- **Quem paga e por que continua pagando:** não se aplica. É uma hipótese descritiva, sem alegação de vantagem de negociação.

## 9. Consequência da abertura (decisão de Ana)

Abrir agosto–setembro gasta esse período como dado virgem. O M19 (rupturas estruturais) e o M31 (HXFB) também estavam planejados para ele. Há três caminhos:

1. Pré-registrar o M19 e o M31 antes e julgar os três na mesma abertura.
2. Abrir só para este teste e aceitar que o M19 e o M31 precisarão de outro período (outubro em diante).
3. Esperar dados novos (outubro–novembro) para este teste.

## 10. Aposta de Claude (antes dos dados, tradição da casa)

- **H1:** ~75%. O efeito é grande na exploração, e estruturas da relação entre sinal e vol costumam persistir entre períodos.
- **H2:** ~35%. A probabilidade de o fenômeno ser real fica em ~55%, mas o poder é baixo, e o efeito observado provavelmente está inflado por ter sido escolhido depois de olhar os dados.

## 11. Como executar

1. Baixar de `https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/` os arquivos `BTCUSDT-1m-2026-08.zip`, `BTCUSDT-1m-2026-09.zip` e os dois `.CHECKSUM`, e colocar em `dados/`.
2. Conferir que os SHA-256 da seção 5 batem com os arquivos do pacote.
3. Rodar `python pipeline/confirmatorio_sigma.py --periodo confirmatorio` (10–15 minutos).
4. Registrar a saída como saiu. O ensaio em junho–julho fica em `resultados/H-sigmaRTT-01_exploracao.json`.

## 12. Registro de execução (13/10/2026, antes do julgamento)

- **Decisão de Ana:** abrir agosto–setembro/2026 só para este teste. O M19 e o M31 não foram pré-registrados para esta abertura.
- **Revisão:** o `PLANO.md` prevê revisão de Ana e do colaborador antes de qualquer dado confirmatório. A revisão do colaborador não aconteceu; a abertura foi autorizada por Ana.
- **Período:** o PLANO define o confirmatório 1m de 01/08 a 31/10/2026. Este teste usa só 01/08–30/09 (o arquivo mensal de outubro ainda não existe). Outubro continua intocado.
- **Execução:** GitHub Actions do sgv-geometria, ramo `confirmatorio/H-sigmaRTT-01`, porque a sessão de análise não alcança `data.binance.vision`. O workflow (1) confere os SHA-256 da seção 5, (2) refaz o ensaio de junho–julho e só continua se o σ real diário bater com a referência (diferença máxima < 0,001), (3) baixa agosto–setembro conferindo os `.CHECKSUM` da Binance, (4) roda o julgamento e (5) grava o resultado neste ramo. Se o passo 2 falhar, o período reservado não é baixado.
