# SGV-M30 — Leitura: o volume reage ao tamanho dos choques

**Execução:** GitHub Actions run 38192411147 (44 jobs, todos com sucesso; resultados em `148efba`). **84/84 origens válidas**; teste nas 42 ímpares. **Nenhuma** simulação do HXFB falhou (as travas de estabilidade de `reports/m30/ENGENHARIA.md` funcionaram); 7 do HXCLK falharam. Recontagem independente confere (hsic_5: HXFB 16/84, BL 8/84, discordantes 10×2, p = 0,019).

## 1. Veredito pré-registrado: "equivalente ao BL" — pela primeira vez
| | HXCLK (M29) | **HXFB (M30)** | BL |
|---|---|---|---|
| M11 / Fisher–Rao / energy | 9 / 5 / 12% | **10 / 5 / 5%** | 12 / 10 / 10% |
| lin 1/5/30 | 8 / 14 / 21% | **8 / 8 / 13%** | 10 / 13 / 13% |
| vol 1/5/30 | 7 / 10 / 6% | **6 / 6 / 6%** | 11 / 8 / 11% |
| HSIC 1/5/30 | 17 / 24 / 29% | **11 / 19 / 18%** | 8 / 10 / 13% |

Nas 84 origens, o HXFB **não é significativamente pior que os blocos reais em nenhuma das 12 estatísticas** (α = 0,05/12); nas ímpares também. O que mais se aproxima é hsic_5 (19% contra 10%, 10×2, p = 0,019, acima do limite de 0,0042).
"Adequação plena" não: o HXFB fica elevado (Wilson inferior > 7%) em lin_30, hsic_5 e hsic_30 — e o próprio BL fica elevado em lin_5, lin_30 e hsic_30.

## 2. Mas não pelo caminho previsto
- **Primário: não.** Nas ímpares, hsic_5 (2×2) e hsic_1 (2×1) não mudam. O ganho veio sobretudo em **30 min** (hsic_30 29→18%, 10×1; lin_30 21→13%, 7×0) e em energy (12→5%) — descritivo, não pré-registrado.
- **Mecanismo, |agressão|: confirmado** — efeito total negativo em 40/42 ímpares (p ≈ 2·10⁻¹⁰): fluxo desequilibrado é seguido de menos volume. O efeito vem da média de 15 min (o de 1 min é fraco, 62% negativo).
- **Mecanismo, |retorno|: refutado no critério pré-registrado** — o efeito total sai **negativo** em 39/42. O efeito de **1 min** (descritivo, acrescentado na engenharia antes dos resultados) é **positivo em 42/42**: retorno grande → mais volume no minuto seguinte, como o diagnóstico mostrava; mas a média de 15 min de |retorno| entra com sinal oposto e maior. Duas leituras possíveis, não decididas aqui: (a) volume que sobe logo após um choque e cai depois de um período agitado (exaustão); (b) colinearidade entre a média de 15 min, o intercepto e o HAR (vista na origem de desenvolvimento). Pelo protocolo, **o critério pré-registrado decide: não apoiado.**

## 3. Ressalva importante: variabilidade entre execuções
O mesmo modelo HXCLK deu hsic_30 = **21%** no M29 e **29%** no M30 (sementes diferentes). Com 84 origens e 39 referências, a taxa de alarme de uma mesma estatística varia vários pontos de uma execução para outra. Comparações **pareadas dentro da mesma execução** (os McNemar) são as válidas; diferenças de poucos pontos entre tabelas de experimentos diferentes não são.

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| |retorno| total positivo (80%) | não (negativo, 39/42) | ❌ |
| |agressão| total negativo (70%) | sim (40/42) | ✅ |
| Primário em hsic_5 (35%) | não | ✅ (não ocorreu) |
| Primário em ≥ 1 (40%) | não | ✅ (não ocorreu) |
| "Equivalente ao BL" nas 84 (40%) | **sim** | ✅ (ocorreu) |
| "Adequação plena" (12%) | não | ✅ (não ocorreu) |
| Alguma estatística piora (10%) | não | ✅ (não ocorreu) |
