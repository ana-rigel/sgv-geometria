# Leitura contra a previsão registrada (PREDICAO_fatias_volatilidade.md, commit 973c6d3)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38823416028).

O código e o workflow foram commitados antes das rodadas (`e9eee03`, `589f7f9`).

**Paridade:** o R de todos os minutos repete a geometria residual: 6,83 em jun–jul e 6,48 em ago–set. A rotação "todos" difere um pouco da rodada anterior, 15,8° contra 16,2° em jun–jul e contra 10,9° em ago–set. Aqui os mapas só precisam da HDR50 válida; lá precisavam também da HDR95, então entram mapas diferentes.

## Resultados

| | jun–jul real | jun–jul M (2) | ago–set real | ago–set M (2) |
|---|---|---|---|---|
| **1a** R_todos | 6,83 | 6,53–6,87 | 6,48 | 12,05–14,04 |
| **1a** R_fatias | 4,11 | 3,72–3,81 | 2,75 | 3,23–4,31 |
| **1a** razão | **0,60** (em parte) | 0,56–0,57 | **0,42** (explica) | 0,27–0,31 |
| **1b** rotação, todos | 15,8° | 7,3–11,0° | 15,8° | 17,9–55,4° |
| **1b** rotação, fatias (calma / média / quente) | 44° / 21° / 18° | 87–90° / 36–57° / 8–9° | 90° / 15° / 24° | 61–80° / 80–84° / 33–55° |
| **2** C (colapso) | **0,88** | 0,89–0,95 | **0,92** | 0,89 |

| Teste | jun–jul | ago–set | Pela regra |
|---|---|---|---|
| 1a | explica em parte | explica | **não estável** |
| 1b | não | não | **não** (estável) |
| 2 | colapsa | colapsa | **colapsa** (estável) |

**Apostas:**

| Aposta | Probabilidade | Resultado |
|---|---|---|
| 1a "explica" | 40 % | não estável |
| 1a "em parte" | 40 % | não estável |
| 1b "mais estáveis" | 40 % | **errou** |
| 2 "colapsa" | 35 % | **acertou** |

## Leitura

1. **Achado mais forte, que não estava no critério: a borda do cubo é a camada quente.**
   - Nos dois períodos, as fatias calma e média têm **zero** minutos com extremidade ≥ 3.
   - Todos os extremos (1.615 avaliados em ago–set) estão na fatia quente.
   - Geometricamente, a temperatura **é** a distância ao centro, nas bordas: o estado só chega à borda quando o mercado está quente.
2. **Colapso de escala (teste 2): a temperatura é um zoom do mesmo objeto.**
   - Medido em unidades de volatilidade, o campo de agitação das três fatias coincide.
   - A dispersão entre fatias cai de 1,74–1,80 (em log) para 0,14–0,21.
   - C = 0,88 e 0,92, igual ao sintético M, onde a volatilidade é por construção a única variável escondida (0,89–0,95).
   - É a assinatura geométrica de uma dimensão de escala.
3. **A borda agitada encolhe dentro da camada quente (1a), mas não some.**
   - R cai de ×6,5–6,8 para ×2,8–4,1.
   - Em jun–jul a redução é a mesma do sintético M (0,60 contra 0,56–0,57).
   - Em ago–set o real encolhe um pouco menos que o M (0,42 contra 0,27–0,31).
   - Mesmo dentro da camada quente, a borda continua mais agitada que o núcleo. Isso é compatível com a volatilidade **rápida** ainda variar dentro de um tercil.
4. **As cascas por fatia (1b) não ficaram mais estáveis, mas o teste não é informativo.**
   - O mesmo acontece no sintético M, onde a volatilidade é a 4ª dimensão.
   - A fatia calma é quase esférica: o eixo principal fica mal definido, e a rotação vai a ~90° por ruído.
   - Fatiar também reduz os pontos por casca.
   - Erro de desenho meu: a rotação do eixo principal não serve para cascas quase isotrópicas.

## Para o programa

A volatilidade aparece na geometria como uma **4ª dimensão de escala**:
- ela define quem pode chegar à borda, porque só os momentos quentes chegam lá;
- medido nas unidades dela, o campo das diferentes temperaturas é o mesmo.

O "cubo" do SGV é, na prática, um cubo cujo tamanho pulsa com a temperatura do mercado.
