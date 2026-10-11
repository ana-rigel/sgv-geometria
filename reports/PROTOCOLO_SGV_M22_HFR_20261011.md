# SGV-M22 (H-FR) — Eventos estruturais aparecem como mudança de acoplamento? (pré-registro antecipado)

STATUS: CONGELADO (regras) — 11/10/2026, antes da existência dos dados. A lista de eventos será montada **depois** do fim do período, pelo procedimento abaixo, e anexada sem alterar nenhuma outra regra.

**Origem:** M19 (descritivo, não testado): alarme da régua Fisher–Rao em 4/15 janelas de evento contra 1/43 nas demais (1m, ago–set/2026). Pela regra do programa, um achado descritivo só vira conclusão em dado virgem.

## Hipótese
**H-FR:** no 1m, janelas que contêm um evento estrutural externo têm alarme da **régua Fisher–Rao** (covariância entre retorno, agressão e volume) com frequência maior que as demais janelas.

## Dados (virgens hoje)
BTCUSDT spot 1m, **01/10/2026 00:00 UTC → 31/12/2026**: 92 dias → **88 janelas** disjuntas de 1500 min a partir do primeiro minuto do período. Os arquivos mensais saem na Binance no início do mês seguinte; a execução só ocorre depois que out, nov e dez/2026 estiverem publicados (previsão: começo de janeiro de 2027). Prefixo da primeira janela: últimos 5000 min de setembro (já gastos para H-RUP, usados só como prefixo).

## Medição (igual ao M19, com o posto conservador do M21a)
Nulo de blocos circulares de 500 linhas reais do prefixo (BL), 39 referências, réguas M11 / Fisher–Rao / energy nas metades gaussianizadas, posto conservador, alarme p ≤ 0,05.

## Eventos (procedimento fixado agora)
- Montados **após 31/12/2026**, a partir de **notícias e calendários oficiais**, sem consultar gráficos ou séries de preço do período; por Claude por delegação ou pela Ana. As fontes ficam registradas evento a evento.
- **Categorias:** (1) falha, ataque ou insolvência de corretora, stablecoin ou protocolo relevante; (2) decisão regulatória ou judicial relevante; (3) política monetária ou dado macro agendado de grande impacto (FOMC, CPI, emprego dos EUA, discursos agendados do presidente do Fed); (4) anúncio institucional estrutural.
- **Agendados (categoria 3)** são incluídos **todos**, pelo calendário oficial, independentemente de terem "mexido" no mercado — isso elimina escolha.
- Excluído: qualquer evento definido pelo próprio movimento de preço; evento sem data identificável.
- Mapeamento: com hora → a janela que contém o minuto; só com data → todas as janelas que tocam o dia UTC.

## Testes
- **Primário:** diferença entre a taxa de alarme **Fisher–Rao** em janelas de evento e nas demais, p unilateral por **deslocamentos circulares** do indicador de evento; **α = 0,05**.
- **Secundários (descritivos):** só eventos agendados; só não agendados; Fisher exato; permutação estratificada por volatilidade; mesma análise para energy e M11; alarme forte (≥2 réguas).
- **Decisão:** p primário < 0,05 → H-FR apoiada; caso contrário, não apoiada, sem reteste nos mesmos dados.

## Poder (declarado)
Com ~88 janelas e ~20–25 janelas de evento (os agendados sozinhos dão ~10–12), um efeito do tamanho do observado no M19 (27% vs 2%) seria detectado com folga; um efeito de 15% vs 5% ficaria perto do limite.

## Apostas de Claude (registradas hoje)
| Item | Aposta |
|---|---|
| P(H-FR apoiada) | ≈ 30% |
| Taxa Fisher–Rao nas janelas sem evento | 3–10% |
| Se apoiada, o efeito aparece mais nos não agendados do que nos agendados | ≈ 60% |
