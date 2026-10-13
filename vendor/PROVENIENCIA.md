# Proveniência do código em vendor/

Cópias fiéis, sem nenhuma alteração, para o pacote rodar sozinho.

| Pasta | Origem | Versão |
|---|---|---|
| `m11i/sgv_m11i/` | pacote SGV_M11I_Instrumento enviado por Ana (zip "SGV_M11I_Instrumento_Windows_Linux") | `instrument.py` como recebido em 13/10/2026 |
| `sgv_original/sgv/` | repositório `ana-rigel/sgv_original` | commit ac6b986 (construtor do input, arquivo 0) |

Do M11-I o pipeline usa `flow_coordinates`, `gaussianize`, `build_shell`, `curvature_d`,
`signature` e `grid_points`. Do sgv_original usa `sgv.common.kde.kde_eval` e
`sgv.common.geometry` (`project_psd`, `safe_inv`, `christoffel_hessian`) e, no espaço original,
`sgv.input_builder.build_btc_90d_input_sgv` (E_norm e jerk do input).
