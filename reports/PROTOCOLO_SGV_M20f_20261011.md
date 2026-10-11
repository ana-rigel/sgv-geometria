# SGV-M20f — Dependência temporal multivariada invariante à rotação

**CONGELADO ANTES DO CÓDIGO E DA PRIMEIRA EXECUÇÃO M20f — 11/10/2026.**
**Base:** research/m20e-direcao-adaptativa. **Ramo:** research/m20f-kernels-invariantes.
**Escopo:** somente dados sintéticos, sem BTC, sem M19 holdout e sem modificar main.

## Pergunta
O erro predominante no M20e foi a dificuldade de encontrar a direção
latente; uma medida em 3D baseada exclusivamente em distâncias euclidianas
(invariante à rotação ortogonal conjunta) consegue detectar H+ e H− sem
direção oracular? A calibração permanece aceitável quando o nulo VAR é
ajustado apenas ao prefixo? A pergunta NÃO presume novidade matemática:
RBF-HSIC e distance covariance são métodos clássicos.

## Geradores (sem mudanças)
Importar `make_truth` de `experiments/m20d_ablacao_fatorial.py`,
rotacionado por SO(3) independente por trajetória, com cinco cenários:
0=N0 iid N3(0,I), 1=NVAR isotrópico rho=.38,
2=H+ rank-one oculto eta=.43, 3=H− eta=−.43,
4=memória de volatilidade VOL. Prefixo=800 e futuro=1800, ambos
por trial. 64 trials INDEPENDENTES por cenário, 5 shards, seed=20261011.
Cada trial usa o mesmo observado em todas métricas e n=500/1800.

## Aprendizado causal do kernel
Prefixo é dividido em 400 treino e 400 validação, ANTES do futuro.
Calcular `sigma0` = mediana das distâncias Euclidianas NÃO NULAS
entre todas as 120 observações igualmente espaçadas do prefixo
de treino, com piso 1e-6. Gerar três bandwidths fixas
sigma=(0.5,1,2)*sigma0.
No prefixo de validação, escolher a bandwidth que maximiza o
HSIC RBF de pares de transição das 192 amostras de pares
deterministicamente espaçadas; desempate menor multiplicador.
Apenas prefixo: nem direção verdadeira, nem futuro observado ou
referências futuras acessam a seleção. A seleção é FIXADA e usada
idêntica em todas as 19 referências de nulo.
Baseline RBF fixa sigma0 também será reportada.

## Medidas, todas nos MESMOS pares
Subamostragem de pares temporais (X_t,X_(t+1)) sem embaralhar tempos:
índices equally spaced determinísticos em n−1 pares, usando
192 pares quando futuro n=500 e 320 pares quando futuro n=1800.
Todos os métodos calculados nesses mesmos 192 ou 320 pares,
inclusive referências futuras e comparadores convencionais.
Não alegar que método com 320 pares utilizou 1800 pares efetivos.
Métricas:
1. `rbf_hsic_selected`: biased HSIC (média Kc*Lc), K_ij =
   exp(-||x_i−x_j||²/(2sigma²)), L análogo para y, sigma selecionada
   na validação, mesmo para x/y. É EXATAMENTE invariante à
   transformação ortogonal comum de todos estados, até precisão FP.
2. `rbf_hsic_fixed`: mesma fórmula usando sigma0 do treino.
3. `distance_covariance`: mean(A_c*B_c), matrizes de distâncias
   euclidianas centradas; convencional, exatamente invariante a SO(3).
4. `rff3d_hsic`: features seno/cosseno gaussianas 3D fixas
   (implementação M20c), baseline convencional aproximado, NÃO
   exatamente invariante sob rotação arbitrária (frequências finitas).
5. `prefix_direction_hsic`: HSIC 1D numa direção selecionada no
   prefixo completo via busca congelada de 32 direções (M20e),
   baseline histórico, SEM oráculo.
