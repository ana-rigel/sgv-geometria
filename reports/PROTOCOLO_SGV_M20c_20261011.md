# SGV-M20c — Geometria de transições condicionais contra comparadores não lineares

**ESTADO: PROTOCOLO PRÉ-REGISTRADO — 11/10/2026, antes de implementar/executar M20c.**
**Base:** ramo research/m20b-dependencia-alem-segunda-ordem.
**Ramo:** research/m20c-acoplamento-condicional. Apenas sintéticos; main e holdouts BTC intactos.

## Pergunta científica
Uma distância geométrica condicional, obtida de quantis de projeções
unidimensionais dos estados sucessores, identifica dependências temporais
não lineares que escapam das estatísticas de segunda ordem? Oferece ganho
mensurável sobre HSIC convencional, usando exatamente as mesmas séries,
mesmas referências e mesmo critério de alarme?

O objetivo NÃO é provar novidade teórica. O estudo compara desempenhos;
a formulação da "geometria" é apenas um funcional explícito do acoplamento
q(x_t,x_(t+1)) e não uma medida intrínseca única da dinâmica.

## Verdades geradoras e cegamento das direções
Cinco cenários, cada trajetória em 3 dimensões:
- N0: ruído branco N(0,I);
- NVAR: VAR(1) gaussiano A=0.38 I, inovações N(0,(1-0.38²)I);
- H+: processo M20b rank-one em 1 dimensão latente com eta=+0.43;
- H-: como H+, eta=-0.43;
- VOL: processo de volatilidade latente com Z_t=0.7 Z_(t-1)+sqrt(1-0.7²)e_t,
  U_t=S_t Z_t, sinais Rademacher iid (a primeira coordenada tem autocovariância 0).

Nos cenários H+,H-,VOL, as 3 coordenadas são submetidas a uma rotação
ortogonal uniformemente aleatória independente POR TRAJETÓRIA,
obtida da decomposição QR de uma matriz gaussiana com ajuste de sinal
e determinante; a rotação NÃO é fornecida aos detectores. A mesma rotação
é aplicada ao prefixo e à janela de avaliação da respectiva trajetória.
Isso mantém a marginal N(0,I) de cada instante; os estados H± têm todas as
autocovariâncias lineares nulas, mas dependência não linear.

## Desenho prefix-only com nulo composto
Cada trial independente: prefixo 800 passos + futuro 500.
Primeiro ajustar somente ao PREFIXO um VAR(1) gaussiano trivariado com
intercepto, regressão ridge 1e-4 e covariância residual regularizada >=1e-6.
O futuro da verdade geradora nunca entra no ajuste.
Gerar 19 referências futuras independentes de comprimento 500 sob o VAR
ajustado, cada uma condicionada ao último vetor do prefixo observado.
Comparar a estatística da janela observada às 19 simuladas do nulo;
alarme se estatística da observação for estritamente MAIOR do que as 19
referências (posto extremo 1/20, nível nominal de discretização 5%).
Nenhuma janela de referência é reajustada ao futuro; o parâmetro do nulo
permanece prefix-only. Avaliação externa com 80 trials por cenário,
sementes independentes prefixadas pelo id do cenário e do trial.
A taxa sob N0 e NVAR **mede** a falha de calibração sob parâmetros
estimados, não presume exatidão formal do posto em nulo composto.

### Estatísticas, TODAS predefinidas
1. `conditional_sw2`: usar 6 direções de projeção (3 eixos canônicos e
   3 direções pseudoaleatórias independentes do trial, fixadas por seed
   271828); para cada projeção antecedente dividir x_t em tercis
   determinados no próprio bloco futuro (iguais regras para observado
   e referência), e para cada projeção do sucessor comparar o vetor
   de QUANTIS [0.1,0.25,0.5,0.75,0.9] de y_(t+1) condicionado ao
   tercil com os quantis incondicionais. Estatística média dos
   deslocamentos quadráticos de quantis (aproximação discretizada de
   W2² unidimensional fatiado/condicional). 6×6×3 combinações.
   Não é W2 exata e pode ter poder baixo: reportar sem correção ad hoc.
