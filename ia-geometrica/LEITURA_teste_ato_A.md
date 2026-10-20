# Leitura do teste do ato A (o laço do ato): J2 e J4 PASSARAM; J1 e J3 REPROVADOS. A organização aprende com a consequência e readapta quando o mundo muda; o preço é tremer num mundo parado

**Predição:** PREDICAO_teste_ato_A.md (registrada como 37 em 8fed1bd; renomeada em dc6e487, sem mudança de critério). **Fumaça:** NOTAS_FUMACA_teste_ato_A.md. **Instrumento:** teste_ato_A.py. **Resultado:** resultados_teste_ato_A.json. L = 1 h, C = 10, D = 100, P = 48 h, h = 1 ano; o córrego assoreia (cheia a 1,0 m) no 5º ano; 100 mundos de 8 anos. Quatro julgamentos; sem emenda.

| | medida | resultado | critério | |
|---|---|---|---|---|
| **J1** aprende (C) | órgão / melhor marca fixa em retrospecto, anos 2–8 | mediana **1,13**; ≤ 1,10 em **35** de 100 | ≥ 80 | **reprovado** |
| **J2** readapta (B) | ganho sobre a afinada, anos 6–8 | **31,7 %** (C: 5,0 %; +26,7 pontos); ≥ 10 % em **80** de 100 | ≥ 10 %; ≥ +10 pontos; ≥ 60 | **passou** |
| **J3** não perde de quem não aprende (C) | órgão / afinada, anos 3–8 | total **0,958**; ≤ 1,05 em **67** de 100 | ≤ 1,05; ≥ 70 | **reprovado** (por 3 mundos) |
| **J4** depende da consequência (D) | ganho de D sobre a afinada, anos 6–8; B mais barato que D | **3,9 %** (abaixo do de C); **95** de 100 | extra ≤ metade do de B; ≥ 70 | **passou** |

Custo total nos 100 mundos, por ano:

| ano | 1 | 2 | 3 | 4 | **5** | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C órgão | 36.490 | 35.480 | 34.280 | 31.860 | 31.790 | 29.990 | 30.870 | 31.570 |
| C afinada | 25.900* | 26.770* | 33.310 | 34.520 | 33.480 | 34.050 | 31.180 | 32.110 |
| B órgão | 36.490 | 35.480 | 34.280 | 31.860 | **64.620** | 55.020 | 53.890 | 51.040 |
| B afinada | 25.900* | 26.770* | 33.310 | 34.520 | **79.480** | 79.350 | 79.080 | 75.910 |
| D órgão (consequências sem a mudança) | = B | | | | 78.290 | 75.090 | 72.970 | 77.070 |
| E órgão (consequências de outro sítio) | 43.710 | 42.980 | 37.790 | 36.130 | 72.060 | 61.440 | 56.520 | 57.410 |

*Nos anos 1–2 a afinada é avaliada nos mesmos dados com que foi escolhida; o número é otimista por construção.

Anos 6–8 de B (100 mundos): órgão 159.950; afinada 234.340; melhor marca fixa em retrospecto 141.360; nunca 479.000.

Apostas: J1 passa (30 %), certa a reprovação; J2 (85 %), certa; J3 (85 %), **errada**; J4 (75 %), certa; E mais perto de B que de D (80 %), certa (25,2 % contra 31,7 % de B e 3,9 % de D).

## O que o resultado diz

**1. Pela primeira vez, aprender vale mais que uma regra afinada.** Quando o córrego assoreia, a regra afinada nos anos 1–2 passa a custar ≈ 79 mil por ano, e não sai disso, porque foi afinada num mundo que deixou de existir. O órgão leva o mesmo choque no ano 5 (de 32 mil para 65 mil), mas já no ano 6 desce para 55 mil e continua descendo (51 mil no ano 8). Nos anos 6–8, custa **32 % menos** que a afinada em 80 de 100 mundos, e fica a 13 % da melhor marca possível em retrospecto. Nenhum teste anterior da v0 tinha mostrado um caso em que aprender ganha de não aprender por essa margem.

**2. É a consequência do próprio mundo que ensina.** O controle D age no mesmo mundo assoreado, com as mesmas leituras e as mesmas marcas, mas aprende com as consequências do mundo sem o assoreamento. Ele não readapta: fica em 73–78 mil, praticamente na afinada (ganho de 3,9 %, menos que o do mundo parado). B é mais barato que D em 95 de 100 mundos. A readaptação vem inteira do erro certo. O controle foi construído para não divergir (lição do defeito 50) e respondeu limpo.

**3. Aprender com outro sítio igual quase vale.** O órgão E recebe as consequências de outro sítio do mesmo tipo, que também assoreou, e ganha 25 % sobre a afinada, três quartos do ganho de B. Antes da mudança ele é pior (cerca de 40 mil por ano contra 34 mil), porque aprende as cheias de outro córrego. Depois da mudança, o que muda é o tipo de mundo, e isso ele aprende de qualquer sítio que tenha passado por ela. Para placas em rede, essa é a base de aprender umas com as outras.

**4. O preço: tremer num mundo parado.** No mundo constante, o órgão vai aprendendo (de 36 mil no ano 1 para ≈ 31 mil nos anos 4–8) e, no total dos anos 3–8, custa **4 % menos** que a afinada. Mas, mundo a mundo, troca de marca pelo ruído das cheias e paga por isso. Ficou a ≤ 1,10 da melhor marca em retrospecto em só 35 de 100 mundos (J1), e a ≤ 1,05 da afinada em 67 de 100, três a menos que o exigido (J3). Na média é melhor que não aprender; mundo a mundo, em um terço dos sítios é pior. É a mesma troca que o teste 36 mediu no relógio (η rápido aprende ruído), agora com custo em dinheiro.

## O que fecha

Pelos termos da predição, **J2, J3 e J4 precisavam passar** para autorizar o teste B. J2 e J4 passaram: a organização aprende com a consequência do ato e readapta quando o mundo muda. J3 reprovou por 3 mundos, mesmo com o total a favor do órgão. Então o teste B **não fica autorizado** por esta predição. Antes dele, o órgão precisa parar de tremer num mundo parado sem perder a readaptação. O desenho que isso sugere, para um teste com predição própria, é trocar de marca só quando a diferença acumulada passar de um limiar, uma histerese como a da régua. O teste 36 pede a mesma coisa para o relógio.

## Para a lista de defeitos de desenho

ato-A-1. A predição apostou 85 % no J3 com base no total das sementes de desenho (0,917), sem olhar a distribuição mundo a mundo. A própria conta prévia dizia que o órgão troca de marca pelo ruído e que cada troca custa; ela deveria ter estimado quantos mundos ficariam acima de 1,05. O J3 misturou um critério de total (que passou) com um critério mundo a mundo (que reprovou), e a aposta só olhou o primeiro.

Placar do laço do ato: 1 teste, J2 e J4 passaram, J1 e J3 reprovaram; 1 defeito.
