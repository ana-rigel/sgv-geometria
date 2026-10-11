# SGV-M24 — Fechar a lacuna: HAR + inovações históricas filtradas (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m24-har-fhs` (a partir de `research/m23-modelo-minimo`). **`main` intocada. Só dados exploratórios** (as mesmas 84 origens do 1m).
**Nota de ritmo:** 4º experimento do dia, a pedido explícito da Ana ("Feche a lacuna, esse será o último de hoje").
**Pergunta sobre o BTC:** as duas peças que o M23 mostrou faltar — a **escala intermediária de minutos** e a **forma não gaussiana** — fecham a lacuna entre um modelo explícito e os blocos reais de 8 h?
**Antes deste documento:** testes unitários e ajuste numa única origem (engenharia: raio da companheira ~0,97–0,99, sem encolhimento; simulação finita). Nenhum posto do M24 foi visto.

## Modelos (ajustados só no prefixo)
- **`HARLM`** — regimes lentos + bloco lento real (como MSARLM do M23), mas a autorregressão dentro de cada regime usa **três horizontes**: x_{t−1}, média de x nos últimos 15 min e média na última hora (HAR, Corsi 2009); companheira com raio < 0,995 (encolhimento se preciso); GARCH(1,1) por coordenada branqueada; inovações **gaussianas**.
- **`HARLMF`** — igual, mas as inovações são **vetores reais de resíduos padronizados do prefixo** (depois do filtro GARCH), sorteados com reposição — simulação histórica filtrada. **Modelo principal.**
- Referências pareadas: **`MSARLM`** (M23) e **`BL`** (blocos reais de 500 barras).

Mesmas 12 estatísticas do M23 (3 réguas + lin/vol/HSIC nos lags 1, 5, 30), 39 referências, posto conservador, alarme p ≤ 0,05.

## Critérios pré-registrados
1. **Primário:** HARLMF alarma **menos** que MSARLM em `lin_5`, `vol_5`, `hsic_5` e `m11` (McNemar exato pareado, unilateral, α = 0,05/4 cada).
2. **Veredito do HARLMF:** "adequação plena" (nenhuma das 12 com Wilson inferior > 7%) / senão "equivalente ao BL" (em nenhuma das 12 significativamente pior que o BL, α = 0,05/12) / senão "não fecha a lacuna".
3. **Descritivo:** HARLM × HARLMF (efeito das inovações reais, sobretudo no M11).

## Ressalvas
Origens consecutivas não são independentes; o BL é levemente liberal (~10–15%) nas estatísticas de dependência. As inovações reais vêm do mesmo prefixo usado no ajuste (como no BL); o bloco lento real continua sendo uma parte não modelada.

## Apostas de Claude (antes de qualquer resultado)
| Item | Aposta |
|---|---|
| Primário: melhora significativa em `lin_5`, `vol_5` e `hsic_5` | ≈ 70% |
| Primário: melhora significativa em `m11` | ≈ 40% |
| Veredito "equivalente ao BL" | ≈ 30% |
| Veredito "adequação plena" | ≈ 8% |
| `hsic_5` do HARLMF | 15–35% (vs 64% do MSARLM) |
