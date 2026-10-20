# Leitura do teste 46 (a janela prevista sem integrar): J1, J3 e J4 PASSARAM; J2 REPROVADO. A autoconsistência de Kuramoto prevê o fim da janela exatamente, a coerência com erro de 0,01 e quem desliza em 89 % dos casos; o começo da janela, em N pequeno, sai cedo demais e converge para a simulação conforme N cresce

**Predição:** PREDICAO_teste46_janela_sem_integrar.md (9fe252a), antes de calcular. **Instrumento:** teste46.py (d8d4428). **Resultado:** resultados_teste46.json. Teoria do estado parcialmente travado resolvida em (r, Ω) para cada K; comparação com as 15 combinações do teste 44 e com uma simulação nova de quem desliza (N = 12). Quatro julgamentos; sem emenda.

| N | β | janela teoria | janela simulação | K_L teo / sim | erro médio de C |
|---|---|---|---|---|---|
| 12 | −0,4 | 0,900–1,125 | 0,930–1,125 | 1,130 / 1,130 | 0,010 |
| 12 | 0 | 0,930–1,115 | 0,970–1,115 | 1,120 / 1,120 | 0,009 |
| 12 | +0,4 | 0,965–1,100 | 1,005–1,100 | 1,105 / 1,105 | 0,009 |
| 24 | −0,4 | 0,900–1,095 | 0,900–1,095 | 1,100 / 1,100 | 0,004 |
| 24 | 0 | 0,910–1,080 | 0,935–1,080 | 1,085 / 1,085 | 0,005 |
| 24 | +0,4 | 0,950–1,070 | 0,975–1,070 | 1,075 / 1,075 | 0,007 |
| 48 | −0,4 | 0,900–1,080 | 0,900–1,080 | 1,085 / 1,085 | 0,002 |
| 48 | 0 | 0,900–1,070 | 0,910–1,070 | 1,075 / 1,075 | 0,004 |
| 48 | +0,4 | 0,940–1,055 | 0,950–1,055 | 1,060 / 1,060 | 0,004 |

(β = ±0,2 no resultados; mesmo padrão.) Diferença de largura (teoria − simulação), média por N: **+0,040** (N = 12), **+0,020** (N = 24), **+0,006** (N = 48).

| | resultado | critério | |
|---|---|---|---|
| **J1** o travamento total | **15 de 15** exatos | ≥ 14 a ≤ 0,01 | **passou** |
| **J2** a largura da janela | 10 de 15 a ≤ 0,025 | ≥ 12 | **reprovado** (os 5 de N = 12) |
| **J3** a coerência | **15 de 15**, erro médio 0,002–0,010 | ≥ 12 a ≤ 0,05 | **passou** |
| **J4** quem desliza (N = 12) | **132 de 148 (89 %)** | ≥ 80 % | **passou** |

A teoria calculou as 15 combinações em 61 s; o teste 44 simulou as mesmas em dezenas de minutos.

Apostas: J1 (90 %), certa; J2 (55 %), errada; J3 (50 %), certa; J4 (70 %), certa.

## O que o resultado diz

**1. A janela de sincronização parcial é uma propriedade calculável da distribuição de frequências.** A borda de cima (o travamento total, K_L) sai exata em todos os casos. A coerência dentro da janela sai com erro de 0,002 a 0,010. A borda de baixo sai com um viés sistemático: a teoria encontra uma solução parcialmente travada antes da simulação, 0,03–0,05 K_c antes em 12 anéis, 0,025 em 24 e ≤ 0,01 em 48. Esse viés diminui com N, como deve uma aproximação de campo médio. É ali, na borda de baixo, que o teste 41 viu caos de fase: em N pequeno, a solução teórica existe, mas o movimento caótico dos anéis deslizantes a desfaz.

**2. Quem desliza é quem está mais longe da frequência do aglomerado.** Em 89 % dos pontos, a teoria acerta exatamente o conjunto. Todos os 16 erros são de um anel só, na borda (o anel marginal, com |x| ≈ 1), e quase todos com a simulação deslizando um anel a mais que a teoria; em dois pontos da borda caótica, a simulação perdeu o aglomerado inteiro. Isso responde à primeira investigação da Ana (geometria espectral): o aglomerado se instala na frequência Ω que equilibra as contribuições, que cai na região densa das frequências baixas (os anéis externos, por Ω ∝ r^(β−1)); entram no aglomerado os anéis com |Δω − Ω| ≤ K r, e saem, um a um, os internos.

**3. A forma da curva entra pela posição de Ω e pela distância dos anéis internos a ela.** Quanto mais a curva cai (β menor), mais assimétrica a distribuição, mais Ω se desloca para o lado denso, e mais cedo o aglomerado se forma com poucos anéis de fora; o travamento total continua exigindo puxar o anel mais interno, e K_L muda pouco. A janela alarga por baixo. É o mecanismo do teste 44, agora explicado.

## O que isso abre

- **A terceira investigação fica barata.** Para cada perfil de inclinação i(r) dentro das incertezas, as frequências inferidas mudam, e a teoria dá a janela, a coerência e quem desliza em segundos. Com 24 anéis ou mais, o erro da borda de baixo fica ≤ 0,025 K_c. Falta só o insumo: perfis i(r) e v(r) da zona com incerteza (a Figura 13 de Aniyan et al. digitalizada, ou os de Sylos Labini et al.).
- **Uma fórmula geral está ao alcance.** No limite contínuo, as duas equações viram integrais sobre p(Ω) ∝ Ω^(−1−1/(1−β)), e a janela fica função só de β (e da forma da distribuição). É uma hipótese matemática que não depende da NGC 628, como a Ana queria.

## Para a lista de defeitos de desenho

62. O J2 usou a mesma tolerância (0,025 K_c) para todos os N, sem estimar o viés de campo médio em N pequeno, que a própria predição esperava ("mais nos N pequenos"). Um critério por N, ou só para N ≥ 24, teria separado o acerto da teoria do seu limite conhecido.

Placar: 46 testes numerados (o 25 sem resultado), mais o teste do ato A. 46: J1, J3, J4 passaram, J2 reprovou. 62 defeitos nesta numeração, 1 emenda.
