"""E-VOL-01 — o campo de difusão D(x) acrescenta algo à vol implícita? (exploração, jun–jul/2026)

Pergunta 1 do caminho das opções: log tr D(x_t) (campo da semana anterior, h = 0,45, âncora de maio) prevê a
amplitude futura ALÉM da vol implícita de curto prazo (IV_curta: mediana da IV dos negócios de opções de BTC na
Deribit com vencimento entre 4 h e 3 dias e strike a ±2 % do índice, nos últimos 60 min) e do DVOL (30 dias)?

Alvos: log Range_{t+5} (5 min), log RV_{60} (vol realizada dos próximos 60 min), log RV_{1d} (24 h).
Controles: fortes (σ 10/30/60, HAR 1d/1s, r5/r30, log-vol 10/60, hora) + log ρ(x_t); depois + log DVOL;
depois + log IV_curta; depois os dois. Correlação parcial de Spearman por semana fora da amostra, 8 semanas,
dois espaços. Sem nula (exploração): reporta-se a dispersão entre semanas.
Também: ρ parcial da própria IV_curta e do DVOL com cada alvo além dos controles fortes (quanto o mercado de
opções sabe que o HAR não sabe).
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import confirmatorio_dif as cd  # noqa: E402
from scipy import stats  # noqa: E402


def rho_parcial(x, y, C, minimo=100):
    xr, yr, _ = cd.residuos(x, y, C)
    return float(stats.spearmanr(xr, yr)[0]) if len(xr) >= minimo else np.nan

PER = cd.PERIODOS["exploracao"]


def iv_curta(ts_min):
    """IV mediana por minuto dos negócios curtos ao dinheiro; depois mediana móvel causal de 60 min, ffill ≤ 180 min."""
    tr = pd.read_csv(gzip.open(ROOT / "vol_implicita" / "dados" / "opcoes_trades.csv.gz", "rt"))
    tr = tr[tr.iv.notna() & (tr.iv > 0) & tr.index_price.notna()]
    parts = tr.instrument.str.split("-", expand=True)
    tr = tr[parts[0] == "BTC"].copy(); parts = parts[parts[0] == "BTC"]
    tr["exp"] = pd.to_datetime(parts[1], format="%d%b%y", utc=True, errors="coerce") + pd.Timedelta(hours=8)
    tr["K"] = pd.to_numeric(parts[2], errors="coerce")
    tr["t"] = pd.to_datetime(tr.ts, unit="ms", utc=True)
    tte = (tr.exp - tr.t).dt.total_seconds() / 3600
    sel = tr[(tte >= 4) & (tte <= 72) & ((tr.K / tr.index_price - 1).abs() <= 0.02)]
    print(f"opções: {len(tr):,} negócios com IV; {len(sel):,} curtos e ao dinheiro", flush=True)
    por_min = sel.groupby(sel.t.dt.floor("min")).iv.median()
    serie = por_min.reindex(ts_min).rolling(60, min_periods=5).median().ffill(limit=180)
    return np.log(serie.to_numpy() / 100.0)


def dvol(ts_min):
    d = pd.read_csv(ROOT / "vol_implicita" / "dados" / "dvol.csv")
    s = pd.Series(d.close.values, index=pd.to_datetime(d.ts, unit="ms", utc=True)).reindex(ts_min).ffill(limit=180)
    return np.log(s.to_numpy() / 100.0)


def main():
    kl = cd.carregar(PER["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    wk = cd.semanas(ts, PER["treino0"], PER["inicio"], PER["fim"])
    hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
    ts_min = pd.DatetimeIndex(ts)
    IV = iv_curta(ts_min); DV = dvol(ts_min)
    print(f"cobertura IV_curta: {np.isfinite(IV)[~may].mean():.1%}; DVOL: {np.isfinite(DV)[~may].mean():.1%}", flush=True)
    close, high, low, vol = (kl[c].values.astype(float) for c in ("close", "high", "low", "volume"))
    lc, hi, lo = np.log(close), np.log(high), np.log(low); n = len(lc)
    r = np.diff(lc, prepend=np.nan); rs = pd.Series(r)
    rng5 = np.full(n, np.nan)
    for t in range(n - 5): rng5[t] = hi[t + 1:t + 6].max() - lo[t + 1:t + 6].min()
    r2 = pd.Series(r ** 2)
    rv60 = r2[::-1].rolling(60).sum()[::-1].shift(-1).to_numpy(); rv1d = r2[::-1].rolling(1440).sum()[::-1].shift(-1).to_numpy()
    alvos = {"range5": (np.log(rng5 + 1e-9), 5), "rv60": (0.5 * np.log(rv60 + 1e-12), 15), "rv1d": (0.5 * np.log(rv1d + 1e-12), 60)}   # rv: janelas sobrepostas (15 e 60 min)
    lvol = pd.Series(np.log(vol)); sig = [np.log(rs.rolling(w).std() + 1e-9) for w in (10, 30, 60)]
    C0 = np.column_stack([np.ones(n)] + sig + [np.log(rs.rolling(1440, min_periods=720).std() + 1e-9), np.log(rs.rolling(10080, min_periods=2880).std() + 1e-9),
                                              rs.rolling(5).sum(), rs.rolling(30).sum(), lvol.rolling(10).mean(), lvol.rolling(60).mean(), hour_d])
    res = {"cobertura": {"iv_curta": float(np.isfinite(IV)[~may].mean()), "dvol": float(np.isfinite(DV)[~may].mean())}, "iv_vs_alvos": {}, "espacos": {}}
    # (0) o que a IV e o DVOL sabem além dos controles fortes
    for nome, (y, step) in alvos.items():
        idx = np.arange(wk[1][0], n); s = idx[np.arange(len(idx)) % step == 0]
        res["iv_vs_alvos"][nome] = {"iv_curta": rho_parcial(IV[s], y[s], C0[s]), "dvol": rho_parcial(DV[s], y[s], C0[s]),
                                    "iv_curta|dvol": rho_parcial(IV[s], y[s], np.column_stack([C0[s], DV[s]]))}
    print("IV vs alvos (ρ parcial além dos controles fortes):", json.dumps(res["iv_vs_alvos"]), flush=True)
    # (1) D(x) além de tudo
    for sp in ("flow", "orig"):
        raw = cd.COORDS[sp](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]
        G = np.full_like(raw, np.nan); G[ok] = cd.gaussianize(anchor, raw[ok])
        acc = {nome: {c: [] for c in ("base", "+dvol", "+iv", "+dvol+iv")} for nome in alvos}
        for k in range(1, len(wk)):
            F = cd.Campo(G, wk[k - 1], r); te = wk[k]; X = G[te]; okx = np.isfinite(X).all(1); idx = te[okx]
            logD, logrho, _ = F.at(X[okx])
            for nome, (y, step) in alvos.items():
                s = np.arange(len(idx)) % step == 0; i = idx[s]
                conj = {"base": np.column_stack([C0[i], logrho[s]]), "+dvol": np.column_stack([C0[i], logrho[s], DV[i]]),
                        "+iv": np.column_stack([C0[i], logrho[s], IV[i]]), "+dvol+iv": np.column_stack([C0[i], logrho[s], DV[i], IV[i]])}
                for c, Cm in conj.items():
                    acc[nome][c].append(rho_parcial(logD[s], y[i], Cm))
        res["espacos"][sp] = {nome: {c: {"rho": float(np.nanmean(v)), "sd": float(np.nanstd(v)), "semanas": [round(float(x), 4) for x in v]} for c, v in d.items()} for nome, d in acc.items()}
        print(f"\n== {sp}")
        for nome in alvos:
            print(f"  {nome:7s} " + "  ".join(f"{c}: {res['espacos'][sp][nome][c]['rho']:+.4f}±{res['espacos'][sp][nome][c]['sd']:.3f}" for c in acc[nome]), flush=True)
    out = ROOT / "vol_implicita" / "resultados" / "E-VOL-01.json"; json.dump(res, open(out, "w"), indent=1); print(f"\n→ {out}")


if __name__ == "__main__":
    main()
