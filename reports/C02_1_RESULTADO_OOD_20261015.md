# SGV-C02.1 — Resultado OOD: SUCESSO do endpoint primário

**Data:** 15/10/2026. **Natureza:** liberação única da amostra OOD selada, julgada pelo plano congelado (`PLANO_SGV_C02_1_TREINO_OOD_20261015.md`, commit `76ff653`).

**Antes da liberação:**
- Congelamento em `a730f57`, com hashes conferidos pelo script antes de gerar o primeiro par.
- Treino e validação: 1.050 e 252 pares (G3, S5, B3), 0 inválidos. Modelos ajustados só no treino.

**Liberação:** 490 pares (R7 e BS35 × T0–T6 × 35), 0 inválidos, 35 de 35 em cada estrato. O gate de validade passa.

## Endpoint primário

| | valor |
|---|---|
| log-loss média, HGB base14 | 1,991 |
| log-loss média, HGB base14 + HDR6 | 1,373 |
| **Delta** | **+0,618 nats/par** |
| IC 95 % (bootstrap pareado estratificado, 14 estratos, 2.000 réplicas, semente 2026101403) | **[+0,482; +0,749]** |
| critério | Delta ≥ 0,03 **e** limite inferior > 0 |
| **veredito** | **SUCESSO** |

## Verificação independente

Um agente separado, que não participou da análise, recalculou o resultado a partir dos arquivos brutos, sem importar o código do projeto:
- **Modelos:** reajustou os modelos no treino e obteve previsões **idênticas** às dos modelos congelados (diferença 0,0). Um modelo ajustado com a validação incluída difere em até 0,70, então a validação não entrou no ajuste.
- **Endpoint:** Delta e IC bateram **até a última casa**. Com outras sementes do bootstrap, o IC fica em [0,48; 0,76].
- **Vazamento:**
  - nenhuma chave nem família em comum entre a OOD e treino/validação;
  - nenhuma linha duplicada;
  - nenhuma feature HDR separa as classes sozinha (balanced accuracy de 0,29 a 0,37 por feature);
  - nenhuma feature carrega a réplica.
- **Robustez a perdas extremas:** limitando a perda por par a 5 nats, Delta = +0,50. Limitando a ln 100, +0,47.

## Secundários (só leitura)

| Braço | log-loss | balanced accuracy | macro-F1 | Brier | ECE |
|---|---|---|---|---|---|
| base14 | 1,991 | 0,627 | 0,604 | 0,651 | 0,296 |
| base14 + HDR6 | 1,373 | 0,722 | 0,702 | 0,457 | 0,193 |
| controle de dimensão (base14 + 6 projeções) | 2,010 | 0,622 | 0,600 | 0,660 | 0,305 |
| base14 + HDR sem W₂ (5) | 1,389 | 0,720 | 0,698 | 0,463 | 0,193 |
| base14 + HDR6 + envelope | 1,390 | 0,727 | 0,708 | 0,455 | 0,190 |
| logística base14 | 6,157 | 0,571 | 0,579 | 0,744 | 0,293 |
| logística base14 + HDR6 | 5,186 | 0,606 | 0,612 | 0,678 | 0,277 |

| Contraste (Delta, IC 95 %) | OOD | BS35 | R7 |
|---|---|---|---|
| **primário HDR6 vs base14** | **+0,618 [0,48; 0,75]** | +1,057 [0,79; 1,31] | +0,179 [0,09; 0,28] |
| controle de dimensão vs base14 | −0,019 [−0,05; 0,01] | −0,004 | −0,034 |
| HDR sem W₂ vs base14 | +0,602 [0,47; 0,73] | +1,038 | +0,165 |
| envelope (HDR6 + env vs HDR6) | −0,017 [−0,03; −0,003] | −0,001 | −0,033 |
| logística HDR6 vs base14 | +0,971 [0,56; 1,38] | +2,031 | **−0,089 [−0,14; −0,03]** |

## Leitura

1. **O que a OOD mostra.** Os dois braços pioram muito em famílias nunca vistas: a balanced accuracy cai de 0,99 na validação para 0,63 (base14) e 0,72 (HDR6). O bloco HDR6 **reduz essa perda de generalização**. Quando a família muda, ele sustenta melhor a classificação que os momentos sozinhos.
2. **De onde vem o ganho.**
   - Vem sobretudo do BS35, a família de caudas pesadas (Delta +1,06).
   - Nas classes, vem de translação (T1), cisalhamento (T4) e identidade (T0). Com caudas ν = 3,5, as diferenças de média e covariância da base ficam ruidosas, e as medidas do núcleo HDR50 são mais estáveis.
   - O ganho é **concentrado**: 10 % dos pares respondem por 82 % do Delta, e a mediana da diferença por par é ≈ 0. O HDR6 corrige poucos erros grandes e confiantes da base (acerta 54 pares que a base errava e erra 7 que ela acertava). Não melhora todos os pares um pouco.
3. **O ganho não vem de ter mais variáveis.** Seis projeções aleatórias da própria base não ajudam (−0,019). A W₂ quase não contribui (+0,602 sem ela). O envelope da Mudança 3 piora levemente.
4. **Limites.**
   - O ganho no R7 é modesto (+0,18) e **depende do classificador**: com a logística ele inverte (−0,09). Essa comparação é secundária, e a primária é o HGB, mas a generalização do R7 não é robusta à escolha do modelo.
   - A T5 (mudança de pesos) continua quase ininteligível para os dois braços (log-loss > 4,5).
   - O bloco retido tinha uma variável rente ao corte de confiabilidade (W₂ do HDR50, 0,5016 no BS35). Sem ela o resultado é praticamente o mesmo (+0,60), então a conclusão não depende dela.
   - É um teste em dados sintéticos. Ele não diz nada sobre mercado, previsão ou ganho econômico (protocolo C02, §Escopo).

## Apostas

- Emenda C02.1, "endpoint primário passa nas famílias OOD", ~35 %: **errou**. O efeito foi muito maior que o limiar e concentrado na família de caudas pesadas.
- Plano de treino/OOD (§7), mantida a ~35 %: **errou**.

## Arquivos

- `reports/c02_1/pares_ood_test.jsonl` (490 pares)
- `reports/c02_1/resultado_ood.json`
- `reports/c02_1/perdas_ood.npy` (perdas por par e braço; colunas em `resultado_ood.json`)
