# SGV-M20a — Geometria de trajetórias e acoplamentos temporais
STATUS: PROTOCOLO PRÉ-EXECUÇÃO — 11/10/2026 — incluído no mesmo commit que o código antes da execução Actions.
Ramo: research/m20-trajetorias-transicoes. Base: research/m19-rupturas-estruturais.
**Apenas dados sintéticos**. Nenhum BTC, nenhuma data reservada e nenhuma atualização da main.

## Problema
Uma trajetória de densidades marginais p_t pode ser idêntica sob dinâmicas diferentes.
Medir velocidade do objeto HDR ou apenas W2(p_t,p_t+Δ) pode ignorar correntes
temporais que conservam a densidade. O teste tenta distinguir descrição da
trajetória das marginais de informação contida no acoplamento q(x_t,x_t+1).

## Verdades geradoras fixadas ANTES do primeiro run
X_(t+1)=A(beta)X_t + epsilon_t; X_0~N(0,I), epsilon~N(0,Q(beta))
A(beta)=[[0.65,-beta,0],[beta,0.65,0],[0,0,0.65]],
Q(beta)=I-A(beta)A(beta)^T. Assim p_t=N(0,I) para todo beta.
Diagonal da covariância lag1 é idêntica para beta=0,+0.22,-0.22.
Null: beta=0 (dinâmica reversível, mesma marginal).
Rotações: beta=+0.22 e beta=-0.22 (correntes opostas, mesmas marginais).
Drift: beta=0 com deslocamento determinístico adicional do centro de 0 a 1.4
ao longo da sequência; é um controle de distribuições realmente variáveis.

Cada série começa na distribuição invariante, sem burn-in. Independência entre
trajetórias e entre calibração e avaliação. RNG numpy PCG64 seed 20261011.
n=1200 observações/série; calibração n=320 séries sob null;
avaliação n=240 para cada grupo (null, rot+, rot-, drift).
Piloto (modo separado) n=640, 24 calibração e 24 avaliações por grupo,
seed 20261012; o piloto serve só para engenharia e não adapta hipóteses.

## Medidas e comparadores
1. endpoint_w2: distância W2/Bures de gaussianas de momentos ajustados nas
   duas metades; proxy, NÃO W2 exata da densidade GMM ou da distribuição empírica.
2. path_length: soma das distâncias gaussianas W2 entre janelas móveis de 256
   observações e passo 128. Janelas sobrepostas não são amostras independentes.
3. transition_cost: custo médio real dos pares consecutivos ||X_t+1-X_t||².
4. excess_cost: transition_cost menos limite inferior W2² gaussiano entre as
   duas marginais empíricas da transição; esperado incapaz de identificar rotação
   com tr(A) constante; valor não representa dissipação física.
5. current_abs: |E[X_t,0 X_t+1,1 - X_t,1 X_t+1,0]|. É uma
   **covariância cruzada defasada antissimétrica**, não uma nova métrica exclusiva.
6. lagcov_frobenius: ||Cov(X_t,X_t+1)-0.65 I||_F,
   comparador convencional que tem acesso ao valor gerador nulo (oracle).
7. lagdiag_departure: |tr(Cov lag1)/3-0.65|; controle de ACF univariada.
8. mean_shift e cov_shift: comparadores estáticos usuais.

Limiar por estatística: quantil superior 95% (método higher) em 320 séries
calibradoras independentes sob null. Alarmar apenas quando valor > limiar.
Avaliação em séries independentes; reportar numerador, denominador e Wilson 95%.
As estatísticas secundárias não recebem controle de multiplicidade e não são
convertidas em descobertas confirmatórias.

## Portões congelados (taxas empíricas, não p-values)
E1: verificação analítica A A^T + Q = I.
E2, primário: current_abs falso alarme <=10% na avaliação null,
   poder >=80% nas duas rotações, endpoint_w2 falso alarme rotacional <=15%.
E3, positivo: endpoint_w2 detecta >=80% do drift.
Comparar obrigatoriamente current_abs com lagcov_frobenius. Se este último
detecta o mesmo, o ganho é identificação temporal, NÃO nova informação geométrica.

## Limites e próximos passos
Resultados mostram detectabilidade num mundo sintético controlado, NÃO
adequação a BTC, nem prova de superioridade frente a modelos VAR/HMM,
nem identificabilidade única de campos de fluxo. Fisher-Rao L2 não é reaberta;
nenhum GMM é rastreado como partícula. O próximo estágio exige ajuste prefix-only,
blocos/regimes adequados, custo OT sobre densidades não gaussianas,
perturbações fora da família linear e calibração aninhada com dados exploratórios.
Se qualquer portão falhar, não trocar limiar nem tamanho de efeito após observar.
