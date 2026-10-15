# SGV — Saltos e memória V2: protocolo anterior à execução

Data: 15/10/2026. Ramo: `research/saltos-markov-v2-controles-20261015`, derivado do resultado exploratório original `exploracao/saltos-markov@9aba56d`. **Não apaga, revisa nem promove o resultado original a confirmação.** Não acessar dados outubro/holdouts ou alterar experimentos congelados. Esta V2 realiza PRIMEIRO testes sintéticos positivos/negativos com verdade conhecida.

## Por que a V1 não identifica os mecanismos

- Curtose de passos em escala fixa de 1 min NÃO é o coeficiente limite de Kramers–Moyal de ordem quatro, e a fórmula de Pawula não permite inferir trajetórias descontínuas desse teste isolado.
- O controle G de V1 reusa um caminho de volatilidade calculado por `rolling(center=True)` nos retornos reais (informação futura na reconstrução retrospectiva). Não é um controle causal endógeno e não isola a única dimensão latente.
- O M da V1 é Spearman entre agitação normalizada e média passada; não é teste completo de Chapman–Kolmogorov/Markov. O controle positivo original falhou; logo seu rótulo `não é a volatilidade` é inconclusivo.

## Teste A: controle positivo de 4º momento em múltiplas resoluções temporais

Simular **trajetórias contínuas** com (dX=\sigma(t)dW_t), `sigma²(t)=0.25*(1+0.5*sin²(2πt/83))`, e **trajetórias com saltos** `dX=\sigma(t)dW_t+dJ_t`, com Poisson composto `lambda=0.3` por unidade de tempo, amplitudes N(0,0.8²), independentes. Mesma parte browniana acoplada nos dois modelos. Usar **32 trajetórias independentes de duração 2048**, passo fundamental `dt=0.125`, sem agregação sobreposta para `dt=(0.125,0.25,0.5,1.0)`. Em cada dt, medir `M4(dt)/dt = mean((ΔX)^4)/dt` com incrementos centrais não subtraídos (deriva nula); média sobre trajetórias; regressão linear só sobre esses quatro dt para estimar intercepto descritivo do limite. Intervalo percentil bootstrap **de trajetórias inteiras**, 1.000 reamostragens, seed 202610151.

Predições fixadas **antes de executar**:
- difusão contínua: intercepto aproximado de zero, |intercepto| < 0,06 e IC incluindo zero;
- difusão+saltos: intercepto positivo > 0,15, limite inferior do IC95 > 0,10;
- coeficiente teórico dos saltos `lambda E[J^4]=0.3*3*0.8^4 = 0.36864`; desvio do estimador finito aceitável até 0,15, **somente controle de sanidade**, não inferência formal de mercado.
- `M4/dt` do modelo contínuo deve diminuir ao diminuir `dt`, enquanto o modelo com saltos tende a intercepto positivo. Se falhar, registrar falha do instrumento; não ajustar critérios pós-resultado.
- Limitação explícita: a série BTC disponível tem resolução nativa de **1 min**. Agregar 1→2→4 min NÃO produz observações abaixo de 1 min; portanto não permite tomar o limite dt→0 nem demonstrar presença/ausência de saltos no sentido de Pawula. V2 não dará classificação física de saltos para BTC.

## Teste B: controle de dimensão latente e proxy causal

Simular `x[t+1]=phi*x[t]+exp(h[t]/2)*eps[t]`, `h[t+1]=rho*h[t]+tau*sqrt(1-rho²)*eta[t]`, `eps,eta ~ N(0,1)` independentes, com `phi=0.2, rho=0.995, tau=1.0`. Comparador negativo: mesmo AR(1) com `h[t]=0` constante. Criar **24 trajetórias independentes de 12000 passos**, primeiro 1000 descartados como burn-in. Para cada passo, usar resíduos verdadeiros de AR(1) `r[t]=x[t+1]-phi*x[t]` (oracle, sem ajuste).
- `M_sem`: Spearman entre `r[t]^2 / exp(tau²/2)` e média dos 10 valores anteriores, sem o estado latente.
- `M_proxy`: mesma agitação dividida pelo **desvio quadrático médio dos resíduos nos 60 passos anteriores**, calculado causalmente por `rolling(60).mean().shift(1)` (nenhum `center=True`).
- `M_oraculo`: mesma agitação dividida por `exp(h[t])`, volatilidade latente conhecida, usada apenas nos controles sintéticos.
- Calcular Spearman por trajetória e média; IC95 bootstrap por **trajetórias independentes** (1.000 réplicas, seed 202610152).
Predições de controle:
  1. Em volatilidade latente: `M_sem > 0.20` e limite inferior do IC>0.10; `|M_oraculo|<0.05`, IC incluindo zero; `M_proxy` melhora (`M_proxy < M_sem`), mas **não é obrigado** a atingir limiar de redução 0.50 da V1.
  2. Em AR(1) homocedástico (controle negativo), `|M_sem|<0.05` e `|M_oraculo|<0.05`, IC abrangendo zero.
  3. `M_proxy` não pode ser interpretado como teste completo de Markov. Mesmo `M_oraculo≈0` só valida a estatística de memória da agitação neste gerador; não prova a propriedade de Markov em dimensão arbitrária.

## Transparência, dados reais e proteção

Esta rodada inicial executa **somente sintéticos autônomos** (bibliotecas numpy, scipy, pandas e pytest). Sem BTC, sem download de dados, sem alterações no `main`, sem reutilizar ou abrir qualquer conjunto reservado.

O código será commitado antes da execução; o relatório usará os valores do script, SHA-256 do JSON e status dos gates. O trabalho subsequente pode criar diagnóstico financeiro **exploratório** com correção causal e comparação por bootstrap semanal, mas os períodos junho–setembro já examinados **não podem virar teste confirmatório**. Não reutilizar o mesmo holdout como se fosse novo. **V2 não altera as classificações arquivadas da V1: adiciona parecer metodológico distinto**.

## Regra de interpretação

Se A ou B falhar no próprio controle de mecanismo conhecido, declará-lo **INCONCLUSIVO como instrumento**, em vez de inferir ausência de efeito real. Se ambos passarem, declarar somente **validade instrumental em sintéticos**. Não extrapolar para salto físico do BTC, unicidade de volatilidade escondida ou independência informacional da geometria.
