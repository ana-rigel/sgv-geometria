# SGV — Dinâmica das formas informacionais sob SF1 local
**Data:** 2026-10-09. **Ramo:** `research/dinamica-formas-sf1`.

## Objetivo
Avaliar se a deformação de regiões de maior densidade tridimensional de `X=(z,iota,nu)` observada no BTC difere daquela produzida pelo modelo nulo **SF1 ajustado apenas ao histórico anterior**. O objetivo é instrumentação descritiva; não antecipação de preços nem demonstração de lei geométrica.

## Procedimento causal
- Prefixo de 2.000 candles, estritamente anterior à janela avaliada: estimar SF1 via `fit_sf1`. O mesmo SF1 prevê trajetórias sintéticas futuras *sob seu próprio mecanismo*.
- Janela posterior de W=1500 candles (1m) ou 1008 (1h): CDF marginal da primeira fração de 30%, posteriormente forma 3D nos 35%+35% finais; a transformação não usa o futuro para ajustar mapas anteriores.
- Quatro simulações SF1 independentes por janela, com 1.700 barras de queima/aquecimento. Medir as sobreposições de Jaccard das HDRs 25%, 50%, 75%, para GMM2 e normal.
- Máximo de 12 janelas distribuídas por índice ao longo de cada período de exploração; stride W//2 torna janelas parcialmente **sobrepostas** e testes NÃO independentes.
- Apenas BTC 1m maio–julho 2026 e BTC 1h janeiro 2020–dezembro 2024; os arquivos passam pela allowlist exploratória e validação de checksums do downloader. A `main` não é editada.

## Controles antes dos resultados reais
Os testes incluem: seleção cronológica de janelas, exclusão de gaps, bloqueio de prefixo incompleto e invariância dos parâmetros SF1 a alterações **posteriores** ao prefixo. Calibração sintética altera somente taker_buy após o prefixo; os valores simulados nulos permanecem exatamente constantes sob mesma seed, enquanto a sobreposição morfológica observada muda.

## Advertências
- Apenas quatro trajetórias simuladas por janela não autorizam p-valores confirmatórios ou alegação de rejeição do SF1.
- O SF1 ajustado pode ser inadequado; é indispensável auditar resíduos, volatilidade, sazonalidade e dependência de longo prazo antes de interpretar diferenças como novas estruturas.
- Qualquer diferença de Jaccard mede uma região HDR modelada, não transferência causal de informação, topologia intrínseca do espaço Fisher–Rao ou singularidades geométricas.
- Mesmo uma vantagem observacional sobre o SF1 não demonstra utilidade preditiva; não é exigência deste estudo.
- A rotina faz avaliações em amostras limitadas, não é um serviço contínuo de streaming de produção.

## Reprodutibilidade
- `experiments/dinamica_formas_sf1.py`
- `tests/test_dinamica_formas_sf1.py`
- `.github/workflows/dinamica-formas-sf1.yml`
- Execução: https://github.com/ana-rigel/sgv-geometria/actions/runs/37940491529
