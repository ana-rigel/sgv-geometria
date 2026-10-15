# SGV-C02.1b — Diagnóstico de sementes do portão substituto (não altera o veredito)

**Data:** 14/10/2026. **Registrado antes de rodar.**

**Pedido da Ana:** testar de novo, porque a falha do C02.1b foi pequena (Jaccard do HDR95 0,0207 contra o limite de 0,02).

## O que este diagnóstico é

O par de execuções de precisão (produção: HDR50 ×1, HDR95 ×4; comparação: o dobro) é repetido com **10 conjuntos novos de sementes de Monte Carlo** (`ml1|diagK`, `ml2|diagK`, K = 1..10) nos mesmos 42 pares do substituto. Ficam fixos:
- os ajustes GMM3 (mesmas sementes);
- o conjunto retido (as 7 variáveis do C02.1b);
- os limites.

Para cada conjunto se registram:
- se o portão passaria;
- quais checagens falham;
- o maior |Δ Jaccard| do HDR95.

## O que este diagnóstico não é

Não é uma nova tentativa do portão. **O veredito do C02.1b continua BLOQUEADO.** Ele foi julgado com as sementes registradas (`ml1`, `ml2`), e nenhum resultado aqui o substitui.

O objetivo é medir a **taxa de falha por acaso** do portão com este orçamento:
- **Raras** (≤ 1 em 10): a falha do C02.1b foi azar, e o portão oficial tem boa chance.
- **Frequentes** (≥ 3 em 10): o limite de 0,02 está no nível do ruído do Jaccard do HDR95 no BS35. O portão oficial seria quase um sorteio, e isso precisa ser dito antes de rodá-lo.

## Aposta (Claude, antes de rodar)

~35 % dos conjuntos com alguma falha. No C02.1b, 1 de 21 pares do BS35 passou do limite, e o p90 de |Δ| foi 0,0126.
