# Leitura do teste 50 (o padrão além de 310″, Tremaine–Weinberg radial com warp no H I do THINGS): J1 e J2 REPROVADOS; J3, J4 e J5 passaram pela letra e NÃO CONTAM. A porta fechou: com estes dados e este método, a região 310″–395″ não separa padrão rígido de cisalhando. A predição do teste 49 continua congelada e sem teste

**Predição:** PREDICAO_teste50_padrao_externo.md (b588add), antes de calcular. **Instrumento:** teste50.py (04ab4e5). **Resultado:** resultados_teste50.json. **Dados:**
- momento 0 do THINGS NA (a cópia de Draine, identificada pelo cabeçalho);
- momento 1 do THINGS NA.

Cinco julgamentos; sem emenda.

## Antes da rodada: um ensaio e uma correção (defeito 69)

Rodei o instrumento uma vez com uma só realização sintética, para ver se funcionava. Os números do dado real (J1, as seis geometrias) saíram nesse ensaio e são **idênticos** aos da rodada final: nada no caminho do dado real mudou depois.

O ensaio mostrou um erro no **sintético**. A construção pré-registrada impunha a continuidade só com fluxo radial, integrado de dentro para fora (r Σ v_r = ∫₀^r …). Isso deixa um fluxo de massa C(θ) atravessando a borda do disco, e a identidade de Tremaine–Weinberg exige que nada atravesse. Medido sem ruído, o modelo verdadeiro deixava 48 % de resíduo na identidade.

A correção devolve esse fluxo por um fluxo azimutal f_θ = w′(r) G(θ), com w a massa acumulada e G = ∫ C dθ. Ela mantém a continuidade exata e não mexe no Ωp dos cenários. Depois dela:
- o resíduo da identidade caiu para **1–2 %** na grade do disco e **5–8 %** passando pelo céu;
- sem ruído, o método devolve **q = 1,27** no cenário cisalhando (verdadeiro 1,01) e **q = 0,17** no rígido (verdadeiro 0).

A identidade com o padrão material (Ωp = Ω) fecha a **0,14 %** no dado real, o que confere o sistema de retas e anéis.

## Checagens

- Fluxo na borda da imagem: 4 × 10⁻⁵ do total. O corte norte não afeta.
- Momento 0 > 0 sem momento 1: 0.
- R_borda = 772″; fluxo além dela: 0,6 %.
- V_sis ajustado: 656,0 km/s (Speights et al.: 655,9).
- Sentido de y pelos braços arrastados: s = −1.
- Rms do resíduo do momento 1 (sem rotação): **7,4 km/s**.
- PA cinemático: gira de 24° (250″) a 9° (370″), como em Aniyan et al. Além de 400″ ele salta para 50–90°: o warp forte do disco externo.

## Julgamentos

| | resultado | critério | |
|---|---|---|---|
| **J1** reproduz Speights et al. em 100″–310″ | **10 %** dos pontos dentro da barra | ≥ 70 % | **reprovado** |
| **J2** a porta: os sintéticos separam rígido de cisalhando | R: **61 %** com q < 0,5; S: **46 %** com q ≥ 0,5 | ≥ 84 % cada | **reprovado** |
| J3 rígido no dado real (G1) | q = −0,91 | < 0,5 | passou, **não conta** |
| J4 nível congelado | 15,2 km/s/kpc (i = 6°) | 17 ± 3 | passou, **não conta** |
| J5 robustez | 4 de 5 geometrias com q < 0,5 | ≥ 4 | passou, **não conta** |

Apostas: J1 (50 %) e J2 (35 %) erradas pela letra, embora a do J2 inclinasse para a reprovação. As de J3–J5 ficam sem efeito.

## O que o resultado diz

**1. O método vê o padrão; o que o afoga é o movimento real que não é rotação.** Em cada realização, o mesmo ruído entra nos dois cenários, e a diferença q_S − q_R ficou em **1,11** (q16–q84: 1,09–1,21; positiva em 100 de 100). A diferença verdadeira é 1. Ou seja, o método responde ao padrão injetado quase sem erro. Mas cada campo de resíduo desloca os dois q juntos (correlação 0,997) por uma quantidade enorme: de −3,9 a +4,4 entre os quantis 16 % e 84 % no cenário rígido. A diferença entre rígido e cisalhando é 1; o espalhamento causado pelo resíduo real é ≈ 8.

