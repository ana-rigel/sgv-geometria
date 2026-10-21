# Predição do teste 54 (a sentinela sabe quando aprendeu? Instalada a frio, ela decide sozinha quando parar de ouvir o campo e não declara um ritmo que não existe)

21/10/2026 · escrita antes de rodar no dado real · instrumento da sentinela em `sentinela.py` (commitado junto com esta predição) · 6 lugares de MT · Ana Rigel

## De onde vem

Hoje, ao analisar a nota "SGV – Resultado Central 01" (memória por geometria de atrasos), três projetos da casa chegaram ao mesmo lugar: o generalista perde para o especialista no terreno dele (nota, SGV, testes 1, 28 e 30). Também ficou claro que a origem de uma memória não se identifica só observando (Proposição 3 da nota, teste 51 contra o 52, régua do OBS-01). A Ana perguntou se a IA geométrica pode ficar útil. A proposta foi uma **sentinela do sítio**.

Ao revisar o repositório antes desta predição, duas das três peças propostas já estavam julgadas:
- **o alarme:** teste 28, a v0 custou 39 % mais que o alarme de chuva e nível;
- **a cegueira antes da cheia perdida:** teste 29, AUC 0,66 contra 0,80 da subida em 6 h (defeito 40).

A terceira peça, "aprender o lugar", tem um concorrente trivial: um registrador de datas que tira a média das entradas (o relógio v1, 18,8 d) aprende o lugar, e qualquer placa sabe o ano com um relógio de tempo real.

O que só a v0 pode oferecer, e nunca foi testado, é **saber quando aprendeu**. No teste 53, quem decidiu parar de ouvir em 1/1/2018 fomos nós. Aqui, quem decide é ela, pelo próprio estado. A Ana escolheu este teste.

## O que muda em relação aos testes 52 e 53

1. **Instalada a frio, sem nada do futuro.** Nos testes 51–53, a normalização e a projeção usavam a média, o desvio e o autovetor de 2010–2017 inteiros, isto é, olhavam à frente. Aqui:
   - média e variância de cada sensor são acumuladas online (Welford);
   - o autovetor é recalculado a cada dia sobre a covariância acumulada do andar 1 (sinal fixado pela carga positiva no 1º sensor, a umidade do solo);
   - ψ começa na 1ª entrada vivida (2010) e segue o laço η = 0,3 desde então.

   Ela não recebe calendário, data de silêncio, histórico nem escala.
2. **Ela decide quando parou de aprender.** Cada andar carrega uma **declaração** (a régua do próprio andar):
   - Z_j = média exponencial de s_j e^{−iφ_j}, isto é, o que o relógio ouve na própria fase, com janela τ_j = 3 períodos naturais do andar (126 d; 3,4 anos; 34 anos; 344 anos);
   - Z_jk = o mesmo, em quatro demoduladores livres a 0,5; 0,7; 1,4 e 2,0 × ω_j: o que se ouviria se o ritmo estivesse em outro lugar;
   - Q_j = |Z_j| / √(média_k |Z_jk|²): o ritmo que ela travou contra os vizinhos que ela não travou.
3. **Régua sequencial.** Sem ritmo, Q_j² segue F(2, 8), com P(Q² > x) = (1 + x/4)^−4. Quem já viveu n_j = t/τ_j janelas paga por ter olhado n_j vezes: q*_j(t)² = 4[(α/n_j)^−1/4 − 1], com **α = 0,01**. Para o andar 2, isso dá q* = 2,9 no 1º ano de maturidade e 3,6 no 3º.
4. **Declaração.** Um andar declara "aprendi um ritmo" quando:
   - está maduro (t ≥ τ_j);
   - Q_j ≥ q*_j(t);
   - ω_j variou ≤ 5 % em um período próprio;
   - as condições acima valem sem interrupção durante um período próprio inteiro.

   Os andares 3 e 4 nunca ficam maduros em 16 anos. **Não ter vivido o bastante para saber** é uma declaração honesta por construção, e fica relatada como tal.
