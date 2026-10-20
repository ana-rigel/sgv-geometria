# Predição do teste 34 (a régua da organização)

20/10/2026 · escrita antes de rodar · instrumento v0.py sem mudança; organização ⋄ (mínimos quadrados recursivos, 5 coeficientes) de teste32.py · Ana Rigel

## De onde vem

Da conversa de 20/10 sobre a NGC 628. A nota da galáxia propôs dη/dt = 𝒢 − 𝒟: um modo é **organizado** quando persiste acima do que a dissipação passiva deixaria. A página "Cubo da dissipação" levou essa leitura para a v0 sobre o clima de Juara e mostrou que, nos andares, a dissipação cai na amplitude do ciclo anual (100 % → 99 % → 66 % → 6 % → 0,05 %), não na fase, e que a v0 tem 𝒢 interno = 0 por construção. Antes de procurar organização num corpo ⋄, a Ana pediu calibrar a régua: ela acha organização quando existe, e não a inventa quando não existe?

Este teste **não** é sobre a ⋄ dos testes 32 e 33 (a que tira o ano dos andares). É sobre o instrumento que mediria qualquer ⋄ que **segure** o ciclo.

## O corpo medido e o 𝒢 injetado

O corpo é o **andar 3** da v0 (λ₃ = 0,0015, τ ≈ 667 dias), sobre o campo de três sensores do Cérebro de Juara (água no solo 28–100 cm, chuva − ET0 em 7 dias, VPD; padronizados por 2010–2017, como em clima/cubo_juara.py). É onde a samambaia quebra (teste 31) e onde um corpo que segura o ciclo teria o que fazer. A entrada do andar 3 é o andar 2, u(t).

**Positivos, P(γ):** um 𝒢 interno de tamanho conhecido. Uma ⋄ por eixo aprende o ritmo do ano na entrada u (mínimos quadrados recursivos sem esquecimento, base 1, sen/cos de 1 e 2 ciclos por ano, começando fria, prevê antes de aprender) e devolve ĉ(t), a parte periódica aprendida (sem o nível). O andar passa a ser

  r₃ ← r₃ + λ₃ (u − r₃) + γ λ₃ ĉ(t),  γ ∈ {0,05; 0,10; 0,25; 0,50; 1,00}.

Isso é organização no sentido da galáxia: o ritmo fica guardado na ⋄ e continua sendo bombeado no andar mesmo que o mundo pare de oscilar.

**Negativos (nenhum 𝒢 interno, nenhum padrão guardado):**

| nome | o que é |
|---|---|
| N0 v0 pura | o andar 3 como ele é |
| N1 ruído vermelho | o andar recebe + λ₃ ξ(t), ξ um AR(1) com τ = 180 dias por eixo, com o mesmo desvio-padrão de γ ĉ em P(0,25) no mesmo mundo, calibração |
| N2 memória mais curta | λ = 1,5 λ₃, passivo |
| N3 esquecimento não linear | λ_t = λ₃ · clip(\|u − r₃\| / κ, 0,25; 4), κ = média de \|u − r₃\| de N0 na calibração do mesmo mundo; passivo, sem padrão guardado |

## Mundos

100 histórias de 16 anos (semente 34): permutações dos 16 anos reais de Juara, 2010–2025, cada ano inteiro e na ordem interna dos dias. Os 8 primeiros anos de cada história são a **calibração**; os 8 últimos, a **medida**. A memória começa em zero no dia 1.

## As duas réguas

**Régua A, da sombra** (a da galáxia). O mundo segue com estações nos 16 anos. Para cada corpo, a sombra passiva é um registro de 1ª ordem que lê a mesma entrada u. Mede-se

  Θ = log₂( Σ_anos Σ_eixos |Z_corpo|² / Σ_anos Σ_eixos |Z_sombra|² ),

com Z o harmônico anual ajustado por ano (nível, tendência, um harmônico de 365,25 dias) nos 8 anos de medida. A sombra começa no valor do corpo no primeiro dia da medida. Três sombras:

- **ajustada:** λ̂ por mínimos quadrados de r₃(t) − r₃(t−1) contra u(t) − r₃(t−1), nos 8 anos de calibração, eixos juntos. É a única possível num observador cujo λ não se conhece (OBS-01).
- **nominal:** λ₃, a constante declarada do projeto.
- **exata:** o mesmo corpo com γ = 0 no mesmo mundo. Dá a verdade, Θ_exato, para os positivos; para os negativos, Θ_exato = 0 por definição.

Limiar θ*_A = quantil 95 % de Θ_ajustada nos 400 negativos (N0–N3 × 100 mundos).

**Régua B, do silêncio** (a que intervém). Nos 8 anos de medida, o mundo perde as estações: o campo passa a ser x − climatologia, com a climatologia por dia do ano dos 8 anos de calibração daquele mundo (média por dia suavizada em 31 dias, como T30.climatologia). A memória e a ⋄ seguem sem reinício. Mede-se a retenção

  R = |Z_medida| / |Z_calibração|,

com Z o harmônico anual ajustado de uma vez sobre os anos 10–16 (medida, pulando o primeiro ano de silêncio) e sobre os anos 2–8 (calibração), somado em quadratura nos três eixos. Um corpo passivo não tem de onde tirar ciclo quando o mundo não tem; um corpo com ritmo guardado continua oscilando. Limiar θ*_B = quantil 95 % de R nos 400 negativos.

