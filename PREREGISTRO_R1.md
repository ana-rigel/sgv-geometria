# Pré-registro R1 — geometria do fluxo de ordens

**Estado:** congelado no commit que contém este arquivo, antes de qualquer cálculo das coordenadas de fluxo em dado real. A única inspeção feita nos dados reais de fluxo foi de formato: as 3 últimas linhas de julho/2026 em 1m, para conferir as colunas. · **Autoria:** Ana Rigel (decisão de reformular, 08/10/2026), com Claude · **Regra do plano:** esta é a **única** reformulação permitida depois da reprovação do G1 (`reports/FASE1_PORTAO_G1.md`). Se R1 reprovar, a linha geométrica se encerra.

## Hipótese

A geometria da distribuição conjunta de estados do mercado tem conteúdo próprio quando o estado é descrito pela **relação entre o movimento do preço e o fluxo de ordens que o produz**. "Conteúdo próprio" quer dizer: além dos fatos estilizados conhecidos, que são volatilidade agrupada, impacto linear, persistência do fluxo e a relação volume–volatilidade.

## Coordenadas (`sgvgeo/flow.py`)

| Coordenada | Definição | O que representa |
| --- | --- | --- |
| z | r_t / σ_t, com σ das 60 barras anteriores | movimento do preço em unidades da volatilidade recente |
| ι | 2·taker_buy/volume − 1 | desequilíbrio do fluxo agressor (−1 = só vendas a mercado) |
| ν | log volume_t − mediana do log volume nas 1.500 barras anteriores | atividade relativa |

As três são gaussianizadas por postos, de forma causal (janela de 1.500 barras). A métrica, a grandeza e o resto do pipeline são os da Fase 1: Fisher local F, ΔF = slog R(F) − slog R(Fref), KDE ajustado só no passado (janela de 1.500, reajuste a cada 60).

## Nulo SF1 (fatos estilizados)

O modelo é ajustado ao próprio segmento de dados:

- retornos GARCH(1,1)-t;
- ι* = a0 + a1·z + a2·ι*₋₁ + e1, com ι = tanh(ι*);
- log volume = b0 + b1·log volume₋₁ + b2·|z| + b3·z + e2;
- os pares de resíduos (e1, e2) são sorteados juntos.

As séries geradas passam pelo mesmo pipeline das coordenadas reais.

## Portão G1′ — os quatro critérios precisam passar

| Critério | Regra | Diagnóstico |
| --- | --- | --- |
| 1. Mensurável | Confiabilidade de ΔF entre metades da janela ≥ 0,8. A largura é o menor múltiplo de Scott em {2, 3, 4} que atinge isso. | D7: 240 barras sorteadas no período de exploração inteiro |
| 2′. Além da posição | Média de ΔF **pareado por posição** difere do nulo com p ≤ 0,05. Pareado por posição: ΔF menos o ΔF que o nulo tem no mesmo raio de Mahalanobis, em decis. | D8 |
| 3. Existe | Média de ΔF difere da de 39 réplicas SF1 ajustadas ao segmento, com p ≤ 0,05 (bilateral, por postos) | D8: últimas 4.500 barras |
| 4. Além da volatilidade | R² de ΔF explicado por volatilidade (10/30/60 barras, \|v\|, \|a\|) ≤ 0,5, fora da amostra | D4/D5: últimas 6.000 barras |

**Revisão do critério 2, feita na calibração e antes de qualquer dado real.** O critério original era \|ρ(ΔF, raio)\| < 0,5. Ele reprovou também a série alternativa, que tem estrutura real por construção (ρ = −0,79). Com estas coordenadas, ΔF sempre anda com o raio, então o critério não tinha poder. A versão 2′ pergunta o que importa: se a diferença em relação ao nulo sobrevive quando se compara na mesma posição. O ρ original continua no relatório.

**Escalas e dados:** 1m e 1h, nos períodos de exploração travados em 08/10/2026 (1m: 01/05–31/07/2026; 1h: 2020–2024). O G1′ é julgado separadamente em cada escala. Passar em uma delas basta para seguir à Fase 2 naquela escala.

**Estatísticas secundárias** (reportadas, sem valor de decisão): mediana de ΔF, log det F, taxa de troca de assinatura de H, autocorrelação de φ.

## Calibração (sintéticos, antes do dado real)

Para cada caso, a série tem 20.000 barras de 1m geradas por SF1 com parâmetros plausíveis, e o D8 usa 39 réplicas.

| Série | Largura escolhida | Crit. 1 | Crit. 2′ (p) | Crit. 3 (p) | Crit. 4 (R²) | G1′ |
| --- | --- | --- | --- | --- | --- | --- |
| Nulo verdadeiro (SF1 puro) | 3× (0,92) | ✓ | 0,425 ✗ | 0,40 ✗ | 0,49 ✓ | **reprova** (correto) |
| Alternativa: impacto depende da atividade, força 0,8 | 3× (0,88) | ✓ | 0,025 ✓ | 0,025 ✓ (z = −12) | 0,48 ✓ | **aprova** (correto) |
| Alternativa fraca, força 0,3 | _preenchido antes do congelamento_ | | | | | |

O critério 4 fica no limite nas duas séries sintéticas (R² ≈ 0,49). Ele quase não discrimina, e a decisão recai sobre os critérios 2′ e 3. Ficou mantido como no plano.

## Consequências

- **G1′ aprova em alguma escala:** escrever o pré-registro preditivo da Fase 2 naquela escala (alvo: amplitude futura residualizada; direção como secundário), julgado só no período reservado ao confirmatório.
- **G1′ reprova nas duas:** a linha geométrica do SGV se encerra. A conclusão registrada será que nem as coordenadas de preço nem as de fluxo mostram geometria além dos fatos estilizados.

## Aposta (antes dos dados, como é tradição da casa)

Claude: **~15%** de G1′ aprovar em pelo menos uma escala. O raciocínio:

- A calibração mostra poder alto contra uma interação forte, e microestrutura com impacto dependente da atividade é plausível no BTC. Isso puxa a aposta para cima.
- Os efeitos reais tendem a ser muito menores que a alternativa sintética de força 0,8. A janela de 4.500 barras limita o poder. E o histórico do projeto é de zero sobreviventes prospectivos. Isso puxa para baixo.
