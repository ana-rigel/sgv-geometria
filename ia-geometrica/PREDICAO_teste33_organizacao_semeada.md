# Predição do teste 33 (a organização nasce sabendo o clima)

20/10/2026 · escrita antes de rodar · instrumento v0.py sem mudança nos andares; organização ⋄ de teste32.py · Ana Rigel

## De onde vem

Da leitura do teste 32. A organização ⋄ (5 coeficientes do ano, aprendidos por mínimos quadrados recursivos) remove o ano dos andares 1 e 2. Mas, instalada fria em 01/01/2018, ela aprendeu como normal a seca de 2019–2025. Além disso, a verdade daquele teste premiava o calendário: só repetir o calendário valia AUC de 0,61–0,69. Os defeitos 43 e 44 pedem duas mudanças, e este teste faz só essas duas:

1. **A placa nasce sabendo o clima.** Os 5 coeficientes e a matriz da organização são calculados uma vez com 2010–2017 e gravados como ponto de partida. A partir de 01/01/2018 ela continua aprendendo como no teste 32. Cada dia novo pesa 1/(2.922 + n), ou seja, ela aprende devagar a partir do clima conhecido.
2. **A verdade não premia o calendário.** A AUC passa a ser calculada **dentro de cada mês do ano** e combinada pelo número de pares (positivo, negativo) de cada mês. Só se comparam dias do mesmo mês, então saber o mês não vale nada.

## Pergunta

Com 5 números de clima gravados na placa, a v0 lê a seca profunda tão bem quanto o SPEI-90 de 8 anos? E, depois de semeada, **aprender ajuda ou atrapalha?** Esta segunda é a pergunta da Ana de 20/10, "então a IA geométrica não aprende?", posta à prova.

## Declaração sobre a verdade (antes de rodar)

A verdade é a mesma do teste 30: anomalia padronizada do solo de 28–100 cm contra o normal de **2010–2017**, seca profunda ≤ −1. Ela diz que o normal de referência é o antigo. Para uma planta isso faz sentido, porque ela sente a água que há, não a que se tornou costume. Com essa verdade, qualquer aprendizado de um normal novo é penalizado por construção, quando o período medido é mais seco. O J2 mede esse custo; não diz se aprender é bom em geral.

## Séries (todas no R2, memória fria em 01/01/2018; medida 2019–2025)

| nome | organização | números de clima de fora |
|---|---|---|
| **v0+⋄ semeada** | semeada com 2010–2017; segue aprendendo | 5 (+15 da matriz) |
| **v0+⋄ semeada congelada** | semeada com 2010–2017; não aprende mais | 5 |
| **SPEI-90** (nulo) | soma de 90 dias, climatologia de 2010–2017 | 365 médias + 365 desvios de 3 séries |
| v0+⋄ fria | a do teste 32 | 0 |
| v0 crua | sem organização | 0 |
| v0 clim. fixa | a do teste 30 (365 médias suavizadas) | 365 |
| calendário | só a média climatológica de chuva − ET0 do dia, passada pela memória | — |

Lugares e dados: os cinco de MT do teste 32 julgados; Juara relatada. Intervalos por bootstrap em blocos de 90 dias (1.000, semente 33), sobre a AUC por mês.

## Portão da métrica (antes dos julgamentos)

A série **calendário** deve ter AUC por mês entre **0,40 e 0,60** em todos os cinco lugares. Ela ainda varia um pouco dentro do mês, então não fica exatamente em 0,5. Se sair dessa faixa em algum lugar, a métrica não removeu o prêmio do calendário e os dois julgamentos ficam **INCONCLUSIVOS**.

## Conta prévia (sem olhar a verdade, só o balanço; números da leitura do 32)

O balanço médio de 2018–2025 ficou 0,6–1,3 mm/dia abaixo do de 2010–2017 em MT. A organização semeada, com 2.922 dias de peso inicial, terá deslocado o seu normal em cerca de metade disso no fim de 2025 (8 anos contra 8 anos), e menos de um sexto em 2019. O deslocamento cresce no tempo e cresce na direção dos anos mais secos, que são onde a verdade tem mais positivos. Então aprender deve custar alguma coisa nessa verdade, e mais nos lugares onde o clima mudou mais (Cuiabá, Rondonópolis, Barra do Garças).

## Critérios

**J1, a placa semeada empata com o índice:** AUC por mês(v0+⋄ semeada) − AUC por mês(SPEI-90) **≥ −0,03** em **≥ 4 dos 5** lugares de MT.

**J2, aprender depois de semeada não atrapalha:** AUC por mês(v0+⋄ semeada) − AUC por mês(v0+⋄ semeada congelada) **≥ −0,02** em **≥ 4 dos 5**.

Relatado: Juara; as demais séries; a AUC comum (não por mês) para comparar com o 32; o normal aprendido no fim de 2025 contra o de 2010–2017.

## Apostas (Claude, antes de rodar)

- **Portão passa: 85 %.**
- **J1 passa: 55 %.** A favor: semeada com o mesmo período da verdade, e sem o prêmio do calendário, que era a vantagem da crua. Contra: o R2 (média exponencial de τ ≈ 67 d) e o SPEI-90 (soma reta de 90 dias) diferem por lugar. No teste 30, em Juara, empataram, mas a v0 clim. fixa perdeu do SPEI em Sinop e Barra do Garças no teste 32 (−0,09 e −0,13 na AUC comum).
- **J2 passa: 35 %.** Pela conta prévia, aprender deve custar algo onde o clima mudou mais.
- **Com a AUC por mês, a v0 crua cai abaixo da v0+⋄ fria em ≥ 4 de 5: 70 %.** Sem o prêmio do calendário, a crua perde o que tinha.

## O que fecha

- **J1 passa, J2 reprova:** a organização certa para a placa nasce com 5 números de clima e **não deve aprender o normal sozinha**, ou deve aprender muito mais devagar, quando a referência é a água que a planta sente. O "aprender" que sobra para a organização é outro: o ritmo dentro do ano, não o nível.
- **J1 e J2 passam:** 5 números de clima bastam, e aprender devagar não atrapalha nem numa seca de sete anos. A placa pode nascer semeada e continuar aprendendo.
- **J1 reprova:** mesmo semeada e sem o prêmio do calendário, o R2 não chega ao SPEI-90. Aí a diferença está na memória (exponencial contra janela reta), não na organização, e a pergunta volta para os andares.
