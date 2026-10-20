# Leitura do teste 43 (43-0: o sinal do m = 5 sobrevive ao feixe?): J1, J2 e J3 PASSARAM; J4 e J5 REPROVADOS. A amplitude do m = 5 é real; a coerência de fase não se distingue do ruído do feixe e não é própria do m = 5

**Predição:** PREDICAO_teste43_auditoria_feixe.md (b56ad9c), antes do passo 2. **Instrumento:** teste43.py, sobre ngc628/analysis_pipeline.py (o pipeline do preprint, sem mudança). **Resultado:** resultados_teste43.json. **Dados:** THINGS, NGC 628 MOM1 NA e RO (fora do repositório). Cinco julgamentos; sem emenda.

## Passo 1 (reprodução do preprint, antes da predição)

| | preprint | pipeline publicado, dados reais |
|---|---|---|
| ⟨A₅⟩ NA | 1,549 | 1,547 |
| ⟨A₅⟩ RO | 1,558 | 1,497 |
| Z | 4,10 | 5,06 |
| C_φ,5 (p) | 0,616 (0,005) | 0,612 (0,0026) |
| vazamento r (p) | +0,165 (0,65) | −0,681 (0,004) |
| anéis na zona | 12 | 16 |

O A₅ e a coerência reproduzem; o Z, o RO e o vazamento não. Os números do preprint vieram de outra versão do código.

## Passo 2 (o feixe considerado)

| | NA (anéis de 0,42 kpc, 11) | RO (anéis de 0,24 kpc, 20) |
|---|---|---|
| ⟨A₅⟩ | **1,511** | 1,511 |
| média do baseline | 0,794 | 0,895 |
| Z | **3,96** | 4,48 |
| C_φ,5 | **0,628** | 0,567 |

Amplitude média por modo (NA): A₂ 1,71 · A₃ 0,53 · A₄ 0,66 · **A₅ 1,51** · A₆ 1,09 · A₇ 0,67 · A₈ 0,73 · A₉ 0,39 · A₁₀ 0,58.
Coerência de fase por modo (NA): C₂ 0,78 · C₃ 0,33 · C₄ 0,73 · **C₅ 0,63** · C₆ 0,74 · C₇ 0,21 · C₈ 0,34 · C₉ 0,09 · C₁₀ 0,80.

Bootstrap por blocos de 12″ (NA): IC 95 % de ⟨A₅⟩ = **[1,43; 1,61]**, desvio 0,050 (o de pixels dava 0,009).
Resíduo depois do ajuste até n = 10: σ = 1,83 km/s; autocorrelação cai à metade em **12″** (ruído só do feixe: ≈ 7,4″).
Nulo de 300 mapas de ruído convolvidos com o feixe: ⟨A₅⟩ mediana 0,25, q99 **0,38**; C_φ,5 mediana 0,30, q95 **0,64**; Z mediana −0,09, q99 3,38.

| | resultado | critério | |
|---|---|---|---|
| **J1** o Z resiste ao feixe | 3,96 | ≥ 3 | **passou** |
| **J2** a amplitude resiste ao feixe | IC [1,43; 1,61] acima do baseline 0,79 | limite inferior > baseline | **passou** |
| **J3** o A₅ não é ruído do feixe | 1,51 contra q99 0,38 | > q99 | **passou** |
| **J4** a coerência não é ruído do feixe | 0,628 contra q95 0,640 | > q95 | **reprovado** |
| **J5** a coerência é própria do m = 5 | m = 10, 2, 6 e 4 são mais coerentes | o m = 5 o maior de 3–10 | **reprovado** |

Apostas: J1 (75 %), certa; J2 (90 %), certa; J3 (90 %), certa; J4 (70 %), errada; J5 (40 %), certa a reprovação.

## O que o resultado diz

**1. A amplitude do m = 5 é real.** Com anéis da largura do feixe, bootstrap por blocos e um nulo de ruído com a correlação do feixe, ⟨A₅⟩ = 1,51 km/s fica quatro vezes acima do que o ruído dá (q99 0,38) e bem acima dos modos vizinhos. É o segundo maior modo, depois do m = 2 dos braços. A detecção de amplitude do preprint se mantém. O Z, com a fórmula do artigo, cai de 5,06 para 3,96, e o próprio nulo mostra que essa fórmula não está calibrada (ruído puro chega a Z = 3,4 em 1 % dos mapas); o p certo é o do nulo, < 1 %.

**2. A coerência de fase não sustenta a "organização" do m = 5.** Com 11 anéis da largura do feixe, C_φ,5 = 0,628 fica abaixo do q95 de ruído puro (0,640), e o ruído real é ainda mais largo que o do nulo (autocorrelação de 12″ contra 7,4″), o que alargaria o nulo. Além disso, quatro outros modos têm fase mais coerente que o m = 5 (m = 10: 0,80; m = 2: 0,78; m = 6: 0,74; m = 4: 0,73). A coerência de fase é uma propriedade do campo de velocidades da NGC 628 em vários modos, ao menos em parte vinda da correlação entre anéis vizinhos; não é uma assinatura do m = 5.

**3. Consequências para o que veio depois.** A nota de síntese ("Phase Coherence and Informational Persistence…") e os testes 37–42 usaram C_φ = 0,627 como o valor observado de organização do m = 5. Esse número é a coerência de 11–16 anéis correlacionados, compatível com ruído do feixe e não exclusiva do m = 5. Os resultados dos testes 37–42 sobre o **modelo** continuam valendo como resultados do modelo; o seu vínculo com a NGC 628 por meio do 0,627 perde a base.

**4. Correções que o preprint precisa (versão 2 no Zenodo).**
- A incerteza do A₅: o ±0,315 é a dispersão entre anéis; o bootstrap correto (por blocos do feixe) dá ±0,05 na média; a frase do "√N com 2.000–5.000 pixels por anel" conta pixels, não feixes.
- O Z: calibrar pelo nulo de ruído do feixe, não pela fórmula; com anéis do feixe, Z = 3,96, p < 0,01 pelo nulo.
- O teste de vazamento: o substituto V_rot/√n é inválido, porque V_rot não é identificável no ajuste (colinear com c₁); e o pipeline publicado dá r = −0,68, não +0,165.
- A coerência de fase: retirar a afirmação de organização do m = 5, ou reformulá-la com o nulo do feixe e a comparação entre modos.
- A geometria: o centro do mapa está a ≈ 13,6″ do núcleo, e o warp de Aniyan et al. começa a 250″ (o 43-G continua necessário para a interpretação da amplitude, inclusive a mistura com movimento vertical em i ≈ 8°).

## Para a lista de defeitos de desenho

61. A conta prévia do J4 supôs o nulo de C_φ de 11 anéis independentes (q95 ≈ 0,5); o nulo com a correlação do feixe tem q95 0,64. A correlação entre anéis vizinhos, que motivou o teste, também alarga o nulo de fase, e a conta não a incluiu.

Placar: 43 testes numerados (o 25 sem resultado), mais o teste do ato A. 43: J1, J2, J3 passaram, J4 e J5 reprovaram. 61 defeitos nesta numeração, 1 emenda.
