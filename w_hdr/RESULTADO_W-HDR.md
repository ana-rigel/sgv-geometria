# W-HDR — resultado (14/10/2026)

Pré-registro `PREREGISTRO_W-HDR.md` (6c3e498) antes do código; código antes dos resultados da parte A. A parte B regenera as 630 comparações do U2 e confere: 630 de 630 casadas, diferença máxima nas variáveis convencionais 7·10⁻¹⁵. Durante a parte B, um embrulho de função acumulava a cada tarefa e deixava a execução lenta; os valores não mudavam (o embrulho mais externo, com a semente certa, escrevia por último) e foi corrigido. Tabelas completas em `resultados/W-HDR_tabelas.md`.

## Parte A — detecção com dose-resposta (30 alternativas por célula, limiar q95 de 30 nulos de calibração)

Falso alarme na conferência: M11-I 11 %, W₂ 11 %, W₂-HDR 9 %, MMD 5 %, |ΔD| 7 % (o q95 de 30 nulos é ruidoso; o esperado era 5 %).

| Mecanismo, k = 1 | M11-I distância | W₂ completo | W₂-HDR | MMD² |
|---|---|---|---|---|
| translação | 0,07 | 0,67 | 0,93 | 1,00 |
| escala | 0,10 | 0,47 | 0,70 | 1,00 |
| rotação | 0,10 | 0,13 | 0,20 | 0,37 |
| bimodal | 0,70 | 0,20 | **0,87** | 0,27 |
| curvatura | 0,77 | 0,53 | **0,87** | 0,67 |
| caudas | 0,20 | 0,73 | 0,27 | 0,80 |

- A distância do M11-I não detecta translação, escala nem rotação. Isso é por construção: a assinatura normaliza posição, tamanho e orientação antes de medir. Ela é uma distância de **forma**, e só deve ser comparada nas três últimas linhas.
- Nas formas, a "distância no HDR" feita por transporte (W₂-HDR) é o melhor detector: 0,87 em bimodal e curvatura, contra 0,70 e 0,77 do M11-I. Em intensidade baixa os dois empatam dentro do ruído de 30 casos (bimodal k = 0,25: M11-I 0,40, W₂-HDR 0,30; k = 0,50: 0,20 e 0,23).
- O MMD com banda pela mediana é o melhor em translação, escala e caudas, mas quase cego a bimodalidade com momentos casados (0,27).
- Caudas ficam fora do HDR50: o W₂-HDR cai para 0,27, e o W₂ completo e o MMD veem (0,73 e 0,80).

Apostas: W₂ > M11-I em translação, escala, rotação e caudas — acertou, com empates nas intensidades mais baixas. M11-I ≥ W₂ completo em bimodal e curvatura em intensidade baixa — acertou. W₂-HDR > W₂ completo em bimodal e curvatura e < em caudas — acertou. MMD o melhor detector geral — **errou** (falha em bimodal e rotação). Falso alarme de 0 a 15 % — acertou.

## Parte B — rotular o mecanismo (as 630 comparações do U2)

| | M11-I | W | convencional | convencional + W | M11-I + W |
|---|---|---|---|---|---|
| F1 macro | 0,433 | 0,511 | 0,641 | 0,622 | 0,539 |

- W − M11-I: +0,078 (IC +0,018; +0,139). O painel W rotula melhor que o M11-I, sobretudo em caudas (+0,28) e translação (+0,29), mas **menos** em curvatura (−0,09; IC −0,23; +0,06).
- W − convencional: −0,130. Convencional + W − convencional: −0,019 (IC −0,045; +0,007). O W não acrescenta nada ao convencional e derruba o reconhecimento de "nada mudou" de 0,73 para 0,44.

Apostas: W > M11-I por mais de 0,10 — **errou** no tamanho (+0,08, mas com IC acima de zero). W < convencional — acertou. Convencional + W ≈ convencional — acertou. O resto de forma ajuda mais que o ΔD em bimodal e curvatura — **errou** (bimodal inconclusivo, curvatura a favor do M11-I).

## Leitura

A "distância no HDR" tem sentido, mas o jeito de medi-la importa: o transporte ótimo restrito aos pontos do HDR50 detecta mudança de forma melhor que a distância entre malhas do M11-I, sem malha, sem cascas inválidas (o M11-I falhou em 3–17 % das comparações) e em uma fração do tempo. Para dizer *qual* mudança foi, nem o M11-I nem o W acrescentam ao painel convencional de momentos. Nenhuma medida de distância é boa em tudo: a do HDR não vê caudas por definição, e o MMD com banda pela mediana não vê bimodalidade.
