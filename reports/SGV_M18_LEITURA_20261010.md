# SGV-M18 — Leitura dos resultados contra o pré-registro

**Execução:** GitHub Actions run 38056193721 (50 jobs, todos com sucesso; 84/84 origens válidas no 1m, 18/18 no 1h). Somente dados exploratórios. Contagens da energy conferidas por recontagem independente. (Correção cosmética posterior: o cabeçalho da tabela gerada citava `m17_agregar.py`; o script certo é `m18_agregar.py` — números inalterados.)

## 1. Contrastes pré-registrados (1m, α = 0,0125)

| | Fisher–Rao (covariância) | Energy (memória/massa) |
|---|---|---|
| **D1 acoplamento dinâmico** (MS → MSDCC) | 44,0% → 38,1%, p=0,09 — **não** | 27,4% → 29,8% — **não** |
| **D2 memória longa** (MS → MSLM) | 44,0% → 35,7%, p=0,033 — não (abaixo do limiar corrigido) | **27,4% → 17,9%, p=0,004 — sim** (8×0) |

No 1h nenhum contraste é significativo (18 origens).

## 2. Leitura pré-acordada → resposta à pergunta

**D2 significativo e D1 não → o resíduo é dependência temporal de longo alcance**, no nível de atividade — não acoplamento informacional dinâmico (na escala que as réguas enxergam).

Detalhes que importam:
- **O acoplamento É dinâmico — mas rápido.** O DCC melhora a verossimilhança no prefixo em **todas** as origens (ganho mediano ≈ 34 nats no 1m), com a ≈ 0,014 e b ≈ 0,96: a correlação entre z, ι e ν oscila com meia-vida da ordem de dezenas de minutos. Essas oscilações se cancelam dentro de cada metade da janela (~500 barras) e **não explicam** o que as réguas veem. Ou seja: existe acoplamento dinâmico, mas ele não é a causa dos alarmes de forma/massa.
- **O que reduz os alarmes é dar ao modelo a trajetória lenta real do nível de atividade.** Com o bloco lento real (MSLM), a energy cai 9,5 p.p. e a Fisher–Rao 8,3 p.p.; juntando DCC + memória longa (MSDCCLM), chega-se ao melhor modelo paramétrico: energy 15,5%, Fisher–Rao 31,0%.
- **Referência decisiva — blocos longos reais (BL, ~8 h):** energy 9,5%, Fisher–Rao 9,5%, M11 10,5% → **fecha a lacuna** pela regra (todas as réguas com limite inferior de Wilson ≤ 7%). Então tudo o que falta existe **dentro de ~8 h de dados reais** — não é não estacionariedade entre o passado e a janela. É limitação da família paramétrica: forma conjunta não gaussiana, acoplamento lento acompanhando os regimes, ou memória de mais escalas.
  *Ressalva:* o M11 do BL foi inválido em 27 das 84 origens (ao menos uma das 39 referências falhou na reconstrução; regra estrita de não substituir). Energy e Fisher–Rao são válidas nas 84; a conclusão do BL se apoia nelas.
- **No 1h**, nem blocos de uma semana fecham a lacuna (energy 33%): na escala horária, a dependência relevante passa de uma semana — ou há não estacionariedade de meses. Baixo poder; descritivo.

## 3. Quadro acumulado M16 → M18 (1m, régua energy)

| Modelo de referência | Alarmes energy |
|---|---|
| blocos curtos (N0) | 72,6% |
| HMM 2 estados | 81,7% |
| HMM 4 estados | 46,3% |
| 2 escalas Markov (MS) | 27–30% |
| + memória longa real (MSLM) | 17,9% |
| + memória longa + DCC (MSDCCLM) | 15,5% |
| **blocos reais de ~8 h (BL)** | **9,5%** |

A memória do BTC no 1m é **multiescala e longa** — dos minutos às muitas horas —, e o acoplamento entre retorno, agressão e volume oscila rápido em torno de relações que mudam junto com os regimes lentos.

## 4. Placar das apostas de Claude

| Aposta | Resultado | |
|---|---|---|
| P(D1a) ≈ 30% | não | ✅ (não ocorreu) |
| P(D1b) ≈ 15% | não | ✅ (não ocorreu) |
| P(D2a) ≈ 50% | não (p=0,033, faltou pouco) | — |
| P(D2b) ≈ 55% | sim | ✅ |
| P(algum MS* fecha a lacuna) ≈ 10% | não | ✅ (não ocorreu) |
| BL com energy ≤ 15% (60%) | 9,5% | ✅ |
| M11 de todos os MS* ≥ 25% (75%) | não: MSDCC 25,9, MSLM 24,4, MSDCCLM 23,7 | ❌ (por pouco) |

A expectativa central registrada — "a memória longa explica mais do resíduo do que o acoplamento dinâmico" — **se confirmou**.

## 5. Próximo passo sugerido

Já sabemos **onde** está o que falta (dentro de ~8 h de dados reais) e **que tipo** de coisa é (memória longa do nível de atividade, mais forma conjunta real). Dois caminhos: (a) modelar a memória longa de forma explícita (por exemplo, nível de atividade com memória fracionária) e ver se ele chega perto do BL; (b) **usar o BL como nulo de trabalho** — ele é o primeiro nulo adequado nas três réguas no 1m — e voltar à pergunta das rupturas estruturais (M16): com um nulo adequado, um alarme passa a significar "algo que nem 8 h de passado real reproduz".
