# SGV-M3 — Resultado de precisão da não convexidade de isosuperfícies

**Data:** 09/10/2026. **Ramo:** `research/m3-precisao-nao-convexidade`. **Resultado:** três trabalhos GitHub Actions concluídos com sucesso; sete testes unitários aprovados; dados confirmatórios preservados.

## Objetivo

Avaliar se o índice `D_alpha=(1/A) integral_surface max(0,-K(x))*(3V/(4pi))^(2/3) dA`, obtido com Hessiana analítica projetada no plano tangente da superfície de densidade GMM2, é reproduzível quanto a **resolução da grade**, **amostragem em blocos** e **controle de sobreajuste contra distribuições convexas**. O índice permanece descritor geométrico: **não** é validado como tensão/estresse financeiro; M2 encontrou associações pequenas e de sinais opostos com discrepância condicional.

## Método congelado pré-execução

- Coordenadas `(z,iota,nu)` de candles BTC spot disponíveis no fechamento; mapa marginal congelado nos primeiros 30% de cada janela, duas metades posteriores separadas cronologicamente.
- Janelas completas sem sobreposição: W=1500 candles de 1m (maio–julho 2026) e W=1008 candles de 1h (2020–2024). Apenas meses de exploração, com allowlist e checksum.
- GMM2, HDR25/50/75 em grade 35³; duas outras grades 25³/49³ em janelas auditadas. Domínio e gates de qualidade herdados de M1/M2; malhas inválidas não produzem medições substitutas.
- Até 20 janelas distribuídas uniformemente ao longo de candidatas elegíveis; **três janelas pré-selecionadas por escala** para resolução e inferência preliminar.
- Bootstrap circular por blocos **dentro de cada metade**, 29 replicações por cenário, em comprimentos 1m L=8 e L=20; 1h L=6 e L=16. Reportar quantis p10/p50/p90 da distribuição de mudanças do índice por reajuste GMM2 — **não são intervalos de confiança calibrados para o estado verdadeiro**.
- Nulos morfológicos: gerar 29 conjuntos **independentes no tempo** por janela auditada, da gaussiana de média/covariância ajustadas à metade B, e da Student-t 5 graus de liberdade de mesma covariância. Reajustar a **mesma GMM2** ao nulo para medir curvatura espúria por ajuste flexível. O nulo não preserva memória temporal, sazonalidade ou mistura de regimes reais; exceder seus quantis não prova independência dos fatos estilizados do mercado.

## Resultado agregado do BTC

| Indicador | 1m | 1h |
|---|---:|---:|
| Janelas elegíveis | 87 | 31 |
| Janelas avaliadas | 20 | 20 |
| HDR25, índice mediano D | 0,122716 | 0,138164 |
| HDR50, índice mediano D | **0,131689** | **0,174758** |
| HDR75, índice mediano D | 0,145762 | 0,206410 |
| HDR25, déficit convexo C mediano | 8,590% | 12,785% |
| HDR50, déficit convexo C mediano | **5,966%** | **12,489%** |
| HDR75, déficit convexo C mediano | 5,206% | 11,591% |
| Janelas auditadas com bootstrap e resolução | 3 | 3 |
| Comparações de grade com D válido | 18 | 17 |
| Mediana de `abs(D(25³)-D(49³))` | **0,002897** | **0,001758** |
| HDR50 B observado acima do p90 de gaussiana reajustada a GMM2 | **3/3** | **2/3** |
| HDR50 B observado acima do p90 da t5 reajustada a GMM2 | **3/3** | **3/3** |
| HDR75 B válidas | 20/20 | 19/20 |

**Interpretação numérica:** no conjunto de pontos testados, a intensidade foi relativamente insensível à resolução da grade entre 25³ e 49³ em termos ABSOLUTOS. Essa pequena diferença **não garante convergência de toda a superfície**, sobretudo para valores de curvatura muito pequenos ou morfologias raras. A sensibilidade amostral (bootstrap) é bem maior do que a numérica para mudanças entre metades.

### Exemplos da variabilidade amostral — HDR50

