# Leitura: a memória da volatilidade é lei de potência ou soma de exponenciais?

**Previsão:** `PREDICAO_memoria_potencia.md` (6dc8d48). **Resultados:** `resultados/memoria_potencia_{junjul,agoset}.json` (jun–jul local; ago–set run 38928700368).

## Veredito pela regra registrada: NÃO ESTÁVEL

| | jun–jul | ago–set |
|---|---|---|
| Real: classe | **potência** (AIC pot −86,1 vs 2exp −79,9; β 0,13) | **potência** (−77,0 vs −70,4; β 0,18) |
| E2: classes das 5 réplicas | 4 duas exp. + 1 indistinguível → **valida** | 3 duas exp. + 2 potência → **reprova** |
| Classe do real contada | potência | INCONCLUSIVO |
| ΔR² real vs envelope E2 | acima | acima |
| Real descola do E2 em | 1 min | 1 min |
| M: classes | 4 indistinguível + 1 duas exp. | 5 duas exp. |

## O que isso diz

1. **O real prefere a reta em log-log nos dois períodos**, e com a mesma margem (ΔAIC ≈ −6). O ΔR² do real fica acima do envelope do E2 nos dois períodos e o real descola do E2 já no primeiro atraso: a autocorrelação de |r| do BTC é maior que a de um processo de duas exponenciais ajustadas em todas as escalas de 1 min a 1 dia.

2. **Mas o instrumento não distingue as formas com segurança nesta janela.** Em ago–set, duas réplicas do E2, que são duas exponenciais por construção (τ_ℓ entre 300 e 730 min), saíram "potência" pelo AIC. Com 21 atrasos até 1.440 min e uma escala lenta de 5 a 12 horas, a soma de duas exponenciais produz uma curva que a reta log-log ajusta quase tão bem quanto a forma verdadeira. É o que a aposta "indistinguível ~40 %" previa, e a validação pegou. A leitura honesta é: **o real parece lei de potência, e um processo de duas exponenciais com a escala lenta certa pode parecer também.** Não dá para fechar com 1 dia de atraso.

3. **O M, com a escala lenta real, agora saiu "duas exponenciais" em ago–set (5/5).** Isso é consistente com a leitura da Emenda 1 do H-TEMPO-01: o M não é uma nula de forma; ele é o real suavizado, e sua classificação acompanha o acaso da amostra.

4. **A escala lenta ajustada tem τ_ℓ de 5 a 12 horas** (φ_ℓ 0,997–0,999 por semana). Isso é descritivo, mas útil: dentro de uma semana, o log da volatilidade de 61 min do BTC se comporta como AR(1) com meia-vida de algumas horas. É a escala que o M "herda" e que o E2 reproduz sem copiar.

## Apostas

| Aposta | Prob. | Resultado |
|---|---|---|
| Real "potência" nos dois períodos | ~40 % | pela classe bruta, sim; pela regra, só jun–jul conta |
| Real "indistinguível" nos dois | ~40 % | não |
| Real "duas exponenciais" em algum | ~20 % | não |
| E2 passa na validação | ~75 % | errou: passou em jun–jul, reprovou em ago–set |
| ΔR² real acima do envelope E2 | ~70 % | acertou (dois períodos) |
| E2 descola antes de 2 h | ~65 % | acertou (1 min) |
| β real entre 0,1 e 0,2 | ~70 % | acertou (0,13 e 0,18) |

## O que faria a pergunta fechar

Mais atraso, não mais período. Com jun–set agrupado (122 dias) a grade pode ir a 3 ou 5 dias (4.320 a 7.200 min), onde uma escala lenta de 12 h já morreu e a lei de potência ainda não. A validação do E2 nessa grade diria se o instrumento passou a distinguir. É uma `PREDICAO` curta, nos mesmos meses abertos, e fica como próximo passo, não como parte desta rodada.

## Frase que fecha

Entre 1 minuto e 1 dia, a memória da volatilidade do BTC é maior em todas as escalas do que a de um processo honesto de duas exponenciais, e cabe numa reta em log-log com β ≈ 0,13–0,18. Se isso é lei de potência ou uma terceira escala, 1 dia de atraso não decide. Nada aqui é direção, previsão ou lucro.
