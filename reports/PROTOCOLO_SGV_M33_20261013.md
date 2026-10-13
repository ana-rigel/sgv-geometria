# SGV-M33 — T3 original: a curvatura da casca acrescenta algo além da forma e da elasticidade? (pré-registro)

**STATUS: CONGELADO** (13/10/2026, antes do código confirmatório e antes de baixar qualquer dado de BNB)
**Ramo:** `research/m33-t3-original`. **`main` intocada.**
**Pedido da Ana (13/10/2026):** executar o T3 **original** do M31 — **B0 + forma + elasticidade + curvatura** contra **B0 + forma + elasticidade** — como teste **confirmatório próprio** em **BNBUSDT 1m jun–set/2026**, ativo escolhido por ela como nunca olhado.

## Relação com testes anteriores
- No M31 (ETH), o T3 estava congelado, mas não foi avaliado: o T1 falhou e a hierarquia fechou.
- O M32 (SOL) testou a curvatura contra B0 + forma, **sem** a elasticidade nos dois modelos; falhou (skill +0,02%).
- Aqui está a especificação exata do T3 original, com as correções da auditoria do M31 (elegibilidade só pelo passado; treino só com rótulos válidos; dependência julgada em 1 dia e 1 semana).

## Dados
- **BNBUSDT spot 1m**, arquivos mensais oficiais da Binance (checksum), **2026-05 a 2026-09**. **Maio:** só aquecimento e treino. **Avaliação:** origens em **[2026-06-01, 2026-10-01) UTC** com alvo disponível.
- Se faltar um mês ou falhar o checksum, o teste não roda. Lacunas: segmentação com reaquecimento.

## Código congelado (commit `e707c75beaca0ff7b4c1539d979fc2c737924573`)
- `experiments/m33_t3.py` — SHA-256 `4b907dc6712483485e4535facff5bf9e16f18c30f1c7a607cd29cd7d56a5b09d`
- `experiments/m32_casca.py` — `42249e3d38b2da4889d5a5f90d47fcc2ca06edbbca2e1b512b4009b98abb78a5`
- `experiments/m31g1_engenharia.py` — `f8a277236f74554e6dc3016571b620ec70b578a3be65b10bb4ef9912c7072476`

Configuração: treino móvel de 1.344 origens (14 dias), ridge 100 em log-RV com *smearing*; janela da forma de 360 min; casca HDR50 GMM2, grade 35³, semente 20261012.

## Modelos (exatamente os do M31)
- **B1+** = B0 + elasticidade móvel volatilidade–volume (6 h) + elasticidade × ν + log-cone + cintura + log-cone × ν.
- **B2** = B1+ + fração da área da casca HDR50 em sela.

Avaliados nas origens elegíveis com casca válida e elasticidade definida (os dois modelos estimados e avaliados no mesmo subconjunto).

## Critério (primário único)
Deviança QLIKE; Δ = d(B2) − d(B1+); skill = 1 − média d(B2)/média d(B1+).
**Passa** se, ao mesmo tempo:
- p unilateral < 0,05 com HAC de Newey–West de **1 dia (96)**;
- p unilateral < 0,05 com HAC de **1 semana (672)**;
- **skill ≥ 0,5%** (o limiar original do T3).

Descritivos: bootstrap em blocos de 1 dia e 1 semana; skill por mês; frações válidas; contexto (B1+ vs B0, B2 vs B0).

## Poder
Mesma estrutura do M32 (`reports/m32/poder_plantado.json` no ramo `research/m32-curvatura-casca`; ~7.300 origens): aprova em ~20% dos casos com ganho plantado de 0,4%, ~60% com 0,8% e 100% com 2%. O BNB jun–set deve ter ~11.700 origens. Um negativo exclui com boa confiança ganhos ≥ ~1%.

## Aposta de Claude (antes dos dados)
| Item | Aposta |
|---|---|
| Primário passa | ~4% (o M32, quase idêntico, deu +0,02% no SOL) |

## Regras
Mudanças após este commit só de engenharia, registradas. O código confirmatório recusa rodar se o SHA-256 deste protocolo ou dos três módulos não conferir. Ensaio só com dados sintéticos. Não reabrir BNB jun–set para outros indicadores.
