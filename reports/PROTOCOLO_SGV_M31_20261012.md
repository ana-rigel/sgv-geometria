# SGV-M31 — A forma acrescenta informação de risco além da econometria? (pré-registro)

**STATUS: CONGELADO** (12/10/2026, antes de escrever o código confirmatório e antes de baixar qualquer dado de ETH)
**Ramo:** `research/m31g1-engenharia`. **`main` intocada.**
**Decisões da Ana (12/10/2026):** teste confirmatório em **ETHUSDT 1m jun–set/2026**; ela confirma nunca ter olhado ETH 1m em nenhum projeto; incluir a variável nativa da casca como 3º teste. Discussão completa no issue #3.

## Pergunta
O estado geométrico da distribuição (retorno z, agressão ι, volume ν) nas últimas 6 h — descoberto pela análise das cascas — melhora a previsão da variância realizada dos próximos 15 min além de um baseline econométrico forte? E, se melhorar, o mérito é da forma ou de uma elasticidade móvel volatilidade–volume que a econometria já mede?

## Dados
- **ETHUSDT spot 1m**, arquivos mensais oficiais da Binance (data.binance.vision, com checksum), **2026-05 a 2026-09**.
- **Maio:** só aquecimento e treino (nenhuma origem avaliada). **Avaliação:** origens com início em **[2026-06-01 00:00, 2026-10-01 00:00) UTC**; o alvo de 15 min precisa estar inteiro dentro de um trecho contínuo.
- Se algum mês não existir ou falhar no checksum, o teste não roda.
- **Status:** ETH 1m nunca usado no projeto (confirmado pela Ana). É replicação **fora do ativo**: os parâmetros e escolhas vieram só do BTC (mai–jul/2026) e de placebos.

## Código congelado
`experiments/m31g1_engenharia.py` no commit **`77ceaa78427d1eca377f830452f3b420b082a742`** (SHA-256 do arquivo `f8a277236f74554e6dc3016571b620ec70b578a3be65b10bb4ef9912c7072476`), sem nenhuma alteração: variáveis, regra de lacunas, `rolling_forecasts` (treino de **1.344 origens = 14 dias**, ridge **100** em log-RV com *smearing*, só rótulos maturados), forma original (janela de 360 min, cópula local), casca (HDR50 GMM2, grade 35³, semente 20261012).

## Modelos
- **B0** (forte): log-RV 15/60/240/1440, HARQ, Parkinson 15/60, fração de semivariância negativa 60, log-volume 15/60, ν, |ι| médio 15, 3 indicadores de quarto de hora, 3 harmônicos da hora do dia, dia da semana.
- **B0+** = B0 + elasticidade móvel (6 h) + elasticidade × ν_t.
- **B1** = B0 + log-cone + cintura + log-cone × ν_t.
- **B1+** = B0+ + as mesmas variáveis de forma.
- **B2** = B1+ + fração da área da casca HDR50 em sela.

## Régua e inferência
- Perda: deviança QLIKE d = RV/v − log(RV/v) − 1 por origem (origens a cada 15 min, alvos sem sobreposição).
- Diferença pareada Δ_t = d(modelo novo) − d(referência); estatística z = média(Δ)/EP, com **EP HAC de Newey–West (Bartlett, defasagem 96 = 1 dia)**; p unilateral = Φ(z).
- **Skill** = 1 − média(d novo)/média(d referência).

## Hipóteses, em hierarquia (cada uma só é testada se a anterior passar; erro tipo I familiar ≤ 5%)
1. **T1 (primário): B1 vs B0.** Passa se **p < 0,05 e skill ≥ 1,0%**.
2. **T2 (atribuição): B1+ vs B0+.** Passa se **p < 0,05 e skill ≥ 0,5%**.
3. **T3 (geometria intrínseca): B2 vs B1+**, só nas origens em que a casca é válida (malha fechada, não truncada, cobertura ≥ 95%); os dois modelos são reestimados nesse mesmo subconjunto. Passa se **p < 0,05 e skill ≥ 0,5%**.

**Leitura:**
- T1 falha → a forma não acrescenta informação de risco relevante a um baseline forte; a linha se encerra.
- T1 passa e T2 falha → **contribuição de descoberta**: a forma apontou algo que a elasticidade móvel captura.
- T1 e T2 passam, T3 falha → a informação está nas estatísticas condicionais da forma, não na casca em si.
- T1, T2 e T3 passam → contribuição geométrica intrínseca.

## Descritivos (sem decisão)
Skill de B0+ vs B0; skill de B1 vs B0 por mês; p por bootstrap circular em blocos de 1 dia para T1; fração de origens com casca válida; número de trechos e lacunas.

## Poder (do BTC, `reports/m31g1/`)
Com ~11.700 origens avaliadas, efeito mínimo detectável a 80% ≈ 0,45% de skill; poder ≈ 100% para 1%. O tamanho sob placebo foi conservador (0/20 rejeições). Um negativo é informativo.

## Apostas de Claude (antes dos dados)
| Item | Aposta |
|---|---|
| T1 passa | ~12% |
| T1 e T2 passam | ~6% |
| T1, T2 e T3 passam | ~2% |
| B0+ melhora o B0 em ≥ 0,5% (descritivo) | ~30% |

## Regras
Mudanças depois deste commit só de engenharia, registradas. O código confirmatório recusa rodar se o SHA-256 deste protocolo ou do arquivo `m31g1_engenharia.py` não conferir. Ensaio prévio do pipeline só com dados **sintéticos** (nenhum desempenho de B1 em BTC ou ETH é olhado antes).