5. **Ao declarar, o andar para de ouvir** (s_j = 0 no relógio). É o segundo tempo do teste 53, agora com hora escolhida por ela. A partir daí, a v0 só olha o mundo uma vez por ano, na entrada das águas, para corrigir ψ.

Relógios, ε, η_w e K = 0 são os do teste 52, braço A. Os 20 inícios de fase usam a semente 51, como nos testes 52 e 53. A previsão do ano y é feita em 1/09, como no teste 53: t₀ + emb(ψ − φ₂(t₀))/ω₂(t₀), mediana dos 20 inícios. Antes da declaração, a previsão sai da fase que ainda ouve o campo (a do braço F do 53, que errou muito) e conta assim mesmo.

## Piloto sintético (rodado antes desta predição; nenhum dado real além das estatísticas da calibração)

O mundo é o do piloto do teste 52: o ano de cada andar (A_j e δ_j de Juara na calibração) mais ruído AR(1) com o desvio do resíduo, 20 mundos por condição. Foi acrescentado um ruído de memória longa (τ ≥ 365 d) para imitar secas plurianuais. Um "lugar" declara se a mediana dos 20 inícios declara.

| mundo | α | algum andar declara | andar 1 | andar 2 | andar 2 antes de 1/9/2019 | mediana da declaração do andar 2 |
|---|---|---|---|---|---|---|
| com ano | 0,01 | 100 % | 0 % | 100 % | 100 % | 4,5 anos |
| sem ano | 0,01 | **5 %** | 5 % | 0 % | 0 % | |
| sem ano, memória longa | 0,01 | **0 %** | 0 % | 0 % | 0 % | |
| com ano, memória longa | 0,01 | 100 % | 0 % | 100 % | 100 % | 4,6 anos |
| sem ano | 0,05 | 25 % | 20 % | 5 % | 5 % | |
| sem ano | 0,10 | 40 % | 35 % | 10 % | 10 % | |

**Por que α = 0,01 e não 0,05.** No piloto, a cauda real de Q ficou 4–5 vezes mais pesada que a da F(2, 8): com α = 0,05, o andar 1 declarou um ritmo inexistente em 20 % dos mundos. O motivo provável é o relógio forçado pelo ruído, que puxa a própria fase para o ruído, enquanto os demoduladores livres não. O valor de α foi fixado aqui e não muda depois.

Antes disso, uma versão com estabilidade de 2 % e q* fixo atrasava a declaração para ≈ 10 anos: o ω travado treme 2–4 %, e o andar 1 declarava ritmo inexistente em 33 % dos mundos com q* = 3. As duas coisas foram corrigidas **no sintético**, antes de qualquer dado real.

**Fumaça do encanamento online** (normalização, cascata, projeção e sentinela sobre três sensores brutos sintéticos com amplitudes arbitrárias, 4 mundos de cada):
- com ano, o andar 2 declarou em 3 de 4 mundos (7,9; 10,5; 14,8 anos);
- sem ano, nenhum andar declarou em nenhum dos 4.

Isso mostra só que o encanamento funciona. A velocidade depende da amplitude do ano no andar 2: o relógio só trava se A₂ ≳ 0,88 (teste 52), e o dado real tem A₂ ≈ 0,82–0,88, no limite.

## Conta prévia (sem rodar no dado real)

