# Previsão registrada antes de calcular (v2): a memória até 5 dias distingue potência de duas exponenciais?

**Registrada em:** 16/10/2026, depois da leitura da v1 (`LEITURA_memoria_potencia.md`) e antes de rodar qualquer coisa com a grade nova.

**Pedido da Ana:** "PODE RODAR", sobre o próximo passo da v1: mais atraso, não mais período.

**Status:** exploração. Meses abertos (jun–set). Nada de outubro; nada congelado muda.

**Ramo:** `exploracao/memoria-potencia`, a partir de 43518e9.

## O que muda em relação à v1

- **Grade de atrasos estendida:** os 21 atrasos da v1 mais 2.048, 2.880, 4.096, 5.760 e 7.200 min (26 atrasos, até 5 dias). Uma escala lenta de 5–12 h já morreu em 2 dias; uma lei de potência com β ≈ 0,15 ainda tem ρ ≈ 0,07 em 5 dias.
- **Período agrupado jun–set** (01/06 a 01/10, 122 dias, ≈ 176 mil minutos): a série principal. O atraso de 7.200 min usa ≈ 169 mil pares.
- **Dois períodos de controle** com a mesma grade: jun–jul e ago–set (61 dias cada; 7.200 min ainda cabe, com ≈ 80 mil pares).
- Tudo o mais igual à v1: a_t = |r_t|/s(h) com s(h) de maio; E2 (5 réplicas, 5026–5030) e M (5 réplicas) gerados a partir de 01/06; três ajustes em log ρ nos atrasos com ρ > 0; AIC; classes "potência" / "duas exponenciais" / "indistinguível" com |ΔAIC| > 2 e β em [0,1; 0,6]; validação do E2 (≥ 4 de 5 réplicas fora de "potência").

## Regra

- **Resultado principal:** a classe do real em jun–set, **se** o E2 validar em jun–set.
- **Estabilidade:** jun–jul e ago–set, com a grade estendida, dão a mesma classe para o real e o E2 valida em ambos. Se um dos dois reprovar na validação, o resultado principal fica, mas marcado "sem controle de estabilidade".
- **Descritivo:** ρ(τ) do real e do E2 nos atrasos longos; o primeiro atraso em que o real sai do envelope do E2; θ₁, θ₂ ajustados; a diferença de AIC em função do atraso máximo (recalculando o ajuste com a grade cortada em 1, 2, 3 e 5 dias), para ver onde a distinção aparece.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| E2 valida em jun–set com a grade de 5 dias | ~80 % |
| Real "potência" em jun–set | ~55 % |
| Real "indistinguível" em jun–set | ~30 % |
| Real "duas exponenciais" em jun–set | ~15 % |
| Estável (jun–jul e ago–set concordam e validam) | ~45 % |
| ρ(7.200) do real > 0,03 | ~60 % |
| ρ(7.200) do E2 < 0,02 em todas as réplicas | ~70 % |

## O que confirma e o que não

- **Potência, validada:** entre 1 min e 5 dias, a memória de |r| do BTC não cabe em duas exponenciais ajustadas. Fica como fato estilizado do instrumento, sem alegação de mecanismo.
- **Indistinguível:** nem 5 dias separam; a pergunta sai do alcance do SGV.
- **Duas exponenciais:** o resultado da v1 era artefato da janela curta.
- Em nenhum caso há direção, previsão ou lucro.
