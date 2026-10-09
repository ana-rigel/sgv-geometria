# SGV-M7 — Reprodução da dinâmica geométrica HDR50: relatório de execução

**Data:** 2026-10-09. **Ramo:** `research/m7-dinamica-hdr50-validacao`.  
**Execução GitHub Actions:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37963662906  
**Estado:** calibração, BTC 1m e BTC 1h concluídos com sucesso; **7 testes automatizados aprovados**. `main` não foi modificada; períodos confirmatórios reservados não foram lidos.

## Problema investigado

No M6, quatro janelas exploratórias (duas por escala) sugeriram erro menor de `ΔD` com o simulador M6 acoplado em comparação com M5 independente. M7 ampliou a observação para testar se o efeito persiste e diferenciar: (1) intensidade absoluta da não convexidade `D_b`, (2) mudança de não convexidade `ΔD=D_b-D_a`, (3) déficit de convexidade volumétrico `C_b=1-V/V(hull)`. O objeto é uma casca extrínseca da densidade de `(z,iota,nu)`; **não** é curvatura intrínseca de Fisher–Rao, tensão de mercado nem evidência causal.

## Método

- Apenas BTCUSDT spot exploratório, arquivos allowlist + SHA-256, janelas temporais contínuas e disjuntas; prefixo histórico 5000 (1m) ou 2000 (1h), janela posterior 1500 (1m) ou 1008 (1h).
- Seis origens por escala, selecionadas uniformemente por índice de janela elegível, sem inspeção prévia das formas. Quatro simulações com sementes pareadas de cada modelo por origem; 1700 barras de burn-in sintético.
- SF1 original, M5 (memória + sazonalidade, resíduos de volume independentes) e M6 (mesma memória+sazonalidade e inovação residual de volume condicionada às inovações do fluxo).
- Mesmos caminhos sintéticos de preço e `iota` por origem e réplica nas três alternativas; coeficientes estimados **somente no prefixo**; comparação com janela observada posterior.
- HDR50 de GMM2 em grade 35³, transformação de postos aprendida apenas nos primeiros 30% de cada janela de fotografia, fixa para 35% e 35% finais; curvaturas por gradiente e Hessiana tangencial analíticos. Somente malhas fechadas, não truncadas e com cobertura numérica suficiente.
- Qualidade geométrica em todas as fotografias aceitas; duas origens por escala com checagem de 49³ e bootstrap circular em blocos (12 reamostragens, blocos 1m L=15 e 1h L=12). Quantis de bootstrap indicam variação dos ajustes, não intervalos de confiança calibrados.

## Métricas e cobertura

- 1m: 6 origens selecionadas, **6 válidas**, nenhuma descartada.
- 1h: 6 origens selecionadas, **6 válidas**, nenhuma descartada.
- Todas as origens tiveram comparações pareadas válidas para os três modelos; cada uma incluiu quatro réplicas por modelo, mas essas réplicas **não são independentes do regime real**.
- Calibração sintética e sete testes automatizados aprovados antes da avaliação real.

## Resultados 1 minuto

| Erro absoluto mediano | SF1 | M5 independente | M6 acoplado |
|---|---:|---:|---:|
| **ΔD**, variação temporal | 0,027181 | **0,024125** | 0,035087 |
| **D_b**, intensidade absoluta | 0,108137 | 0,088086 | **0,068865** |
| **C_b**, déficit convexo | 0,080163 | 0,067782 | **0,065309** |

A vantagem de `M6` para mudança `ΔD` do piloto M6 **não se reproduziu** em 1m: apenas **2/6** origens com erro ΔD inferior ao M5, e também 2/6 inferiores ao SF1. Em contraste, `M6` superou M5 em **6/6** para nível absoluto `D_b` e em **5/6** para déficit `C_b`. O erro absoluto mediano na reprodução da mudança foi maior para M6 que nos dois concorrentes.

### Precisão 1m
- Primeira janela auditada: diferença `abs(D_b(35³)-D_b(49³))=0,000262`, diferença de `ΔD`=0,000383.
- Última janela auditada: diferença absoluta do nível D=0,001985 e de ΔD=0,002129.
- Bootstrap de ΔD (p10/p50/p90), 12 replicações em cada uma:
  - primeira: `[-0,11564; -0,05776; +0,03884]`;
  - última: `[-0,12793; -0,00583; +0,05014]`.