2. `rff_hsic`: norma quadrática da covariância cruzada de 16 características
   trigonométricas (sin/cos de 8 projeções gaussianas, seed 104729)
   para x_t e y_(t+1). Dependência kernel clássica e comparador principal.
3. `joint_mmd`: distância quadrática entre o embedding Fourier do
   acoplamento conjunto q e o embedding do produto de suas marginais,
   12 direções gaussianas 6D, seed 161803. Estimador característico
   aproximado, não MMD de kernel universal em dimensão infinita.
4. `linear_lag`: norma Frobenius da covariância cruzada 3×3 em lag1.
5. `quadratic_lag`: norma Frobenius da covariância cruzada entre
   vetores dos quadrados centralizados em lag1.
6. `marginal_shift`: distância gaussiana de momentos entre metades
   (norma das diferenças de média/covariância), controle de fotografia.

Todas as estatísticas são não negativas, calculadas somente sobre o
próprio futuro de 500 passos. As direções dos detectores têm sementes
globais fixas e são iguais para todos os cenários.
Nenhum conhecimento da rotação verdadeira é fornecido aos detectores.
Não selecionar configurações após observar os resultados.
Observação e referências usam as mesmas regras de estimador e
a mesma discretização. Janelas temporais são unidades dependentes
internamente; APENAS os 80 trials independentes por cenário sustentam
estimativas de poder/erro.

## Fixações de execução e poder
SEED=20261011; prefixo=800; futuro=500; R=19; trials=80/cenário.
Dividir em 5 jobs por cenário; cada trial possui RNG independente
baseado nos três inteiros (seed,scenario_id,trial), sem ordem entre shards.
Os testes automáticos de engenharia são distintos da rodada de resultados.
No piloto, três trials por cenário com dados menores e marcados como
engenharia, sem leitura de resultados para alterar o desenho principal.
Se código falhar, corrigir apenas BUG e declarar commit de reparo; nunca
alterar métricas, parâmetros científicos, R, N ou portões após executar.

## Portões pré-declarados
- G0: falha se taxa de alarme de `conditional_sw2` OU `rff_hsic`
  sob N0 ou NVAR >12.5% (10/80). Isso é um limite operacional
  permissivo, não prova de nível tipo I =5%.
- G1: detectar H+ e H- em >=35% dos trials por `rff_hsic` OU
  `conditional_sw2` em cada cenário, sem promover o melhor ex post.
  Reportar por estatística, com critérios de separação.
- G2 (teste de **vantagem geométrica**): `conditional_sw2` deve
  superar `rff_hsic` por >=10 pontos percentuais em CADA H±,
  e obter teste McNemar exato unilateral pareado p<0.025 em CADA.
  Caso não: "sem evidência de vantagem da geometria" (mesmo que
  ambos tenham poder alto).
- G3 (validade dos controles): `linear_lag` e `quadratic_lag`
  <=15% nos H+ e H-, com ressalvas de calibração sob nulo composto.
- VOL é controle auxiliar da potência para memória de variância;
  NÃO será usado para escolher o melhor método pós-hoc.

Todos os alarmes e pares discordantes por trial serão salvos em JSON e
agregados sem exclusões silenciosas. McNemar é exato binomial com H0 50/50
sobre pares discordantes; sem confiança entre trials causais? Trials
independentes por construção. Intervalos Wilson 95% para taxas.
Nenhum controle FWER global entre todos indicadores secundários.

## O que não se pode concluir
Até uma vitória de conditional_sw2 seria específica aos cinco geradores
e parametrização de custo/quantis. Comparação não inclui todos os
detectores não lineares possíveis e não prova novidade geométrica.
O modelo temporal VAR pode ser inadequado às alternativas POR DESENHO;
as taxas de alarme medem incompatibilidade, não tensão ou retorno futuro.
Nenhum BTC será usado, nenhum holdout M19 reaproveitado, nenhuma
inferência de causalidade nem vantagem financeira.

## Próxima etapa
Somente após leitura destes resultados, decidir se uma medida geométrica
condicional merece aprimoramento, auditoria de robustez ou arquivamento.
Uma nova família de medidas será protocolada em novo ensaio e não
"otimizada" retrospectivamente sobre M20c.
