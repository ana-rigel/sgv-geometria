# Manual do painel SGV: as quatro métricas

16/10/2026 · Ana Rigel · fonte: Claude Doc "Manual do painel SGV: as quatro métricas"

## Leitura em 30 segundos

O painel responde quatro perguntas, nesta ordem: **onde** o minuto está no cubo (ext), **quão quente** o mercado está (w), se a **borda** se comporta como o núcleo (R) e se o cubo inteiro é **um só objeto** visto em tamanhos diferentes (C). As duas primeiras são do minuto; as duas últimas são da janela.

| Métrica | Rótulo no painel | Pergunta que responde | De onde vem | Faixa normal (BTC, jun–set) |
| --- | --- | --- | --- | --- |
| ext | "extremidade do minuto" (1º quadro) | Este minuto é comum ou extremo? | o maior dos três eixos do cubo, em valor absoluto | abaixo de 1: núcleo · 3 a 10: borda |
| w | "σ̂ na régua (log)" (2º quadro) | O mercado está frio ou quente? | log da volatilidade estimada (σ̂), na mesma régua | tercis de maio: frio / morno / quente |
| R | "borda/núcleo R da janela" (4º quadro) | A borda tem dinâmica própria? | campo D na borda dividido pelo campo D no núcleo | perto de 1; muito acima de 1 é sinal |
| C | "colapso C das cascas" (5º quadro) | O cubo quente é o cubo frio ampliado? | 1 menos o tamanho padronizado sobre o bruto | acima de 0,7 (a linha tracejada do gráfico) |

Regra prática: ext e w você lê a cada minuto e esquece; R e C você lê uma vez por janela e guarda. O painel é um instrumento de observação, não de previsão: nenhuma das quatro diz para onde o preço vai.

## ext: onde o minuto está no cubo

ext é a distância do minuto ao centro do cubo, medida pelo eixo que mais se afastou. O cubo tem três eixos (energia dos retornos, jerk e fluxo de memória), cada um numa régua em que 0 é a mediana de maio e 3 é a cauda de maio (o quantil 99,5%). ext é o maior dos três valores absolutos.

Como ler:

- **ext abaixo de 1**: núcleo. O minuto é comum em todos os eixos. É onde o BTC passa a maior parte do tempo; a nuvem densa do centro é isso.
- **ext entre 1 e 3**: transição. Algum eixo saiu do comum, mas ainda dentro do que maio já mostrava.
- **ext entre 3 e 10**: borda. Pelo menos um eixo passou da cauda de maio. São os minutos que o H-TEMPO-01b olha (reverte ou não?).
- **ext acima de 10**: fora da escala. Raro; quase sempre um salto de preço. Na régua de maio, 10 é três vezes a cauda.

O que não confundir: ext diz o tamanho do desvio, não qual eixo o causou. Para saber o eixo, olhe a posição do ponto no cubo (a cor por eixo ajuda). E ext alto não significa mercado quente: um minuto de ext 5 num dia frio é uma surpresa; num dia quente, é rotina. Por isso ext só se interpreta junto de w.

## w: a temperatura, quarta coordenada

w é o logaritmo da volatilidade estimada (σ̂, pelo estimador HAR) posto na mesma régua dos outros eixos: 0 é a volatilidade mediana de maio, valores positivos são mercado mais quente que o típico de maio, negativos mais frio. É a quarta dimensão do hipercubo: o cubo inteiro incha quando w sobe e encolhe quando w desce.

Como ler:

- **w negativo** (tercil frio de maio): mercado calmo. Os pontos ficam colados ao centro; ext raramente passa de 2.
- **w perto de 0** (tercil morno): o regime de referência. A casca HDR50 tem o tamanho "normal".
- **w positivo** (tercil quente): mercado agitado. A nuvem se abre, a borda enche, ext 3 vira comum.

w muda devagar. Pelo v3 da memória, a temperatura tem duas escalas: uma de dezenas de minutos (10–50 min) e uma de dias (1–3 dias). Se w está alto agora, a aposta mais segura é que continua alto no próximo minuto, e provavelmente na próxima hora. É a única coisa que o painel "prevê": tamanho, nunca sinal.

O que não confundir: w é lido no minuto, mas descreve o entorno (os últimos minutos, hora e dia que o HAR combina). Um minuto isolado de salto sobe ext, não w; w só sobe se o salto vier acompanhado. Nas ferramentas tradicionais a temperatura fica "compactada" porque é tratada como escala e descartada; no hipercubo ela é um eixo, por isso dá para ver o cubo quente e o cubo frio lado a lado.

