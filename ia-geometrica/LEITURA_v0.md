# IA geométrica v0: leitura consolidada (etapa 3)

18/10/2026 · depois dos quatro testes · nenhuma emenda em nenhum deles

## O veredito do projeto, como foi escrito em 17/10

"Os quatro passando: a v0 é um observador, não um filtro, dentro dos mundos testados." Os quatro reprovaram. **Dentro dos mundos testados, a v0 como está é um filtro com andares decorativos, uma política de olhar que não vale o nome, uma régua que não grita e não vê, e uma escada que é dela e não do mundo.** Esta frase fica, sem atenuante, porque é o que os critérios escritos antes disseram.

| # | teste | aposta (projeto → predição) | resultado | o que decidiu |
|---|---|---|---|---|
| 1 | deriva | 55 % → 55 % | reprovado | λ₁ = 0,15 é cego à escala de um passo; o mundo só tem essa |
| 2 | custo de olhar | 60 % → 35 % | reprovado (V −1,9 %) | a política dorme cega; não tem expectativa de tensão |
| 3 | salto | 70 % → 70 % | reprovado | régua calibrada com os saltos dentro: silêncio quase perfeito, 20 % de detecção |
| 4 | escada livre | 50 % → 25 % | reprovado (a); (b) passou | ajuste por predição põe λ₁ ≈ 1 e espalha o resto; no cíclico a v0 sabe que não há escada |

Apostas do projeto: 0 de 4 acertos de passagem. Apostas das predições, refeitas antes de cada rodada: 3 de 4 previram a reprovação. A diferença entre as duas colunas é o que os testes anteriores ensinaram a cada predição seguinte, e fica registrada.

## O que os quatro, juntos, dizem

Três lições se repetem em testes diferentes, e isso é mais informativo do que qualquer reprovação isolada.

1. **Copiar o mundo ganha de lembrar, em todo mundo onde olhar é de graça.** Testes de 17/10, teste 1, teste 4: sempre que os ganhos ficam livres, o andar rápido vai a λ ≈ 1. Uma memória só vale alguma coisa se olhar custa (teste 2) ou se o mundo tem estrutura que um passo não contém. O v0 testou o custo com uma política de reflexo e perdeu por 2 %; não testou ainda uma política de expectativa.

2. **A régua fixa é uma escolha sobre o que conta como raro, não um detector.** No BTC ela definiu a borda; no teste 3 ela definiu que só os maiores saltos são saltos. Herdar a régua de maio sem herdar a pergunta de maio foi o erro.

3. **A escada b = 10 é projeção da mente.** Em 400 rodadas a escada livre ganhou da fixa; nos mundos com escada, o ajuste não a reencontrou; no mundo sem escada, a v0 soube. O que a v0 ainda não tem é um critério, que não seja predição, para perguntar ao mundo onde estão as suas escalas. O compromisso 1 do projeto (a tensão é o objeto) foi escrito e não foi usado no teste 4.

## O que não foi refutado

Nenhum dos quatro testes refuta a ideia que justifica o projeto: um observador com cegueira declarada usado como régua sobre outros observadores. Os quatro testes mediram se a v0 **rastreia, decide, detecta e ajusta** melhor que um filtro; nenhum mediu se o que ela declara sobre a própria cegueira é verdadeiro e útil. Isso não é consolo; é escopo: o projeto de 17/10 testou a v0 como máquina e não como instrumento, e a leitura da conversa de 18/10 (sentinela versus régua de cegueira) chegou depois de os testes estarem escritos.

## Os dez defeitos, agrupados

- **Herança sem pergunta:** λ₁ = 0,15 (1), b = 10 (3, 9), régua de maio (6).
- **Mundos mal postos:** uma escala só (2), saltos menores que o ruído (7).
- **Política sem expectativa:** decide pela última tensão vista (4); afinação discreta (5).
- **Instrumento:** leitura sem regularização (3, tratado no teste 4), critério sem desconto pelo acaso (8), parametrização sem faixa (10).

## O que vem depois, se vier

Uma v0.1 só faz sentido se mudar de pergunta, não só de parâmetros. Três candidatas, cada uma com predição própria antes de qualquer código, uma por vez, quando a Ana pedir:

