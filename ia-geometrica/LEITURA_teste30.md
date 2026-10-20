# Leitura do teste 30 (a seca silenciosa em Juara) — J1 e J2 REPROVADOS; a v0 é um índice de seca com outro nome

**Predição:** PREDICAO_teste30_seca_silenciosa.md (f7509b4), antes de abrir os dados. **Dados:** clima/dados/era5land_juara_horario.csv.gz (2ª rodada do download, completa, sem campos vazios). **Instrumento:** teste30.py. **Resultado:** resultados_teste30.json. Dois julgamentos; sem emenda.

**Dias na medida (2018–2025):** 2.922; seca profunda em 595 (20 %); silenciosos (superfície normal ou molhada) 1.098; seca silenciosa em **160**, o bastante para J2 não ser inconclusivo.

**Escolhas na calibração (2010–2017):** nulo **SPEI-90** (AUC 0,775); v0 **R2**, o andar de τ ≈ 67 dias (AUC 0,760). Todas as candidatas: SPI 30/90/180 = 0,729 / 0,772 / 0,703; SPEI 30/90/180 = 0,732 / 0,775 / 0,708; v0 R1 / R2 / R3 = 0,688 / 0,760 / 0,700; vincos R1−R3 / R2−R3 / R2−R4 = 0,655 / 0,710 / 0,759.

| medida 2018–2025 | AUC v0 (R2) | AUC nulo (SPEI-90) | diferença (IC 95 %, blocos de 90 dias) |
|---|---|---|---|
| todos os dias | **0,780** (0,660–0,890) | 0,778 | +0,002 (−0,049; +0,035) |
| dias silenciosos | **0,775** (0,653–0,908) | 0,781 | −0,006 (−0,059; +0,039) |

**J1, a v0 acompanha a seca profunda:** AUC 0,780, acima do acaso, abaixo do 0,80 exigido. **Reprovado.**
**J2, a v0 vê a seca silenciosa melhor que o índice padrão:** diferença −0,006. **Reprovado.**

Apostas: J1 passa (70 %), errada por 0,02; leitura escolhida R2 ou R2−R3 (60 %), certa (R2); nulo SPEI-90 ou -180 (65 %), certa (SPEI-90); J2 reprova (90 %), certa, e a diferença caiu na faixa apostada (−0,03 a +0,02); J2 inconclusivo (15 %), certa a não ocorrência.

## O que o resultado diz

A v0 e o índice padrão fazem a mesma conta e chegam ao mesmo lugar. O andar que a calibração escolheu é o R2, que lembra o balanço de água dos últimos ≈ 2 meses com peso exponencial; o índice escolhido é o SPEI de 90 dias, que soma o balanço dos últimos 3 meses com peso igual. A AUC dos dois difere na terceira casa, em todos os dias e nos silenciosos.

O **vinco**, a peça central do texto que deu origem ao teste, ficou abaixo do nível simples nos dois casos em que se compara com o andar 3 (R1−R3 0,655 e R2−R3 0,710 contra R2 0,760 na calibração). Medir a distância entre a memória curta e a identidade longa dá *menos* informação sobre o solo profundo do que a memória média sozinha. Faz sentido físico: o solo de 28–100 cm é ele próprio uma memória de algumas semanas a meses do que choveu e evaporou; o que o descreve é um acumulador nessa escala, não uma diferença entre escalas.

E a "seca silenciosa" não é silenciosa para um índice de 3 meses: quando chove na superfície, a camada de cima se molha, mas a soma de 90 dias quase não se mexe, e ela continua dizendo "seco". Nos dias silenciosos a AUC dos dois é a mesma dos outros dias. O que o texto apresentava como algo que só a v0 perceberia, o índice padrão já percebe, porque olha a escala certa.

A ressalva da predição vale aqui com força: a verdade é o solo calculado pelo ERA5-Land a partir da mesma chuva e da mesma evaporação. O teste diz que nenhum dos dois integra melhor do que o outro esse modelo de solo; o solo real de Juara só uma sonda diz.

## O que fica para Juara

Para acompanhar a seca profunda na região, o **SPEI de 3 meses** (índice público, calculado por vários serviços de clima) faz o que a v0 faz, com nota ≈ 0,78 contra o solo do ERA5-Land. A v0 não traz um alarme de seca novo.

## Para a lista de defeitos de desenho

41. O texto de origem atribuía ao vinco (andar 1 − andar 4) a percepção da seca profunda; a predição herdou o vinco entre as candidatas sem perguntar antes em que escala o solo profundo guarda memória. Uma conta prévia (a escala de memória do solo de 28–100 cm no ERA5-Land, por correlação com o balanço acumulado em várias janelas, na calibração) teria mostrado que a pergunta era de escala, não de diferença entre escalas.

Placar: 30 testes numerados (o 25 sem resultado). 26: J1 passou, J2 reprovou; 27: ambos reprovaram; 28: J1 passou, J2 reprovou; 29: ambos reprovaram; 30: ambos reprovaram. 41 defeitos, 1 emenda.
