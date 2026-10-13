"""Pipeline completo da camada geométrica.

Ordem (a mesma dos scripts originais):

    input ─┬─► info_local
           ├─► info ─► geodesic ─► singularity
           └─► terrain ─┬─► force_field
                        ├─► alignment ─┐
                        └─► expected_value ─┴─► edge

Uso:
    python -m sgv.pipeline --input btc_90d_input_sgv.csv --out-dir saida/
    python -m sgv.pipeline --raw btc_90d_1m_raw.csv --out-dir saida/       # monta o input antes
    python -m sgv.pipeline --input ... --out-dir ... --legacy          # reproduz os originais
    python -m sgv.pipeline --input ... --out-dir ... --set causal.W_FIT=20160 --set legacy.LEGACY_NAN_COS=true
    python -m sgv.pipeline --input ... --out-dir ... --steps terrain,alignment,expected_value,edge
    python -m sgv.pipeline --input ... --out-dir ... --live-fill        # C7: zero-fill único no final
"""
from __future__ import annotations

import argparse
import dataclasses
import logging
import time
from pathlib import Path

import pandas as pd

from . import (edge_signal, expected_value, force_alignment, force_field, geodesic_field, information_field,
               information_field_local, input_builder, singularity, terrain)
from .common.validity import finalize_for_live, write_outputs
from .config import SGVConfig

log = logging.getLogger("sgv.pipeline")

OUTPUT_NAMES = {
    "input": "btc_90d_input_sgv.csv",
    "info_local": "sgv_information_field_local_90d.csv",
    "info": "sgv_information_field_geometry_90d.csv",
    "geodesic": "sgv_geodesic_field_full_90d.csv",
    "singularity": "sgv_singularity_field_90d.csv",
    "terrain": "sgv_terrain_layer_v1_90d.csv",
    "force_field": "sgv_force_field_map_90d.csv",
    "alignment": "sgv_force_alignment_detail_90d.csv",
    "alignment_summary": "sgv_force_alignment_summary_90d.csv",
    "expected_value": "sgv_expected_value_90d.csv",
    "edge": "sgv_edge_signal_90d.csv",
}
ALL_STEPS = ["info_local", "info", "geodesic", "singularity", "terrain", "force_field",
             "alignment", "expected_value", "edge"]
DEPENDS = {"geodesic": ["info"], "singularity": ["geodesic"], "force_field": ["terrain"],
           "alignment": ["terrain"], "expected_value": ["terrain"], "edge": ["alignment", "expected_value"]}


def _with_deps(steps: list[str]) -> list[str]:
    need: set[str] = set()

    def add(s):
        for d in DEPENDS.get(s, []):
            add(d)
        need.add(s)

    for s in steps:
        add(s)
    return [s for s in ALL_STEPS if s in need]


def run_pipeline(df: pd.DataFrame, cfg: SGVConfig, steps: list[str] | None = None) -> dict[str, pd.DataFrame]:
    steps = _with_deps(steps or ALL_STEPS)
    out: dict[str, pd.DataFrame] = {}
    timings: dict[str, float] = {}

    def run(name, fn):
        t0 = time.perf_counter()
        res = fn()
        timings[name] = time.perf_counter() - t0
        log.info("%-15s %7.1f s", name, timings[name])
        return res

    if "info_local" in steps:
        out["info_local"] = run("info_local", lambda: information_field_local.build_information_field_local_90d(df, cfg))
    if "info" in steps:
        out["info"] = run("info", lambda: information_field.build_information_field_geometry_90d(df, cfg))
    if "geodesic" in steps:
        out["geodesic"] = run("geodesic", lambda: geodesic_field.build_geodesic_field_full3d_90d(out["info"], cfg))
    if "singularity" in steps:
        out["singularity"] = run("singularity", lambda: singularity.build_singularity_detector_90d(out["geodesic"], cfg))
    if "terrain" in steps:
        out["terrain"] = run("terrain", lambda: terrain.build_terrain_layer_90d(df, cfg))
    if "force_field" in steps:
        out["force_field"] = run("force_field", lambda: force_field.build_force_field_90d(out["terrain"], cfg))
    if "alignment" in steps:
        fmap = out.get("force_field") if cfg.legacy.LEGACY_GLOBAL_MAP else None
        detail, summary = run("alignment", lambda: force_alignment.build_force_alignment_90(out["terrain"], fmap, cfg))
        out["alignment"], out["alignment_summary"] = detail, summary
    if "expected_value" in steps:
        out["expected_value"] = run("expected_value", lambda: expected_value.build_expected_value_90d(out["terrain"], cfg))
    if "edge" in steps:
        out["edge"] = run("edge", lambda: edge_signal.build_edge_signal_90(out["alignment"], out["expected_value"], cfg))
    for v in out.values():
        v.attrs.setdefault("sgv_meta", {})["pipeline_timings_s"] = {k: round(t, 2) for k, t in timings.items()}
    return out


def parse_overrides(cfg: SGVConfig, items: list[str]) -> SGVConfig:
    """``section.FIELD=valor`` → nova configuração (tipo pelo valor padrão)."""
    for item in items or []:
        key, _, raw = item.partition("=")
        section, _, fld = key.partition(".")
        sec = getattr(cfg, section)
        cur = getattr(sec, fld)
        if isinstance(cur, bool):
            val = raw.strip().lower() in ("1", "true", "sim", "yes", "on")
        elif isinstance(cur, int):
            val = int(raw)
        elif isinstance(cur, float):
            val = float(raw)
        elif isinstance(cur, tuple):
            val = tuple(int(x) for x in raw.split(","))
        else:
            val = raw
        cfg = dataclasses.replace(cfg, **{section: dataclasses.replace(sec, **{fld: val})})
    return cfg


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Pipeline da camada geométrica do SGV")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="CSV já montado (timestamp, close, E_norm, jerk, lambda_dynamic)")
    src.add_argument("--raw", help="barras OHLCV de 1m (btc_90d_1m_raw.csv): monta o input antes")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--legacy", action="store_true", help="liga todas as flags LEGACY_*")
    ap.add_argument("--set", action="append", default=[], help="section.FIELD=valor (repetível)")
    ap.add_argument("--steps", default=",".join(ALL_STEPS))
    ap.add_argument("--live-fill", action="store_true", help="aplica finalize_for_live (NaN→0) nas saídas")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    cfg = SGVConfig.legacy_config() if args.legacy else SGVConfig()
    cfg = parse_overrides(cfg, args.set)
    out_dir = Path(args.out_dir)
    if args.raw:
        df = input_builder.build_btc_90d_input_sgv(pd.read_csv(args.raw), cfg)
        write_outputs(df, out_dir / OUTPUT_NAMES["input"], cfg)
        print(f"{'input':16s} {len(df):>8d} linhas → {out_dir / OUTPUT_NAMES['input']}")
    else:
        df = pd.read_csv(args.input)
    results = run_pipeline(df, cfg, [s.strip() for s in args.steps.split(",") if s.strip()])
    for name, frame in results.items():
        if args.live_fill and name not in ("alignment_summary", "force_field"):
            frame = finalize_for_live(frame)
        path = write_outputs(frame, out_dir / OUTPUT_NAMES[name], cfg)
        print(f"{name:16s} {len(frame):>8d} linhas → {path}")
    print(f"config_hash={cfg.config_hash()}")


if __name__ == "__main__":
    main()