- **A régua de cegueira:** um teste em que a v0 declara, por andar, a fração do mundo que não vê, e se mede se essa declaração é **verdadeira** (contra a cegueira real, calculável em mundo sintético) e **útil** (um leitor que a recebe erra menos do que um que não recebe). É o teste que o OBS-01 precisa e que o v0 não fez.
- **Política de expectativa:** olhar quando a tensão **esperada** desde a última olhada passa de θ, com a taxa de crescimento aprendida do próprio mundo (linha "reobservar versus lembrar"). Nulo: periódico, o mesmo do teste 2.
- **Escada pela tensão:** ajustar os andares para que as tensões entre andares sejam o mais independentes possível (ou para que o colapso C_j quebre onde o mundo tem escala), e medir se isso reencontra τ_j onde o teste 4 não reencontrou.

A regra 5 do projeto fica: nada de mercado até os testes serem julgados; foram julgados, e a v0 não ganhou o direito de olhar o BTC. Outubro e novembro continuam do SGV.

## Adendo de 18/10, depois do teste 5

A primeira candidata ("a régua de cegueira") foi desenhada, rodada e reprovada nas duas hipóteses (LEITURA_teste5.md): a declaração de cegueira da v0 é calculada sobre o resíduo do próprio andar e por isso declara escuridão em toda parte (ρ com a cegueira real: 0,16 / 0,34 / 0,75 / indefinido); e a reescala do leitor explode onde os pesos têm sinais mistos. Dois requisitos nasceram com número e valem para qualquer observador, inclusive o do OBS-01: a cegueira se mede sobre a **entrada** do registro, não sobre o seu erro, e em prazo maior que a constante de tempo do registro medido. Cinco testes, cinco reprovações, treze defeitos nomeados. Candidatas restantes: a declaração linear (sobre R_{j−1}), a política de expectativa, a escada pela tensão. Cada uma com predição própria, quando a Ana pedir.

## Adendo de 18/10, depois dos testes 6, 7 e 8

As três candidatas rodaram, uma por vez, cada uma com predição antes. Nenhuma passou no critério; duas mudaram o que se sabe.

- **6, declaração linear** (LEITURA_teste6.md): medir a cegueira sobre a entrada do andar levou ρ de 0,16 para **0,99** no andar 1 e para 0,87 no andar 3. Os andares 2 e 4 reprovaram por causas nomeadas antes: corte abrupto onde o filtro é suave (declara 0,999 onde a verdade é 0,77), e um mundo sem nada mais lento que a identidade (nada a correlacionar).
- **7, política de expectativa** (LEITURA_teste7.md): empate (+0,13 %). Num AR(1) a última tensão deixa de informar em cinco passos e a política vira periódica com outro nome. O mundo não tem momento certo de olhar; a política só pode valer num mundo com regimes.
- **8, escada pela tensão** (LEITURA_teste8.md): pela primeira vez os andares caíram nas constantes de tempo do mundo (λ·τ de 0,7 a 2,9, contra 7 e 0,0004 no teste 4), e no mundo sem escada a v0 soube e ganhou da fixa. Mas a razão lida é ≈ 5 para um mundo 10: as fatias de primeira ordem vazam para as vizinhas e os cortes se aproximam.

**O que os oito dizem juntos.** A v0 como filtro perde de qualquer filtro bem escolhido (1–4). A v0 como **instrumento** tem duas propriedades que já se sustentam com número e uma que não: ela lê a cegueira real quando declara sobre a entrada (6), e lê a escala do mundo quando ajusta pela tensão (8); não tem política de olhar que valha num mundo sem regimes (2, 7). Os dois defeitos que restam nas propriedades boas (14 e 18) têm a mesma raiz, o corte suave do filtro de primeira ordem, e um conserto só: declarar e pesar com o **ganho real** do andar, |H_j(f)|², em vez de um corte. Esse é o próximo teste, com predição própria, quando a Ana pedir; depois dele, um mundo com regimes para a política (7b) e um mundo com algo mais lento que a identidade para o andar 4 (6b).

