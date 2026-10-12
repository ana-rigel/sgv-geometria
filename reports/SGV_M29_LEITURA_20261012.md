# SGV-M29 — Leitura: o relógio do volume

**Execução:** GitHub Actions run 38190384553 (44 jobs, todos com sucesso; resultados em `03d5877`). **84/84 origens válidas**; teste nas 42 ímpares. 10 simulações de referência falharam no total (contadas contra o alarme). Recontagem independente confere (hsic_30: HXCLK 18/84 contra HXACT 24/84; ímpares 4×1).

## 1. O relógio existe
Em **81% das origens ímpares** (34/42, p ≈ 3·10⁻⁵), o perfil estimado só no passado de 3,5 dias tem o **minuto :00 como o de maior volume**; a correlação mediana com o perfil do diagnóstico das pares é **0,71**, e o encolhimento mediano mantém 59% do perfil (nunca zero). **O volume do BTC tem um relógio no minuto da hora:** pico na virada da hora, outro na meia hora, vale logo antes da virada.

## 2. Efeito nas réguas
| | HXACT (M28) | **HXCLK (M29)** | BL |
|---|---|---|---|
| HSIC 1 / 5 / 30 (84) | 14 / 25 / 29% | **17 / 24 / 21%** | 10 / 11 / 13% |
| HSIC 30 (ímpares) | 31% | **24%** | 17% |

- **Primário: não significativo.** hsic_30 cai de 29% para 21% (nas ímpares, 4×1 discordantes, p = 0,19); hsic_5 não muda (2×1). Pelo protocolo: direção certa em 30 min, sem poder; nada em 5 min.
- **Veredito pré-registrado (84): "não fecha a lacuna"** — mas agora o HXCLK é significativamente pior que o BL **só em hsic_5** (11×0). hsic_30 deixou de ser significativamente pior (p = 0,008, acima de 0,0042). Nas ímpares: "equivalente ao BL".
- **Nada piorou** contra o HXACT.

## 3. O que sobra: uma estatística, uma defasagem
Do que eram 7 de 12 estatísticas piores que os blocos reais no M24, resta **uma**: a dependência não linear em **5 minutos** (24% contra 11%). O diagnóstico das pares do M28 já apontava o candidato: **o nível do volume reage a magnitudes** — retorno grande agora → volume maior daqui a 5 min (acima do modelo em 93% das origens) e agressão desequilibrada agora → volume menor depois (abaixo em 88%). O modelo atual liga o volume à **escala** do retorno e da agressão (M28), mas não faz o **nível** do volume responder ao tamanho dos choques. Hipótese, ainda não testada.

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário em hsic_30 (35%) | não (p = 0,19) | ✅ (não ocorreu) |
| Primário em hsic_5 (20%) | não | ✅ (não ocorreu) |
| Primário em ≥ 1 (40%) | não | ✅ (não ocorreu) |
| "Equivalente ao BL" nas 84 (35%) | não (por uma estatística) | ✅ (não ocorreu) |
| "Adequação plena" (10%) | não | ✅ (não ocorreu) |
| Alguma estatística piora (10%) | não | ✅ (não ocorreu) |
| :00 mais alto em > 50% das ímpares (75%) | sim (81%) | ✅ |
