# Leitura do teste 52 (o erro contra o mundo): J1, J2, J3, J4 e J5 PASSARAM. Com o erro medido contra o mundo, o andar cuja escala contém o ano aprende o ano e o guarda quando a v0 para de olhar; os outros andares guardam as suas escalas. A regra é a mesma do teste 51; o que falhava lá era o acoplamento

**Predição:** PREDICAO_teste52_erro_contra_o_mundo.md (c4cac8c), antes de simular no dado real, conferida num piloto sintético. **Instrumento:** teste52.py (fe2acc9). **Resultado:** resultados_teste52.json. O piloto foi rerrodado dentro do instrumento e deu os mesmos números da predição. Cinco julgamentos; sem emenda.

## Braço A: relógios desacoplados, regra do mundo

Valores ao fim de 2017 e no silêncio (2018–2025); medianas de 20 inícios.

| lugar | ω/Ω, andares 1 · 2 · 3 · 4 | andar 2 no silêncio | controle sem aprendizado | nulo sem estações: ω₂ aprendido |
|---|---|---|---|---|
| Juara | 8,59 · **0,980** · 0,10 · 0,01 | **372,8 d** | 418,9 d | 688 d |
| Sinop | 8,56 · **0,989** · 0,07 · 0,02 | **369,3 d** | 418,9 d | 575 d |
| Cuiabá | 8,62 · **0,991** · 0,14 · 0,00 | **368,5 d** | 418,9 d | 683 d |
| Barra do Garças | 8,56 · **0,977** · 0,09 · 0,02 | **373,9 d** | 418,9 d | 511 d |
| Alta Floresta | 8,57 · **0,991** · 0,07 · 0,02 | **368,4 d** | 418,9 d | 582 d |
| Rondonópolis | 8,59 · **0,982** · 0,11 · 0,01 | **371,9 d** | 418,9 d | 581 d |

| | resultado | critério | |
|---|---|---|---|
| **J1** o andar 2 aprende o ano | 0,977–0,991 Ω, 6/6 | ≤ 5 %, ≥ 5/6 | **passou** |
| **J2** os outros guardam o seu ritmo | andar 1 ≈ 8,6 Ω; andares 3 e 4 ≤ 0,14 Ω, 6/6 | > 50 % do ano | **passou** |
| **J3** o ano sobrevive ao silêncio | 368–374 d (+0,9 a +2,4 %), 6/6; controle 418,9 d, 6/6 | ≤ 5 % / > 5 % | **passou** |
| **J4** o ano vem do mundo | nulo 511–688 d, 6/6 | > 10 % | **passou** |
| **J5** acoplados, com a regra do mundo | silêncio 354–373 d; nulo 404–487 d, 6/6 | ≤ 5 % e > 10 % | **passou** |

Apostas: J1 (75 %), J2 (80 %), J3 (70 %) e J4 (85 %) certas; J5 (35 %) errada.

## O que o resultado diz

**1. A regra é a mesma do teste 51; o que mudou foi o acoplamento.** Com os relógios desacoplados, a regra "aprender com o próprio erro" do teste 51 é exatamente a regra do mundo, porque o único desvio entre o que o relógio esperava e o que fez é o torque do mundo. No teste 51, o acoplamento enchia esse erro com o empurrão dos outros relógios, e ela aprendeu o grupo. Aqui o erro só contém o mundo, e ela aprendeu o mundo. O teste 36 já dizia isso numa forma simples; este o diz para o ritmo.

**2. A organização é por andar, e a escada sobrevive.**
- O andar 2 (registro de 67 dias, ritmo próprio de 419 dias) aprendeu o ano a 1–2 % nos seis lugares.
- O andar 1 ficou na sua faixa de ≈ 42 dias.
- Os andares 3 e 4, que não ouvem o ano (a amplitude anual que lhes chega é 8 % e 0,1 % da do andar 2), não o aprenderam.

