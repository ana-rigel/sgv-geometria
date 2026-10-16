# Previsão registrada antes de calcular: o cubo é o mesmo em 1, 5 e 15 minutos?

**Registrada em:** 16/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "sim quero que faça", sobre o teste de invariância de escala **no tempo** (a fractal), distinto do colapso em amplitude já medido (fatias de volatilidade, C ≈ 0,9) e do H-4D-01.

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já foram abertos. Nada de outubro é lido; nada congelado muda.

**Ramo:** `exploracao/autosimilaridade-temporal`, a partir de `confirmatorio/H-4D-01@d1f48d0`.

## A pergunta

Se agregarmos os candles de 1 min para 5 e 15 min e aplicarmos **o mesmo instrumento, com as mesmas janelas em barras**, o cubo mostra o mesmo objeto? "Mesmo" aqui é relativo ao sintético M, calculado do mesmo jeito em cada resolução: o que importa é se a posição do real em relação ao M se mantém quando o relógio engrossa, não os valores brutos (que mudam com a amostra e com k).

## Agregação

- Blocos de `agg` barras consecutivas (agg = 1, 5, 15), alinhados ao início de cada mês de dados: timestamp e open do primeiro, high máximo, low mínimo, close e demais do último, volume e taker_buy somados.
- O instrumento (`coords_orig` do sgv_original, `estimativas` har, `gerar_m`) recebe a série agregada **como se fosse de 1 min**: todas as janelas ficam em barras. Uma semana tem 10.080, 2.016 e 672 barras.
- Régua de caudas ancorada em maio, calculada em cada resolução. Quantis das 7 fatias de temperatura, idem.

## Medidas (as mesmas das rodadas anteriores, em cada resolução)

1. **R** = borda/núcleo do campo D(x) (`explora_geometria_residual.p1`: campo localmente linear treinado na semana anterior, mediana em 3 ≤ extremidade < 10 sobre mediana em < 1).
   - **k dos vizinhos:** 200, 100 e 60 para agg = 1, 5, 15. Em 15 min uma semana tem 672 barras; k = 200 seria quase global. O mesmo k vale para o real e para o M na mesma resolução.
2. **C**, o colapso de escala (`explora_fatias_volatilidade.teste1a_2`), com `fatias` por tercil de log har em maio e n mínimo por fatia e semana = 2·k.
3. **ρ_forma, R²_tilt, R² quadrático e taxa de zoom** (`confirmatorio_4d.medir/resumo`), com n mínimo por fatia = 300/agg (300, 60, 20) e n mínimo por semana para b = 2000/agg. Em 15 min essas medidas ficam ruidosas; entram como descritivas.

Séries: real e M (5 réplicas, sementes 4026–4030), em cada resolução.

## Classificação (por período; só conta se repetir em jun–jul e ago–set)

- **Classe de R por resolução:** "abaixo", "dentro" ou "acima" do envelope [mín, máx] das 5 réplicas M. Em 1 min, a geometria residual deu "dentro" (6,83 em 5,7–6,9; 6,48 em 5,2–6,3 — no limite).
  - **"Borda auto-similar":** a classe é a mesma nas três resoluções.
  - **"Borda muda de escala":** senão. Relatar em que resolução e para que lado.
- **Colapso por resolução:** C_real ≥ 0,7 ("colapsa"), 0,3–0,7 ("em parte"), < 0,3 ("não").
  - **"Colapso auto-similar":** "colapsa" nas três resoluções.
- **Descritivo:** R bruto do real nas três resoluções (razão R(15)/R(1)); n de extremos avaliados; ρ_forma e zoom por resolução.

## Validação

Se, em alguma resolução, o real ou alguma réplica M tiver menos de 3 semanas com R calculável (n_extremos ≥ 30), essa resolução é "sem dados" e o período fica INCONCLUSIVO para a borda.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Borda auto-similar (classe igual em 1, 5, 15 min, dois períodos) | ~45 % |
| R bruto do real cai com a agregação (R(15) < R(1)) | ~70 % |
| Colapso auto-similar (C ≥ 0,7 nas três, dois períodos) | ~55 % |
| C em 15 min ainda ≥ 0,7 | ~60 % |
| Jun–jul e ago–set concordam na classe da borda | ~60 % |

A aposta de 70 % em "R cai" vem de que agregar soma retornos e suaviza as caudas (teorema central do limite parcial); o M sofre o mesmo, por isso a classe relativa pode se manter mesmo com R caindo.

## O que confirma e o que não

- **Auto-similar nos dois critérios:** o objeto do cubo não depende do relógio; o que vimos em 1 min é uma propriedade do processo, não da resolução. Compatível com auto-similaridade temporal, sem demonstrá-la em toda a escala.
- **Muda de escala:** o cubo de 1 min é um objeto de 1 min. Qualquer leitura "fractal" fica sem base nestes dados.
- Em nenhum caso há direção, previsão ou lucro.

## Como roda

- Fumaça: maio, sem imprimir.
- Jun–jul: localmente. Ago–set: no GitHub Actions.
