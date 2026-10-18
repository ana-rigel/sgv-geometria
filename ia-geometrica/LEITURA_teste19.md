# Leitura do teste 19 (não ver e errar) — REPROVADO por 0,006 num Ω; "não ver" exato nos doze casos

**Predição:** PREDICAO_teste19_duas_grandezas.md (26cce1a), antes de rodar. **Resultado:** resultados_teste19.json. Um julgamento; sem emenda.

| mundo / Ω | corte | \|ν̂ − ν\| (não ver) | \|ε̂ − ε\| (errar) | ε − ν (o atraso, em número) |
|---|---|---|---|---|
| escada-3 / EMA 0,3 | 100 | 0,000 | 0,007 | −0,043 |
| escada-3 / EMA 0,03 | 100 | 0,000 | 0,032 | −0,046 |
| escada-3 / EMA 0,003 | 100 | 0,001 | **0,056** | −0,063 |
| escada-3 / cascata 0,03 | 100 | 0,000 | 0,049 | +0,087 |
| escada-3 / média móvel 50 | 100 | 0,000 | 0,038 | +0,092 |
| escada-3 / EMA 0,03 + ruído | 100 | 0,000 | 0,033 | −0,046 |
| deriva / os seis | 100 | 0,000 | 0,000–0,003 | −0,067 a +0,217 |

Critério (escada-3): não ver ≤ 0,05 nos seis: **sim**; errar ≤ 0,05 nos seis: **não** (0,056 no Ω lento). **Reprovado.** Apostas: 65 % em passar (errada); "Ω 3 reprova em ν" 40 % (errada: ν foi exato; reprovou em ε); gap entre 0,03 e 0,10 nos de primeira ordem e > 0,08 na cascata e na média móvel (certa, com o sinal que eu não previ); deriva com ε̂ a ≤ 0,05 (certa, e por muito: ≤ 0,003).

## O que o resultado diz

**"Não ver" a régua mede exatamente.** ν̂ − ν ≤ 0,001 nos doze pares mundo × Ω: a fração da potência do mundo que a saída de um observador desconhecido não contém sai do espectro cruzado sem erro mensurável, para qualquer forma de Ω, com ou sem ruído na saída.

**"Errar" a régua mede bem e não exatamente:** 0,007 a 0,056 em escada-3, ≤ 0,003 em deriva. O erro que sobrou está no Ω mais lento e no mundo com a componente mais lenta (τ = 700): a fase de Ĥ nas duas ou três bolhas de frequência mais baixa é mal estimada por Welch com segmentos de 8.192 passos, e |1 − Ĥ|² é sensível à fase onde |H| ≈ 1. Em deriva, sem potência tão baixa, ε̂ fecha. É o limite de resolução nomeado antes, só que na grandeza com fase, não na sem.

**O sinal do atraso.** A predição falou do atraso como se ε fosse sempre maior que ν. Não é: para uma EMA, ε < ν (−0,04 a −0,07); para a cascata e a média móvel, ε > ν (+0,09 em escada-3; +0,16 e +0,22 em deriva). A diferença é 2 Σ S_xx (Re Ĥ − |Ĥ|²): positiva quando o observador atrasa pouco na banda em que o mundo tem potência (o resíduo de um registro de primeira ordem é um passa-alta mais fino do que "o que não vê"), negativa quando atrasa muito (segunda ordem, janela). O sinal de ε − ν é, portanto, uma medida da **ordem** do observador, e a régua o obtém de graça. Isso não estava na predição; fica como observação, não como resultado.

## O que fecha e o que não

- Fecha: de um observador linear de forma desconhecida, vendo entrada e saída, a régua obtém o corte (600/600, teste 18), o que ele não vê (exato) e o que ele erra (≤ 0,056), e o sinal da diferença diz se ele atrasa pouco ou muito. Para o OBS-01, as cláusulas 1–5 estão todas com número.
- Não fecha: ε̂ para observadores lentos em mundos com potência muito baixa (segmentos maiores); e tudo o que depende de ver a entrada: um modelo de IA cuja entrada não se conhece continua fora.

## Para a lista de defeitos de desenho do projeto

31. Predição que supôs ε > ν em geral; o sinal depende da ordem do observador. Erro de conta, nomeado depois.

Dezenove testes, dezessete reprovações, duas passagens, trinta e um defeitos. A linha da régua sobre outro observador está de pé em escada-3 e deriva, com os limites escritos.
