# Leitura do teste 47 (a janela no limite contínuo): J1, J2 e J4 PASSARAM; J3 REPROVADO, por uma conta prévia errada. A janela não some na rotação sólida; ela só some quando Ω cresce linearmente com o raio (β = 2), e segue a lei largura ≈ 0,056 (2 − β)^1,6 K_c

**Predição:** PREDICAO_teste47_limite_continuo.md (40347dd), antes de calcular. **Instrumento:** teste47.py (c4c0a00, mais uma correção, abaixo). **Resultado:** resultados_teste47.json. Quatro julgamentos; sem emenda.

**Correção do instrumento, sem efeito nos números:** a primeira rodada calculou todas as janelas e quebrou na hora de julgar, porque o arredondamento gerou β = −0,0, e a chave "−0.0" não casava com "+0.0" das simulações. A correção (somar 0,0 à grade de β) só muda o nome; a segunda rodada deu números idênticos aos da primeira.

| β | janela contínua (K/K_c) | largura | K_L pela fórmula | ρ no começo → no fim | N = 48 simulado (largura · K_L) |
|---|---|---|---|---|---|
| −0,6 | 0,822–1,079 | 0,257 | 1,0792 | 0,39 → 0,86 | |
| −0,4 | 0,844–1,072 | 0,228 | 1,0715 | 0,39 → 0,86 | ≥ 0,185 · 1,085 |
| −0,2 | 0,866–1,064 | 0,199 | 1,0639 | 0,40 → 0,86 | ≥ 0,180 · 1,080 |
| 0 | 0,886–1,057 | **0,171** | 1,0565 | 0,39 → 0,85 | ≥ 0,165 · 1,075 |
| +0,2 | 0,905–1,050 | 0,145 | 1,0492 | 0,39 → 0,85 | 0,135 · 1,065 |
| +0,4 | 0,923–1,042 | 0,120 | 1,0421 | 0,40 → 0,84 | 0,110 · 1,060 |
| +0,6 | 0,939–1,036 | 0,097 | 1,0351 | 0,39 → 0,84 | |
| +0,9 | 0,960–1,026 | **0,066** | 1,0253 | 0,40 → 0,83 | |

(passo de 0,1 no resultados.) Depois do julgamento, sem critério: β = 1,0 → 0,056; β = 1,5 → 0,019; **β = 2,0 → 0** (K_L = K_c exatamente); β = 2,5 → 0,014.

| | resultado | critério | |
|---|---|---|---|
| **J1** o fim converge | diferenças 0,013–0,019 nos cinco | ≤ 0,02 | **passou** |
| **J2** a largura converge | 4 de 5 a ≤ 0,02 (−0,4: 0,043, mas o N = 48 é um mínimo) | ≥ 4 | **passou** |
| **J3** a lei de β | estritamente decrescente, mas β = 0,9 dá 0,066 | ≤ 0,02 em 0,9 | **reprovado** |
| **J4** a curva plana sobrevive | 0,171 | ≥ 0,12 | **passou** |

Apostas: J1 (80 %), J2 (70 %), J4 (85 %), certas; J3 (80 %), errada.

## O que o resultado diz

**1. A janela de sincronização parcial é uma função da forma da curva de rotação e sobrevive ao contínuo.** Para a curva plana, ela tem 0,171 K_c com infinitos anéis, perto dos 0,165 de 48 anéis simulados. A fórmula de K_L (com todos travados, Ω = 0, e uma minimização em uma variável) bate com a solução completa a 0,0005 em todos os β: o fim da janela é uma conta de uma linha.

**2. A conta prévia do J3 estava errada, e o erro ensina.** Escrevi que, para β → 1, as frequências tenderiam à distribuição uniforme. Não: para β → 1, Ω ≈ const + (β − 1) ln r, e com r uniforme a densidade de ln r é proporcional a r — ainda assimétrica, mais densa nos anéis externos, por um fator 14/9. A distribuição só fica uniforme quando Ω é linear em r, ou seja, **β = 2** (v ∝ r²). É ali, e só ali, que a janela some: K_L = K_c, travamento direto, como no controle uniforme do teste 42. Entre β = −0,6 e 2,5, a largura segue de perto

  **largura ≈ 0,056 · (2 − β)^1,6 K_c** (ajuste depois do julgamento, erro máximo 0,003 em −0,6 ≤ β ≤ 1,5),

e volta a crescer depois de β = 2, quando a assimetria se inverte (densa nos anéis internos).

**3. Um invariante que eu não procurava.** Em todos os β, a coerência no começo da janela (metade dos anéis travada) é ρ ≈ 0,39–0,40, e no fim (todos travados) ρ ≈ 0,83–0,86. O que muda com β é o K em que esses estados acontecem, não a coerência deles.

**4. O que a normalização esconde.** Tudo está em K/K_c, com a mesma abertura de frequências. Fisicamente, perto da rotação sólida (β → 1) a abertura de frequências vai a zero e K_c também: o disco sincroniza com qualquer acoplamento. A lei acima descreve a forma da janela, não quão fácil é chegar a ela.

## O que isso significa para a pergunta da Ana

No modelo, uma galáxia com rotação diferencial mantém regiões parcialmente sincronizadas sem que todos os anéis girem juntos sempre que a distribuição radial das velocidades angulares é assimétrica — o que acontece para toda curva de rotação fisicamente usual (de caindo a sólida, β ≤ 1). A largura da faixa de acoplamento em que isso ocorre é dada pela forma da curva, ≈ 0,056 (2 − β)^1,6 K_c: de ≈ 0,26 K_c para curvas que caem a ≈ 0,06 K_c perto da rotação sólida. Os anéis que deslizam são os do lado esparso da distribuição (os internos, para β < 2). Isso continua sendo uma propriedade do modelo de osciladores; a correspondência com o acoplamento físico de um disco (autogravidade, ondas de densidade) não foi demonstrada.

## Para a lista de defeitos de desenho

63. A conta prévia afirmou que β → 1 leva à distribuição uniforme sem calcular a densidade de Ω = (β − 1) ln r com r uniforme. Essa densidade é ∝ r, assimétrica por 14/9; a uniforme exige Ω linear em r (β = 2). Uma linha de cálculo de mudança de variável teria posto o critério do J3 no lugar certo.

Placar: 47 testes numerados (o 25 sem resultado), mais o teste do ato A. 47: J1, J2, J4 passaram, J3 reprovou. 63 defeitos nesta numeração, 1 emenda.
