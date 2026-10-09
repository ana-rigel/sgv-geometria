# SGV — Precisão da forma tridimensional e reconstrução da densidade
**Data:** 2026-10-09. **Ramo:** `research/precisao-forma-3d`. **Resultado:** 13 testes aprovados; sintético, BTC 1m e 1h concluídos na execução final.

## Objeto e método

Representar a distribuição conjunta de `X=(z, iota, nu)` com GMM2 versus normal 3D. Retorno normalizado por desvio-padrão **anterior**, desequilíbrio de compra agressora contemporâneo e atividade de volume relativa à mediana **anterior**. Descrever as regiões de maior densidade (HDR) 25%, 50%, 75% em grade [-3,3]³ com 21 pontos por eixo (verificação 27 em 8 janelas/escala), conectividade por 26 vizinhos e similaridade de Jaccard entre duas metades.

Cada janela histórica não sobreposta (W=1500 em 1m, 1008 em 1h) usa os primeiros 30% como âncora da normalização marginal (CDF empírica de treino). As duas metades seguintes usam essa **mesma escala anterior**, sem reestimar quantis sobre dados futuros. Cada metade tem seu próprio modelo de densidade estimado, e a forma se refere ao *período*, não a um estado instantâneo com a precisão de um tick.

**Importante:** as HDR abrangem porcentagens da massa DENTRO DA GRADE, não necessariamente toda a massa probabilística do modelo. A fração da massa capturada pela grade foi calculada e relatada. HDR no espaço de coordenadas observáveis ≠ topologia/curvatura intrínseca do manifold Fisher–Rao.

### Resultados por escala

| Indicador | 1m | 1h |
|---|---:|---:|
| Janelas completas válidas | 87 | 31 |
| HDR mistura Jaccard 25% | 0,39348 | 0,48632 |
| HDR mistura Jaccard 50% | 0,53191 | 0,60799 |
| HDR mistura Jaccard 75% | 0,61635 | 0,67310 |
| HDR normal Jaccard 25% | 0,51043 | 0,58737 |
| HDR normal Jaccard 50% | 0,59690 | 0,66880 |
| HDR normal Jaccard 75% | 0,65735 | 0,71541 |
| HDR 50% da mistura com metades desconexas | 0 | 0 |
| HDR 25% da mistura com alguma metade desconexa | 1/87 janelas | 0 |
| Cobertura mediana MIN entre metades pela grade (mistura) | 0,99184 | 0,99323 |
| Fração com cobertura mínima inferior a 0,85 | 1/87 | 0 |

A diferença entre Jaccard da mistura e a normal não é teste de fidelidade: a GMM pode representar densidade mais detalhada e flutuar mais por ter parâmetros adicionais. O controle de qualidade de ajuste posterior já foi avaliado em experimentos anteriores, mas **não** substitui o teste de estabilidade morfológica.

### Bootstrap em 8 janelas equiespaçadas por escala

Blocos circulares 15 candles no 1m e 12 no 1h, 29 repetições por janela. Produziu: (i) incerteza de ajuste interno na HDR em cada metade; (ii) nulo exploratório gerado de A|B combinado, aproximando a hipótese de mesma lei temporal.

| Medida na HDR 50% | 1m | 1h |
|---|---:|---:|
| Mediana da mudança observada (1-Jaccard) | 0,49323 | 0,44110 |
| Mediana do ruído local mediano | 0,19906 | 0,23244 |
| Janelas acima do limiar nulo p95 | 6/8 | 4/8 |
| Mediana ΔJaccard grade 21→27 | -0,00114 | -0,00494 |
| Concordância da conectividade na troca de grade | 8/8 | 8/8 |

No nível HDR 25%, acima do nulo: 5/8 (1m) e 4/8 (1h). No nível HDR 75%: 7/8 (1m), 3/8 (1h).

Esses p nominais têm apenas resolução de 1/30, e são numerosos (3 HDRs × 2 escalas × 8 janelas) sem controle múltiplo, de modo que **não são evidência confirmatória de mudanças topológicas**. A interpretação só vale sob as suposições do nulo combinado, o qual pode misturar estados genuinamente diferentes.

### Calibração sintética (6 réplicas por cenário, subconjunto 2 com bootstrap)

Jaccard HDR 50% da GMM: normal estacionária 0,81590; troca de regime 0,39189; mistura persistente 0,77653; relação curvada 0,77598; alternância predominantemente em atividade 0,76573; SF1 **default** 0,73525.

No pequeno subconjunto bootstrap, 2/2 mudanças temporais fortes ficaram acima do nulo local e 0/2 estacionárias foram sinalizadas. Essa amostra é insuficiente para inferir erro de tipo I real. O SF1 default **não foi ajustado a cada período BTC**, portanto não constitui um teste de independência estrutural ou de rejeição do SF1.

### Limitações científicas e de engenharia

- Melhora de log densidade do GMM sobre gaussiana (experimentos anteriores) não significa que a forma estimada seja estável.
- Um grupo GMM2 pode produzir uma HDR de um único componente conexo; duas gaussianas **não são** duas regiões reais.
- Coordenadas `z,iota,nu` não capturam toda a informação de mercado: faltam livro de ordens, cancelamentos, dados de trades individuais, liquidez e fluxos exógenos.
- Não há interpretação de causalidade informacional, previsão nem lei geométrica singular.
- HDR e Jaccard dependem do limiar, do sistema de coordenadas, da grade e da janela; mudanças de densidade também dependem dos regimes intrajanelas.
- Bootstrap condicional ao modelo e blocos fixados não preserva toda heterocedasticidade/autocorrelação.
- Benchmark REST anterior captou dois candles reais; não há ainda validação de operação 24 horas ininterruptas ou de um WebSocket real nesse runner.
- No replay foram usados apenas os períodos **exploratórios** BTC 1m maio–julho 2026 e BTC 1h 2020–2024; não foi aberto holdout confirmatório.

### Próxima etapa recomendada

1. Ampliar bootstraps, comparar comprimentos de bloco e intervalos de confiança das formas, controlar múltiplos testes. Formalizar estabilidade de uma deformação em relação à incerteza amostral.
2. Ajustar SF1 localmente e confrontar o mecanismo nulo com o BTC, controlando padrões sazonais e clusters de volatilidade.
3. Testar superfícies condicionadas à atividade, e trajetórias de regiões HDR em janelas deslizantes, distinguindo mudança da distribuição de mudança do estimador.
4. Consolidar especificação de observação contínua, ingestão causal e qualidade de dados antes de inferir dinâmica mais fina.

## Proveniência

- Código: `experiments/precisao_formas_3d.py`
- Testes: `tests/test_precisao_formas_3d.py`; 13 testes aprovados após correção da normalização da gaussiana **no teste de referência**, sem mudar modelos.
- GitHub Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37939421169 (3 jobs aprovados)
- Artefatos: `sgv-forma-3d-sintetico`, `sgv-forma-3d-1m`, `sgv-forma-3d-1h`.
- Ramo isolado, `main` intacta.