**Piso de detecção** de uma régua: o menor γ da grade a partir do qual P(γ) passa do limiar em ≥ 90 dos 100 mundos, e todos os γ maiores também.

## Conta prévia (sem rodar o teste; só os ganhos da cascata e a forma da ⋄)

1. No ciclo anual, o andar 3 passa ≈ 8,7 % da amplitude que recebe do andar 2 (0,0570 / 0,6564), e com ωτ ≈ 11,5 esse ganho é quase proporcional a λ. Um P(γ) aumenta a amplitude anual de entrada em cerca de (1 + γ), então Θ_exato ≈ 2 log₂(1 + γ): 0,14; 0,27; 0,64; 1,17; 2,00.
2. **A sombra ajustada deve engolir quase todo o 𝒢.** O termo γĉ é quase o ciclo anual de u, e u − r₃ é dominado por esse ciclo. O ajuste de λ̂ atribui o reforço a um λ maior: λ̂ ≈ λ₃(1 + βγ), com β ≈ 0,8 (a fração anual do andar 2 em lugares de estação forte, teste 31). Como o ganho anual do andar 3 é quase proporcional a λ, a sombra ajustada cresce quase tanto quanto o corpo: Θ_ajustada ≈ 2 log₂((1 + γ) / (1 + 0,8γ)), cerca de 0,12 em γ = 0,25 contra 0,64 de verdade, ou seja, ≈ 1/5 do 𝒢. Um reforço em fase com o ciclo é, para uma sombra ajustada de 1ª ordem, uma memória mais curta.
3. **A sombra nominal não separa organização de arquitetura errada.** N2 (λ × 1,5) deve dar Θ_nominal ≈ 2 log₂ 1,5 ≈ 1,2, maior que o de P(0,50). N3 também deve sair positivo, porque o λ efetivo dele cresce nos desvios grandes, que são os da estação.
4. **No silêncio, o fundo é a diferença entre as duas metades do clima.** A climatologia vem de 8 anos e o silêncio é feito com outros 8; a diferença entre os ciclos médios das duas metades sobra coerente e passa pela cascata como um ciclo de verdade. Com a dispersão dos ciclos anuais entre anos da ordem de 20 % (C_φ ≈ 0,98 na página do cubo), espero R ≈ 0,1 típico nos negativos e θ*_B perto de 0,2. Nos positivos, R ≈ γ/(1 + γ) × (a fração de ĉ que a ⋄ guarda nos anos 10–16; a ⋄ sem esquecimento, depois de 8 anos de ciclo, guarda algo entre 0,5 e 0,8). P(0,25) ≈ 0,13; P(0,50) ≈ 0,22; P(1,00) ≈ 0,33. O piso da régua B deve ficar perto de γ = 0,5.

## Critérios

**J1, a régua do silêncio acha organização de tamanho moderado:** piso de detecção da régua B **≤ 0,50**.

**J2, a régua da sombra ajustada acha organização de tamanho moderado:** piso de detecção da régua A com sombra ajustada **≤ 0,50**.

Relatado: o piso da régua A com sombra nominal e a taxa de falso positivo de N2 e N3 nela (contra o quantil 95 % de N0 e N1); a mediana de Θ_ajustada / Θ_exato por γ; a mediana de R por corpo; a diferença de C_φ entre corpo e sombra; o λ̂ ajustado por corpo.

## Apostas (Claude, antes de rodar)

- **J1 passa: 50 %.** A conta prévia põe o piso bem em 0,5, na beira.
- **J2 passa: 20 %.** A conta prévia diz que a sombra ajustada engole ≈ 4/5 do 𝒢; só passa se o ruído entre mundos de Θ_ajustada nos negativos for muito menor que 0,2.
- **Θ_ajustada / Θ_exato mediano em P(0,25) entre 0,05 e 0,35: 70 %.**
- **Com a sombra nominal, N2 passa do quantil 95 % de N0 e N1 em ≥ 90 dos 100 mundos: 90 %; N3 em ≥ 50 dos 100: 60 %.**

## O que fecha

- **J1 passa, J2 reprova:** organização só se identifica **intervindo** (tirando o ciclo do mundo e vendo o que fica) ou com a arquitetura **declarada**; uma sombra ajustada aos próprios dados a lê como memória mais curta. Para o OBS-01: medir organização numa IA alheia exige mexer na entrada dela, não só observá-la. Para a galáxia: sem intervenção possível, o Z = 82 não separa organização de uma física passiva mal especificada, que é a forma precisa da ressalva já escrita na nota.
- **J1 e J2 passam:** a absorção prevista não acontece no tamanho previsto, e a sombra ajustada serve como régua sem intervenção. A conta prévia fica registrada como defeito.
- **J1 reprova:** mesmo com silêncio, o fundo de 8 contra 8 anos cobre um 𝒢 de 50 %. Um ⋄ que segure o ciclo só seria visível se fosse grande, ou com mais anos de climatologia; o próximo desenho precisa disso antes de procurar organização em Juara.
- **J1 reprova e J2 passa:** a intervenção atrapalha mais do que ajuda neste mundo; registrar e entender antes de seguir.

Um julgamento por hipótese; 100 mundos; sem emenda. Instrumento: teste34.py, escrito depois do commit desta predição.
