"""Complemento à exploração do H-SGV-01 (rascunho): ago–set fora da amostra e três controles novos.

Previsão registrada antes de calcular: PREDICAO_sgv_original_complemento.md.

    python pipeline/explorar_sgv_original_complemento.py --periodo fumaca   # só confere que roda (maio); não imprime estatísticas
    python pipeline/explorar_sgv_original_complemento.py --periodo junjul   # paridade com explorar_sgv_original.py + controles novos
    python pipeline/explorar_sgv_original_complemento.py --periodo agoset   # ago–set/2026 (aberto em 13/10 pelo H-σRTT-01)

Mesmo desenho e mesmas funções de pipeline/explorar_sgv_original.py (importadas, não copiadas): variáveis do sgv_original,
alvo log Range dos 5 min seguintes, 1 minuto a cada 5, ρ parcial de Spearman por semana, nula de pipeline.
Conjuntos de controles:
    prim      os controles primários do rascunho
    sec_orig  prim + log ρ e log tr D do campo do H-DIF-01 no espaço original (a secundária do rascunho)
    sec_fluxo prim + log ρ, log tr D e c(x) do campo do H-DIF-01 no espaço de FLUXO + ν(t)   [complementaridade]
    sec_ret   prim + retornos com sinal de 60, 240 e 1.440 min                                [alavancagem lenta]
Nada de outubro é lido.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import confirmatorio_forma as F  # noqa: E402
import explorar_sgv_original as XS  # noqa: E402

VARS = XS.VARS
PERIODOS = {"fumaca": {"meses": ["2026-05"], "treino0": "2026-05-10", "inicio": "2026-05-17", "fim": "2026-05-31"},
            "junjul": F.PERIODOS["exploracao"],
            "agoset": {"meses": ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "treino0": "2026-07-25", "inicio": "2026-08-01", "fim": "2026-10-01"}}
CONJ = ("prim", "sec_orig", "sec_fluxo", "sec_ret")


def analisar(V, Go, Gf, kl, ts, wk, hour_d):
    close, high, low, vol = (kl[c].values.astype(float) for c in ("close", "high", "low", "volume"))
    lc, hi, lo = np.log(close), np.log(high), np.log(low); n = len(lc)
    r = np.diff(lc, prepend=np.nan); rs = pd.Series(r)
    rng5 = np.full(n, np.nan)
    for t in range(n - 5):
        rng5[t] = hi[t + 1:t + 6].max() - lo[t + 1:t + 6].min()
    y = np.log(rng5 + 1e-9)
    lvol = pd.Series(np.log(vol)); r1 = pd.Series(np.log(np.maximum(hi - lo, 1e-6)))
    sig = [np.log(rs.rolling(w).std() + 1e-9) for w in (10, 30, 60)]
    C = np.column_stack([np.ones(n)] + sig + [
        np.log(rs.rolling(1440, min_periods=720).std() + 1e-9), np.log(rs.rolling(10080, min_periods=2880).std() + 1e-9),
        rs.rolling(5).sum(), rs.rolling(30).sum(), lvol.rolling(10).mean(), lvol.rolling(60).mean(), hour_d]
        + [r1.rolling(w, min_periods=1).mean() for w in (1, 5, 10, 30, 60, 1440)])   # idêntico a explorar_sgv_original.analisar
    RET = np.column_stack([rs.rolling(w, min_periods=w // 2).sum() for w in (60, 240, 1440)])
    res = {v: {c: [] for c in CONJ} for v in VARS}
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        s5 = te[np.arange(len(te)) % 5 == 0]
        extra = {}
        for nome, G in (("orig", Go), ("fluxo", Gf)):
            Cf = F.Campo(G, tr); X = G[s5]; okx = np.isfinite(X).all(1)
            cc, lt, lr_ = (np.full(len(s5), np.nan) for _ in range(3))
            c_, _, lt_, lrr = Cf.at(X[okx]); cc[okx] = c_; lt[okx] = lt_; lr_[okx] = lrr
            extra[nome] = (cc, lt, lr_)
        Cs = {"prim": C[s5],
              "sec_orig": np.column_stack([C[s5], extra["orig"][2], extra["orig"][1]]),
              "sec_fluxo": np.column_stack([C[s5], extra["fluxo"][2], extra["fluxo"][1], extra["fluxo"][0], Gf[s5, 2]]),
              "sec_ret": np.column_stack([C[s5], RET[s5]])}
        for j, v in enumerate(VARS):
            for c in CONJ: res[v][c].append(F.rho_parcial(V[s5, j], y[s5], Cs[c]))
    return {v: {c: [round(float(x), 4) for x in res[v][c]] for c in CONJ} for v in VARS}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True)
    a = ap.parse_args(); P = PERIODOS[a.periodo]
    kl = F.carregar(P["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    wk = F.semanas(ts, P["treino0"], P["inicio"], P["fim"])
    hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
    rng_null = np.random.default_rng(F.SEED_NULL)
    i_perm = wk[0][0]; day = ts.dt.floor("D").to_numpy(); perm = np.arange(len(kl))
    for d in np.unique(day[i_perm:]):
        s = np.where(day == d)[0]; s = s[s >= i_perm]; perm[s] = rng_null.permutation(s)
    lc = np.log(kl.close.values); lr = np.diff(lc, prepend=lc[0]); hi = np.log(kl.high.values) - lc; lo = lc - np.log(kl.low.values)
    lv = np.log(kl.volume.values.astype(float)); frac = kl.taker_buy.values / kl.volume.values
    c2 = np.exp(lc[0] + np.cumsum(lr[perm]))
    kl_null = pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]),
                            "close": c2, "volume": np.exp(lv[perm]), "taker_buy": frac[perm] * np.exp(lv[perm])})
    out = {"periodo": a.periodo, "semanas_julgadas": [str(ts.iloc[w[0]].date()) for w in wk[1:]], "res": {}}
    for label, K in (("real", kl), ("pipeline", kl_null)):
        G = {}
        for sp in ("orig", "flow"):
            raw = F.COORDS[sp](K); ok = np.isfinite(raw).all(1)
            anc = F.COORDS[sp](kl); anc = anc[may & np.isfinite(anc).all(1)]
            G[sp] = np.full_like(raw, np.nan); G[sp][ok] = F.gaussianize(anc, raw[ok])
        out["res"][label] = analisar(XS.variaveis_sgv(K), G["orig"], G["flow"], K, ts, wk, hour_d)
        print(f"  [{label}] pronto", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    for label in ("real", "pipeline"):
        for v in VARS:
            row = out["res"][label][v]
            p = np.array(row["prim"]); sgn = np.sign(np.nanmean(p))
            print(f"{label:8s} {v:7s} prim {np.nanmean(p):+.4f} ({int((np.sign(p) == sgn).sum())}/{len(p)}) | sec_orig {np.nanmean(row['sec_orig']):+.4f} "
                  f"| sec_fluxo {np.nanmean(row['sec_fluxo']):+.4f} | sec_ret {np.nanmean(row['sec_ret']):+.4f} | semanas prim {p.round(3).tolist()}", flush=True)
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"sgv_original_complemento_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
