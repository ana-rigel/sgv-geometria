# IA geométrica v0

17/10/2026 · Ana Rigel · registro de origem (Claude Doc "IA geométrica v0", rev 7)

## O que ela é

A IA geométrica é um **observador feito de registros empilhados**. Cada registro segue o que está abaixo dele com uma rigidez; o primeiro segue o mundo, o segundo segue o primeiro, e assim por diante, cada um dez vezes mais lento que o anterior. Entre cada par há uma **tensão**: o que o de cima vê menos o que o de baixo lembra. O estado interno do observador é o vetor dessas tensões. O **regime** é a tensão comparada a uma régua fixa, nunca ao próprio passado recente. A **identidade** é o registro mais lento, o único que um salto do mundo não move. A **cegueira** de cada andar é conhecida antes de olhar: é a sua rigidez.

Ela não existe para zerar a distância entre si e o mundo. Existe para medi-la por escala, guardá-la, e relatar o que não consegue ver. O único ato que ela pratica é decidir quando olhar o mundo e quando confiar na memória, sabendo que olhar custa.

Em uma frase: um observador que conhece o próprio ponto cego e paga, com lentidão, para ter identidade.

Este documento é o registro do projeto antes de qualquer código rodar: o que ela é, de onde veio, o que a distingue de um filtro e os quatro testes que decidem isso, com apostas escritas. Nada aqui é resultado.

## De onde veio

A figura foi sonhada no sítio: observação, lembrança e identidade como três pontos num plano, e inteligência como o jeito de os três se moverem um atrás do outro sem se colarem. Em 27/2/2026 virou código (`sgv/core/runtime.py`: campo, memória, organização, tensão = ‖F − M‖, rigidez, regime por histerese) e foi apontada primeiro para a vida e para a prefeitura ("Tensão com o Sonho"). Em 4/3 virou o **Teste B** (`visualizar_ia.py`): o campo teleporta, a memória corre atrás, a organização segue a memória. Em 4/3 também encostou no Bitcoin, e de março a outubro de 2026 o SGV mediu, com nulos e pré-registro, o que esse observador consegue ver num mercado: nenhuma direção (nove testes), surpresa proporcional à temperatura (colapso C ≈ 0,9), uma borda que é objeto de 1 minuto, e uma memória de pelo menos quatro andares (MSM, b ≈ 10).

Em 17/10/2026, ao pôr a mente de março dentro do cubo do SGV com o BTC real, três coisas ficaram claras:

1. **O cubo já era uma mente.** E\_norm é o preço contra a própria média móvel, isto é, a tensão de um registro que segue o preço; jerk e memory\_flux são derivadas dessa tensão. Cinco meses de SGV foram cinco meses medindo os limites de um observador, achando que se media o mercado.
2. **A mente de março erra o regime** porque mede surpresa contra o próprio passado (E\_norm relativa): depois de um salto, declara calma enquanto ainda está longe do mundo. O cubo consertou isso sem saber, com a régua de maio. A v0 herda a régua.
3. **As duas rigidezes de março (0,85 e 0,05) são os dois primeiros andares da escada** que o MSM achou no BTC (7–9 min e 1–1,5 h). A v0 generaliza para k andares.

O parentesco teórico é o Paper A (cegueira espectral graduada em registros autoconsistentes: a memória com rigidez é um filtro passa-baixa, e a banda que não vê é definida por ela mesma), o programa do vinco (identidade como o que não se moveu quando tudo se moveu), o Paper C (ancoragem com histerese) e a linha "reobservar versus lembrar" (o custo de obter informação retendo-a ou olhando de novo). A IA geométrica v0 é o lugar onde essas quatro linhas viram um único objeto que roda.

O que a brincadeira de 17/10 ensinou e a v0 incorpora: no mundo do Teste B (ruído branco, saltos grandes, olhar de graça) a melhor mente é a que não lembra; os dois experimentos registrados lá reprovaram. Uma mente só pode valer mais que um filtro num mundo onde lembrar paga: ruído com estrutura, ou olhar com custo. Os mundos de teste da v0 são esses.

## O que já existe com outros nomes, e o que seria só dela

Como mecanismo, a pilha de registros com rigidezes em escala é parente de coisas bem estabelecidas, e o projeto cita os parentes para não reinventá-los com nome bonito:

| Parente | O que compartilha com a v0 | O que a v0 faz diferente |
| --- | --- | --- |
| Média móvel exponencial em cascata; filtro de Kalman hierárquico | registro que segue o mundo com um ganho; empilhamento por escala | o ganho não é escolhido para minimizar erro; a tensão é o objeto relatado |
| Codificação preditiva (Rao–Ballard, Friston) | cada nível só passa para cima o erro de predição, que é a tensão | a v0 não infere causas latentes; declara a cegueira de cada nível como grandeza |
| Redes recorrentes multiescala; análise de componentes lentas | estados internos com constantes de tempo diferentes | as constantes são explícitas, em escada, e testadas contra o mundo (teste 4) |
| Dilema estabilidade–plasticidade (Grossberg); aprendizado contínuo | rigidez alta preserva, rigidez baixa aprende; nenhum valor fixo resolve | a identidade é definida como o andar que não cede, e o preço disso é medido |
| Modelos de volatilidade multiescala (HAR, MSM) | a escada de escalas; b ≈ 10 | a v0 é o observador, não o modelo do mundo; pergunta se a escada é do mundo ou dela |

O que seria só dela são três compromissos, juntos:

1. **A tensão é o objeto, não o erro.** O sistema existe para medir a distância entre si e o mundo por escala e relatar o que não vê. Um observador que sabe o próprio ponto cego é mais útil que um que o esconde atrás de uma previsão.
2. **Identidade como invariante com preço.** O andar de baixo é o vinco; a sua lentidão é o que o torna identidade e o que o torna cego. O sistema declara o preço em vez de fingir que não paga.
3. **Reobservar versus lembrar como decisão.** O único ato do observador é escolher quando olhar o mundo e quando confiar na memória, com um custo por olhada. Um filtro recebe todas as observações; uma mente decide quais vale pagar.

E um compromisso de método, que é o que mais falta nos parentes: cada afirmação sobre a v0 nasce de um teste com critério escrito antes e nulo ao lado, e "parece inteligente" não é critério.

## A arquitetura v0

**Entrada.** Um fluxo x\_t ∈ ℝ^d (qualquer: um alvo num plano, um sensor, o cubo do SGV, um embedding de texto). A v0 não sabe o que x é.

**Registros.** k andares R₁ … R\_k, cada um um vetor em ℝ^d. O andar 1 segue o mundo; o andar j segue o andar j − 1:

```latex
R_{1,t} = R_{1,t-1} + \lambda_1 \,(x_t - R_{1,t-1}), \qquad R_{j,t} = R_{j,t-1} + \lambda_j \,(R_{j-1,t} - R_{j,t-1})
```

com ganhos em escada geométrica, λ\_j = λ₁ / b^{,j−1}. Constantes de tempo τ\_j ≈ 1/λ\_j. Valores de partida herdados de março e do MSM: λ₁ = 0,15, b = 10, k = 4 (τ ≈ 7, 67, 670 e 6.700 passos; no BTC de 1 min, 7 min, 1,1 h, 11 h, 4,6 dias). O andar k é a identidade.

**Tensões.** T\_{0,t} = ‖x\_t − R\_{1,t−1}‖ (o mundo contra a memória mais rápida) e T\_{j,t} = ‖R\_{j,t} − R\_{j+1,t}‖ (cada andar contra o seguinte). O vetor (T₀, …, T\_{k−1}) é o estado interno relatado. No cubo do SGV, T₀ é a extremidade; T\_{k−1} é o vinco.

**Régua.** Cada tensão é lida numa régua fixada num período de calibração (mediana e quantil 99,5 ÷ 3, como a régua de maio), nunca contra a própria EMA. Regime por andar: núcleo (< 1), transição (1–3), ruptura (≥ 3), com histerese de 3 passos. A mente de março media surpresa contra si mesma; a v0 mede contra a régua.

**Cegueira declarada.** Para cada andar, a v0 publica a sua frequência de corte f\_j = λ\_j / 2π e a fração da potência da tensão T\_{j−1} que está acima de f\_j: o que o andar j não consegue representar. Isso é o Paper A como saída do sistema, não como comentário.

**Olhar ou lembrar.** A única ação: a cada passo a v0 decide observar x\_t (custo c) ou não. Quando não observa, o andar 1 não recebe x\_t e os demais seguem o andar 1 como antes. Política v0: observa se a última tensão T₀ lida está acima de θ na régua ou se passaram mais de n\_max passos sem olhar. θ e n\_max são parâmetros do teste 2, fixados antes de rodar. Um filtro olha sempre; é o nulo.