- No teste 52, com a normalização que olhava à frente, ω₂ entrou e ficou em ±5 % de Ω depois de **6,2–7,3 anos** nos seis lugares, mais devagar que no sintético (2–4 anos). Somando a régua sustentada por um período e a estabilidade, a declaração deve cair entre ≈ 7 e 10 anos depois da instalação, isto é, **perto de 1/9/2019 (9,67 anos)**. O J1 está no fio.
- A normalização online infla z no primeiro ano (desvio de meia estação), o que pode acelerar a trava. A projeção online muda o autovetor nos primeiros meses, o que pode atrasá-la. Não sei qual pesa mais.
- O nulo real tem o que o sintético não tem: secas plurianuais de verdade (2019–2025), oscilações intrassazonais e anos anômalos. Isso pode enganar o andar 1 ou o andar 2.
- **J3.** O S do teste 53 fez 21,2 d com 8 anos de calibração vista de uma vez e silêncio a partir de 2018. Aqui ψ nasce de uma entrada só e aprende sobre a fase ruidosa da escuta. Se a declaração atrasar além de 2019, as primeiras previsões saem da fase ouvindo (o braço F do 53 fez 36,5 d). Espero algo entre 20 e 28 dias.

## Critérios (dado real, 6 lugares; um lugar conta se a mediana dos 20 inícios satisfaz)

**J1, ela aprende o ano e sabe que aprendeu.** No mundo real, o andar 2 declara antes de **1/9/2019**, com ω₂ no dia da declaração a ≤ **5 %** de Ω, em **≥ 5 de 6** lugares.

**J2, ela não declara o que não existe.** No mundo sem estações (o nulo dos testes 51–52: anomalias sobre a climatologia de 2010–2017, que é construção do mundo e não informação dada à sentinela; mesma normalização online), **nenhum andar** declara até 31/12/2025, em **≥ 5 de 6** lugares.

**J3, com o que decidiu sozinha, ela prevê como o calendário local.** O EAM das 42 previsões 2019–2025 (as mesmas dos testes 36b e 53, todas contadas, inclusive as feitas antes da declaração) é ≤ EAM(C) + **3,0** dias. C é o calendário fixo local do 36b, que exige 8 anos de histórico do lugar escritos à mão (EAM 20,0 d). O critério vira **≤ 23,0 d**.

Um julgamento por hipótese; sem emenda.

**Relatado, sem julgamento:**
- dia da declaração por andar e por lugar, ω na declaração, e dias ouvindo o campo até declarar (o custo de olhar);
- declarações do andar 1 no mundo real (uma oscilação intrassazonal pode ser ritmo de verdade, e por isso não julgo);
- **controle sem aprendizado** (η_w = 0): ele também trava e declara, e o que prevê depois do silêncio a 419 dias;
- EAM e viés por lugar; V1 (18,8 d), S do teste 53 (21,2 d) e um **calendário regional**: a média das entradas de 2010–2017 dos seis lugares, um firmware só para todos;
- o espalhamento das previsões entre os 20 inícios.

## Apostas (Claude, antes de rodar)

- **J1: 50 %.**
- **J2: 65 %.**
- **J3: 40 %.**
- Os três juntos: ≈ 15 %.
- Controle sem aprendizado declara em ≥ 5/6 lugares: 55 %.

## O que fecha

- **J1 e J2 passam:** a v0 tem a primeira propriedade que um filtro e um registrador de datas não têm. Ela sabe, pelo próprio estado e com taxa de falso alarme controlada, quando aprendeu um ritmo, e não o inventa onde ele não está. Isso vale para qualquer sensor, mesmo de período desconhecido. É o caminho para a sentinela.
- **J1 reprova e J2 passa:** ela é honesta mas lenta. Em 9 anos e meio, ainda não tem certeza do ano. Para uma placa, isso pesa contra: é tempo demais para aprender.
- **J2 reprova:** a declaração inventa ritmos no mundo real. A régua sequencial calibrada no sintético não sobrevive às secas e às oscilações de verdade.
- **J3** diz se a decisão dela, e não a nossa, sustenta a previsão. Mesmo passando, ela não supera o calendário local nem o v1. O ganho seria fazer o mesmo sem que ninguém escreva nada nela.

Instrumento: `teste54.py`, escrito depois do commit desta predição. Ele roda de novo o piloto sintético e exige esta predição.
