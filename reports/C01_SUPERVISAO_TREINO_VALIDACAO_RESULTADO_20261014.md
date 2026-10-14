# SGV-C01 — Execução local de treino e validação (14/10/2026)

**Estado:** `VALIDATION_DESCRIPTIVE_ONLY`. Execução sintética supervisionada concluída localmente, sem abertura do teste final e sem acesso a dados financeiros. O resultado **não** é confirmação da hipótese; não alterar hiperparâmetros em resposta às métricas abaixo.

## O que foi executado

- Preflight de 44 testes: **44/44 aprovados localmente**.
- Smoke externo aos splits oficiais: 14/14 pares, todas as classes T0–T6, sem falhas.
- 9 shards determinísticos: sete de `training` e dois de `validation`.
- Treino: **560/560 pares válidos**; validação: **140/140 válidos**; erros de estimação, convergência, HDR ou cobertura: **0/700**.
- Cada par possui observações A/B independentes, 750 por braço e ajustes GMM3 separados. Extraídas 14 variáveis do bloco base e 12 HDR50/HDR95, MC=32.000 e grade 35³.
- O auditor `scripts/c01_auditar_shards.py` verificou a completude e unicidade de IDs, partições, covariáveis, hashes de A/B, finitude e cobertura HDR antes de permitir classificação.
- Classificador fixo: `StandardScaler` + `LogisticRegression(C=1,solver='lbfgs',max_iter=2000)`, aplicado ao bloco de 14 ou ao bloco ampliado de 26 variáveis.

## Desempenho na validação (140 exemplos; 20 por classe)

| Métrica | Base 14 | Base + HDR 26 |
|---|---:|---:|
| Log-loss | 0,09533925344059234 | **0,024105028179630193** |
| Balanced accuracy | 0,9928571428571429 | **1,0** |
| Macro-F1 | 0,9928526757795051 | **1,0** |

**Diferença de log-loss base − ampliado = +0,07123422526096215 nats/par**, descritivamente favorável à adição das HDR. Isso **não passa ainda o gate primário**, pois ele exige teste previamente selado, ganho >=0,03 e bootstrap pareado estratificado, que **não foram executados**.

## Limitações e interpretação

- **Geradores conhecidos e rigidamente estruturados:** sete mecanismos sintéticos predefinidos, altamente separáveis para os classificadores. O desempenho quase perfeito de ambos significa que a principal diferença está em probabilidades previstas, não em grande ganho de acurácia.
- **Comparação de blocos finitos, não informação absoluta:** HDR é funcional das mesmas densidades estimadas; não cria informação ausente da distribuição completa. O ganho é estritamente sobre os descritores de base/estimador/classificador escolhidos, em validação.
- **Mesmo protocolo para ambos os braços:** as medidas base foram preservadas integralmente no braço HDR; atributos de cobertura e custo não entraram como preditores. A dimensionalidade maior pode beneficiar regularização/classificador mesmo sem uma propriedade exclusivamente geométrica; hipótese ainda requer controles de complexidade/dimensões.
- **Validação foi vista agora:** não otimizar descritores, seeds, hiperparâmetros, limiares, geradores ou método após inspecionar esses resultados e depois apresentar a mesma avaliação como confirmação.
- **Nenhuma estimativa de generalização financeira, estudo humano ou efeito causal.** Não atribuir significado físico a translação/rotação de densidade sintética.

## Integridade e proveniência

O registro local `reports/c01_SUPERVISAO_LOCAL_RESULTADO_20261014.json` foi criado com SHA-256 **`bddf89c20b9e33f7f32c28763f4d69960125151f7302025fc439437cc85c271e`**. Nove arquivos JSON de shards possuem hashes próprios no manifesto; cópias originais da execução local são preservadas. Na ramificação, o workflow `.github/workflows/c01-treino-validacao.yml` foi enviado para reprodução remota em shards paralelos. **Não foi confirmado o sucesso do GitHub Actions**, portanto os números desta nota são da execução local.

## Decisão operacional

**Fase de treino/validação aprovada localmente como engenharia.** Preservar parâmetros do pré-registro e os 26 descritores do contrato operacional. O **teste final (280 pares, 40 por classe) continua não gerado e não aberto**.

Antes de executar confirmação, auditar o grau de inflação de confiança/calibração em dados novos, o protocolo de incerteza (bootstrap pareado no nível de par), e custo/dimensionalidade dos dois braços; registrar freeze reprodutível do código. Se houver alteração após esta validação, abrir hipótese nova e amostra nova, sem reclassificar os atuais resultados.
