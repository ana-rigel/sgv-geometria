# Leitura do teste 56 (ela acompanha o dia na língua dela?): J1, J2 e J3 REPROVADOS. Na declaração, a leitura estava certa: as 8 "certas" estavam arrastadas pelo dia e as 5 "erradas" escorregavam. Mas, ouvindo sempre, ela não fica num estado: entra e sai do passo do dia, e às vezes desaba. E a medida tinha um defeito: na hora do máximo, o mundo empurra a fase dela para o mesmo lugar, relógio ou não

**Predição:** PREDICAO_teste56_acompanha_o_dia.md (77d1bc5), antes de calcular. **Instrumento:** teste56.py (a0b624c). **Resultado:** resultados_teste56.json. **Diagnóstico depois do julgamento:** diagnostico_teste56_pos_julgamento.txt. Três julgamentos; sem emenda.

## Resultados (R = estabilidade da fase dela na hora da temperatura máxima, 30 dias; teto do mundo no nosso relógio: 0,91–1,00)

| instalação | grupo (teste 55) | R 30 d depois de declarar | R nos últimos 30 dias | ν/Ω no fim | controle sem aprender: R no fim |
|---|---|---|---|---|---|
| 2010 | certa | 0,66 | 0,69 | 0,885 | 0,56 |
| 2011 | errada | **0,89** | 0,76 | 0,970 | 0,41 |
| 2012 | certa | 0,61 | 0,76 | 0,908 | 0,71 |
| 2013 | certa | 0,74 | 0,88 | 0,993 | 0,76 |
| 2014 | não declarou | | 0,70 | 1,001 | 0,92 |
| 2015 | errada | **0,93** | 0,19 | 0,207 | 0,70 |
| 2016 | certa | 0,35 | 0,72 | −0,007 | 0,49 |
| 2017 | não declarou | | 0,30 | 0,066 | 0,54 |
| 2018 | errada | **0,78** | 0,78 | 0,980 | 0,80 |
| 2019 | certa | 0,91 | 0,81 | 0,796 | 0,91 |
| 2020 | errada | **0,79** | 0,76 | 0,985 | 0,79 |
| 2021 | certa | 0,73 | 0,46 | 0,810 | 0,44 |
| 2022 | errada | **0,72** | 0,65 | 0,790 | 0,51 |
| 2023 | certa | 0,92 | 0,73 | 0,809 | 0,67 |
| 2024 | certa | 0,87 | 0,35 | 0,360 | 0,56 |

| | resultado | critério | |
|---|---|---|---|
| **J1** certas: R pós-declaração ≥ 0,7 | 5 de 8 | ≥ 7 de 8 | **reprovado** |
| **J2** erradas: R pós-declaração < 0,4 | **0 de 5** (0,72–0,93) | ≥ 4 de 5 | **reprovado**, ao contrário |
| **J3** R nos últimos 30 dias ≥ 0,7 | 8 de 15 | ≥ 12 de 15 | **reprovado** |

Controle sem aprender, ouvindo sempre: R no fim ≥ 0,7 em **7 de 15**, contra 8 de 15 da sentinela que aprende.

Apostas: J1 (75 %) errada; J2 (65 %) errada; J3 (35 %) certa a reprovação; controle arrastado em ≥ 8/15 (55 %) errada, por um.

## Diagnóstico depois do julgamento (não conta)

A frequência que ela percorre (ν), no dia da declaração e nos 30 dias seguintes ouvindo:

| | na declaração: ω/Ω · ν/Ω | percorrida nos 30 dias seguintes |
|---|---|---|
| certas (8) | ω 0,958–0,974 · **ν 0,973–1,020** | 2019, 2023: 1,00; 2010, 2021, 2024: 0,96–0,97; 2012: 0,77; 2013: 0,86; **2016: 0,14** |
| erradas (5) | ω 0,822–0,913 · **ν 0,857–0,898** | **2011, 2015, 2018: 1,00**; 2020, 2022: 0,87 |

