# Leitura do teste 55 (a sentinela do dia): J1 REPROVADO; J2 e J3 PASSARAM. Ela nunca inventou o dia, e a correção do defeito 75 calou o relógio arrastado nas 15 instalações; mas declarou com confiança um "dia" de 26–29 horas em 5 das 13 vezes em que declarou

**Predição:** PREDICAO_teste55_sentinela_do_dia.md e sentinela55.py (a0f1e2a), antes de rodar no dado horário. **Instrumento:** teste55.py (63d8bc6). **Resultado:** resultados_teste55.json. Três julgamentos; sem emenda.

## Resultados (15 instalações a frio de um ano; mediana dos 20 inícios)

| instalação | andar 1 declara | período declarado | J1 | nulo | controle com correção | controle sem correção |
|---|---|---|---|---|---|---|
| jan/2010 | 79 d | 24,7 h | ✓ | nada | nada | declara (179 d) |
| fev/2011 | 97 d | **27,1 h** | ✗ ω | nada | nada | declara (28 d) |
| mar/2012 | 61 d | 24,8 h | ✓ | nada | nada | declara (71 d) |
| abr/2013 | 105 d | 24,7 h | ✓ | nada | nada | declara (35 d) |
| mai/2014 | não declara (ω no fim: 26,5 h) | | ✗ | nada | nada | declara (11 d) |
| jun/2015 | 43 d | **27,3 h** | ✗ ω | nada | nada | declara (17 d) |
| jul/2016 | 46 d | 25,0 h | ✓ | nada | nada | declara (13 d) |
| ago/2017 | não declara (ω no fim: 16 dias, colapsou) | | ✗ | nada | nada | declara (17 d) |
| set/2018 | 256 d | **29,2 h** | ✗ prazo, ω | nada | nada | declara (19 d) |
| out/2019 | 259 d | 24,8 h | ✗ prazo | nada | nada | declara (117 d) |
| nov/2020 | 308 d | **27,1 h** | ✗ prazo, ω | nada | nada | declara (23 d) |
| dez/2021 | 142 d | 24,7 h | ✓ | nada | nada | declara (51 d) |
| jan/2022 | 114 d | **26,3 h** | ✗ ω | nada | nada | declara (20 d) |
| fev/2023 | 174 d | 24,6 h | ✓ | nada | nada | declara (113 d) |
| mar/2024 | 144 d | 24,7 h | ✓ | nada | nada | declara (11 d) |

| | resultado | critério | |
|---|---|---|---|
| **J1** declara em ≤ 180 d, ω a ≤ 5 % do dia | **7 de 15** | ≥ 12 de 15 | **reprovado** |
| **J2** no nulo sem dia, nenhum andar declara | **15 de 15** (nenhum dos 300 inícios) | ≥ 13 de 15 | **passou** |
| **J3** o controle sem aprendizado, com a correção, não declara | **15 de 15** (sem a correção: declara em 15 de 15) | ≥ 13 de 15 | **passou** |

O piloto refeito no instrumento reproduziu a tabela da predição linha a linha. Os andares 2 a 4 nunca declararam.

Apostas: J1 (35 %), certa a reprovação; J2 (75 %), certa; J3 (75 %), certa; controle sem correção declara em ≥ 8/15 (85 %), certa (15/15).

## O que o resultado diz

**1. A honestidade sobre a ausência continua perfeita.** No nulo sem dia, nenhum dos 300 inícios (15 instalações × 20) declarou ritmo em nenhum andar. Somado ao teste 54, isso dá dois mundos, duas escalas (ano e dia), passo diário e horário, e zero ritmos inventados.

**2. A correção do defeito 75 é decisiva, e agora está medida no dado real.**
- **Sem ela,** o relógio que não aprende declara em **todas** as 15 instalações, às vezes em 11 dias, sempre com a frequência errada. Com ε = 0,4, ele se deixa arrastar por qualquer coisa.
- **Com ela** ("só declaro se a frequência que guardo é a que ouço"), o mesmo relógio não declarou em nenhuma.

A correção entra na sentinela de vez.

