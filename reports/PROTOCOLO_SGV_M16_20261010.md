# SGV-M16 — As três réguas sobre os nulos N0–N3 no BTC exploratório (pré-registro)

**Data:** 10/10/2026. **Ramo:** `research/m16-trio-btc-exploratorio` (a partir de `research/m15-forma-persistencia-comparadores@ba9540d`). **`main` intocada.**
**Dados:** somente exploratórios, conferidos por `checked_exploratory_month` e SHA-256 — BTCUSDT spot **1m mai–jul/2026** e **1h jan/2020–dez/2024**. Nenhum mês reservado (1m ≥ ago/2026; 1h ≥ jan/2025) é baixado ou lido.
**Autoria:** desenho de Claude a pedido da Ana, depois do M15.
**Este documento é commitado antes do código que roda o experimento.** Antes dele, só foram feitos: contagem de origens elegíveis (84 no 1m, 18 no 1h), medição de tempo de um sorteio por nulo e um piloto de engenharia com 2 referências na primeira origem de cada intervalo, sem leitura de postos.

## Pergunta

Os nulos temporais do M12, ajustados no passado de cada origem, reproduzem as deformações das cascas do BTC? E, quando não reproduzem, **qual tipo de mecanismo falta** — forma da distribuição conjunta ou memória/migração de massa —, segundo a assinatura das três réguas estabelecida no M15 (erro de forma: M11 ≫ energy; erro de persistência: energy ≫ M11)?

## Desenho (congelado)

- **Origens:** **todas** as origens contíguas elegíveis, sem seleção — prefixo 5000 (1m) / 3500 (1h), janela 1500 / 1008, passo de uma janela (mesma regra do M12/M13). Contagem travada: 84 (1m), 18 (1h); se o download produzir outro número, o experimento falha fechado.
- **Nulos:** N0 (blocos estacionários curtos), N1 (GARCH-t + SF1-M5: memória de volume e calendário), N2 (regime-relógio, blocos curtos), N3 (regime-relógio, blocos longos) — **código do M12 inalterado**, ajustado só no prefixo.
- **Referências:** **39 por nulo** por origem (postos 1–40). **Alarme:** `p_rank=(1+#(ref≥obs))/40 ≤ 0,05` (observado acima de ≥38 das 39), nível nominal 5% — o mesmo α calibrado no M14/M15.
- **Réguas:** `m11` (cascas HDR50, inalterada), `fr_cov` (Fisher–Rao entre covariâncias das metades), `energy` (energy distance entre metades) — exatamente `all_stats` do M15, nas mesmas metades gaussianizadas.
- **Execução:** GitHub Actions — testes + plano + piloto → 21 shards (1m, 4 origens) + 6 shards (1h, 3 origens) → agregação que falha fechada → commit automático.

## Classificação pré-registrada (por intervalo × nulo)

McNemar exato pareado entre os alarmes de `m11` e `energy`, **bilateral com α = 0,05/8 = 0,00625** (4 nulos × 2 intervalos):
1. `m11 > energy` significativo → **"falta forma"**;
2. `energy > m11` significativo → **"falta memória/massa"**;
3. senão, se alguma régua tem limite inferior de Wilson acima de **7%** (nível empírico de uma família correta ajustada, M14/M15) → **"inadequado, tipo indefinido"**;
4. senão → **"sem evidência de inadequação nas três réguas"**.

`fr_cov`, histogramas de postos (8 faixas), PIT médio e a linha do tempo dos alarmes são **descritivos**. A linha do tempo será lida contra eventos conhecidos do período (mar/2020, mai/2021, nov/2022 no 1h) **só como exploração**, sem teste.

## Ressalvas declaradas antes

- Origens consecutivas compartilham regimes; **os alarmes não são independentes** e os intervalos de Wilson são otimistas. A classificação é descritiva-forte, não confirmatória.
- O nível de 7% vem de geradores sintéticos (M14/M15); o nível real de cada nulo ajustado no BTC é desconhecido — justamente o que se audita.
- 18 origens no 1h dão pouco poder; ausência de classificação no 1h não é evidência de adequação.
- Uma classificação diz qual mecanismo **o nulo** não tem — não diz que o mercado está "em tensão", nem prevê preço.

## Apostas de Claude (antes de qualquer resultado)

| Item | Aposta |
|---|---|
| No 1m, todo nulo tem ≥1 régua com alarme > 20% | P ≈ 75% |
| N0 (blocos curtos) no 1m classificado **"falta memória/massa"** | P ≈ 45% |
| N1 (GARCH-t + SF1) no 1m classificado **"falta forma"** | P ≈ 45% |
| N3 (regime, blocos longos) com a menor taxa de alarme `energy` entre os 4 no 1m | P ≈ 50% |
| Algum nulo no 1m como "sem evidência de inadequação" | P ≈ 15% |
| Alguma classificação de tipo (1 ou 2) no 1h | P ≈ 30% |
| `fr_cov` com a menor taxa das três réguas na maioria das células | P ≈ 70% |
