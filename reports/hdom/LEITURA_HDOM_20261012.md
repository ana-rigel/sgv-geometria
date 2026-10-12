# H-DOM — Leitura (12/10/2026)

**Execução:** GitHub Actions run 38199640273 (resultados em `f84dd17`). Protocolo congelado `reports/PROTOCOLO_SGV_HDOM_20261012.md`, SHA-256 `6b71561511e7f8e80e9ce54f13970aac5917e97c84dc0c87bcc7c958bb05047f`, conferido pelo código antes de baixar os dados. Dados de teste: BTCUSDT 1m 2026-08 e 2026-09. A 1ª tentativa (run 38199347038) falhou no ensaio por sintaxe incompatível com Python 3.11, **antes** de baixar os dados de teste; correção só de engenharia (`1a86847`). O ensaio nos dados exploratórios reproduziu a origem (366 janelas, 48 no subconjunto, 62,5%).

## Resultado
| | Exploração (mai–jul) | **Teste (ago–set)** |
|---|---|---|
| Janelas / subconjunto | 366 / 48 | 242 / 58 |
| Acerto do sinal em 60 min no subconjunto | 62,5% | **34,5% (20/58)** |
| p unilateral (> 50%) | 0,056 | **0,994** |
| Spearman(A, retorno 60 min), todas as janelas | −0,02 | −0,05 |
| Ganho médio com custo de 0,10% (60 min, subconjunto) | −0,045% | **−0,096%** por operação |

**H-DOM não apoiada.** O acerto não só não passou de 50%: **inverteu** (34,5%). Pela mesma regra adotada no julgamento do IIT≥0,30 (ago/2026), a inversão **não** vira filtro novo nem hipótese "ao contrário": nasceu depois de ver os dados e tem o padrão de ruído com troca de sinal entre períodos. No conjunto inteiro, a dominância não se relaciona com o retorno seguinte em nenhum horizonte (|ρ| ≤ 0,08).

## Leitura
A forma da casca (cintura e cone) descreve **como** o mercado se move dentro do minuto, não **para onde** vai depois. Este é o mesmo resultado da linha direcional inteira do SGV, agora também para a geometria da forma.

## Apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário significativo (10%) | não | ✅ (não ocorreu) |
| Acerto > 50% só na direção (50%) | não (34,5%) | — (moeda) |
| \|ρ\| < 0,1 em 60 min no conjunto inteiro (85%) | sim (−0,05) | ✅ |
