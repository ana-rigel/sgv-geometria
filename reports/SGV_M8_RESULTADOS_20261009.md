# SGV-M8 — Transformações tridimensionais de superfícies HDR50: resultados

**Data:** 09/10/2026. **Ramo:** `research/m8-transformacoes-forma-3d`.  
**GitHub Actions:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37966070545.  
**Execução:** três jobs concluídos com sucesso (calibração sintética, BTC 1m e BTC 1h), **sete testes aprovados**. `main` e períodos confirmatórios preservados.

## Objeto e método

M8 abandona a expectativa de que a diferença de um único índice D descreva toda a transformação. Estimamos isosuperfícies HDR50 de GMM2 de `(z,iota,nu)` a partir de uma âncora histórica (30% primeiros candles para transformação marginal), e duas fotografias seguintes (~35/35%). A densidade estimada gera malhas via Marching Cubes no limiar da HDR50, com gates de qualidade para fechamento, truncamento e massa coberta.

Medimos quatro observáveis parcialmente convencionais:
1. **Deslocamento** `||c_B-c_A||`: centros volumétricos das HDRs no espaço de scores fixo.
2. **Expansão** `log(V_B/V_A)`: variação relativa do volume geométrico, não necessariamente entrada de volatilidade.
3. **Rotação** em graus: transformação dos eixos principais volumétricos, apenas se autovalores distinguíveis; eixo simétrico → indefinido, sem preenchimento por zero.
4. **Deformação residual**: distância Chamfer amostrada entre cascas após centro, escala isotrópica e alinhamento de orientação por eixos; não é deslocamento material nem transporte de massa e depende da convenção de registro.

O M8 preserva os parâmetros do prefixo de ajuste SF1 e simula quatro atributos de movimento por comparação entre SF1, M5 e M6 com trajetórias de preço e agressão relativa `iota` pareadas. A comparação é exploratória: seis origens não sobrepostas por escala, três simulações por origem/modelo; origin-level bootstrap com 12 réplicas em três origens, grade 35³ e 49³ em duas origens. BTCUSDT spot **somente exploratório**, 1m maio–julho de 2026 e 1h 2020–2024, allowlist e SHA-256 do downloader.

## Calibração

Sete testes unitários passaram:
- translação conhecida de uma esfera `[0,4;-0,3;0,2]` sem alegação de rotação identificável;
- expansão e translação de elipsoide sintético;
- a orientação próxima de degeneração não vira rotação zero;
- integridade de comparação pareada e de quantidade mínima de pares;
- bootstrap descritivo, sem inferência de precisão com poucas réplicas;
- checagem 35³/49³;
- falha fechada em lacunas temporais.

## BTC de 1 minuto: erros absolutos medianos (6 origens válidas)

| Movimento | SF1 | M5 independente | M6 acoplado |
|---|---:|---:|---:|
| Translação, norma | 0,524827 | **0,474129** | 0,526101 |
| Expansão, módulo de erro de log(VB/VA) | 0,185522 | **0,161992** | 0,210616 |
| Rotação, erro angular | 5,1504° | 39,6515° | **4,0674°** |
| Deformação residual, erro Chamfer | 0,007461 | **0,002974** | 0,015292 |

A disponibilidade de rotação/deformação residual foi de **4/6 origens**, por não identificação de orientação nos demais casos. Na comparação M6 versus M5: M6 venceu em 2/6 translações, 3/6 expansões, 2/4 rotações, 1/4 deformações. **Não há modelo dominante**.

### Exemplos 1m e incerteza

- Primeira janela: translação observada 0,61914, `log(VB/VA)=-0,09018`, rotação ≈9,49°, deformação residual ≈0,09146. Na grade 49³: translação 0,61867, log-volume −0,08270, rotação ≈9,42°, residual ≈0,09138.
- Última janela: translação 1,06402; log-volume +0,15391; rotação ≈15,73°; residual ≈0,11926. Na 49³: translação 1,06376; log-volume +0,15998; rotação ≈15,77°; residual ≈0,11656.
- Em janela intermediária, gap de autovalores 0,05 e 0,0098: eixo global não identificável. Rotação e residual alinhado mantidos **nulos**, não zero.
- Reamostragens em blocos (12 × 3 janelas) mostraram variabilidade, especialmente de volume; percentis p10/p50/p90 **não são intervalo de confiança calibrado**.

