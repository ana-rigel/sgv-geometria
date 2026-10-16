# SGV-D01 — Resultado final: memória direcional condicional (sintéticos + ago–set/2026)

**Data do fechamento: 15/10/2026 (horário do registro do experimento).** Status: `CONTROLES SINTÉTICOS APROVADOS; AVALIAÇÃO EXPLORATÓRIA FINANCEIRA SEM GANHO DIRECIONAL REPRODUZÍVEL`. Dados de novembro e outubro **não foram acessados**. Ramo isolado `research/sgv-d01-direcao-ago-set-20261015`. Nenhum resultado da `main` ou holdout previamente congelado alterado.

## Pergunta científica

Separar o eventual ganho direcional de:
- **B0**: quatro últimos sinais, quatro log-retornos padronizados e volatilidade causal EW10/EW60/EW240;
- **B1**: B0 + `E_norm`, `jerk`, `memory_flux` do SGV original com `SGVConfig()`;
- **B2**: B1 + sinais nos atrasos 5,10,20,40,60 min.

Alvo: próximo sinal de retorno de preço; zeros descartados. Log-loss é a métrica principal. `D_geom=L(B0)-L(B1)`, `D_hist=L(B1)-L(B2)`. Quanto maior delta positivo, maior a informação incremental aparente. Os mesmos três modelos `StandardScaler + LogisticRegression(C=0.1,max_iter=500)` são ajustados com os dados passados, antes da avaliação.

## Cronologia e auditoria — incluindo as falhas

1. **Pré-registro anterior ao código**: `reports/D01_PROTOCOLO_PRE_REGISTRO_20261015.md`, commit `63a1ddf`. A correção de indexação `reports/D01_ERRATA_INDEXACAO_PRECODIGO_20261015.md`, commit `1688e34`, foi escrita antes do código e da abertura de teste.
2. Código científico congelado Git blob `c7ef72ae2e6d72f79c7dade06013a3c7add0cdc8`, em `pipeline/sgv_d01_direcao.py`. Run `38829564103` falhou no primeiro preflight por assertiva equivocada: inverteu os retornos futuros e exigiu que o rótulo futuro não mudasse. Foi corrigida **somente a assertiva de engenharia**, sem alterar hipóteses/limiares, antes do treino.
3. Run `38829672104`: nove testes passaram, ajuste de 12 pares sintéticos (IDs 0–11), validação sintética IDs 12–15, e **85.760 observações BTC junho–julho** no treino financeiro com maio como âncora. Modelos congelados em `resultados/d01_modelos_congelados.json`, Git blob `142f4ffafa3c9b8fdb676fa271a5306a37acd736`. Freeze `reports/D01_FREEZE_ANTES_TESTES_20261015.md`.
4. Run `38829840815`: registrou `resultados/d01_TEST_RELEASE.txt` antes de abrir IDs sintéticos finais 16–23; executou sintético final **uma única vez** e obteve `PASS_SYNTHETIC_INSTRUMENT`. A avaliação financeira da mesma run falhou no CHECK de SHA binário de treino; shell `python ... | tee` sem `pipefail` **mascarou o erro** na conclusão do job. O sintético foi recuperado **do artefato original, sem refazer os oito pares**, e preservado em `resultados/d01_sinteticos_teste_final.json` (run `38830071935`).
5. Auditorias `38830071935`, `38830231993` e `38830379492`: as características junho–julho e maio–setembro, dentro de uma mesma máquina, têm **85.760 rótulos e 19/19 colunas idênticos bit a bit**. O SHA de bytes float64 pode variar *entre execuções* (`3992d0c...` em algumas e `f010821...` em outra), sem diferença de prefixo causal na mesma execução. A operação exata que provoca tal divergência não foi identificada. A guarda SHA original bloqueou dados legítimos em algumas máquinas.
6. **Antes de obter resultados de mercado**, registrada errata de engenharia `reports/D01_ERRATA_OPERACIONAL_INVARIANCIA_20261015.md`: manter código científico e modelos intactos; exigir igualdade binária do prefixo dentro da mesma execução e `StandardScaler` média/escala igual ao freeze com `atol=rtol=1e-8`. Somente a chave do checksum de integridade é ajustada numa cópia em memória **após todas as verificações** para reaproveitar a função `test_market` original. Nenhum coeficiente, variável, métrica, seed, teste sintético, período ou limiar mudado.
7. Run `38830631675`: **success real**, guardas de freeze, download e SHA-256 oficiais, 19 colunas idênticas, médias e escalas do modelo iguais (`max diff=0` nos três braços), e `--stage market` concluído com `set -o pipefail`. Resultado em `resultados/d01_mercado_agoset_exploratorio.json`, com log e auditoria embutida. Na run final, inclusive, o SHA binário de treino coincidiu com congelado.

