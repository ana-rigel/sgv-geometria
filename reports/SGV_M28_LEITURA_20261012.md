# SGV-M28 — Leitura: a atividade governa a escala

**Execução:** GitHub Actions (resultados no commit `a6594c2`). **84/84 origens válidas**; teste pré-registrado nas **42 origens ímpares**, não vistas no diagnóstico (feito nas pares). 8 de 9.828 simulações de referência do HXACT falharam (contadas contra o alarme, posto conservador).
Pós-hoc declarado (depois dos resultados): `scripts/m28_pos_hoc.py`, 10 origens ímpares, 19 referências por modelo; saída em `reports/m28/pos_hoc.json` e `pos_hoc.txt`. Correção de engenharia no pós-hoc: a primeira passada deu NaN porque algumas simulações raras do HXACT não eram finitas; a segunda descarta simulações não finitas (guardada a primeira em `pos_hoc_v1_nan.json`).

## 1. Mecanismo — confirmado nas origens de teste
| | Previsão | Resultado (ímpares) |
|---|---|---|
| γ_ι (agressão) | negativo | **42/42** negativas, mediana −0,084, p ≈ 2·10⁻¹³ |
| γ_z (retorno) | positivo | **41/42** positivas, mediana +0,043, p ≈ 10⁻¹¹ |
| γ_ν (volume, descritivo) | — | negativo em todas (mediana −0,068) |

**No BTC 1m, o nível de atividade governa a escala:** com mais volume, o retorno fica mais volátil e o desequilíbrio de agressão fica **mais concentrado perto de zero** (mais negócios → desequilíbrio relativo menor). É a hipótese da mistura de distribuições (o volume como relógio da informação), vista aqui minuto a minuto. O pós-hoc confirma que o modelo agora reproduz a relação contemporânea volume–|agressão| (z −0,95 → −0,10) e metade da relação defasada (volume agora → agressão mais equilibrada depois: modelo −0,008 → −0,042, observado −0,10).

## 2. Primário e veredito
- **Primário: não.** O HXACT não reduz os alarmes de HSIC nas ímpares (hsic_5 e hsic_30: 1×2 discordantes, p = 0,88).
- **Veredito pré-registrado (84): "não fecha a lacuna"** — pior que o BL só em hsic_5 e hsic_30 (27% e 25% contra 13–15%). Nas ímpares: "equivalente ao BL", sem poder para separar.
- **Nada piorou:** nenhuma das estatísticas já adequadas no M27 ficou significativamente pior.

## 3. Onde está o resto (pós-hoc, hipótese — não conclusão)
| Componente (z do observado contra o modelo) | HXLOC | HXACT |
|---|---|---|
| HSIC 3D sem o volume (retorno, agressão), 5 / 30 min | +0,10 / −0,28 | +0,13 / −0,29 |
| HSIC 3D completo, 5 / 30 min | +0,60 / +0,51 | +0,49 / +0,42 |
| HSIC volume → volume, 30 min | +0,91 | +0,79 (obs 0,0026 × modelo 0,0017) |

Tirando o volume, a dependência não linear entre instantes **já está reproduzida**. O que sobra no HSIC mora na **dinâmica própria do volume**, sobretudo em 30 min. O diagnóstico das pares já apontava isso (persistência linear do volume em 30 min acima do modelo em 76% das origens; |volume| agora → volume depois acima em 93%).

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| γ_ι negativo (85%) | sim (42/42) | ✅ |
| γ_z positivo (60%) | sim (41/42) | ✅ |
| Primário em hsic_5 (35%) | não | ✅ (não ocorreu) |
| Primário em ≥ 1 (45%) | não | ✅ (não ocorreu) |
| "Equivalente ao BL" nas 84 (35%) | não | ✅ (não ocorreu) |
| "Adequação plena" (8%) | não | ✅ (não ocorreu) |
| Alguma estatística piora (10%) | não | ✅ (não ocorreu) |
