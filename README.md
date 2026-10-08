# sgv-geometria

Projeto próprio para testar a camada de **geometria informacional** do SGV: o pipeline de campo "90d" (9 camadas) e o `run_sgv_runtime`, que o sistema usa ao vivo sobre uma janela de 220 barras.

A pergunta é se a geometria da distribuição de estados do mercado tem informação própria sobre o que vem depois, além da volatilidade e da simples posição do estado. O objeto do teste é a métrica de informação sobre as coordenadas do SGV (E = v²+a², jerk, memory_flux) e sua curvatura. Antes de responder, é preciso que essa geometria seja calculável, causal e mensurável. A Fase 0 cuida disso.

**Estado (08/10/2026):** Fase 0 concluída, com núcleo exato, testes, diagnóstico de calibração e revisão independente. A grandeza candidata é ΔF: a curvatura da métrica de Fisher local além da referência gaussiana. A Fase 1 (dados reais) aguarda os klines. Leia primeiro:

- [`reports/DIAGNOSTICO.md`](reports/DIAGNOSTICO.md): o que o legado calcula de fato e o que a calibração decidiu.
- [`PLANO.md`](PLANO.md): fases, portões e decisões abertas.

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `legacy/` | Os 10 arquivos originais, byte a byte (proveniência e hashes em `legacy/PROVENIENCIA.md`), e o único dado real do legado (132 barras de 31/03/2026). **Não editar.** |
| `sgvgeo/` | Núcleo novo. `data` (sintéticos, substitutos, leitor de klines), `features` (coordenadas e escalas causais), `kde` (derivadas analíticas), `geometry` (métricas H, F e referência gaussiana; Christoffel, Riemann, Ricci, R, Einstein), `field` (campo causal no tempo), `legacy` (executa o legado sem alterá-lo) |
| `tests/` | Casos de resposta conhecida: espaço plano (R = 0), esferas S² e S³ (R = 2 e 6), derivadas do KDE, identidade da informação, referência gaussiana |
| `diagnostics/` | D1–D8 e figuras; `run_all.py` roda tudo |
| `reports/` | Relatório e saídas de cada rodada (`sintetico/`, `real/`) |
| `data/` | Klines (fora do git) |

## Como rodar

```bash
pip install numpy pandas scipy scikit-learn matplotlib pytest
python -m pytest -q                       # 11 testes
python diagnostics/run_all.py             # calibração sintética (~35 min)
SGV_DATA=data/BTCUSDT-1m-2026-06.zip SGV_TAIL=6000 python diagnostics/run_all.py   # dados reais
python diagnostics/run_all.py d7_confiabilidade figuras   # só alguns passos
```

## Diagnósticos

| | Pergunta |
| --- | --- |
| D1 | O que cada coluna do legado carrega (variação, saturação, duplicatas) |
| D2 | A curvatura da malha do legado converge para a exata? |
| D3 | Alguma camada usa o futuro? O ao vivo repinta o passado? |
| D4 | Como é a geometria exata e causal (assinatura, curvatura) com as métricas H, F e a referência gaussiana |
| D5 | Quanto da geometria é volatilidade |
| D6 | O campo obedece a uma equação G = κT? |
| D7 | A curvatura é mensurável (confiabilidade entre metades da janela)? |
| D8 | A geometria da série difere da de substitutos (GARCH ajustado, IAAFT, embaralhado)? |

Nenhum diagnóstico usa retorno futuro.
