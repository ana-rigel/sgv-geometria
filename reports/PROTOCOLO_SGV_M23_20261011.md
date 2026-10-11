# SGV-M23 — Um modelo mínimo explícito do BTC 1m (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m23-modelo-minimo` (a partir de `research/m21b-dependencia-btc`). **`main` intocada. Só dados exploratórios** (1m mai–jul/2026, as mesmas 84 origens).
**Nota de ritmo:** é o 3º experimento do dia, acima da regra de "um ou dois por dia" do documento de referência; feito a pedido explícito da Ana ("Teste amigo").
**Pergunta sobre o BTC:** um modelo explícito — regimes de duas escalas + autorregressão vetorial + volatilidade condicional — reproduz o funcionamento do BTC no 1m tão bem quanto os blocos reais de 8 h (BL)? Se sim, temos uma **descrição explícita** do funcionamento, não só um nulo empírico.
**Antes deste documento:** testes unitários (o GARCH recupera parâmetros conhecidos; o modelo reproduz autocorrelação e memória de volatilidade em dados sintéticos) e o ajuste numa origem com semente de desenvolvimento (engenharia). Nenhum posto do M23 foi visto.

## Modelos (ajustados só no prefixo de cada origem)
- **`MSAR`** — regime lento de 2 estados (como no M17/M18, decodificado da média móvel causal de ν) com transição markoviana; **dentro de cada regime, VAR(1) trivariado** (intercepto + matriz 3×3, raio espectral limitado a 0,99) estimado só com pares consecutivos do mesmo regime; inovações branqueadas pela covariância do regime, com **GARCH(1,1) por coordenada** (variância incondicional 1, quase-verossimilhança).
- **`MSARLM`** — igual, com o **bloco lento real** do M18 (sequência de regimes e parte lenta contínua de ν do prefixo). **Modelo principal.**
- Referências pareadas: **`MSDCCLM`** (melhor paramétrico do M18/M21b) e **`BL`** (blocos reais de 500 barras).

## Medição
12 estatísticas por janela: as três réguas (M11, Fisher–Rao, energy, como no M15) e as 9 de dependência do M21b (lin/vol/HSIC nos lags 1, 5, 30). 39 referências, posto conservador (M21a), alarme p ≤ 0,05.

## Critérios pré-registrados
1. **Primário (a peça faltante funciona?):** MSARLM alarma **menos** que MSDCCLM em `lin_1`, `vol_1` e `hsic_1` (McNemar exato pareado, unilateral, α = 0,05/3 cada).
2. **Veredito de adequação do MSARLM:**
   - **"Adequação plena"** se nenhuma das 12 estatísticas fica elevada (limite inferior de Wilson ≤ 7%);
   - senão, **"equivalente ao BL"** se em nenhuma das 12 o MSARLM alarma significativamente mais que o BL (McNemar unilateral, α = 0,05/12);
   - senão, **"não fecha a lacuna"** — e as estatísticas em que ele perde para o BL dizem o que ainda falta.
3. **Descritivo:** MSAR × MSARLM (papel da memória longa real), parâmetros GARCH e raio espectral do VAR.

## Ressalvas
Origens consecutivas não são independentes. O BL é levemente liberal (~10–15%) nas estatísticas de dependência (M21b), então "equivalente ao BL" não significa "calibrado". As emissões continuam gaussianas condicionalmente: caudas e forma conjunta não gaussiana podem continuar faltando (o M11 dirá).

## Apostas de Claude (antes de qualquer resultado)
| Item | Aposta |
|---|---|
| Primário: melhora significativa em `lin_1`, `vol_1` e `hsic_1` (as três) | ≈ 75% |
| `lin_1` do MSARLM | 10–25% (vs 74% do MSDCCLM) |
| `vol_1` do MSARLM | 15–40% (vs 88%) |
| Veredito "adequação plena" | ≈ 7% |
| Veredito "equivalente ao BL" | ≈ 25% |
| Se não fechar, a régua em que mais perde para o BL | M11/forma (≈ 45%), energy (≈ 30%), dependência de lag longo (≈ 25%) |
