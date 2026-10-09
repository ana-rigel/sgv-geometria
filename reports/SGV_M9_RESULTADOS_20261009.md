# SGV-M9 — Relatório científico de orientação quociente e registro geométrico

**Data:** 09/10/2026. **Ramo isolado:** `research/m9-simetrias-registro-3d`.  
**Execução validada GitHub Actions:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37967131614.  
**Integridade:** 7 testes aprovados, três trabalhos concluídos com sucesso, BTC 1m e 1h exploratórios, `main` intacta e períodos confirmatórios reservados não acessados.

## Motivação do M8 para o M9

No M8, as rotações entre eixos principais de cascas HDR50 apresentaram ambiguidades de sinal dos autovetores e grandes variações entre reamostragens (ângulos aparentes próximos de 172°). Além disso, o resíduo de deformação era calculado somente quando três eixos volumétricos eram identificáveis. O M9 corrige essas duas limitações como **instrumentação observacional**, não como prova de mudança física no mercado.

## Métricas e implementação

- **Translação:** norma entre centros volumétricos das duas cascas.
- **Expansão:** `log(Vb/Va)`.
- **Rotação de eixos quando identificável:** distância angular mínima no espaço quociente `SO(3)/D2`, que testa as quatro inversões equivalentes de sinais dos autovetores. Se o menor gap relativo entre autovalores de inércia for <0,07 em uma das fotografias, o ângulo é indefinido (`null`), não zero.
- **Deformação residual independente dos eixos:** remover centros volumétricos e escalas `r=(3V/4π)^(1/3)`; amostrar 360 pontos por superfície para ajustar alinhamento rígido por ICP multistart e Kabsch. A função de perda é a Chamfer simétrica; avaliação separada utiliza **360 pontos novos por superfície que não entraram no registro**. Uma forma quase esférica permite comparação de deformação mesmo sem rotação de eixos identificável.
- **Atenção ao piso de amostragem:** duas superfícies geometricamente idênticas produzem distâncias Chamfer positivas ao empregar pontos de avaliação independentes. Controle com esfera transladada gerou valor de referência ≈0,09318. Não tratar valores pequenos como distâncias geométricas exatas ou curvatura adicional.

As malhas HDR50 usam GMM2 com mesma transformação marginal congelada nos primeiros 30% da janela e duas metades posteriores (aprox. 35/35%). Grade 35³, verificação em 49³ em duas origens por escala. Os gates de malha fechada, ausência de truncamento, cobertura >=95% e volume positivo seguem M1.

## Calibração sintética

**7 testes aprovados** após uma correção de importação no próprio teste (nenhuma mudança de hipótese):
- esfera submetida a translação `[0,4;-0,3;0,2]` → deslocamento `0,53852`, orientação corretamente indefinida;
- elipsoide de três eixos diferentes com rotação de 25° → ângulo-quociente de 25° e expansão log-volumétrica ≈0,28593 sob fator de escala 1,1;
- elipsoide com mudança real de proporções de semieixos apresentou aumento de deformação de holdout (≈0,1312), comparado ao análogo rigidamente transformado (≈0,0969);
- controle de simetria de eixos, rejeição de amostras para inferência de bootstrap insuficiente, comparação explícita de grades, falhas de pareamento.

## BTC 1 minuto

Seis origens válidas; três simulações pareadas por origem e modelo. Erros absolutos medianos:

| Métrica | SF1 | M5 | M6 |
|---|---:|---:|---:|
| Deslocamento | 0,520925 | **0,464846** | 0,506431 |
| Expansão (log volume) | 0,185522 | **0,160240** | 0,194556 |
| Rotação de eixos identificáveis | 2,944° | **2,758°** | 7,211° |
| Deformação holdout registrada | 0,011330 | 0,008120 | **0,006768** |

A rotação foi identificável para comparações em **4/6 origens**; a deformação de holdout pôde ser avaliada em **6/6**. Na comparação pareada M6 vs M5, M6 teve menor erro de deformação em **5/6 origens**, mas venceu em 2/6 no deslocamento, 3/6 na expansão e 1/4 na rotação. **M5 continua melhor em várias dimensões; não há vencedor geral.**

### Auditoria 1m de orientação

- Primeira origem: orientação real 9,490°, bootstrap em blocos (8 replicações) com percentis p10–p90 [11,144°,21,838°], amplitude **10,694°**, sem ângulos acima de 90°, eixos identificáveis em 8/8 reamostragens.
- Última origem: orientação real 15,735°, percentis [11,415°,48,140°], amplitude **36,726°**, 8/8 orientações identificáveis; sem ângulos acima de 90°.
- Comparação 35³→49³: primeira origem deformação 0,11345→0,11080; última 0,12894→0,12978. Rotação 9,490°→9,417° e 15,735°→15,772°.

