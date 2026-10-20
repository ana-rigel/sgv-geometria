# Predição do teste 50 (o padrão além de 310″: rígido ou cisalhando? Tremaine–Weinberg radial com warp, no H I do THINGS)

20/10/2026 · escrita antes de calcular · dados: THINGS NGC 628, momento 0 e momento 1, ponderação natural · Ana Rigel

## De onde vem

O teste 49 deixou uma predição congelada para a região que Speights et al. (2025) não mediram (cortada em 310″ por causa do warp). Com a fronteira entre os anéis que deslizam e o aglomerado em r\* ≈ 278″, a predição é:

- **padrão rígido de 310″ a 395″**, enquanto o material continua em rotação diferencial;
- **nível ≈ 17 km/s/kpc** (na geometria de Speights, i = 6°);
- corrotação ≈ 330″.

A Ana trouxe o mapa de momento 0 do H I. Nada disso é reajustado aqui. Ela propôs três confrontos, e os três entram neste teste:

1. a medida na região descoberta;
2. perfis alternativos de PA(r) e i(r);
3. dados sintéticos com a mesma geometria, máscara, feixe e ruído.

Ela também lembrou que uma medida muito incerta pode "concordar" com 17 sem separar rígido de cisalhando. Por isso o confronto sintético é a **porta**: se ele não separar os dois casos, a medida real não decide nada, seja qual for o valor.

## Os dados (cabeçalhos conferidos; nenhum número da emissão foi calculado antes desta predição)

- **Momento 0:** NGC0628_Original_Data_HI.fits (cópia de B. T. Draine).
  - O histórico AIPS mostra XMOM0 do cubo N628_NA_RES (THINGS, programa AW605, configurações B, C e D), corrigido do feixe primário, com brancos trocados por 0.
  - Feixe 11,88″ × 9,30″, BPA −70,34°: **o mesmo do momento 1 NA** que já temos.
  - **Grade idêntica** (mesmos CRVAL, CRPIX, CDELT, 1,5″/pixel). As 45 linhas do norte foram cortadas: 979 linhas em vez de 1024.
  - A escala foi multiplicada por Draine. A unidade não importa, porque o método é linear na intensidade.
- **Momento 1:** NGC_628_NA_MOM1_THINGS.FITS (da Despesa.zip).
- Os dois saem do mesmo cubo NA. O mapa de Draine é tratado como o momento 0 do THINGS por esses três fatos do cabeçalho (feixe, grade, histórico), não por suposição.

## O método

**A identidade.** É a de Speights et al. (Eq. 1), que vem da equação de continuidade integrada na região além de uma reta y = y₀ do disco:

  ∫ I(x, y₀) V_y(x, y₀) dx = ∫_{|y₀|}^{∞} Ωp(r) [I(+√(r² − y₀²), y₀) − I(−√(r² − y₀²), y₀)] r dr,  com V_y = (V_los − V_sis) / sen i.

**A generalização para o warp (anéis inclinados).** Cada anel r tem o seu PA(r) e i(r). As coordenadas do disco "desempenado" são x = r cos θ e y = r sen θ, com θ medido a partir da linha dos nodos do próprio anel. A velocidade na linha de visada de um elemento do anel é sen i(r)·(v_θ cos θ + v_r sen θ) + cos i(r)·v_z. Logo, V_y = (V_los − V_sis)/sen i(r) é a componente v_y do disco desempenado, a menos do termo v_z·cot i, que é o limite físico do método e não se corrige. A identidade vale no disco desempenado se o warp for estático. Na prática:

- uma grade (x, y) de 1,5″ é mapeada para o céu anel por anel: X = r cos θ na linha dos nodos, Y = r sen θ cos i(r), girado por PA(r);
- momento 0 e momento 1 são interpolados (bilinear) nessa grade;
- I = momento 0 × cos i(r);
- onde o momento 0 é 0 (branco), I = 0;
- onde o momento 0 > 0 e o momento 1 está em branco, I·V_y = 0 (a fração desses pixels é relatada).

