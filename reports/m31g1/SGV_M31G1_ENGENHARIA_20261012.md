# SGV M31-G1 — Engenharia (sem teste de hipótese)

**Ramo:** `research/m31g1-engenharia` (a partir de `research/m31g0-engenharia-causal`). **`main` intocada. Nenhum dado reservado, nenhum ETH.** Dados: só BTCUSDT 1m mai–jul/2026 (já explorado) e sintético.
**Não calculado, de propósito:** desempenho de B0+, B1 ou B1+ (qualquer coisa que informe sobre a hipótese H-G′).

## 1. O que foi construído
- **Variáveis de forma originais** (`shape_original`), idênticas a `scripts/forma_movimento.py` @ `e1e86b1` (teste de igualdade numérica ≤ 1e-12): cópula local da janela de 6 h; cone = razão de dp de u_z entre tercis de u_ν; cintura = massa central da diagonal compra/venda nos 40% de maior volume ÷ 0,2358.
- **B0 forte:** log-RV 15/60/240/1440; HARQ (½·log RQ₆₀ − log RV₆₀ e interação com log RV₁₅); amplitude de Parkinson 15/60; fração de semivariância negativa (60); log-volume 15/60; ν; |ι| médio 15; **3 indicadores de quarto de hora**; 3 harmônicos da hora do dia; dia da semana.
- **B0+ (controle de atribuição):** B0 + elasticidade móvel volatilidade–volume (inclinação de |z| em ν nas mesmas 6 h ÷ média de |z|) + interação com ν_t. Correlação entre log-cone e elasticidade: **0,63** (parentes, não iguais).
- **B1 = B0 + forma; B1+ = B0+ + forma.**
- **Regra de lacunas:** a série é dividida em trechos contínuos; nenhuma janela, defasagem ou alvo atravessa uma lacuna; cada trecho reaquece do zero (mínimo de 1.500 + 1.440 + 1 minutos). Testada.
- **Previsão:** regressão ridge em log RV₁₅ com *smearing*, só com rótulos já maturados, refeita a cada origem.

## 2. Testes (5, todos aprovados)
Igualdade com a definição original; mexer no futuro não muda nenhuma variável no instante t; lacuna não é atravessada e o trecho após a lacuna é calculado como se o anterior não existisse; indicadores de quarto de hora exatos; previsões não usam rótulos ainda não maturados.

## 3. Achado de desenho: o ruído de estimação viesava o teste
Três variáveis **placebo** (ruído AR(1) com a persistência do cone, sem nenhuma informação) somadas ao B0 com 7 dias de treino e ridge 1 **pioravam** a QLIKE em ~0,9–1,1%. Com isso, a forma precisaria de ~2% de informação real para aparecer com 1% de ganho. Escolha feita **só com B0 e placebos** (`reports/m31g1/grade_placebo.json`):

| treino | ridge | deviança B0 | penalidade dos placebos |
|---|---|---|---|
| 7 dias | 1 | 0,3418 | 1,07% |
| 7 dias | 100 | 0,3372 | 0,40% |
| **14 dias** | **100** | **0,3322** | **0,15%** |
| 21 dias | 100 | 0,3324 | 0,15% |

**Fixado: 14 dias de treino, ridge 100.** O B0 também fica melhor.

## 4. Poder (com a configuração fixada, 20 sementes de placebo)
- Origens avaliadas: 7.290; deviança média do B0: 0,346; erro-padrão HAC (1 dia) da diferença média: 0,00076.
- **Tamanho:** 0 de 20 placebos rejeitaram H0 a 5% unilateral (teste levemente conservador; penalidade média 0,16%).
- **Efeito mínimo detectável (80% de poder, 3 meses ≈ 8.600 origens): skill ≈ 0,5%.** Poder para skill de 1%: ≈ 100%.
- Consequência: o limiar de relevância de **1%** é bem detectável. Um resultado negativo com este poder **é informativo**.

## 5. Pendente para o pré-registro (decisão da Ana)
1. Dados de teste: ETHUSDT 1m (confirmar que nunca foi olhado) e/ou BTC out–dez/2026 junto do H-FR, ou jan–mar/2027. Período de aquecimento de 14 dias **antes** do início da avaliação.
2. Hierarquia de hipóteses: primário **B1 vs B0** (ΔQLIKE < 0, DM-HAC 1 dia, unilateral 5%, e skill ≥ 1%); atribuição **B1+ vs B0+** como segundo teste com α próprio (ou hierárquico: só testado se o primário passar).
3. Variável nativa da casca (área em sela/déficit convexo): incluir como teste separado ou deixar de fora.
