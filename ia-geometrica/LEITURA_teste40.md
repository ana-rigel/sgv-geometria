# Leitura do teste 40 (40-A: os ramos de equilíbrio do disco): J1, J2 e J3 PASSARAM; J4 REPROVADO. Neste disco, 0,627 não é um equilíbrio: todo estado travado tem C ≥ 0,79, e a faixa da NGC 628 só existe como regime em movimento numa janela de 8 % de K_c

**Predição:** PREDICAO_teste40_ramos_do_disco.md (09b9de4), antes de calcular. **Instrumento:** teste40.py. **Resultado:** resultados_teste40.json. Disco de 12 anéis, sem memória e sem controlador. Quatro julgamentos; sem emenda.

## Os equilíbrios

K_c = 25,84 mrad/Myr; max|Δω| = 22,99 mrad/Myr (o anel de 9 kpc). As frequências relativas (Δω/max) vão de +1,00 a −0,77, quase uniformes.

| | valor |
|---|---|
| limiar de travamento K_L/K_c | **1,115** |
| coerência no limiar C_L | **0,808** |
| u no limiar (KC/max\|Δω\|) | 1,012 |
| menor C de qualquer estado travado, com todos os cos > 0 | **0,791** |

Em K/K_c = 1,12, logo acima do limiar, há duas soluções todas positivas: C = 0,795, instável (λ_max = +2,6 × 10⁻³ /Myr), e C = 0,822, estável (−2,6 × 10⁻³ /Myr). É uma bifurcação sela-nó em K_L. Daí para cima, o ramo estável vai de C = 0,835 (λ_max −4,6 × 10⁻³) a 0,944 em 1,6 K_c (−2,9 × 10⁻²). As selas (um cosseno negativo) têm sempre um autovalor positivo.

## A média de C no tempo (sem equilíbrio abaixo de K_L)

| K/K_c | 0,60 | 0,80 | 0,90 | 0,95 | **1,00** | **1,02** | 1,05 | 1,10 | 1,20 | 1,60 |
|---|---|---|---|---|---|---|---|---|---|---|
| coerente, sem ruído | 0,300 | 0,313 | 0,339 | 0,373 | **0,672** | **0,712** | 0,746 | 0,793 | 0,875 | 0,944 |
| sorteado, sem ruído | 0,256 | 0,282 | 0,348 | 0,462 | 0,675 | 0,707 | 0,748 | 0,792 | 0,875 | 0,944 |
| coerente, com ruído | 0,297 | 0,347 | 0,429 | 0,532 | 0,633 | 0,656 | 0,708 | 0,781 | 0,861 | 0,941 |

Janela da faixa [0,527; 0,727]: sem ruído, K/K_c de **0,96 a 1,03** (largura 0,08 K_c); com ruído, 0,11 K_c. Maior diferença entre partir coerente e sorteado: 0,150, em 0,91 K_c.

| | resultado | critério | |
|---|---|---|---|
| **J1** 0,627 não é equilíbrio | C_L = 0,808 | ≥ 0,70 | **passou** |
| **J2** ramo travado estável, selas instáveis | em toda a grade acima de K_L | | **passou** |
| **J3** a faixa pede ajuste fino | 0,08 K_c | < 0,10 K_c | **passou** |
| **J4** há histerese | 0,150 | > 0,2 | **reprovado** |

Apostas: J1 (80 %), certa; J2 (95 %), certa; J3 (60 %), certa; J4 (50 %), reprovou.

## O que o resultado diz

**1. Neste disco, 0,627 não é um estado de equilíbrio, e não pode ser, com nenhum acoplamento a uma fase comum.** Um equilíbrio exige que todos os anéis travem, e o anel que mais difere da média (o de 9 kpc) só trava se a força puxando para a fase comum for ao menos |Δω_max|. Nesse caso-limite, a coerência é a média de √(1 − (Δωᵢ/Δω_max)²), que dá **0,791**, e qualquer força maior dá mais. Isso não depende de quem puxa: o campo médio do disco, o pino de uma memória lenta ou um controlador, desde que o termo seja do tipo F · sen(φ − θᵢ) para uma fase comum φ. Para estes 12 anéis, com curva plana e 200 km/s, **todo equilíbrio tem C ≥ 0,79**. A pergunta do 40-C ("existe alguma região de parâmetros em que a realimentação negativa estabiliza um equilíbrio intermediário?") tem resposta negativa para esta família de acoplamentos: não há equilíbrio intermediário a estabilizar.

