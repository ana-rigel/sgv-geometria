# SGV-C02 — Pré-registro de generalização entre famílias e comparadores não lineares
**Data:** 14/10/2026. **Ramo:** `research/c02-crossfamily-nonlinear-20261014` (iniciado a partir do registro confirmatório encerrado C01 `4b956cce908922a0665a827dd383854f50cf0ed2`). **Status:** plano experimental prospectivo; nenhuma amostra C02 de confirmação executada nesta data.

## Questão distinta de C01
Dado o mesmo pipeline GMM3 (750 observações A e 750 B independentes), os descritores HDR50/HDR95 acrescentam qualidade probabilística a um classificador **não linear** treinado em certas famílias geradoras quando aplicado a **famílias geradoras nunca vistas**? C01 demonstrou resultado positivo *dentro* de uma família de mistura gaussiana e regressão logística; C02 NÃO reutilizará seu holdout de 280 pares, nem o tratará como fonte de otimização.

**Alegação investigada:** ganho de diagnóstico de transformações **T0–T6**, condicionado a representação das densidades por 14 medidas base versus 14 + 12 HDR, com classificador e famílias explicitamente fixados. Não se testa criação de informação além de `p`, identificação de uma lei física, causalidade, inferência temporal ou trading.

## Geradores de verdade com famílias disjuntas

Base `P_F` 3D gerada por componentes probabilísticas conhecidas, com **semente de nuisance por caso**, aplicada de forma idêntica a A/B. As seguintes famílias recebem parâmetros fixos antes da abertura da confirmação:
- **Treino + validação, três famílias:** `G3` (mistura assimétrica de três gaussianas), `S5` (mistura de três Student-t elípticas com `ν=5`), `B3` (transformação banana invertível e jacobiano unitário, aplicada a mistura gaussiana assimétrica com três componentes).
- **Teste OOD, duas famílias completamente ausentes do treino:** `R7` (mistura de sete gaussianas em anel irregular e assimétrico 3D, pesos desiguais) e `BS35` (mistura Student-t `ν=3,5`, deformação banana mais intensa; caudas mais pesadas). `R7` não é rotacionalmente simétrica; validar identidade e distância entre `P` e `T3(P)` antes de qualquer teste.
- Para todos os modelos `T0` é `P` inalterada, mas com A/B independentes; `T1` translada B em `0,65 e2`; `T2` escala B por `1,25`; `T3` gira B por 90° no plano e1-e2; `T4` aplica cisalhamento `x1'=x1+0,55 x2`; `T5` aumenta peso relativo do primeiro componente, renormalizando demais componentes; `T6` mistura `0,95P + 0,05N(2,8e1,0,35²I)`. As famílias com deformação banana aplicam deformação **antes** de `T1–T4`; `T5` altera os pesos latentes antes da deformação; `T6` adiciona um modo explícito **após** deformação. Isso evita rótulos matematicamente ambíguos.
- O mesmo operador aleatório global (rotação rígida `Q`, escala isotrópica em [0,9;1,1], translação em [-0,25;0,25]^3) atua em ambas A/B; o modelo recebe só suas amostras, não o gerador, classe, operador ou semente.

As misturas e transformações são normalizadas por construção. Estimar propriedades de densidade verdadeira em testes oraculares **antes** de qualquer classificação; não usar semelhança casual de distribuições como vantagem escondida de um braço.

## Coleta e separação, fixadas

- **G3/S5/B3:** 50 pares de treino + 12 de validação por classe e por família: `1050 treino + 252 validação`.
- **R7/BS35:** 35 pares reservados por classe e família: `490 pares OOD selados`.
- Cada par: 750 amostras **independentes** de A e B; GMM3 com 3 componentes, `n_init=3`, `reg_covar=1e-4`, `tol=1e-4`, `max_iter=300`; mesmos dados e ajuste para os dois braços.
- Identidades `(split,family,class,replicate)` e seeds SHA-256 por propósito. O módulo de desenvolvimento recusa `ood_test`. Seeds, designs e observações reservadas **não serão gerados durante engenharia, treino ou validação**.
- Não reusar C01 treino/validação/teste em treinamento ou seleção de C02. C01 é somente referência histórica e para identificação do congelamento conceitual.

## Descritores: mesmos nomes e ordens da comparação C01

