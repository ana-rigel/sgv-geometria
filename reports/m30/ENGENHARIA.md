# M30 — Registro de engenharia (depois do protocolo, antes de qualquer posto)

Tudo abaixo foi visto **só na origem de desenvolvimento 0 (par)** e em simulações das origens pares 10 e 40, sem calcular nenhum posto.

1. **Simulações explodiam** (piloto falhou: ~8% das simulações do HXFB não finitas na origem 0). Causa: laço entre o termo |volume − normal| e o fator de atividade do M28 (exponencial no volume) quando o volume vai para valores muito baixos. Isso **não** podia ficar como "falha conta contra o alarme": com 39 referências, uma taxa de falha dessas suprimiria alarmes e favoreceria artificialmente o HXFB no primário.
   Correções (só de estabilidade, sem mudar o ajuste):
   - **Trava dos dois ramos:** o par de coeficientes de |volume − normal| é encolhido (×0,98 por passo) até que o modelo linear de cada ramo (volume acima/abaixo do normal) tenha raio < 0,995, como a trava do HAR desde o M24. Os termos de |retorno| e |agressão| não são tocados. Fator registrado por trecho (`beta_shrink`).
   - **Suporte do ajuste:** na simulação, o volume usado no fator de atividade fica dentro do intervalo visto no ajuste do trecho, e as magnitudes nos termos novos ficam limitadas ao máximo visto no trecho.
   Depois disso: 0 de 120 simulações não finitas (origens 0, 10, 40), também 0 no HXCLK.
2. **Colinearidade nos termos de 15 min** (observado na origem 0): os coeficientes das médias de 15 min das magnitudes saem grandes e negativos, trocando com o intercepto e com o HAR. O critério pré-registrado (efeito total β₁ + β₁₅) fica como está; **acrescento como descritivo** o efeito de 1 min (β₁) de |retorno| e |agressão|, que é o que o diagnóstico mediu (magnitude de um minuto → volume depois). Os dois são reportados; o pré-registrado decide.
3. Testes unitários: recuperam os sinais plantados (|retorno| +, |agressão| −), coeficientes pequenos sem realimentação, e a simulação reproduz a realimentação.
