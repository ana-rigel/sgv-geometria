# Predição do teste 43 (43-0: o sinal do m = 5 sobrevive ao feixe?)

20/10/2026 · escrita antes de rodar o passo 2 · pipeline do preprint (analysis_pipeline.py, Zenodo 10.5281/zenodo.20821463) · dados THINGS NGC 628 MOM1 (NA e RO) · Ana Rigel

## De onde vem

Da conversa de 20/10. O colaborador propôs auditar a exclusão do warp no artigo do m = 5 (43-G). Ao ler o pipeline publicado, apareceu um problema anterior: o feixe do THINGS na NGC 628 (NA 11,88″ × 9,30″; RO 6,85″ × 5,57″, do HISTORY do cabeçalho) cobre ~50 pixels de 1,5″ no NA, e o pipeline trata pixels e anéis como independentes. O bootstrap sorteia pixels um a um; o Z divide pela raiz do número de anéis, com anéis de 0,31 kpc (8,8″), mais estreitos que o feixe; o nulo de C_φ supõe fases de anéis independentes. Antes de perguntar se um warp imita o sinal, é preciso saber se o sinal resiste à correlação do feixe.

## Passo 1, já rodado antes desta predição (sem julgamento)

O pipeline publicado, sem mudanças, nos dados reais: ⟨A₅⟩ NA = 1,547 (preprint 1,549); RO = 1,497 (preprint 1,558); Z = 5,06 (preprint 4,10); C_φ,5 = 0,612 com p = 0,0026 (preprint 0,616, p = 0,005); vazamento r = −0,681, p = 0,004 (preprint +0,165, p = 0,65); 16 anéis na zona (preprint 12); dispersão de A₅ entre anéis 0,328 (≈ o ±0,315 do preprint); bootstrap de pixels ±0,009. Amplitudes médias na zona: A₂ 1,70 · A₃ 0,55 · A₄ 0,63 · **A₅ 1,55** · A₆ 1,10 · A₇ 0,71 · A₈ 0,73 · A₉ 0,45 · A₁₀ 0,55; baseline (n = 2–10 sem o 5) média 0,804, desvio 0,587.

## Passo 2: o mesmo pipeline com o feixe considerado

Geometria, distância, velocidade sistêmica, máscara e decomposição do pipeline publicado, sem mudança (i = 7°, PA = 25°, 7,3 Mpc, n ≤ 10). Mudam só quatro coisas:

1. **Anéis da largura do feixe:** 0,42 kpc (11,88″ a 7,3 Mpc) no NA, de 9 a 14 kpc (11 anéis). No RO, 0,24 kpc (6,85″).
2. **Bootstrap por blocos:** em cada anel, os pixels são agrupados em blocos de 8 × 8 pixels (12″), e o sorteio é de blocos, não de pixels. 1.000 repetições, semente 43.
3. **Nulo de mapas de ruído:** 300 mapas sintéticos = campo axissimétrico (V_sys + V sen i cos ψ do próprio ajuste, anel a anel) + ruído branco convolvido com o feixe NA (gaussiana 11,88″ × 9,30″, BPA −70,34°), escalado para o desvio-padrão do resíduo dos dados depois do ajuste até n = 10 na zona, com a mesma máscara. Cada mapa passa pelo mesmo pipeline. Semente 4300.
4. **Controle interno das fases:** C_φ de cada modo n = 2…10 nos dados, com os anéis do feixe.

O ruído do nulo é só ruído com a correlação do feixe; estrutura real do disco em outras escalas fica fora dele. Por isso o item 4 (comparar o m = 5 com os outros modos nos próprios dados) é o controle que não depende de modelo.

## Conta prévia

- Com anéis de 0,42 kpc, N passa de 16 para 11, e anéis vizinhos ficam a ~1 feixe (correlação do ruído ≈ 0,25 nessa distância). A mesma fórmula do Z cai por ≈ √(11/16) ≈ 0,83, se as amplitudes não mudarem: de 5,06 para ≈ 4,2. A fórmula ainda trata a dispersão entre modos como ruído do A₅, o que não é ruído de medida.
- O bootstrap por blocos deve alargar o intervalo em ≈ √(pixels por bloco) = 8 × em relação ao de pixels: de ±0,009 para ≈ ±0,07. Ainda bem abaixo da diferença entre A₅ (1,55) e a média do baseline (0,80).
- Num mapa de ruído com a correlação do feixe e σ igual ao resíduo, cada anel tem ~9.000 pixels e ~160 feixes; a amplitude de ruído esperada por modo é da ordem de σ·√(π/N_feixes). Com σ de alguns km/s, isso dá A ≈ 0,3–0,6 km/s. O A₅ = 1,55 deve ficar bem acima da distribuição nula, e as fases do ruído devem ter C_φ perto do acaso de 11 anéis (≈ 0,27).
- O A₆ (1,10) e o A₂ (1,70) também estão acima do baseline. Se o disco tiver estrutura coerente em vários modos, o m = 5 pode não ser o mais coerente.

## Critérios

**J1, o Z resiste ao feixe:** com anéis do feixe (NA), o Z (mesma fórmula) é **≥ 3**.

**J2, a amplitude resiste ao feixe:** o limite inferior do IC 95 % do bootstrap por blocos de ⟨A₅⟩ (NA, anéis do feixe) é **maior que a média do baseline** dos mesmos anéis.

**J3, o A₅ não é ruído do feixe:** o ⟨A₅⟩ observado (NA, anéis do feixe) é maior que o quantil 99 % do ⟨A₅⟩ nos 300 mapas de ruído.

**J4, a coerência não é ruído do feixe:** o C_φ,5 observado (NA, anéis do feixe) é maior que o quantil 95 % do C_φ,5 nos 300 mapas de ruído.

**J5, a coerência é própria do m = 5:** nos dados (NA, anéis do feixe), o C_φ do m = 5 é o **maior** entre os modos n = 3…10.

Relatado: tudo também no RO (anéis de 0,24 kpc); o Z e o C_φ do nulo; as amplitudes de todos os modos com os anéis do feixe; a autocorrelação do resíduo (para ver se o ruído real é mais largo que o feixe).

## Apostas (Claude, antes de rodar)

- **J1: 75 %.**
- **J2: 90 %.**
- **J3: 90 %.**
- **J4: 70 %.** Com 11 anéis, o nulo de C_φ é largo (q95 ≈ 0,5).
- **J5: 40 %.** O m = 6 e o m = 4 podem ter fase tão organizada quanto o m = 5, se o disco tiver estrutura coerente em vários modos.

## O que fecha

- **J1–J4 passam:** a amplitude e a coerência do m = 5 resistem à correlação do feixe. O preprint precisa corrigir a forma das incertezas (o bootstrap, a frase do √N e o teste de vazamento), mas o sinal fica. Segue o 43-G (warp e movimento vertical).
- **J2 e J3 passam, J4 reprova:** a amplitude é real, mas a coerência de fase não se distingue do ruído do feixe com 11 anéis; o argumento de "organização" do artigo e da nota de síntese perde a sua base.
- **J5 reprova:** a coerência não é própria do m = 5; se vários modos forem coerentes, o que se vê é estrutura do disco em geral, e o destaque do m = 5 precisa ser repensado.
- **J2 ou J3 reprovam:** o sinal não resiste ao feixe, e o preprint precisa de uma nova versão antes de qualquer outra coisa.

Um julgamento por hipótese; sem emenda. Instrumento: teste43.py, escrito depois do commit desta predição. Os mapas FITS ficam fora do repositório (dados públicos do THINGS; o teste lê de um diretório indicado na linha de comando).
