# Leitura do teste 42 (a memória das interações e a largura da janela): J1 e J5 PASSARAM; J2, J3, J4 e J6 REPROVADOS. A memória empurra a janela para cima e a alarga um terço em 12 anéis, mas não em 16 nem em 24; com frequências uniformes, a janela já não existe

**Predição:** PREDICAO_teste42_memoria_na_janela.md (4b08c98), antes de escrever o instrumento. **Instrumento:** teste42.py (9f11b8e). **Resultado:** resultados_teste42.json. Disco de 12 anéis do teste 41 com a memória do colaborador; malha α × τ (4 × 4) escolhida em 10 condições de seleção e julgada em 10 de validação. Seis julgamentos; sem emenda.

## A seleção (condições de seleção; larguras em K/K_c)

| α \ τ | 30 | 100 | 300 | 1.000 |
|---|---|---|---|---|
| 0,25 | 0,060 · 0,135 · 1,12 | 0,060 · 0,140 · 1,12 | 0,070 · 0,150 · 1,14 | 0,015 · 0,150 · 1,175 |
| 0,50 | 0,050 · 0,115 · 1,12 | 0,070 · 0,170 · 1,16 | 0,070 · 0,200 · > 1,2 | 0 · 0,130 · > 1,2 |
| 0,75 | 0,050 · 0,105 · 1,12 | **0,110 · 0,200 · > 1,2** | 0,005 · 0,170 · > 1,2 | 0 · 0 · > 1,2 |
| 1,00 | 0,045 · 0,090 · 1,12 | 0,105 · 0,155 · > 1,2 | 0 · 0 · > 1,2 | 0 · 0 · > 1,2 |

(janela da faixa · janela de sincronização parcial · K_L). Sem memória: 0,060 · 0,145 · 1,12. **Célula escolhida: α = 0,75, τ = 100 Myr.**

## A validação (as 10 condições que não entraram na seleção)

| | janela da faixa | sincronização parcial | K_L | inclinação de C̄(K) na janela | λ_max > 5×10⁻⁴ na janela |
|---|---|---|---|---|---|
| sem memória | **0,060** (0,975–1,035) | | 1,12 | 1,35 | 1 de 12 |
| α = 0,75, τ = 100 | **0,080** (1,030–1,125) | 0,195 | > 1,20 | 1,13 | 10 de 16 |

Com a memória, C̄ forma um **patamar** em 0,68–0,69 entre 1,07 e 1,125 K_c e salta para 0,78 em 1,135. O λ_max convergiu: a maior diferença entre 20 e 40 Gyr é 9 × 10⁻⁵ sem memória e 5 × 10⁻⁴ com ela.

| | resultado | critério | |
|---|---|---|---|
| **J1** recuperação (α = 0) | 0,975–1,035 | 0,965–0,975 até 1,030–1,040 | **passou** |
| **J2** ampliação | 0,080 / 0,060 = **1,33 ×** | ≥ 1,5 × | **reprovado** |
| **J3** robustez | 12 de 16 K com espalhamento ≤ 0,03 (75 %); 0,18 e 0,37 nos dois primeiros | ≥ 80 % | **reprovado** |
| **J4** escala | razões 0,64 (N = 16) e 0,73 (N = 24) | ≥ 1,5 nas duas | **reprovado** |
| **J5** sincronização parcial genuína | 100 % da janela | ≥ 80 % | **passou** |
| **J6** o controle uniforme estreita | sincronização parcial 0 · 0,005 · 0,005 · 0,005 (N = 12 · 16 · 24 · 48) | estritamente decrescente | **reprovado** (já é zero em N = 12) |

Apostas: J1 (95 %), certa; J2 (45 %), certa a reprovação; J3 (65 %), errada; J4 (40 %), certa a reprovação; J5 (60 %), certa; J6 (70 %), errada pela letra (ver item 4). Aposta do mecanismo (célula com τ ≥ 100, α ≥ 0,5 e K_L acima do de α = 0): o instrumento a marcou falsa porque K_L da célula ficou acima da grade (> 1,20) e o código exigia um valor; pelo que a frase diz, ela está certa (defeito 60).

