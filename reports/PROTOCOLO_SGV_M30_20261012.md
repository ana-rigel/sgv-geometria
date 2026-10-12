# SGV-M30 — O volume reage ao tamanho dos choques (pré-registro)

**Data:** 12/10/2026. **Ramo:** `research/m30-volume-reage-choques` (a partir de `research/m29-relogio-volume`). **`main` intocada. Só dados exploratórios** (1m mai–jul/2026).
**Ritmo:** 2º experimento do dia 12/10 (dentro da regra de 1–2 por dia), a pedido da Ana ("Continue, vamos conseguir").
**Antes deste documento:** nenhum código do M30 escrito; nenhum diagnóstico novo. A hipótese vem do diagnóstico das origens pares do M28 (`reports/m28diag/diag_pares.json`).

## De onde vem a hipótese
Depois do M29, o modelo (HXCLK) é pior que os blocos reais em **uma única estatística**: HSIC em 5 min (24% contra 11%). No diagnóstico das pares (observado contra o modelo local do M27), os componentes de "**magnitude agora → nível do volume depois**" eram os mais desalinhados em 5 min:
- |retorno| agora → volume daqui a 5 min: **acima** do modelo em 93% das origens (z mediano +1,2);
- |agressão| agora → volume daqui a 5 min: **abaixo** em 88% (z −1,75);
- |volume| (afastamento do normal, para cima ou para baixo) agora → volume depois: acima em 93% (z +1,15).
Leitura: o **nível** do volume responde ao **tamanho** dos choques — um movimento de preço grande atrai negociação nos minutos seguintes (atenção, reposicionamento); um fluxo muito desequilibrado é seguido de menos volume. O modelo atual faz o volume governar a **escala** do retorno e da agressão (M28), mas a média do volume só depende linearmente dos valores com sinal (HAR), não das magnitudes.

## Modelo
**`HXFB`** = HXCLK (M29: parâmetros locais em 6 trechos, variância cruzada, fator de atividade, relógio do minuto da hora, bloco lento real) com a **média do volume** acrescida de termos de magnitude:
ν_t = [HAR do M24] + β₁·(|z_{t−1}|, |ι_{t−1}|, |ν_{t−1}−m_ν|) + β₁₅·(média de 15 min dos mesmos) + ruído,
nas coordenadas do estado do modelo (sem bloco lento e sem relógio; m_ν = média do volume no trecho). Seis coeficientes a mais por trecho, por mínimos quadrados junto com o HAR, **só na equação do volume** (retorno e agressão inalterados). O resto do ajuste (variância cruzada, γ, inovações) segue o M28/M29 sobre os novos resíduos.
Referências pareadas: **`HXCLK`** (M29) e **`BL`**. Mesmas 12 estatísticas, 39 referências, posto conservador, alarme p ≤ 0,05. Roda nas 84 origens.

## Critérios pré-registrados
Conjunto de teste: as **42 origens ímpares** (a hipótese veio das pares; as ímpares já foram usadas como teste no M28 e M29 — registrado).
1. **Mecanismo (ímpares, teste do sinal unilateral, α = 0,05 cada):** efeito total de |retorno| (β₁ + β₁₅, mediana dos 6 trechos) **positivo** na maioria; efeito total de |agressão| **negativo** na maioria. Descritivo: efeito de |volume|.
2. **Primário (ímpares):** HXFB alarma menos que HXCLK em `hsic_5` e `hsic_1` (McNemar exato pareado, unilateral, α = 0,05/2 cada).
3. **Veredito do HXFB (84 origens):** "adequação plena" / "equivalente ao BL" (nenhuma das 12 significativamente pior, α = 0,05/12) / "não fecha a lacuna". Também só nas ímpares.
4. **Não piorar (descritivo):** nenhuma das outras 10 estatísticas piora contra o HXCLK (McNemar bilateral, α = 0,05/12).

## Ressalvas
- 42 origens: pouco poder (queda grande sem significância = "direção certa, sem poder").
- Ímpares reusadas pela terceira vez como teste; pares e ímpares são vizinhas no tempo. Confirmação de verdade só em dado virgem.
- Termos de magnitude podem, em princípio, desestabilizar a simulação; falhas contam contra o alarme (posto conservador) e serão reportadas.

## Apostas de Claude (antes de qualquer código)
| Item | Aposta |
|---|---|
| Efeito de |retorno| positivo (sinal significativo) | ≈ 80% |
| Efeito de |agressão| negativo (sinal significativo) | ≈ 70% |
| Primário significativo em `hsic_5` | ≈ 35% |
| Primário significativo em ≥ 1 das 2 | ≈ 40% |
| Veredito "equivalente ao BL" nas 84 | ≈ 40% |
| Veredito "adequação plena" nas 84 | ≈ 12% |
| Alguma estatística piora significativamente | ≈ 10% |
