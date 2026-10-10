# SGV-M18 — Acoplamento dinâmico × memória de longo alcance (pré-registro)

**Data:** 10/10/2026. **Ramo:** `research/m18-acoplamento-dinamico` (a partir de `research/m17-tipo-de-memoria@4233a32`). **`main` intocada. Somente dados exploratórios**, mesmas 84 (1m) / 18 (1h) origens do M16/M17.
**Recomendação da Ana:** "investigar a covariância dinâmica entre as três coordenadas, mantendo um controle para memória de longo alcance — para identificar se os alarmes restantes resultam de alterações no acoplamento informacional ou de dependências temporais ainda não representadas."
**Antes deste documento**, apenas: testes unitários (o DCC recupera a=0,06/b=0,90 em dados sintéticos e dá ganho ≈0 em dados estáticos) e ajuste dos nulos em **uma** origem por intervalo com semente de desenvolvimento (engenharia). Nenhum posto, alarme ou taxa do M18 foi visto.

## Desenho fatorial 2×2 (sobre o melhor modelo do M17, "MS" = Markov de duas escalas)

|  | acoplamento estático | **acoplamento dinâmico (DCC)** |
|---|---|---|
| sem memória longa | `MS` | `MSDCC` |
| **com memória longa** | `MSLM` | `MSDCCLM` |

- **DCC (acoplamento dinâmico):** dentro de cada estado (lento, rápido), as emissões são "branqueadas" pela covariância do próprio estado; as inovações branqueadas ganham correlação dinâmica DCC(1,1): Q_t = (1−a−b)I + a·e_{t−1}e_{t−1}ᵀ + b·Q_{t−1}, com (a, b) estimados por quase-verossimilhança **no prefixo**. Com a=b=0, reduz-se exatamente ao MS. Mede-se o acoplamento *entre* z, ι e ν que muda no tempo, além do que os estados já explicam.
- **LM (controle de memória longa):** ν é dividido em uma parte lenta contínua d_t (média móvel causal menos a média do seu regime lento) e o resto; o modelo é ajustado no resto, e cada janela simulada recebe um **bloco contíguo real** da sequência de regimes lentos e de d_t do prefixo. Assim, qualquer dependência de longo alcance do nível de atividade (até a extensão do prefixo) é **preservada, não modelada**.
- **Referências descritivas:** `BL` — blocos circulares longos de linhas reais do prefixo (500 barras no 1m ≈ 8 h; 168 no 1h = 1 semana), que preservam tudo até essa escala, inclusive acoplamento e forma reais; `N3` do M12.
- 39 referências por nulo; réguas M11, Fisher–Rao, energy; alarme = observado acima de ≥38 das 39.

## Contrastes pré-registrados (McNemar exato pareado, unilateral; α = 0,05/4 = 0,0125 cada; primário no 1m)

| Código | A alarma mais que B? | Régua |
|---|---|---|
| D1a | MS > MSDCC | Fisher–Rao (covariância) |
| D1b | MS > MSDCC | energy |
| D2a | MS > MSLM | Fisher–Rao |
| D2b | MS > MSLM | energy |

**Leitura pré-acordada:**
- D1 significativo (a ou b) e D2 não → **o resíduo é acoplamento informacional dinâmico**.
- D2 significativo e D1 não → **o resíduo é dependência temporal de longo alcance**.
- Ambos → os dois mecanismos contribuem (a interação é lida no `MSDCCLM`, descritivamente).
- Nenhum → nenhum dos dois explica o resíduo; olhar a referência `BL`: se ela praticamente fecha a lacuna, o que falta existe **dentro** de ~8 h de dados reais e é limitação da família paramétrica (por exemplo, forma não gaussiana); se nem `BL` fecha, o que falta é **não estacionariedade** entre o prefixo e a janela.

"Fecha a lacuna" = as três réguas com limite inferior de Wilson ≤ 7%. Diagnósticos descritivos: quartis de (a, b) do DCC e do ganho de verossimilhança contra o estático no prefixo.

## Ressalvas declaradas antes

- O DCC estimado no desenvolvimento tinha persistência de dezenas de barras (b ≈ 0,84–0,98). Como as réguas comparam **metades de ~500 barras**, flutuações de correlação mais rápidas que isso tendem a se cancelar dentro de cada metade: **o desenho tem pouco poder para acoplamento rápido**; ele detecta acoplamento que muda na escala de horas.
- O LM preserva memória longa **só do nível de atividade (ν)** e só até a extensão do prefixo (~3,5 dias no 1m; ~5 meses no 1h).
- Emissões gaussianas: a forma (M11) dos nulos paramétricos deve continuar pior que a do N3/BL; os contrastes são dentro da família.
- Origens consecutivas não são independentes.

## Apostas de Claude (antes de qualquer resultado)

| Item | Aposta |
|---|---|
| P(D1a significativo no 1m) — acoplamento na covariância | ≈ 30% |
| P(D1b significativo no 1m) — acoplamento na energy | ≈ 15% |
| P(D2a significativo no 1m) — memória longa na covariância | ≈ 50% |
| P(D2b significativo no 1m) — memória longa na energy | ≈ 55% |
| P(algum MS* fecha a lacuna no 1m) | ≈ 10% |
| BL com energy ≤ 15% no 1m | ≈ 60% |
| M11 de todos os MS* ≥ 25% no 1m | ≈ 75% |

Expectativa central: **a memória longa do nível de atividade explica mais do resíduo do que o acoplamento dinâmico**, porque as réguas comparam metades longas e o DCC estimado é rápido; o acoplamento que importa, se houver, é o que acompanha as mudanças lentas de regime.
