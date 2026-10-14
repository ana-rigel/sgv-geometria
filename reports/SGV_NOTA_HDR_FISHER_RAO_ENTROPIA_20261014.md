# SGV — Nota científica: coordenadas, superfícies HDR, Fisher–Rao e entropia

**Data:** 14/10/2026. **Natureza:** registro conceitual e auditoria documental de M8–M11 (com referência complementar a M15); **não é pré-registro nem resultado experimental novo**. Ramo isolado `research/nota-hdr-fisher-entropia-20261014`, originado do commit `fd5a051d3982281cd8f65a3b54ebb1ca7d048830` da integração M11-I/U03/RTT/M35. A `main`, ramos experimentais e datasets reservados não foram modificados.

## 1. Premissa matemática (fixada como diretriz de pesquisa)

Separar rigorosamente:

1. **Coordenadas observacionais/sintéticas** `x=(x1,x2,x3)`: definem o domínio no qual se localizam as observações.
   - Mercado, espaço fluxo: retorno normalizado, desequilíbrio de agressão, volume relativo.
   - Mercado, espaço original: `E_norm`, `jerk`, `memory_flux`; a definição computacional efetiva desta última depende da versão e deve ser auditada.
   - U03.1/U03.2: três coordenadas sintéticas de transformações; não representam diretamente as variáveis financeiras.
   - Probabilistic v3.3: coordenadas espaciais das misturas gaussianas analíticas, sem semântica financeira automática.
2. **Distribuição/densidade** `p(x)`: objeto estatístico estimado/modelado naquele domínio. As cascas `HDR_alpha(p) = {x : p(x) >= tau_alpha}` satisfazem idealmente `integral_HDR_alpha p(x) dx = alpha`; resultados numéricos são aproximados. A geometria 3D dessas cascas é **extrínseca** ao domínio escolhido.
3. **Fisher–Rao**: tensor de informação `g_ij(theta) = E_{p_theta}[partial_i log p_theta * partial_j log p_theta]` numa família paramétrica regular; não é eixo no navegador. Distância de Fisher–Rao depende da família e da convenção métrica. Para misturas gaussianas, não tratar a fórmula da covariância de gaussianas simples como distância exata entre GMMs.
4. **Entropia diferencial**: `H(p) = -integral p(x) log p(x) dx`; não é coordenada. Depende de sistema de coordenadas e da medida de referência; não é, isoladamente, distância A–B nem descrição completa da forma.

**Interpretação:** diferenças HDR, Fisher–Rao, entropia e momentos são descritores diferentes de um mesmo par de distribuições. Uma casca é uma função de `p`, portanto **não agrega informação matemática não contida na distribuição completa conhecida**. A hipótese testável é ganho *operacional/estatístico* de detecção, diagnóstico ou generalização sobre um conjunto explícito e limitado de medidas comparadoras; não criação de nova informação além de `p`.

## 2. Auditoria dos experimentos M8–M11 (ramos originais)

- **M8** `research/m8-transformacoes-forma-3d`: HDR50 GMM2 em espaço fluxo gaussianizado; observa deslocamento, log de razão de volumes, ângulo de eixos e distância Chamfer residual após registro. Sete testes, experimentos BTC exploratórios 1m/1h com seis origens por escala. Nenhum modelo SF1/M5/M6 domina todos os atributos; rotação apresentou ambiguidade por simetrias de autovetores. Não usa Fisher–Rao nem entropia como medidas de comparação.
- **M9** `research/m9-simetrias-registro-3d`: orientação no quociente `SO(3)/D2` com gate de autovalores; deformação com ICP/Kabsch e pontos independentes de holdout. Corrige ângulos espúrios específicos, mas distância Chamfer tem piso de amostragem. Sete testes. Não quantifica informação incremental sobre Fisher–Rao ou entropia.
- **M10** `research/m10-piso-amostragem-registro`: mede piso condicionado à malha, densidade de pontos e sementes; em controle sintético o piso de 180 para 720 pontos cai ~52%. BTC: distâncias acima do piso de pontos em 6/6 janelas em cada escala, sem rejeição do nulo de mesma distribuição geradora. Sete testes. Não usa Fisher–Rao ou entropia como concorrentes.
- **M11** `research/m11-distancia-superficie-nulos-temporais`: distância ponto–triângulo exata por ponto, integral global aproximada por quadratura, registro livre após retirar centro e escala. Distância self entre malhas idênticas ~4,84e-17; mudanças medianas de quadratura 256→512: 1,5704% (1m) e 2,1513% (1h). Nulo temporal pooled simplificado: 0/2 acima de q90 em 1m, 2/2 em 1h. São apenas duas auditorias por escala e o nulo pode não reproduzir memória/regimes. Seis testes. Não implementa Fisher–Rao ou entropia.
- Os quatro trabalhos foram documentados em 09/10/2026 e não leram dados confirmatórios reservados. A precisão da malha, o erro da estimação GMM e a adequação dos nulos são questões distintas.
- **Incompatibilidade experimental importante**: M8–M11 trabalham com HDR50 e gaussianização; a interface atual usa HDR50/HDR95, e análises posteriores de caudas usam coordenadas brutas. Não agregar resultados ou assumir equivalência entre versões.

