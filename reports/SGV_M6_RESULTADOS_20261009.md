# SGV-M6 — Inovações emparelhadas e teste piloto da dinâmica HDR50

**Data:** 09/10/2026. **Ramo isolado:** `research/m6-acoplamento-residual-hdr`.  
**GitHub Actions:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37960253079 — 3 jobs encerrados com sucesso, **7 testes automatizados aprovados**. A `main` permaneceu intacta e nenhum período confirmatório reservado foi utilizado.

## 1. Pergunta

O SF1-M5 (memória de log-volume + sazonalidade diária) já melhora a fidelidade conjunta da atividade no BTC, mas simula resíduos de volume independentemente das inovações do fluxo agressor. O M6 testa se **acoplar empiricamente as inovações**, preservando o mesmo caminho sintético de retorno e `iota`, melhora (a) fidelidade da relação fluxo–atividade e (b) reprodução exploratória do índice de não convexidade `D` e sua mudança temporal `delta D`.

Esse objetivo é **observacional**: não testar previsão, lei geométrica, causalidade informacional ou estresse financeiro.

## 2. Implementação

### Dados e modelos
- Prefixo anterior à origem: 5000 candles BTCUSDT 1m (maio–julho/2026) ou 2000 candles BTCUSDT 1h (2020–2024). Futuro de avaliação: 1500 (1m) ou 1008 (1h). Todos os intervalos completos, sem gaps, arquivos restritos por allowlist de exploração e SHA-256 do downloader.
- SF1 original: GARCH-t em retornos e modelo acoplado `iota*` e log-volume, com reamostragem pareada de inovações originais.
- M5 independente: caminhos de preço e `iota` invariantes, volume simulado com defasagens 1/2/5/10 e harmônico diário; inovações de volume sorteadas independentemente do fluxo.
- M6: mesmas equações do volume M5, mas inovação de volume escolhida de 16 estratos empíricos determinados pelos quantis dos resíduos `e1` do fluxo do SF1, alinhados por candle aos resíduos de volume do modelo M5 no prefixo. A inovação `e1` simulada é recuperada invertendo GARCH e a equação recursiva do fluxo sintético.
- 4 origens por escala, selecionadas sem consultar resultados; 6 trajetórias sintéticas pareadas por origem. Comparações com o mesmo caminho de preço e `iota`. O valor absoluto de `taker_buy` muda ao acompanhar a nova trajetória de volume.
- Indicadores: perda conjunta M5, erros ACF(nu,1)/ACF(nu,10)/std(nu)/corr(abs(z),nu), mais erro de `corr(iota,nu)`, já que este era o alvo novo do M6.
- Morfologia: **HDR50 GMM2**, duas origens por escala e somente **3 réplicas por modelo**. Intensidade de não convexidade `D`, déficit do invólucro convexo e mudança `delta D` entre duas metades com transformação marginal fixada no segmento inicial da janela.

### Calibração sintética
Foram plantadas inovações conjuntas fortemente correlacionadas. Os resultados foram:
- Correlação empírica histórica das inovações: **0,83454**.
- Inovações simuladas reamostradas independentemente: **−0,00660**.
- Inovações simuladas condicionalmente por estratos M6: **0,82010**.

Isso demonstra que a implementação recupera um acoplamento conhecido e preserva preço/`iota` sintéticos, **não** que exista tal dependência forte no BTC real. **7 testes aprovados** (sintético plantado, inviolabilidade do ajuste do prefixo a alterações futuras, alinhamento, amostragem repetível, rejeição de gaps, integridade de preço/`iota` e falhas fechadas da geometria).

## 3. Resultados BTC real — estatística dos observáveis

| Escala / Critério (mediana de erro) | SF1 | M5 indep. | M6 acoplado |
|---|---:|---:|---:|
| **BTC 1m**, perda conjunta | 0,75598 | **0,29585** | 0,32968 |
| 1m, erro abs corr(iota,nu) | **0,03347** | 0,04502 | 0,03978 |
| 1m, erro ACF(nu,1) | **0,02009** | 0,06939 | 0,09987 |
| 1m, erro ACF(nu,10) | 0,34806 | 0,03543 | **0,01961** |
| **BTC 1h**, perda conjunta | 0,62812 | **0,41930** | 0,43204 |
| 1h, erro abs corr(iota,nu) | **0,10017** | 0,13658 | 0,11127 |
| 1h, erro ACF(nu,1) | 0,10001 | **0,08113** | 0,08396 |
| 1h, erro ACF(nu,10) | 0,19570 | **0,08839** | 0,10117 |

