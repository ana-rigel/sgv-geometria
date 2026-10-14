# SGV-C01 — Auditoria pós-validação: calibração, dimensionalidade e contribuição HDR

**14/10/2026 — Auditoria documental e reprocessamento independente.** Ramo isolado `research/c01-auditoria-pos-validacao-20261014`, criado de `research/hdr-fisher-entropia-controle-sintetico@c0aa64170d2e`. A `main`, os protocolos, os conjuntos A/B, os classificadores originais e o holdout de 280 pares **não foram modificados ou acessados**. Todos os resultados abaixo reutilizam o **mesmo conjunto de treino/validação previamente visto**, portanto são exploratórios, **não confirmação**.

## Proveniência e gates

Fonte local `C01_resultados_treino_validacao_20261014.zip`, SHA-256 `824334f0683585455bcad964b1fd1433532add433de3fefa2d5bc39fed78bf80`. Nove shards JSON conferidos contra hashes do manifesto (todos coincidiram); 560 pares no treino, 140 na validação, 7 classes balanceadas, 700 IDs e 1.400 hashes A/B diferentes. Cada linha tem 14 variáveis base, 12 HDR e passou gates numéricos registrados. O ZIP não contém os dados A/B originais — a independência observacional foi conferida por proveniência/hashes, não reconstituída integralmente da série bruta. Nenhum shard `test` foi lido.

O pipeline original `StandardScaler + LogisticRegression(C=1,solver=lbfgs,max_iter=2000)` foi reajustado **sem mudanças** e o resultado inicial reproduzido.

## Métricas independentes da validação

| Métrica | Base (14) | Base + HDR (26) |
|---|---:|---:|
| Log-loss | 0,0953393 | **0,0241050** |
| Brier multiclasse | 0,0350333 | **0,0041424** |
| ECE de 10 faixas | 0,0717649 | **0,0227080** |
| Média da confiança máxima | 0,92109 | 0,97729 |
| Erros em 140 validações | 1 | **0** |

Ganho de log-loss **+0,0712342 nats/par**; favorece a inclusão da HDR em **125/140 pares**. Intervalo bootstrap pareado estratificado sobre *esses mesmos 140 pares* [0,05190; 0,09360], **apenas diagnóstico**, jamais substituir o bootstrap da futura amostra de teste.

Ganho médio por classe: T0 +0,04976; T1 +0,05945; T2 +0,00611; T3 +0,01796; T4 +0,04665; T5 +0,11316; T6 +0,20555. A contribuição é heterogênea e especialmente concentrada em T6 (modo raro), mas positiva em todas as classes neste conjunto.

## Controle exploratório de dimensionalidade

Com o **mesmo** treino/validação e classificador, gerar 100 vezes 12 atributos gaussianos independentes e 100 vezes 12 combinações lineares aleatórias das 14 bases. Resultados de log-loss:

- Base original: **0,09534**.
- Base + ruído aleatório, média 100 execuções: **0,10931** (intervalo entre execuções 0,09027–0,13362).
- Base + características redundantes lineares, média 100: **0,08396** (intervalo 0,07280–0,09667).
- Base + 12 HDR reais: **0,02411**.

Nenhum dos 200 controles de características extras obteve perda menor que HDR. **Mas 98/100 reparametrizações redundantes melhoraram a base**. Portanto, dimensionalidade/reparametrização afeta o classificador; não basta alegar que todo o ganho HDR seja exclusivamente informação geométrica. As 200 execuções não são novos pares independentes e não fornecem p-valor confirmatório.

## Ablacões informacionais — somente diagnóstico pós-validação

| Modelo | Log-loss validação | CV 5 folds, apenas treino |
|---|---:|---:|
| Base (14) | 0,09534 | 0,09441 |
| Base + HDR50 (6) | 0,03481 | 0,04402 |
| Base + HDR95 (6) | 0,05347 | 0,05204 |
| **Base + HDR50/HDR95 (12)** | **0,02411** | **0,03410** |
| Base + IoU e tensor de forma (4) | 0,03730 | 0,03938 |

HDR50 e HDR95 têm utilidade complementar **na representação desse classificador e desses geradores sintéticos**. Não selecionar variáveis com base nessa inspeção e reutilizar o mesmo teste como se a hipótese alterada fosse pré-registrada.

## Limites e decisão

- Melhoram principalmente as **probabilidades atribuídas às classes**; a base já acertava 139/140. ECE em n=140 é sensível a pequenos números em bins; log-loss/Brier são pontuações próprias mais apropriadas.
- HDR é uma função da mesma densidade GMM estimada; pode fornecer uma **representação não linear útil** à regressão logística, sem criar informação que não estava em p(x).
- Validação já foi vista. Nenhuma evidência de ganho em famílias desconhecidas, BTC, previsão ou interpretação humana.
- **Preservar sem mudança o comparador original 14 vs 26 e seus gates**. Não abrir a partição selada até congelar versão e plano de única leitura. O teste futuro deverá ser novo e não reutilizar a validação.
- A reprodução remota GitHub Actions não está confirmada por esta auditoria; os números vêm do reprocessamento do arquivo de resultados.

## Artefatos auditáveis (conversa)

Scripts `auditar_c01.py` e `ablacao_exploratoria.py`; JSON `resultados_auditoria.json` SHA-256 `b7736c6dd7c826c087ec9884d29dfcd2c92df711b19e746b7f42c9770a110e2e`; `ablacao_resultados.json` SHA-256 `29022e8dd5e3d91c3e6998394f9dcc35795de5ca346769b2db8d7e277033608e`; relatório Markdown completo. Os scripts e dados auditados estão reunidos em `C01_AUDITORIA_CALIBRACAO_20261014.zip` gerado na conversa. Esta nota GitHub é registro científico; não contém nem libera o conjunto final.
