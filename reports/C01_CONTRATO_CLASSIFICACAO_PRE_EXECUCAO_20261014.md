# SGV-C01 — Contrato de variáveis e plano executável (antes da classificação)
**Data:** 14/10/2026. **Ramo isolado:** research/hdr-fisher-entropia-controle-sintetico. **Status:** especificação de engenharia para comparação pareada; não altera resultados prévios ou o pré-registro original. **Avaliação final: selada.**

## 1. Amostra e limites de acesso

Casos sintéticos T0–T6 de `known_pair`, com transformações e nuisance já fixadas. Duas amostras A/B independentes de 750 observações cada, e dois ajustes GMM3 independentes (`n_components=3; n_init=3; reg_covar=1e-4; max_iter=300; tol=1e-4`). Seeds SHA-256 por split/classe/réplica/função.

- Treinamento: **80 pares por classe**, índices 0–79 (560 pares).
- Validação: **20 pares por classe**, índices 0–19 (140 pares), somente leitura descritiva de eficiência e diagnóstico, **sem ajuste retrospectivo de variáveis/hiperparâmetros**.
- Teste final: **40 pares por classe** (280 pares), **não gerados, não lidos, não executáveis nesta ramificação**. O desbloqueio exigirá artefato e critério de freeze separado. Proibido tratar validação como confirmação.
- Controles T0 calibratórios anteriores usam a partição `calibration` com índices >=1.000.000, sem interseção com os IDs acima.

## 2. Mesma informação para ambos os classificadores

Cada par produz uma única tabela de medidas a partir das mesmas duas densidades estimadas. O braço ampliado **contém integralmente** o bloco de referência. Não é comparação da qualidade de desenho de interface.

**Bloco base (14 variáveis em ordem estável):**
`delta_mu_0, delta_mu_1, delta_mu_2, delta_cov_00, delta_cov_01, delta_cov_02, delta_cov_11, delta_cov_12, delta_cov_22, logdet_cov_delta, entropy_delta, fr_cov, fr_ambient, energy`.

As diferenças assinadas estão em um sistema de coordenadas compartilhado por A/B. `fr_cov` = distância Fisher de gaussianas centradas apenas por covariâncias. `fr_ambient` = **distância ambiente** entre as duas densidades estimadas: `2 arccos∫sqrt(p_A p_B)dx`, por MC; não confundir com a geodésica restrita à variedade de misturas gaussianas. `energy` recebe as mesmas amostras observadas. As 14 variáveis são calculadas em ambos os braços, sem indicadores do rótulo/seed.

**Bloco HDR (12 variáveis, 6 por α=50% e 95%):**
`hdr50_center_distance, hdr50_log_volume_ratio, hdr50_log_area_ratio, hdr50_delta_components, hdr50_voxel_iou_loss, hdr50_shape_tensor_diff`, seguidas das seis análogas com `hdr95_`.

Os últimos dois são **adições de engenharia após o pré-registro geral, anteriores à classificação oficial**: perda de IoU de voxels e distância Frobenius entre tensores de forma de regiões ocupadas, avaliadas na mesma grade comum por par. São descritores extrínsecos, sensíveis às coordenadas e a registro; nenhum recebe interpretação de transporte material/curvatura Fisher. Para transparência, a inferência final com 26 variáveis será rotulada como **protocolo operacional consolidado antes da execução**, e não como a variante original de 4 descritores HDR.

**Aquisição:** Monte Carlo 32.000 para entropia, afinidade/FR ambiente, calibração do limiar HDR e verificação independente da cobertura de cada braço; grade 35³ para as duas HDR; pares independentes A/B. Logs de erro MC e tempo por par são diagnósticos, **não** variáveis do classificador. O protocolo de calibração 35³→49³ foi exploratório e fica arquivado.

## 3. Transformação estatística e teste

Dois pipelines separados, ajustados só no treino, com `StandardScaler` seguido de `LogisticRegression(C=1, solver='lbfgs', max_iter=2000)`, multiclasse 7. Mesma ordem de amostras; algoritmo e regularização idênticos; nenhum grid search/seleção posterior. Não acrescentar índices de caso, seeds, metadados de execução ou medidas de qualidade numérica como variáveis.

**Estimando primário posterior (ainda não executado):** `Δlogloss = logloss_base - logloss_base+HDR` em teste selado; positivo favorece HDR. Regra predefinida: benefício >=0,03 nats por par, intervalo percentual bootstrap pareado estratificado por classe 95% com limite inferior >0 (2.000 reamostragens de pares inteiros), além dos gates de validade. Secundários: balanced accuracy, macro-F1, matriz de confusão, alarme T0 e desempenho por tipo, sem reinterpretar como confirmação.

**Na validação:** podem ser gerados log-loss e métricas descritivas para auditoria de implementação, mas não será tomada decisão de sucesso, não se muda método em reação a métricas e não se consulta `test`.

## 4. Política de integridade/missingness

IDs de par `(split,case,replicate)` exclusivos, seeds diferentes A/B, hashes SHA-256 de amostras, parâmetros congelados, schema de registro versionado. Nenhum caso inválido é recriado com seed nova. Erros de ajuste GMM, não finitude, malha não fechada/truncada, energia negativa além de arredondamento ou erro de cobertura HDR `abs(cobertura-alpha)>0,015` geram `invalid` com motivo e classe preservada no manifesto. Para comparar modelos, só entram IDs válidos **em ambos** (como todos os descritores são produzidos juntos), e requer-se no mínimo 95% de sucesso **por classe e split**; caso contrário, execução `INCONCLUSIVE` antes de pontuar os modelos. Nunca imputar perdas ou substituir falhas por zero. Sem permutar A/B.

O limiar T0 max-score definido na etapa anterior **não é empregado** como limiar de classificação nem afinado pela validação.

## 5. Regras de execução

1. Testes locais com fixtures numéricas e falhas injetadas; não chamar isso de validação humana nem resultado científico.
2. Smoke de 1–2 pares `calibration` por classe, **fora** dos 560/140 oficiais, para aferir compatibilidade de schema e custo.
3. Executar treinos/validações completos somente com shards determinísticos, manifestos e hashes; relatório marca `VALIDATION_DESCRIPTIVE_ONLY`, sem dados test.
4. Congelar versão e protocolo; somente então planejar abertura controlada do teste final, uma única vez, sem usar BTC nem alterar U03/M8–M15.

**Os resultados anteriores T0 8k/32k são diagnósticos, não confirmação da taxa nominal de 5%.** A escolha de 32k baseia-se na precisão de cobertura, não em otimização de log-loss.
