# SGV-C02.1b — Errata prospectiva: orçamento de Monte Carlo ×4 no HDR95

**Data:** 14/10/2026.
- **Ramo:** `research/c02-1-hdr-sem-malha-20261014`.
- **Quando foi registrada:** antes de qualquer alteração de código posterior ao portão substituto C02.1a (`C02_1A_PORTAO_SUBSTITUTO_20261014.md`, commit `02dfae4`). Também antes do gerador oficial e de qualquer treino, validação ou OOD.
- **Escopo:** altera somente o que está escrito aqui. O protocolo C02, a emenda C02.1 e a errata C02.1a continuam valendo em todo o resto.
- **Retomada:** a Ana pausou a C02.1 em 14/10 e a retomou depois.

## Motivo

O portão substituto C02.1a falhou em quatro checagens, todas no HDR95 da família BS35 e todas de orçamento de Monte Carlo:

| Checagem | Valor | Limite |
|---|---|---|
| \|Δ\| Jaccard (dois casos) | 0,0214 e 0,0295 | 0,02 |
| ESS (dois casos) | 1.624–1.725 | 2.000 |

Nenhuma checagem falhou por instabilidade da medida, por ajuste inválido ou por cobertura. O ruído de Monte Carlo cai com a raiz do orçamento. Com ×4:
- a diferença entre execuções cai à metade (0,0295 → ~0,015);
- o ESS sobe ~4× (1.624 → ~6.500).

## Mudança única: orçamento do HDR95

Para α = 0,95, todos os tamanhos da seção 3 da emenda C02.1 passam a ser **128.000**:
- `n_cut`, `n_cover`, `n_vol`;
- `n_jac`, com 64.000 de cada componente da mistura;
- `n_cross`.

**O que não muda:**
- O HDR50 continua com 32.000.
- `w2_hdr` não usa Monte Carlo e não muda.
- Sementes, limites, regra de retenção, endpoint e todo o resto ficam iguais.

**Consequências (fixadas agora):**
- **Portão de precisão:** continua comparando a execução de produção (agora HDR50 ×1 e HDR95 ×4) com o dobro dela (HDR50 ×2 e HDR95 ×8).
- **Retenção:** os 5 reajustes por reamostragem usam o orçamento de produção, então a regra de retenção é **recalculada**. Isso pode mudar o conjunto retido em qualquer direção:
  - menos ruído de Monte Carlo nos reajustes tende a elevar a confiabilidade das variáveis do HDR95;
  - o ruído do **ajuste** do GMM3 não muda.
- **Nada é preservado do resultado anterior:** vale o conjunto que a regra der.

## Limite a novas erratas

Esta é a **última errata julgada no gerador substituto.** Iterar erratas sobre uma imitação até passar seria ajustar o instrumento a ela.

**Se o substituto passar com o C02.1b:** isso é evidência de engenharia, não aprovação.

**Se falhar:** a falha fica documentada, e o portão **oficial** roda mesmo assim, uma única vez, com as regras vigentes (C02.1 + C02.1a + C02.1b), sobre o gerador oficial integrado byte a byte. O gerador oficial é o pacote `SGV_C02_GERADOR_PILOTO_20261014.zip`, SHA-256 `4691266c…`. Ele ainda não está no ramo e depende da Ana.

## Aposta (Claude, antes de rerodar)

- **Portão substituto passa com o C02.1b: ~70 %.** O risco restante é:
  - o pior Jaccard ficar perto de 0,02 mesmo com metade do ruído;
  - a regra de retenção recalculada puxar para o bloco uma variável do HDR95 (centro ou forma) cuja checagem de precisão falhe.
- **Conjunto retido igual ao do C02.1a (7 variáveis): ~60 %.**
