# SGV-M27 — Não estacionariedade dos parâmetros (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m27-nao-estacionariedade` (a partir de `research/m26-resiliencia-cruzada`). **`main` intocada. Só dados exploratórios** (as mesmas 84 origens do 1m, mai–jul/2026).
**Nota de ritmo:** 7º experimento do dia, a pedido da Ana ("Continue"), contra a regra de 1–2 por dia (registrado).
**Antes deste documento:** nada do M27 foi programado nem rodado. Mudanças após este commit só de engenharia, registradas.

## Pergunta sobre o BTC
Depois do M26, o modelo explícito (HARLMFX) ainda alarma 17–31% em volatilidade e dependência não linear nas defasagens de 5–30 min, contra ~7–14% dos blocos reais (BL). Hipótese: **o funcionamento muda ao longo do dia** — os parâmetros (persistência, resiliência, volatilidade) de umas horas não são os de outras. O BL herda isso de graça (cada bloco de 500 min carrega a dinâmica do seu trecho); o HARLMFX usa um único conjunto de parâmetros para os ~3,5 dias do prefixo.

## Modelos (nulos)
O prefixo (5000 min) passa pela mesma camada lenta do M23–M26 (regimes lentos + bloco lento real do volume). O restante é dividido em **K = 6 trechos contíguos** (~13–14 h cada).
- **`HXLOC` (principal):** em cada trecho, o modelo do M26 com **parâmetros locais** — HAR 1/15/60 na média (um regime por trecho), variância cruzada do M26, inovações reais filtradas **do próprio trecho**. Simulação **em blocos de 500 min, como o BL**: cada bloco sorteia um trecho e uma posição inicial dentro dele, aquece 300 passos com os parâmetros desse trecho e soma o bloco lento real da mesma posição.
- **`HXNOISE` (controle de ruído de estimação):** idêntico ao HXLOC, mas os parâmetros locais são estimados num prefixo **sintético** gerado pelo HARLMFX global (estacionário por construção), passando pelo mesmo pipeline (camada lenta, 6 trechos, ajustes locais, blocos). Ele tem a mesma dispersão de parâmetros que vem só do ruído de estimar em ~800 linhas — sem mudança real de funcionamento. Serve para separar "parâmetros que mudam de verdade" de "referências mais largas porque as estimativas são ruidosas".
- **`HARLMFX`** (M26, parâmetros globais) e **`BL`** (blocos reais de 500) como referências pareadas.

Mesmas 12 estatísticas do M23–M26, 39 referências, posto conservador, alarme p ≤ 0,05.

## Critérios pré-registrados
Estatísticas-alvo: `vol_5`, `vol_30`, `hsic_5`, `hsic_30` (McNemar exato pareado, unilateral, α = 0,05/4 cada).
1. **Primário A (parâmetros locais ajudam):** HXLOC alarma menos que HARLMFX.
2. **Primário B (não é ruído de estimação):** HXLOC alarma menos que HXNOISE.
3. **Leitura:** **não estacionariedade apoiada** se A e B forem significativos **na mesma estatística**. A sem B → o ganho vem de referências mais largas (ruído), não de mudança real. Sem A → não apoiada.
4. **Veredito do HXLOC** contra o BL, como no M25/M26: "adequação plena" (nenhuma das 12 com Wilson inferior > 7%) / "equivalente ao BL" (nenhuma significativamente pior, α = 0,05/12) / "não fecha a lacuna".
5. **Descritivo (sem teste confirmatório):** dispersão dos parâmetros locais entre trechos — persistência da variância de retorno e volume, termo de resiliência agressão←retorno, persistência HAR do volume — no real contra no sintético (mediana entre origens; fração de origens com real > sintético).

## Ressalvas
- 6 trechos e blocos de 500 são escolhas fixadas aqui, não otimizadas. Trechos de ~13 h são mais longos que os blocos do BL (~8 h); um resultado nulo não exclui mudança em escalas mais curtas.
- Ajustar ~50 parâmetros em ~800 linhas é ruidoso — por isso o HXNOISE.
- Dados exploratórios já usados em M16–M26: qualquer resultado vira hipótese para dado virgem.

## Apostas de Claude (antes de qualquer código)
| Item | Aposta |
|---|---|
| Primário A significativo em ≥ 1 das 4 | ≈ 55% |
| Primário B significativo em ≥ 1 das 4 | ≈ 30% |
| Não estacionariedade apoiada (A e B na mesma estatística) | ≈ 25% |
| HXNOISE alarma menos que HARLMFX em ≥ 1 das 4 (o ruído sozinho já "ajuda") | ≈ 45% |
| Veredito "equivalente ao BL" | ≈ 20% |
| Veredito "adequação plena" | ≈ 5% |
| Dispersão real > sintética na persistência da variância (maioria das origens) | ≈ 65% |
