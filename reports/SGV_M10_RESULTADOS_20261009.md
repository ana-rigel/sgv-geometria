# SGV-M10 — Piso de amostragem do registro 3D: resultados

**Data:** 09/10/2026. **Ramo isolado:** `research/m10-piso-amostragem-registro`. **Execução final GitHub Actions:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37972700018. **Estado:** três jobs concluídos com sucesso, **7 testes aprovados**, dados confirmatórios não lidos, `main` preservada.

## Pergunta
Que parcela da distância Chamfer de holdout entre duas cascas HDR50 decorre **somente do sorteio independente de pontos sobre malhas fixas**? Como ela muda com 180, 360 ou 720 pontos? O excesso acima desse piso resiste ao refinamento da grade e à reamostragem temporal?

## Método
Instrumento do M9: malhas triangulares fechadas de HDR50 GMM2 da densidade em scores gaussianizados `(z,iota,nu)`; transformação marginal da âncora histórica congelada nos primeiros 30% da janela; duas fotografias nas metades posteriores. Alinhamento rígido por ICP multistart, centrar pelo centro de massa e normalizar pelo raio volumétrico equivalente. Treinar ICP em pontos de amostragem superficial, avaliar Chamfer simétrica em pontos **independentes** de holdout. O valor é um resíduo geométrico, não distância de transporte de probabilidade.

Para cada par de malhas e densidade `n`, seis sementes determinísticas: `d(A,B;n,s)` e controles internos `d(A,A;n,s)` / `d(B,B;n,s)`. Piso operacional `F=max(q90 self_A,q90 self_B)`. Mediana da distância entre fotografias `d*=median(d(A,B))`. Excesso censurado `E=max(0,d*-F)`, **não** uma estimativa sem viés nem p-valor. Registro no mesmo mesh com pontos independentes fornece `F>0` mesmo quando não houve alteração geométrica alguma.

BTC spot exploratório apenas, proteção por checksum/allowlist: 1m maio–julho 2026 e 1h 2020–2024. Seis janelas completas/disjuntas selecionadas equiespaçadamente por escala. Três janelas predefinidas por escala auditadas com 180/360/720 pontos, grade 35³ versus 49³ e 16 reamostragens circulares por blocos de cada fotografia (1m L15; 1h L12). O bootstrap temporal usa três sementes para controle de piso por réplica e quantis p10/p50/p90; **não constitui intervalo de confiança calibrado**.

## Calibração sintética (7 testes aprovados)
Uma esfera transladada, girada e escalada uniformemente é rigidamente equivalente depois da normalização; outra sofre distorção real dos semieixos. A medição de holdout da primeira mantém distância positiva pelo erro de amostragem. Resultados:

| Pontos por superfície | Piso self equivalente | Distância entre formas rigidamente equivalentes | Distância entre forma original e deformada | Excesso deformada |
|---|---:|---:|---:|---:|
| 180 | 0,138617 | 0,131417 | 0,187463 | 0,044191 |
| 360 | 0,095185 | 0,091923 | 0,161741 | 0,065274 |
| 720 | 0,066818 | 0,065509 | 0,143311 | 0,074239 |

A queda do piso de 180 para 720 pontos é aproximadamente 52%. A distância bruta também decresce com aumento de pontos mesmo quando há deformação verdadeira; por isso comparar residuais obtidos com n diferentes sem normalização/controle é inadequado.

## BTC real — resultado agregado

| Medida (n=360 salvo observação) | BTC 1m | BTC 1h |
|---|---:|---:|
| Janelas elegíveis | 87 | 31 |
| Janelas avaliadas/válidas | 6/6 | 6/6 |
| Distância bruta mediana d* | 0,125768 | 0,140088 |
| Piso de amostragem local mediano F | 0,104279 | 0,105074 |
| Excesso local mediano E | **0,018981** | **0,034972** |
| Janelas com d* acima do piso F | **6/6** | **6/6** |
| Três auditorias por escala | 3 | 3 |
| Mediana |E(grade 35³)-E(49³)| | 0,002325 | 0,002929 |

**Interpretação estrita:** em todas as janelas o registro entre duas malhas HDR50 diferentes gerou distância acima do percentil 90 do auto-registro das próprias malhas fixas. Isto é indício *operacional* de diferença observável de malhas acima do piso de pontos. Não equivale a significância estatística da mudança da distribuição geradora, pois nem o GMM2 nem as observações temporais foram congelados nesse nulo. A incerteza de estimação das duas fotografias pode explicar parte das diferenças.

