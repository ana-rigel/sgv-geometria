# SGV RTT ↔ M11-I — H-J e H-GEO, ponte de engenharia

**Estado:** código e testes sintéticos versionados; resultados BTC descritos a seguir
vieram de execução **local** com o pacote `navegador_sgv (2).zip` do usuário.
Não é um pré-registro, não é confirmação, não foram vistos dados reservados.

## Problema

A propagação da ocupação `pi @ P^H` fica perto de `pi`; além disso
janelas 1500 com saltos de 240 minutos sobrepõem 84%. Isso torna trivial
prever superfícies aparentemente semelhantes. **Solução**: janelas A e B
totalmente disjuntas de 1500 pontos e dois endpoints distintos.

### H-J: estrutura direcional das transições

A RTT é treinada apenas no bloco A (últimos 1440 estados). Comparar
log probabilidade por transição durante **todo o bloco B futuro**:

- `P` : matriz original de 20 nós;
- `P_rev=(P+diag(pi)^-1 P^T diag(pi))/2` : reversibilizada com **exatamente a mesma pi**;
- `P_shuffle` : treinamento nos mesmos nós A em ordem embaralhada;
- `P_iid`: transições independentes com linhas pi.

O endpoint primário candidato a eventual pré-registro é
`mean_logscore(P)−mean_logscore(P_rev)` com comparação temporal robusta,
mas **não foi pré-registrado nem submetido a teste confirmatório**.

### H-GEO: capacidade de prever a assinatura das superfícies

Para prever a ocupação do bloco futuro, calcular

```
p_future_block = (1/H) * sum_{k=1}^H delta(node_A_end) @ P^k
```

*Não* usar só `delta P^H`. Para converter pesos dos 20 nós em amostra
tridimensional, reamostrar apenas pontos de A condicionados ao nó.
Gerar GMM2/HDR50 M11-I para `Bhat`. Comparar as cinco componentes de
`G(A→Bhat)` com `G(A→B)`, usando as mesmas regras de reconstrução
e as mesmas sementes entre métodos. O baseline **persistência** prevê
`Bhat=A`, assinatura exatamente zero.

Perdas de diagnóstico: erro Euclidiano do vetor de centro, módulo do
erro log-volume, erro de ângulo orientacional, módulo do erro residual
M11, módulo do erro ΔD. Escalas de engenharia fixadas `[1,1,180,1,1]`
e perda média de quadrados disponível. Não é uma loss confirmatória
validada estatisticamente.

### Origem dos dados e segurança

Somente BTCUSDT spot 1m de maio a julho de 2026, fornecido e já
explorado. Mai calibra âncora de normal scores e codebook 20 nós.
O script rejeita arquivos com SHA divergente e não lê outros meses,
nem baixa dados. São janelas disjuntas no período jun/jul de 2026.

## Resultados executados (ambiente local do pacote enviado)

**H-J sintético, cadeia de 6 nós** (um dos testes identifica giro conhecido):
- giro horário: ganho da RTT vs reversível **+0,43155** nats/transição;
- giro anti-horário: **+0,43313**;
- cadeia reversível: aproximadamente **0**.

**H-J BTC 30 blocos disjuntos** de 1500 minutos, 01/06 a 02/07:
- média RTT **−2,93887** nats/transição;
- média reversível **−2,86144**;
- média IID **−2,92846**;
- diferença pareada RTT−reversível **−0,07742**;
- RTT vence reversível em **0/30** blocos.

**H-GEO BTC 3 blocos disjuntos** (perdas diagnósticas menores são melhores):
- persistência **0,065000**;
- RTT **0,061827**;
- reversível **0,061745**;
- shuffled-training **0,061748**;
- IID **0,061839**.

As melhorias numéricas pequenas da RTT contra a casca persistente
**não** superam o controle reversibilizado. A proximidade entre
reversível e RTT é justamente uma evidência de que prever a ocupação
futura não demonstra o efeito da corrente.

**Interpretação:** H-J desfavorável exploratoriamente; H-GEO empatada
com os melhores controles neste piloto; sem evidência confirmatória de
vantagem. Não otimizar métricas, número de nós ou horizonte nos mesmos
blocos ex-post.

## Reproduzir no repositório GitHub

```bash
git switch research/ponte-rtt-m11i-hj-hgeo
python -m pip install -r requirements_m11i.txt
python -m pytest -q tests/test_rtt_m11i_bridge.py
python scripts/run_rtt_m11i_bridge.py --mode synthetic --output reports/rtt_bridge_synthetic.json
# Real somente com dados MAI-JUL usados e SHA256SUMS fornecidos:
python scripts/run_rtt_m11i_bridge.py --mode btc-exploratory \
  --btc-dir /caminho/para/navegador_sgv/dados \
  --n-hj 30 --n-geo 3 --output reports/rtt_bridge_btc_exploratory.json
```

**Observação de proveniência:** os números BTC deste relatório são os da
implementação local que reutilizou o `sgv_m11i.instrument` incluído no
ZIP do usuário. A implementação GitHub usa os módulos históricos
`sgvgeo.flow` e `sgv_m11i.integrated`; pequenas diferenças numéricas
podem surgir e devem ser reportadas como replicação, não ocultadas.

Para a versão Windows/Linux autocontida que roda diretamente no
navegador original, usar o ZIP entregue na conversa:
`SGV_Ponte_RTT_M11I_HJ_HGEO_20261013.zip`.