## BTC de 1 hora: erros absolutos medianos (6 origens válidas)

| Movimento | SF1 | M5 independente | M6 acoplado |
|---|---:|---:|---:|
| Translação, norma | 0,233961 | **0,177628** | 0,236885 |
| Expansão, erro log(VB/VA) | 0,174510 | 0,189113 | **0,156547** |
| Rotação, erro angular | **7,2030°** | 22,7045° | 27,7010° |
| Deformação residual, erro Chamfer | 0,015801 | 0,014872 | **0,013232** |

As seis origens 1h forneceram medidas globais e orientação identificável pelo gate original. M6 versus M5: 3/6 com menor erro de deslocamento; 4/6 com menor erro de expansão; 3/6 de rotação; 3/6 de deformação. Tampouco existe vencedor uniforme.

### Exemplos 1h e cautela angular

- Primeiro período auditado: translação observada 0,51832, log-volume −0,23285, rotação 15,81°, deformação residual 0,12352. Grade 49³: translação 0,51907, log-volume −0,23321, rotação 15,83°, residual 0,12048.
- Último período: translação 0,64323, log-volume +0,24493, rotação 12,01°, residual 0,11998. Grade 49³: translação 0,64361, log-volume +0,23734, rotação 11,99°, residual 0,12034.
- Numa janela intermediária, reamostragens produziram rotação aparente tão grande quanto ≈172°, apesar de rotação original moderada e gate de autovalores formalmente aprovado. **Isso constitui um alerta de orientação/equivalância de eixos**: precisamos auditar a determinação de rotação em amostras bootstrap antes de interpretá-la como fenômeno do mercado. A ausência de erro numérico de grade em outras janelas não remove essa incerteza.
- Os quantis de bootstrap relativos à rotação são meros diagnósticos de reamostragem; a ambiguidade de alinhamento pode causar valores espúrios grandes.

## Conclusão científica

**Foi implementado e testado um observador quantitativo dos quatro tipos de transformação da forma tridimensional**, respeitando limites de fechamentos de malha e de observabilidade de rotação. O deslocamento, a expansão e a deformação residual têm concordância inicial entre resoluções em janelas testadas; **inferência sobre sua estabilidade temporal generalizada ainda é incerta**. A rotação requer auditoria adicional do grupo de simetrias dos autovetores, degenerescência e estabilidade de alinhamento por bootstrap.

As quatro medidas não constituem decomposição matemática aditiva única; são descritores complementares da forma de densidade em um sistema de coordenadas específico. Os rankings mostram que **SF1, M5 e M6 são melhores em atributos diferentes**. Não há nulo estatístico dominante, relação com estresse de mercado comprovada, causalidade, nova lei geométrica ou vantagem preditiva.

## Próxima etapa recomendada — M9

1. Calibrar rotação no quociente de simetrias dos eixos e determinar erro angular estável apenas quando orientação material for identificável; utilizar distância entre subespaços quando autovalores quase empatados.
2. Separar **deformação residual independente de orientação global** quando possível (otimização de alinhamento contínuo com controle de sobreajuste) da rotação de eixos principais — caso contrário conservar nulos.
3. Ampliar a auditoria de incerteza e comparação por regimes antes de nomear um indicador de mudança geométrica.
4. Preservar dados confirmatórios fechados até critérios de estabilidade e instrumentação serem congelados.

## Reprodutibilidade

- Protocolo `reports/PROTOCOLO_SGV_M8_20261009.md`
- Experimento `experiments/m8_transformacoes_forma_3d.py`
- Testes `tests/test_m8_transformacoes_forma_3d.py`
- Workflow `.github/workflows/m8-transformacoes-forma-3d.yml`
- GitHub Actions https://github.com/ana-rigel/sgv-geometria/actions/runs/37966070545
- Arquivos JSON e CSV individuais nos artefatos `SGV-M8-BTC-1m` e `SGV-M8-BTC-1h`.
