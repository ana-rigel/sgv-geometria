# SGV-M20e — Direção adaptativa causal de dependências temporais

**CONGELAMENTO PRÉ-EXECUÇÃO: 11/10/2026, antes do código e de qualquer ensaio M20e.**
**Base:** research/m20d-ablacao-fatorial; **ramo novo:** research/m20e-direcao-adaptativa.
**Escopo:** APENAS processos sintéticos; não acessar BTC, não reabrir confirmação M19, não modificar main.

## Pergunta
A recuperação da direção não linear `d` exclusivamente do histórico prefixado,
sem acesso ao gerador verdadeiro, melhora a detecção de dependências de
pares ordenados (X_t, X_(t+1)) frente a projeção fixa e à HSIC multivariada?
O rastreio adaptativo é estatística kernel clássica, NÃO nova curvatura.

## Processos geradores
Reutilizar **sem modificação** `make_truth` de M20d para cinco grupos:
N0 iid N(0,I), NVAR isotrópico rho=.38, H+ e H− com kernel
rank-one M20b eta=±0.43, e memória de volatilidade VOL.
Cada trial é rotacionado aleatoriamente por Q∈SO(3); direção latente
verdadeira `d=Q[:,0]` é mantida apenas para AFERIÇÃO da recuperação,
e para o teto do detector oráculo. NUNCA informar `d` ao estimador adaptativo.
Mesmo prefixo de 800 e futuros de 500 e 1.800 pontos para todos os métodos.

## Aprendizagem causal da direção
Criar 32 direções candidatas determinísticas globais: eixos
(1,0,0),(0,1,0),(0,0,1) + 29 pontos Fibonacci na esfera
com sinal canônico; mesmas candidatas para todos os trials.
Na sequência prefixada `P=X[:800]`, computar em cada direção
o HSIC de Fourier univariado com características sin/cos
das frequências 1,2,3, conforme M20b. Selecionar o índice de
máxima dependência (tie->menor índice).
**Seleção usa somente prefixo e nunca os 500/1.800 pontos futuros.**
Sem usar pesos `h`, labels H±, índice verdadeiro do cenário, `d`
ou dados das 19 referências. Seleção é cega ao gerador e sem ajustes
posteriores. Direção fixa convencional: e1.

## Instrumentos
1. `adaptive_hsic` (primário): HSIC 1D de Fourier na direção
   selecionada prefix-only, nos pares consecutivos do futuro.
2. `fixed_hsic`: HSIC 1D em e1 (sem aprendizagem).
3. `scan_hsic`: máximo HSIC 1D sobre as mesmas 32 direções
   computado *no futuro* observado. Aplicar exatamente o mesmo
   procedimento em cada futuro sintético de referência para
   calibrar a seleção (evita usar p-values de direção fixa
   após busca no futuro). É comparador clássico, não detector causal.
4. `rff3d_hsic`: HSIC multivariada de 3D com 8 frequências
   gaussianas fixas (função `rff_hsic` de M20c). Não recebe `d`.
5. `adaptive_cqw2`: métrica de cinco quantis condicionais
   a tercis, `projected_stats` do M20d (proxy Wasserstein);
   aplicada à direção prefix-only escolhida por HSIC.
6. `oracle_hsic`: teto diagnóstico HSIC em `d`; não
   elegível como vencedor.
Todas medidas não negativas e calculadas apenas na série futura
(não anexar último ponto do prefixo como primeiro par).
Relatar recuperação |dot(d_hat,d)|, comparadores e pares discordantes.
Os métodos adaptativos usam um detector estatístico clássico (HSIC)
para escolher direção; sucesso não significa ganho intrínseco geométrico.

## Nulos aninhados: prefix-only
Para cada trial independente gerar futuro observado de 1800 e 19 futuros
de referência de 1800 a partir de VAR(1) Gaussiano ajustado somente
ao prefixo 800, com intercepto, regularização ridge=1e-4
e covariância residual PD (funções M20c).
Condicionar as simulações ao último vetor do prefixo.
Usar os MESMOS 19 futuros para todos detectores e ambos comprimentos,
os primeiros 500 são prefixo dos 1800. `d_hat` congelado do prefixo
é o mesmo na observação e em TODAS as referências.
Se `scan_hsic` busca uma direção diferente na referência,
isso é esperado e necessário para calibração da busca interna.
Alarme por posto extremo: observado estritamente > máximo das 19 referências.
Com nulo estimado, o posto NÃO é teoricamente uniforme por construção:
medir taxas nulas N0 e NVAR em ensaios independentes.

## Amostragem, sementes e testes
5 grupos, 64 ensaios independentes por grupo: total 320.
SEED=20261011, identificador de RNG: [SEED,sid,trial,stream].
Prefixo=800, futuros 500/1800; R=19.
5 shards paralelos, um por grupo, cada um com 64 trials.
Um piloto de engenharia com 2 ensaios/grupo, SEED+1,
não pode orientar alterações científicas; bugs podem ser
corrigidos com commits explicitamente documentados.
Todas as condições e sementes ficam fixas no mesmo protocolo
antes de iniciar o workflow.

## Portões pré-especificados
G0 — Integridade: todos 320 trials completos, testes unitários,
sem vazamento futuro; comparação de condições pareadas.
G1 — Calibração: para `adaptive_hsic` e `scan_hsic`,
em N0 e NVAR nas duas janelas, taxa em cada célula <=12.5%
(8/64); é limite OPERACIONAL, não nível tipo I exato.
G2 — Recuperação direcional: ao menos 60% de H+ E H−
com |cos(d_hat,d)|>=0.80; estimativa baseada no prefixo.
G3 — Poder do adaptativo em 500 pontos: >=35% em H+ E H−.
G4 — Benefício da seleção causal no 500:
adaptive_hsic supera fixed_hsic em >=10 pontos percentuais
e McNemar exato unilateral p<0.025 em H+ E H−.
G5 — Comparador sem oráculo: adaptive_hsic não fica >10
pontos abaixo de scan_hsic em H+ E H− no 500.
G6 — Superioridade da proxy geométrica, NÃO pressuposta:
adaptive_cqw2 supera adaptive_hsic por >=10 pontos
e McNemar unilateral p<0.025 em H+ E H− na janela 500.
Se G6 falhar, nenhuma alegação de vantagem geométrica.
Os percentuais entre 500 e 1800 são efeitos exploratórios,
com mesmo trial e não amostras independentes.
G0..G6 serão todos reportados, sem gate reclassificado depois.
Não escolher parâmetros nem selecionar nova combinação
com base no que der melhor no ensaio.

## Limites
Recuperação `d` é possível de avaliar somente porque o gerador
sintético fornece um oráculo para VERIFICAÇÃO, nunca seleção.
A base VAR fita ao prefixo pode ser inadequada; resultados
não devem ser extrapolados a preço, stress, causalidade,
intrinsic Fisher-Rao, BTC real ou retorno de trading.
Comparar ao HSIC scan e HSIC 3D para evitar declarar novidade
onde um método estatístico convencional já resolve.
