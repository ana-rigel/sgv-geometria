# SGV-M20b — Identificação de dependência temporal além da segunda ordem

**STATUS: PRÉ-REGISTRADO EM 11/10/2026, antes da execução M20b.**
**Ramo:** `research/m20b-dependencia-alem-segunda-ordem`.
**Base:** M20a (em research/m20-trajetorias-transicoes).
**Escopo:** somente sintéticos. Não acessar BTC exploratório ou confirmatório, não alterar main.
**Hipótese H20b:** dois processos podem ter marginais normais idênticas e
autocovariâncias nulas em TODOS os lags, inclusive autocovariâncias de
|X| e X², mas acoplamentos temporais de ordem superior diferentes.
Estatísticas não lineares de dependência devem detectar tais diferenças,
enquanto métricas marginais e autocovariâncias usuais ficam calibradas.

## 1. Geradores, invariantes e parâmetros irrevogáveis

**Cenário N0:** X_t=(U_t,V_t,W_t) iid N_3(0,I).

**Cenários H+, H-:** V_t e W_t iid N(0,1), independentes de U.
U_t é cadeia Markoviana iniciada na distribuição estacionária N(0,1) com
densidade de transição exata:

K_eta(y|x)=phi(y)[1 + eta h(x)h(y)],
h(x)=sin(2x)-c sin(x),
c=2 exp(-3/2) [pois E[X sin(kX)]=k exp(-k²/2)].
eta=+0.43 (H+) e eta=-0.43 (H-).

|h|<=1+c; |eta|(1+c)² <1, logo K>=0.
E[h]=E[Xh]=E[X²h]=E[|X|h]=0.
O nulo e H± têm a MESMA marginal p_t=N_3(0,I) e
Cov(X_t,X_(t+k))=0 para todo k>=1. Também Cov(U_t²,U_(t+k)²)=0 e
Cov(|U_t|,|U_(t+k)|)=0, embora haja dependência no acoplamento temporal.
A transição é reversível (q(x,y)=q(y,x)); não se alega corrente irreversível.
A densidade de transição é amostrada por rejeição com envelope rigoroso
1+|eta h(x)|(1+c); toda proposta y~N(0,1) é aceita com
probabilidade [1+eta h(x)h(y)]/envelope.

**Cenário H-vol:** Z_t=0.7 Z_(t-1)+sqrt(1-0.7²)epsilon_t com Z_0~N(0,1);
U_t=S_t Z_t, onde os sinais S_t são iid Rademacher independentes.
Mesmo N(0,1) marginal e Cov(U_t,U_(t+k))=0 para k>=1, mas
a memória de |U| e de U² é positiva. V,W iid normais independentes.

## 2. Desenho amostral e sementes
N=1800 candles sintéticos por trajetória.
Calibração: 280 trajetórias independentes N0.
Avaliação: 200 trajetórias INDEPENDENTES em cada N0, H+, H-, H-vol.
Semente 20261011; gerar amostras de calibração antes de qualquer avaliação.
Para piloto de engenharia somente: N=450, 16 calibração, 16 avaliação
por cenário, semente diferente 20261012. Resultados do piloto NÃO ajustam
hipóteses, parâmetros nem limiares.

## 3. Estatísticas fixadas
Todas calculadas exclusivamente a partir das transições ordenadas t->t+1.
- `fourier_hsic` (primária): dependência de x=U_t e y=U_(t+1) pela
  norma Frobenius² da covariância das características Fourier
  (sin(kx), cos(kx)) para k=1,2,3, e os mesmos k em y.
  É HSIC de características finitas de um kernel determinístico,
  EQUIVALENTE A UM TESTE CONVENCIONAL DE DEPENDÊNCIA NÃO LINEAR.
  A dimensão 1 foi escolhida com conhecimento do mecanismo; não se
  alega detecção automática de direções 3D desconhecidas.
- `lag_cov`: |Cov(U_t,U_(t+1))|.
- `lag_abs`: |Cov(|U_t|,|U_(t+1)|)|.
- `lag_square`: |Cov(U_t²,U_(t+1)²)|.
- `lag_sign`: |Cov(sign(U_t),sign(U_(t+1)))| (comparador não linear).
- `lag_hermite3`: |Cov(H3(U_t),H3(U_(t+1)))| com H3=x³-3x;
  comparador de momento superior.
- `oracle_h`: |Cov(h(U_t),h(U_(t+1)))|; não é estimador às cegas:
  comparador com conhecimento da verdade, limite superior ilustrativo.
- `static_mean`, `static_var`: diferenças absolutas entre
  metades, controles de estatísticas marginais.
Todos os valores testados contra quantil 95% empírico ("higher")
das 280 trajetórias independentes de N0; `alarme` se score > limiar.
Cálculo e limiar aplicados sem exceção a todas as trajetórias independentes.
Resultados: contagem, taxa e intervalo Wilson 95% em cada célula.
Os testes compartilham séries; não usar erros-padrão iid das janelas.

## 4. Portões de decisão FIXADOS
- G1: identidades matemáticas verificadas numericamente:
  integral de h contra phi, x phi, x² phi, |x| phi próximas de 0,
  e integrabilidade/positividade de K; testes independentes.
- G2: false alarm de fourier_hsic em N0 <=10%.
- G3: poder de fourier_hsic >=80% em H+ e H-.
- G4: `lag_cov`, `lag_abs`, `lag_square` <=15% em ambos H+ e H-.
- G5: `lag_abs` detecta H-vol em >=75%.
- G6: `oracle_h` detecta ambos H± em >=80%.
Critérios auxiliares `lag_sign`, `lag_hermite3`, `static_*` são
relatados, SEM reivindicação confirmatória por comparação múltipla.
Qualquer portão não satisfeito permanece reprovado; não otimizar
efeito, frequência, amostra, limiar ou estatísticas pós-observação.

## 5. Interpretação ex ante
Sucesso demonstrará apenas que observar acoplamentos temporais além de
momentos de segunda ordem permite discriminar dinâmicas com a mesma
marginal e autocovariâncias. NÃO valida originalidade geométrica:
Fourier-HSIC e os comparadores de alta ordem são métodos convencionais.
Não testa causalidade, previsão de BTC, eventos estruturais, tensão,
campo de transporte real ou Fisher-Rao L2.
Em seguida, se houver sucesso, comparar métodos de transporte condicional
e detectores não lineares em dados sintéticos fora da família geradora e
com nulos ajustados causalmente no prefixo, antes de qualquer BTC real.
