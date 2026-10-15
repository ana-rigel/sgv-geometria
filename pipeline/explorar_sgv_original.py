"""Exploração (BTC jun–jul/2026) das variáveis do sgv_original que sobreviveram à varredura de 188 métricas,
com o desenho do H-FORMA-D-01 (mesmos alvos, controles, semanas, amostragem 1 a cada 5 min e nula de pipeline).

    python pipeline/explorar_sgv_original.py

Variáveis (vendor/sgv_original @ ac6b986, SGVConfig() padrão = causal):
    log_rho   log da densidade KDE 2D de (E_norm, jerk), ajustada nos 7 dias anteriores (information_field)
    basin     terrain_basin_depth = log ρ − 0,6·|∇log ρ|  (terrain)
    disp      terrain_informational_displacement = log(1 + Mahalanobis² ao atrator EWMA de 80 barras) (terrain)
    n_obs     log(1 + contagem da célula 40×40 de (E_norm, jerk) nos 7 dias anteriores) (force_alignment)
    mem_e     EMA_0,05(E_norm): nível suavizado do esticamento do preço em relação à sua EMA (information_field)
Controles primários: os do H-FORMA-D-01 sem log ρ e log tr D (σ 10/30/60, HAR 1d/1s, r5/r30, logvol 10/60, hora,
memória de amplitude 1/5/10/30/60/1440). Secundário: + log ρ e log tr D do campo do H-DIF-01 no espaço original.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import confirmatorio_forma as F  # noqa: E402  (carregar, Campo, residuos, rho_parcial, semanas, gaussianize, COORDS)
from sgv import force_alignment, information_field, terrain  # noqa: E402
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402

VARS = ("log_rho", "basin", "disp", "n_obs", "mem_e")


def variaveis_sgv(kl):
    raw = pd.DataFrame({"timestamp": kl["timestamp"].to_numpy(),
                        "datetime": pd.to_datetime(kl["timestamp"], unit="ms", utc=True).astype(str).to_numpy()})
    for c in ("open", "high", "low", "close", "volume"):
        raw[c] = pd.to_numeric(kl[c]).to_numpy()
    cfg = SGVConfig()
    inp = build_btc_90d_input_sgv(raw, cfg); assert len(inp) == len(kl)
    info = information_field.build_information_field_geometry_90d(inp, cfg)
    ter = terrain.build_terrain_layer_90d(inp, cfg)
    ali, _ = force_alignment.build_force_alignment_90(ter, None, cfg)
    # as camadas descartam linhas do aquecimento; alinhar pelo timestamp inteiro em ms. A camada de informação
    # converte o inteiro em datetime como se fosse ns (1970): o valor inteiro desse datetime é o ms original.
    out = pd.DataFrame(index=pd.RangeIndex(len(kl)))
    key = kl["timestamp"].to_numpy("int64")

    def as_ms(col):
        if pd.api.types.is_integer_dtype(col):
            return col.astype("int64").to_numpy()
        ns = pd.DatetimeIndex(col).as_unit("ns").asi8
        return ns if ns.max() < 10 ** 14 else ns // 10 ** 6     # 1970 (ms lido como ns) ou datas reais

    for df_, cols in ((info, {"rho_field": "rho", "mem_e": "mem_e"}),
                      (ter, {"terrain_basin_depth": "basin", "terrain_informational_displacement": "disp"}),
                      (ali, {"force_cell_n_obs": "n_obs"})):
        m = pd.Series(np.arange(len(df_), dtype=float), index=as_ms(df_["timestamp"]))
        assert m.index.is_unique and np.isin(m.index, key).all(), "timestamps da camada não batem com os klines"
        pos = m.reindex(key).to_numpy()
        for src, dst in cols.items():
            v = np.full(len(kl), np.nan); okp = np.isfinite(pos)
            v[okp] = df_[src].to_numpy(float)[pos[okp].astype(int)]
            out[dst] = v
    out["log_rho"] = np.log(np.maximum(out.pop("rho"), 1e-300))
    out["n_obs"] = np.log1p(out["n_obs"])
    return out[list(VARS)].to_numpy(float)


def analisar(V, Gorig, kl, ts, wk, hour_d, label):
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
        + [r1.rolling(w, min_periods=1).mean() for w in (1, 5, 10, 30, 60, 1440)])
    res = {v: {"prim": [], "sec": []} for v in VARS}
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        s5 = te[np.arange(len(te)) % 5 == 0]
        Cf = F.Campo(Gorig, tr)
        X = Gorig[s5]; okx = np.isfinite(X).all(1)
        logrho_d = np.full(len(s5), np.nan); logtr = np.full(len(s5), np.nan)
        _, _, lt, lr_ = Cf.at(X[okx]); logtr[okx] = lt; logrho_d[okx] = lr_
        for j, v in enumerate(VARS):
            res[v]["prim"].append(F.rho_parcial(V[s5, j], y[s5], C[s5]))
            res[v]["sec"].append(F.rho_parcial(V[s5, j], y[s5], np.column_stack([C[s5], logrho_d, logtr])))
    # correlação entre as variáveis (em todos os minutos avaliados)
    idx = np.concatenate(wk[1:]); ok = np.isfinite(V[idx]).all(1)
    corr = pd.DataFrame(V[idx][ok], columns=VARS).corr(method="spearman").round(3).to_dict()
    for v in VARS:
        a, b = np.array(res[v]["prim"]), np.array(res[v]["sec"])
        print(f"{label:9s} {v:8s} ρ̄ prim {np.nanmean(a):+.4f} ({int((np.sign(a) == np.sign(np.nanmean(a))).sum())}/{len(a)})  "
              f"ρ̄ sec {np.nanmean(b):+.4f}  semanas {np.round(a, 3).tolist()}", flush=True)
    return {v: {"prim_semanal": [round(float(x), 4) for x in res[v]["prim"]], "prim_media": float(np.nanmean(res[v]["prim"])),
                "sec_semanal": [round(float(x), 4) for x in res[v]["sec"]], "sec_media": float(np.nanmean(res[v]["sec"]))}
            for v in VARS} | {"correlacao_spearman": corr}


def main():
    P = F.PERIODOS["exploracao"]
    kl = F.carregar(P["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
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
    out = {}
    for label, K in (("real", kl), ("pipeline", kl_null)):
        raw = F.COORDS["orig"](K); ok = np.isfinite(raw).all(1)
        anchor = F.COORDS["orig"](kl); anchor = anchor[may & np.isfinite(anchor).all(1)]
        G = np.full_like(raw, np.nan); G[ok] = F.gaussianize(anchor, raw[ok])
        out[label] = analisar(variaveis_sgv(K), G, K, ts, wk, hour_d, label)
    dest = ROOT / "resultados" / "explorar_sgv_original_jun_jul.json"; dest.parent.mkdir(exist_ok=True)
    json.dump(out, open(dest, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("correlações (real):", json.dumps(out["real"]["correlacao_spearman"], indent=0))
    print("→", dest)


if __name__ == "__main__":
    main()
