# Dicionário geométrico do SGV — o que cada movimento da casca significa no mercado

**Data:** 13/10/2026. **Ramo:** `research/dicionario-geometrico`. **`main` intocada.**
**Dados:** BTCUSDT 1m mai–jul/2026 (exploratório, já gasto). 1.079 origens, uma a cada 2 h; 1.055 com casca válida.
**Método:** em cada origem, a janela das últimas 25 h (1.500 min) é dividida como no M11: âncora (7,5 h, fixa a régua) + metade **A** (~9 h, a mais antiga) + metade **B** (~9 h, a mais recente). Para cada medida da casca entre A e B:
1. **identidade:** quanto dela é explicado por momentos conhecidos (R²) e por quais;
2. **mercado:** correlação com observáveis **brutos** nas mesmas metades (volatilidade realizada, volume, dispersão do desequilíbrio de agressão, irregularidade do volume, saldo de agressão, preço);
3. **persistência** entre origens;
4. **exemplos reais** dos extremos;
5. **o que veio depois**, só descritivo, para gerar hipóteses.

Scripts: `scripts/dicionario_dados.py`, `scripts/dicionario_analise.py`, `scripts/dicionario_figura.py`. Dados: `reports/dicionario/dados.csv`, `analise.json`. Figura: `fig_expansao.png`.

---

## Antes de tudo: o que a casca enxerga

A casca vive em **coordenadas normalizadas**:
- o retorno z vem dividido pela volatilidade da última hora;
- o volume ν é relativo à mediana das últimas 25 h;
- a agressão ι é a fração comprador − vendedor de cada minuto;
- e tudo passa pela régua da âncora.

**Por isso a casca não mede o tamanho dos movimentos; mede a organização do estado conjunto** (como retorno, fluxo e atividade se distribuem e se acoplam). Quase todo erro de leitura vem de esquecer isso.

---

## 1. Expansão da casca — `log(V_B/V_A)`

**Matemática.** Para uma distribuição gaussiana, o volume da casca é proporcional a √det Σ, logo a expansão = ½·Δ log det Σ, que é a **variação da entropia conjunta**. Medido: inclinação **0,496** (teoria 0,5), correlação 0,96, R² nos momentos 0,94.

**Mercado — o resultado contraintuitivo: a casca expande quando o mercado ESVAZIA.**

| tercil da expansão | volume B/A | volatilidade B/A | dispersão do fluxo B/A |
|---|---|---|---|
| contrai | ×1,33 | ×1,62 | ×0,90 |
| estável | ×1,04 | ×0,97 | ×1,00 |
| **expande** | **×0,78** | **×0,66** | **×1,10** |

**Mecanismo:** com menos negócios por minuto, o desequilíbrio de agressão de cada minuto fica mais errático (lei dos grandes números; dispersão do fluxo × volume: correlação **−0,78**). O fluxo e o volume ficam mais irregulares (correlações +0,75 e +0,54 com a expansão), e a entropia conjunta sobe. **Contração = o mercado enchendo:** mais negócios, o desequilíbrio se concentra, o estado fica mais organizado. É a mesma lei que o M28 mostrou minuto a minuto ("a atividade governa a escala"), agora vista como forma.

**Faixa típica (p5–p95):** −0,40 a +0,40 (a casca muda ~±50% de volume entre as metades). **Persistência:** 0,72 em 2 h (janelas sobrepostas), ~0 em 6 h. **Confiabilidade:** 0,72.
**Exemplos:** maior expansão em 25/06 06h (volatilidade ×0,23, volume ×0,25, dispersão do fluxo ×1,52: a calmaria logo depois de um choque); maior contração em 24/06 20h (volatilidade ×6,1, volume ×4,5, preço −4%).
**Depois (descritivo):** volume nas 6 h seguintes ×0,89 após contração e ×1,08 após expansão — a atividade tende a voltar ao normal.

## 2. Deslocamento da casca — `‖centro_B − centro_A‖`

**Matemática.** R² 0,94; praticamente todo explicado pela **mudança do nível de atividade**, |Δ média de ν| (coeficiente 0,96). Retorno e agressão quase não movem o centro.

