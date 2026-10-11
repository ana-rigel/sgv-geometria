# SGV-M20d — Ablação fatorial da perda de poder nas transições
**STATUS: PROTOCOLO CONGELADO — 11/10/2026, ANTES de código e GitHub Actions M20d.**
**Base:** research/m20c-acoplamento-condicional
**Branch:** research/m20d-ablacao-fatorial
**Dados:** apenas geradores sintéticos. Sem BTC, sem abrir holdout M19; sem alterar main.

## Pergunta e inferência permitida
No M20c, HSIC e "transporte" condicional perderam poder versus M20b ao
mudar simultaneamente dimensão/direção de projeção, amostra 1800→500,
nulo conhecido→VAR ajustado no prefixo. M20d decompõe as três mudanças
sobre as MESMAS trajetórias geradoras por trial. Isso é uma ablação,
não uma nova descoberta estatística ou garantia de identificação dinâmica.

## Geradores, condições, sequências pareadas
Cenários: N0 iid N_3(0,I); NVAR VAR(1) com A=0.38I e inovação
N(0,(1-0.38²)I); H+ e H− da família M20b, com kernel rank-one
K_eta(y|x)=phi(y)[1+eta h(x)h(y)], eta=±0.43, h(x)=sin(2x)−2e^(−3/2)sin(x).
VOL: processo M20b com z_t AR(1) rho=.7 e sinais Rademacher iid.
Nos 5 grupos, gerar trajetória base de 800+1800 observações e aplicar
uma rotação própria Q∈SO(3) aleatória, fixa ao longo de um trial.
Sob H± e VOL a dependência latente está na direção d=Q[:,0].

FATORES CRUZADOS 2×2×2=8:
- D: known = projetar x_t na direção d (oráculo de direção); blind =
  projetar na direção fixa e1 (sem acesso a d);
- N: 500 ou 1800 observações prospectivas, SEM mudar prefixo;
- R: known = nulo gerador nominal do cenário (IID N(0,I) para N0,
  H± e VOL; VAR(0.38 I) para NVAR); fitted = VAR(1) ajustado SOMENTE
  ao prefixo de 800 observações, intercepto e covariance regularizados.
A observação é idêntica nos cenários R=known/fitted, e os primeiros
500 candles de N=1800 são os mesmos em N=500.
Sob NVAR simular a referência conhecida condicional ao último vetor do
prefixo; sob IID não há estado inicial a condicionar. Ajuste de parâmetros
nunca usa prospectivo observado.

**Limitação estrutural de D:** o método blind=projeção fixa e1 é deliberadamente
um comparador direcional simples (não um detector 3D universal ou invariante
a rotações). Assim, qualquer efeito "direção" combina acesso ao oráculo
e possível diluição da projeção; não prova incapacidade geral dos métodos cegos.
Para transparência, rodar também um RFF-HSIC 3D rotacionalmente cego
(com projeções gaussianas FIXAS por seed) como diagnóstico secundário
nas células N/R, independente do fator D; não otimizar esse baseline após ver dados.

## Estatísticas e alarme
Testes primários na projeção unidimensional:
- HSIC-1D = ||Cov(f(U_t),f(U_{t+1}))||²_F,
  f(u)=[sin(k u), cos(k u)] para k=1,2,3, tal como M20b.
- CQW2-1D = média dos deslocamentos quadráticos dos cinco quantis
  .1,.25,.5,.75,.9 entre três tercis de U_t e marginal incondicional
  de U_{t+1}; proxy discreta de Wasserstein condicional, NÃO OT exata.
- LAG-1D = |Cov(U_t,U_{t+1})|, controle linear.
Comparador secundário fora do fatorial D: RFF-HSIC-3D com 8 projeções
gaussianas fixadas por seed 104729, como M20c. Não chamar CQW2
de propriedade única ou vantagem teórica de geometria.

Para cada observação e célula, gerar 19 referências N=1800 sob o
mesmo nulo R ajustado ao prefixo ou conhecido. O score de cada referência
usa os primeiros 500 ou os 1800 passos conforme fator N.
Posto extremo: score observado > TODAS as 19 referências; nível
discreto nominal 5% apenas sob um nulo com permutabilidade válida.
Usar MESMAS sementes dos 19 futuros de referência entre
as direções e comprimentos de cada célula R. Sob R=known/fitted,
referências diferem por construção, mas os observados não diferem.

## Tamanho, independência e avaliação
64 trials independentes por cenário, cada um com prefixo=800,
futuro longo=1800, R=19, SEED=20261011.
Identificadores de RNG gerados por SeedSequence([seed,scenario_id,trial,stream]),
com streams distintas para verdade e os dois conjuntos de referências.
Congelar tamanho e critérios antes do primeiro ensaio Actions.
Cada job processa um cenário, gera 64 trials e emite JSON
com contagens POR CÉLULA e, por trial, booleanos de alarme; negar
dados faltantes e duplicados. Um único piloto de engenharia com
2 trials/cenário (seed+1), sem adaptação científica.

## Análise travada
Calcular taxas (k/64) e Wilson95 para TODAS as 8 células de
HSIC-1D, CQW2-1D, LAG-1D, mais RFF-HSIC-3D por N/R.
Para H+ e H−, contrastes pareados POR TRIAL para cada fator,
marginalizando igualmente as quatro combinações dos outros fatores:
∆D = taxa(known)−taxa(blind);
∆N = taxa(1800)−taxa(500);
∆R = taxa(known_nulo)−taxa(fitted_nulo).
Reportar os contrastes por H+,H− e por métrica; média dos dois
cenários apenas como descritivo. A incerteza de diferenças deve
reaproveitar ensaios independentes como unidade (bootstrap 2000
resamples de 64 trials de cada cenário, seed fixada 314159);
NÃO tratar 256 células dentro do cenário como 256 amostras iid.
Ablar em igual base pareada e publicar resultados negativos.

Portões, TODOS antes de execução:
G0: sem leaks, todos os shards presentes (5×64), integridade
de observações e quantis; testes automatizados aprovados.
G1: calibração operacional no N0 e NVAR, para HSIC-1D e CQW2-1D:
média de alarme sobre oito células <=10% e nenhuma célula >16%
(10/64; limite operacional, NÃO teste exato tipo I).
G2: poder >=60% para HSIC-1D em H+ E H−
na célula D=known,N=1800,R=known.
G3: poder <=20% para HSIC-1D em H+ E H−
na célula D=blind,N=500,R=fitted.
G4: ao menos um fator entre D,N,R gera contraste médio
de HSIC-1D >=10 pontos percentuais nas duas H±
(a direção não deve ser declarada causal se interações
não forem descritas). G4 caracteriza diagnóstico sintético,
não vantagem contra outro método.
G5 (vantagem geométrica): CQW2-1D deve superar HSIC-1D
por >=10 pontos percentuais e McNemar unilateral EXATO
p<.025 em cada H± na célula "blind,500,fitted".
Caso contrário: "não demonstrada vantagem geométrica".

Se algum portão falhar, relatar como falhou. Não modificar
efeitos, tamanho, limiar ou especificação a posteriori.
Não usar indicador de sucesso de workflow como suporte científico.
Não reproduzir análises confirmatórias BTC. Sem claims de trading.

## Limitações de interpretação
Direção conhecida exige oráculo não disponível no mercado.
Nulo conhecido é oráculo estatístico.
VAR ajustado no prefixo pode produzir pseudo-postos não exatos.
M20b e M20c diferem em outros pontos; fatorial captura fatores
definidos NESTE experimento, não estabelece causalidade universal
das discrepâncias de versões anteriores.