- **1m, janela 0:** mudança observada `delta D=-0,11409`; bootstrap L8 p10/p50/p90: `[-0,17504;-0,06883;+0,03449]`; L20: `[-0,17757;-0,08000;-0,00851]`. Resultados sensíveis à escolha do bloco, impossibilitando afirmação forte de direção com esta amostra.
- **1m, janela 40:** `delta D=-0,00973`, bootstrap inclui sinais positivos e negativos em ambos os blocos; precisão insuficiente para a variação.
- **1m, janela 86:** `delta D=-0,06367`, bootstrap L8 `[-0,09253;-0,00713;+0,18004]`; L20 `[-0,11687;-0,02225;+0,23831]`.
- **1h, janela 0:** `delta D=-0,14255`; L6 `[-0,13508;-0,00374;+0,06324]`; L16 `[-0,16870;-0,01339;+0,09690]`.
- **1h, janela 14:** `delta D=+0,05480`, bootstrap L6 `[-0,14504;+0,01636;+0,10909]`, L16 `[-0,06823;+0,06075;+0,11962]`.
- **1h, janela 30:** `delta D=+0,03721`, bootstrap L6 `[-0,05040;+0,01423;+0,11646]`, L16 `[-0,05557;+0,01925;+0,11819]`.

Estes percentis descrevem uma distribuição de reamostragens, sem controle de cobertura sob não estacionariedade e heterocedasticidade. Não interpretar percentis como p-values nem afirmar que o sinal de `delta D` é confirmado.

## Controles de forma e calibração

- Rodada sintética com casos gaussiano, Student-t elíptico e mistura não gaussiana persistente, uma realização por caso. Calibração de engenharia, não estudo de poder de teste.
- Sete testes unitários aprovados antes dos replays (nulo gaussiano sem curvatura negativa na própria normal, reprodutibilidade do resampling, família t5, checagem de malha em três resoluções, rejeição de casos inválidos).
- Nos três conjuntos auditados de 1m, D observado no segmento B superou o percentil 90 dos 29 controles gaussianos e Student-t **após reestimar GMM2**; no 1h, 2/3 contra normal e 3/3 contra t5. **Mas com amostras minúsculas, quantis ruidosos e nulos temporalmente independentes, isso é exploração, não rejeição confirmatória de modelos convencionais.**
- Exemplo importante: primeira janela 1h apresentou `D_B≈0,00099`, abaixo do q90 gaussiano `≈0,04080`; logo, uma curvatura negativa pontual não implica deformação além do ruído de ajuste em todas as janelas.

## O que está demonstrado, e o que ainda falta

**Demonstrado no sentido instrumental:** isosuperfícies de densidade 3D, curvatura analítica, déficit volumétrico, reprodução descritiva do índice em resolução múltipla e distribuição inicial de variabilidade por bootstrap em blocos; execução reproduzível nos períodos exploratórios, sem leitura do holdout.

**Não demonstrado:** intervalos calibrados sob mudanças de regime, robustez universal, significância estatística de `delta D`, curvatura intrínseca Fisher–Rao, tensão financeira real, direção causal do fluxo, ganho de forecast ou uma lei geométrica especial.

**Próximo experimento científico:** intensificar reamostragem e ampliar janelas auditadas; atualizar o simulador SF1 para preservar persistência de atividade/fluxo, e incluir controles de heterocedasticidade e calendário. Só então avaliar quais deformações geométricas excedem nulos adequados em diferentes regimes. A observação por WebSocket contínuo ainda requer validação de integração e latência real.

## Reproduzir

- Protocolo: `reports/PROTOCOLO_SGV_M3_20261009.md`.
- Experimento: `experiments/m3_precisao_nao_convexidade.py`.
- Testes: `tests/test_m3_precisao_nao_convexidade.py`.
- Workflow: `.github/workflows/m3-precisao-nao-convexidade.yml`.
- Execução final bem-sucedida: https://github.com/ana-rigel/sgv-geometria/actions/runs/37950906618.
- Relatórios por escala em JSON e linhas de medição em CSV nos artefatos da execução.
- `main` intocada; períodos confirmatórios reservados protegidos.
