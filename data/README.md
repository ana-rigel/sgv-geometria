# Dados

Esta pasta fica fora do git (veja `.gitignore`). Coloque aqui os klines da Binance.

## Onde baixar

Arquivos mensais de spot em `https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/<intervalo>/`,
por exemplo `BTCUSDT-1m-2026-06.zip` ou `BTCUSDT-1h-2024-01.zip`. O `baixar_klines.py` que você já usa
serve; o leitor aceita os `.zip` direto, sem descompactar.

O leitor (`sgvgeo.data.load_binance_klines`) trata os dois formatos de tempo da Binance
(milissegundos até 2024, microssegundos nos dumps de spot a partir de 2025).

## Como rodar com dados reais

```bash
SGV_DATA=data/BTCUSDT-1m-2026-05.zip:data/BTCUSDT-1m-2026-06.zip SGV_TAIL=6000 \
  python diagnostics/run_all.py
```

Os resultados vão para `reports/real/`.

## Regra do período reservado

Os diagnósticos D1–D8 não olham retorno futuro, mas o período do teste confirmatório
não deve nem ser carregado antes do pré-registro. Os limites estão em `PLANO.md`.
