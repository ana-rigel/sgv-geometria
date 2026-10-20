"""Gera os dados da página "Cérebro de Juara": a v0 (4 andares, λ₁ = 0,15, b = 10, passo diário) lendo três sensores
padronizados (água no solo 28–100 cm, balanço chuva − ET0 em 7 dias, sede do ar/VPD), 2010–2025. Visualização, não teste."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); import v0 as V
import teste30 as T

def main(saida):
    D, ano, doy, P, E, s0, s3 = T.ler_diario()
    import csv, gzip
    vpd = {}
    with gzip.open(T.DADOS, "rt") as f:
        r = csv.reader(f); h = next(r); iv = h.index("vapour_pressure_deficit")
        for row in r: vpd.setdefault(row[0][:10], []).append(float(row[iv]))
    vp = np.array([np.mean(vpd[d]) for d in D])
    bal = np.convolve(P - E, np.ones(7) / 7)[:len(P)]
    cal = ano <= 2017
    z = lambda v: (v - v[cal].mean()) / v[cal].std()
    x = np.column_stack([z(s3), z(bal), z(vp)])
    obs = V.Observador(3); obs.R[:] = 0.0; Ts, _, Rh = V.rodar(x, obs)   # andares começam no normal da calibração (média 0)
    out = {"dias": D, "eixos": ["água no solo (28–100 cm)", "chuva − evaporação (7 dias)", "sede do ar (VPD)"],
           "tau_dias": (1 / obs.lams).round(1).tolist(),
           "x": np.round(x, 2).tolist(), "R": np.round(Rh, 2).tolist()}
    Path(saida).write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(len(D), "dias;", Path(saida).stat().st_size // 1024, "KB; τ", out["tau_dias"])
    print("faixas x:", np.round(x.min(0), 1), np.round(x.max(0), 1))

if __name__ == "__main__":
    main(sys.argv[1])