6. `scan_direction_hsic`: máximo HSIC 1D nas mesmas 32 direções
   dentro da janela FUTURA, reproduzido igualmente em cada
   referência de nulo para corrigir busca dentro da janela.
7. `oracle_direction_hsic`: teto diagnóstico 1D
   na direção verdadeira; NÃO acessível fora dos sintéticos.

`Kc` calculada por duplo centramento. Score não negativo
salvo tolerância numérica de arredondamento. Recolher bandwidth
escolhida, proxy de aproximação |dot(d_hat,d_true)| apenas
diagnóstica, e binários de alarme por trial.

## Nulo temporal e decisão
Ajustar VAR(1) Gaussiano trivariado apenas ao prefixo completo
800 via `fit_var` M20c (ridge 1e-4, covariance regularização
1e-6). Gerar 19 referências independentes de comprimento 1800
condicionadas ao último vetor do prefixo; usar os primeiros 500
para condição curta. Para TODAS métricas (inclusive scan),
alarme se escore observado > máximo das 19 referências
(20 posições, extremo nominal 5% somente em nulo conhecido).
Em nulo ajustado, uniformidade do posto NÃO é garantida:
usar N0 e NVAR para medir empiricamente erro, mantendo
a interpretação operacional. Não reestimar os parâmetros de nulo
em nenhuma referência e não usar o futuro na calibração do kernel.

## Amostra e controle de artefatos
64 trials por cenário, 5 cenários=320 unidades independentes.
Seed por experimento/sid/trial/stream usando SeedSequence.
Resultados de todos os 320 trials devem conter scores observados,
máximos de referência, decisão por método/nível de n e
bandwidth/índice. O agregador deve recusar arquivos ausentes,
shards duplicados, contagens inconsistentes e scores malformados.
Piloto só para engenharia: 2 trials/cenário, seed=20261012,
sem modificar hipóteses a partir do resultado.

## Portões pré-definidos
G0: 320 trials e todos testes executados; invariância à rotação
dos dois métodos métricos (RBF-HSIC e distância-cov) <1e-9
sob matriz SO(3) para mesmas amostras.
G1: calibração operacional: rbf_hsic_selected e
distance_covariance com <=8/64 alarmes em CADA condição
N0/NVAR e n=500/1800; o limite <=12,5% é permissivo e não
garante controle nominal em qualquer nulo composto.
G2: rbf_hsic_selected poder >=25% em H+ E H− em n=1800.
G3: rbf_hsic_selected deve superar rff3d_hsic em
>=10 pontos percentuais E McNemar exato unilateral p<.025,
em H+ E H− em n=1800 (não alegar superioridade universal).
G4: rbf_hsic_selected deve superar prefix_direction_hsic
em >=10 pontos e McNemar p<.025 nas duas H± em n=1800.
G5: distance_covariance atingir poder >=25% em H+ E H−
em n=1800 (controle adicional de que não é só banda RBF).
G6: vantagem de selecionar sigma causalmente: RBF selecionada
supera RBF fixa em >=10 pontos E McNemar p<.025 nas duas
H± em n=1800.
Se qualquer gate falhar, preservar a falha. RBF selecionada,
RBF fixa, dCov e todas as métricas são ESTATÍSTICAS CLÁSSICAS;
mesmo sucesso não prova nova geometria, dinâmica física ou
vantagem preditiva e muito menos trading. Não abrir BTC.

## Observação metodológica
As matrizes de kernel incluem a dependência entre pares
sobrepostos na série, mas o teste de calibração é externo por
trial. As métricas são comparadas nos MESMOS pares amostrados.
O aumento de n também aumenta a amostra de pares de 192 para
320: não é efeito puro de extensão de histórico.
A seleção de bandwidth por HSIC de validação pode aproveitar
dependência de baixa ordem VAR; por isso registrar taxas NVAR.
Este teste não implementa transporte ótimo nem Fisher-Rao.
