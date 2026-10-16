# SGV-AMB01 — Pré-registro de memória ambiental (Paper A → SGV)
**Data 15/10/2026; este arquivo é publicado ANTES do código, dos ajustes, da inspeção de validação ou da avaliação AMB01.** Novo ramo isolado `research/sgv-amb01-memoria-ambiental-20261015`; base do SGV-D01 `f94b82b`. Sem alteração da main, D01, ID4, C01 ou holdouts.

## Ponte com Paper A: hipótese, não aplicação automática do teorema
O Paper A (*Environmental Memory as a Resource for Self-Consistency*) separa persistência herdada do ambiente e autorretenção do observador, sob orçamento informacional. O SGV-AMB01 **não** transfere o teorema, o platô ou o orçamento C para o BTC. Operacionaliza a distinção entre informação contida na **história ambiental observada** e na **história interna dos retornos**, depois de controlar estado atual, volatilidade e passado curto.

Alvo direcional (Y_{t+1}=1[r_{t+1}>0]), barras de um minuto. A pergunta não é se a volatilidade isolada determina toda a memória, mas se **histórias ambientais** têm informação adicional condicionalmente ao estado atual e às quatro direções recentes.

## Grupos e recursos observados
- (X_t=(E_norm,jerk,memory_flux)), **construtor do repositório SGV no BTC**, sem mudar definições.
- História interna curta: sinais e retornos escalados dos últimos 4 minutos; proxies da vol atual EW10/EW60/EW240 de r².
- Ambiente atual (Z_t): log(1+volume) de BTCUSDT e agressão líquida (A_t=2\,taker_buy_t/volume_t-1), com escala adaptada só pelo treinamento de cada classificador. Volume e agressão são observáveis da barra COMPLETA t (não antes dela), para prever retorno de fechamento t→t+1. **Proxies de ambiente, não variáveis externas independentes nem causa estabelecida**.
- Histórico ambiental (Z_{t-k}, k=(1,5,15,30,60,120)); 12 componentes.
- Histórico interno longo: sinais (s_{t-k}), k=(5,10,20,40,60), 5 componentes.
- A0: estado SGV, história curta, volatilidade e ambiente atual.
- AE: A0 + história ambiental.
- AI: A0 + história interna longa.
- AEI: A0 + ambas histórias.
Fixar `StandardScaler + LogisticRegression(C=0.2, solver=lbfgs, max_iter=1500)`, sem seleção de variáveis, penalty L2 padrão. O escalonador e pesos treinados são congelados antes de olhar agosto–setembro.

## Estatísticas e interpretação
Log-loss de (Y_{t+1}), métricas incrementais:
- (Δ_E=L(A0)-L(AE)): informação ambiental extra frente ao estado atual;
- (Δ_I=L(A0)-L(AI)): informação interna extra frente ao estado atual;
- (Δ_{I|E}=L(AE)-L(AEI)): interna **depois** da ambiental;
- (Δ_{E|I}=L(AI)-L(AEI)): ambiental **depois** da interna.
Avaliação por caminho sintético independente e, no BTC, por semana inteira de 7 dias. Bootstrap 2000 reamostragens da unidade independente (`seed=202610157`), IC95 percentual. Reportar estimativas pontuais, perdas absolutas, acurácia, semanas, fração de retorno zero. Não fazer reivindicação de Markov, causação ou lucro; média positiva sem IC excluir zero não é confirmação.

