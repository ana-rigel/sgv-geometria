# SGV — Morfologia de superfícies informacionais: calibração e BTC exploratório
**Data:** 2026-10-09. **Ramo:** `research/morfologia-superficies`. **Status:** bateria executada no GitHub Actions, sem tocar períodos confirmatórios ou `main`.

## Qual objeto foi reconstruído?

Primeira superfície de densidade bidimensional de `(z, iota)`: retorno normalizado e desequilíbrio do fluxo agressor. A atividade `nu` faz parte do sistema SGV, mas **não entrou nesta fatia 2D**. Logo, o teste não reconstruiu a geometria informacional conjunta completa de três variáveis.

Cada janela de 1.500 barras no 1m ou 1.008 no 1h:
1. Os primeiros 30% das observações estabelecem um mapa de postos para scores gaussianizados, sem olhar o futuro.
2. Os 70% restantes são divididos em duas metades cronológicas; cada metade ajusta separadamente uma normal bidimensional e uma mistura de duas gaussianas.
3. Em uma grade fixa de 61×61 pontos em [-3,3]², determina-se a região que contém 50% da **massa de densidade discretizada dentro da grade** (*highest density region*, HDR). A normalização não representa 50% exatos da massa probabilística fora da grade.
4. Medem-se componentes conexas com 8 vizinhos e Jaccard (interseção/união) entre HDRs das duas metades. A comparação com a normal fornece uma referência de estabilidade morfológica.
5. Comparam-se resultados com geradores sintéticos gaussianos estacionários, mudança temporal de correlação, dependência não gaussiana persistente, relação curvada e o gerador `default_sf1` já existente no SGV.

**Atenção:** componentes conexas de uma região estimada numa grade NÃO são as componentes de um manifold intrínseco, e o número de componentes de um modelo GMM2 não equivale ao número de modos densitários.

## Calibração sintética (10 réplicas por caso)

| Gerador | Jaccard médio GMM, metades | Jaccard médio normal, metades | Ambas as HDRs GMM conexas |
|---|---:|---:|---:|
| Normal estacionária | 0,8804 | 0,8998 | 100% |
| Mistura temporal (troca de regime entre metades) | 0,3906 | 0,4015 | 100% |
| Dependência não gaussiana misturada persistentemente | 0,7312 | 0,8899 | 100% |
| Relação curvada | 0,7818 | 0,8818 | 100% |
| **SF1 nulo estilizado** | **0,8677** | **0,9020** | 100% |

Esses números estabelecem o comportamento do instrumento nesses geradores específicos, não calibram uma distribuição de confiança universal. O SF1 usado foi `default_sf1()` sem ajuste neste teste às propriedades temporais do BTC em cada escala; portanto **não** é uma rejeição estatística de SF1.

## Bitcoin real, somente exploração

| Indicador | BTCUSDT 1m | BTCUSDT 1h |
|---|---:|---:|
| Período | maio–julho 2026 | 2020–2024 |
| Janelas completas | **87** | **31** |
| Jaccard médio HDR GMM entre metades | **0,7344** | **0,7925** |
| Jaccard médio HDR normal entre metades | 0,7962 | 0,8372 |
| Jaccard médio GMM versus normal na primeira metade | 0,8083 | 0,7972 |
| Jaccard médio GMM versus normal na segunda metade | 0,7968 | 0,8144 |
| HDR GMM conexa em ambas as metades | 100% | 100% |
| HDR GMM desconexa em ambas | 0% | 0% |
| Fração GMM com maior estabilidade Jaccard que normal | 4,6% | 25,8% |

**Interpretação:** as superfícies densitárias flexíveis permitem medir deformações, mas neste recorte são, em média, **menos estáveis** entre duas subamostras sucessivas do que a gaussiana. Suas HDR de 50% permaneceram todas conexas na grade usada. Isso não contradiz os ganhos anteriores de log-score não gaussiano: melhor densidade fora da amostra e maior estabilidade da região de maior densidade são propriedades diferentes.

A menor estabilidade da GMM em comparação com a normal também foi encontrada no SF1 sintético, mostrando que **não podemos usar apenas esse fenômeno como evidência exclusiva da geometria do BTC**.

## Respostas e limites

- **A forma é reconstruível?** Sim, no sentido operacional de reconstruir regiões de densidade bidimensionais das coordenadas observadas, após transformações estabelecidas apenas no passado.
- **Encontramos duas regiões separadas?** Não no nível de 50% de massa sobre a grade fixada. Outros níveis, resoluções e modelos podem produzir resultados diferentes.
- **Forma exata e invariável?** Não demonstrado. A morfologia é condicional à janela, mapa de postos, modelo de densidade, nível HDR, grade e regime.
- **Separação do ruído estatístico?** Ainda incompleta: esta execução não estima intervalos de confiança das formas por bootstrap interno de cada janela.
- **Independência do SF1?** Não demonstrado. O SF1 default só serve como referência ilustrativa neste teste, não como nulo ajustado rigorosamente a cada amostra.
- **Fluxo causal de informação?** Não inferido pela simultaneidade de preço e agressão.
- **Topologia intrínseca Fisher–Rao?** Não testada; HDR topológica é outro objeto matemático.

## Próximo experimento prioritário

1. Construir regiões HDR em diferentes massas (25%, 50%, 75%) e várias resoluções.
2. Bootstraps em blocos **dentro** de cada subjanela para medir a precisão das superfícies e descartar deformações abaixo do ruído.
3. Confrontar o resultado real com simulações SF1 parametrizadas em janelas reais, preservando padrões intradiários, clusters de volatilidade e resíduos.
4. Estender de (z,iota) para a distribuição tridimensional (z,iota,nu), preferencialmente com superfícies e projeções condicionadas à atividade; exigir testes de estabilidade antes de atribuir nomes geométricos a formas.
5. Diferenciar morfologia da distribuição em um intervalo da trajetória temporal entre tais distribuições.

## Reprodutibilidade

- Código: `experiments/morfologia_superficies.py`
- Testes: `tests/test_morfologia_superficies.py`; **11 aprovados**.
- Workflow: `.github/workflows/morfologia-superficies.yml`.
- Execução GitHub Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37937730157.
- Artefatos JSON e CSV por janela nas três tarefas sintética/1m/1h.
