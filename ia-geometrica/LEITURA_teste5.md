# Leitura do teste 5 (a régua de cegueira) — A REPROVADO, B REPROVADO

**Predição:** PREDICAO_teste5_cegueira.md (2b08c22), antes de rodar. **Instrumento:** teste5.py (e78ab69; uma correção de *broadcasting* no cálculo de β depois de a primeira rodada abortar na primeira semente, sem mudança de definição). **Resultado:** resultados_teste5.json. Dois julgamentos, um por hipótese; sem emenda.

## O que a v0 declara e o que é verdade

| mundo | δ̂ declarada (andares 1–4) | β real (andares 1–4) |
|---|---|---|
| branco | 0,95 · 0,98 · 0,97 · 1,00 | 0,78 · 1,00 · 1,00 · 1,00 |
| deriva | 0,85 · 0,93 · 0,97 · 1,00 | 0,33 · 0,95 · 1,01 · 1,00 |
| escada-3 | 0,86 · 0,90 · 0,92 · 1,00 | 0,17 · 0,58 · 0,91 · 1,05 |
| cíclico | 0,91 · 1,00 · 1,00 · 1,00 | 0,03 · 0,77 · 1,07 · 1,00 |

## Hipótese A: a declaração é verdadeira?

| andar | ρ Spearman (δ̂, β) | envelope de permutação | erro absoluto mediano | veredito |
|---|---|---|---|---|
| 1 | +0,16 | −0,17 a +0,15 | 0,59 | não |
| 2 | +0,34 | −0,13 a +0,19 | 0,13 | não |
| 3 | **+0,75** | −0,17 a +0,18 | 0,045 | **sim** |
| 4 | indefinido (δ̂ ≡ 1) | — | 0,001 | não |

**Reprovado** (passa só no andar 3). Apostas: 55 % em passar, errada; por andar 45/60/65/55 %, acertou o 3 e os não-passes de 1 e 4, errou o 2.

A declaração da v0 está **errada no valor em todos os andares e certa na ordem em um**. Ela se declara mais cega do que é: no andar 1 diz 0,85–0,95 onde a verdade vai de 0,03 (cíclico) a 0,78 (branco). A causa é a que a predição nomeou: a declaração é calculada sobre a **norma** da tensão, e a norma é um resíduo já passado pelo próprio andar (T₀ = ‖x − R₁‖ é o que o andar 1 *não* capturou). Perguntar "quanta potência do meu resíduo está acima do meu corte?" dá sempre "quase toda", porque o resíduo é, por construção, o que ficou acima do corte. A v0 mede a cegueira olhando para o próprio ponto cego, e vê escuro em todo lugar.

No andar 3 a ordem fica certa (ρ 0,75) porque T₂ = ‖R₂ − R₃‖ é a diferença entre dois registros lentos e carrega a forma do mundo nas escalas em que os mundos diferem. No andar 4 a declaração é exatamente 1 em todas as sementes: o período do andar (≈ 42.000 passos) é maior que a série (20.000), e a FFT não tem nenhuma raia abaixo do corte. A identidade só se mede em prazo maior que ela, e a série não tinha esse prazo; isso estava escrito antes.

## Hipótese B: a declaração é útil a quem lê?

| destino | erro sem declaração | com declaração | teto (retreinado) | U > 0 em | veredito |
|---|---|---|---|---|---|
| branco | 1,302 | **1,259** | 1,252 | 97/100 | sim |
| escada-3 | 1,161 | 2,138 | 1,022 | 0/100 | não |
| cíclico | 0,611 | 3,128 | 0,392 | 1/100 | não |

**Reprovado.** Apostas: 40 % em passar, certa a não-passagem; por destino 35/55/35 %, acertou branco (passou, contra a aposta de 35 %... errada, portanto), errou escada-3, acertou cíclico.

No branco a reescala ajudou e chegou quase ao teto (1,259 contra 1,252): a declaração disse "todos os andares quase cegos", o que é verdade lá, e o leitor achatou os pesos. Nos outros dois ela destruiu o leitor: a renormalização Σw' = Σw divide por uma soma que, com pesos de sinais opostos, fica perto de zero e explode (envelope até −3.839 % no cíclico). É o defeito que a predição nomeou (heurística minha, sem sinal), e o teto mostra que o leitor retreinado melhora muito (0,392 contra 0,611 no cíclico): havia o que ganhar, e a reescala não soube.

## O que fecha e o que não

- Fecha: a declaração de cegueira da v0, **como está escrita** (potência da norma da tensão acima do corte), não é uma medida verdadeira da cegueira real; é uma constante próxima de 1 com um pouco de ordem no andar 3. A frase "sei do que sou cega" ainda é retórica neste instrumento. O OBS-01 não pode usar `v0.cegueira` como régua.
- Fecha: a reescala positiva com renormalização não é um leitor que aproveite a declaração, mesmo onde ela acerta a ordem.
- Não fecha: uma declaração **linear** (potência de R_{j−1} − R_j, ou do próprio registro R_{j−1}, em vez da norma da tensão) acompanharia β; a predição já nomeou esse candidato. Nem fecha se um leitor que use a declaração para escolher **qual andar ler** por horizonte (em vez de reescalar pesos) ganharia; esse é outro leitor.

## Para a lista de defeitos de desenho do projeto

11. `v0.cegueira` mede a cegueira sobre o resíduo do próprio andar: olha para o ponto cego e declara escuridão. A declaração verdadeira tem de ser feita sobre o que o andar **recebe** (R_{j−1}, linear), não sobre o que ele deixou passar.
12. Série menor que o período do andar mais lento: a declaração do andar 4 é vazia por construção. Regra para o futuro: N ≥ 3 × 2π/λ_k.
13. Reescala de leitor com renormalização por soma de pesos de sinais mistos: instável.

## O que isto diz ao OBS-01

É o resultado mais útil dos cinco testes, e não por ter passado. Um observador que mede a própria cegueira **a partir do próprio resíduo** se declara cego em toda parte, e a declaração não distingue mundos. Se um modelo de IA fizesse o mesmo ("quanta coisa eu não entendi?" avaliada sobre o que ele não entendeu) daria sempre "quase tudo" ou "quase nada", e isso não seria medida. A régua de cegueira precisa ser calculada sobre a entrada do registro, não sobre o seu erro, e em prazo maior que a constante de tempo do registro que se quer medir. Esses dois requisitos nasceram aqui, com número, e valem para qualquer observador, inclusive para o que o OBS-01 quer medir.
