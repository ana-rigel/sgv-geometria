# SGV-M19 — Os alarmes do nulo adequado marcam rupturas estruturais? (protocolo confirmatório)

STATUS: RASCUNHO — aguardando a lista de eventos da Ana e o seu OK final. **Nenhum dado reservado foi baixado ou lido.**

**Ramo:** `research/m19-rupturas-estruturais`. **`main` intocada.**
**Escolha da Ana (10/10/2026):** testar no 1m, período reservado **agosto–setembro de 2026**.
**Origem da hipótese:** M16 (exploratório, 1h) — os poucos alarmes de forma coincidiram com Terra/LUNA, FTX e ETFs, observação feita *depois* dos dados. M18 forneceu o primeiro nulo adequado no 1m (blocos reais de ~8 h). M19a (exploratório) mostrou que os alarmes desse nulo **não** acompanham volatilidade, movimentos extremos nem volume.

## Hipótese

**H-RUP:** janelas de 1m que contêm um evento estrutural externo têm alarme forte do nulo de blocos longos com frequência maior do que as demais janelas.

## Dados e unidades (congelados)

- BTCUSDT spot 1m, **01/08/2026 00:00 UTC → 30/09/2026**: **58 janelas** disjuntas de 1500 min, a partir do primeiro minuto do período. Janelas com lacuna nos dados são registradas como lacuna e excluídas (não substituídas).
- Prefixo de cada janela: os 5000 min imediatamente anteriores (o da primeira janela vem do fim de julho, exploratório).
- Download **somente** por `scripts/m19_baixar_confirmatorio.py`, que recusa rodar se este arquivo não disser "STATUS: CONGELADO" e se o SHA-256 informado não bater. Execução no GitHub Actions apenas por disparo manual depois do OK da Ana.

## Medição (congelada; idêntica ao M18-BL)

- Nulo: blocos circulares de **500 linhas reais** do prefixo, **39 referências**.
- Réguas: M11 (forma), Fisher–Rao (covariância), energy (massa/memória), nas mesmas metades gaussianizadas.
- Alarme por régua: observado acima de ≥38 das 39. **Alarme forte = alarme em ≥2 réguas** (taxa de base exploratória: 6,0%).

## Eventos (a preencher pela Ana ANTES da abertura dos dados)

Arquivo: `reports/m19/eventos_ago_set_2026.json`, com data (UTC) ou data-hora (UTC), nome, categoria e fonte.
**Critério de inclusão:** acontecimento **externo ao preço**, de alcance estrutural para o mercado de cripto:
1. falha, ataque ou insolvência de corretora, emissora de stablecoin ou protocolo relevante;
2. decisão regulatória ou judicial relevante (EUA, UE, Ásia);
3. decisão de política monetária ou dado macro de grande impacto **agendado** (por exemplo, decisão do FOMC);
4. anúncio institucional estrutural (ETFs, reservas soberanas, grandes tesourarias corporativas).
**Excluído:** qualquer "evento" definido pelo próprio movimento de preço ("o BTC caiu 10%"), e qualquer coisa escolhida olhando gráficos do período.
**Mapeamento:** evento com hora → a janela que contém aquele minuto; evento só com data → todas as janelas que tocam aquele dia UTC.

## Testes (congelados)

- **Primário:** diferença entre a taxa de alarme forte nas janelas de evento e nas demais, com **p unilateral por deslocamentos circulares** do indicador de evento (preserva o agrupamento temporal das janelas). **α = 0,05.**
- **Secundários (descritivos):** Fisher exato unilateral; permutação estratificada por terço da razão de volatilidade (controle de volatilidade); mesma análise com alarme em ≥1 régua; taxas por régua.
- **Decisão:** p primário < 0,05 → H-RUP **apoiada** no confirmatório (1m, ago–set/2026). Caso contrário → H-RUP **não apoiada**; os meses ago–set/2026 do 1m ficam gastos para esta hipótese, sem reteste nem troca de régua ou de limiar depois de ver os dados.

## Poder (declarado)

Com ~58 janelas e algo como 6–10 janelas de evento, o teste só detecta efeitos grandes: por exemplo, alarme forte em ~40% das janelas de evento contra ~6% nas demais. Um resultado nulo **não** exclui efeitos moderados.

## Ensaio de engenharia (antes do congelamento)

O pipeline inteiro rodou em dados **exploratórios** (janelas a partir de 01/06/2026) com **eventos fictícios**, só para validar código, mapeamento e testes: `reports/m19/ensaio/`. Esse ensaio não tem valor científico.

## Apostas de Claude (registradas antes de qualquer dado reservado)

| Item | Aposta |
|---|---|
| Taxa de alarme forte nas janelas sem evento | 4–10% |
| P(H-RUP apoiada, p primário < 0,05) | ≈ 25% |
| Se apoiada, a régua mais frequente nas janelas de evento | energy (≈ 45%), M11 (≈ 35%), Fisher–Rao (≈ 20%) |

Raciocínio: a coincidência do M16 foi vista depois dos dados, em 18 janelas e noutra escala; no 1m o período tem só ~58 janelas, e eventos estruturais em dois meses podem ser poucos ou fracos. Uma confirmação seria forte; uma não confirmação seria o resultado mais provável e ainda informativo.

## Para congelar

1. A Ana envia a lista de eventos de agosto–setembro de 2026 seguindo o critério acima.
2. Claude grava `eventos_ago_set_2026.json`, troca o STATUS para CONGELADO, faz commit e informa o SHA-256.
3. A Ana dá o OK final → disparo manual da execução confirmatória.