Oito testes, oito reprovações, dezoito defeitos nomeados. Nenhuma emenda. Nada de mercado.

## Adendo de 18/10, depois dos testes 9 e 10

- **9, declaração com ganho real** (LEITURA_teste9.md): andares 1–3 passam com ρ 0,997 · 0,986 · 0,923 em cinco mundos; o andar 4 declara certo no único mundo mais lento que ele (0,51 contra 0,60) e o Spearman dilui nos outros quatro. A régua de cegueira, no sintético, ficou escrita com número: espectro da entrada, pesado por (1 − ganho real), em série mais longa que o registro, composta andar a andar quando se quer a cegueira sobre o mundo.
- **10, expectativa num mundo com regimes** (LEITURA_teste10.md): a tensão informa o regime por 16 passos (b_n ≈ 0,65) e a política de limiar perde mesmo assim, porque concentra olhadas em rajada onde um registro lento não as aproveita. A grandeza certa é o ritmo por regime, não o instante.

Dez testes, dez reprovações, vinte e dois defeitos. Próximos, cada um com predição própria quando a Ana pedir: ritmo por regime (política), andar 4 com maioria de mundos lentos (declaração), declaração composta contra β no valor, e andares de corte mais abrupto para a escada pela tensão.

## Adendo de 18/10, depois dos testes 11 e 12

- **11, ritmo por regime** (LEITURA_teste11.md): primeira política com V > 0 na média (+0,67 %); a forma é a certa (ritmo, não instante) e o registro herdado (λ₁ = 0,15) a segura.
- **12, ritmo com λ₁ do mundo** (LEITURA_teste12.md): λ₁ → 0,94 e V +1,19 %, metade de um teto analítico de ≈ 5 % que a própria estrutura do mundo impõe: numa deriva, o erro de não olhar cresce como raiz, e saber o momento certo vale pouco por construção. Fecha a família "deriva" para a política: cinco testes (2, 7, 10, 11, 12), nunca acima de 1,2 %. O ato da v0 só pode valer em mundos onde não olhar custa de uma vez (saltos).

Doze testes, doze reprovações, vinte e quatro defeitos. O próximo da política é o mundo de saltos, com a régua como gatilho; os próximos da declaração e da escada seguem como no adendo anterior.

## Adendo de 18/10, depois do teste 13

- **13, saltos em cachos** (LEITURA_teste13.md): reprovado e inconclusivo. O mundo tinha um cacho por janela de afinação e o oráculo (que sabe o cacho) ficou instável (envelope −31 % a +37 %); sem teto medido, o teste não responde sobre a política. Na única semente em que o oráculo foi alto e a afinação acertou, a v0 capturou um quarto do ganho com a régua como gatilho. Defeito 25: o teto tem de ser calculado por janela. Próximo: o mesmo mundo com cachos a cada ≈ 400 passos.

Treze testes, treze reprovações, vinte e cinco defeitos.

## Adendo de 18/10, depois do teste 14

- **14, cachos densos** (LEITURA_teste14.md): o mundo saiu como a conta por janela previu e o teto não: o oráculo que sabe o cacho rende +1,2 %, a v0 +1,3 %. Um salto custa alguns passos uma vez; a deriva custa todo passo; o custo de salto é 8 % do erro e a melhor política poupa um quarto disso. Acima de tudo: com 25 % de olhadas o periódico já erra só 50 % mais que olhar sempre, e a política disputa uma fração pequena disso. **Nos mundos testados e nesse orçamento, saber quando olhar vale 1 %.** A linha de política fecha, salvo um último teste com orçamento de 5 %.

Catorze testes, catorze reprovações, vinte e seis defeitos. Restam: política com orçamento de 5 % (último da linha); andar 4 com maioria de mundos lentos; declaração composta contra β no valor; escada pela tensão com andares de corte abrupto.

## Adendo de 18/10, depois do teste 15: a linha de política fecha