**2. A faixa da NGC 628 existe, mas como movimento.** Entre 0,96 e 1,03 K_c, abaixo do travamento, alguns anéis escorregam o tempo todo, e a média de C cai entre 0,527 e 0,727. É um regime, não um ponto. E a janela tem 8 % de K_c: abaixo dela o disco solta (0,37 em 0,95), acima passa da faixa (0,75 em 1,05). Com ruído, a janela alarga um pouco (11 %). É ajuste fino, como na TAR.

**3. Perto do travamento, o disco fica lento.** Logo acima de K_L, o autovalor que manda é ≈ −2,6 × 10⁻³ /Myr, um tempo de relaxação de ≈ 380 Myr. Isso é o desaceleramento crítico de uma sela-nó. Explica por que o Laço I do teste 37 oscilou (defeito 52): perto do limiar, o disco responde em centenas de Myr, e um controlador que mede em 50 Myr age sobre um sistema que ainda não respondeu. Dá número ao ponto do colaborador: a janela de velocidades estáveis de um controlador depende dos autovalores, e eles ficam pequenos justamente onde se queria controlar.

**4. Sem histerese que conte.** Partir coerente ou sorteado dá quase o mesmo C̄ em toda a grade (diferença máxima 0,15, em 0,91 K_c, onde os dois estão soltos). A transição quase descontínua não deixou, neste disco finito, dois regimes estáveis lado a lado. O disco não tem uma "memória própria" que pudesse substituir a v0.

## O que muda no programa do colaborador

- **40-B e 40-C, como estavam formulados, perdem o objeto.** Não há equilíbrio intermediário cujos autovalores a memória retardada ou a realimentação possam deslocar; o limite inferior de 0,79 é geométrico.
- O que sobra para um controlador é outra coisa: **manter o disco dentro de uma janela de K de 8 %**, num regime sem ponto fixo, onde o tempo de resposta passa de centenas de Myr. É um problema de regulação de regime, não de estabilização de equilíbrio.
- Para o 0,627 ser um equilíbrio, a física do disco teria de mudar: outra distribuição de frequências (outra curva de rotação), acoplamento entre vizinhos em vez de campo médio, ou anéis que não precisem travar todos. Isso confirma a frase final do colaborador: se nenhuma região intermediária pode ser estabilizada, é a dinâmica dos anéis que tem de mudar, e não a equação de g.

Placar: 40 testes numerados (o 25 sem resultado), mais o teste do ato A. 40: J1, J2, J3 passaram, J4 reprovou. 58 defeitos nesta numeração (nenhum novo), 1 emenda.

## Correção (20/10/2026, depois da leitura; apontada pelo colaborador)

O item 1 acima diz que "todo equilíbrio tem C ≥ 0,79". Isso está **errado** como foi escrito. O limite de 0,791 vale para os estados travados com todos os cossenos positivos (o ramo principal). A autoconsistência geral admite sᵢ = ±1 em cada anel, e esses ramos são outros equilíbrios. O J1, como foi definido (C_L do ramo principal ≥ 0,70), continua aprovado; a frase interpretativa é que passou do que o teste mediu.

Enumeração completa dos 4.096 padrões de sinais (enumeracao_ramos_teste40.py, rodada depois da correção, não julgada):

| K/K_c | equilíbrios estáveis (C, nº de sinais −) | instáveis: quantos, faixa de C | instáveis com C a ±0,02 de 0,627 |
|---|---|---|---|
| 1,2 | (0,875; 0) | 1, 0,779 | 0 |
| 1,6 | (0,944; 0) | 29, 0,556–0,801 | 9 (todos com 2 sinais −) |
| 3,0 | (0,986; 0) | 475, 0,297–0,825 | 46 (todos com 2 sinais −) |
| 10 | (0,999; 0) | 1.831, 0,089–0,833 | 0 (com 2 sinais −, C → 10/12 − 2/12 ≈ 0,667; com 3, ≈ 0,50) |

A frase correta é: **em todo K testado, há um único equilíbrio estável, o do ramo principal, com C ≥ 0,79. Existem equilíbrios com C ≈ 0,627, mas são selas instáveis (dois anéis em oposição à fase comum), e só de ≈ 1,6 K_c para cima.** As consequências dos itens 2 a 4 e da seção seguinte não mudam: não há equilíbrio intermediário **estável** a estabilizar no ramo principal. Uma sela com C ≈ 0,627, porém, é um objeto que um controlador poderia, em princípio, tentar estabilizar; isso fica para a análise que vier.