Cada andar aprende o ritmo que a sua escala deixa passar e é cego para o resto. É a cegueira declarada da v0, agora como propriedade do que ela aprende, e não só do que ela vê. Ao contrário do teste 51, a identidade lenta não foi arrastada.

**3. É memória, e é do mundo.**
- Quando a v0 deixa de olhar, o andar 2 continua girando a 368–374 dias. Sem aprendizado, ele volta aos 419 dias.
- No mundo sem estações, a mesma regra leva o andar 2 para 511–688 dias: ele anda à toa com o torque do ruído, longe do ano.

O ano que ela guarda veio do mundo, não da arquitetura. É a primeira organização da v0 que passa no critério do silêncio do teste 34: um padrão que fica quando o mundo some e que não aparece num mundo sem ele.

**4. O que ela guarda é aproximado, e o que falta está à vista.**
- No silêncio, o relógio atrasa **3 a 8,5 dias por ano** em relação ao calendário. Em 8 anos sem olhar, acumula de 25 a 68 dias.
- Aprender levou bem mais que a conta: o andar 2 só entrou e ficou em ±5 % do ano depois de **6 a 7 anos** (2.258–2.681 dias), contra 1–2 anos previstos (defeito 73).
- No nulo, a mesma regra desloca o andar 2 em 20–40 %. Ela é sensível ao ruído quando não há ano para segurá-la.

**5. O braço B passou, mas por outro caminho.** Com os relógios acoplados e a regra do mundo, o aglomerado guarda o ano no silêncio (354–373 dias) e o nulo fica fora (404–487 dias). Mas **nenhum relógio aprendeu o ano sozinho**: o andar 2 terminou entre 1,09 e 1,25 Ω, e a frequência do grupo resulta de um equilíbrio entre membros errados. A deriva no silêncio vai de −7,6 a +11,2 dias por ano, mais espalhada que no braço A. O nulo de Juara (404 dias) passou por 0,6 ponto do limite. Passou pela letra; como memória do mundo, é mais frágil e menos legível que o braço A.

## O que fecha

Com o teste 51, a pergunta da Ana sobre a organização da v0 ganha uma resposta medida:

- **Auto-organização sem referência externa** (relógios acoplados, erro contra si mesmos) produz um ritmo comum persistente, mas surdo ao mundo e destruidor da escada.
- **Aprendizado com o erro contra o mundo,** em relógios que respeitam as escalas dos andares, produz memória do ritmo do mundo no andar que o contém. Ela persiste no silêncio, não aparece sem o ritmo e deixa os outros andares nas suas escalas.

O que a galáxia ensinou entrou duas vezes:
- a coordenação depende da distribuição dos ritmos (só o andar perto do ano trava);
- o acoplamento mútuo conserva o ritmo médio (por isso o teste 51 deu consenso).

O que ela não ensinou, e a v0 precisou: a referência tem de ser o mundo.

**Para a v0:** os relógios por andar com a regra do mundo são candidatos a incorporação, como decisão de projeto separada. O próximo passo natural é ligar o relógio do andar 2 ao relógio v1 do teste 36: o dia esperado da entrada das águas lido na fase de um ritmo aprendido, e não num calendário escrito.

## Para a lista de defeitos de desenho

73. A predição pôs o aprendizado do ano em 1–2 anos (constante de tempo ε/η_w = 365 dias, na aproximação travada). O dado real levou 6–7 anos para o andar 2 entrar e ficar em ±5 %. A conta supôs travamento contínuo com uma forçante senoidal limpa. O ano real tem estação seca e chuvosa assimétricas e variação entre anos, e não foi verificado qual dos dois atrasou o aprendizado. O piloto sintético não mediu esse tempo.

Placar: 52 testes numerados (o 25 sem resultado), mais o teste do ato A. 52: J1–J5 passaram. 73 defeitos nesta numeração, 1 emenda.
