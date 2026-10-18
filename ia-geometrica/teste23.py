"""Teste 23 (o teste de amplitude). Predição: PREDICAO_teste23_amplitude.md."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import teste22 as T

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste23_amplitude.md").exists(), "sem predição, sem teste"
AMPS = [0.1, 0.3, 1.0, 3.0]; A0 = 0.1; SIG = 0.05; LIMIAR = 0.05
VERSOES = {"linear": lambda z: z, "tanh": np.tanh}


def main():
    acc = {v: {A: [] for A in AMPS if A != A0} for v in VERSOES}
    for s in T.SEEDS:
        x = T.mundo(s); a, W, u, r = T.rede(s); rng = np.random.default_rng(s + 7)
        for v, phi in VERSOES.items():
            Hs = {}
            for A in AMPS:
                y = T.rodar_rede(A * x, a, W, u, r, phi) + rng.normal(0, SIG, len(x)); f, Sxx, H, _ = T.regua(x, y); Hs[A] = (Sxx, H)
            Sxx, H0 = Hs[A0]; den = (Sxx * np.abs(H0) ** 2).sum()
            for A in AMPS:
                if A == A0: continue
                acc[v][A].append(float((Sxx * np.abs(Hs[A][1] - H0) ** 2).sum() / den))
        if (s - 1000) % 10 == 0: print(f"  s{s} ok", flush=True)
    out = {}
    for v in VERSOES:
        out[v] = {str(A): {"D_mediano": float(np.median(acc[v][A])), "acima_do_limiar": int(sum(d > LIMIAR for d in acc[v][A])), "abaixo_do_limiar": int(sum(d < LIMIAR for d in acc[v][A]))} for A in acc[v]}
        print(f"  {v}: " + " | ".join(f"D({A}) mediano {out[v][str(A)]['D_mediano']:.4f}, > limiar em {out[v][str(A)]['acima_do_limiar']}" for A in acc[v]), flush=True)
    a = out["linear"]["3.0"]["abaixo_do_limiar"] >= 95; b = out["tanh"]["3.0"]["acima_do_limiar"] >= 95
    out["criterio"] = {"a_linear_abaixo": bool(a), "b_tanh_acima": bool(b), "passa": bool(a and b)}
    print(f"\n== teste 23: (a) linear D(3) < 0,05 em {out['linear']['3.0']['abaixo_do_limiar']} | (b) tanh D(3) > 0,05 em {out['tanh']['3.0']['acima_do_limiar']} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste23.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