**Base 14:** `delta_mu_0..2`, seis `delta_cov_ij` (`i<=j`), `logdet_cov_delta`, `entropy_delta`, `fr_cov`, `fr_ambient`, `energy`.
**HDR12:** para HDR50 e HDR95, `center_distance`, `log_volume_ratio`, `log_area_ratio`, `delta_components`, `voxel_iou_loss`, `shape_tensor_diff`.
O gerador verdadeiro pode ser não gaussiano; **todas** essas medidas são computadas a partir da **mesma aproximação GMM3 ajustada** às observações em ambos os modelos (exceto `energy`, calculada dos dados A/B). Logo, falha do GMM3 em representar uma família OOD será parte do teste e nunca deverá ser ocultada.

Precisão: `32.000` pontos MC por integral, limiares HDR estimados por MC independente do conjunto de checagem; grade comum de `35³`; mesma regra de falha se `|cobertura−alfa|>0,015`, malha aberta/truncada, não SPD, não finitude, ou ajuste não convergente. Não afinar MC/malha por desempenho de validação.

## Modelos congelados prospectivamente

**Classificador primário (não linear):** `HistGradientBoostingClassifier(learning_rate=0.06, max_iter=180, max_leaf_nodes=15, l2_regularization=1.0, early_stopping=False, random_state=20261014)`, mesmas configurações para **base14** e **base14+HDR12**. Sem busca de hiperparâmetros, seleção de variáveis, ajuste de probabilidade ou ajuste ex post.
**Secundário pré-fixado:** `StandardScaler + LogisticRegression(C=1,solver='lbfgs',max_iter=2000)` para os mesmos blocos, apenas diagnóstico de efeito do classificador. Dimensionalidade: **controle secundário** base14+12 projeções lineares aleatórias fixadas por SHA da seed de desenho `2026101402`, calculadas apenas das bases, no classificador não linear; não se usa para substituir o braço oficial.

## Portões e inferência OOD

1. **Gate matemático/oracular:** amostras finitas e densidades normalizadas, verificação da banana inversível, diferenças T0 nulas no gerador, operação T3 distinta em todas as famílias, ruído de estimação não escondido, campos e IDs sem acesso a `ood_test`.
2. **Gate de engenharia:** smoke apenas `calibration` com IDs >=2.000.000, fora dos IDs oficiais; registrar tempos e erros; classes e famílias de teste apenas examinadas por **amostras oraculares de calibração com seeds distintas** (não as sementes OOD, não amostras OOD).
3. **Treino/validação:** produzir 1050/252 pares novos, comparar blocos em validação apenas descritiva; **sem alterações** orientadas por resultado; congelar código, versões, parâmetros do classificador, hashes da base e critérios.
4. **Gate de validade do OOD:** pelo menos **34/35 casos válidos em cada estrato família×classe**, sem reposição; abaixo disso resultado `INCONCLUSIVE` e não reexecutar no mesmo holdout.
5. **Estimando primário OOD único:** `Delta = log_loss(HGB_base14) − log_loss(HGB_base14+HDR12)`, média em pares de **ambas as famílias OOD**, estratificando por família×classe. Sucesso apenas se `Delta >= 0,03` nats/par **e** limite inferior de IC95 de bootstrap pareado estratificado por 14 estratos acima de zero (2.000 réplicas, semente `2026101403`). Ambos os critérios fixados antes de qualquer OOD.
6. **Diagnósticos secundários:** log-loss por família/classe, balanced accuracy, macro-F1, calibração, resultado logístico, controle de dimensão; não criar hipótese confirmatória secundária após inspecionar números.
7. **Falha:** ganho insuficiente, IC cruzando zero, nulos de implementação, ou não generalização para famílias reservadas. Publicar integralmente e encerrar C02 sem otimizar as mesmas 490 observações.

### Proibição de vazamentos e escopo
O teste final C01 **foi consumido** e não será reaberto nem incorporado a C02. Nenhum arquivo de BTC, ETH, SOL ou BNB é usado em C02; nenhum período financeiro reservado será acessado. Resultados de C02 nunca implicarão efeito econômico ou funcionamento em dados reais.

## Status inicial
**Protocolo fixado no GitHub antes da geração de resultados C02.** O desenvolvimento pode verificar matemática, construir instrumentos e executar `calibration`. O conjunto reservado `ood_test` permanece intocado até um **freeze separado e uma única liberação**.
