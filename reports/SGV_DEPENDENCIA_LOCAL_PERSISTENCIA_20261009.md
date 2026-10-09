# SGV — Persistência local de dependências não gaussianas
**Data:** 09/10/2026 · **Ramo:** `research/dependencia-local-persistencia` · **Status:** exploratório concluído, não preditivo.

## Pergunta científica

O ganho dos modelos flexíveis para representar a distribuição conjunta de `X=(z, iota, nu)`, retorno normalizado, fluxo agressor e atividade, decorre somente da agregação temporal de diferentes regimes gaussianos, ou também persiste em subperíodos analisados separadamente?

**Sem exigência de nova lei, previsão de mercado ou independência dos indicadores usuais.** A questão é a fidelidade da fotografia da organização informacional observada.

## Configuração e proteção de dados

- BTCUSDT spot, apenas klines exploratórios verificáveis por checksum: **1m 2026-05 a 2026-07; 1h 2020-01 a 2024-12**. Nenhum período confirmatório reservado é lido.
- Janelas originais **não sobrepostas** de 1500 candles (1m) e 1008 (1h); cada janela repartida em duas metades cronológicas de 750/504 candles.
- Na janela total E EM CADA metade, o mapa de gaussianização de cada marginal é estimado usando **somente os primeiros 70% daquele segmento**. A última fração de 30% serve para avaliar log-verossimilhança comparativa dos modelos sobre dados ainda não usados no ajuste naquele segmento.
- Modelos: normal multivariada (referência), Student-t multivariada, mistura de duas gaussianas (GMM2) e KDE com parâmetros do experimento anterior congelados. A gaussiana/Student-t representa uma família de contornos elipsoidais; GMM2/KDE permitem outras dependências.
- Os ganhos são diferenças de log-score em **nats por observação** entre dois modelos avaliados nos MESMOS pontos e escala transformada. Valores absolutos de diferentes mapas de marginais **não** devem ser comparados.
- Incerteza: bootstrap de blocos de **4 janelas independentes em termos de observações**, com 2000 reamostragens; as estruturas temporais ainda podem correlacionar janelas adjacentes. CI95% exploratório, **não** confirmatório ou corrigido para múltiplas análises.

## Calibração sintética — cinco respostas conhecidas

Cada caso: 12 realizações, 1500 observações por realização, subdivididas em duas metades cronológicas.

Ganho médio da mistura gaussiana frente à gaussiana simples:

| Caso artificial | Janela inteira | Primeira metade | Segunda metade |
|---|---:|---:|---:|
| Estrutura gaussiana estacionária | -0,00631 | -0,01013 | -0,01455 |
| Correlação muda entre metades (mistura TEMPORAL) | +0,37797 | -0,00850 | -0,01011 |
| Duas dependências misturadas dentro de cada metade | +0,05170 | +0,08562 | +0,10307 |
| Marginais assimétricas independentes | -0,01434 | -0,01434 | -0,01353 |
| Dependência estrutural curvada (y~z²) | +0,48843 | +0,58738 | +0,56445 |

Poder do critério de ambas as metades positivas: **0/12** no nulo gaussiano; **0/12** na mistura apenas temporal; **6/12** na mistura persistente menos distinta; **12/12** na curva persistente forte. Portanto, o método pode distinguir causas em casos fortes, mas tem sensibilidade incompleta para certas misturas persistentes.

**Nota:** o critério não prova que as duas metades tenham distribuição idêntica, só que a complexidade modelável volta a aparecer em ambas.

## BTC real — ganhos em 1 minuto

**87 janelas originais**, janela = 1500, meia janela = 750 candles.

| Comparação | Janela completa | Primeira metade | Segunda metade | Média das metades |
|---|---:|---:|---:|---:|
| GMM2 - Gauss | +0,059745 | +0,065128 | +0,052429 | **+0,058778** |
| GMM2 - Student-t | +0,057604 | +0,061855 | +0,051833 | **+0,056844** |
| KDE - Gauss | +0,014114 | +0,025331 | +0,001787 | +0,013559 |
| KDE - Student-t | +0,011973 | +0,022058 | +0,001192 | +0,011625 |

- GMM2-Gauss, intervalo de confiança exploratório da média das metades: **[+0,047750; +0,068654]**.
- GMM2-Student-t, intervalo da média das metades: **[+0,045659; +0,067815]**.
- GMM2-Gauss positivo em ambas as metades em **79,31%** das janelas; mesma proporção frente à Student-t.
- O diferencial de ganho no agregado contra a média das metades para GMM2-Gauss foi somente **+0,000967** nat/observação (descritivo).
- KDE-Gauss nas metades tem intervalo **[-0,011369; +0,035496]**, incluindo zero. Nem todo estimador flexível obteve vantagem clara localmente.

