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

---

# Leitura v2 (grade até 5 dias): o instrumento reprova, e o motivo é duplo

**Previsão:** `PREDICAO_memoria_potencia_v2.md` (222740e). **Resultados:** `resultados/memoria_potencia_v2_{junjul,agoset,junset}.json` (jun–jul local; ago–set e jun–set no run 38929348276).

## Veredito pela regra: INCONCLUSIVO nos três períodos

O E2 reprovou a validação em jun–jul, ago–set e jun–set: com a grade até 5 dias, **todas** as réplicas do E2 saem "potência", e o M também. O real sai "potência" nos três (ΔAIC −9,6 / −7,0 / −8,2; β 0,14 / 0,21 / 0,16), mas isso não conta, porque o instrumento classifica como potência até o que é duas exponenciais por construção.

## Por que reprovou: dois defeitos de desenho, os dois meus

1. **A sazonalidade diária não foi removida.** O perfil s(h) de maio tira a média por minuto do dia, mas não o fato de que dias se parecem com dias. A ρ(τ) do real **sobe** nos múltiplos de 1.440: 0,072 em 2.048 → 0,125 em 2.880 → 0,051 em 4.096 → 0,088 em 5.760. Dois dos cinco atrasos novos caem exatamente em 2 e 4 dias. O E2 herda o mesmo calombo, porque usa o mesmo s(h) e a mesma regua de minutos. Nenhuma das três formas ajusta uma curva com calombos periódicos, e o AIC escolhe a reta porque ela é a menos errada. A grade da v1 também tinha 1.440 e eu já tinha notado o calombo (Emenda 1 do H-TEMPO-01); estendê-la sem tirar os múltiplos de um dia foi erro.

2. **O E2 é re-ancorado no real toda semana.** A escala lenta é simulada por semana "partindo do ℓ real do primeiro minuto da semana", com c e φ_ℓ ajustados na semana. Isso reinjeta no E2, a cada 7 dias, o nível real de volatilidade, e os parâmetros semanais acompanham o real. Em atrasos de 1 a 5 dias, o E2 passa a carregar memória do real através das âncoras semanais. Na v1, com atrasos até 1 dia, isso quase não pesava; de 2 dias em diante, pesa. O θ ajustado do E2 em exponencial única, 5.000 a 10.000 min, é a assinatura: um AR(1) semanal com τ_ℓ de 5–12 h não deveria mostrar memória de 4 a 7 dias.

## O que sobrevive

- O real continua acima do E2 em todos os atrasos curtos (descola em 1 min), e sua ΔR² ficou **dentro ou abaixo** do envelope E2 na grade longa, não acima como na v1. Isso é consequência do defeito 2, não do mercado.
- β do real: 0,14–0,21, estável entre v1 e v2 e entre períodos.
- A pergunta "potência ou duas exponenciais entre 1 min e 5 dias" **não foi respondida** nesta rodada, nem a favor nem contra.

## O que a v3 precisa (não rodada; registrar antes)

1. Grade sem múltiplos de 1.440 nem de 10.080: atrasos longos em 1,5, 2,5, 3,5 e 4,5 dias, ou dessazonalização por diferença (ρ de a_t − a_{t−1440}).
2. E2 gerado de uma vez para o período inteiro: um só ajuste de (c, φ_ℓ, Var η) em jun–set e uma só trajetória simulada, sem re-ancorar por semana; a escala rápida idem.
3. Validação com 10 réplicas, e exigência de que o E2 saia "duas exponenciais" (não só "fora de potência") em ≥ 8.

## Apostas da v2

| Aposta | Prob. | Resultado |
|---|---|---|
| E2 valida em jun–set | ~80 % | errou, e por muito |
| Real "potência" em jun–set | ~55 % | pela classe bruta sim; não conta |
| Estável | ~45 % | não |
| ρ(7.200) real > 0,03 | ~60 % | acertou (0,074), mas inflado pela sazonalidade |
| ρ(7.200) E2 < 0,02 em todas | ~70 % | errou (defeito 2) |

## Frase que fecha

A v2 não mediu o mercado; mediu o instrumento, e o instrumento reprovou. Dois defeitos meus: a grade de atrasos pisa nos múltiplos de um dia e o sintético é re-ancorado no real toda semana. Ficam escritos para a v3. O que se mantém de descritivo é o β ≈ 0,15 do real e o fato de que ele tem mais memória curta que qualquer sintético de duas escalas.