## O que o resultado diz

**1. Na hora da declaração, a leitura pela língua dela estava certa.** As 8 "certas" percorriam o dia (ν ≈ 1,01–1,02 Ω): estavam arrastadas, com um dia interno de ≈ 24,7 h, como o circadiano. As 5 "erradas" percorriam 0,86–0,90 Ω: escorregavam 2,5–4 h por dia contra o sol. O J1 do teste 55 reprovou estas pelo motivo certo, e não pela nossa unidade. A pergunta da Ana mostrou isso, e o diagnóstico confirma.

**2. Mas ouvindo sempre, ela não fica num estado.** Nos 30 dias depois de declarar, três "erradas" se prenderam ao dia (1,00 Ω) e três "certas" saíram dele (0,77, 0,86 e 0,14 Ω). Ao fim do ano, a frequência percorrida caiu abaixo de 0,4 Ω em 4 instalações (2015: 0,21; 2016: ≈ 0; 2017: 0,07; 2024: 0,36): o aprendizado contínuo a puxa para os componentes lentos (defeitos 79–80). A declaração vale para o momento em que é feita, não para os meses seguintes.

**3. A medida tinha um defeito, e ele explica o J2 ao contrário.** As erradas de 2020 e 2022 percorreram 0,87 Ω nos 30 dias seguintes e mesmo assim deram R = 0,79 e 0,72. Com ε = 0,4, na hora do máximo, que é quando o sinal é mais forte, **o mundo empurra a fase dela para o mesmo lugar**: ela escorrega nas outras horas e é reposta no máximo. O caso extremo é 2016: frequência quase zero, e R = 0,72 no fim. Um ponteiro que só espelha a entrada passa nessa medida. Medir a fase no momento de maior força mede a força, não o relógio (defeito 81).

**4. Aprender a frequência não ajudou a acompanhar.** O controle que não aprende acompanhou quase igual (7 contra 8 de 15). Enquanto ouve, quem a põe no passo do mundo é o acoplamento, não o que ela aprendeu. Aprender a frequência só serviria para quando ela para de ouvir (a memória do teste 53). Mas o aprendizado contínuo, ouvindo sempre, estraga essa memória em parte das instalações.

## O que fecha

- **A pergunta da Ana estava certa no princípio.** O critério não é o nosso relógio, é a relação com o mundo. Medido assim, na declaração, a sentinela acertou nas 8 e errou nas 5 pelos motivos certos.
- **A sentinela não tem, ainda, um estado estável.** Com acoplamento forte e aprendizado sempre ligado, ela entra e sai do passo do dia e às vezes desaba. Para virar relógio dela mesma, precisa de uma regra que pare ou desacelere o aprendizado depois de declarar. É o "dois tempos" do 53, mas sem o silêncio: ela continua ouvindo e só deixa de mudar a frequência.
- **A régua da fase precisa ser lida fora do empurrão do mundo.** Por exemplo, ler a fase 6 horas antes do máximo e perguntar se ela **antecipa** onde o máximo vai cair. Prever o próximo máximo é o que separa um relógio de um ponteiro.

## Para a lista de defeitos de desenho

81. A estabilidade da fase foi lida na hora da temperatura máxima, que é o momento em que o sinal mais empurra o relógio (ε = 0,4). Ali, um relógio que escorrega nas outras horas e até um ponteiro sem frequência (2016) caem no mesmo ponto: a medida mede a força do mundo, não o relógio. A correção é ler a fase longe do empurrão e julgar a antecipação.
82. A predição tratou o estado da declaração como permanente ("escorregavam enquanto ouviam"). Na declaração isso era verdade (ν 0,86–0,90). Mas com o aprendizado sempre ligado, a frequência percorrida muda em semanas, nos dois sentidos, e desaba em 4 de 15 instalações até o fim do ano.

Placar: 56 testes numerados (o 25 sem resultado), mais o teste do ato A. 56: J1, J2 e J3 reprovaram. 82 defeitos nesta numeração, 1 emenda.
