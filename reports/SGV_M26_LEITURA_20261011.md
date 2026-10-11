# SGV-M26 — Leitura: resiliência da liquidez como volatilidade cruzada

**Execução:** GitHub Actions run 38177499459 (44 jobs, todos com sucesso). 83/84 origens válidas (1 falha de ajuste registrada). Só dados exploratórios. Recontagem independente confere (HARLMFX: Fisher–Rao 8/83, vol_5 17/83; BL: Fisher–Rao 9/83).

## 1. Mecanismo — confirmado (com a ressalva declarada no protocolo)
O termo **agressão ← retorno** saiu **negativo em 83 de 83 origens** (mediana −0,047; quartis −0,053 a −0,038; teste do sinal p ≈ 10⁻²⁵).
**No BTC 1m, um choque de preço reduz a volatilidade do desequilíbrio de agressão no minuto seguinte.** É a resiliência da liquidez: depois do movimento, o outro lado entra e o fluxo se reequilibra.
Ressalva: a previsão foi feita depois do diagnóstico do M25 e de ver o valor numa origem de desenvolvimento (declarado). É uma confirmação forte em dados exploratórios, não confirmatória; para virar resultado confirmatório, precisa ser julgada em dados virgens.

## 2. Ajuste às réguas
| | HARLMFV (M25) | **HARLMFX (M26)** | BL |
|---|---|---|---|
| **Fisher–Rao (acoplamento)** | 17% | **10%** | 11% |
| M11 / energy | 14 / 13% | 19 / 16% | 9 / 7% |
| vol 1/5/30 | 19 / 29 / 28% | **17 / 20 / 23%** | 10 / 7 / 7% |
| HSIC 1/5/30 | 17 / 28 / 30% | 19 / 27 / 31% | 8 / 11 / 14% |

- **O acoplamento agora é reproduzido**: a régua Fisher–Rao do modelo (10%) empata com os blocos reais (11%).
- **Primário de volatilidade: não significativo** (vol_5 p=0,033, acima do α corrigido de 0,0167).
- **Veredito pré-registrado: "não fecha a lacuna"** — ainda pior que o BL em vol_5, vol_30, HSIC (1, 5, 30) e M11.

## 3. Onde estamos depois de M23–M26
Com cada peça, o modelo explícito chegou perto dos blocos reais em **dependência linear, acoplamento e massa** (energy sem diferença significativa). O que resiste em todos os modelos, na faixa de 17–31%, é a **dependência não linear e de volatilidade nas defasagens de 5 a 30 minutos** — e cada nova peça agora reduz menos (retorno decrescente).
A hipótese mais provável para esse resto é **não estacionariedade dos parâmetros**: os blocos reais carregam a dinâmica *local* das últimas horas, enquanto os modelos usam parâmetros fixos estimados em ~3,5 dias. Isso é testável (estimar o modelo só no passado recente), mas é outra pergunta — não mais um mecanismo que falta, e sim o quanto o próprio funcionamento muda de um dia para o outro.

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Mecanismo c_ιz negativo (70%) | sim (83/83) | ✅ |
| Primário em vol_1 (50%) | não | ❌ |
| Primário nas três (20%) | não | ✅ (não ocorreu) |
| "Equivalente ao BL" (25%) | não | ✅ (não ocorreu) |
| "Adequação plena" (7%) | não | ✅ (não ocorreu) |