| tercil | \|Δν\| mediano | \|Δι\| | \|Δz\| |
|---|---|---|---|
| parada | 0,14 | 0,08 | 0,03 |
| andou | **0,76** | 0,10 | 0,03 |

**Mercado:** **a casca anda quando o regime de atividade muda** — para mais ou para menos (45% das vezes para cima). Não indica direção de preço nem lado do fluxo.
**Persistência:** 0,63 em 2 h, ~0 em 6 h. **Confiabilidade:** 0,76.
**Exemplos:** 24/06 18h–22h (deslocamento 1,9–2,2; volume ×4–4,5, volatilidade ×4,5–6, preço −5,4%); parada em 09/06 08h (tudo ×1,0).

## 3. Persistência da região — Jaccard das HDR50

**Matemática.** R² 0,80; dominado pelo **inverso da mudança de atividade** (−0,88) e, em menor grau, pela entropia (+0,31). Na prática, é uma distância entre a distribuição de antes e a de agora.
**Mercado:** "o mercado continua no mesmo lugar". Alto = mesmo regime de atividade; quase zero = regime substituído.
**Persistência:** 0,62 em 2 h, ~0 em 6 h. **Confiabilidade:** 0,80.
**Exemplos:** 0,91 em 25/05 18h (calma estável); 0,001–0,03 em 24/06 20h–25/06 06h (choque e a calmaria seguinte).

## 4. Intensidade da curvatura — mediana de K na casca atual

**Matemática.** R² 0,36 nos momentos: sobe quando a casca é **mais compacta** (Δ log det negativo), o volume e o fluxo são **mais regulares** e a cintura é mais funda (cintura B menor).

| tercil | volatilidade B/A | volume B/A | cintura B | Δ log det |
|---|---|---|---|---|
| baixa | ×0,83 | ×0,96 | 0,88 | +0,17 |
| **alta** | **×1,20** | **×1,16** | **0,81** | **−0,20** |

**Mercado:** **casca compacta e torcida = mercado cheio e organizado** — mais atividade, fluxo regular, minutos tomando partido. **É o estado geométrico mais persistente** (0,72 em 2 h, **0,28 em 6 h**). **Confiabilidade:** 0,69.
**Exemplos:** máximos em 27/07 00h–08h (volatilidade ×1,5–3,4, volume ×1,2–1,8, saldo vendedor) — o mesmo período em que a animação da casca mostrou o cone mais aberto.

## 5. Variação da curvatura — Δ mediana de K

**Matemática.** R² 0,54: sobe quando a **irregularidade do volume cai** (−0,87) e a do fluxo também (−0,49).
**Mercado:** "o mercado está se organizando" (volume ficando regular). Correlação −0,55 com a irregularidade bruta do volume.
**Persistência:** 0,63 em 2 h, ~0 em 6 h. **Confiabilidade:** 0,38 (ruidosa).

## 6. Área em sela (atual) e sua variação

**Matemática.** R² 0,10: quase nada nos momentos. Relações fracas: mais sela com cone mais aberto (+0,19), mais acoplamento retorno–agressão (+0,21) e volatilidade subindo (+0,19).
**Mercado:** a cintura ("os minutos tomam partido"), já vista na investigação da forma; mas, medida em metades de ~9 h, **o sinal é fraco**. **Confiabilidade:** 0,47 (atual) e 0,20 (variação).
**Veredito:** significado conhecido, mas **pouco legível nesta escala**.

## 7. Deformação residual (M11)

**Matemática.** R² 0,06; nenhuma relação com os observáveis de mercado (|r| ≤ 0,08). **Confiabilidade:** 0,32.
**Veredito (corrigido em 13/10, a pedido da Ana):** **não se reduz a escalas tradicionais** — nem a momentos (R² 0,06) nem aos observáveis de mercado usados aqui. Isso **não** é o mesmo que ruído. O que a confiabilidade (0,32) mostra é outra coisa: cerca de 1/3 da variação é sinal e ~2/3 vem de estimar uma superfície 3D com ~525 pontos. **Esse terço de sinal, que nenhuma escala tradicional explica, é o candidato a algo que só a geometria mede** — e precisa de um instrumento menos ruidoso e de localização (onde a casca deforma) para ser traduzido. Ver M35.

