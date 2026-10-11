# SGV-M21b — Dependência temporal entre instantes no BTC exploratório (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m21b-dependencia-btc` (a partir de `research/m21-m11-robusto`). **`main` intocada. Só dados exploratórios** (1m mai–jul/2026, as mesmas 84 origens do M16–M18).
**Pergunta sobre o BTC (regra 2 do documento de referência):** o mercado tem dependência entre x_t e x_{t+k} que o melhor modelo paramétrico do M18 não reproduz? Se tiver, é linear, de memória de volatilidade, ou não linear além delas (o tipo estudado no M20)? Isso decide se a linha M20 importa para o mercado.
**Antes deste documento:** testes unitários e a medição do tempo de uma origem com semente de desenvolvimento (só engenharia). Nenhum posto do M21b foi visto.

## Medição (congelada)
Em cada janela de 1500 barras, as três coordenadas viram escores normais **por postos dentro da própria janela** (nível de cópula: remove a forma das marginais). Para k ∈ {1, 5, 30}:
- `lin_k`: norma de Frobenius da covariância cruzada defasada 3×3 (linear);
- `vol_k`: o mesmo sobre |x| centrado (memória de volatilidade);
- `hsic_k`: HSIC com kernel gaussiano entre x_t e x_{t+k} em ℝ³, banda pela mediana (qualquer dependência, invariante a rotação).

## Nulos (ajustados só no prefixo de cada origem; 39 referências; posto conservador do M21a; alarme p ≤ 0,05)
- `MS` — duas escalas, Markov (M17/M18);
- `MSDCCLM` — duas escalas + DCC + memória longa real (o melhor paramétrico do M18) — **nulo principal**;
- `BL` — blocos reais de 500 barras: **controle de sanidade** (preserva por construção a dependência de curto alcance; deve dar ~nominal).

## Contrastes (McNemar exato pareado, unilateral, α = 0,05/3 por defasagem)
- **P1:** HSIC sob MSDCCLM alarma mais que sob BL?
- **P2a / P2b:** sob MSDCCLM, HSIC alarma mais que `vol` / que `lin`?

## Veredito por defasagem (pré-acordado)
"Elevado" = limite inferior de Wilson acima de 7%.
1. HSIC sob MSDCCLM **não** elevado → **sem dependência que o modelo não reproduza** → a linha M20 não tem objeto no BTC (nesta escala).
2. HSIC elevado, `vol` e `lin` **não** elevados, P2a e P2b significativos → **dependência não linear além da 2ª ordem e da volatilidade (tipo M20)** → a linha M20 tem objeto no BTC.
3. HSIC elevado com `vol` elevado → **compatível com memória de volatilidade** mal modelada.
4. Outro padrão → tipo indefinido.
Sanidade: BL com HSIC não elevado; se falhar, o veredito daquela defasagem fica suspenso.

## Ressalvas
Origens consecutivas não são independentes (Wilson otimista). Escala de 1m e coordenadas normalizadas localmente. Emissões gaussianas por estado nos nulos paramétricos podem gerar alarmes de dependência por forma conjunta errada; a leitura separa isso pelo padrão `lin`/`vol`/`hsic`.

## Apostas de Claude (antes de qualquer resultado)
| Item | Aposta |
|---|---|
| HSIC_1 elevado sob MSDCCLM | ≈ 60% |
| Algum lag com veredito "tipo M20" | ≈ 15% |
| Algum lag com veredito "memória de volatilidade" | ≈ 45% |
| BL passa na sanidade nos 3 lags | ≈ 85% |
