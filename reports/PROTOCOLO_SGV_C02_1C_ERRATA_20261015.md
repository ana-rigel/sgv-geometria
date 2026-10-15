# SGV-C02.1c — Errata prospectiva: orçamento de Monte Carlo ×4 no HDR50 e ×16 no HDR95, para o portão oficial

**Data:** 15/10/2026. **Ramo:** `research/c02-1-hdr-sem-malha-20261014`.

**Quando foi registrada:**
- antes de qualquer alteração de código posterior aos diagnósticos do C02.1b (`C02_1B_DIAGNOSTICO_JACCARD95_20261015.md`);
- antes de integrar o gerador oficial;
- antes do portão oficial, e de qualquer treino, validação ou OOD.

**Decisão:** a Ana pediu que Claude escolhesse entre as três opções do relatório de diagnóstico. A escolhida foi a **(b)**, só orçamento.

**Escopo:** altera somente o que está escrito aqui. O protocolo C02, a emenda C02.1 e as erratas C02.1a e C02.1b continuam valendo em todo o resto.

## Desvio declarado

A errata C02.1b registrou que o portão oficial rodaria com as regras C02.1 + a + b. Esta errata desvia desse compromisso, pelos seguintes motivos:

1. **Os diagnósticos mostraram que o portão, com aquelas regras, seria quase um sorteio.** No substituto, 4 de 10 conjuntos de sementes bloqueiam, e as falhas aparecem tanto no HDR95 quanto no HDR50. Rodar o oficial assim seria apostar num resultado que o próprio extrator não controla.
2. **O desvio não usa nenhum desempenho de classificador.** Também não muda nenhum limite e não muda o critério "todas as checagens em todos os pares".
3. **Nenhuma nova execução no substituto julga esta errata.** O primeiro e único julgamento dela é o portão oficial.

## Mudança única: orçamento

| Nível | C02.1 / C02.1a | C02.1b | **C02.1c** |
|---|---|---|---|
| HDR50 (α = 0,50) | 32.000 | 32.000 | **128.000** (×4) |
| HDR95 (α = 0,95) | 32.000 | 128.000 | **512.000** (×16) |

**Onde vale:** em todos os tamanhos da seção 3 da emenda C02.1, no nível correspondente:
- `n_cut`, `n_cover` e `n_vol`;
- `n_jac`, metade de cada componente da mistura;
- `n_cross`.

**Como fica o portão de precisão:** continua comparando a produção com o dobro dela.

**Retenção:** os 5 reajustes da regra de retenção usam o orçamento de produção. A retenção é recalculada no gerador oficial, e vale o conjunto que a regra der.

**O que não muda:** `w2_hdr`, limites, sementes, regra de retenção, endpoint e todo o resto.

## Por que este orçamento (projeção feita com dados já existentes, sem rodar nada novo)

Com mais orçamento, o ruído de Monte Carlo cai com a raiz do aumento. Do C02.1b para o C02.1c:
- **×4 no HDR50:** o ruído cai à metade;
- **×4 no HDR95** (de 128 mil para 512 mil): o ruído também cai à metade.

**Nas 420 medições do diagnóstico do Jaccard do HDR95** (BS35 a ×4):

| Hipótese de redução da cauda | Maior \|Δ\| | Medições acima de 0,02 | Chance de os 21 pares do BS35 passarem |
|---|---|---|---|
| ruído ÷ 2 (raiz do orçamento) | 0,017 | 0 % | ~100 % |
| ÷ 1,43 (fator observado na cauda entre o C02.1a e o C02.1b, o pior caso) | 0,024 | 0,24 % | ~95 % |

**Nas checagens do HDR50 que falharam no diagnóstico de sementes** (centro no G3, Jaccard no BS35, 1 em 10 conjuntos cada), o orçamento ×4 reduz o ruído à metade pelo mesmo argumento. Não há medição direta desse efeito.

## Custo

Por execução de produção, ~4× o tempo de cálculo do C02.1b. O portão oficial (35 pares; produção, dobro e 5 reajustes por par) fica estimado em 1 a 2 horas nesta máquina.

## Ordem (inalterada da emenda C02.1, §6)

1. Esta errata.
2. Código: parâmetros de orçamento e testes analíticos.
3. Integração byte a byte do gerador oficial `SGV_C02_GERADOR_PILOTO_20261014.zip` (SHA-256 `4691266c…`), que depende da Ana.
4. Portão oficial, julgado uma única vez com as regras C02.1 + a + b + c.
5. Só então treino, validação, congelamento e uma única liberação OOD.

## Aposta (Claude, antes de qualquer execução)

- **Portão oficial passa com o C02.1c: ~80 %.** O risco restante:
  - o gerador oficial pode ser mais difícil que a imitação;
  - a projeção do HDR50 não foi medida;
  - um ajuste de GMM3 pode ser inválido no BS35 oficial.
