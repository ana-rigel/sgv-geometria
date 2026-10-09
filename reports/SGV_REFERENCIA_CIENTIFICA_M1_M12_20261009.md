# SGV — Documento de Referência Científica e Estado Reproduzível (M1–M12)

**Congelamento do estado do conhecimento:** 09/10/2026, antes do SGV-M13.  
**Repositório:** \`ana-rigel/sgv-geometria\`. **Base deste registro:** \`research/m12-nulos-regimes-temporais\` (\`6e54ff2ea1e615f132016830f9bbf0cf08c8156d\`).  
**Ramo de continuidade:** \`research/m13-calibracao-alarmes-regimes\`. **Política:** nenhum commit na \`main\`; não abrir dados confirmatórios reservados.

## 1. Pergunta e objeto observacional

O SGV pretende registrar, **ao fechamento de cada candle**, a geometria tridimensional da distribuição de variáveis observadas em fluxos do mercado BTC, acompanhando mudanças de forma sem pressupor causalidade, trading alpha, nova lei física ou estresse econômico. Coordenadas disponíveis ao fechamento de cada candle:

- \`z_t = r_t / sigma_t\`, com \`sigma\` calculado dos **60 retornos anteriores**;
- \`iota_t = 2*taker_buy_t/volume_t-1\`, desequilíbrio relativo de agressão contemporâneo;
- \`nu_t = log(volume_t)-mediana(log(volume))\` dos **1500 candles anteriores** (min 300).

As margens são gaussianizadas com mapa fixado no primeiro 30% da janela para comparar as duas fotografias posteriores de 35%+35%. Essa fotografia vive em um **espaço de coordenadas padronizadas**, não em uma variedade Fisher–Rao intrínseca.

Não substituir o objetivo do SGV por prever preço. Distorção de uma isosuperfície não é, por definição, tensão do mercado.

## 2. Regras de integridade

1. Dados **exclusivamente exploratórios**: BTCUSDT spot 1m **maio–julho/2026** e 1h **janeiro/2020–dezembro/2024**. Não ler BTC 1m desde agosto/2026 nem 1h desde janeiro/2025 (reservados confirmatórios). Checksum SHA-256 e allowlist estrita.
2. Nenhum ajuste usa preços/fluxos/volumes posteriores ao instante de decisão. O prefixo de histórico e a âncora são tratados separadamente. Os dados futuros nas comparações históricas são conhecidos **somente para avaliação posterior**, nunca para calibrar os simuladores.
3. Trabalhar em \`research/*\`; não mexer na \`main\`.
4. Malhas inválidas, truncadas, abertas ou cobertura insuficiente são registradas como **inválidas**, sem imputação. Ângulo não identificável = \`null\`, nunca zero.
5. Definir controles, métricas, seleção de janelas e critérios **antes** dos resultados. Não converter envelope descritivo de poucas simulações em p-value/nível de teste.
6. Diferenciar erro numérico da grade, erro de quadratura/registro, incerteza de ajuste de densidade, dependência temporal e inadequação do nulo.

## 3. Medidas morfológicas vigentes

- Superfícies HDR25/50/75: ajuste gaussianas simples e GMM2, com malhas Marching Cubes condicionadas à cobertura de massa adequada.
- **Não convexidade local:**
  \`D_alpha = (1/A) * integral_{S_alpha} max(0,-K(x)) * r² dA\`,
  \`r=(3V/(4*pi))^(1/3)\`, \`K=k1*k2\`. As curvaturas principais vêm da **Hessiana analítica da densidade projetada no plano tangente da casca**, NÃO dos três autovalores brutos da Hessiana.
- **Déficit global de convexidade:** \`C_alpha=1-V(S_alpha)/V(convex_hull(S_alpha))\`.
- **Movimentos entre fotografias:** deslocamento de centros volumétricos, \`log(Vb/Va)\`, distância angular de eixos identificáveis no quociente \`SO(3)/D2\` e deformação geométrica residual após registro rígido/escala. Não representam necessariamente movimento de partículas, direção econômica ou massa transportada.
- **Instrumento de referência M11:** distância simétrica direta da quadratura determinística em uma malha à superfície triangular oposta, após centro/escala/ICP multistart. Com malha idêntica, ~zero. Quadratura global ainda aproximada, e ICP ainda pode errar/alcançar mínimos locais.

## 4. Resultados e decisões M1–M12 (resumo rastreável)

| Etapa | Ganho instrumental / resultado decisivo | Decisão científica |
|---|---|---|
| M1 | HDRs 3D, 72/72 superfícies válidas 1m e 71/72 1h. GMM2 HDR50 mostrou área \`K<0\` mediana ~16,7% 1m e ~21,4% 1h; gaussiana ~0%. Cascas válidas componentes=1, gênero=0 | Curvatura extrínseca da densidade ajustada, não prova de dois lóbulos ou tensão |
| M2 | Quantificou \`D\`, \`C\` e discrepância condicional preço-fluxo independente. Associação Spearman pequena e com sinais opostos (+0,091 1m; -0,176 1h, dez janelas/escala) | Não promover D a oscilador de tensão |
| M3 | Grades 25³/35³/49³ e bootstrap em blocos; diferença numérica de D pequena na amostra auditada; incerteza de variação temporal bem maior | Não declarar sinal de ΔD robusto sem calibração |
| M4 | Memória de volume reduziu substancialmente erro ACF(nu,10) 1m, mas piorou lag1; não melhorou lag10 em 1h | Ajuste dependente de escala; sazonalidade 1h inicialmente indisponível |
| M5 | Memória + harmônico diário venceu critério de fidelidade conjunta exploratório em 1m e 1h; reduziu perda ~53,2% e ~48,7% contra SF1 original | Melhor candidato para atividade, não nulo universal da geometria |
| M6 | Inovações condicionais volume-fluxo recuperaram acoplamento sintético plantado; M5 independente ainda venceu na perda conjunta, M6 ajudou aspectos de ΔD em piloto pequeno | Manter M5 e M6 como nulos concorrentes |
| M7 | Ampliou janelas de dinâmica HDR50; vantagem ΔD do M6 não se reproduziu uniformemente; rankings diferiram entre D, ΔD e C | Não promover M6 globalmente |
| M8 | Separou deslocamento, expansão, rotação e deformação residual da casca; rotação exibiu ambiguidade por simetria/autovetores | Exigir identificabilidade e registro adequado |
| M9 | Ângulo-quociente \`SO(3)/D2\`; ICP multistart e Chamfer em holdout separaram orientação de deformação; introduziram piso de amostragem positiva | Não interpretar Chamfer pequeno como deformação exata |
| M10 | Quantificou piso entre nuvens amostradas; para n=360, piso local mediano ~0,104 (1m/1h), dependente do n; excesso ainda incerto | Medir distância à superfície, não corrigir por constante universal |
| M11 | Distância direta ponto→triângulo: mesma superfície ~4,84e-17; medianas 256→512 variaram 1,57% (1m), 2,15% (1h). Nulo pooled simples: acima q90 em 0/2 janelas 1m e 2/2 1h | Piso de pontos independentes resolvido; nulo temporal inadequado |
| M12 | Quatro nulos N0/N1/N2/N3 com memória, relógio e regimes; contagens acima q90 dependem intensamente da família e escala | **Não há rejeição confirmatória de nenhum nulo**. Investigar adequação e taxas de falso alarme antes de qualquer diagnóstico econômico |

### Nulos M12
- **N0:** blocos estacionários curtos, preservam tuplas contemporâneas e memória local.
- **N1:** GARCH-t + SF1-M5 (memória de volume e harmônico diário).
- **N2:** blocos trivariados condicionados por estado binário e faixa de 6h, comprimento curto.
- **N3:** mesmo catálogo condicional, blocos longos.
- O catálogo de regimes é **heurístico**; preservação do relógio por seleção de blocos não equivale a ajuste correto da sazonalidade ou dos tempos de permanência.
- Blocos curtos/longos: 1m \`15/60\` candles, 1h \`12/36\` candles.

### Alertas M12: contagem observada > q90 de SEIS simulações por origem

| Nulo | BTC 1m (4 origens) | BTC 1h (4 origens) |
|---|---:|---:|
| N0 | 1/4 | 3/4 |
| N1 | 3/4 | 2/4 |
| N2 | 2/4 | 2/4 |
| N3 | 2/4 | 1/4 |

**Não são p-values, significância nem taxa de falsos positivos.** A variação entre 1/4 e 3/4 sublinha a importância de validar nulos e a estabilidade de sua distribuição de referência.

## 5. Estado de maturidade e lacunas prioritárias

**Implementado:** imagens tridimensionais observacionais a partir de dados fechados, medidas extrínsecas de não convexidade, movimento/registro em simetrias, distância superfície–superfície sem piso artificial de amostras independentes, múltiplos controles temporais, GitHub Actions com relatórios de execução e validação de arquivos históricos.

**Em aberto:** geradores que reproduzam simultaneamente autocorrelação longa, caudas conjuntas, duração dos regimes, sazonalidade e heterocedasticidade; calibração de cobertura/taxa de falso alarme sob nulos conhecidos e geometria reestimada; estabilidade fora da amostra exploratória; streaming real prolongado; comparação confirmatória após congelamento da especificação.

**Não demonstrado:** nova lei geométrica do mercado, curvatura intrínseca Fisher–Rao, causalidade informacional, força/tensão física, estresse financeiro, previsão de retornos, ganho de trading ou testes confirmatórios com controle tipo I.

## 6. M13 — Próxima etapa congelada

**M13: Calibração de Taxas de Falso Alarme e Adequação de Nulos Temporais.** 
- Primeira prioridade: verificar que uma origem e seu modelo de geração correspondem a uma unidade válida de ensaio. Desenhar um experimento de **auto-calibração sintética** em que um modelo é a verdade geradora e o mesmo método geométrico reestima as HDRs e cria réplicas de referência usando somente histórico anterior.
- Usar **distribuição de postos leave-one-out / Monte Carlo** com amostras suficientes para estimar cobertura/taxa tipo I; não usar q90 de seis desenhos. Diferenciar calibração **condicional ao gerador conhecido** de avaliação com dados reais.
- Separar critérios de adequação temporal multivariada, caudas, duração de regimes e perfil horário das decisões de alarme geométrico; registrar o que foi medido e o que permaneceu sem resolução.
- Manter holdout BTC reservado fechado.

## 7. Índice reprodutível dos relatórios e execuções

As versões de M1–M12 estão preservadas nas suas **respectivas branches**, com protocolos, scripts, testes e workflows. Os links são registros de engenharia (uma execução aprovada não é, sozinha, validação científica universal).

| Etapa | Relatório | GitHub Actions |
|---|---|---|
| M1 | [Isosuperfícies](https://github.com/ana-rigel/sgv-geometria/blob/research/isosuperficies-morfometria/reports/SGV_RESULTADO_ISOSUPERFICIES_M1_20261009.md) | [M1](https://github.com/ana-rigel/sgv-geometria/actions/runs/37945591837) |
| M2 | [M2](https://github.com/ana-rigel/sgv-geometria/blob/research/m2-nao-convexidade-tensao/reports/SGV_M2_RESULTADOS_20261009.md) | [M2](https://github.com/ana-rigel/sgv-geometria/actions/runs/37947839176) |
| M3 | [M3](https://github.com/ana-rigel/sgv-geometria/blob/research/m3-precisao-nao-convexidade/reports/SGV_M3_RESULTADOS_20261009.md) | [M3](https://github.com/ana-rigel/sgv-geometria/actions/runs/37950906618) |
| M4 | [M4](https://github.com/ana-rigel/sgv-geometria/blob/research/m4-sf1-memoria-sazonalidade/reports/SGV_M4_RESULTADOS_20261009.md) | [M4](https://github.com/ana-rigel/sgv-geometria/actions/runs/37954782378) |
| M5 | [M5](https://github.com/ana-rigel/sgv-geometria/blob/research/m5-validacao-conjunta-sf1/reports/SGV_M5_RESULTADOS_20261009.md) | [M5](https://github.com/ana-rigel/sgv-geometria/actions/runs/37956362999) |
| M6 | [M6](https://github.com/ana-rigel/sgv-geometria/blob/research/m6-acoplamento-residual-hdr/reports/SGV_M6_RESULTADOS_20261009.md) | [M6](https://github.com/ana-rigel/sgv-geometria/actions/runs/37960253079) |
| M7 | [M7](https://github.com/ana-rigel/sgv-geometria/blob/research/m7-dinamica-hdr50-validacao/reports/SGV_M7_RESULTADOS_20261009.md) | [M7](https://github.com/ana-rigel/sgv-geometria/actions/runs/37963662906) |
| M8 | [M8](https://github.com/ana-rigel/sgv-geometria/blob/research/m8-transformacoes-forma-3d/reports/SGV_M8_RESULTADOS_20261009.md) | [M8](https://github.com/ana-rigel/sgv-geometria/actions/runs/37966070545) |
| M9 | [M9](https://github.com/ana-rigel/sgv-geometria/blob/research/m9-simetrias-registro-3d/reports/SGV_M9_RESULTADOS_20261009.md) | [M9](https://github.com/ana-rigel/sgv-geometria/actions/runs/37967131614) |
| M10 | [M10](https://github.com/ana-rigel/sgv-geometria/blob/research/m10-piso-amostragem-registro/reports/SGV_M10_RESULTADOS_20261009.md) | [M10](https://github.com/ana-rigel/sgv-geometria/actions/runs/37972700018) |
| M11 | [M11](https://github.com/ana-rigel/sgv-geometria/blob/research/m11-distancia-superficie-nulos-temporais/reports/SGV_M11_RESULTADOS_20261009.md) | [M11](https://github.com/ana-rigel/sgv-geometria/actions/runs/37976030631) |
| M12 | [M12](https://github.com/ana-rigel/sgv-geometria/blob/research/m12-nulos-regimes-temporais/reports/SGV_M12_RESULTADOS_20261009.md) | [M12](https://github.com/ana-rigel/sgv-geometria/actions/runs/37977210206) |

**Versão do documento:** \`SGV_REFERENCIA_CIENTIFICA_M1_M12_20261009.md\`. Se o M13 encontrar um problema de implementação em M12, registrar como correção de instrumento, não reinterpretar ou alterar silenciosamente resultados anteriores.
