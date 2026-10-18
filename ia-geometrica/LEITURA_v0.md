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
