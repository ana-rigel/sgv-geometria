# SGV-M17 — Que tipo de memória o BTC tem? (pré-registro)

**Data:** 10/10/2026. **Ramo:** `research/m17-tipo-de-memoria` (a partir de `research/m16-trio-btc-exploratorio@cfb9b3d`). **`main` intocada. Somente dados exploratórios** (1m mai–jul/2026; 1h 2020–2024), mesmas 84/18 origens do M16.
**Pedido da Ana:** "Qual memória — markoviana ou não markoviana?"
**Antes deste documento**, apenas: (i) uma inspeção descritiva da autocorrelação de |z| e ν nos dados exploratórios (ν no 1m: duas escalas, ~14 min e ~4 h; ν no 1h: pico em 168 h = ciclo semanal); (ii) ajuste dos nulos em **uma** origem por intervalo com semente de desenvolvimento, para checar engenharia. Esse teste mostrou que HMMs gaussianos comuns escolhem só escalas rápidas (maior escala ≈ 18 min no 1m), e por isso o desenho foi mudado **antes de qualquer posto ser calculado**: entrou um nulo de **duas escalas explícitas**. Nenhum posto, alarme ou taxa do M17 foi visto.

## Pergunta e mapa de leitura

Qual mecanismo de memória fecha a lacuna que o M16 encontrou (a régua energy alarmando muito, sinal de "falta memória/massa")?

| Nulo | Memória que oferece |
|---|---|
| `H2`, `H4` — HMM gaussiano 2/4 estados | Markov, escalas escolhidas pelo EM (na prática, rápidas) |
| `MS` — **duas escalas, Markov** | regime lento de atividade (decodificado da média móvel causal de ν: 60 barras no 1m, 24 no 1h) com durações geométricas; dentro de cada regime lento, um HMM rápido de 2 estados |
| `MSSM` — **duas escalas, semi-Markov** | igual ao MS, mas as durações do regime lento são reamostradas das durações reais do prefixo (regimes que "envelhecem") |
| `MSR`, `MSSMR` | MS / MSSM + **relógio**: perfil de ν por hora do dia (1m) ou hora da semana (1h), estimado no prefixo e reposto nos horários da janela |
| `N3` | âncora do M16 (regime-relógio, blocos longos) |

Todos ajustados **só no prefixo** de cada origem, em escores normais do prefixo (a medição re-gaussianiza cada janela por postos). 39 referências por nulo. Réguas: M11, Fisher–Rao, energy (`all_stats` do M15). Alarme: observado acima de ≥38 das 39 (nominal 5%).

## Contrastes pré-registrados (régua energy; McNemar exato pareado, unilateral; α = 0,05/5 = 0,01 cada; primário no 1m, o 1h é reportado com a mesma regra e é de baixo poder)

| Código | A alarma mais que B? | Se significativo |
|---|---|---|
| C1 escala lenta | H4 > MS | a memória que faltava é uma **escala lenta (horas)** que um Markov de 2 níveis captura |
| C2 envelhecimento | MS > MSSM | durações **não geométricas**: regimes que envelhecem → **não-markoviano** no regime |
| C3a relógio | MS > MSR | o **calendário** é parte da memória |
| C3b relógio | MSSM > MSSMR | idem, com semi-Markov |
| C4 mais estados | H2 > H4 | estados rápidos extras ajudam |

**"Fecha a lacuna"** (regra do M16): as três réguas com limite inferior de Wilson ≤ 7%.
**Leitura final pré-acordada:**
- C1 sim, C2 não → **Markov de várias escalas basta** (até onde estes dados distinguem).
- C2 sim → **não-markoviano no regime lento** (envelhecimento).
- C3 sim → relógio relevante (separadamente de Markov/não-Markov).
- Nenhum nulo da família MS perto de 7% na energy → a memória é mais complexa do que duas escalas (mais escalas, lei de potência ou acoplamento) — **não identificada** aqui.

Diagnósticos descritivos registrados por origem: escalas implícitas do H4 (−1/ln|λ| da matriz de transição), duração média dos regimes lentos, CV das durações e distância KS contra a geométrica de mesma média.

## Ressalvas declaradas antes

- **Poder de C2 é baixo no 1m:** um prefixo de 5000 min contém poucos regimes lentos completos (~4–5 por estado na origem de desenvolvimento), então o semi-Markov reamostra de poucas durações. No 1h há ~20 por estado.
- Emissões gaussianas por estado: os nulos HMM/MS podem errar a **forma** conjunta mais que o N3 (que usa linhas reais). A comparação **dentro** da família (H4/MS/MSSM/MSR/MSSMR) é controlada; a comparação com N3 é descritiva.
- As coordenadas do SGV são normalizadas localmente (σ em 60 barras; ν pela mediana de 1500), o que **corta memória muito lenta**: o M17 só pode falar da memória de médio alcance.
- Origens consecutivas não são independentes.

## Apostas de Claude (antes de qualquer resultado)

| Item | Aposta |
|---|---|
| energy 1m: H2 / H4 | 60–75% / 55–70% |
| energy 1m: MS | 30–45% |
| P(C1 significativo no 1m) | ≈ 85% |
| P(C2 significativo no 1m) — envelhecimento | ≈ 20% |
| P(C2 significativo no 1h) | ≈ 25% |
| P(C3a significativo no 1m) — relógio | ≈ 45% |
| P(C4 significativo no 1m) | ≈ 40% |
| P(algum nulo fecha a lacuna no 1m) | ≈ 10% |
| P(algum nulo MS* com energy menor que o N3 no 1m) | ≈ 35% |
| P(M11 do MS maior que M11 do N3 no 1m) | ≈ 70% |

Minha expectativa central: **Markov de várias escalas + relógio explica boa parte; envelhecimento não aparece com este poder; ainda sobra memória não explicada.**