## O que o resultado diz

**1. A memória faz o que a conta previu, mas o ganho é pequeno e não escala.** Com τ ≥ 100 e α ≥ 0,5, o recrutamento dos anéis internos fica mais difícil e o travamento total sai da grade (K_L > 1,2). A janela se desloca para cima em ≈ 0,05 K_c, a curva fica menos íngreme (1,35 → 1,13) e aparece um patamar em C ≈ 0,68–0,69 (dois anéis escorregando, estendido). Em 12 anéis, a janela alarga um terço (0,060 → 0,080). Em 16 e 24 anéis, a memória a **estreita** (razões 0,64 e 0,73). É um efeito de disco pequeno.

**2. A seleção superestimou.** Nas condições de seleção, a célula escolhida dava 0,110; na validação, 0,080. É a maldição do vencedor numa malha de 16 células com 10 condições; a separação seleção/validação, pedida pelo colaborador, existia para isso, e funcionou.

**3. A borda de baixo fica caótica e dependente do início.** Na janela com memória, 10 de 16 pontos têm λ_max > 5 × 10⁻⁴ (sem memória, 1 de 12), e os dois primeiros pontos têm espalhamento de 0,18 e 0,37 entre condições. A memória acrescenta 12 graus de liberdade com atraso, e o lado de baixo da janela ganha caos e multiestabilidade. Com α e τ grandes demais (α ≥ 0,75 e τ ≥ 300), o disco não sincroniza em parte nenhuma da grade.

**4. A janela vem da curva de rotação, não do número de anéis.** Com as mesmas 12 frequências, mas igualmente espaçadas, a janela de sincronização parcial **já é praticamente zero em N = 12** (0 a 0,005 em todos os N), e K_L desce para K_c conforme N cresce (1,08 · 1,06 · 1,04 · 1,02). É o resultado conhecido para a distribuição uniforme: a transição vai direto do incoerente ao travamento total. O J6 reprovou porque o critério pedia um estreitamento estrito e a janela já começou no zero. A pergunta que ele fazia está respondida: a janela de ≈ 6 % do teste 41 existe porque Ω ∝ 1/r deixa as frequências mais densas nos anéis externos. A organização parcial deste disco é um efeito da **forma** da distribuição de frequências.

## O que isso significa para os caminhos

- **Caminho A, na forma da memória das interações, não resolve o ajuste fino.** O ganho é de um terço em 12 anéis, some com N, e vem com caos na borda de baixo.
- **O Caminho B ganhou um alvo concreto.** Como a janela vem da forma da distribuição de frequências, a física a mudar é a curva de rotação (ou o perfil radial dos anéis), e não acrescentar memória. A pergunta para a NGC 628 vira: o perfil Ω(r) da zona estável, medido, produz uma distribuição de frequências com janela larga ou estreita? É uma pergunta que os dados respondem.

## Para a lista de defeitos de desenho

59. O J6 pediu estreitamento estrito sem calcular antes a janela uniforme em N = 12. Ela já era zero, e um critério de monotonia sobre zeros só pode reprovar. Uma conta de uma linha (a do limite uniforme, com K_L → K_c) teria mostrado que a pergunta certa era "a janela uniforme é muito menor que a de 1/r?", e a resposta é sim.
60. A aposta do mecanismo foi codificada exigindo K_L dentro da grade, quando a própria conta prévia previa que ele subiria; com K_L > 1,20, o código marcou falso. A aposta foi lida pelo que a frase diz.

Placar: 42 testes numerados (o 25 sem resultado), mais o teste do ato A. 42: J1 e J5 passaram, J2, J3, J4 e J6 reprovaram. 60 defeitos nesta numeração, 1 emenda.
