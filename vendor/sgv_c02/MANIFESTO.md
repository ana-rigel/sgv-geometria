# Gerador oficial da C02, integrado byte a byte

Origem: `SGV_C02_GERADOR_PILOTO_20261014.zip`, enviado pela Ana em 15/10/2026, com SHA-256 `4691266c21d313b3522577a5dfc6390c7dc654b8ee648ba8524a95bc50ebcd7a`, igual ao registrado em `reports/C02_GERADOR_SANIDADE_20261014.md` e na emenda C02.1.

Arquivos copiados sem alteração (SHA-256):

| Arquivo | SHA-256 |
|---|---|
| `README.md` | `862aff1c844b4ffc22bf62940a35bb3a8401795be94a38b3fe6379de44c834d4` |
| `experiments/c02_generators.py` | `8d98fd9022192df2b4bd65e5bd8912aab6acadf083d503c06afef1eed2491ead` |
| `tests/test_c02_generators.py` | `c821cda534d28d4f2831bc34fdef55b4a9d68df572be1a8e16df68a202c31f2f` |

Os 7 testes originais passam (`cd vendor/sgv_c02 && PYTHONPATH=. python -m pytest -q tests/test_c02_generators.py`). O executor do portão carrega `c02_generators.py` pelo caminho do arquivo (`importlib`), porque a pasta `experiments/` do pacote colidiria com a do repositório; nada é renomeado.
