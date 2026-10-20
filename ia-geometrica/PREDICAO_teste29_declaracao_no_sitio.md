# Predição do teste 29 (a declaração no sítio)

19/10/2026 · escrita antes de rodar · Ana Rigel · leva ao sítio a única propriedade da v0 que ficou de pé nos testes 16–17

## Pergunta

Nos testes 26–28 a v0, como alarme, não acrescentou nada a uma regra de chuva e nível. Nos testes 16–17 o que ficou de pé foi outra coisa: **a v0 declara com verdade o que ela não vê.** No sítio, isso vira uma frase que serve para quem cuida: a cada cheia que o sistema perdeu, dizer se ela veio rápido demais para o que o sensor e o ato conseguem ver (cegueira do sistema) ou se veio devagar e o alarme deveria ter pego (falha da regra). **A declaração do andar 1, feita sobre a janela antes de cada cheia, separa as cheias que o alarme comum perdeu das que ele protegeu? E faz isso melhor que uma medida comum de "subiu rápido"?**

## O que é igual

Mundo, sementes 1000–1099, anos 1–2 para afinar e anos 3–4 para medir, D = 100, P = 48 h, o alarme comum N3 (chuva em 3 h e nível, formas OU e E), afinado exatamente como no teste 28.

## O ponto julgado

**L = 6 h, C = 3**: o ato lento e de preço médio, onde N3 capturou 55 % do teto no mapa do teste 28, isto é, perde parte das cheias e protege parte. Nas sementes de desenho 5000–5004 (contagem feita antes, sem avaliar declaração nenhuma): 93 cheias, **15 perdidas e 78 protegidas**. Em 100 sementes espero ≈ 1.900 cheias e ≈ 300 perdidas. Relatados sem julgamento: (3, 3) e (1, 1).

## A declaração (regra dos testes 9 e 16, sem mudança)

Para cada cheia no instante t do cruzamento, sobre o nível lido na janela [t − 48 h, t]: δ̂₁ = Σ S(f) · (1 − |H₁(f)|²) / Σ S(f), com |H₁(f)|² o ganho do andar 1 (λ₁ = 0,15, τ ≈ 7 h). É a fração do que aconteceu no córrego nas últimas 48 h que andou mais rápido do que o andar 1 acompanha. O τ do andar 1 é quase o L do ato (7 h e 6 h), por isso a declaração do andar 1 é, nesse ponto, a declaração do que o sistema não podia ver a tempo. Não houve escolha de λ para este teste: é o andar 1 dos testes 1–28.

**Verdade:** a cheia foi perdida (nenhuma chamada a protegia) ou protegida pelo N3 afinado.

**Medidas comuns (o nulo que importa):** a subida nas últimas L horas, x(t) − x(t − L); e a fração da subida da janela que aconteceu nas últimas L horas. Na comparação entra a mais forte das duas (maior AUC), escolhida depois, o que favorece o nulo.

## Critérios (dois julgamentos, ponto (6, 3), todas as cheias das 100 sementes)

**J1, a declaração separa perdidas de protegidas:** AUC da declaração ≥ **0,70**, e o limite inferior do intervalo de 95 % (bootstrap por semente, 1.000 reamostras) acima do quantil 95 % da AUC com os rótulos permutados.

**J2, a declaração diz mais que "subiu rápido":** AUC da declaração − AUC da medida comum mais forte ≥ **0,03**, com o intervalo de 95 % da diferença (mesmo bootstrap) acima de zero.

Relatado: médias da declaração nas perdidas e nas protegidas, e as duas outras células.

## Apostas (Claude, antes de rodar)

- **J1 passa: 60 %.** No teste 28 o N3 protegeu ficando de guarda quando o córrego estava alto; as cheias que escapam devem ser as que partem de nível baixo e sobem em poucas horas, e essas têm muita potência acima do corte do andar 1. Contra: muitas cheias protegidas também sobem rápido na hora final, e uma janela de 48 h tem resolução de frequência grosseira (25 bandas).
- **J2 passa: 15 %.** A declaração é uma soma ponderada do espectro da janela; a fração da subida nas últimas 6 h mede quase a mesma coisa sem espectro. Espero diferença entre −0,05 e +0,03.
- **A declaração média das perdidas maior que a das protegidas: 80 %.**
- **Na célula (1, 1) a AUC da declaração é menor que em (6, 3): 65 %.** Com o ato de 1 h, o andar 1 (τ ≈ 7 h) é lento demais para dizer o que foi rápido demais para o ato.

## O que fecha

- **J1 passa, J2 reprova (o que eu espero):** a v0 diz com verdade, cheia a cheia, quais vieram rápido demais, e uma medida simples diz o mesmo. A declaração vale como relatório para quem cuida do sítio, mas não é exclusividade da v0. O que seria só dela fica para quando houver mais de um andar e mais de uma escala a declarar (o andar 3, de semanas, sobre a estação).
- **J1 e J2 passam:** a declaração da v0 separa melhor do que "subiu rápido"; o teste seguinte mostra por quê.
- **J1 reprova:** no sítio a cegueira do andar 1 não explica as perdas; elas vêm de outra coisa (a regra, a estação, a chuva que o córrego ainda não viu), e a leitura dirá qual.