**Sentido de y.** É escolhido para que os braços sejam arrastados (trailing), como em Speights et al.: a fase do m = 2 do momento 0 desempenado deve decrescer com o raio entre 60″ e 250″ no sentido da rotação. A rotação vai de x para y; x aponta para o lado que se afasta.

**Retas e anéis.**
- Retas y₀ a cada 3″, dos dois lados, de 0 até a borda dos dados.
- Ωp constante por anel, em anéis de 7,5″ de 0 até R_borda. R_borda é o maior raio em que algum pixel com momento 0 > 0 tem a cobertura azimutal do anel ≥ 50 %.
- Uma incógnita a mais, δV (erro de V_sis), que entra como (δV/sen i)·∫I dx.
- O instrumento confere que o momento 0 é zero nas bordas da imagem, inclusive no corte norte. Se não for, as retas que tocam a borda são retiradas e isso é relatado.

**Regularização.** Tikhonov de **segunda ordem** (penaliza curvatura), com λ por validação cruzada generalizada (GCV). A escolha é deliberada e diferente da de Speights et al. (primeira ordem, curva L): a primeira ordem puxa o perfil para uma constante, ou seja, **a favor da predição rígida**. A segunda ordem não penaliza nem uma constante nem uma rampa linear, e o Ω material em 310″–395″ é quase uma rampa.

**Unidades.** km/s por segundo de arco, convertidos a km/s/kpc por 34,2 pc/″ (a escala de Speights et al.).

**Rotação e geometria.**
- **Centro:** o núcleo em raios X adotado por Speights et al., 01h36m41,747s +15°47′01,18″. A Tabela 2 deles imprime 47,747 s, o que poria o centro 86″ a leste do núcleo; tomo isso como erro tipográfico.
- **PA(r):** ajuste harmônico do momento 1 em anéis de 15″ (V_los = V_sis + c cos φ + s sen φ + segundos harmônicos), duas iterações da geometria. O PA cinemático sai da fase do primeiro harmônico, e o erro formal é inflado pela raiz do número de pixels por feixe (≈ 50).
- **Rotação:** V_rot = amplitude/sen i(r), Ω = V_rot/r, no mesmo anel.
- **V_sis inicial:** a mediana dos termos constantes; δV fica livre no ajuste do padrão.

**A estatística do teste.** Seja b a inclinação de uma reta ajustada a Ωp dos anéis com centro em 310″–395″, e b_Ω a mesma inclinação para Ω nos mesmos anéis. Então **q = b / b_Ω**: q = 0 é rígido, q = 1 é cisalhando com o material.

## As geometrias (confronto 2)

| | PA(r) | i(r) |
|---|---|---|
| **G1, principal** | ajustado ao momento 1 | 8,5° constante |
| G2 | ajustado | de Aniyan et al. (Fig. 13), média corrida de ±15″, mantido o último valor além de 350″ |
| G3 | de Aniyan et al. até 350″, constante além | 8,5° |
| G4 | ajustado + 1σ (em todos os anéis) | 8,5° |
| G5 | ajustado − 1σ | 8,5° |
| G6, a de Speights | 21,8° fixo | 6,0° fixo |

G6 é a geometria plana, conhecida por ignorar o giro de PA. Entra só para a validação (J1) e como relato na região externa. Por que i = 8,5° constante na principal: o teste 48 mostrou que a subida de inclinação de Aniyan et al., lida como inclinação pura, daria uma curva que cai mais rápido que a de Kepler. Uma inclinação a mais ou a menos escala Ωp e Ω pelo mesmo fator, então q não depende dela. O nível em "unidades de Speights" é Ωp·sen i/sen 6°; para i = 8,5°, isso é × 1,414.

## Os sintéticos (confronto 3)

Usa a mesma morfologia real.

