# SGV-M11 — Distância direta à superfície triangular e nulo temporal simplificado

**Data:** 09/10/2026. **Ramo isolado:** `research/m11-distancia-superficie-nulos-temporais`. **Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37976030631. **Estado:** três trabalhos GitHub Actions concluídos com sucesso; seis testes aprovados; `main` intacta e períodos confirmatórios reservados não lidos.

## Pergunta científica

No M10, uma distância Chamfer baseada em dois conjuntos independentes de pontos amostrados sobre as superfícies produzia um piso positivo mesmo entre malhas idênticas. M11 busca uma medida próxima da distância superfície–superfície sem esse piso artificial e separa o **erro numérico de integração** da **variação estatística do ajuste de densidade**.

## Método registrado e implementado

- Casca HDR50 da GMM2 estimada a partir das duas metades posteriores da janela, após transformação marginal da âncora inicial de 30% congelada. Grade Marching Cubes 35³, checagem 49³ nas janelas auditadas, gates de malha fechada/não truncada/cobertura de massa.
- Remover deslocamento e escala volumétrica; ajustar orientação livre por ICP multistart somente a pontos de treino. A rotação escolhida **não é interpretada como rotação física do mercado**.
- Selecionar pontos **determinísticos por área de faces** nas superfícies trianguladas (256 ou 512) e calcular **distância euclidiana exata de cada ponto à superfície triangular oposta**. Usa busca KDTree de centroides com limite conservador pelo maior raio de triângulo, seguido de projeção exata nos triângulos candidatos. O cálculo da distância por ponto é exato até precisão numérica; a **integral global continua aproximada por quadratura finita**.
- Distância simétrica `(media_A→B + media_B→A)/2`, sem identificação de transporte ótimo nem curvatura intrínseca da geometria estatística.
- Seis janelas BTCUSDT spot exploratórias por escala, não sobrepostas, com timestamps contínuos. Para duas janelas por escala: 12 pares de reamostragens circulares de blocos **A/B separados** (sensibilidade estatística da medição), além de 12 pares provenientes de A+B *pooled* (nulo aproximado de uma distribuição comum estacionária). Blocos de comprimento 15 candles em 1m e 12 em 1h.
- Apenas arquivos autorizados: 1m maio–julho/2026; 1h 2020–2024, downloader restrito e checagensums SHA256. Holdout confirmatório preservado.

## Controle sintético

**6 testes aprovados.** Calibração:
- Malha comparada com ela própria: distância simétrica `4,84e-17`, numericamente zero.
- Malha rigidamente equivalente depois da normalização/alinhamento: distância direta com 512 pontos `0,00086945`.
- Malha deliberadamente deformada: `0,13575344`.
- Alteração relativa de resolução de quadratura 256→512 no controle rígido ≈0,00075 (como proporção), no deformado ≈0,00378.
- Teste da distância ao triângulo mais próximo comparando explicitamente a busca espacial otimizada com um cálculo **exaustivo sobre todas as faces**, em pontos de teste.

Isso resolve operacionalmente o piso de **amostragem independente dos pontos de avaliação** observado no M10, sem remover todas as outras fontes de erro (alinhamento, grade, estimador de densidade ou quadratura).

## BTC real 1 minuto (seis janelas válidas, entre 87 elegíveis)

| Indicador | Resultado |
|---|---:|
| Mediana da distância com 256 pontos de quadratura | 0,057247 |
| Mediana da distância com 512 pontos | 0,057923 |
| Mediana da diferença relativa 256→512 | 1,5704% |
| Janelas auditadas com nulo pooled | 2 |
| Observada acima de q90 do nulo pooled | **0/2** |
| Refit temporal válido nas auditorias | 24/24 |

- Primeira origem auditada: distância 512 `0,0677709`, q90 pooled `0,0796909`. Refits separados p10/p50/p90 `[0,05084;0,08465;0,11298]`. Alterar grade 35³→49³ mudou a distância para `0,0663353`.
- Última origem auditada: distância 512 `0,0436314`, q90 pooled `0,0947505`. Refits separados p10/p50/p90 `[0,03861;0,07241;0,10611]`. A distância com grade 49³ foi `0,0432486`.

A relação real–nulo indica que, nesse conjunto muito pequeno, **não** há evidência exploratória de diferença acima do controle pooled de blocos, embora as malhas estimadas sejam diferentes e produzam distância positiva.

## BTC real 1 hora (seis janelas válidas, entre 31 elegíveis)

| Indicador | Resultado |
|---|---:|
| Mediana da distância com 256 pontos de quadratura | 0,078146 |
| Mediana da distância com 512 pontos | 0,077968 |
| Mediana da diferença relativa 256→512 | 2,1513% |
| Janelas auditadas com nulo pooled | 2 |
| Observada acima de q90 do nulo pooled | **2/2** |
| Refits temporais válidos nas auditorias | 23/24 |

- Primeira origem auditada: distância 512 `0,1206907`, q90 do nulo pooled `0,0970943`; refits separados p10/p50/p90 `[0,06279;0,09203;0,13946]`; grade 49³ deu `0,1218352`.
- Última origem auditada: distância 512 `0,0758575`, q90 do pooled `0,0658040`; refits separados `[0,05680;0,08277;0,10934]`; grade 49³ deu `0,0767151`.

No nulo pooled simplificado, ambas as distâncias excederam q90. Isso **não** é rejeição confirmatória da estabilidade nem implica que o mercado possua força física ou mecanismo geométrico especial. Nulos que não preservam memória longa, regimes e sazonalidade podem gerar taxas falsas de alarme.

## Conclusões

1. **Resultado instrumental positivo:** distância à malha triangular elimina quase totalmente o piso ocasionado por amostragens independentes de pontos das superfícies *de avaliação*. Com malhas exatamente iguais, a distância é numericamente nula. Alinhamento ICP e quadratura ainda têm erro.
2. **Convergência preliminar:** mudança relativa mediana entre quadratura 256 e 512 foi de 1,57% no 1m e 2,15% no 1h. Concordância também favorável nas quatro verificações pontuais de malha 35³→49³. Não estabelece convergência universal.
3. **Resultados temporais divergentes:** 0/2 (1m) e 2/2 (1h) distâncias acima de q90 do nulo de blocos pooled; **amostra insuficiente para inferência**. Janelas de 1h podem integrar regimes mais longos e o método do nulo pode ser inadequado.
4. **Variabilidade de estimação ainda material:** percentis de refit separado frequentemente cobrem intervalos amplos; uma comparação superficial rigorosa exige quantificar reestimação do GMM e dependência temporal, não apenas erro da métrica.
5. **Próxima etapa apropriada:** expandir as janelas auditadas, comparar diferentes comprimentos de bloco e implementar nulos temporais capazes de reproduzir persistência de volume, sazonalidade e heterocedasticidade. Definir gate de estabilidade instrumental antes de interpretação econômica.
6. A superfície é geometria **extrínseca** da densidade estimada em espaço gaussianizado; não curvatura Fisher–Rao intrínseca, tensão financeira, causalidade informacional ou vantagem preditiva.

## Reproduzir

- Protocolo: `reports/PROTOCOLO_SGV_M11_20261009.md`
- Código: `experiments/m11_distancia_superficie_nulos.py`
- Testes: `tests/test_m11_distancia_superficie_nulos.py`
- Workflow: `.github/workflows/m11-distancia-superficie-nulos.yml`
- Dados completos JSON e CSV em artefatos Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37976030631
