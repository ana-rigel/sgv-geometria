# SGV-D01 — Memória direcional residual: pré-registro antes do código, 15/10/2026

## Status e escopo
Exploração **não confirmatória em BTCUSDT de agosto–setembro/2026**, pois já foram abertos por outros experimentos. Controles sintéticos independentes, com verdade conhecida, são primeiro portão de validade instrumental. Setembro e agosto são os períodos de avaliação pedidos; junho–julho são **apenas treino**, maio é o aquecimento/âncora. **Outubro intocado. Novembro/2026 não disponível em 15/10/2026 e reservado para repetição futura, somente após fechamento do mês e congelamento novo da execução; jamais acessá-lo neste experimento.** Ramificação `research/sgv-d01-direcao-ago-set-20261015`, sem alterar `main` ou holdouts congelados.

## Pergunta precisa

Se o retorno direcional seguinte tem dependência de atrasos maiores do que os quatro últimos sinais, depois de controlar quatro retornos recentes, proxies causais de volatilidade e as três coordenadas atuais `(E_norm,jerk,memory_flux)`.

Três preditores aninhados com `StandardScaler + LogisticRegression(C=0.1,max_iter=500,solver=lbfgs)`, hiperparâmetros FIXOS, ajuste sempre somente no treino:
- B0: `sign[t],sign[t-1],sign[t-2],sign[t-3]`; quatro log-retornos correspondentes divididos por volatilidade EW10 disponível em t; log das estimativas causais EW10, EW60, EW240 (estimativas aplicadas ao próprio retorno corrente e não ao próximo). Identificação: memória curta + volatilidade.
- B1: B0 + exatamente as três coordenadas `E_norm, jerk, memory_flux` do estado em t. Pergunta: **a representação SGV acrescenta informação direcional sobre B0?**
- B2: B1 + sinais em atrasos de 5, 10, 20, 40, 60 minutos, todos anteriores ao retorno previsto (t+1). Pergunta: **o histórico mais longo acrescenta informação além da geometria e vol?**
Alvo `Y[t+1]=1{log(C[t+1]/C[t])>0}`; retornos zero excluídos de treino/eval, e nenhum indicador usa preço de t+1.

Métrica primária: log-loss probabilística. `D_geom=loss(B0)−loss(B1)`; `D_hist=loss(B1)−loss(B2)`; `D_total=loss(B0)−loss(B2)`. Reportar por **semana** e médias ponderadas pelo número de observações; bootstrap de **semanas inteiras** (B=2000 seed 202610156) com IC95% de D_geom e D_hist. Métricas secundárias: log-loss absolutos, acurácia, contagem, proporção de r=0 e fração de p>0.5. Nenhum número ser rotulado propriedade de Markov ou causalidade.

## Controle sintético pareado: poder e especificidade

Dois geradores com **os mesmos caminhos de volatilidade lenta e rápida** (`hL` AR(1) phi=0.999 var=0.3 e `hF` AR(1) phi=0.9 var=0.2), e **as mesmas magnitudes abs(N(0,1))**. `sigma[t]=0.0007*exp(.5*(hL[t]+hF[t]−.5))`.
- VOL_ONLY: sinais `s[t]` iid equiprováveis.
- VOL_PLUS_DIRECTION: `s[t]` repete `s[t−20]` com probabilidade `0.82` (ou inverte com 0.18); quatro+ atrasos recentes e volatilidade iguais em distribuição marginal, memória verdadeira long lag 20. Como os choques em módulo são idênticos, `rVOL_ONLY[t]^2=rDIRECTION[t]^2` exatamente por par.
- Synthetic coord: construir `E_norm` de preço sintético − EMA 0.05, padronizada por âncora exclusiva de 800 instantes iniciais, `jerk=Δ² retorno simples`, `memory_flux=ΔEMA0.05(E_norm)`. **Série synthetic análoga ao SGV**, não equivalência exata com configuração `SGVConfig` do BTC.
- 24 caminhos emparelhados independentes com N=7000 após burn 500. IDs 0–11 treino, 12–15 validação somente engenharia, 16–23 teste sintético independente. Limiar de entrada >800+60; nenhum ajuste após inspecionar teste.
- Ajustar B0,B1,B2 separadamente em ambas condições. Portões instrumentais: `D_hist_direction>=0.05` nat/observação e IC95% (bootstrap **caminhos**, 2000 seed 202610156) inferior >0; `abs(D_hist_null)<=0.015`; energia em cada par matematicamente idêntica (checagem exata).
- Previsões: sinal com memória no atraso 20 deve gerar `D_hist>0.05`, e cenário VOL_ONLY deve ter `|D_hist|<0.015`. Isto testa apenas a alternativa plantada, não todas as memórias possíveis. Se portão falhar, **instrumento inconclusivo** e o valor histórico continua exclusivamente descritivo.

## Mercado BTC — corte de treino, avaliação e integridade

- Dados do repositório junho–julho/2026 para treinar; maio/2026 fornece só aquecimento e pode influenciar a configuração causal da reconstrução SGV; pós-corte de julho **NÃO entra no ajuste**.
- Agosto–setembro/2026 avaliação exploratória **fora da amostra do ajuste**, mas historicamente já examinada pelos investigadores. Reusar função `E.carregar` com arquivos Binance e SHA-256 oficiais. `GR.E.coords_orig` reflete o código SGV original para `E_norm,jerk,memory_flux` com `SGVConfig()`. Não substituir `E_norm` por uma transformação sintética simplificada no BTC.
- Escalas do `StandardScaler` e coeficientes dos três modelos serão congelados no GitHub **antes** de baixar/abrir agosto–setembro neste workflow. Testes de causalidade e checksums precedem avaliação. Fechar todos os resultados de uma vez, sem tuning por agosto–setembro.
- Divisão avaliação: semanas começando em 1 ago, 8 ago, 15 ago etc., sem seleção pós-dados; se semana final curta, incluir se tiver ao menos 1440 observações; zero ajuste aos resultados.
- Gates descritivos para releitura: `D_hist>0` na média do período e IC95% da diferença acima de zero, e `D_geom>0` com IC95% acima de zero, relatados independentemente. Estes **não são gates confirmatórios** e não são provas de memória não-Markov.
- Não pedir arquivos de outubro/novembro. Não retreinar na avaliação; não atribuir acurácia elevada a ganho financeiro sem custos, spread e execução.

## Previsões feitas antes do teste (probabilidades subjetivas)

- Controles sintéticos identificam a memória plantada sem falso positivo energético: 90%.
- Agosto–setembro tem `D_hist>0` em média: 45%; IC95 inferior >0: 20%.
- `D_geom>0` em média: 45%; IC95 inferior >0: 20%.
- É possível que as três coordenadas não acrescentem informação frente ao histórico do preço e volatilidade. Resultado negativo é informativo.

## Nov/2026

Reservar como futuro experimento novo, quando mês completo estiver acessível; não o agendar automaticamente nem estimar seu resultado. **Antes de novembro**, registrar hash do código, features, coeficientes, treinamentos e thresholds congelados. Decidir previamente se modelos serão fixos da rodada agosto–setembro ou reajustados até outubro, SEM jamais usar novembro para selecionar. Novembro somente executável depois de novembro/2026 terminar, respeitando outro holdout SGV se houver.