- Ambos intervalos de quantis atravessam zero; não sustentam afirmação firme sobre sinal da mudança.

## Resultados 1 hora

| Erro absoluto mediano | SF1 | M5 independente | M6 acoplado |
|---|---:|---:|---:|
| **ΔD**, variação temporal | **0,027873** | 0,052213 | 0,033979 |
| **D_b**, intensidade absoluta | 0,104697 | **0,073323** | 0,095287 |
| **C_b**, déficit convexo | 0,078599 | **0,063815** | 0,064830 |

Em 1h, M6 supera M5 no erro ΔD em **4/6** origens; porém SF1 original apresentou menor erro mediano absoluto de ΔD. Para forma absoluta `D_b`, M6 foi superior ao M5 somente em **1/6** origens; para `C_b`, **2/6**.

Portanto, nem a hipótese de maior fidelidade dinâmica pelo acoplamento nem a de forma absoluta superior é universal entre escalas. Os rankings diferem entre escala e atributo geométrico.

### Precisão 1h
- Primeira janela auditada: diferença `abs(D_b(35³)-D_b(49³))=0,000232`, diferença `ΔD`=0,000465.
- Última janela auditada: diferença absoluta D=0,003208 e ΔD=0,001846.
- Bootstrap ΔD p10/p50/p90, com 12 réplicas:
  - primeira: `[-0,20067; -0,02952; +0,08195]`;
  - última: `[-0,12150; -0,00646; +0,06417]`.
- Novamente as distribuições de ΔD incluem direções positivas e negativas, demonstrando sensibilidade amostral maior que as pequenas diferenças de resolução no subconjunto.

## Resultado metodológico

Este é um exemplo real de **falsificabilidade interna**: um indício atraente do M6 foi ampliado e **não se confirmou uniformemente**. Em BTC 1m a vantagem do M6 sobre M5 para ΔD desapareceu, enquanto M6 aproximou melhor a forma absoluta. Em 1h, M6 aproximou ΔD melhor que M5 na maioria das origens, mas ainda foi inferior ao SF1 em erro mediano; M5 aproximou melhor os valores absolutos da forma.

A precisão numérica inicial do indicador é satisfatória nas janelas auditadas, **mas não suficiente para declarar confiabilidade estatística das variações temporais**, dado o bootstrap amplo. A constatação de não convexidade dos modelos de densidade estimada continua observacional; sua interpretação econômica ou dinâmica exige validação adicional.

## Decisão e próximo trabalho

1. **Não promover M6** a controle global superior: não há consistência entre 1m e 1h e entre ΔD, D e C.
2. Preservar M5 como melhor controle para a perda conjunta de atividade do M5; preservar SF1 e M6 como referências alternativas importantes, pois cada um pode aproximar melhor aspectos diferentes.
3. Para a dinâmica geométrica, ampliar origens e replicações e estimar incerteza por blocos realistas, corrigindo multiplicidade e incorporando nulos com regimes/sazonalidade e volatilidade agrupada; não usar valor médio de erro isolado como teste estatístico.
4. Investigar métricas de **alteração de forma diretamente sobre densidades**, além do ΔD: por exemplo, distância entre HDRs alinhadas e estabilidade de mapas de curvatura; ΔD pode ser próximo de zero mesmo quando duas formas se deformam fortemente e de modo compensatório.
5. Testar coerência temporal das fotografias fechadas em sequência longa de streaming real, sem presumir 24h validado a partir de dois candles reais anteriores.

## Reprodutibilidade

- Protocolo: `reports/PROTOCOLO_SGV_M7_20261009.md`
- Código: `experiments/m7_dinamica_hdr50_validacao.py`
- Testes: `tests/test_m7_dinamica_hdr50_validacao.py`
- Workflow: `.github/workflows/m7-dinamica-hdr50-validacao.yml`
- CSV de erros por origem e modelo e JSON com controles e auditorias completos disponíveis nos artefatos da execução.
- GitHub Actions: https://github.com/ana-rigel/sgv-geometria/actions/runs/37963662906

**Integridade:** nenhuma alteração na `main` e nenhuma leitura dos períodos confirmatórios reservados.
