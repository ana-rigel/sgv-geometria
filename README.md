# sgv-geometria

Projeto próprio para testar a camada de **geometria informacional** do SGV: o pipeline de campo "90d" (9 camadas) e o `run_sgv_runtime`, que o sistema usa ao vivo sobre uma janela de 220 barras.

A pergunta é se a geometria da distribuição de estados do mercado tem informação própria sobre o que vem depois, além da volatilidade e da simples posição do estado. O objeto do teste é a métrica de informação sobre as coordenadas do SGV (E = v²+a², jerk, memory_flux) e sua curvatura. Antes de responder, é preciso que essa geometria seja calculável, causal e mensurável. A Fase 0 cuida disso.

**Estado (09/10/2026): linha encerrada pela regra pré-registrada.**

- Com as coordenadas do legado (preço), a curvatura candidata ΔF é mensurável, mas não se distingue de séries GARCH ajustadas.
- Com a única reformulação permitida (R1, fluxo de ordens: z, ι, ν), ΔF também não se distingue de um modelo de fatos estilizados ajustado (SF1), em 1m e em 1h.
- O código, os testes e a calibração ficam como ferramenta reutilizável.

Leia primeiro:

- [`reports/R1_PORTAO_G1.md`](reports/R1_PORTAO_G1.md): o julgamento da reformulação R1 (veredito final).
- [`reports/FASE1_PORTAO_G1.md`](reports/FASE1_PORTAO_G1.md): o julgamento do portão G1 em dado real.
- [`reports/DIAGNOSTICO.md`](reports/DIAGNOSTICO.md): o que o legado calcula de fato e o que a calibração decidiu.
- [`PLANO.md`](PLANO.md): fases, portões e decisões abertas.

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `legacy/` | Os 10 arquivos originais, byte a byte (proveniência e hashes em `legacy/PROVENIENCIA.md`), e o único dado real do legado (132 barras de 31/03/2026). **Não editar.** |
| `sgvgeo/` | Núcleo novo. `data` (sintéticos, substitutos, leitor de klines), `features` (coordenadas e escalas causais), `kde` (derivadas analíticas), `geometry` (métricas H, F e referência gaussiana; Christoffel, Riemann, Ricci, R, Einstein), `field` (campo causal no tempo), `legacy` (executa o legado sem alterá-lo) |
| `tests/` | Casos de resposta conhecida: espaço plano (R = 0), esferas S² e S³ (R = 2 e 6), derivadas do KDE, identidade da informação, referência gaussiana |
| `diagnostics/` | D1–D8 e figuras; `run_all.py` roda tudo |
| `reports/` | Relatórios e saídas de cada rodada (`sintetico/`, `real_1m/`, `real_1h/`, `r1_calib_*`, `r1_real_*`) |
| `scripts/` | `baixar_klines.py`: baixa os klines de exploração da Fase 1 |
| `data/` | Klines (fora do git) |

## Como rodar

```bash
pip install numpy pandas scipy scikit-learn matplotlib pytest
python -m pytest -q                       # 14 testes
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
