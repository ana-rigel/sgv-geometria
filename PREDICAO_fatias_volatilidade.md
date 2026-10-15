# Previsão registrada antes de calcular: fixando a volatilidade, a geometria do cubo fica mais simples?

**Registrada em:** 15/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "Sim, rode 1 e 2". Se refere aos testes geométricos de "a volatilidade como 4ª dimensão": fatiar por temperatura e colapso de escala.

**Status:** exploração, **não** confirmatória. Jun–set já foram abertos. Nada de outubro é lido, e nada congelado muda (H-VOL-01, H-DIF-01 e os demais).

**Ramo:** `exploracao/fatias-volatilidade`, a partir de `exploracao/volatilidade-multiescala@5c55d4a`.

## Espaço, temperatura e fatias

- **Espaço:** o original (E_norm, jerk, memory_flux) na régua de caudas, com âncora em maio. Extremidade = max |xⱼ|.
- **Temperatura:** σ̂ = `har`, a raiz da média das variâncias realizadas de 10, 60 e 240 min, com retornos até t, causal. É a estimativa multiescala das rodadas anteriores.
- **Fatias:** os tercis de log σ̂ **em maio** (limites fixos): calma, média e quente. Cada minuto pertence à fatia da sua temperatura.

## Teste 1 — fatiar o cubo por temperatura

**1a. A borda agitada encolhe dentro de cada fatia?**
- **Campo:** o estimador localmente linear das rodadas anteriores (k = 200, tricúbico, correção por ESS).
- **Treino e avaliação:** o campo de uma fatia é treinado só com os passos dos minutos **daquela fatia** na semana anterior, e avaliado nos minutos daquela fatia na semana seguinte.
- **Pontos avaliados:** até 3.000 sorteados com extremidade < 1, mais todos com extremidade ≥ 1 (semente 20261019).
- **Estatística:** R = mediana de D com 3 ≤ extremidade < 10, dividida pela mediana de D com extremidade < 1.
  - Calculada para todos os minutos juntos (R_todos, como na geometria residual).
  - E para cada fatia que tenha ≥ 30 minutos extremos avaliados. **R_fatias** = média dessas fatias.
- **Classificação, por período:**
  - **"A temperatura explica a borda agitada":** R_fatias ≤ 0,5 · R_todos.
  - **"Explica em parte":** 0,5 · R_todos < R_fatias ≤ 0,8 · R_todos.
  - **"Não explica":** R_fatias > 0,8 · R_todos.

**1b. As cascas de cada fatia ficam mais estáveis?**
- **Mapas:** um a cada 240 min, com janela de 1.500 min.
- **Casca de uma fatia:** HDR50 de `build_shell` (semente 20261009, n = 25) só com os minutos da janela que pertencem à fatia. São necessários ≥ 300 pontos.
- **Pares:** a 28 h (7 mapas).
- **Estatística:** a rotação mediana do eixo principal, para todos os minutos e para cada fatia. **rot_fatias** = média das fatias.
- **Classificação:**
  - **"Mais estáveis":** rot_fatias < rot_todos nos dois períodos.
  - **"Não":** o resto.

## Teste 2 — colapso de escala

Se as fatias diferem só pela temperatura, o campo medido em **unidades de volatilidade** é o mesmo nas três.

- **Bandas de extremidade:** núcleo < 1, meio 1–3, extremos 3–10.
- **Medida bruta:** D_bruto = a mediana do campo (como em 1a) em cada fatia e banda.
- **Medida em unidades de volatilidade:** D_padr = o mesmo, com os passos divididos por σ̂ do minuto de partida.
- **Dispersão entre fatias:** em cada banda, a amplitude entre as três fatias de log D. **Disp_bruto** e **Disp_padr** = média sobre as bandas com dados nas três fatias.
- **Índice de colapso:** C = 1 − Disp_padr / Disp_bruto.
- **Classificação, por período:**
  - **"Colapsa":** C ≥ 0,7. A temperatura é um zoom do mesmo objeto.
  - **"Colapsa em parte":** 0,3 ≤ C < 0,7.
  - **"Não colapsa":** C < 0,3. A temperatura muda também a forma.

## Referência (descritiva, sem critério)

O sintético M da rodada multiescala, 2 réplicas (sementes 4026 e 4027), passa pelas mesmas medidas. Nele a volatilidade é, por construção, a única variável escondida. Ele mostra quanto R encolhe e quanto C vale num mundo onde a 4ª dimensão é exatamente a volatilidade, com as mesmas amostras finitas.

## Regra geral

**Só conta se repetir nos dois períodos** (jun–jul e ago–set). Senão, "não estável".

## Aposta de Claude, antes de tudo

| Aposta | Probabilidade |
|---|---|
| 1a "explica" (≤ 0,5) | ~40 % |
| 1a "em parte" | ~40 % |
| 1a "não explica" | ~20 % |
| 1b "mais estáveis" | ~40 % |
| 2 "colapsa" | ~35 % |
| 2 "em parte" | ~45 % |
| 2 "não colapsa" | ~20 % |

## Como roda

- **Fumaça:** maio, sem imprimir estatísticas.
- **Jun–jul:** localmente.
- **Ago–set:** no GitHub Actions.