## BTC 1 hora

Seis origens válidas; três simulações pareadas por origem e modelo. Erros absolutos medianos:

| Métrica | SF1 | M5 | M6 |
|---|---:|---:|---:|
| Deslocamento | 0,239546 | **0,176836** | 0,224496 |
| Expansão (log volume) | 0,165983 | 0,188660 | **0,156322** |
| Rotação de eixos identificáveis | **6,439°** | 12,855° | 8,126° |
| Deformação holdout registrada | 0,013133 | 0,014259 | **0,010764** |

Todas as seis origens admitiram comparação do ângulo, mas isso não garante confiabilidade de orientação em quaisquer outras janelas. Na comparação pareada M6 vs M5, M6 melhorou erro de deformação em **4/6**; deslocamento, expansão e ângulo também 4/6 cada, embora para deslocamento o erro mediano por variante tenha sido melhor para M5.

### Auditoria 1h de orientação

- Primeira origem: ângulo real 15,811°, bootstrap p10–p90 [8,257°,29,521°], amplitude **21,263°**, 8/8 identificáveis e 0% acima de 90°.
- Última origem: ângulo real 12,006°, p10–p90 [6,785°,29,239°], amplitude **22,453°**, 7/8 identificáveis, 0% acima de 90°.
- Na grade 49³ versus 35³, ângulos praticamente idênticos: primeira 15,8105°→15,8284°; última 12,0056°→11,9864°.
- Na última origem, a distância de holdout de deformação mudou de 0,14127 para 0,13371 com o refinamento; esse efeito de discretização/amostragem deve continuar auditado.

## Interpretação e limites

1. **Melhoria instrumental real:** separação operacional entre a orientação observável dos eixos e a deformação da casca após registro livre; a última agora permanece quantificável em superfícies sem orientação principal distinguível.
2. **Resolução de uma ambiguidade específica:** o ângulo-quociente eliminou os ângulos espúrios >90° nas quatro origens auditadas (2 por escala, 8 reamostragens cada). Isso **não** prova estabilidade universal da orientação nem elimina ambiguidades de alinhamento em formas complexas.
3. **M6 e geometria:** erro de deformação de holdout menor que M5 em 5/6 origens 1m e 4/6 1h. São amostras pequenas (três simulações por origem), e ganhos são pequenos próximos do piso de amostragem. Não inferir superioridade confirmatória nem uma lei.
4. **Rotação e deformação são distintas:** o ângulo dos autovetores não representa rotação física da informação; a matriz do ICP é escolhida para minimizar a diferença geométrica e **não** deve ser interpretada como giro real.
5. **Limites:** o alinhamento ICP multistart ainda pode estacionar em mínimos locais; a distância holdout depende do número de pontos e da grade. Reamostragens (8 por origem) oferecem diagnóstico, não intervalo de confiança calibrado. Os simuladores SF1/M5/M6 ainda não garantem reprodução de caudas, dependência de longo alcance nem regimes.
6. **Objeto:** isosuperfície extrínseca da distribuição em coordenadas gaussianizadas, distinta da curvatura intrínseca Fisher–Rao. O estudo não confirma tensão de mercado, causalidade nem vantagem preditiva.

## Decisão e próximo passo

Manter **SF1, M5 e M6** como referências concorrentes: M5 segue forte em deslocamento/memória da atividade, M6 tem vantagem exploratória para deformação residual, SF1 ocasionalmente aproxima melhor orientação. Antes de congelar um oscilador geométrico ou avaliar período confirmatório, precisamos calibrar o **piso de amostragem** do registro livre variando o número de pontos, validar bootstrap por mais janelas e ampliar os nulos temporais adequados. Não atribuir sentido econômico obrigatório à deformação.

## Reprodutibilidade

- Protocolo: `reports/PROTOCOLO_SGV_M9_20261009.md`
- Instrumento: `experiments/m9_registro_simetrico_3d.py`
- Testes: `tests/test_m9_registro_simetrico_3d.py`
- Workflow: `.github/workflows/m9-registro-simetrico-3d.yml`
- GitHub Actions aprovado: https://github.com/ana-rigel/sgv-geometria/actions/runs/37967131614
- Resultados originais JSON e CSV por timeframe nos artefatos de execução.