**Fontes originais:**
- [M8](https://github.com/ana-rigel/sgv-geometria/blob/research/m8-transformacoes-forma-3d/reports/SGV_M8_RESULTADOS_20261009.md)
- [M9](https://github.com/ana-rigel/sgv-geometria/blob/research/m9-simetrias-registro-3d/reports/SGV_M9_RESULTADOS_20261009.md)
- [M10](https://github.com/ana-rigel/sgv-geometria/blob/research/m10-piso-amostragem-registro/reports/SGV_M10_RESULTADOS_20261009.md)
- [M11](https://github.com/ana-rigel/sgv-geometria/blob/research/m11-distancia-superficie-nulos-temporais/reports/SGV_M11_RESULTADOS_20261009.md)

## 3. Evidência posterior e diretamente pertinente: M15

O experimento **M15**, em **dados exclusivamente sintéticos**, comparou em metades gaussianizadas:
- `m11`: distância entre cascas HDR50 registradas;
- `fr_cov`: distância Fisher–Rao **entre gaussianas N(0, Sigma_A) e N(0, Sigma_B)**, `sqrt(0.5 * sum(log(eigenvalues(Sigma_A^-1 Sigma_B))^2))`; **não** entre misturas gaussianas completas;
- `energy`: energy distance amostral multivariada.

Conforme a tabela do M15, taxas de alarme nominal 5% (posto 1/20):
- HMM verdadeiro vs nulo VAR inadequado: `m11 60,2%`, `fr_cov 19,0%`, `energy 45,2%`.
- HMM verdadeiro vs nulo GMM_IID inadequado: `m11 37,2%`, `fr_cov 23,6%`, `energy 67,8%`.
- HMM verdadeiro vs HMM adequado: `m11 6,9%`, `fr_cov 6,2%`, `energy 7,2%`.
- VAR verdadeiro vs VAR adequado: `m11 6,2%`, `fr_cov 3,0%`, `energy 4,4%`.

**Interpretação estrita:** a medição geométrica foi mais sensível a certos erros de forma (neste gerador e com essa regra de alarme), enquanto a energy distance foi mais sensível a certos erros de persistência. A condição de calibração pré-registrada do Q4 (Fisher–Rao covariâncias) falhou no cenário VAR correto: diferença de 3,2 p.p. excedeu o limite de 2 p.p.; assim a vantagem nominal do M11 sobre `fr_cov` foi formalmente rotulada **possivelmente afetada por calibração diferente**. No Q5 frente à energy distance, a diferença de calibração permaneceu dentro do gate. Não equivale a comprovação de ganho geral, de independência informacional, de previsão ou a resultados sobre BTC.

**Entropia não foi testada como comparador** no M15, e tampouco em M8–M11.

Fontes:
- [Pré-registro M15](https://github.com/ana-rigel/sgv-geometria/blob/research/m15-forma-persistencia-comparadores/reports/PROTOCOLO_SGV_M15_20261009.md)
- [Resultados M15](https://github.com/ana-rigel/sgv-geometria/blob/research/m15-forma-persistencia-comparadores/reports/m15/SGV_M15_RESULTADOS.md)
- [Leitura M15](https://github.com/ana-rigel/sgv-geometria/blob/research/m15-forma-persistencia-comparadores/reports/SGV_M15_LEITURA_20261009.md)

## 4. Distinção entre implementações de Fisher–Rao já existentes no SGV

O ramo `research/fotografia-informacional` possui `experiments/fotografia_informacional.py`: métrica Fisher **gaussiana local de localização**, `Sigma^-1`, mais distância de Bhattacharyya entre janelas aproximadas por gaussianas. O ramo `experiment/fisher-rao-trajectory` experimentou curvatura de trajetória gaussiana para previsão de magnitude. Na auditoria 1m, a inclusão de `k` após HAR e GARCH não acrescentou ganho robusto de MSE; a formulação dessa trajetória não é uma medida exata de geodésica entre GMMs usadas pelas cascas. Estes são instrumentos distintos do navegador 3D e não contradizem a premissa de que seus eixos não são Fisher–Rao.

## 5. Questão aberta e requisitos de um teste posterior

**Questão proposta:** 'Dado o mesmo par de distribuições A e B, a métrica de mudança de forma HDR50/HDR95 melhora a identificação de transformações relevantes quando já conhecemos a distância Fisher–Rao escolhida, a variação de entropia, os momentos/covariâncias, quantis e um comparador multivariado forte como energy distance?'

Condições **antes de executar**, em protocolo novo separado dos M8–M11:

1. Definir uma tarefa/endpoint mensurável: detecção de transformação plantada, identificação de tipo, ou desempenho prospectivo; não misturar essas alegações.
2. Definir formalmente a distância informacional: `fr_cov` do M15 é **restrita às covariâncias gaussianas**; se adotar uma distância entre densidades gerais, explicitar se é Fisher–Rao na variedade ambiente via embedding raiz-quadrada, afinidade de Hellinger ou aproximação numérica sobre uma família de GMMs. Não tratá-las como equivalentes por conveniência.
3. Usar o **mesmo par A/B**, a mesma régua, a mesma amostra observada, a mesma informação disponível no prefixo e procedimentos de incerteza para todas as estatísticas; auditar normalização, cobertura do domínio, discretização da grade e problemas de rótulos/permutação de componentes.
4. Entropia diferencial por integração numérica/Monte Carlo com erro aferido; sob mudança de variáveis comuns, documentar Jacobiano. Variação `Delta H = H(B)-H(A)` não detecta por si só uma translação pura nem toda mudança de formato.
5. Manter controles sintéticos de translação, escala, rotação, anisotropia, caudas, multimodalidade e mudanças de dependência; incluir exemplos com média/covariância/entropia semelhantes mas formato distinto, e casos nos quais o HDR fica cego.
6. Testar ganho incremental por modelo de base `momentos + quantis + entropia + d_FR + energy` comparado com `base + medidas_HDR`, com divisão de amostras, calibração de falsos alarmes e controle de multiplicidade. Ganho operacional não deve ser traduzido em 'nova informação física'.
7. Caso evolua ao mercado, respeitar livro de dados do programa integrado: BTC 1m maio–julho/2026 explorado; BTC agosto–setembro/2026 e ETH/SOL/BNB em seus intervalos já consumidos; BTC outubro–dezembro/2026 reservado ao H-FR/M22. Não abrir períodos protegidos nem otimizar sobre holdouts.
8. Registrar a regra de fracasso antes do experimento. Se o ganho condicional não sobreviver aos comparadores e nulos fortes, declarar redundância para aquele endpoint.

## 6. Veredito documental em 14/10/2026

**Sim:** M8–M11 comprovam desenvolvimento, calibração parcial e distinção conceitual de medidas de superfície. **Não:** esses experimentos, isoladamente, não testaram Fisher–Rao contra HDR nem incluíram entropia. **Parcialmente:** M15 fornece uma comparação formal entre HDR50, Fisher–Rao de covariâncias gaussianas e energy distance em cenários sintéticos, com complementaridade e ressalva expressa de calibração; nenhuma validação de entropia ou informação incremental geral foi produzida.

**Status:** registro documental. Sem nova execução, novos resultados, alteração de código, acesso a dados de mercado ou modificação de gabaritos.