- **Densidade:** Σ = o momento 0 real desempenado (G1). Assim, a alavanca do método é exatamente a do dado.
- **Rotação:** v_θ = rΩ(r), com o Ω ajustado em G1 suavizado (média corrida de 30″).
- **Velocidade radial:** imposta pela continuidade para um padrão que gira a Ωp(r): r Σ v_r (r, θ) = ∫₀^r r′ [Ωp(r′) − Ω(r′)] ∂Σ/∂θ dr′, em grade polar (Δr = 1,5″, 720 azimutes).
- **Dois cenários,** iguais até 278″ (Δ = Ω(278″) − Ω(330″), contínuo em 278″):
  - **R, o do modelo:** Ωp = Ω − Δ para r < 278″; Ωp = Ω(330″) constante para r ≥ 278″.
  - **S, cisalhando:** Ωp = Ω − Δ em todo raio.
- **O momento 1 sintético:**
  - V_sis + sen i·(v_θ cos θ + v_r sen θ), projetado em G1;
  - mais o **resíduo real** do momento 1 (momento 1 menos o modelo circular de G1) girado de um ângulo aleatório em torno do centro, como ruído. Ele contém ruído, movimentos não circulares e qualquer v_z real; girado, perde a correlação com os braços;
  - a mesma máscara do dado.
- **Realizações:** 100 por cenário (semente 50), analisadas com o mesmo pipeline (G1, GCV).

## Critérios

**J1, o instrumento reproduz Speights et al. onde eles mediram.** Na geometria G6, com o V_sis deles (655,9 km/s) e só as retas com |y₀| ≤ 310″, o Ωp dos nossos anéis fica dentro da barra de erro deles (Fig. 12d, digitalizada no teste 49) em **≥ 70 %** dos pontos deles entre 100″ e 310″.

**J2, a porta: os sintéticos separam rígido de cisalhando em 310″–395″.** q < 0,5 em **≥ 84 %** das realizações do cenário R, e q ≥ 0,5 em **≥ 84 %** das do cenário S.

**J3, a predição congelada: o padrão é rígido em 310″–395″.** No dado real, em G1, **q < 0,5**.

**J4, o nível congelado.** A média de Ωp nos anéis de 310″–395″, em unidades de Speights (× sen 8,5°/sen 6°), fica em **17 ± 3 km/s/kpc**.

**J5, a robustez geométrica.** A classificação do J3 (q < 0,5 ou ≥ 0,5) é a mesma em **≥ 4 das 5** geometrias G1–G5.

Relatado sem critério:
- Ωp(r) e Ω(r) em cada geometria;
- a corrotação (Ωp = Ω), cuja predição é 330″ ± 20″;
- δV e λ;
- a fração de pixels com momento 1 em branco;
- o viés de q nos sintéticos (mediana em R e em S);
- os sintéticos analisados em G3 e G6, como estimativa do erro sistemático de geometria.

## Apostas (Claude, antes de calcular)

- **J1: 50 %.** Outra regularização, outro λ, e um centro corrigido por suposição.
- **J2: 35 %.** A 8,5°, sen i ≈ 0,15: 5 km/s de resíduo no momento 1 viram ≈ 34 km/s em V_y. A região tem 85″, ≈ 8 feixes.
- **J3: 45 %.**
- **J4: 30 %.**
- **J5: 50 %.**

## O que fecha

- **J1 reprova:** o instrumento não reproduz a medida publicada. J3–J5 são relatados, mas não contam.
- **J2 reprova:** com estes dados e este método, a região 310″–395″ não separa padrão rígido de cisalhando. O teste da predição fica **indecidível**, e J3–J5 não contam a favor nem contra. Saber isso também é resultado: diz que o confronto exige outro dado (resolução, outro traçador) ou outro método.
- **J1 e J2 passam, J3 e J5 passam:** a predição sobrevive ao warp e à geometria. É uma correspondência observacional nova, ainda com a ressalva de representação (o padrão total do H I, não o m = 5).
- **J1 e J2 passam, J3 reprova (e J5 confirma):** o padrão externo cisalha. A identificação entre o aglomerado sincronizado do modelo e o padrão espiral real falha nesta galáxia, e o modelo tem de ser revisto nesse ponto.
- **J4** separa o nível do formato: um padrão rígido no nível errado também não é a predição.

Um julgamento por hipótese; sem emenda. Instrumento: teste50.py, escrito depois do commit desta predição.
