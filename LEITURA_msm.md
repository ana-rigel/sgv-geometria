# Leitura: quantas escalas de volatilidade o BTC de 1 min pede? (MSM, jun–jul e ago–set/2026)

**Predição:** PREDICAO_msm.md (84e9c05) + PREDICAO_msm_v2.md com Emendas 1 e 2 (19e9d11), todas registradas antes de rodar o período correspondente. **v1:** INCONCLUSIVA (validação reprovou; escala da Student-t errada; real não lido). **v2 + Emenda 2:** esta leitura.

**Resultados:** resultados/msm_{junjul,agoset}.json (jun–jul local; ago–set Actions run 38979103170, agosto e setembro conferidos por SHA-256; outubro não lido).

## Validação do instrumento (antes de ler o real)

| | jun–jul | ago–set |
|---|---|---|
| Sintético k = 2 (2 min, 50 min) | k* = 2 | k* = 2 |
| Sintético k = 3 (2 min, 50 min, 21 h) | k* = 3 | k* = 3 |

Válido nos dois períodos.

## Real

| | jun–jul | ago–set |
|---|---|---|
| **k\*** | **4** | **4** |
| ΔBIC k1→k2 / k2→k3 / k3→k4 | 5192 / 1828 / 908 | 7969 / 4241 / 2456 |
| Escalas 1/γ_i em k = 4 | 8,6 min · 1,5 h · 16 h · 7,5 d | 7,1 min · 1,0 h · 9,8 h · 3,9 d |
| b (razão entre escalas) | 11,0 | 9,5 |
| m₀ | 1,57 | 1,86 |
| ν (cauda da inovação) | 6,3 | 2,75 |
| **Classe** | muitas escalas (≥ 4) | muitas escalas (≥ 4) |

M_4026 (descritivo): k* = 4 nos dois períodos, escalas 14 min · 1,1 h · 5 h · 1 d (jun–jul) e 12 min · 55 min · 4,4 h · 21 h (ago–set), com ν subindo até 29 e 13 (inovação quase gaussiana, como construído).

## Veredito

**"Muitas escalas (≥ 4)" nos dois períodos, com instrumento validado.** O tempo de negociação do BTC de 1 min pede pelo menos quatro componentes multiplicativas, numa escada geométrica de razão ≈ 10: minutos, hora, meio dia a um dia, dias. O ganho de BIC cai pela metade a cada degrau mas ainda é de centenas a milhares no quarto, que é a fronteira da grade; k = 5 provavelmente também seria escolhido. A aposta principal (55 % em "poucas escalas") **errou**; a secundária (35 % em k* = 4) acertou nos dois períodos.

## Como isto conversa com o que já tínhamos

- **v3 da memória (duas exponenciais, 10–50 min e 1–3 dias):** não contradiz; é a vista grossa da mesma escada. A ACF de um produto de quatro componentes de dois estados, olhada entre 1 min e 4,5 dias, se deixa aproximar por duas exponenciais: a rápida junta os degraus de minutos e hora, a lenta junta os de meio dia e dias. O MSM, que ajusta a verossimilhança minuto a minuto e não só a ACF, resolve o que a ACF fundia.
- **Multifractal v2 (σ̂ de 10/60/240 min absorve tudo até 4 h):** consistente. As três janelas do HAR cobrem os degraus de minutos e hora e parte do de meio dia; é por isso que, até 4 h, z = r/σ̂ ficou indistinguível do embaralhado. Os degraus de 10–16 h e de dias ficam fora do alcance daquele teste, não contradizem.
- **O M não é "duas escalas":** eu o descrevi assim nas predições de hoje e estava errado. Sua componente lenta é o caminho **real** de volatilidade suavizado em 61 min, que carrega toda a escada acima de uma hora; só abaixo de uma hora o M é sintético. Por isso o M também dá k* = 4. Fica registrado: o M é nulo para a escala rápida, não para a hierarquia lenta.
- **MMAR/MSM:** o quadro é de MSM com k ≥ 4 e b ≈ 10, não de "tempestade de dois andares". A metáfora da samambaia volta a ter alguma razão **dentro de 10 min a uma semana**: pelo menos quatro andares igualmente espaçados em log. Fora dessa faixa, nada medido.

## Limitações (declaradas antes; o que elas fazem com o resultado)

- **Ciclo diário não removido:** o degrau de 10–16 h pode ser, em parte, a sazonalidade intradiária vestida de componente. Isso tiraria um degrau, não a escada: ficariam minutos, hora e dias.
- **BIC com 87 mil observações** penaliza pouco; mas a validação com escalas separadas recuperou k = 2 e 3 exatos nesta mesma amostra, logo o BIC não "compra" componentes à toa aqui.
- **k ≤ 4** é fronteira: o resultado é "pelo menos quatro".
- ν variou de 6,3 a 2,75 entre períodos: a cauda condicional de ago–set é bem mais gorda; não é objeto deste teste, fica como descritivo.

## Apostas

| Aposta | Prob. | Saiu |
|---|---|---|
| Validação passa nos dois períodos | 65 % | sim (após Emendas 1 e 2) |
| "Poucas escalas" (k* = 2 ou 3) nos dois períodos | 55 % | **não** |
| k* = 4 em algum período | 35 % | sim (nos dois) |
| k* = 1 em algum período | 5 % | não (acerto) |
| Uma escala em 10–60 min e outra em 0,5–3 dias, dois períodos | 60 % | não (as escalas caem fora dessas janelas: 7–9 min, 1–1,5 h, 10–16 h, 4–7,5 d) |
| ν entre 2,5 e 5 | 70 % | não (6,3 e 2,75) |

Duas versões, dois defeitos de desenho registrados (escala da t; parâmetros de validação), um resultado que repete e que me contraria.

## O que fecha e o que não

- Fecha: "quantas escalas" nestes dados não é duas; é pelo menos quatro, espaçadas por ~10×, de minutos a dias, com o instrumento validado.
- Não fecha: se a escada continua além de uma semana (precisaria de meses de dados e k ≥ 5) e quanto do degrau de ~meio dia é ciclo diário (precisaria dessazonalizar, e isso é uma v3 com predição própria, não pedida).
- Em nenhum caso há direção, previsão ou lucro.