- **15, orçamento de 5 %** (LEITURA_teste15.md): o oráculo que sabe o cacho rende +1,8 % e escolhe olhar quase em ritmo fixo; a v0 empata (+1,8 %). Pela cláusula escrita na predição (oráculo < 5 %), **a linha de política está fechada**: oito testes, quatro mundos, dois orçamentos, dois registros, quatro formas; sempre 0–2 %, e o oráculo igual. Para um observador que só olha e lembra, quando olhar quase não importa; com que rigidez lembrar e o que declarar sobre o que não vê importam. A distinção entre a v0 e um filtro está na declaração, não no ato (defeito 27).

Quinze testes, quinze reprovações, vinte e sete defeitos. Restam, na linha da declaração e da escada: andar 4 com maioria de mundos lentos; declaração composta contra β no valor; escada pela tensão com andares de corte abrupto.

## Adendo de 18/10, depois dos testes 16 e 17: as duas primeiras passagens

- **16, o andar da identidade** (LEITURA_teste16_17.md): com três mundos em cinco mais lentos que a identidade, a declaração do andar 4 acompanha a cegueira real (ρ 0,746, critério 0,7). **Passou.**
- **17, a declaração composta**: composta por produto andar a andar, a declaração acerta a cegueira real no valor: erro mediano 0,020 · 0,007 · 0,006 nos andares 1–3 (critério 0,05), e 0,023 no 4. **Passou.** A composição não é aproximação; é a definição exata para a cascata.

Estado das três linhas depois de dezessete julgamentos: **declaração de cegueira: de pé, nos quatro andares, na ordem e no valor, em cinco mundos sintéticos** (regra: espectro da entrada, pesado por 1 − ganho real, série mais longa que o registro, composta por produto). **Escala pela tensão: de pé na escala (λ·τ ≈ 1), razão comprimida (≈ 5 para 10); pendente o andar de corte abrupto.** **Política de olhar: fechada por cláusula (≤ 2 % em todo mundo de observação pura).**

O próximo passo que importa é o primeiro fora do sintético puro: a v0 como régua **sobre outro observador**, cujos ganhos ela não conhece. Predição própria, quando a Ana pedir.

## Adendo de 18/10, depois do teste 18

- **18, a régua sobre outro observador** (LEITURA_teste18.md): vendo entrada e saída de um registro de forma desconhecida (EMA rápida, média, lenta; cascata de segunda ordem; média móvel; EMA com ruído na saída), a v0 acha o corte em 600 de 600 casos (erro < 1 % em cinco, 28 % no mais lento, por resolução). Reprovado na cegueira por definição, não por estimativa: a v0 declara o que a saída **não contém** (1 − |H|²) e o teste mediu o que a saída **não reproduz** (|1 − H|²); para todo observador que atrasa as duas diferem, e a diferença é o atraso. Quinta cláusula para o OBS-01: cegueira e erro são grandezas diferentes; declarar as duas, com nome. Correção de registro: a mensagem do commit 395eff0→seguinte afirmou uma verificação que falhou (os mundos por lfilter diferem no primeiro passo dos do laço; resultados iguais nas casas impressas).

Dezoito testes, dezesseis reprovações, duas passagens, trinta defeitos.

## Adendo de 18/10, depois do teste 19

- **19, não ver e errar** (LEITURA_teste19.md): do mesmo Ĥ complexo a régua declara "não ver" (exato: erro ≤ 0,001 nos doze pares) e "errar" (≤ 0,056; reprovou por 0,006 no Ω mais lento, por resolução nas bolhas mais baixas). O sinal de ε − ν diz a ordem do observador (negativo na primeira ordem, positivo em cascata e janela), observação não prevista. Cláusulas 1–5 do OBS-01 todas com número.

Dezenove testes, dezessete reprovações, duas passagens, trinta e um defeitos.

## Adendo de 18/10, depois do teste 20

- **20, andares de segunda ordem** (LEITURA_teste20.md): a razão lida subiu de 4,9 para 5,8 na escada-3 e piorou na escada-4 e na escada-2 (mínimos múltiplos); o primeiro andar continua no corte do mundo (λ₁·τ₁ 0,8–1,1). A ordem não era a causa toda: o critério de partes iguais também comprime (defeito 32). Último da linha: descorrelação entre fatias; se não ler a razão, a v0 fica com a escala e sem a razão.

Vinte testes, dezoito reprovações, duas passagens, trinta e dois defeitos.
