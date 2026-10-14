#!/usr/bin/env python3
"""Retomada M35 passo 1 por lotes determinísticos, sem novos alvos de mercado.

Modos:
  synthetic: os mesmos 60 trabalhos sintéticos da especificação congelada.
  btc-spent: os mesmos jobs BTC mai-jul do script m35_passo1.py; exige
             SOMENTE os três ZIP locais de 2026-05, 06, 07.
Nenhuma hipótese é testada aqui; os lotes NÃO fazem seleção de variante.
Consolidação/inferência continua definida por scripts/m35_passo1.py e
reports/m35/PLANO_M35_PASSO1_20261013.md. Não reparametrizar instrumentos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STAGE_SYNTHETIC = "synthetic"
STAGE_BTC = "btc-spent"
SOURCE_FILES = (
    ROOT / "experiments" / "m35_instrumento.py",
    ROOT / "scripts" / "m35_passo1.py",
    ROOT / "reports" / "m35" / "PLANO_M35_PASSO1_20261013.md",
)
MONTHS = ("05", "06", "07")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def source_fingerprints() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): sha256(p) for p in SOURCE_FILES}


def synthetic_jobs() -> list[dict]:
    # Replicar EXATAMENTE a geração da lista syn de scripts/m35_passo1.py.
    import numpy as np
    rng = np.random.default_rng(7)
    pairs = [(float(a), float(b), 9000 + k)
             for k, (a, b) in enumerate(rng.uniform(0, 3, (40, 2)))]
    pairs += [(float(s), float(s), 9500 + k)
              for k, s in enumerate(rng.uniform(0, 3, 20))]
    return [{"kind": "synth", "sep_a": a, "sep_b": b, "seed": seed}
            for a, b, seed in pairs]


def _spent_btc_inputs() -> dict[str, str]:
    import zipfile
    hashes = {}
    for mo in MONTHS:
        p = ROOT / "data" / f"BTCUSDT-1m-2026-{mo}.zip"
        if not p.is_file():
            raise FileNotFoundError(f"BTC exploratório ausente: {p}")
        with zipfile.ZipFile(p) as z:
            if z.testzip() is not None:
                raise ValueError(f"ZIP exploratório corrompido: {p}")
        hashes[str(p.relative_to(ROOT))] = sha256(p)
    return hashes


def spent_btc_jobs() -> list[dict]:
    # Sem import até a checagem da whitelist May-Jul ter sido concluída.
    _spent_btc_inputs()
    from scripts import m35_passo1 as original
    jobs = [{"kind": "full", "i": int(i), "rep": 0} for i in original.FULL]
    jobs += [{"kind": kind, "i": int(i), "rep": int(r)}
             for i in original.PICK
             for kind in ("alg", "boot") for r in range(original.REPS)]
    return jobs


def selected_indices(total: int, shard: int, shards: int) -> list[int]:
    if not 1 <= shards <= 256 or not 0 <= shard < shards:
        raise ValueError("shard deve estar em [0, shards); shards 1..256")
    return list(range(shard, total, shards))


def execute_spec(stage: str, spec: dict) -> dict:
    if stage == STAGE_SYNTHETIC:
        import numpy as np
        from experiments import m35_instrumento as instrument
        # O script original instancia um único rng para as duas chamadas.
        rng = np.random.default_rng(spec["seed"])
        a = instrument.planted(spec["sep_a"], 525, rng)
        b = instrument.planted(spec["sep_b"], 525, rng)
        return {"kind": "synth", "sep_a": spec["sep_a"], "sep_b": spec["sep_b"],
                **instrument.measure_all(a, b, spec["seed"])}
    from scripts import m35_passo1 as original
    return original.job((spec["kind"], spec["i"], spec["rep"]))


def run(stage: str, shard: int, shards: int, output: Path,
        *, max_jobs: int | None = None, resume: bool = True) -> dict:
    if stage not in (STAGE_SYNTHETIC, STAGE_BTC):
        raise ValueError("modo não autorizado")
    inputs = source_fingerprints()
    if stage == STAGE_BTC:
        inputs.update(_spent_btc_inputs())
        jobs = spent_btc_jobs()
    else:
        jobs = synthetic_jobs()
    indices = selected_indices(len(jobs), shard, shards)
    if max_jobs is not None:
        if max_jobs < 1:
            raise ValueError("max-jobs deve ser positivo")
        indices = indices[:max_jobs]
    expected = {
        "study": "M35 passo 1, APENAS engenharia; sem alvo de mercado",
        "stage": stage, "shard": shard, "shards": shards,
        "source_sha256": inputs, "all_jobs": len(jobs),
        "indices": indices, "job_specs": [jobs[i] for i in indices],
        "limit_is_smoke_only": max_jobs is not None,
    }
    rows = []
    if output.exists() and resume:
        old = json.loads(output.read_text(encoding="utf-8"))
        for field, val in expected.items():
            if old.get(field) != val:
                raise ValueError(f"checkpoint incompatível, recusa reutilizar: {field}")
        rows = old.get("rows", [])
        if len(rows) > len(indices):
            raise ValueError("checkpoint contém mais linhas que jobs autorizados")
        if len(rows) == len(indices):
            return old
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    for no in range(len(rows), len(indices)):
        i = indices[no]
        rows.append(execute_spec(stage, jobs[i]))
        # Checkpoint atômico APÓS cada job: interrupção não perde medições concluídas.
        result = {**expected, "rows": rows}
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, output)
        print(f"M35 {stage}: shard {shard}/{shards}, job {no + 1}/{len(indices)} (global {i})", flush=True)
    return {**expected, "rows": rows}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=(STAGE_SYNTHETIC, STAGE_BTC), required=True)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--shards", type=int, default=1)
    p.add_argument("--out", type=Path)
    p.add_argument("--max-jobs", type=int, help="limita trabalhos para smoke; NÃO vale como execução completa")
    p.add_argument("--no-resume", action="store_true")
    a = p.parse_args()
    out = a.out or ROOT / "reports" / "m35" / "lotes" / f"{a.stage}-{a.shard:03d}-of-{a.shards:03d}.json"
    res = run(a.stage, a.shard, a.shards, out, max_jobs=a.max_jobs, resume=not a.no_resume)
    print(json.dumps({"out": str(out), "status": "engenharia",
                      "rows": len(res["rows"]), "total": res["all_jobs"],
                      "partial_smoke_only": res["limit_is_smoke_only"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
