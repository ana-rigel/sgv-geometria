# Predição do teste 55 (a sentinela do dia: com dado horário, ela aprende o dia em meses, sabe que aprendeu, não inventa o dia onde ele não está, e a correção do defeito 75 impede o relógio arrastado de declarar?)

21/10/2026 · escrita antes de rodar a sentinela no dado horário · instrumento da sentinela em `sentinela55.py` (commitado junto com esta predição; `sentinela.py`, do teste 54, fica intocada) · Juara, ERA5-Land horário, 2010–2025 · Ana Rigel

## De onde vem

O teste 54 mostrou duas coisas. A declaração é honesta: nenhum ritmo inventado no mundo sem estações. Mas ela é lenta: 8–10 anos para ter certeza do ano. A leitura apontou ritmos curtos como o próximo passo, com a correção do defeito 75. A Ana escolheu o dia, com acoplamento maior.

## O obstáculo, e o que o piloto obrigou a mudar (tudo no sintético, antes do dado real)

1. **Com a v0 intacta, o dia está fora de alcance.** Com passo horário, o andar 1 tem ritmo próprio de 42 h, e o dia fica a 0,112 rad/h dele. O relógio só trava se εA/2 ≥ 0,112 (teste 52). Com ε = 0,01, isso exigiria uma amplitude ~20 vezes a real. **ε passa a 0,4.** O tempo de aprender a frequência fica em 365 passos (η_w = ε/365), o mesmo número dos testes 52–54, que agora quer dizer 15 dias.
2. **O relógio ouve a tensão do andar, não o registro.** No piloto, o registro do andar 1 carrega o ano e a deriva lenta da normalização. O relógio se prendia à frequência zero (ω₁ caía de 0,57 Ω para 0,02–0,2 Ω em um ano). Com a entrada s_j = (R_j − R_{j+1})·u, isto é, o que o andar recebe e não guarda (defeito 11), o andar ouve uma banda.
3. **Defeito 75 corrigido.** O andar só declara se a frequência que guarda é a que ouve: |ω − ν| ≤ 5 % de ν, com ν = média exponencial do passo realizado dφ na janela.
4. **Janela de 3 períodos naturais, como no teste 54.** Testei janelas de 6 e 10 períodos para resolver melhor a frequência. Pioraram: declarações mais cedo e com ω errado (0,71–0,86 Ω), e o controle passou a declarar mesmo com a correção (50–100 %). Ficam 3.
5. **α = 0,001**, porque com α = 0,01 e ε = 0,2 o andar 1 declarou um dia inexistente em 1 de 8 mundos, no 8º dia de maturidade.

**A amplitude do dia usada no piloto** vem de uma estatística descritiva do dado real, como as amplitudes A_j no piloto do teste 52. Medi só 2010: na tensão do andar 1, o dia tem amplitude 0,98 para um desvio de 0,87. Por mês, a amplitude vai de 0,64 (novembro a dezembro, chuvas) a 1,25 (abril a junho). Ela não foi usada para nada além do piloto.

## O piloto (8 mundos sintéticos de um ano por condição, 20 inícios de fase, um sensor)

O mundo sintético tem:
- o dia, com amplitude modulada pela estação (±30 %, instalação em estação aleatória);
- ruído AR(1) de 24 h, e na variante "lenta" mais AR(1) de 7 dias (frentes);
- um pedaço do ano.

Os valores de A dão, na tensão do andar 1: "realista" ≈ a razão amplitude/desvio de 2010; "forte" = dia dominante.

| ε | mundo | andar 1 declara (no ano) | em ≤ 90 d | mediana | ω₁/Ω na declaração | andar 2 | controle com correção | controle sem correção |
|---|---|---|---|---|---|---|---|---|
| 0,2 | dia realista | 38 % | 38 % | 55 d | 0,941 | 0 % | 0 % | 25 % |
| 0,2 | dia forte | 100 % | 100 % | 42 d | 0,962 | 0 % | 0 % | 12 % |
| **0,4** | **dia realista** | **100 %** | 50 % | 77 d | **0,964** | 0 % | **0 %** | 88 % |
| 0,4 | dia realista, ruído lento | 62 % | 12 % | 173 d | **0,872** | 0 % | 0 % | 100 % |
| 0,4 | dia forte | 100 % | 100 % | 40 d | 0,967 | 0 % | 0 % | 100 % |
| 0,4 | sem dia | **0 %** | | | | 0 % | 0 % | 100 % |
| 0,4 | sem dia, ruído lento | **0 %** | | | | 0 % | 0 % | 100 % |