- Em 1m, o M6 aproximou `corr(iota,nu)` em **3 das 4 origens** relativamente ao M5, mas melhorou a perda conjunta em apenas **2/4**.
- Em 1h, a melhoria pareada em `corr(iota,nu)` ocorreu em **2/4** origens, e melhoria de perda conjunta em **2/4**.
- Em ambas as escalas, **M5 independente tem a menor perda conjunta mediana**. O M6 melhorou alguns atributos isolados, mas piorou outros.
- Correlação de inovações e1/e2 observada no prefixo real: média 1m **+0,03724**, 1h **+0,04733**. Gerada no M6: 1m **+0,02436**, 1h **+0,03884**. As inovações emparelhadas reais exibem correlações médias fracas; o controle sintético com `rho≈0.83` é demonstração de sensibilidade do código, **não um retrato quantitativo do mercado**.

## 4. Resultado geométrico exploratório HDR50

Em cada escala foram escolhidas duas janelas para comparar `D(B)` e `delta D=D(B)-D(A)`, com três simulações por variante. As quatro janelas reais passaram o controle geométrico, e as 36 realizações simuladas por variante/escala neste piloto foram válidas (cada origem × 3 réplicas; há 6 realizações por modelo por escala).

| Escala / janela | Delta D observado | Erro abs Delta D — SF1 | M5 | M6 |
|---|---:|---:|---:|---:|
| 1m, 1ª auditada | −0,03012 | **0,01426** | 0,06749 | 0,04762 |
| 1m, 2ª auditada | +0,00239 | 0,04256 | 0,00891 | **0,00222** |
| 1h, 1ª auditada | −0,01606 | **0,02264** | 0,08593 | 0,03133 |
| 1h, 2ª auditada | +0,01084 | 0,07685 | 0,02522 | **0,00936** |

Nas **quatro comparações pareadas M6 vs M5** para `delta D`, M6 apresentou erro menor. **Entretanto, SF1 original teve erro menor que M6 em duas dessas quatro**, e a métrica absoluta `D(B)` não apresentou domínio consistente de M6 sobre M5. Além disso, três simulações por modelo não bastam para quantis confiáveis.

### Intensidade absoluta D(B) — exemplos

- 1m janela inicial: observado **0,15519**; SF1 **0,02162**, M5 **0,04776**, M6 **0,04572** (M5 ligeiramente mais perto que M6).
- 1m janela final: observado **0,15735**; SF1 **0,02677**, M5 **0,06644**, M6 **0,09025** (M6 mais perto).
- 1h janela inicial: observado **0,16840**; SF1 **0,14085**, M5 **0,16814**, M6 **0,17358** (M5 mais perto).
- 1h janela final: observado **0,20747**; SF1 **0,13718**, M5 **0,07988**, M6 **0,09390** (M6 mais perto).

O controle SF1 original tem melhor resultado ocasional sobre **variação** geométrica embora pior fidelidade de atividade. Portanto, nenhuma comparação isolada prova superioridade morfológica geral.

## 5. Conclusões honestas

**Demonstrado:**
- Mecanismo de recuperação da inovação do fluxo simulada e reamostragem condicional de resíduos de volume historicamente alinhados funciona em controle plantado.
- Prefixo causal e preço/`iota` invariantes por construção; replays BTC nas duas escalas bem-sucedidos.
- M6 altera a fidelidade de correlações e pode melhorar a reprodução de mudanças de `D` em algumas janelas, mas não reproduz todas as métricas melhor que M5.

**Não demonstrado:**
- Superioridade geral sobre M5: a perda conjunta mediana foi **pior em ambas as escalas**.
- Assinatura de tensão/estresse financeiro, causalidade, novidade física/informacional ou trading alpha.
- Controle definitivo de não convexidade: ainda há pouca auditoria HDR50 (duas janelas/escala, três simulações por modelo), diferenças por regime e acoplamento residual médio real fraco.
- Curvatura intrínseca Fisher–Rao, pois `D` mede curvatura extrínseca das isosuperfícies de densidade estimada no espaço observável.

## 6. Próxima etapa recomendada: M7

1. Comparar `D(B)`, `delta D` e déficit convexo em mais janelas **sem calibrar os modelos sobre o futuro**, com mais simulações por janela e seleção de origens disjuntas.
2. Melhorar nulos temporais por memória, sazonalidade e persistência de regime/heterocedasticidade; examinar acoplamento residual **condicional não linear** em vez de apenas correlação média.
3. Estimar intervalos calibrados para `D` e `delta D` por bootstrap em blocos, controlar multiplicidade e testar várias grades HDR.
4. Separar qualidade da fotografia estatística do mercado da adequação do simulador nulo: SGV é instrumento observacional mesmo que a dinâmica seja completamente explicável por modelos comuns.

## Reprodutibilidade
- Protocolo: `reports/PROTOCOLO_SGV_M6_20261009.md`
- Código: `experiments/m6_acoplamento_residual_hdr.py`
- Testes: `tests/test_m6_acoplamento_residual_hdr.py`
- Workflow: `.github/workflows/m6-acoplamento-residual-hdr.yml`
- Artefatos `M6-synthetic`, `M6-BTC-1m`, `M6-BTC-1h`.
- Execução final: https://github.com/ana-rigel/sgv-geometria/actions/runs/37960253079.