## 8. Rotação dos eixos

R² 0,04, nenhuma relação com o mercado, confiabilidade ≈ 0 **no conjunto de todas as janelas**. A orientação só existe quando a casca tem eixos distintos; nas janelas em que ela é quase redonda, o ângulo é indefinido e domina o ruído. **Veredito (corrigido):** não medido adequadamente — precisa ser estudado só nas janelas com eixos identificáveis (M35).

---

## Anatomia de um evento: 24–25/06/2026

| origem | o que a casca fez | o que o mercado fez |
|---|---|---|
| 24/06 18h | anda muito (deslocamento 2,2), região substituída | volume ×3,9, volatilidade ×4,5, preço −5,4% |
| 24/06 20h–22h | **contrai** ao máximo (−1,06), Jaccard ~0,02 | volume ×4,5, volatilidade ×4,4–6,1, fluxo concentrado (×0,7) |
| 25/06 06h | **expande** ao máximo (+0,96), Jaccard 0,001 | volume ×0,25, volatilidade ×0,23, fluxo errático (×1,5) |

Lido no dicionário: **o choque enche o mercado (casca se desloca e contrai); horas depois, a calmaria o esvazia (casca expande).** A geometria conta a história da atividade e da organização do fluxo, não a do preço.

---

## Síntese

| medida | significado no mercado | identidade | confiab. | veredito |
|---|---|---|---|---|
| expansão | mercado esvaziando, fluxo mais errático (entropia ↑) | ½ Δ log det Σ | 0,72 | **claro** |
| deslocamento | mudança do regime de atividade | \|Δ ν médio\| | 0,76 | **claro** |
| Jaccard | permanência do regime | ≈ inverso do anterior | 0,80 | **claro** |
| intensidade da curvatura | mercado cheio, compacto e organizado | parcial (R² 0,36) | 0,69 | **claro; o mais persistente** |
| variação da curvatura | volume ficando regular | parcial (R² 0,54) | 0,38 | ruidoso |
| área em sela | minutos tomando partido | quase nenhuma | 0,47 | fraco nesta escala |
| M11 | ainda sem tradução | nenhuma (não é escala tradicional) | 0,32 | **candidato a medida nova; instrumento ruidoso** |
| rotação | ainda sem tradução | nenhuma | ≈ 0 no geral | **não medida adequadamente** |

**O que o dicionário mostra:** a geometria da casca é uma linguagem visual para três coisas do funcionamento do mercado — **o nível de atividade** (onde a casca está), **a entropia do fluxo, que depende de quantos negócios há** (o tamanho da casca) e **o grau de organização** (quão compacta e torcida ela é). As três têm tradução exata ou parcial em quantidades conhecidas. As medidas "puramente geométricas" (M11, rotação, sela em metades de 9 h) **não se reduzem a nenhuma escala tradicional** testada; parte delas é sinal (~1/3 no M11) e parte é ruído de estimação do instrumento atual. **Traduzir essa parte é o próximo passo (M35)**: instrumento menos ruidoso, deformação localizada na superfície e comparação com escalas não tradicionais (caudas, assimetria compra/venda, quantis condicionais).

## Hipóteses com mecanismo (para amostra nova; nada disto é resultado)
1. **Reversão da atividade:** depois de uma contração (mercado cheio), o volume das horas seguintes tende a cair, e depois de uma expansão, a subir (descritivo: ×0,89 e ×1,08).
2. **Organização persistente:** a intensidade da curvatura (mercado compacto e organizado) é um estado que dura horas (0,28 em 6 h) e acompanha períodos de volatilidade e volume altos.
3. **Entropia do fluxo × número de negócios:** a expansão deve desaparecer se o desequilíbrio for normalizado pelo número de negócios do minuto, o que testaria diretamente o mecanismo da lei dos grandes números.

**Ressalvas:** um único período exploratório; janelas de 25 h sobrepostas (origens a cada 2 h); correlações descritivas; o que "veio depois" não é teste.
