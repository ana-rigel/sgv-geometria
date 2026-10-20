# Predição do teste 45 (43-G: um warp geométrico produz o A₅ da NGC 628?)

20/10/2026 · escrita antes de rodar · pipeline do preprint (ngc628/analysis_pipeline.py) sem mudança · máscara e grade do MOM1 NA do THINGS · Ana Rigel

## De onde vem

Do plano do colaborador (20/10) e do teste 43. O teste 43 mostrou que a amplitude do m = 5 na zona estável é real: ⟨A₅⟩ = 1,51 km/s com anéis da largura do feixe, IC 95 % [1,43; 1,61], contra q99 de 0,38 no ruído com a correlação do feixe. A zona (254″–395″) coincide com o disco externo onde Aniyan et al. (2018) modelam um warp a partir de 250″; o colaborador lembrou que Sylos Labini et al. (2023) relatam PA e inclinação constantes só até ≈ 300″ e uma mudança forte de PA entre 200″ e 400″. O pipeline do artigo usa geometria fixa (i = 7°, PA = 25°) e o pixel de referência do mapa como centro, que está a ≈ 13,6″ do núcleo do catálogo PHANGS. A pergunta (H₀ do colaborador): **um disco com rotação circular, orientação variando com o raio e centro deslocado, depois do processamento do artigo, gera um A₅ aparente do tamanho do observado?**

## Os mapas sintéticos

Na grade e com a máscara de pixels válidos do MOM1 NA:

- **Rotação circular** plana, v = 184 km/s (para que v sen 7° ≈ 22,4 km/s, a amplitude do m = 1 medida no teste 43), V_sys = 656,1 km/s.
- **Anéis inclinados:** i(r) = 7° + Δi · f(r) e PA(r) = 25° + ΔPA · f(r), com f = 0 até 250″, subindo linearmente até 1 em 400″, e 1 depois. Cada pixel do céu é atribuído ao seu raio por iteração (a geometria do anel depende do raio).
- **Centro:** no núcleo do catálogo PHANGS (RA 24,17385°, Dec 15,78364°) ou no pixel de referência do mapa.
- **Feixe:** o mapa é convolvido com o feixe NA (11,88″ × 9,30″, BPA −70,34°) antes da máscara.
- **Ruído:** 30 realizações de ruído branco convolvido com o feixe e escalado a σ = 1,83 km/s (o resíduo do teste 43), semente 4500; e uma versão sem ruído.

**Malha:** ΔPA ∈ {0°, 10°, 20°, 40°} × Δi ∈ {−3°, 0°, +3°} × centro ∈ {núcleo, pixel de referência}: 24 configurações.

**Medida:** o pipeline do artigo, sem mudança, com geometria fixa (7°, 25°, 7,3 Mpc, centro no pixel de referência) e anéis da largura do feixe (11 anéis de 0,42 kpc em 9–14 kpc, como no teste 43). ⟨A₅⟩ e as amplitudes dos outros modos.

**Controle positivo (relatado):** sobre a configuração de warp mais forte (ΔPA = 40°, Δi = +3°, centro no núcleo), um campo **vertical** m = 5 de 1,55 km/s (v_z = 1,55 cos 5ψ no plano do anel; projeção cos i). E a conta, para comparação, do m = 5 **no plano** que daria o mesmo A₅: u · sen 7° = 1,51, u ≈ 12,4 km/s.

## Conta prévia

- A galáxia é quase de frente: cos 7° = 0,9925. Um erro de PA praticamente só gira o m = 1 (muda a fase dele); um erro de inclinação só reescala o m = 1. O que vaza para outros modos vem do estiramento 1/cos i − 1 ≈ 0,0075: no m = 3, ~22 km/s × 0,0075 / 2 ≈ 0,08 km/s; no m = 5, segunda ordem, ~22 × 0,0075² ≈ 0,001 km/s.
- O centro deslocado em δ/r ≈ 0,48/9–14 ≈ 0,03–0,05 gera m = 0 e m = 2 de ~22 × 0,04 ≈ 0,9 km/s; m = 3 de ~22 × 0,04² ≈ 0,04 km/s; m = 5 em quarta ordem, ~10⁻⁴ km/s.
- Com a curva plana, o borramento pelo feixe quase não mexe no campo.
- **Esperado:** sem ruído, A₅ geométrico ≲ 0,01 km/s em todas as configurações; com ruído, ⟨A₅⟩ no nível do ruído (≈ 0,25–0,4). A H₀ deve ser rejeitada com folga. Um warp simples não produz o m = 5; o A₅ observado tem de vir de outra coisa, e numa galáxia a 7–8,5° a linha de visada mede sobretudo movimento vertical.

## Critérios

**J1, controle sem warp:** sem warp e com centro no pixel de referência, a mediana de ⟨A₅⟩ nas 30 realizações é **≤ 0,4 km/s**.

**J2, o warp não imita o sinal:** em **todas** as 24 configurações, o quantil 95 % de ⟨A₅⟩ nas 30 realizações é **< 1,43 km/s** (o limite inferior do IC observado).

**J3, o vazamento geométrico vai para o m = 3, não para o m = 5:** em todas as configurações com warp, sem ruído, **A₃ ≥ A₅**.

**J4, o controle positivo é recuperado:** com o m = 5 vertical injetado sobre o warp mais forte, ⟨A₅⟩ fica entre **1,35 e 1,75 km/s** em **≥ 90 %** das realizações.

Relatado: o A₅ sem ruído de cada configuração; as amplitudes A₁…A₁₀; a fase do m = 1 (para ver o warp agindo); o u equivalente no plano.

## Apostas (Claude, antes de rodar)

- **J1: 90 %.**
- **J2: 90 %.**
- **J3: 70 %.** As duas amplitudes sem ruído são muito pequenas, e o arredondamento numérico pode decidir.
- **J4: 90 %.**

## O que fecha

- **J2 passa:** um warp geométrico como o da literatura, com o centro deslocado e o feixe do THINGS, não produz o A₅ da NGC 628. A exclusão do warp na seção 4.3 do preprint pode ser mantida, mas com esta justificativa (um teste geométrico direto), e não com o Δv_sys. A interpretação do A₅ fica entre uma perturbação no plano de ≈ 12 km/s e uma vertical de ≈ 1,5 km/s, e os dados de um só ângulo de visão não separam as duas.
- **J2 reprova:** alguma geometria plausível produz um A₅ do tamanho observado; a detecção precisa ser revista antes de qualquer interpretação.

Um julgamento por hipótese; sem emenda. Instrumento: teste45.py, escrito depois do commit desta predição.
