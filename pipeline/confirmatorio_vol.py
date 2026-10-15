"""H-VOL-01 — confirmatório (outubro/2026). Código congelado; definições em PREREGISTRO_H-VOL-01.md.

    python pipeline/confirmatorio_vol.py --paridade     # jun–jul: reproduz exatamente resultados/volatilidade_multiescala_junjul.json
    python pipeline/confirmatorio_vol.py --julgamento   # outubro/2026, uma única vez
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_escondida as V  # noqa: E402
import explora_volatilidade_escondida_v2 as V2  # noqa: E402
import explora_volatilidade_multiescala as MS  # noqa: E402

E = GR.E
MODOS = {"paridade": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
         "julgamento": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"], "2026-09-24", "2026-10-29")}
EST = ["ew10", "c60", "ew30", "har"]


def rodar(modo):
    meses, ini, fim = MODOS[modo]
    kl = E.carregar(meses, ROOT / "dados"); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    res = {"real": V2.medir(kl, ts, may, wk)}; print("  real: ok", flush=True); calib = {}
    for s in MS.SEEDS_M:
        k_, o, p = MS.gerar_m(kl, ts, i0, s); res[f"M_{s}"] = V2.medir(k_, ts, may, wk, o); calib[f"M_{s}"] = p; print(f"  M_{s}: ok", flush=True)
    for s in V.SEEDS_G:
        k_, o = V.gerar(kl, ts, i0, s, True); res[f"G_{s}"] = V2.medir(k_, ts, may, wk, o); print(f"  G_{s}: ok", flush=True)
    return res, calib, [str(ts.iloc[w[0]].date()) for w in wk]


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--paridade", action="store_true"); g.add_argument("--julgamento", action="store_true"); a = ap.parse_args()
    out_dir = ROOT / "resultados"; out_dir.mkdir(exist_ok=True)
    if a.paridade:
        res, _, _ = rodar("paridade")
        ref = json.loads((ROOT / "resultados" / "volatilidade_multiescala_junjul.json").read_text())["series"]
        dif = max(abs(res[s][k] - ref[s][k]) for s in ref for k in ref[s])
        print(f"paridade: diferença máxima contra a exploração = {dif:.2e}")
        (out_dir / "H-VOL-01_paridade.json").write_text(json.dumps({"diferenca_maxima": dif, "series": res}, ensure_ascii=False))
        sys.exit(0 if dif < 1e-9 else "Paridade falhou")
    alvo = out_dir / "H-VOL-01_julgamento.json"
    if alvo.exists():
        sys.exit("H-VOL-01 já julgado: julgamento único")
    res, calib, semanas = rodar("julgamento")
    Ms = [res[f"M_{s}"] for s in MS.SEEDS_M]; Gs = [res[f"G_{s}"] for s in V.SEEDS_G]
    red_orc = float(np.mean([1 - m["oraculo"] / m["sem_vol"] for m in Ms]))
    out = {"hipotese": "H-VOL-01", "semanas": semanas, "series": res, "calibracao": calib, "red_oraculo_M": red_orc,
           "validacao_passa": red_orc >= 0.7}
    comp = {}
    for e in EST:
        mr = res["real"][e]; mm = [m[e] for m in Ms]; mg = [g_[e] for g_ in Gs]
        comp[e] = {"M_real": mr, "M_M": [min(mm), max(mm)], "M_G": [min(mg), max(mg)], "real_le_max_M": mr <= max(mm),
                   "dentro_G_M": min(mg) <= mr <= max(mm)}
    out["comparacoes"] = comp
    if not out["validacao_passa"]:
        out["veredito"] = "INCONCLUSIVO (validação falhou)"
    else:
        out["veredito"] = "CONFIRMADA" if comp["ew10"]["real_le_max_M"] else "NÃO CONFIRMADA"
        out["robusta"] = len({c["real_le_max_M"] for c in comp.values()}) == 1
    print(json.dumps({k: v for k, v in out.items() if k not in ("series", "calibracao")}, ensure_ascii=False, indent=1))
    alvo.write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
