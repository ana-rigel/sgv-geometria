# SGV — H-DOM: a dominância dos lóbulos prevê a direção do preço? (pré-registro)

**STATUS: CONGELADO** (12/10/2026, antes de escrever o código confirmatório e antes de abrir qualquer dado do período de teste)
**Ramo:** `research/h-dom-dominancia` (a partir de `research/forma-isosuperficie`). **`main` intocada.**
**Pedido:** Ana, "Teste" (12/10/2026), depois da proposta de julgar a hipótese de dominância só em dados fora da exploração.

## Origem (exploratória)
`scripts/forma_dominancia.py` no 1m mai–jul/2026 (exploratório, já muito usado): 366 janelas de 6 h sem sobreposição; dominância **A** sem relação com o retorno seguinte no geral (Spearman −0,02 a −0,05; acerto do sinal 47–51%); no subconjunto **cintura forte e cone aberto** (48 janelas), acerto de **62,5% em 60 min** (p = 0,11), visto entre 6 comparações (3 horizontes × geral/subconjunto). É exatamente o tipo de número que já se inverteu antes (célula Gold, IIT≥0,30).

## Dados de teste
BTCUSDT spot **1m, 01/08/2026 → 30/09/2026** (arquivos mensais oficiais da Binance, baixados pelo mesmo `download_month` do M19, com checksum).
**Ressalva de honestidade:** este período foi aberto no M19 (confirmatório da H-RUP: alarmes das cascas contra eventos). Nunca foram examinados nele retornos futuros, dominância, cintura ou cone. Não é virgem em sentido estrito; é **virgem para esta pergunta**. Uma replicação em 1m out–dez/2026 pode ser acrescentada depois, como teste separado, com este mesmo protocolo.

## Definições (idênticas a `scripts/forma_dominancia.py`)
- Coordenadas de fluxo do SGV (z, ι, ν) calculadas sobre a série contínua do período (os primeiros minutos sem histórico suficiente ficam de fora, como sempre).
- Janelas de **360 min sem sobreposição**, consecutivas a partir do primeiro minuto válido; janela descartada se tiver lacuna ou se não houver 240 min de preço depois do fim.
- Em cada janela, cópula local (postos → normal) e:
  - **A** = média de s = (z + ι)/√2 entre os 40% de minutos de maior volume (A > 0: lóbulo comprador mais pesado);
  - **cintura** = fração desses minutos com |s padronizado| < 0,3, dividida por 0,2358 (valor normal);
  - **cone** = dp(z) no terço de volume alto / dp(z) no terço baixo.
- **Limiares congelados** (p10 da cintura e p90 do cone no nulo embaralhado da exploração, `reports/forma/movimento_forma.json`): cintura < **0,71** e cone > **1,86**.
- Retorno futuro: log(preço de fechamento 60 min depois do último minuto da janela) − log(fechamento do último minuto). Idem 15 e 240 min (secundários).

## Hipótese e critério
**Primário (H-DOM):** nas janelas com cintura < 0,71 **e** cone > 1,86, o sinal de A acerta o sinal do retorno de 60 min mais do que 50% das vezes. Binomial exata unilateral, **α = 0,05**. Retornos exatamente zero contam como erro.
**Secundários (descritivos, sem correção):** Spearman(A, retorno 60 min) no subconjunto; os mesmos números em 15 e 240 min; e em todas as janelas.
**Leitura econômica (descritiva):** ganho médio de operar o sinal de A por 60 min nas janelas do subconjunto, bruto e com custo de 0,10% ida e volta.

## Poder (honesto)
Esperam-se ~240 janelas e, se a proporção da exploração se mantiver (~13%), **~30 no subconjunto**. Com 30, é preciso ≥ 20 acertos (67%) para significância. Se o acerto verdadeiro fosse 62,5%, o poder seria ~30%. **Um resultado negativo não distingue "não existe" de "existe e é pequeno"**; um positivo com n ≈ 30 ainda precisaria de replicação antes de qualquer uso.

## Aposta de Claude (antes dos dados)
| Item | Aposta |
|---|---|
| Primário significativo | ≈ 10% |
| Acerto no subconjunto > 50% (só a direção) | ≈ 50% |
| Spearman no conjunto inteiro, \|ρ\| < 0,1 em 60 min | ≈ 85% |

## Regras
Mudanças após este commit só de engenharia, registradas. O código confirmatório recusa rodar se o SHA-256 deste arquivo não bater.
