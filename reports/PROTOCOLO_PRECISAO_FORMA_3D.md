# SGV — Protocolo de precisão das formas 3D

**Data:** 09/10/2026. **Ramo:** `research/precisao-forma-3d`. **Tipo:** pesquisa observacional exploratória; não é previsão, não identifica lei geométrica do mercado.

## 1. Objeto

Construir regiões de alta densidade (HDR) da distribuição aproximada de `X=(z,iota,nu)`: retorno padronizado por volatilidade *anterior*, desequilíbrio contemporâneo do fluxo agressor e log-volume relativo à história *anterior*.

A aproximação com duas gaussianas é comparada com uma normal única. Regiões HDR da **densidade estimada no espaço das observações** não são a topologia ou curvatura intrínseca do manifold de distribuições Fisher–Rao.

## 2. Procedimento matemático

- Janela fechada: 1500 candles de 1m ou 1008 candles de 1h.
- Primeiros 30%: CDFs empíricas por marginal, fixadas antes das duas metades posteriores; usar o mesmo mapa em ambas impede comparar formas em sistemas de coordenadas incompatíveis.
- 70% posteriores: duas metades cronológicas não sobrepostas, cada uma ajustando uma normal 3D e uma GMM2. Nunca atualizar o mapa da âncora com informações das metades futuras.
- Grade cúbica de 21×21×21 pontos no domínio [-3,3]^3 (scores gaussianizados), segunda resolução 27×27×27 nas janelas de auditoria. HDRs da massa **dentro da grade**: 25%, 50%, 75%.
- Contar componentes conexas da região com 26 vizinhos e medir Jaccard (interseção/união) da HDR estimada em A e B. O número de componentes de uma GMM2 não equivale a número de regiões conexas da HDR.
- Registrar `sum(densidade)*delta³` para monitorar a massa capturada pelo cubo, pois truncamento pode afetar as formas (integração numérica aproximada).

## 3. Quantificação de erro

Em 8 janelas pré-selecionadas em cada escala, reamostrar em blocos dentro de cada metade e medir quanto cada HDR reconstruída difere de sua referência original. Adicionalmente, combinar A|B e reamostrar blocos para um nulo **aproximado** de igualdade de lei entre metades. 29 replicações por janela; p nominal limitado à resolução 1/30. Comparações simultâneas NÃO são corrigidas para multiplicidade.

Esse bootstrap pode falhar sob mudanças de regime e autocorrelação mais longa que os blocos; sua finalidade é diagnóstico inicial de precisão, não inferência confirmatória.

## 4. Controle

Calibração com gaussiana estacionária, mudança de correlação entre metades, dependência não gaussiana persistente, dependência curvada, mistura com separação principalmente em atividade (terceira dimensão) e o gerador SF1 **default**, não ajustado à amostra BTC deste teste. O SF1 default não é uma hipótese nula calibrada rigorosamente aos dados reais.

## 5. Proteções e limitações

Somente BTCUSDT spot de maio a julho de 2026 (1m) e janeiro de 2020 a dezembro de 2024 (1h), arquivos mensais validados em allowlist e baixados com conferência de checksum. Nenhum período confirmatório reservado é aberto.

Sem livro de ofertas, cancelamentos ou notícias, não podemos afirmar que a superfície descreva a totalidade da informação do mercado. A forma depende da janela, da estimação das marginais, do tamanho da amostra, do tipo de densidade, do nível HDR e da grade.

Se alguma escala não puder executar, registrar explicitamente o erro sem converter resultados sintéticos em observação de BTC.

## Reprodutibilidade

- `experiments/precisao_formas_3d.py`
- `tests/test_precisao_formas_3d.py`
- `.github/workflows/precisao-forma-3d.yml`
- GitHub Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37939421169

**Situação do protocolo:** hipóteses, parâmetros, testes e limites definidos no código antes da leitura dos agregados da execução real.
