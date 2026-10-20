# Leitura do teste 41 (o atlas dos regimes em movimento): J1 e J2 PASSARAM; J3, J4 e J5 REPROVADOS. A faixa da NGC 628 é um regime real e persistente, de sincronização parcial, em que os anéis internos escorregam; a janela é estreita e só a parte de baixo dela é caótica

**Predição:** PREDICAO_teste41_atlas_dos_regimes.md (0748915), antes de escrever o instrumento. **Instrumento:** teste41.py (f698c51). **Resultado:** resultados_teste41.json. Disco de 12 anéis sem memória nem controlador; 20 Gyr por trajetória, 4 Gyr de transiente; 21 condições iniciais; K/K_c de 0,90 a 1,12, passo 0,005. Cinco julgamentos; sem emenda.

## O atlas (N = 12, condição coerente)

| K/K_c | C̄ | aglomerado travado · anéis escorregando | λ_max (/Myr) | deriva entre janelas | espalhamento entre condições |
|---|---|---|---|---|---|
| 0,90–0,965 | 0,36–0,50 | 1–3 · 9–11 | +1,4 a +2,6 × 10⁻³ | 0,03–0,17 | — |
| **0,970** | 0,586 | 7 · 5 | +1,1 × 10⁻³ | 0,030 | 0,083 |
| **0,975** | **0,627** | 9 · 3 | +7,0 × 10⁻⁴ | 0,013 | 0,031 |
| **0,980–0,985** | 0,64–0,65 | 9 · 3 | +2 a +6 × 10⁻⁴ | 0,009–0,018 | 0,03–0,04 |
| **0,990–1,035** | 0,68–0,72 | 10 · 2 | entre −1,8 e +1,5 × 10⁻⁴ (≈ 0) | 0,001–0,011 | ≤ 0,003 |
| 1,040–1,115 | 0,73–0,81 | 11 · 1 | ≈ 0 | ≤ 0,010 | ≤ 0,003 |
| 1,120 | 0,822 | 12 · 0 (travado) | −2,6 × 10⁻³ | 0 | 0 |

Janela da faixa [0,527; 0,727]: **0,970 a 1,035 K_c** (14 pontos, largura 0,07). Quem escorrega são sempre os anéis **internos** (9 kpc, depois 9,45 e 9,9 kpc): em 1,0 K_c, os dois de dentro giram 16,7 e 8,3 mrad/Myr mais rápido que o aglomerado.

| | resultado | critério | |
|---|---|---|---|
| **J1** a média persiste | 13 de 14 K da janela com deriva ≤ 0,02 (93 %) | ≥ 80 % | **passou** |
| **J2** sincronização parcial | 14 de 14 com aglomerado ≥ 6 e ≥ 1 escorregando | ≥ 80 % | **passou** |
| **J3** caos de fase | 3 de 14 com λ_max > 5 × 10⁻⁴ (21 %) | ≥ 50 % | **reprovado** |
| **J4** um só atrator estatístico | 10 de 14 com espalhamento ≤ 0,03 (71 %) | ≥ 80 % | **reprovado** |
| **J5** a janela estreita com N | larguras 0,105 · 0,075 · 0,065 · 0,065 (N = 8 · 12 · 16 · 24) | estritamente decrescente | **reprovado** (16 = 24) |

Com ruído (N = 12, 5 sementes): janela de 0,095 K_c.

Apostas: J1 (70 %), certa; J2 (55 %), certa; J3 (55 %), errada; J4 (70 %), errada; J5 (55 %), errada, por empate na última comparação.

## O que o resultado diz

**1. É o caso (2) do colaborador: um regime real.** Dentro da janela, a média de C fica parada por 16 Gyr (deriva ≤ 0,02 em 13 de 14 pontos) enquanto os anéis continuam se movendo. Não é uma média caminhando devagar para o travamento: abaixo de K_L não há ponto fixo para onde caminhar, e a média não deriva. É sincronização parcial: um aglomerado de 7 a 10 anéis trava, e 2 a 5 anéis internos escorregam por ele, para sempre.

**2. O regime tem duas partes, e só a de baixo é caótica.** De 0,990 a 1,035 K_c, com dois anéis escorregando, λ_max ≈ 0: é movimento regular (quase-periódico, num toro de duas frequências), o mesmo para qualquer ponto de partida (espalhamento ≤ 0,003), com C̄ de 0,68 a 0,72. De 0,970 a 0,985, com três a cinco anéis escorregando, λ_max > 0 (caos de fase, como em Popovych et al.), e o resultado depende um pouco do ponto de partida (espalhamento 0,03–0,08). Os J3 e J4 reprovaram pela mesma razão: a janela é majoritariamente regular, e só a sua borda inferior é caótica e multiestável. Abaixo da janela, o caos é forte (λ ≈ 2 × 10⁻³) e a média oscila muito (deriva até 0,17), com quase nenhum aglomerado.

**3. Onde fica 0,627.** C̄ = 0,627 cai em K = 0,975 K_c, na **borda caótica** da janela: 9 anéis travados e 3 internos escorregando, média estável (deriva 0,013), mas com λ_max > 0 e um pouco de dependência do início. A parte regular e robusta da janela começa em 0,68. Isso é um resultado do modelo, não um encaixe: neste disco, a coerência observada corresponderia à fronteira entre o regime caótico e o regular, onde a organização é a mínima que ainda persiste. Não é afirmação sobre a NGC 628.

**4. A janela é estreita, mas não some.** 0,07 K_c em N = 12; 0,105 em N = 8; 0,065 em N = 16 e 24. Ela estreita de 8 para 16 e depois para de estreitar, na resolução da grade (0,005). O ruído a alarga (0,095). O caso (3) do colaborador não piora sem limite com N: a janela parece convergir para ≈ 0,065 K_c, cerca de 6 % do acoplamento.

## Para os caminhos do colaborador

- **Caminho A tem objeto.** Existe um regime móvel persistente e, na parte regular, robusto ao ponto de partida. Uma memória adaptativa sem alvo poderia (a) alargar a janela ou (b) mover o disco da borda caótica para a parte regular. A pergunta seguinte seria a dele: uma memória que preserve a organização estatística de um movimento, e não uma configuração.
- **Caminho B continua necessário para a robustez em K.** A janela tem ≈ 6 % de K_c e não alarga com N. Se o objetivo é uma organização parcial que não exija acertar K a 6 %, é a física do acoplamento que tem de mudar.
- **Uma observação física para registro:** quem escorrega são os anéis internos, onde o cisalhamento é maior (Ω ∝ 1/r). O aglomerado são os anéis de fora. Isso é uma previsão do modelo que dá para comparar com a fase do m = 5 anel a anel na NGC 628: se o modelo valesse, a fase coerente ficaria nos raios externos da zona estável, e os anéis de 9–10 kpc mostrariam fase deslizante. Fica como pergunta, não como teste.

Placar: 41 testes numerados (o 25 sem resultado), mais o teste do ato A. 41: J1 e J2 passaram, J3, J4 e J5 reprovaram. 58 defeitos nesta numeração (nenhum novo), 1 emenda.
