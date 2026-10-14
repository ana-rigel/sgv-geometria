# E-FLX-02 — o fluxo de segundos como filtro de operações mais longas

**Registrado em 13/10/2026, antes do código.** Exploração em jun–jul/2026, nos mesmos 10 dias de `aggTrades` do E-FLX-01 (BTCUSDT spot), executada no GitHub Actions. Testa duas regras propostas como filtro: (R1) só entrar em rompimento se o fluxo dos segundos anteriores estiver a favor; (R3) abortar a operação se, em 15–30 s, o preço não andar a favor e o desequilíbrio sumir.

## Construção comum

- Grade de 1 s: preço = último negócio até o segundo; fluxo F_k = volume assinado dos últimos k s (k = 1, 5, 15), normalizado pelo volume total da mesma janela (fica em [−1, 1]).
- Execução com latência de 250 ms: preço de entrada = primeiro negócio a partir de t + 250 ms.
- Custo: 20 bp por ida e volta (taker 0,10 % por lado). Bootstrap por dia (10 dias, 5.000 reamostras) para os intervalos.
- Ficam de fora os primeiros e os últimos 60 min de cada dia (horizontes e janelas de referência não atravessam o arquivo diário).

## R1 — rompimento com e sem fluxo a favor

- **Evento:** primeiro segundo em que o preço supera a máxima (ou fica abaixo da mínima) dos últimos L min, L ∈ {15, 60}; depois de um evento, o mesmo lado só vale de novo após 5 min. Direção = lado do rompimento.
- **Fluxo a favor:** F₅ no sentido do rompimento > 0 (e, como secundário, tercil superior contra inferior).
- **Desfechos:** retorno no sentido do rompimento a partir da entrada, em h ∈ {5 s, 60 s, 5 min, 15 min, 60 min}; "rompimento falso" = preço de volta além do nível rompido em 5 min.
- **Apostas:** a 5 s, fluxo a favor > contra (o E-FLX-01 já mostra isso); a partir de 60 s, |Δ retorno médio (a favor − contra)| < 1 bp com IC contendo 0; diferença na taxa de rompimento falso < 5 pontos percentuais; retorno líquido de 20 bp negativo nos dois grupos em todos os horizontes.

## R3 — abortar se não andar em τ segundos

- **Entradas:** 300 instantes aleatórios por dia (semente fixa), também repetido sobre os eventos de R1 (L = 60).
- **Estratégia com vantagem plantada:** o lado da entrada acerta o sinal do retorno até o horizonte H com probabilidade q ∈ {0,50; 0,60; 0,75}; H ∈ {15, 60 min}. Duas variantes:
  - V1, vantagem sobre r(t → H): realista, uma tese certa também tende a andar um pouco a favor no começo;
  - V2, vantagem só sobre r(t + τ → H): a tese não tem relação com os primeiros segundos.
- **Regra de aborto:** em t + τ (τ ∈ {15, 30 s}), sai se o retorno desde a entrada for ≤ 0 **e** F₅ no sentido da operação for ≤ 0. Quem não aborta segura até H. As duas versões pagam 20 bp por operação.
- **Medidas:** fração abortada; ρ de Spearman entre a condição de aborto e o retorno de t + τ até H (a pergunta-chave: a condição prevê o resto da operação?); retorno líquido médio por operação, segurar contra abortar.
- **Apostas:** a condição de aborto não prevê o retorno de τ até H (|ρ| < 0,02); com q = 0,50, abortar ≈ segurar (|Δ| < 1 bp); com vantagem (q = 0,60 e 0,75), abortar **perde** cerca de 40 % da vantagem plantada na V2, e menos na V1, mas perde nas duas; nenhuma combinação de abortar supera segurar em mais de 1 bp.