(α = 0,001 em todas as linhas.)

**Leituras do piloto:**
- **A correção do defeito 75 é decisiva.** Sem ela, o relógio que não aprende declara em 88–100 % dos mundos, inclusive nos **sem dia**: o acoplamento forte o arrasta para qualquer coisa. Com ela, 0 %.
- **O ω aprendido fica abaixo do dia**, em 0,94–0,97 Ω (períodos de 24,8–25,5 h). O ruído vermelho dentro da banda puxa a frequência para baixo. Com o ruído de 7 dias, ela declara um ritmo de 27,5 h (0,872 Ω) com confiança. A janela de 3 dias de 42 h não separa 0,87 de 1,0 Ω. Esse é o modo de falha que o critério de ω no J1 pega.
- O andar 2 nunca declarou. Os andares 3 e 4 não ficam maduros em um ano.

## O teste no dado real

- **Instalações:** 15, uma por ano de 2010 a 2024. A instalação do ano y começa no dia 1 do mês ((y − 2010) mod 12) + 1, à 0 h local, e roda 365 dias (8.760 horas). Os meses ficam espalhados pelas estações, e cada instalação começa a frio.
- **Sensores:** temperatura do ar, umidade relativa e umidade do solo 0–7 cm, os de uma placa barata. Normalização, cascata, projeção e ψ são todos online.
- **Sentinela:** `sentinela55.sentinela(s, ph0, eps=0,4, tau_aprender=365, alfas=[0,001])`, janela de 3 períodos, 20 inícios (semente 51). Uma instalação conta se a mediana dos 20 inícios satisfaz.
- **Nulo sem dia:** anomalias horárias sobre a climatologia por (mês, hora) de 2010–2025. É construção do mundo; a sentinela não a recebe.
- **Controles:** sem aprendizado (η_w = 0) com a correção, e sem aprendizado sem a correção.

## Critérios

**J1, ela aprende o dia em meses e sabe que aprendeu.** O andar 1 declara em até **180 dias** depois da instalação, com ω₁ no dia da declaração a ≤ **5 %** de 2π/24 h, em **≥ 12 de 15** instalações.

**J2, ela não inventa o dia.** No nulo sem dia, **nenhum andar** declara no ano, em **≥ 13 de 15** instalações.

**J3, a correção do defeito 75 funciona.** No dado real, o controle sem aprendizado, com a correção, **não declara** no ano em **≥ 13 de 15** instalações.

Um julgamento por hipótese; sem emenda.

**Relatado, sem julgamento:**
- dia da declaração e ω₁/Ω por instalação e por mês de instalação;
- ω₁/Ω no fim do ano;
- o controle sem a correção (quantas instalações declaram);
- declarações do andar 2;
- o espalhamento entre inícios.

## Apostas (Claude, antes de rodar)

- **J1: 35 %.** O piloto realista dá ω a 3,6 % do dia, perto do limite de 5 %. O ruído lento empurrou o ω para 13 % abaixo, e o dado real tem frentes e dias de chuva. Instalar na chuva (amplitude 0,64) atrasa.
- **J2: 75 %.**
- **J3: 75 %.**
- Controle sem correção declara em ≥ 8/15: 85 %.

## O que fecha

- **J1 e J2 passam:** a sentinela aprende o dia em meses, sem relógio escrito, e não o inventa onde ele não está. É a velocidade que faltou no teste 54, na escala em que uma placa vive.
- **J1 reprova pelo ω:** ela aprende um "dia" de 25–27 h e declara com confiança. O acoplamento forte que a fez alcançar o dia também a deixa ser puxada pelo ruído. A resolução da janela é o limite.
- **J3 passa:** a correção do 75 separa "arrastado" de "aprendido", e entra na sentinela de vez.
- **J2 ou J3 reprovam:** o acoplamento forte custa a honestidade que o 54 tinha.

Instrumento: `teste55.py`, escrito depois do commit desta predição. Ele roda de novo o piloto da linha ε = 0,4.
