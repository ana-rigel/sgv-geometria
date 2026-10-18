# Predição do teste 8 (a escada pela tensão)

18/10/2026 · escrita antes de rodar · corrige o defeito 9 do teste 4, e só ele

## Pergunta

O teste 4 ajustou os andares pelo erro de predição e encontrou a escada da predição, não a do mundo (λ₁ → 1, razões ≈ 20). O compromisso 1 do projeto diz que a tensão é o objeto, não o erro. **Ajustando os andares para que as tensões entre andares dividam a potência do mundo em partes iguais, a v0 reencontra a escada de um mundo que tem escada, e num mundo com uma escala só a progressão quebra?**

## O critério de ajuste (declarado antes)

Tensões lineares por andar: D₀ = x − R₁, D_j = R_j − R_{j+1} (j = 1 … k−1). Cada D_j é o que o andar j vê e o andar j+1 não: a fatia da tempestade entre dois cortes. O ajuste escolhe λ para que as k fatias tenham **a mesma potência** (minimiza o desvio-padrão de log Var(D_j)); é a escada em que nenhum andar carrega mais mundo do que outro. Alternativa não testada, registrada: descorrelacionar as fatias adjacentes. Uma só por teste.

Por que isso pode achar a escada do mundo: num mundo que é soma de componentes de variância igual em escalas separadas, dividir a potência em partes iguais põe um corte entre cada par de componentes; as razões entre cortes seguem as razões entre escalas. Por que pode não achar: os cortes caem **entre** as escalas (λ_j · τ_j ≠ 1), e se as escalas do mundo estiverem a razão 10 os cortes também estarão, mas deslocados; o critério de razões aceita isso, o de λ·τ não, e os dois serão relatados.

## Mundos, instrumento e critério

Os do teste 4, sem mudança: escada-2/3/4 (τ = 7, 70, 700, 7.000; k igual ao número de escalas), cíclico (período 300, k = 4); N = 20.000; 100 sementes; ajuste na calibração [0, 10.000); λ = sigmoide(u) **com faixa declarada** λ ∈ [10⁻⁴, 0,99] (defeito 10); Nelder–Mead com 3 partidas (λ₁ ∈ {0,5; 0,15; 0,05}, b = 10). Critério do teste 4: (a) razões em [7, 13] em ≥ 80 sementes em cada mundo-escada; (b) no cíclico, alguma razão fora de [7, 13] em ≥ 80 sementes **e** a escada ajustada com erro de leitura (mínimos quadrados, ridge) menor que a fixa em ≥ 80. Informativo: λ_j · τ_j; erro de leitura da escada ajustada contra a fixa e contra a do teste 4.

## Apostas

- **Passar: 30 %.** Por mundo: escada-2 55 %, escada-3 50 %, escada-4 40 % (o andar de 7.000 passos tem só 1,4 períodos na calibração e a sua potência é mal estimada), cíclico 70 % (uma senoide forte faz todos os cortes se amontoarem em torno de 1/300 para dividir uma potência que está num lugar só; a progressão quebra; mas a segunda metade de (b), ganhar da fixa em erro de leitura, não é o que este ajuste otimiza, e pode falhar: 60 %).
- λ_j · τ_j entre 0,2 e 5 em todos os andares (60 %): os cortes caem entre as escalas, não nelas.
- A escada pela tensão tem erro de leitura **maior** que a do teste 4 em todos os mundos-escada (85 %): otimiza outra coisa, e isso é o esperado, não um defeito.

## O que fecha

Passar: a escada do mundo é legível pela tensão e não pelo erro, o compromisso 1 do projeto vira resultado, e a auto-similaridade da v0 deixa de ser projeção **neste sentido**. Reprovar em (a) com razões consistentes mas fora de [7, 13]: o ajuste acha uma escada regular que não é a do mundo, e a leitura dirá qual. Reprovar em (b): a v0 por tensão não sabe quando não há escada, e perde o único acerto do teste 4.