## R: a borda tem vida própria?

R compara o campo D na borda com o campo D no núcleo: mediana de D nos minutos com ext entre 3 e 10, dividida pela mediana de D nos minutos com ext abaixo de 1. D é o campo local (ajuste linear por vizinhança, treinado na semana anterior) que mede quanto o próximo passo se afasta do que a vizinhança previa. R perto de 1 diz que a borda obedece à mesma regra do núcleo; R bem maior diz que a borda tem dinâmica própria.

Como ler:

- **R entre 1 e 3**: borda contínua com o núcleo. O que acontece nos extremos é o que acontece no centro, só mais longe.
- **R entre 3 e 10**: borda mais "viva". O campo responde diferente nos extremos; vale olhar a cor por eixo para ver qual.
- **R acima de 10**: a borda não se parece com o núcleo. Nos sintéticos M isso apareceu (12–15 em ago–set a 1 min) e foi registrado como instabilidade do instrumento, não como achado. No BTC real, R alto numa janela pequena quase sempre é pouca amostra na borda; veja n antes de acreditar.

R é uma medida de janela: precisa de minutos suficientes na borda (o painel exige pelo menos 30 na borda e 30 no núcleo; abaixo disso mostra só a contagem de extremos no lugar do número) para a mediana valer alguma coisa. Com janela de 1 hora em dia frio, R é ruído; com janela de 1 dia ou 1 semana, é leitura. A tabela "medido" mostra o R das rodadas registradas (jun–jul e ago–set, por resolução); a linha da resolução atual fica marcada para você comparar a janela de agora com o que já foi medido.

O que não confundir: R não é "quanto a borda reverte". A reversão (o bounce do cubo de 15 min) é o H-TEMPO-01b e se mede pelo sinal do próximo retorno, não pelo campo. R diz se a borda é outro objeto; a reversão diz o que ela faz.

## C: o colapso, o cubo é um só objeto?

C mede quanto da abertura da nuvem é explicada só pela temperatura. O painel calcula a dispersão da nuvem duas vezes: bruta e depois com cada minuto dividido pelo seu σ̂. C é 1 menos a razão entre as duas. É assim nas rodadas registradas. O painel usa uma versão própria, por isso o rótulo diz "das cascas (versão de painel)": ele compara o tamanho da casca HDR50 entre as fatias calma, média e quente, em unidades de σ̂ e em unidades brutas, e C é 1 menos a razão. Os dois medem a mesma ideia; os números não são idênticos, e a tabela "medido" mostra o das rodadas para comparação. Se C é 0,9, dividir pela temperatura tirou 90% da abertura: o cubo quente é o cubo frio ampliado, e o botão "unidades de σ̂" mostra isso ao vivo, a casca encolhendo para o tamanho da calma.

Como ler:

- **C acima de 0,7**: colapso vale. Um único objeto em escalas diferentes. Foi o que o BTC mostrou em jun–jul e ago–set, nas três resoluções (1, 5 e 15 min), com C em torno de 0,9.
- **C entre 0,5 e 0,7**: colapso parcial. A temperatura explica a maior parte, mas sobra forma. Vale perguntar qual eixo não encolheu.
- **C abaixo de 0,5**: a forma mudou, não só o tamanho. É o que seria visível "de fora": minutos quentes com cara própria. Nunca apareceu numa janela de semana; se aparecer, é o evento mais interessante que o painel pode mostrar, e vira hipótese antes de virar afirmação.

C também é de janela e também precisa de amostra: numa hora fria quase toda a nuvem é núcleo e C fica instável. Leia com 1 dia ou 1 semana. O gráfico de C ao longo do período, com o losango da janela atual, é o jeito mais rápido de ver se a janela de hoje é típica ou não.

O que não confundir: "colapso" aqui não é queda de preço. É colapso no sentido de curvas que caem umas sobre as outras quando se reescala (invariância de escala). O nome colide com o SGV original, onde colapso era evento de preço; se isso atrapalhar, o rótulo do painel pode virar "invariância de escala C" sem mudar nada no cálculo. E C alto não é notícia boa nem ruim para operar: diz que não há forma nova para explorar, só tamanho, e tamanho se mede com σ̂.

## As quatro juntas: cenários que você vai ver

