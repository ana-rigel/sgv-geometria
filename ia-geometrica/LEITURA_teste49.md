# Leitura do teste 49 (a geometria da janela contra as velocidades de padrão de Speights et al. 2025): J1, J2 e J3 PASSARAM; J4 REPROVADO. O "rígido por dentro" do artigo é outra escala; a parte da zona que o modelo prevê rígida não foi medida; e o J2 passou pela letra com o sentido contrário: dentro da janela, o modelo nunca deixa a sobreposição deslizar inteira

**Predição:** PREDICAO_teste49_velocidade_de_padrao.md (f099a9c), antes de calcular. **Instrumento:** teste49.py (70fbdef). **Resultado:** resultados_teste49.json. **Dados:** Speights, Aust & Lu (2025), ApJ 981, 115, Figura 12d (H I, modelo PCM). A figura é JPEG; foi digitalizada por cor (58 pontos de Ωp com barra de erro, curva pontilhada de Ω), e a digitalização foi conferida sobrepondo os pontos à figura. Os pontos estão em ngc628/speights2025_fig12d.json. Quatro julgamentos; sem emenda.

## O que o artigo cobre

- O disco **rígido** de Speights et al. é o interno, até ≈ 4 kpc (corrotação em 3,4 kpc, m = 2). O **cisalhamento** é de ≈ 4 kpc para fora. A nossa zona começa em 8,7 kpc. O "oposto" relatado pelo colaborador não se aplica à zona do modelo: o artigo e o modelo falam de regiões diferentes do disco.
- O perfil do H I vai só até **310″** (10,6 kpc), cortado em R25 para evitar o warp. A sobreposição com a zona estável (254″–395″) é **254″–310″**, os 40 % internos. A região externa, que o modelo prevê rígida, **não foi medida**.

## Os dados na sobreposição (11 pontos)

| r | 258″ | 268″ | 278″ | 288″ | 298″ | 308″ |
|---|---|---|---|---|---|---|
| Ωp (km/s/kpc) | 24,0 | 21,3 | 18,8 | 18,2 | 17,0 | 16,9 |
| Ω | 26,8 | 25,4 | 23,9 | 22,3 | 20,6 | 19,4 |
| Ω − Ωp | 2,9 | 4,1 | **5,1** | 4,1 | 3,5 | 2,5 |
| barra de erro de Ωp (±) | 4,9 | 6,6 | 8,0 | 8,6 | 8,0 | 3,0 |

## O modelo

| curva | janela (K/K_c) | r\* no começo da janela | r\* no terço baixo | parte da janela com a sobreposição inteira deslizando |
|---|---|---|---|---|
| plana, 254″–395″ | 0,888–1,059 | 303″ (travados 303″–374″) | 273″–303″ | **nenhuma** |
| Aniyan (publicada), 254″–350″ | 0,790–1,048 | 279″ | 271″–279″ | **nenhuma** |

No começo da janela, o aglomerado **não encosta na borda externa**: na curva plana, ele ocupa 303″–374″, e as duas bordas deslizam. A borda externa entra no aglomerado logo depois (com 20 % da janela, os travados já vão de 278″ a 395″). A figura da geometria da janela ("rígido por fora") vale do primeiro quinto da janela em diante, não no começo.

## Julgamentos

| | resultado | critério | |
|---|---|---|---|
| **J1** a sobreposição cisalha | S = **0,90** | ≥ 0,5 | **passou** |
| **J2** os dados restringem K à parte baixa da janela | fração compatível = **0** | ≤ 1/3 | **passou pela letra** |
| **J3** o padrão gira mais devagar que o material | **11/11** pontos com Ωp < Ω | ≥ 80 % | **passou** |
| **J4** o atraso cresce para fora | inclinação **−0,44** km/s/kpc² | > 0 | **reprovado** |

Apostas: J1 (85 %), certa; J2 (60 %), certa pela letra; J3 (70 %), certa; J4 (35 %): reprovou, como a aposta inclinava. J1 e J3 não eram cegos (a figura e o texto do artigo foram vistos antes).

## O que o resultado diz

**1. O J2 passou com o sentido contrário ao que a predição esperava.** O critério "≤ 1/3 da janela compatível" foi escrito para quando a sobreposição inteira desliza na parte baixa da janela. O resultado foi zero: em nenhum K da janela a sobreposição desliza inteira, porque o r\* nunca passa de 303″. Pela letra, passou; pelo sentido, nenhuma parte da janela tem a sobreposição só deslizando, e com isso cai a premissa do J4 (defeitos 66 e 67).

