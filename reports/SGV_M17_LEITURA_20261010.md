# SGV-M17 — Leitura dos resultados contra o pré-registro

**Execução:** GitHub Actions run 38019934899 (50 jobs, todos com sucesso). 1m: 82 de 84 origens válidas (2 falharam porque o prefixo tinha menos de 3 regimes lentos completos num estado — registradas, não substituídas). 1h: 18/18. Contagens principais conferidas por recontagem independente. Somente dados exploratórios.

## 1. Contrastes pré-registrados (régua energy, α = 0,01)

| | 1m | 1h (baixo poder) |
|---|---|---|
| C4 mais estados rápidos (H2 → H4) | **81,7% → 46,3%, significativo** (29×0) | 83,3% → 50,0%, p=0,016 |
| C1 escala lenta (H4 → MS) | **46,3% → 30,5%, significativo** (14×1) | 50,0% → 44,4%, n.s. |
| C2 envelhecimento (MS → MSSM) | 30,5% → 32,9%, **não** | 44,4% → 44,4%, não |
| C3 relógio (MS → MSR; MSSM → MSSMR) | 30,5% → 30,5%; 32,9% → 31,7%, **não** | 44 → 39%, n.s. |

Nenhum nulo fecha a lacuna (todos com a energy bem acima de 7%).

## 2. Leitura pré-acordada → resposta à pergunta da Ana

**C1 sim, C2 não → "Markov de várias escalas basta, até onde estes dados distinguem"** — com a ressalva, também pré-acordada, de que **sobra memória não identificada**:
- Cada escala que se acrescenta ao modelo markoviano reduz a lacuna: estados rápidos extras (−35 p.p.) e depois uma escala lenta de horas (−16 p.p.).
- **Dar aos regimes durações reais (não-markovianas) não muda nada**: MS 30,5% vs MSSM 32,9%. Curiosamente, as durações reais dos regimes lentos são **mais regulares** que as de um processo sem memória (CV mediano 0,84 no 1m e 0,62 no 1h, contra ~1 da geométrica) — os regimes "envelhecem" um pouco —, mas isso não aparece em nenhuma régua.
- O **relógio** (hora do dia no 1m, hora da semana no 1h) não acrescenta nada além da escala lenta.
- **Sobram ~30% de alarmes na energy** com a melhor família — praticamente o mesmo nível do N3 (26,8%), que usa linhas reais do mercado. Ou seja: o que falta **não é** duração de regime nem calendário.

## 3. O que sobra, e onde procurar

1. **Acoplamento que muda no tempo.** A Fisher–Rao (covariância) fica em ~45–49% em **todos** os nulos paramétricos do 1m, inclusive os de duas escalas — muito acima do N3 (15,9%). É o mesmo sinal do N1 no M16: a relação entre retorno, agressão e volume se reorganiza de um jeito que modelos com covariância fixa por estado não reproduzem.
2. **Memória mais lenta que o prefixo** (ou não estacionariedade de dias/semanas). O prefixo tem ~3,5 dias no 1m; a escala lenta estimada já é de ~3,4 h com só ~4–5 regimes por prefixo. Memória de lei de potência não pode ser vista com as coordenadas atuais, que são normalizadas localmente.
3. **A forma dos nulos gaussianos é pior que a do N3** (M11 30% vs 7,8% no 1m), como previsto: as emissões gaussianas por estado não reproduzem a forma conjunta real. Isso não afeta os contrastes dentro da família, mas mostra que **a forma conjunta real (não gaussiana) é parte do que o mercado é**.

## 4. Placar das apostas de Claude

| Aposta | Resultado | |
|---|---|---|
| energy 1m H2 60–75% / H4 55–70% | 81,7% / 46,3% | ❌ ❌ (H2 pior, H4 melhor que o previsto) |
| energy 1m MS 30–45% | 30,5% | ✅ (na borda) |
| C1 no 1m (85%) | sim | ✅ |
| C2 no 1m (20%) / no 1h (25%) | não / não | ✅ (não ocorreu) |
| C3a no 1m (45%) | não | — (não ocorreu) |
| C4 no 1m (40%) | sim | ❌ contra a aposta |
| algum nulo fecha a lacuna (10%) | não | ✅ (não ocorreu) |
| algum MS* com energy < N3 no 1m (35%) | não | ✅ (não ocorreu) |
| M11 do MS > M11 do N3 (70%) | sim (30,0% vs 7,8%) | ✅ |

## 5. Próximo passo natural

Atacar o resíduo que sobrou com as duas pistas: (a) **covariância variável no tempo** dentro dos regimes (por exemplo, correlação dinâmica entre z, ι e ν), medindo se a Fisher–Rao cai; (b) **coordenadas sem normalização local** (ou com janelas de normalização mais longas), para ver se existe memória de lei de potência que as coordenadas atuais cortam.