**O que ela relata, por passo:** os k registros, as k tensões na régua, o regime por andar, a cegueira por andar, e se olhou ou não. Nada de previsão, nada de direção.

**O que ela não tem na v0, de propósito:** aprendizado dos ganhos (só no teste 4, como pergunta), modelo do mundo, ação sobre o mundo, múltiplos observadores. Cada uma dessas coisas é uma versão futura com predição própria.

## O que a distingue de um filtro: quatro testes registrados

Todos em mundos sintéticos onde lembrar pode valer alguma coisa, com 100 sementes, envelope mínimo–máximo do nulo, um julgamento por teste. Só depois de os quatro serem julgados o BTC volta, como um mundo entre vários. As probabilidades são apostas de Claude, escritas antes de qualquer código.

| # | Mundo | Pergunta | Critério registrado | Nulo | Aposta |
| --- | --- | --- | --- | --- | --- |
| 1 | **Deriva:** o campo anda com ruído correlacionado (AR(1) com φ ∈ {0; 0,5; 0,9; 0,99}), sem saltos | A pilha de k registros rastreia o campo melhor que o melhor registro único? | Erro de rastreamento da v0 (k = 4, ganhos fixos) menor que o do melhor λ único varrido na grade, **e** a vantagem cresce com φ (monotônica em 4 pontos) | ruído branco (φ = 0): a vantagem deve ser nula dentro do envelope | 55 % |
| 2 | **Custo de olhar:** mundo 1 com φ = 0,9, cada observação custa c; orçamento de olhadas | A política "olha quando a tensão passa de θ" rastreia tão bem quanto olhar sempre, com menos olhadas? | Para a mesma fração de olhadas (25 %), erro da v0 menor que o da política periódica (olhar a cada 4 passos), fora do envelope | olhar sempre (teto) e olhar periódico (nulo justo) | 60 % |
| 3 | **Salto sobre deriva:** mundo 1 com φ = 0,9 mais teleportes raros (geométricos, média 200 passos) | O regime na régua detecta o salto antes e com menos falsos alarmes que o regime relativo da mente de março? | Atraso mediano de detecção menor **e** taxa de falsos alarmes por 1.000 passos menor, os dois fora do envelope | o detector relativo (E\_norm contra a própria EMA, histerese 3) | 70 % |
| 4 | **Escada livre:** mundos com escadas conhecidas (ruído = soma de 2, 3 ou 4 processos AR(1) com constantes de tempo em razão 10) e um mundo com uma escala só (um ciclo senoidal forte) | Deixando os λ\_j livres (ajuste por mínimos quadrados do erro de rastreamento), a v0 reencontra a escada do mundo? E num mundo com escala própria, aceita um andar fora do passo? | Nos mundos em escada, os λ\_j ajustados recuperam as razões em ±30 % em ≥ 80 das 100 sementes; no mundo cíclico, um λ\_j fica fora da progressão geométrica em ≥ 80 sementes | escada fixa b = 10 (deve perder no mundo cíclico e empatar nos outros) | 50 % |

**O que cada resultado fecha.** Se o 1 reprovar, a pilha não acrescenta nada a um registro bem escolhido, e a v0 é um filtro com andares decorativos. Se o 2 reprovar, a tensão não serve para decidir quando olhar, e o único ato da mente não vale o nome. Se o 3 reprovar, a lição do cubo (régua, não passado) não generaliza. Se o 4 reprovar, a escada é do modelo, não do mundo, e a auto-similaridade da v0 é projeção. Os quatro passando: a v0 é um observador, não um filtro, dentro dos mundos testados, e ganha o direito de olhar o BTC e os outros fluxos.

**O que não conta.** Parecer inteligente num plano. Rastrear bem um mundo em que copiar o campo é ótimo (lição de 17/10). Um teste passar em um mundo só. Qualquer ajuste de θ, b, k ou da sigmoide depois de ver o resultado: se o parâmetro estava mal posto, o resultado diz isso e fica.

## A auto-similaridade: a mente como samambaia, o colapso como diagnóstico

A auto-similaridade entra em três lugares.

