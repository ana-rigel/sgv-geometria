# Predição do teste 28 (o sítio com ato automático: rápido e barato)

19/10/2026 · escrita antes de rodar · Ana Rigel · corrige o que o teste 27 leu (o gargalo é o preço e a demora do ato), e só isso

## Pergunta

Nos testes 26–27, com um ato de 6 h que custa um décimo da perda, nenhum sensor local fez o ato se pagar. **Com um ato automático (uma comporta ou bomba acionada pelo próprio sistema: vale em 1 h e custa 1), o sítio fica resolvível por um alarme comum? E aí a v0 vê o que esse alarme não vê?**

## O que é igual

Mundo (`mundo_sitio`), sementes 1000–1099, 4 anos (1–2 afinação e réguas; 3–4 medida), cheia a 1,2 m, D = 100, P = 48 h, refratário de 48 h, pluviômetro de 0,2 mm, as leituras da v0 dos testes 26–27.

## O que muda

**Ponto julgado: L = 1 h, C = 1.** Mapa relatado (não julgado), em 30 sementes (1000–1029): L ∈ {1, 3, 6} h × C ∈ {1, 3, 10}. A célula (6, 10) é o ato dos testes 26–27 e serve de conferência.

Todas as famílias escolhem, na afinação, entre as formas OU e E (no teste 26 só havia OU; muda para todas igualmente).

## As contas, antes (defeitos 37 e 38), nas sementes de desenho 5000–5009, anos 3–4

**Teto (oráculo) e teto da chuva (sabe qual chuva vira cheia), em % abaixo de "nunca":**

| | C = 1 | C = 3 | C = 10 |
|---|---|---|---|
| L = 1 | 99,0 · 96,0 | 97,1 · 93,9 | 90,3 · 86,2 |
| L = 3 | 99,0 · 74,2 | 97,1 · 72,0 | 90,3 · 64,4 |
| L = 6 | 99,0 · 50,1 | 97,1 · 47,9 | 90,4 · 40,2 |

**Ponto de equilíbrio:** uma chamada se paga se a fração de chamadas que protegem uma cheia passa de C/D: **1 %** no ponto julgado (10 % nos testes 26–27).

**Taxas-base:** chuvas que viram cheia protegível: **12,2 %** com L = 1; 9,0 % com L = 3; 5,8 % com L = 6. Com L = 1, chamar a cada chuva já acerta doze vezes o ponto de equilíbrio. Cheias com alguma subida ≥ 0,10 m em 3 h pelo menos L horas antes (janela de 48 h): 97 % (L = 1), 68 % (L = 3), 45 % (L = 6).

A conta já diz o principal: **com o ato automático, o problema do sítio deixa de ser difícil.** Isso também diz por que J2 dificilmente passa: quando qualquer regra simples chega perto do teto, sobra pouco para uma leitura melhor ganhar.

## As políticas

| | leituras | grade |
|---|---|---|
| N2, córrego comum | nível; subida em 3 h | 42 × 21 × 2 formas |
| **N3, alarme comum de dois sensores** | chuva em 3 h; nível | 41 × 42 × 2 |
| v0 córrego | surpresa; vinco (régua) | 33 × 42 × 2 |
| **v0 dois sensores** | surpresa da chuva; vinco do córrego (régua) | 33 × 42 × 2 |
| cada chuva (relatada) | chama no início de cada chuva (≥ 12 h secas antes) | nenhuma |
| teto da chuva, oráculo | limites | — |

## Critérios (dois julgamentos, ponto L = 1, C = 1, 100 sementes)

Fração do teto: (custo de nunca − custo da política) / (custo de nunca − custo do oráculo), em totais.

**J1, o sítio fica resolvível com o ato automático:** N3 captura **≥ 70 %** do teto **e** fica abaixo de "nunca" em **≥ 95 sementes**.

**J2, a v0 vê o que o alarme comum não vê:** custo total da v0 dois sensores **≥ 10 % menor** que o de N3 e mais barata em **≥ 60 sementes**.

## Apostas (Claude, antes de rodar)

- **J1 passa: 85 %.** Chamar a cada chuva sai por ≈ 1 por chuva e perde só as cheias que chegam em menos de 1 h; espero N3 entre 80 % e 95 % do teto.
- **"Cada chuva", sem afinação nenhuma, captura ≥ 70 % do teto: 70 %.**
- **J2 passa: 15 %.** Perto do teto, 10 % do custo de N3 são poucas chamadas ou uma cheia por semente; espero a v0 entre −10 % e +10 % de N3.
- **Mapa:** a fração capturada cai mais ao longo de L do que de C (65 %); a célula (6, 10) dá N3 abaixo de 15 % do teto, como nos testes 26–27 (85 %); a célula (1, 10) dá N3 ≥ 50 % (60 %), isto é, **a rapidez sozinha já resolve boa parte**, mesmo com o ato caro.

## O que fecha

- **J1 passa, J2 reprova (o que eu espero):** a resposta para o sítio é de engenharia, não de mente: um ato automático e rápido resolve as cheias com um alarme simples de chuva e nível. O mapa diz qual das duas alavancas (rapidez ou preço) pesa mais e quanto de cada uma basta. A v0 não é necessária para o alarme; o lugar dela, se houver, continua na declaração.
- **J1 reprova:** mesmo com o ato rápido e barato, alarmes simples não se aproximam do teto; o mundo esconde algo que as contas acima não viram, e isso vira defeito antes de virar conclusão.
- **J2 passa:** perto do teto, a v0 ainda acha cheias que o alarme comum perde; o teste seguinte mostra quais.
