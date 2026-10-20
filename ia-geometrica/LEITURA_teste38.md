# Leitura do teste 38 (o laço que apara): J1, J3, J4 e J5 REPROVADOS; J2 PASSOU só pela letra. Nenhum laço apara até a faixa; a autoconsistência confunde o piso do ruído com ordem e trava tudo; a ordem semeada se desfaz em poucos Gyr

**Predição:** PREDICAO_teste38_laco_que_apara.md (ff8cc2f), antes de escrever o instrumento. **Instrumento:** teste38.py. **Resultado:** resultados_teste38.json. Modelo do teste 37, escuta no andar 3, 5.000 Myr, 100 sementes, medida em 3.000–5.000 Myr. Cinco julgamentos; sem emenda.

Mediana de C̄(3.000–5.000) e sementes na faixa [0,527; 0,727]:

| braço | 0,7 K_c | 0,8 K_c | 0,9 K_c | espalhamento entre K |
|---|---|---|---|---|
| referência (sem laço, semeada) | 0,250 · 0 | 0,286 · 0 | 0,404 · 0 | 0,154 |
| III-a, autoconsistência (semeada) | 0,999 · 0 | 0,999 · 0 | 0,999 · 0 | 0,000 |
| III-b, criticidade (semeada) | 0,429 · 12 | 0,780 · 7 | 0,869 · 5 | 0,440 |
| III-a, memória vazia | | 0,999 · 0 | | |
| III-b, memória vazia | | 0,260 · 6 | | |

| | resultado | critério | |
|---|---|---|---|
| **J1** III-a apara até a faixa | 0 de 100 (trava em 0,999) | ≥ 80 | **reprovado** |
| **J2** III-a tem um ponto próprio | espalhamento 0,000 | ≤ 0,05 | **passou pela letra** (o ponto é o teto de g) |
| **J3** III-b apara até a faixa | 7 de 100 | ≥ 80 | **reprovado** |
| **J4** III-b tem um ponto próprio | espalhamento 0,440 | ≤ 0,05 | **reprovado** |
| **J5** os laços não criam ordem | III-a vazia 0,999; III-b vazia 0,260 | ≤ 0,25 nos dois | **reprovado** (pelo III-a) |

Apostas: J1 (25 %), certa a reprovação; J2 (15 %), errada pela letra, mas pela razão que a leitura mostra; J3 (35 %), certa a reprovação; J4 (40 %), certa a reprovação; J5 (60 %), errada.

## O que o resultado diz

**1. A ordem semeada não se segura: ela se desfaz devagar.** Sem laço, a memória do andar 3 perde o que guardava (|R₃| 0,99 → 0,75 → 0,54 → 0,39 → 0,27 a cada Gyr, em 0,8 K_c), e o disco vai junto: C 0,99 → 0,58 → 0,43 → 0,29 → 0,30. Os 0,662 do teste 37 eram a média de 300–1.000 Myr de uma descida lenta. "Quem segura perto de 0,627 é a memória lenta semeada" (leitura 37, item 5) vale só para o primeiro Gyr. Ver defeito 54.

**2. A autoconsistência cria ordem a partir do ruído, e cria demais.** A trajetória é a mesma nos três K e na memória vazia. Primeiro, com a memória guardando mais do que o disco, a voz cai até o piso (g = 0,05) e o disco se solta (C ≈ 0,17). Depois, o critério inverte: com 12 anéis soltos, C tem um piso de acaso (≈ 0,2–0,26), enquanto |R₃| é a média lenta de um Z que gira e vai a quase zero. C − |R₃| fica positivo o tempo todo, a voz sobe até o teto (g = 20), e mesmo uma memória fraca, falando alto, trava todos os anéis: C = 0,999. O J2 passou porque os três K bateram no mesmo teto, não porque o laço achou um nível. É o mesmo piso de |Z| que derrubou o J1 do teste 37, agora dentro de uma regra de aprendizado: **a autoconsistência lê o acaso como ordem que a memória não acompanha, e responde dando voz à memória até travar.**

**3. A busca da criticidade não achou a borda, e a borda não se sustenta.** A voz quase não se moveu (g de 1,0 para 1,4 em 5 Gyr): o gradiente demodulado da flutuação foi fraco demais com 12 anéis, e o laço agiu pouco além da referência. O resultado passou a depender do K, como sem laço (0,43 · 0,78 · 0,87). Por semente, a distribuição é dividida: em 0,8 K_c, 39 sementes abaixo de 0,527, 7 na faixa e 54 acima. O disco cai para um dos lados; o meio é o lugar menos habitado. A borda entre soltar e travar existe, mas este laço não consegue segurar o disco nela.

**4. A resposta à pergunta da Ana.** "A auto-organização cria a estrutura ou apara uma estrutura que já nasceu pronta?" Neste modelo, nenhuma das duas regras apara. A estrutura semeada se perde em poucos Gyr. A única regra que mexeu de verdade, a autoconsistência, **criou** estrutura, mas a partir de um erro de leitura: tomou o piso estatístico da coerência por ordem. Uma regra que apara precisaria distinguir coerência de verdade do piso do acaso, por exemplo medindo C contra o valor esperado para N fases sorteadas, e isso é um desenho novo.

**5. Para a galáxia (modelo ilustrativo).** Se uma ordem inicial do disco se desfaz em ≈ 2 Gyr mesmo com memória lenta, uma coerência de 0,627 vista hoje num disco de vários Gyr pede algo que a mantenha agora (um K perto de K_c, ou reposição contínua), e não apenas uma lembrança da origem. É só o que o modelo diz; não é afirmação sobre a NGC 628.

## Para a lista de defeitos de desenho

54. A leitura do teste 37 concluiu que a memória lenta semeada "segura" o disco, com medida só até 1.000 Myr, menos de duas constantes de tempo do andar 3. Um horizonte de vários τ teria mostrado a descida. A conclusão 5 daquela leitura fica restrita ao primeiro Gyr.
55. A regra III-a comparou C, que tem um piso positivo com 12 fases soltas, com |R₃|, que vai a zero quando o disco gira solto. A conta prévia viu que o ponto fixo era degenerado, mas não viu que o piso torna C − |R₃| sempre positivo num disco solto. Com isso, g corre até o teto e trava tudo, e o J2 passou pelo teto.
56. A regra III-b não teve a sua relação sinal-ruído calculada: o gradiente da variância de C com 12 anéis, demodulado com período de 100 Myr num disco que responde em ≈ 100 Myr, pode ficar pequeno ou mudar de sinal pelo atraso. O laço quase não agiu.

Placar: 38 testes numerados (o 25 sem resultado), mais o teste do ato A de outra sessão. 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33, 34, 35: ambos reprovaram; 36: J1–J4 passaram, J5 reprovou; 37: J1–J4 reprovaram, J5 passou; 38: J2 passou (pela letra), J1, J3, J4, J5 reprovaram. 56 defeitos nesta numeração, 1 emenda.
