# Resultado DG-01: o +0,64 do BTC sobrevive à troca de régua?

**Leitura pela regra registrada: NÃO é artefato do GMM2.** Exploratório; BTCUSDT 1m jun–jul/2026, já explorado. Código e leitura congelados antes dos resultados (`5e7994d`, `a1e0067`).

**Paridade:** a régua atual (A0) reproduziu exatamente os números já conhecidos: +0,638 em 291 pares e +0,656 em 20 pares disjuntos.

## ρ entre a feature de caudas e Δlog(q99,9/mediana de |r|)

| Construção | Real, relatório | Nula, relatório | Real, disjunto | Nula, disjunto |
|---|---|---|---|---|
| A0, atual (malhas do vendor) | **+0,638** (291) | +0,521 (336) | +0,656 (20) | +0,083 (25) |
| B, GMM2 + Hyndman | +0,620 (359) | +0,485 (359) | +0,612 (26) | +0,134 (26) |
| C, GMM3 + Hyndman | **+0,642** (359) | +0,594 (359) | +0,597 (26) | +0,331 (26) |
| D, mistura de t | +0,605 (313) | +0,599 (276) | +0,577 (22) | +0,326 (20) |
| E, KDE | +0,559 (359) | +0,501 (359) | +0,493 (26) | +0,136 (26) |

**Concordância da feature com a A0, par a par (ρ):** 0,95 a 0,98 no real.

## Leitura

1. **A ligação do BTC não vem do viés do GMM2.** Com qualquer uma das quatro alternativas, ρ fica entre 0,56 e 0,64. A feature calculada pela régua atual e pelas alternativas é praticamente a mesma, par a par (0,95–0,98). O viés de caudas espúrias que o RB-01 achou nos sintéticos de caudas pesadas não pesa no BTC jun–jul.
2. **A régua atual perde janelas, mas isso não muda o resultado.** As alternativas aproveitam 359 pares, contra 291 da A0, e o ρ fica igual.
3. **A nula de pipeline reproduz a maior parte da ligação no desenho do relatório** (0,49–0,60 contra 0,56–0,64). Pela regra registrada (real acima da nula), a leitura não muda. Mas o recado é claro: a feature acompanha a cauda **do conjunto de retornos de cada janela**, qualquer que seja a ordem em que aconteceram. Para um medidor de cauda, é o comportamento esperado: a cauda de uma janela não depende da ordem dos minutos. O resultado é de **validade do instrumento**, não de estrutura temporal do mercado. Parte da ligação é mecânica, porque E_norm é construído a partir do preço. No desenho disjunto, a nula fica mais baixa (0,08–0,33), mas com 20–26 pares e janelas que, no desenho do relatório, se repetem entre pares.
4. **Consequência para o LTC (H-CASCA-01).** Como a troca de régua não mexe no BTC, fica menos provável que a queda para +0,35 no LTC venha da régua. A explicação mais provável passa a ser o próprio LTC: a cauda do E_norm traduz pior a cauda do retorno (contra a curtose de E_norm, o LTC deu +0,53; contra o preço, +0,35). Isso corrige a hipótese, levantada antes deste diagnóstico, de que "parte da queda pode ser da régua".

## Aposta registrada

~45% de "não é artefato": acertou.
