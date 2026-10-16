# Leitura: o cubo é o mesmo em 1, 5 e 15 minutos?

**Previsão:** `PREDICAO_autosimilaridade_temporal.md` (ce6026c). **Resultados:** `resultados/autosimilaridade_temporal_{junjul,agoset}.json` (jun–jul local; ago–set run 38921353797).

## Veredito, pela regra registrada, igual nos dois períodos

- **Borda: muda de escala.**
- **Colapso: auto-similar.**

| | 1 min | 5 min | 15 min |
|---|---|---|---|
| **jun–jul** R real / M | 6,83 / [6,53; 7,14] → dentro | 5,52 / [4,00; 5,47] → acima | 4,60 / [2,05; 5,25] → dentro |
| **ago–set** R real / M | 6,48 / [12,05; 15,03] → abaixo | 6,04 / [3,29; 4,75] → acima | 2,41 / [1,57; 3,11] → dentro |
| **jun–jul** C real / M | 0,88 / [0,88; 0,95] | 0,93 / [0,87; 0,92] | 0,80 / [0,72; 0,91] |
| **ago–set** C real / M | 0,92 / [0,86; 0,96] | 0,84 / [0,82; 0,95] | 0,70 / [0,79; 0,92] |
| R(15)/R(1) real | 0,67 (jun–jul) | | 0,37 (ago–set) |

## O que isso diz

1. **A invariância em amplitude sobrevive ao relógio.** Fixada a temperatura, o cubo colapsa para o mesmo objeto em 1, 5 e 15 min, nos dois períodos (C de 0,70 a 0,93). Em 15 min de ago–set o C ficou exatamente no limiar (0,70) e abaixo do envelope M (0,79–0,92): a invariância enfraquece quando a amostra por fatia fica pequena, mas não some. Esta é a parte "estrutura sólida" da frase da Ana, e ela é robusta.

2. **A borda agitada é um objeto de 1 minuto.** R bruto cai monotonicamente com a agregação: 6,8 → 5,5 → 4,6 e 6,5 → 6,0 → 2,4. Somar retornos suaviza as caudas, e a borda ×10 vira ×2–5. A aposta "R cai" (70 %) acertou. Isso é o contrário de auto-similar: o objeto que o cubo mostra em 1 min não é o mesmo em 15 min, só menor. Qualquer leitura "fractal" do cubo, no sentido de ver a mesma coisa em qualquer escala de tempo, não tem base nestes dados.

3. **A posição relativa ao M não se mantém, e parte disso é defeito do M.** Em 5 min o real fica acima do M nos dois períodos (5,52 > 5,47; 6,04 > 4,75): o sintético, agregado, perde borda mais rápido que o real. Em 1 min de ago–set o M deu R entre 12 e 15, o dobro do real, quando em jun–jul tinha dado 6,5–7,1. É a calibração semanal da escala rápida (Var h com teto em 2): em alguma semana de ago–set ela produz choques que inflam a borda do sintético muito além do mercado. O M é uma boa nula para memória (H-VOL-01), e uma nula instável para a borda quando agregado ou em semanas extremas. Fica registrado como limitação do instrumento, não como achado sobre o mercado.

4. **As medidas 4D em 5 e 15 min são ruidosas** (20 a 60 barras por fatia) e entraram só como descritivas. O ρ_forma troca de sinal entre resoluções; a taxa de zoom fica entre 1,05 e 1,48. Não se lê nada deles.

## Apostas

| Aposta | Prob. | Resultado |
|---|---|---|
| Borda auto-similar | ~45 % | errou (muda de escala nos dois períodos) |
| R bruto cai com a agregação | ~70 % | acertou |
| Colapso auto-similar | ~55 % | acertou |
| C em 15 min ≥ 0,7 | ~60 % | acertou (0,80 e 0,70, no limiar) |
| Os dois períodos concordam na classe da borda | ~60 % | acertou no veredito; as classes por resolução diferem (dentro/acima/dentro vs abaixo/acima/dentro) |

## Frase que fecha

A temperatura é uma coordenada de estado que age como zoom em qualquer resolução testada; isso é invariância de escala em amplitude, e é robusta. A borda agitada, o traço mais visível do cubo, é uma propriedade do minuto: some ao engrossar o relógio. O cubo do SGV é, portanto, um instrumento de 1 minuto com uma quarta dimensão que vale em qualquer minuto. Nada aqui é direção, previsão ou lucro.
