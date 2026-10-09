# SGV-M4 — SF1 com memória temporal e sazonalidade: resultados exploratórios
**09/10/2026 · ramo** `research/m4-sf1-memoria-sazonalidade` · **GitHub Actions final:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37954782378 — 3 jobs sucesso, 6 testes unitários aprovados.

## Motivação e pergunta
A auditoria anterior mostrou persistência de atividade `nu` muito maior no BTC do que no SF1 simulado em lag10, em 1m e 1h. O M4 tenta separar a contribuição da **memória de volume** e da **sazonalidade diária** e descobrir se suas correções melhoram o simulador usado como nulo morfológico. Não testamos trading, previsão, física, causa ou uma nova lei.

## Desenho comparativo
- SF1 original permanece intacto no módulo `sgvgeo/flow.py`. As ablações substituem **apenas a simulação de log-volume**, preservando o caminho de preço e desequilíbrio agressor idênticos por construção, validado por testes. Como a quantidade `taker_buy` escala com o volume, os valores absolutos de taker_buy mudam, mas a razão de fluxo agressor `iota` é preservada.
- Ajuste unicamente ao prefixo anterior da origem, com `fit_sf1` GARCH-t convergido, e regressão de log-volume: variante M possui lags 1,2,5,10; variante S possui lag1 e seno/cosseno diário; variante M+S combina. Regularização ridge, limite de soma de coeficientes AR e inovação reamostrada do prefixo.
- Prefixo e avaliação: **BTC 1m, 5000 candles passados + 1500 futuros para comparação**; **BTC 1h, 2000 passados + 1008 posteriores**. Quatro origens sem lacunas por escala; quatro trajetórias sintéticas por origem e por variante, burn-in 1700.
- Proteção de dados: BTC 1m maio-julho de 2026, BTC 1h 2020-2024, arquivos autorizados por allowlist e downloader com checksum; confirmação reservada intocada.
- S requer `>=3000` candles de prefixo e três dias completos. Isso permite S no 1m (5000 = 3,47 dias), mas **não** no 1h (2000 < 3000), embora 2000h cubram muitos ciclos diários. Sua indisponibilidade no 1h decorre de uma porta conservadora pré-definida e **não indica irrelevância da sazonalidade**.
- Comparar erro absoluto por origem, após tirar mediana das quatro simulações, para autocorrelação de nu lag1/lag10, sigma nu, correlações z/iota e abs(z)/nu, ACF iota lag1 e ACF abs(z) lag1.

## Resultados BTC 1 minuto (n=4 origens válidas)

| Variante | Erro absoluto mediano ACF(nu, lag1) | Erro absoluto mediano ACF(nu, lag10) | Erro mediano corr(abs(z),nu) |
|---|---:|---:|---:|
| SF1 original | **0,005335** | 0,348018 | 0,028725 |
| SF1 + memória M | 0,061328 | 0,055290 | 0,013389 |
| SF1 + sazonal S | 0,032330 | 0,317541 | 0,031014 |
| SF1 + M+S | 0,064134 | **0,054731** | **0,011384** |

- A memória reduziu o erro médio-mediano da ACF10 em ~84%, mas deteriorou ACF1 de ~0,0053 para ~0,0613: **tradeoff entre escalas de memória**.
- A adição de sazonalidade à memória produziu pouca diferença na ACF10. S isolada melhorou pouco.
- Valores medianos de ACF10 da atividade simulada: SF1 0,00630, M 0,34290, S 0,04443, M+S 0,35003; ACF10 observada mediana 0,34649 (não confundir diferença de medianas com mediana do erro absoluto).
- Preservação exata dos preços e desequilíbrio agressor sintéticos em todas as variantes confirmada pelo teste. A correlação z/iota é idêntica por construção e continua discrepante em algumas origens.

## Resultados BTC 1 hora (n=4 origens válidas)

| Variante | Erro absoluto mediano ACF(nu, lag1) | Erro absoluto mediano ACF(nu, lag10) |
|---|---:|---:|
| SF1 original | 0,111688 | **0,150554** |
| SF1 + memória M | **0,100344** | 0,155987 |
| SF1 + sazonal S | **indisponível** | **indisponível** |
| SF1 + M+S | **indisponível** | **indisponível** |

- M melhorou ligeiramente ACF1, mas piorou ACF10 em relação ao SF1 original (erro 0,156 vs 0,151).
- Não existem resultados de sazonalidade na escala de 1h: não comparar modelos sem execução.
- Medianas simuladas ACF10: SF1 0,01647 e M 0,23826; mediana observada 0,19297. A mediana de erros absolutos por janela é a referência comparativa correta.

## Calibração / engenharia
- **6 testes automatizados passaram**; três jobs GitHub Actions concluídos. Um primeiro job falhou porque uma série Pandas exportada para NumPy era read-only. Foi corrigido com cópia explícita do vetor antes do burn-in, sem alterar hipóteses ou períodos.
- Testes asseguram que a alteração do futuro não muda o ajuste passado, que variantes não alteram trajetória simulada de preço ou `iota`, que sazonalidade tem porta de amostra, que a regularização dos coeficientes lag evita explosão e que modelos não disponíveis são reportados, não substituídos por valores.
- Variante nova de volume substitui as inovações originais conjuntas de volume/fluxo no SF1 por resíduos reamostrados separadamente. Isso pode alterar correlações condicionais/temporais apesar de preservar `iota` e preço em cada trajetória. É um limite do desenho e requer aperfeiçoamento do simulador de inovações acopladas.

## Interpretação científica
**Resultado positivo restrito:** lag10 da atividade em 1m, anteriormente mal representada, pode ser aproximada bem melhor por dinâmica com memória maior no log-volume, ainda que a ACF1 se deteriore.

**Resultado negativo/inconclusivo:** em 1h a correção por memória não melhora lag10; não houve sazonalidade testada. Não há nulo SF1 estendido já adequado em ambas as escalas.

**Implicação para SGV:** continuar usando SF1 como nulo com defeitos explícitos, não interpretar diferença de morfologia entre BTC e SF1 como nova estrutura geométrica além de mecanismos conhecidos. O índice de não convexidade M2/M3 permanece um **descritor geométrico observacional**, não indicador comprovado de estresse de mercado.

## Próximos testes
1. Aumentar número de origens e replicações; comparar erro multivariado de ACF1/lag10 e propriedades distributivas para não escolher modelo por métrica isolada.
2. Ajustar a exigência de `>=3000` candles sazonal no 1h (mantendo suficiente número de ciclos e preregistrando a mudança) para testar S e M+S.
3. Reavaliar acoplamento de resíduos volume-fluxo, sazonalidade intradiária, padrões de heterocedasticidade/volatilidade e diferenças de regimes.
4. Só depois repetir as geometrias HDR 3D sob uma referência mais fiel, sem exigir novidade/predição.

## Reprodução
- Protocolo: `reports/PROTOCOLO_SGV_M4_20261009.md`
- Código: `experiments/m4_sf1_memoria_sazonalidade.py`
- Testes: `tests/test_m4_sf1_memoria_sazonalidade.py`
- Workflow: `.github/workflows/m4-sf1-memoria-sazonalidade.yml`
- Execução final: https://github.com/ana-rigel/sgv-geometria/actions/runs/37954782378
- Saídas: arquivos JSON e CSV nos artefatos do Actions.
- `main` e amostras confirmatórias preservadas.
