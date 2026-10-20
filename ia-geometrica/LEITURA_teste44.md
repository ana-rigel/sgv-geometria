# Leitura do teste 44 (43-D: a forma da curva de rotação decide a janela?): J1, J2, J3 e J4 PASSARAM. A janela de sincronização parcial cresce quando a curva cai e encolhe quando ela sobe, sem depender do número de anéis; 1,5° de warp na zona bastam para mudá-la pela metade

**Predição:** PREDICAO_teste44_forma_da_rotacao.md (3f664ff), antes de escrever o instrumento. **Instrumento:** teste44.py (ab782cf), sobre o mapa do teste 42 sem memória. **Resultado:** resultados_teste44.json. Curvas v ∝ r^β, frequências reescaladas para a abertura da curva plana; 10 condições; 20 Gyr. Quatro julgamentos; sem emenda.

Largura da janela de sincronização parcial (K/K_c; aglomerado ≥ N/2 e ≥ 1 anel escorregando, na maioria das condições):

| β (warp equivalente) | N = 12 | N = 24 | N = 48 | K_L em N = 12 · 24 · 48 |
|---|---|---|---|---|
| −0,4 (+1,5°) | **0,200** (0,930–1,125) | ≥ 0,200 | ≥ 0,185 | 1,130 · 1,100 · 1,085 |
| −0,2 (+0,8°) | 0,175 | ≥ 0,185 | ≥ 0,180 | 1,125 · 1,095 · 1,080 |
| 0 (plana) | **0,150** | 0,150 | ≥ 0,165 | 1,120 · 1,085 · 1,075 |
| +0,2 (−0,8°) | 0,115 | 0,125 | 0,135 | 1,110 · 1,080 · 1,065 |
| +0,4 (−1,5°) | **0,100** | 0,100 | 0,110 | 1,105 · 1,075 · 1,060 |

"≥": a janela começa no limite inferior da grade (0,90 K_c) e pode se estender abaixo dele.

| | resultado | critério | |
|---|---|---|---|
| **J1** recuperação (β = 0, N = 12) | 0,150 | 0,14 ± 0,02 | **passou** |
| **J2** a forma importa (N = 12) | 0,200 / 0,100 = **2,0 ×** | ≥ 2 × | **passou** (no limite) |
| **J3** a direção prevista | Spearman **−1,00** | ≤ −0,9 | **passou** |
| **J4** sobrevive em N (β ≤ 0) | N = 48 / N = 12: 0,93 · 1,03 · 1,10 | ≥ 0,5 | **passou** |

Apostas: J1 (85 %), J2 (75 %), J3 (75 %), J4 (60 %): as quatro certas.

## O que o resultado diz

**1. A forma da curva de rotação decide a janela, e na direção prevista.** Com a mesma abertura de frequências, curvas que caem (β < 0) deixam as frequências mais concentradas nos anéis externos e a janela larga; curvas que sobem aproximam a distribuição da uniforme e a janela estreita. Entre β = −0,4 e +0,4, a janela cai à metade, com a ordem perfeita nos cinco valores e nos três N. O limite β → 1 (rotação sólida, distribuição quase uniforme) é o caso do teste 42, com janela ≈ 0.

**2. Não é efeito de poucos anéis.** Para cada forma, a janela fica praticamente igual de 12 para 48 anéis (e até cresce um pouco para as curvas que sobem). O que estreita com N é só K_L, que se aproxima de K_c. A sincronização parcial de discos com curva plana ou caindo é uma propriedade da distribuição de frequências, não da discretização.

**3. Para a NGC 628, a janela não pode ser lida dos dados atuais.** Com i ≈ 8,5°, um warp que muda a inclinação em 1,5° de 9 a 14 kpc equivale a β ≈ ∓0,4, e isso dobra ou corta pela metade a janela. Aniyan et al. modelam um warp exatamente nessa região; Sylos Labini et al. (2023), segundo o colaborador, relatam PA e inclinação constantes só até 300″. Sem um perfil i(r) e v(r) medido na zona, com incerteza, o modelo só diz que a janela fica entre ≈ 0,10 e ≈ 0,20 K_c, conforme o warp.

**4. A hipótese do colaborador, no modelo, está sustentada:** a persistência da sincronização parcial depende da distribuição radial das frequências induzida pela curva de rotação, sem memória. O que falta para falar da galáxia é a medida, e o teste 43 retirou o 0,627 como alvo; o que se compararia agora é a estrutura radial (anéis internos escorregando), não um número de coerência.

## Limites

As janelas de β ≤ 0 em N = 24 e 48 começam no limite inferior da grade (0,90 K_c); são limites inferiores. A grade de β é de leis de potência; um warp real não precisa ter essa forma. A representação do padrão espiral (Speights et al. 2025) não foi testada.

Placar: 44 testes numerados (o 25 sem resultado), mais o teste do ato A. 44: J1–J4 passaram. 61 defeitos nesta numeração (nenhum novo), 1 emenda.