Sozinha, nenhuma das quatro conta a história; a leitura está na combinação. Os cenários abaixo são os que apareceram no replay de maio a setembro.

| Cenário | ext | w | R | C | O que está acontecendo |
| --- | --- | --- | --- | --- | --- |
| Rotina fria | < 1 | negativo | 1–3 | > 0,7 | Mercado calmo, nuvem no centro. Nada a fazer além de observar. |
| Rotina quente | 1–5 | positivo | 1–3 | > 0,7 | Mercado agitado, mas o mesmo objeto ampliado. Candles maiores, forma igual. |
| Salto em dia frio | > 5 | negativo | sobe na hora | cai na hora | Um evento isolado (notícia, liquidação). ext sobe, w ainda não. Espere a hora fechar antes de ler R e C. |
| Aquecimento | 1–3 crescendo | subindo | 1–3 | > 0,7 | A temperatura está virando. Pelo v3, tende a durar dezenas de minutos ou dias. |
| Borda viva | 3–10 frequente | positivo | > 3 com amostra | > 0,7 | A borda responde diferente do núcleo, mas o tamanho ainda explica a abertura. É o caso que o H-4D-01 e o H-TEMPO-01b julgam em outubro. |
| Quebra de forma | qualquer | qualquer | qualquer | < 0,5 numa semana | Nunca visto. Se aparecer: anote a janela, não conclua, e pré-registre antes de olhar de novo. |

Duas regras de olhar:

1. Leia na ordem w, ext, C, R. Primeiro a temperatura, porque ela diz quanto de ext é esperado; depois C, porque ele diz se a temperatura basta; R por último, porque é o mais sensível à amostra.
2. Troque a resolução antes de acreditar. O colapso vale igual em 1, 5 e 15 min; a borda é um objeto de 1 minuto (nos cubos de 5 e 15 ela quase some). Se algo aparece numa resolução e desaparece nas outras, é pista sobre a escala do fenômeno, não erro.

## O que o painel não diz (e por quê)

O painel não diz direção. Oito testes de direção (H-DIF, H-DIR e réplicas) não passaram e a fila de 2/09 não achou vantagem explorável em 1 minuto. Se um dia o cubo parecer "apontar" para cima ou para baixo, isso é o cérebro completando padrão, não o instrumento.

O painel não diz o preço do próximo minuto. Ele diz o tamanho esperado do movimento, porque w tem memória; o sinal é moeda ao ar.

O painel não mostra outubro. Outubro está reservado até 3/11 para o julgamento dos confirmatórios; novembro até 1/12. O serviço ao vivo só liga quando LIBERACAO.json for editado depois do julgamento. Olhar antes contaminaria o teste.

E a regra da casa vale para o que você vir nele: uma janela interessante vira hipótese registrada, com critério escrito antes dos dados, e só depois vira frase.

## Métricas de apoio, em uma linha cada

| No painel | O que é | Para que serve |
| --- | --- | --- |
| barras na janela (3º quadro) | quantos minutos (ou barras de 5/15 min) a janela contém | saber se R e C têm amostra; janela de 1 hora em dia frio quase não tem borda |
| alongamento log(λ₁/λ₃) da casca (6º quadro) | quanto a casca HDR50 é mais comprida que larga: eixo maior sobre eixo menor, em log | é o que o H-4D-01a julga em 3/11: a casca quente é mais alongada que a fria? Até lá, só observe |
| fatia | posição do corte 4D (o plano que o Miegakure mostra): calma, média, quente | olhar só os minutos de uma temperatura por vez |
| casca HDR50 | elipsoide que contém metade dos pontos da janela | o "tamanho" do cubo; é ela que encolhe em unidades de σ̂ |
| anéis | esferas de ext 1, 3 e 10 | ler ext no olho sem ir ao número |
| trajetória | os últimos minutos ligados em linha | ver o caminho, não só a posição; jerk é a curvatura dela |
| cor por eixo | qual dos três eixos domina o ponto | saber se ext veio de energia, jerk ou memória |
| medido (tabela) | R e C das rodadas registradas, por resolução, com o envelope das réplicas M | comparar a janela de agora com o que foi julgado |
| gráficos R e C | os valores das rodadas por resolução, losango na janela atual, tracejado no limiar 0,7 | ver se a janela de agora está dentro do medido |

Quando as quatro principais estiverem no olho, estas entram sozinhas. Um segundo manual, só das de apoio e dos controles, fica para depois de outubro.
