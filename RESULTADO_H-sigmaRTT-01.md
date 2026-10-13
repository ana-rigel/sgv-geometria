# Resultado H-σRTT-01 (julgamento único, 13/10/2026)

Executado pelo workflow `confirmatorio-sigma.yml`, run 38441682316, com o código congelado (hashes da seção 5 do pré-registro conferidos no runner). A trava de paridade passou: o ensaio de junho–julho no runner reproduziu a referência. Agosto e setembro/2026 foram baixados da Binance e conferidos pelos `.CHECKSUM`. 61 dias julgados (01/08–30/09/2026).

| | D (média diária) | p unilateral | Decisão (Holm, m = 2) |
|---|---|---|---|
| **H1** real − sinais sorteados | +0,0125 | < 0,0001 | **confirmada** |
| **H2** real − dia invertido | +0,0033 | 0,18 | **não confirmada** |
| (descritivo) real − pipeline | +0,0018 | 0,31 | — |
| (descritivo) dias com real > máx de 8 réplicas de sinais | 11,5% (acaso ≈ 11,1%) | | — |

Comparação com a exploração (junho–julho): H1 caiu de +0,0217 para +0,0125; H2, de +0,0095 para +0,0033; o excesso sobre a pipeline, de +0,0147 para +0,0018.

## Leitura

- **H1 confirmada, mas o efeito não é temporal.** A pipeline, que mantém cada retorno com seu sinal e só embaralha a ordem dos minutos no dia, reproduz quase todo o excesso (pipeline − sinais = +0,0108 dos +0,0125). O que sobe o σ acima dos sinais sorteados é a relação entre sinal e tamanho dos retornos (a distribuição não é simétrica), uma propriedade estática que as fórmulas do SGV convertem em giro. A ordem real dos minutos acrescenta só +0,0018, sem significância.
- **H2 não confirmada.** Pelo poder registrado (68% no melhor caso), o resultado não distingue ausência de assimetria temporal de uma assimetria pequena. O efeito ficou em ~35% do observado na exploração.
- **O "excesso sobre a pipeline" visto na exploração não replicou.** Era a parte que sugeria estrutura na sequência de retornos.

## Apostas registradas antes dos dados

H1 ~75% (confirmada); H2 ~35% (não confirmada).

## Consequência

A linha "excesso de σ no espaço original" se resolve assim: há um excesso real sobre a nula de sinais sorteados, explicado por assimetria da distribuição dos retornos, não por dinâmica; nenhuma estrutura temporal ou flecha do tempo foi demonstrada. Agosto–setembro/2026 deixa de ser virgem; outubro/2026 continua intocado.