**3. Quando há ritmo, ela pode declarar o ritmo errado.** Das 13 declarações:
- 8 caíram em 24,6–25,0 h;
- 5 caíram em **26,3–29,2 h**, e todas com confiança plena (100 % dos inícios declararam).

A declaração certifica "há um ritmo e estou presa a ele", mas não o período exato. A janela do andar 1 (3 períodos de 42 h, ≈ 5 dias) não separa 27 h de 24 h: o que roda 0,12 ciclo por dia em relação ao dia ainda parece coerente em 5 dias. O piloto mostrou exatamente esse modo de falha no mundo com ruído lento (0,872 Ω) e a predição apostou contra o J1 por isso. As frentes e os dias de chuva do dado real fazem o papel do ruído lento.

**4. Mesmo as declarações "certas" ficam 3–4 % abaixo do dia.** O ruído vermelho da banda puxa a frequência para baixo (defeito 79 abaixo).
- 24,7 h quer dizer que, no silêncio, o relógio atrasa **≈ 45 minutos por dia**: meio dia de erro em ≈ 16 dias.
- Nas declarações erradas, o atraso é de 2 a 5 horas por dia.

Para o dia, o "segundo tempo" do teste 53 (guardar o ritmo e olhar só os eventos) não serve como está. A sentinela precisaria voltar a olhar o campo a cada poucos dias. Numa placa que sempre ouve o termômetro, isso não custa nada.

**5. Ela aprende o dia em meses quando aprende.** As 7 que passaram declararam em 46–174 dias, contra 8–10 anos do ano no teste 54. A escala mudou como esperado: dois a seis meses para aprender um ritmo de um dia.

## O que fecha

- **A sentinela sabe distinguir "há ritmo" de "não há ritmo"**, nas duas escalas testadas, sem nenhum erro (J2 aqui e no 54). Essa é a parte firme.
- **Ela não sabe o período com precisão.** Com acoplamento forte e janela curta, ela pode se prender a 27 h e jurar que é o dia. "Sei que há um ritmo" e "sei qual é o ritmo" são declarações diferentes. A v0 hoje só faz a primeira com garantia.
- **A correção do 75 funciona** e fica.
- **Para uma placa:** como detector de presença de ritmo, ela é honesta e rápida (semanas a meses). Como relógio, ela é pior que qualquer relógio de tempo real. Ainda é a mesma conclusão de fundo: o valor dela está em declarar o que vê e o que não vê, não em medir melhor.

O passo seguinte natural é separar as duas declarações. Depois de "há ritmo", a sentinela faz um "zoom": demoduladores vizinhos a ω(1 ± δ) dentro de uma janela mais longa, e declara o período só quando ele estiver resolvido. Isso pede predição própria.

## Para a lista de defeitos de desenho

78. A declaração não resolve a frequência. Uma janela de 3 períodos naturais do andar (≈ 5 dias para o andar 1 horário) não separa ritmos a menos de ≈ 20 % um do outro, e Q fica alto para um relógio preso a 0,82–0,91 Ω. O piloto mostrou isso (ruído lento) e o desenho não mudou. Janelas mais longas (6 e 10 períodos) pioraram no piloto, porque o relógio declara antes de aprender. A solução tem de separar "presença" de "período".
79. O ω aprendido fica sistematicamente abaixo do ritmo (0,96–0,97 Ω no dia e no piloto; no teste 54 o ano ficou a ±1,2 %, sem lado preferido). No dia, o ruído vermelho dentro da banda puxa a frequência adaptativa para baixo. No silêncio, isso vira ≈ 45 min de atraso por dia.
80. Em ago/2017, o relógio do andar 1 colapsou para ω ≈ 0,06 Ω (período de 16 dias) mesmo ouvindo a tensão. A tensão do andar 1 ainda carrega componentes lentos quando a normalização online se desloca (início no fim da seca). A régua não declarou, o que foi correto, mas a sentinela passou o ano sem aprender.

Placar: 55 testes numerados (o 25 sem resultado), mais o teste do ato A. 55: J2 e J3 passaram, J1 reprovou. 80 defeitos nesta numeração, 1 emenda.
