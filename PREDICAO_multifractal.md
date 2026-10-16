# Previsão registrada antes de calcular: o espectro de escala ζ(q) do BTC é côncavo além do que o M explica?

**Registrada em:** 16/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "Legal amigo vamos medir", depois da explicação de multifractalidade. Uma exploração: um julgamento por período.

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já foram abertos. Nada de outubro é lido; nada congelado muda.

**Ramo:** `exploracao/multifractal`, a partir de `exploracao/assimetria-nuvem@f5970aa`.

## A pergunta

Os momentos dos retornos agregados escalam como S_q(τ) = ⟨|r_τ|^q⟩ ∝ τ^ζ(q). Monofractal: ζ(q) = qH (reta). Multifractal: ζ(q) côncava. O cubo já viu as duas metades (colapso no corpo, borda que não escala). Aqui medimos a curva inteira e perguntamos **se a concavidade do real excede a que o sintético M produz** só com agrupamento de volatilidade de poucas escalas.

## Instrumento

- Retornos log de 1 min do período (índices das semanas de `GR.semanas`, agrupados). r_τ = soma de τ retornos consecutivos em blocos **não sobrepostos**.
- τ ∈ {1, 2, 3, 5, 8, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720, 1440} min. **Ajuste principal até 240 min** (4 h; evita o ciclo diário e mantém ≥ 350 blocos por τ em dois meses). Ajuste secundário até 1440, descritivo.
- q ∈ {0,5; 1; 1,5; 2; 2,5; 3; 4}. ζ(q) = inclinação de log S_q contra log τ (mínimos quadrados).
- **Concavidade:** κ = 2ζ(2) − ζ(4). Monofractal: κ = 0. Multifractal: κ > 0. Descritivo: H = ζ(2)/2 e a curva ζ(q) inteira.
- Séries: real; **M** (5 réplicas, sementes 4026–4030, `gerar_m`: AR(1) + caminho real de volatilidade suavizado em 61 min + escala rápida calibrada por semana); **embaralhada** (5 permutações dos retornos de 1 min do período, sementes 7026–7030: mata o agrupamento, deve dar κ ≈ 0 e serve de piso do ruído).

## Classificação (por período; só vale se repetir em jun–jul e ago–set)

- **"Multifractal além do M":** κ_real > máx κ_M **e** κ_real > máx κ_embaralhada.
- **"Multifractal como o M":** mín κ_M ≤ κ_real ≤ máx κ_M, e κ_real > máx κ_embaralhada.
- **"Abaixo do M":** κ_real < mín κ_M, ainda acima da embaralhada.
- **"Monofractal dentro do ruído":** κ_real ≤ máx κ_embaralhada.

## Limitações declaradas antes

- Momentos de q = 4 são dominados por poucos minutos extremos; dois meses dão estimativa grosseira. O envelope M e o embaralhado carregam a mesma amostra, por isso a comparação é justa mesmo com κ ruidoso.
- Sazonalidade intradiária não é removida; afeta τ < 1440 igualmente no real e no M (que herda o caminho de volatilidade), e não existe na embaralhada. Logo a embaralhada é um piso otimista, declarado.
- O M tem escala lenta real (61 min) e rápida sintética: abaixo de ~1 h a multifractalidade do M é parcialmente construída, acima é herdada. Se o real exceder o M, é mais provável que seja em τ curto.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| κ_real > máx κ_embaralhada nos dois períodos (há multifractalidade aparente) | ~90 % |
| "Multifractal como o M" nos dois períodos | ~45 % |
| "Multifractal além do M" nos dois períodos | ~35 % |
| "Abaixo do M" em algum período | ~15 % |
| H = ζ(2)/2 entre 0,45 e 0,55 no real, dois períodos | ~75 % |
| κ_real (até 240 min) entre 0,05 e 0,30 | ~65 % |

A aposta de 45/35 vem do v3: o real tem mais memória que o sintético em todos os atrasos (descola em 1 min), e memória extra em escala curta é o que faz q alto escalar mais devagar. Mas o M herda o caminho real de volatilidade, que é a fonte principal da concavidade.

## O que confirma e o que não

- **Como o M:** a multifractalidade do BTC de 1 min é a que poucas escalas de volatilidade produzem; "cascata infinita" não é necessária. Fecha a pergunta nestes dados.
- **Além do M:** há estrutura de escala que agrupamento de volatilidade com duas escalas não reproduz; candidata a hipótese sobre a escala rápida, não a indicador.
- Em nenhum caso há direção, previsão ou lucro.
