# SGV — Saltos e Markov V2: resultados reais dos controles sintéticos

Data: 15/10/2026. Executado **após** pré-registro `PREDICAO_saltos_markov_V2.md` e commit do código `5e7dcbf`, testes `b83333e`. Workflow GitHub Actions `38818887579` **concluído com sucesso** (nove testes e medição). Resultado bruto imutado: `resultados/saltos_markov_v2_controles_20261015.json`. Este relato **não** classifica séries financeiras.

## A — Série contínua versus processo com saltos conhecidos

32 trajetórias por condição, 2048 unidades temporais por trajetória, resolução fundamental 0,125. Mesma parte browniana emparelhada, processo com saltos Poisson composto de intensidade `lambda=0.3` e tamanho `J~N(0,0.8²)`.

| dt | M4(dt)/dt contínuo | M4(dt)/dt difusão+saltos |
|---|---:|---:|
| 0,125 | 0,03757 | 0,44502 |
| 0,25 | 0,07521 | 0,55682 |
| 0,5 | 0,14938 | 0,74503 |
| 1 | 0,30330 | 1,10923 |

Interceptos extrapolados por regressão linear em quatro escalas: **difusão contínua = −0,000999** (IC95 bootstrap por trajetórias: [−0,002671; +0,000611]); **difusão+saltos = +0,361556** ([+0,335424; +0,389182]). Limite teórico da componente de saltos: `lambda E[J^4] = 0,36864`. **Três gates A aprovados**.

**Limites:** essa regressão é aproximação em escalas finitas; não uma demonstração analítica de limite no BTC. A interpretação de Pawula não deriva de excesso de curtose em dt=1 apenas. Uma difusão com volatilidade variável pode ter curtose positiva em escala finita sem saltos.

## B — Volatilidade latente conhecida, proxy causal e nulo homocedástico

24 trajetórias independentes de 12.000 passos após burn-in; modelo `x[t+1]=0.2*x[t]+exp(h[t]/2)*eps[t]`, `h[t+1]=0.995*h[t]+sqrt(1−0.995²)*eta[t]`. O instrumento mede correlação de Spearman da energia quadrática normalizada contra média dos dez valores anteriores.

| Série sintética | M sem normalizar pela vol local | M com proxy causal de 60 passados | M com volatilidade latente verdadeira |
|---|---:|---:|---:|
| Volatilidade latente | **0,389738** [0,377649;0,400588] | **0,127676** [0,123118;0,132516] | **0,000961** [−0,003183;0,005136] |
| Homocedástica | 0,000961 [−0,002747;0,005229] | −0,004253 [−0,008674;0,000039] | 0,000961 [−0,003183;0,005136] |

**Cinco gates B aprovados**. A estatística positiva desaparece quando normalizamos pela variância verdadeira conhecida; o proxy causal remove parte da dependência. O novo positivo demonstra poder instrumental neste modelo e mostra que redução <50% no teste antigo não poderia, sozinha, excluir volatilidade escondida. Não prova propriedade de Markov do processo observado em geral: é um teste de dependência de energia.

## Julgamento científico

**8/8 gates pré-registrados aprovados, 9/9 testes de sanidade aprovados no GitHub Actions.** Isso valida a **instrumentação em controles sintéticos conhecidos**, não a extrapolação de salto, continuidade, unicidade de dimensão latente ou previsão no mercado. O teste V1 continua arquivado como exploração com interpretação excessivamente forte. Junho–setembro são períodos já usados e nunca podem ser apresentados como dados novos confirmatórios.

O estágio V2b foi definido em `PROTOCOLO_saltos_markov_V2b_mercado.md` para reavaliar DESCRITIVAMENTE os mesmos meses com proxies causais; suas futuras leituras não podem mudar as regras deste documento.