**Interpretação restrita:** não é apenas a mistura simples de duas metades temporalmente diferentes que explica a maior qualidade descritiva da GMM2 nos dados de 1m. A vantagem é repetida localmente, mas as formas/parametrizações específicas podem mudar, e os resíduos de não estacionariedade dentro de cada metade ainda não foram modelados.

## BTC real — ganhos em 1 hora

**31 janelas originais**, janela = 1008, meia janela = 504 candles.

| Comparação | Janela completa | Primeira metade | Segunda metade | Média das metades |
|---|---:|---:|---:|---:|
| GMM2 - Gauss | +0,125522 | +0,123257 | +0,124327 | **+0,123792** |
| GMM2 - Student-t | +0,116707 | +0,117244 | +0,118439 | **+0,117841** |
| KDE - Gauss | +0,075217 | +0,068662 | +0,093441 | +0,081052 |
| KDE - Student-t | +0,066402 | +0,062650 | +0,087553 | +0,075101 |

- GMM2-Gauss, intervalo exploratório da média das metades: **[+0,100971; +0,137744]**.
- GMM2-Student-t, intervalo: **[+0,091932; +0,131555]**.
- GMM2-Gauss positivo em ambas as metades em **83,87%** das janelas; mesma proporção frente à Student-t.
- KDE-Gauss média das metades +0,08105, intervalo **[+0,06140; +0,09786]**.
- KDE-Student-t média das metades +0,07510, intervalo **[+0,05516; +0,08983]**.
- O ganho extra obtido ao agregar metades em GMM2-Gauss foi somente +0,00173 nat/observação.

**Interpretação restrita:** também em 1h a complexidade descritiva local reaparece. Não foi demonstrado que o estado geométrico seja o mesmo nas diferentes metades. Não foi demonstrado o número de modos ou topologia das superfícies de densidade.

## Validação de integridade

- GitHub Actions na revisão final: **23 testes automatizados aprovados**, incluindo testes sobre causalidade dos segmentos, consistência das métricas e aceitação/bloqueio explícito de nomes dos meses exploratórios/reservados.
- O primeiro replay falhou devido à formatação de quantificador em regex de filename: rejeitou maio/2026, período autorizado. Foi corrigido antes da revisão final; o gate permanece explícito e coberto por regressões. Não houve acesso ao período reservado na execução com erro.
- Os **três jobs da execução final passaram**: sintético, 1m e 1h. Arquivos JSON/CSV individuais foram anexados como artefatos.
- `main` e pré-registros históricos permaneceram intactos.

## O que sabemos agora

**SIM:** a representação conjunta das coordenadas observáveis exige, para boa qualidade de densidade neste estudo exploratório, mais flexibilidade que uma gaussiana e uma Student-t; o ganho da mistura reaparece em duas sub-janelas cronológicas independentes em grande parte dos intervalos 1m e 1h.

**NÃO demonstrado:** forma geométrica única, persistência da mesma topologia, duas regiões/modos reais, curvatura intrínseca, causalidade do fluxo, informação além dos indicadores disponíveis ou capacidade preditiva. Tais propriedades não são necessárias para o sucesso do instrumento descritivo.

**Próximo teste prioritário:** confrontar a persistência local com:
1. Nulos mais realistas, incluindo SF1 (dinâmica usual de fluxo agressor condicionada a preços e atividade), heterocedasticidade, sazonalidade de volume, autocorrelação e troca de regimes.
2. Precisão morfológica: ajuste de superfícies de nível em amostras separadas; distância de formas e número de componentes conexas sob bootstrap, evitando confundir componentes do GMM com modos reais.
3. Janela deslizante e streaming real prolongado: a foto muda a cada candle, mas a estimação não precisa inventar uma forma estável onde os dados não a suportam.

## Reprodutibilidade

- Branch `research/dependencia-local-persistencia`
- Código: `experiments/persistencia_dependencia.py`
- Testes: `tests/test_persistencia_dependencia.py`
- Workflow: `.github/workflows/persistencia-dependencia.yml`
- Execução final: https://github.com/ana-rigel/sgv-geometria/actions/runs/37933623707
- Na primeira execução houve falha de leitura por regex; a última execução a corrigiu, sem alterar parametrização ou seleção dos modelos.

**Conclusão:** a complexidade não gaussiana da dependência observada é *localmente recorrente*, em sentido descritivo, nas amostras exploratórias de BTC. Isso fornece razão suficiente para estudar a geometria temporal dessas distribuições, sem inventar lei geométrica, previsão ou curvatura intrínseca.
