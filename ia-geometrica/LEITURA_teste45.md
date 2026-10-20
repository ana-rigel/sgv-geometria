# Leitura do teste 45 (43-G: um warp geométrico produz o A₅ da NGC 628?): J1, J2, J3 e J4 PASSARAM. Nenhuma geometria plausível chega perto: o warp põe no m = 5 menos de 0,003 km/s; o centro deslocado, porém, põe até 1 km/s no m = 2

**Predição:** PREDICAO_teste45_warp_e_m5.md (3d16a90), antes de escrever o instrumento. **Instrumento:** teste45.py (a33733f), com o pipeline do preprint sem mudança. **Resultado:** resultados_teste45.json. Mapas sintéticos na grade e máscara do MOM1 NA; rotação circular plana de 184 km/s; warp a partir de 250″; feixe NA; 30 realizações de ruído (σ = 1,83 km/s, com a correlação do feixe); anéis da largura do feixe. Quatro julgamentos; sem emenda.

| | sem ruído | com ruído (30) |
|---|---|---|
| A₅, as 24 configurações | **0,0000 – 0,0024** km/s | mediana 0,246, q95 **0,342–0,343** em todas |
| A₃, configurações com warp | 0,006 – 0,083 km/s | |
| A₂, centro no núcleo | **0,15 – 1,00** km/s | |
| A₂, centro no pixel de referência | 0,000 | |
| fase do m = 1 | gira 4,7° · 9,4° · 18,9° com ΔPA = 10° · 20° · 40° | |

Controle positivo (m = 5 vertical de 1,55 km/s sobre ΔPA = 40°, Δi = +3°, centro no núcleo): mediana de ⟨A₅⟩ **1,47**, dentro de 1,35–1,75 em 29 de 30 realizações. Um m = 5 no plano daria o A₅ observado com **u ≈ 12,4 km/s** (1,51 / sen 7°).

| | resultado | critério | |
|---|---|---|---|
| **J1** controle sem warp | mediana 0,246 | ≤ 0,4 | **passou** |
| **J2** o warp não imita o sinal | q95 ≤ 0,343 em todas | < 1,43 em todas | **passou** |
| **J3** o vazamento vai para o m = 3 | A₃ > A₅ em todas as 23 com warp | A₃ ≥ A₅ | **passou** |
| **J4** controle positivo | 97 % em 1,35–1,75 | ≥ 90 % | **passou** |

Apostas: J1 (90 %), J2 (90 %), J3 (70 %), J4 (90 %): as quatro certas.

## O que o resultado diz

**1. A hipótese geométrica (H₀ do colaborador) está rejeitada com folga.** Um warp que gira o PA até 40° e muda a inclinação em ±3° na zona estável, com o centro deslocado e o feixe do THINGS, põe no máximo 0,0024 km/s no m = 5 — seiscentas vezes menos que o observado. Com ruído, o A₅ fica no nível do ruído (q95 0,34), muito abaixo do limite inferior observado (1,43). Como a conta prévia previu, numa galáxia a 7°, um erro de geometria quase só gira ou reescala o m = 1 (a fase do m = 1 gira metade do ΔPA, na média da zona) e vaza pouco para o m = 3; para o m = 5 o vazamento é de segunda ordem.

**2. O que o preprint pode dizer sobre o warp.** A exclusão do warp na seção 4.3 pode ficar, mas com outra justificativa: não o Δv_sys (que não enxerga um warp de inclinação ou de PA), e sim este teste geométrico direto, com mapas sintéticos pelo mesmo pipeline. A conclusão é mais forte que a do texto atual: mesmo que o warp exista na zona, como a literatura indica, ele não produz o A₅.

**3. Um efeito que o teste não procurava: o centro deslocado contamina o m = 2.** Com o centro verdadeiro no núcleo do catálogo PHANGS (13,6″ do pixel de referência usado pelo pipeline), um disco sem nenhuma estrutura ganha um A₂ de 0,15 a 1,0 km/s, conforme o warp. O A₂ observado é 1,71 km/s. O preprint compara A₅ com A₂ (A₅/A₂ = 0,920, o "ambiente harmônico silencioso"); uma parte do A₂ pode ser artefato de centro, e essa razão precisa ser recalculada com o centro correto.

**4. A interpretação do A₅ fica entre duas físicas.** O controle positivo mostra que um m = 5 vertical de ≈ 1,5 km/s reproduz o sinal; um m = 5 no plano precisaria de ≈ 12 km/s. Com um só ângulo de visão, os dados não separam as duas. Numa galáxia quase de frente, a leitura mais econômica é uma ondulação vertical de baixa amplitude; uma perturbação no plano de 12 km/s seria grande para um disco externo e deveria aparecer em outros traçadores. Isso é uma hipótese, não um resultado deste teste.

## Correções para a versão 2 do preprint (somadas às do teste 43)

- Seção 4.3: trocar a justificativa do Δv_sys pelo teste geométrico direto (warp de até 40° em PA e ±3° em inclinação dá A₅ < 0,003 km/s).
- Centro: usar o núcleo, não o pixel de referência; recalcular A₂ e a razão A₅/A₂.
- Interpretação: dizer que, a i ≈ 7–8,5°, o A₅ medido equivale a ≈ 1,5 km/s de movimento vertical ou ≈ 12 km/s no plano.

Placar: 45 testes numerados (o 25 sem resultado), mais o teste do ato A. 45: J1–J4 passaram. 61 defeitos nesta numeração (nenhum novo), 1 emenda.