## Controles sintéticos: capacidade de detectar dependência plantada

Nulo e alternativo têm caminhos idênticos de volatilidade rápida/lenta e mesmas magnitudes a cada minuto (`r_nulo[t]² = r_dir[t]²` por construção). O alternativo planta `sign[k]` persistindo no atraso 21, alinhado à feature `sign[t−20]` do próximo retorno.

| Holdout sintético único | Ganho D_hist (nats/observação) |
|---|---:|
| VOL_ONLY (nulo) | **−0,00001205** |
| VOL_PLUS_DIRECTION (alternativa) | **+0,21746855** [IC95 por trajetórias: **+0,21269390 a +0,22231800**] |

Três gates de sensibilidade, especificidade e igualdade energética **aprovados**. **Isso valida somente a capacidade do indicador de direção neste cenário plantado, não sua existência em BTC**. Sintético do SGV é análogo, mas não necessariamente idêntico byte a byte à configuração original do mercado.

## Agosto–setembro — resultados financeiros exploratórios, modelos NÃO reajustados

82.683 rótulos válidos, **nove blocos de semanas** (sábado 1º agosto a 30 setembro). Bootstrap 2.000 reamostragens de semanas inteiras, seed `202610156`; IC95 descritivos, sem alegação de independência perfeita entre semanas.

| Modelo | Log-loss agosto–setembro | Acurácia |
|---|---:|---:|
| B0 (sinais curtos, retornos, vol) | **0,69370919** | 50,1397% |
| B1 (+ SGV 3D atual) | **0,69354721** | 50,4928% |
| B2 (+ atrasos 5,10,20,40,60) | **0,69354440** | 50,4154% |

**Ganho SGV geométrico:** `D_geom = +0,00016198` nats/obs, **IC95 [−0,00006874; +0,00035145]**. Não atinge critério descritivo de intervalo estritamente positivo.

**Ganho histórico direcional longo:** `D_hist = +0,00000281` nats/obs, **IC95 [−0,00005638; +0,00006535]**. Praticamente zero, os sinais semanais alternam, e não atinge critério de positividade.

Esses resultados **não demonstram** ganho incremental direcional confiável nem da geometria SGV sobre o histórico curto, nem do histórico longo sobre B1. Não provam ausência geral de memória direcional; são negativos **para este conjunto de features, arquitetura logística, parâmetros fixos e horizonte de 1 minuto**. Acurácia perto de 50% não prova negociação lucrativa.

## Interpretação científica e limites

A distinção é clara: o instrumento **detecta a dependência direcional forte e conhecida plantada em controles sintéticos**; nos dados de mercado já examinados, não há redução de log-loss com suporte estatístico neste desenho. O resultado anterior `FECHADO: volatilidade multiescala` continua sendo uma classificação por sua própria regra sobre a **memória da agitação**, mas não demonstra ausência de todas as outras memórias. Esta avaliação direcional não detectou uma componente extra reproduzível — não é teste completo de Markov nem impossibilidade matemática de uma dimensão escondida.

A diferença entre modelos B0, B1, B2 é muito pequena comparada ao ruído por semanas; não ajustar atrasos ou hiperparâmetros com base em agosto–setembro se o objetivo for confirmação futura.

## Continuação — novembro preservado

**Nenhum dado novembro/2026 foi lido.** Para avaliar novembro completo, aguardar **01/12/2026** e verificar previamente se esse mês é reserva de outro experimento; se for, não abrir. Reutilizar modelos congelados e definições do D01 ou preregistrar novo desenho sem olhar novembro; os parâmetros **não serão ajustados a partir do fracasso de agosto–setembro**. Para regressão temporal/mercado, registrar antecipadamente comparações, intervalos por semanas e convenção de classificação. A tarefa de retomada foi agendada para 01/12/2026, sem execução automática em dados antes dessa data.

Fontes: `pipeline/sgv_d01_direcao.py`, `resultados/d01_modelos_congelados.json`, `resultados/d01_sinteticos_teste_final.json`, `resultados/d01_mercado_agoset_exploratorio.json`, `reports/D01_ERRATA_OPERACIONAL_INVARIANCIA_20261015.md`, GitHub Actions `38830631675`.
