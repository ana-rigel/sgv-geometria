"""Executa a camada original (pasta legacy/) sem modificar uma linha dela."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd

LEGACY_DIR = Path(__file__).resolve().parent.parent / "legacy"
if str(LEGACY_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_DIR))

warnings.filterwarnings("ignore")

from build_btc_90d_input_sgv_refactored import build_btc_90d_input_sgv  # noqa: E402
from sgv_build_information_field_geometry_90d_refactored import build_information_field_geometry_90d  # noqa: E402
from sgv_geodesic_field_full3d_90d_refactored import build_geodesic_field_full3d_90d  # noqa: E402
from sgv_build_singularity_detector_90d_refactored import build_singularity_detector_90d  # noqa: E402
from sgv_build_terrain_layer_90d_refactored import build_terrain_layer_90d  # noqa: E402
from sgv_build_expected_value_90d_refactored import build_expected_value_90d  # noqa: E402
from sgv_build_force_field_90d_refactored import build_force_field_90d  # noqa: E402
from sgv_force_alignment_90_refactored import build_force_alignment_90  # noqa: E402
from sgv_edge_signal_90_refactored import build_edge_signal_90  # noqa: E402
from sgv_runtime_live import run_sgv_runtime  # noqa: E402
import sgv_geodesic_field_full3d_90d_refactored as geodesic  # noqa: E402,F401


def run_offline_chain(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Encadeia as 9 camadas offline na ordem do legado.

    O `main()` de cada arquivo lê/grava CSVs em caminhos que não batem entre si
    (../data vs ../scripts) e o edge offline exige colunas que só existem juntando
    EV + alinhamento; aqui as funções são chamadas em memória, juntando EV ao
    alinhamento pela linha, que é o que o run_sgv_runtime faz."""
    out: dict[str, pd.DataFrame] = {}
    out["input"] = build_btc_90d_input_sgv(raw)
    out["info"] = build_information_field_geometry_90d(out["input"])
    out["geodesic"] = build_geodesic_field_full3d_90d(out["info"])
    out["singularity"] = build_singularity_detector_90d(out["geodesic"])
    out["terrain"] = build_terrain_layer_90d(out["input"])
    out["expected_value"] = build_expected_value_90d(out["terrain"])
    out["force_field"] = build_force_field_90d(out["terrain"])
    al = build_force_alignment_90(out["terrain"], out["force_field"])
    out["alignment"] = al[0] if isinstance(al, tuple) else al
    edge_in = out["alignment"].copy()
    edge_in["expected_value_score"] = out["expected_value"]["expected_value_score"].values
    out["edge"] = build_edge_signal_90(edge_in)
    return out


def run_live(raw: pd.DataFrame) -> pd.DataFrame:
    return run_sgv_runtime(raw)
