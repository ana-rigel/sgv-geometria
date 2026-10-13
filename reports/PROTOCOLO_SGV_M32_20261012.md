# SGV-M32 — A curvatura da casca acrescenta informação de risco? (pré-registro)

**STATUS: CONGELADO** (12/10/2026, antes do código confirmatório e antes de baixar qualquer dado de SOL)
**Ramo:** `research/m32-curvatura-casca`. **`main` intocada.**
**Decisões da Ana (12/10/2026):** testar a curvatura da casca (a variável do T3 do M31, que não chegou a ser avaliada) como **hipótese própria, em amostra nova**: **SOLUSDT 1m jun–set/2026**, escolhida por ela como ativo nunca olhado; comparação principal **contra B0 + cone/cintura**.
**Origem:** M31 (T1 falhou; T3 não avaliado) e a auditoria independente do M31 (issue #3), cujas correções estão incorporadas.

## Pergunta
A **fração da área da casca HDR50 em sela** (curvatura gaussiana analítica K < 0; GMM2 na cópula local das últimas 6 h) melhora a previsão da variância realizada dos próximos 15 min **além** de um baseline forte que **já inclui** as estatísticas condicionais da forma (cone, cintura, cone × ν)?
É o único teste do projeto que credita a **geometria da casca em si**.

## Dados
- **SOLUSDT spot 1m**, arquivos mensais oficiais da Binance (checksum), **2026-05 a 2026-09**. **Maio:** só aquecimento e treino. **Avaliação:** origens em **[2026-06-01, 2026-10-01) UTC** com alvo disponível.
- Se algum mês faltar ou falhar no checksum, o teste não roda. Lacunas: regra de segmentação (cada trecho reaquece do zero).

## Código congelado
- `experiments/m32_casca.py` (SHA-256 `42249e3d38b2da4889d5a5f90d47fcc2ca06edbbca2e1b512b4009b98abb78a5`), que reutiliza sem alteração `experiments/m31g1_engenharia.py` (SHA-256 `f8a277236f74554e6dc3016571b620ec70b578a3be65b10bb4ef9912c7072476`). Commit `1b2ebf74bd1aaa4431c2f75417dfe002db0b5ba9`.
- **Correções da auditoria incorporadas:** (1) a origem é **elegível para previsão só com o passado**; a existência do alvo decide apenas se ela entra na avaliação; (2) o treino usa só rótulos maturados, finitos e positivos; (3) a dependência é julgada em duas escalas (abaixo); (4) o poder vem de **ganho plantado**, não de aproximação.
- Treino móvel de 1.344 origens (14 dias), ridge 100 em log-RV com *smearing*; janela da forma de 360 min; casca HDR50 GMM2, grade 35³, semente 20261012.

## Modelos
- **B1** = B0 (log-RV 15/60/240/1440, HARQ, Parkinson 15/60, semivariância 60, log-volume 15/60, ν, |ι| 15, 3 indicadores de quarto de hora, 3 harmônicos da hora do dia, dia da semana) + log-cone + cintura + log-cone × ν.
- **B1S** = B1 + `saddle_frac`.
- O teste usa só as origens em que a casca é válida (malha fechada, não truncada, cobertura ≥ 95%). **Os dois modelos são estimados e avaliados nesse mesmo subconjunto.**

## Critério (primário único)
Deviança QLIKE por origem; Δ = d(B1S) − d(B1); skill = 1 − média d(B1S)/média d(B1).
**Passa** se, ao mesmo tempo:
- p unilateral < 0,05 com EP HAC de Newey–West de **1 dia (96)**;
- p unilateral < 0,05 com EP HAC de **1 semana (672)**;
- **skill ≥ 0,5%**.

Descritivos (sem decisão): bootstrap circular em blocos de 1 dia e de 1 semana; skill por mês; fração de casca válida; skill de B1 contra o mesmo B1 sem forma (B0), só para contexto.

## Poder (por ganho plantado, BTC mai–jul já gasto, `reports/m32/poder_plantado.json`, ~7.300 origens)
| ganho plantado | aprovações (10 réplicas) |
|---|---|
| 0 | 0% |
| ~0,4% | 20% |
| ~0,8% | 60% |
| ~2,0% | 100% |

O SOL jun–set deve ter ~11.700 origens (~1,6× mais), o que estreita o erro em ~20%. **Leitura honesta:** um negativo exclui com boa confiança ganhos ≥ ~1%; ganhos entre 0,5% e 1% podem passar despercebidos.

## Aposta de Claude (antes dos dados)
| Item | Aposta |
|---|---|
| Primário passa | ~5% |
| Skill pontual > 0 (só o sinal) | ~45% |

## Regras
Mudanças após este commit só de engenharia, registradas. O código confirmatório recusa rodar se o SHA-256 deste protocolo ou dos dois módulos não conferir. Ensaio prévio só com dados sintéticos. Não reabrir SOL jun–set para outros indicadores depois do resultado.