### Controle de densidade — valores medianos entre as três origens auditadas

| N pontos | Piso 1m | Piso 1h |
|---|---:|---:|
| 180 | 0,152661 | 0,148560 |
| 360 | 0,104769 | 0,104824 |
| 720 | 0,073476 | 0,074960 |

O piso diminuiu de modo coerente em ambos os timeframes. Esses valores são específicos das formas amostradas, de como a área é distribuída, do algoritmo ICP multistart e da normalização por volume.

### Excesso não estável em magnitude entre número de pontos

Nas janelas auditadas, o excesso cresceu várias vezes ao aumentar n: por exemplo 1m janela central `E=0,04255 (n180)`, `0,06831 (n360)`, `0,07444 (n720)`; 1h janela inicial `E=0,05435`, `0,06342`, `0,07544`. **Não confundir o aumento de E com aumento de deformação no tempo**: a malha temporal A/B é a mesma em cada linha; o valor varia somente porque diminuiu o piso de amostragem e mudou a aproximação da distância geométrica.

## Incerteza por bootstrap temporal (três janelas auditadas por escala)

Todas as **48 reamostragens por escala** produziram malhas válidas e medidas de excesso. Mas as amplitudes de variação foram relevantes:
- 1m, primeira janela, excesso p10/p50/p90: [0,02918;0,04739;0,06913]; janela central [0,03479;0,05869;0,09215]; última [0,01610;0,02436;0,05668].
- 1h, primeira: [0,02822;0,04438;0,07294]; central [0,02479;0,03315;0,06121]; última [0,03187;0,04251;0,05268].
- A orientação dos eixos foi identificável em 1m 16/16, 8/16, 16/16 repetições nas três janelas, e em 1h 15/16, 16/16, 8/16. Isso demonstra a necessidade de não representar ângulo indisponível por valor 0.
- Variação do `E` por bootstrap é significativamente maior, em escala numérica descritiva, que a alteração mediana de `E` causada pelo refinamento 35³→49³. **Não há aqui teste formal de significância**, e quantis de bootstrap não garantem cobertura sob regimes/heterocedasticidade.

## Limitações e decisão

1. **Instrumento calibrado parcialmente:** quantificamos o erro de amostragem de pontos em malhas fixas e sua sensibilidade ao número de pontos. O algoritmo de otimização ICP pode convergir para mínimos locais. Ainda não há comparação contra projeção de distância à superfície contínua que elimine o ruído de pontos.
2. **Piso é condicional à forma e às amostras:** não aplicar constante universal `0,1` a todos os objetos; não interpretar o excesso `d*-F` como distância geométrica com erro subtraído de modo exato.
3. **Não rejeitamos nulo de mesma distribuição geradora:** diferenças do ajuste GMM e da segmentação temporal continuam. Para isso é necessário bootstrap sintético temporal com regimes e estimadores reajustados, múltiplas sementes, calibração da taxa de alarme e comparação fora da exploração.
4. **Rotação não é giro físico**, e a deformação não é tensão financeira nem sinal de trading. A casca estimada é geometria extrínseca da densidade em coordenadas transformadas, não curvatura Fisher–Rao intrínseca.
5. Números pequenos de janelas (6/timeframe) e de réplicas de piso (6) não permitem determinar poder ou erro tipo I. Não abrir a confirmação.

## Próximo experimento recomendado — SGV-M11
Calcular a **distância direta de pontos da malha à superfície contínua** (ou um estimador com muitas amostras comuns de referência), para estimar o limite da Chamfer sem piso arbitrário; repetir sob nulos de mesma distribuição observada com autocorrelação e regimes, com pré-registro de limites de alarme. Só então avaliar, em janelas independentes, quando uma alteração geométrica excede o ruído do estimador. Comparadores SF1/M5/M6 permanecem secundários.

## Reprodutibilidade
- Protocolo: `reports/PROTOCOLO_SGV_M10_20261009.md`
- Código: `experiments/m10_piso_amostragem_registro.py`
- Testes: `tests/test_m10_piso_amostragem_registro.py`
- Workflow: `.github/workflows/m10-piso-amostragem-registro.yml`
- Replays e JSON/CSV: https://github.com/ana-rigel/sgv-geometria/actions/runs/37972700018
- `main` e dados confirmatórios reservados preservados.
