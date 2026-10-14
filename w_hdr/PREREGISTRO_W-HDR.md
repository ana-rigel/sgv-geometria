# W-HDR — a distância entre cascas HDR do M11-I contra o transporte ótimo (Wasserstein)

**Registrado em 14/10/2026, antes do código.** Sintético; mesmo gerador do U2 (`u2_rotulador/gerar.py`, famílias, mecanismos, N = 750, grade 25³, ordem canônica).

## Medidas comparadas (todas no referencial branqueado pela média e covariância de A)

- **M11-I:** `distance_512` (casca HDR50 contra casca HDR50, depois do alinhamento) e |ΔD|.
- **W₂ completo:** distância de Wasserstein-2 exata entre as duas amostras (casamento ótimo 750 × 750).
- **W₂-HDR:** W₂ exato entre os pontos de cada amostra que estão no seu próprio HDR50 (os 50 % de maior densidade segundo o GMM2 do próprio M11-I, ajustado com a mesma semente; 375 contra 375). É a "distância no HDR" pelo transporte, sem malha.
- **MMD² RBF:** como no U1/U2.
- **Decomposição de W₂²:** parte de média ‖Δμ‖², parte de covariância (Bures²), e resto de forma = W₂² − ‖Δμ‖² − Bures² (o que sobra além de uma gaussiana).

## Parte A — detecção com dose-resposta

- Mecanismos do U2 com intensidade k ∈ {0,25; 0,50; 0,75; 1,00} da intensidade do U2 (translação δ·k; escala 1 + (s−1)·k; rotação ângulo·k; bimodal a·k; curvatura c·k; caudas fator 1 + 1,5·k).
- Famílias gaussiana e t₆; 15 réplicas por família; em cada réplica, 4 nulos (amostra nova da mesma distribuição) e 24 alternativas (6 mecanismos × 4 intensidades).
- Limiar de cada medida = q95 da metade dos nulos (réplicas pares); falso alarme conferido na outra metade (réplicas ímpares). Desfecho: taxa de detecção por medida × mecanismo × intensidade (30 alternativas por célula).
- **Apostas:** W₂ completo detecta mais que o M11-I em translação, escala, rotação e caudas em todas as intensidades; M11-I empata ou ganha de W₂ em bimodal e curvatura nas intensidades baixas; W₂-HDR ganha de W₂ completo em bimodal e curvatura e perde em caudas; MMD é o melhor detector geral; falso alarme de todos entre 0 % e 15 % na metade de conferência.

## Parte B — rotular o mecanismo (as 630 comparações do U2, mesmas sementes)

- As amostras do U2 são regeneradas pelo mesmo código e sementes (o gerador do U2 não consome o RNG ao ajustar cascas); só se acrescentam as variáveis W. Conferência: as variáveis convencionais regeneradas têm de bater com `variaveis.csv` até 10⁻⁹.
- **Painel W (5 variáveis):** W₂², ‖Δμ‖², Bures², resto de forma, W₂-HDR². Mesmo classificador e validação do U2 (floresta 500 árvores; deixa uma família de fora).
- **Apostas:** painel W > M11-I em F1 macro por mais de 0,10; painel W < convencional; convencional + W ≈ convencional (|Δ F1| < 0,03), porque média e Bures são funções dos mesmos momentos; o resto de forma ajuda em bimodal e curvatura mais que o ΔD do M11-I.

## Fora do escopo

Entropia de transferência e expoentes de Lyapunov medem dinâmica temporal, não distância entre duas nuvens; não entram aqui.