**2. Por que isso acontece.** O resíduo de 7,4 km/s do momento 1 é ruído, movimentos não circulares e qualquer movimento vertical. A 8,5°, ele entra em V_y multiplicado por 1/sen i ≈ 6,8 (e o vertical por cot i ≈ 6,7): ≈ 50 km/s de "velocidade no plano" espúria, contra o sinal que separa os cenários, de poucos km/s/kpc. O teste 43 já tinha mostrado que, nessa inclinação, a linha de visada é quase toda movimento vertical. Aqui isso aparece como limite do Tremaine–Weinberg.

**3. O J1 reprova pelo mesmo motivo, mais a regularização.** O GCV escolheu λ pequeno, porque o resíduo é correlacionado pelo feixe e o GCV supõe ruído independente (defeito 70). O perfil sai oscilando ±30–100 km/s/kpc, e Speights et al. regularizam mais forte (primeira ordem, curva L). Um λ maior teria reproduzido melhor a forma deles, mas puxando o perfil para a constante — e a primeira ordem favorece justamente a predição rígida. Este teste não troca a regra depois de ver o resultado.

**4. A geometria pesa tanto quanto o ruído.** Com o PA de Aniyan et al. (G3) ou o PA fixo de Speights et al. (G6), o q do dado real vai a −26 e −19. Nos sintéticos analisados com essas geometrias, vai de −20 a +11. Erros de poucos graus no PA, numa região onde ele gira 15°, produzem inclinações espúrias muitas vezes maiores que o sinal.

**5. O que fica da predição.** Ela **não foi testada**: nem confirmada nem refutada. O q = −0,91 do dado real está no meio da distribuição de ruído dos dois cenários. O nível de 15,2 km/s/kpc (perto de 17) é apenas um número desse mesmo ruído, e ler os dois como acordo seria o erro que a Ana apontou: uma medida incerta "concordando" sem separar nada. As predições do teste 49 (Ωp ≈ 17 km/s/kpc rígido em 310″–395″, corrotação ≈ 330″, r\* ≈ 278″) continuam congeladas.

**6. O que o teste ensina sobre o confronto.** Com Tremaine–Weinberg no H I do THINGS, a NGC 628 não decide esta predição. A inclinação de 6–9° multiplica por ≈ 7 qualquer movimento que não seja rotação, e o warp externo gira o PA na mesma região. Para separar rígido de cisalhando, o espalhamento espúrio de q teria de cair ≈ 8 vezes. Os caminhos que mudam isso são:
- uma galáxia com a mesma pergunta e inclinação de 40–60°, onde sen i ≈ 0,7 e o vertical pesa pouco;
- ou, na NGC 628, uma medida de Ωp que não passe pelas velocidades: por exemplo, o deslocamento azimutal entre traçadores de idades diferentes (gás, formação estelar, aglomerados jovens), que depende só da morfologia e da diferença Ω − Ωp.

## Para a lista de defeitos de desenho

69. O sintético pré-registrado impunha a continuidade só com fluxo radial integrado de dentro para fora, o que deixa massa atravessando a borda e viola a identidade que o teste mede (48 % de resíduo sem ruído). Foi corrigido com um fluxo azimutal de compensação antes da rodada, depois de um ensaio de uma realização; o caminho do dado real não mudou.
70. A predição chamou o GCV de neutro sem considerar que ele supõe resíduos independentes. Com o resíduo correlacionado pelo feixe, ele escolhe λ pequeno demais, e o perfil fica dominado pelo ruído. Um ensaio sintético com ruído, antes de fixar os critérios, teria mostrado tanto isso quanto o espalhamento de q que fechou a porta.

Placar: 50 testes numerados (o 25 sem resultado), mais o teste do ato A. 50: J1, J2 reprovaram; J3, J4, J5 passaram pela letra, sem valor (porta fechada). 70 defeitos nesta numeração, 1 emenda.