## Sintéticos fatoriais pré-registrados, verdade conhecida
Quatro condições independentes, usando em cada ID o **mesmo caminho de volatilidade lenta/rápida e as mesmas magnitudes de retornos**:
- N: ambiente branco (Z iid), sinais iid equiprováveis e independentes de Z.
- E: ambiente latente AR(1) `rho=.985`, variância estacionária 1, com observações contemporâneas ruidosas `log_volume_proxy=Z+2.0 ε_v`, `imbalance_proxy=tanh((Z+2.0 ε_a)/2)`; sinal do retorno de (t+1) é Bernoulli(sigmoid(`1.8*Z[t]`)). **Memória ambiental, mas não autocópia de sinais.** O histórico dos indicadores ambientais pode melhorar a inferência de Z.
- I: mesmo Z iid e observações sem informação, sinal (s_{t+1}) repete (s_{t-20}) com probabilidade `0.82`, ou inverte com `0.18`. **Memória interna de atraso longo**, sem efeito de Z.
- EI: ambos os mecanismos; (P(s_{t+1}=+1)=sigmoid(1.8 Z_t + 1.5 s_{t-20})), com Z AR(0.985) e observações ruidosas.
Todos têm (r_t=\sigma_t |u_t|s_t), (u_t\sim N(0,1)), com `log(sigma_t/.0007)=0.5(hL_t+hF_t-0.5)`, `rhoL=.999,varL=.3;rhoF=.9,varF=.2`. Para evitar confusão, as observações ambientais artificiais são **proxies** de fluxo/volume, não OHLCV replicado do BTC. Magnitudes e volatilidade iguais entre condições dentro do mesmo ID, portanto (r_t^2) iguais (validar exatidão).
N=5000 observações por trajetória após burn-in de 500, IDs 0–19: treino 0–7, validação técnica 8–11, **teste sintético selado 12–19**. Âncora robusta do E_norm sintético exclusivamente nos primeiros 800 pontos, rótulos a partir do índice 950. Usar semente determinística `20261015` particionada por ID/uso e HMAC hash prefix. Nenhuma geração do conjunto 12–19 durante teste unitário/preflight. Controles não são previsão do BTC.

Gates prospectivos APENAS dos 8 caminhos sintéticos intactos:
1) Em E, `Delta_E>=0.005` nats por observação e IC95 bootstrap de trajetórias inteiras acima de zero;
2) Em I, `Delta_(I|E)>=0.04` e IC95 inferior >0;
3) Em N, `abs(Delta_E)<=0.005` e `abs(Delta_(I|E))<=0.005`;
4) em I, `abs(Delta_E)<=0.005`;
5) magnitudes/volatilidade exatamente emparelhadas em cada ID.
Se falhar, declarar instrumento AMB01 não validado para separar mecanismos, sem recalibrar com o holdout. EI é análise adicional **descritiva**; uma direção futura também pode carregar informação sobre Z, portanto não se espera que `Delta_(I|E)` seja zero automaticamente em E.

## Dados BTC retrospectivos e corte temporal
- **Treino:** somente junho–julho/2026 (mai/2026 somente âncora/aquecimento), OHLCV + `taker_buy`, checagem SHA-256 mensal pela função do repositório.
- **Avaliação:** agosto–setembro/2026, períodos JÁ examinados em outras investigações; **exploração** mesmo usando treino prefix-only. Sem ajuste, sem reponderar modelos, sem tuning, antes de abrir o corte na rodada AMB01. Dez primeiros lags de preço com causalidade estrita.
- Reportar incrementos e IC95 por semanas (fronteiras começando 01/08/2026, incluída a semana final se ≥1440 barras). Semana parcial não confere nova evidência independente.
- Especificar estatisticamente que volume e taker_buy da própria barra t podem ter relação com r_t; como são observados até t, não há acesso a r_{t+1}, mas isso não isola mecanismo físico ambiental.
- Treino revalidado por SHA-256 do **buffer de características e rótulos** com e sem meses adicionais e por paridade elemento a elemento; se divergir, PARAR E AUDITAR. `set -euo pipefail` obrigatório nos workflows.
- Novembro/2026 será fechado apenas após terminar o mês e checados holdouts em outro experimento. **Nenhum dado de out/nov pode ser lido na AMB01**.

## Apostas subjetivas registradas antes de calcular
- Gates sintéticos todos passam: 70%.
- BTC ago–set `Delta_E>0`: 50%; limite inferior IC95>0: 20%.
- BTC ago–set `Delta_(I|E)>0`: 40%; limite inferior IC95>0: 15%.
- Algum efeito de memória ambiental pode aparecer em volume/fluxo apesar de não haver sinal direcional previsível; encontrar persistência dos indicadores **não basta** para inferir efeito sobre o sinal.
