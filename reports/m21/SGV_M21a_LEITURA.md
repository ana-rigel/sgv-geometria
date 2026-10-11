# SGV-M21a — Por que o M11 falha sob o nulo de blocos longos, e o conserto

**Data:** 11/10/2026. **Tipo:** engenharia/diagnóstico. Só dados exploratórios e resultados já gravados; nenhum dado reservado novo.

## Diagnóstico
Reproduzi 234 referências BL (6 origens do M18 que tinham o M11 inválido): **7 falhas (3%)** — 6 "casca aberta" e 1 "cobertura insuficiente".
Causa: a gaussianização usa os primeiros 30% da janela como âncora; valores fora da faixa da âncora recebem o mesmo escore normal extremo. Quando **mais de ~10%** de uma metade cai fora dessa faixa, forma-se uma "pilha" num plano, a GMM2 cria um componente degenerado e a casca HDR50 sai aberta.
- Fração máxima empilhada: referências válidas, mediana 2,1% (q90 9,8%); **todas as que falharam estavam entre 10,5% e 28,4%**.
- Janelas observadas reais: mediana 1,7%, q90 5,6%, máximo 20,6% — o mesmo mecanismo pode ocorrer nelas, mais raramente.
- O nulo BL mistura blocos de 8 h de momentos diferentes, por isso sai da faixa da âncora com mais frequência.

**Por que isso importa:** a falha não é aleatória — acontece justamente quando a janela sai do repertório da âncora, que é uma forma de "novidade". A regra antiga (uma referência que falha invalida a célula) descartava ~1/3 das células com o M11 exatamente nessas situações.

## Conserto (sem mudar o instrumento)
**Posto conservador:** p = (1 + #(referências válidas ≥ observado) + #referências que falharam) / (R + 1). Uma falha conta como "pelo menos tão extrema quanto o observado". O teste continua válido (é estocasticamente maior que o posto ideal) e fica conservador; o valor do M11 continua o mesmo de antes. Observado que falha continua inválido. Teste unitário inclui verificação de nível sob nulo.

## Efeito nos resultados gravados
| | Antes | Com a regra |
|---|---|---|
| M18, BL, M11 válidas | 57/84 | **82/84** |
| M18, BL, M11 alarmes | 6 | 6 (7,3% [3,4–15,1]) |
| M19, M11 válidas | 23/58 | **54/58** |
| M19, M11 alarmes (evento / demais) | 0 / 0 | 0 / 1 |
| M19, alarme forte (evento / demais) | 2/15 / 1/43 | 2/15 / 1/43 |

Conclusões do M18 inalteradas (BL continua adequado). O veredito confirmatório do M19 **não muda e não pode mudar** — esta é só uma análise de sensibilidade pós-hoc.

## Pendência registrada
Uma versão do instrumento que estenda as caudas na gaussianização (em vez de empilhar no extremo) eliminaria a falha na origem, mas mudaria o M11 e exigiria recalibrar (M14/M15). Fica como opção, não como necessidade: com a regra conservadora, o M11 já é utilizável sob BL.