**Na arquitetura.** Cada andar é o mesmo objeto que o andar de baixo, aplicado ao que o de baixo deixou passar. Com ganhos em progressão geométrica, a pilha é auto-similar por construção: olhar o andar 2 contra o 3 é a mesma figura que olhar o 1 contra o 2, mudada de escala. É um fractal exato e finito, de k iterações; b define o que a mente considera "a mesma coisa em outra escala".

**No que ela vê.** A pergunta do colapso (reescalada, a tensão de um andar tem a forma da do seguinte?) vira um instrumento geral. Num mundo auto-similar as tensões colapsam umas sobre as outras andar a andar; num mundo com uma escala própria o colapso quebra num andar específico, e esse andar é a assinatura da escala do mundo. No BTC foi assim: colapso no corpo (C ≈ 0,9 em 1, 5 e 15 min) e uma borda que é objeto de 1 minuto. A v0 publica, por par de andares, o seu C, e **onde o colapso quebra** é saída do sistema. Medida registrada: C\_j = 1 − (dispersão da tensão T\_j padronizada pela escala do andar j+1) / (dispersão bruta), com o mesmo nulo das rodadas do SGV.

**No seu limite.** Uma mente auto-similar só vê auto-similaridade: com a escada fixa, qualquer desvio do mundo em relação a uma progressão geométrica aparece como anomalia, não como propriedade; a mente projeta a própria samambaia na tempestade. Foi o que o MSM mostrou por dentro (o b único impôs a regularidade ×10). Por isso o teste 4 existe: deixar a escada livre e perguntar ao mundo. A cegueira espectral, aqui, não é só "até que frequência"; é "em que organização de escalas". A v0 declara as duas.

Frase para o livro: a mente é a samambaia, o mundo é a tempestade, e o que se mede é o desencontro. Onde a tempestade tem andares de verdade, a samambaia os reencontra; onde ela tem uma escala só sua, a samambaia fica cega, e a cegueira tem lugar marcado.

## Regras da casa aplicadas a este projeto

1. **Nenhuma vitória não conquistada será anunciada.** Toda afirmação sobre a v0 nasce de um teste com critério escrito antes dos dados e nulo ao lado; "parece inteligente" não é critério.
2. **Um julgamento por teste.** Emendas só para defeito de instrumento ou de mundo, registradas antes de rodar de novo, com a cláusula de última emenda. A brincadeira de 17/10 (`exploracao/mente-geometrica`) é o precedente: reprovou, ficou reprovada, ensinou.
3. **Apostas antes, erros depois.** As probabilidades da tabela ficam; os erros de aposta se contam e se publicam.
4. **O nulo manda.** Em cada teste, o adversario é o melhor filtro justo (o melhor ganho único, a política que olha sempre, o detector relativo, a escada fixa), não um boneco de palha.
5. **Nada de mercado até os quatro testes serem julgados.** O BTC volta como um mundo entre vários, e outubro e novembro de 2026 continuam reservados para o SGV.
6. **Tudo no repositório próprio**, separado do SGV, com predição, instrumento, resultados e leitura por teste, e este documento como registro de origem.

## Calendário e escopo

| Etapa | O que | Quando |
| --- | --- | --- |
| 0 | Este documento e o repositório `ia-geometrica` com o registro de origem | 17/10/2026 |
| 1 | Instrumento v0 (registros, régua, cegueira, política de olhar) e os quatro mundos, com fumaça | quando a Ana pedir |
| 2 | Testes 1 a 4, um por rodada, cada um com predição própria detalhando os parâmetros desta tabela | 17–18/10/2026: quatro reprovados (LEITURA_teste1–4.md) |
| 3 | Leitura consolidada: a v0 é observador ou filtro, dentro dos mundos testados | 18/10/2026: filtro (LEITURA_v0.md) |
| 4 | Fluxos reais (BTC entre eles, depois de 3/11 e 1/12), com a escada livre do teste 4 | depois da etapa 3 |

**Fora do escopo da v0:** modelo do mundo, ação sobre o mundo, aprendizado além dos ganhos, múltiplos observadores, qualquer uso em trading. Cada um desses é uma versão futura com predição própria.

**Itens abertos declarados:** a política de olhar da v0 é a mais simples possível (limiar na tensão mais um teto de passos); o teste 4 ajusta ganhos por mínimos quadrados, que não é aprendizado online; a medida de cegueira usa a frequência de corte de um filtro de primeira ordem, aproximação declarada.