**2. O J3 não separa o modelo das alternativas.** Ωp < Ω em toda a sobreposição só diz que a corrotação do padrão fica além de 310″. Isso vale para o aglomerado do modelo e também para qualquer onda rígida com corrotação mais para fora. A tabela de alternativas da predição pôs o sinal errado na onda rígida (defeito 68).

**3. Depois do julgamento, sem critério: a forma dos dados é a do modelo com a borda dentro da sobreposição.** O J4 supunha a sobreposição inteira deslizando, e o modelo calculado nega essa premissa. Com a borda r\* dentro da sobreposição, o modelo prevê três coisas, e os dados mostram as três nos valores centrais:
- Dentro de r\*, os anéis deslizam com o padrão caindo **mais rápido** que o material (S > 1, a cúspide de √(d² − a²)). Nos dados, de 258″ a 278″, **S = 1,82**.
- Em r\*, o atraso é máximo. Nos dados, ele é máximo em **278″** (5,1 km/s/kpc).
- Fora de r\*, o padrão fica rígido e o atraso diminui até zero na corrotação do aglomerado. Nos dados, de 278″ para fora, **S = 0,43** e o atraso cai.

A curva publicada de Aniyan et al., que é um dado independente (velocidade de rotação, não Ωp), põe o r\* em **271″–279″** em todo o terço baixo da janela, por causa da ondulação que o teste 48 achou. A curva plana põe r\* em 278″ com 20 % da janela. O nível também cabe: Ωp na borda, 16,9 km/s/kpc, iguala o Ω extrapolado em **331″**, e a corrotação do aglomerado no modelo plano nesse K é **327″**. Os números estão em diagnostico_teste49_pos_julgamento.txt.

**4. Por que isso não é um resultado.**
- É um ajuste depois do julgamento.
- O atraso medido fica **dentro de 1σ** em todos os pontos (5,1 contra ±8,0 no pico).
- O PCM é regularizado (Tikhonov), e a regularização suaviza degraus. Os próprios autores mostram que um degrau verdadeiro sai parecido com uma rampa.
- Os 11 pontos não são independentes.
- A curva de Ω deles cai como **r^−0,90** em v na sobreposição, mais rápido que Kepler. É o mesmo sintoma do teste 48: a cinemática a 6–8° de inclinação, nessa faixa, não é só rotação circular.
- O Ωp do H I mistura todos os m, e o modelo fala do m = 5.

O que se pode dizer é mais modesto: os dados **não contradizem** a geometria do modelo na única parte da zona em que foram medidos, e o perfil deles tem a forma que o modelo dá com a borda em ≈ 278″, que é onde a curva de rotação independente a põe.

**5. O que vira predição para o próximo teste.** Com r\* ≈ 278″, o modelo prevê, **além de 310″**, o padrão rígido:
- Ωp ≈ constante ≈ 17 km/s/kpc até a borda externa do aglomerado;
- corrotação em ≈ 330″;
- fora dela, Ωp > Ω.

Isso só se testa medindo Ωp no H I de 310″ a 395″, a região que Speights et al. cortaram por causa do warp. Isso exige uma medida de Ωp que trate o warp, por exemplo Tremaine–Weinberg ou a equação de continuidade em anéis inclinados, com a geometria de Aniyan et al.

## Para a lista de defeitos de desenho

66. A conta prévia supôs que, no começo da janela, o aglomerado encosta na borda externa (r\* ≈ 324″). O solver do teste 46 o põe no meio-externo (303″–374″), com as duas bordas deslizando. O r\*(K) era calculável antes de escrever os critérios, e teria mostrado que a sobreposição nunca desliza inteira dentro da janela.
67. O J2 não tinha limite inferior: passa com 0, que significa "nenhuma parte da janela é compatível", o contrário do que o "O que fecha" dizia. O J4 foi escrito sobre uma premissa (sobreposição inteira deslizando) que o próprio modelo, calculado, nega. O critério certo teria sido sobre a posição do máximo do atraso, com o r\* calculado.
68. A tabela de alternativas trocou o sinal da onda rígida. Com corrotação dentro da sobreposição, Ω − Ωp < 0 fora dela; Ω − Ωp > 0 só põe a corrotação além. O J3 não separava o modelo de uma onda rígida com corrotação mais para fora, e o "O que fecha" do J3 sem o J4 apontou a direção errada ("mais para dentro").

Placar: 49 testes numerados (o 25 sem resultado), mais o teste do ato A. 49: J1, J2, J3 passaram, J4 reprovou. 68 defeitos nesta numeração, 1 emenda.
