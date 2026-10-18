# Leitura do teste 18 (a régua sobre outro observador) — REPROVADO em (b); (a) passou 600 de 600

**Predição:** PREDICAO_teste18_regua_sobre_outro.md (395eff0), antes de rodar. **Instrumento:** teste18.py. **Resultado:** resultados_teste18.json. Um julgamento; sem emenda.

**Correção de registro, antes da leitura.** A primeira rodada, com os mundos gerados pelo laço do v0, foi interrompida por mim por tempo depois de quatro dos seis Ω; a segunda gera os mesmos mundos por `lfilter`. A mensagem do commit da segunda diz "idênticos, verificado", e isso está errado: a verificação que rodei imprimiu `False`. Os dois geradores diferem no primeiro passo (o laço do v0 parte de x₀ = 0 e ignora e₀; o `lfilter` o inclui) e, por acumulação, em todos os seguintes; são estatisticamente o mesmo mundo, não o mesmo arquivo. A evidência de que a diferença não importa aqui: os quatro Ω que a primeira rodada completou deram, na segunda, os mesmos números em todas as casas impressas (acerta 100/100; erros 0,043 · 0,046 · 0,065 · 0,087; cobertura 1,00). Fica registrado como erro de registro meu, não de instrumento.

## Resultado no mundo de julgamento (escada-3)

| Ω (desconhecido para a v0) | f_c verdadeiro | f̂_c mediano | acerta ±30 % | \|β̂ − β\| mediano | cobertura |
|---|---|---|---|---|---|
| EMA λ = 0,3 | 5,74 × 10⁻² | 5,75 × 10⁻² | 100/100 | 0,043 | 1,00 |
| EMA λ = 0,03 | 4,85 × 10⁻³ | 4,88 × 10⁻³ | 100/100 | 0,046 | 1,00 |
| EMA λ = 0,003 | 4,78 × 10⁻⁴ | 6,10 × 10⁻⁴ | 100/100 | **0,065** | 1,00 |
| cascata de duas EMAs 0,03 | 3,12 × 10⁻³ | 3,17 × 10⁻³ | 100/100 | **0,087** | 1,00 |
| média móvel W = 50 | 8,86 × 10⁻³ | 8,91 × 10⁻³ | 100/100 | **0,092** | 1,00 |
| EMA 0,03 + ruído 0,2 na saída | 4,85 × 10⁻³ | 4,88 × 10⁻³ | 100/100 | 0,046 | 0,87 |

Critério: (a) corte a ±30 % em ≥ 80 por Ω: **sim, 100 em todos**; (b) erro de cegueira ≤ 0,05 por Ω: **não** (três acima). **Reprovado.** Apostas: 50 % em passar (certa a não-passagem); por Ω 85/85/45/70/60/75 em (a): todas passaram (apostas do 3 e do 5 erradas, para o lado bom); cobertura ≥ 0,9 em escada-3 (certa); cobertura < 0,5 em deriva para o Ω rápido (**errada**: 1,00; a deriva tem potência em toda a banda, só que decrescente).

Deriva (relatado): cortes acertados 100/100 nos seis; erros de cegueira 0,067 · 0,026 · 0,006 · **0,161** · **0,217** · 0,026.

## O que o resultado diz

**A régua acha o corte de qualquer registro linear que vê entrar e sair**, de primeira ou segunda ordem, com zeros no ganho (média móvel) ou com ruído na saída: 600 acertos em 600, com erro mediano no corte abaixo de 1 % em cinco dos seis e de 28 % no mais lento (a resolução de Welch, como a predição apontou: f_c = 4,8 × 10⁻⁴ contra bolhas de 1,2 × 10⁻⁴). A forma de Ω não importou; o espectro cruzado não sabe o que é uma EMA.

**A cegueira estimada erra o valor por um motivo de definição, não de estimativa.** A v0 declara 1 − |Ĥ|², a fração da potência do mundo que a saída de Ω não contém. O teste chamou de verdade β = E‖x − y‖² / Var(x), a potência do resíduo, que no espectro é |1 − H|² = 1 − 2 Re H + |H|², e não 1 − |H|². As duas coincidem só quando H é real (sem atraso de fase). Um registro que **atrasa** (toda EMA, toda cascata, toda média móvel) erra mais do que deixa de ver: o resíduo inclui o que ele viu com atraso. A diferença cresce com o atraso de fase na banda em que o mundo tem potência: pequena na EMA rápida (0,04), maior na cascata (0,09) e na média móvel (0,09), e muito maior na deriva para essas duas (0,16 e 0,22), onde a potência está exatamente na banda de transição.

Nos testes 9, 16 e 17 isso não apareceu com esse tamanho porque lá o andar 1 tem λ = 0,15 e os andares seguintes recebem entradas já suavizadas; o viés de 0,02–0,03 do andar 1 naqueles testes é a mesma diferença, pequena.

## O que fecha e o que não

- Fecha: vendo entrada e saída, a v0 mede o corte de um observador linear de forma desconhecida; é a primeira cláusula do OBS-01 fora da v0 medindo a si mesma, e sustenta número.
- Fecha também uma distinção que o OBS-01 precisa escrever: **não ver** (1 − |H|², o que a saída não contém) e **errar** (|1 − H|², o que a saída não reproduz) são grandezas diferentes para todo observador que atrasa, e o atraso é a diferença entre elas. A v0 declara a primeira; um auditor que compara saída com mundo mede a segunda; os dois estão certos e medem coisas diferentes.
- Não fecha: a régua declarando as duas (o espectro cruzado dá Ĥ complexo, logo dá |1 − Ĥ|² de graça) contra as duas verdades; e a cegueira quando só se vê a saída, sem o mundo.

## Para a lista de defeitos de desenho do projeto

29. "Verdade" do teste definida como resíduo (|1 − H|²) e declaração definida como potência não contida (1 − |H|²): duas grandezas chamadas pelo mesmo nome. A predição não as distinguiu; a régua deve declarar as duas, com nome.
30. Mensagem de commit afirmando uma verificação que falhou. Erro de registro; corrigido nesta leitura.

Dezoito testes, dezesseis reprovações, duas passagens, trinta defeitos. Para o OBS-01, a quinta cláusula: **cegueira e erro são grandezas diferentes para um observador que atrasa; declarar as duas, com nome.**
