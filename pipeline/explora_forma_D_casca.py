"""Exploração: a forma de D e a forma da casca mudam juntas menos no mercado real do que na nula de pipeline?

Mesma medida da exploração de jun–jul/2026 (Navegador SGV, pipeline/forma_D_casca.py), aqui num script autônomo que lê
os klines mensais da Binance (SHA-256 conferido) para poder rodar em agosto–setembro/2026 no GitHub Actions.

    python pipeline/explora_forma_D_casca.py --periodo junjul    # paridade com a exploração original
    python pipeline/explora_forma_D_casca.py --periodo agoset    # agosto–setembro/2026 (aberto em 13/10 pelo H-σRTT-01)

Régua gaussianizada com âncora congelada em maio (a mesma do H-DIF-01). Mapas a cada 240 min, janela de 1.500 min.
Em cada mapa k: forma de D = D̄/tr D̄ (tensor D médio, núcleo h = 0,45, em 400 estados da janela); forma da casca =
Σ_mix/tr Σ_mix do GMM2 (semente 20261009 + k) e assinatura M11-I (distance_512, θ) entre a casca k−1 e a k.
Mudanças entre mapas consecutivos; Spearman com defasagem j = −2..+2 (j > 0: D antecede); IC 95% por blocos de dia.
Nula de pipeline: retornos, sombras, volume e agressão permutados dentro de cada dia a partir do início do período
(semente 2026); mesmas fórmulas e mesma âncora. Grava também a série por mapa (com a vol realizada da janela) para
recortes posteriores. Nada de outubro é lido.
"""
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.mixture import GaussianMixture

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "m11i")); sys.path.insert(0, str(ROOT / "vendor" / "sgv_original"))
from sgv_m11i.instrument import flow_coordinates, gaussianize, build_shell, signature  # noqa: E402
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402

H, W, SNAP, NP = 0.45, 1500, 240, 400
PERIODOS = {"junjul": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
            "agoset": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "2026-08-01", "2026-10-01")}
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades", "taker_buy", "taker_buy_quote", "ignore"]
PARES = [("dFD", "dFS"), ("dFD", "d512"), ("angD", "angS"), ("angD", "theta"), ("dcbar", "d512")]


def sha_esperado(nome, dados):
    chk = dados / (nome + ".CHECKSUM")
    if chk.exists(): return chk.read_text().split()[0]
    for linha in (dados / "SHA256SUMS").read_text().splitlines():
        if linha.strip() and linha.split()[1].lstrip("*") == nome: return linha.split()[0]
    sys.exit(f"Sem SHA-256 para {nome}")


def carregar(meses, dados):
    partes = []
    for m in meses:
        nome = f"BTCUSDT-1m-{m}.zip"; c = dados / nome
        if hashlib.sha256(c.read_bytes()).hexdigest() != sha_esperado(nome, dados): sys.exit(f"SHA-256 não confere: {nome}")
        with zipfile.ZipFile(c) as z: df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
        if df.open_time.iloc[0] > 1e14: df["open_time"] //= 1000
        partes.append(df); print(f"{nome}: SHA-256 conferido", flush=True)
    df = pd.concat(partes, ignore_index=True); df["timestamp"] = df.open_time.astype("int64")
    if (np.diff(df.timestamp.values) != 60000).any(): sys.exit("Série com buracos ou duplicatas")
    return df[["timestamp", "open", "high", "low", "close", "volume", "taker_buy"]].astype({c: float for c in ("open", "high", "low", "close", "volume", "taker_buy")}).reset_index(drop=True)


def coords_orig(df):
    raw = pd.DataFrame({"timestamp": df["timestamp"].to_numpy(), "datetime": pd.to_datetime(df["timestamp"], unit="ms", utc=True).astype(str).to_numpy()})
    for c in ("open", "high", "low", "close", "volume"): raw[c] = pd.to_numeric(df[c]).to_numpy()
    inp = build_btc_90d_input_sgv(raw, SGVConfig()); e = inp["E_norm"]; mf = e.ewm(alpha=0.05, adjust=False).mean().diff()
    return np.column_stack((e.to_numpy(), inp["jerk"].to_numpy(), mf.to_numpy()))


COORDS = {"flow": lambda df: flow_coordinates(df[["timestamp", "close", "volume", "taker_buy"]]), "orig": coords_orig}


def dbar(win):
    X = win[:-1]; S = win[1:] - win[:-1]; ok = np.isfinite(X).all(1) & np.isfinite(S).all(1); X, S = X[ok], S[ok]
    P = X[np.linspace(0, len(X) - 1, NP).astype(int)]
    d2 = (P ** 2).sum(1)[:, None] + (X ** 2).sum(1)[None, :] - 2 * P @ X.T
    w = np.exp(-0.5 * np.maximum(d2, 0) / H ** 2); sw = w.sum(1)
    SS = (S[:, :, None] * S[:, None, :]).reshape(len(S), 9)
    mu = (w @ S) / sw[:, None]; D = ((w @ SS) / sw[:, None]).reshape(-1, 3, 3) - mu[:, :, None] * mu[:, None, :]
    d = np.maximum(np.einsum("nii->ni", D), 1e-12); tr = d.sum(1)
    return D.mean(0), float((np.log(tr / 3) - np.log(d).mean(1)).mean())


def mapas(G, i0, i1, lr, tag):
    out = []; prev = None
    for k, s in enumerate(range(i0, i1, SNAP)):
        win = G[s - W + 1:s + 1]; win = win[np.isfinite(win).all(1)]
        Db, cb = dbar(win)
        gm = GaussianMixture(2, covariance_type="full", reg_covar=1e-4, max_iter=100, n_init=2, random_state=20261009 + k).fit(win)
        mu = (gm.weights_[:, None] * gm.means_).sum(0)
        Sig = sum(w * (C + np.outer(m, m)) for w, C, m in zip(gm.weights_, gm.covariances_, gm.means_)) - np.outer(mu, mu)
        rec = {"k": k, "s": s, "FD": Db / np.trace(Db), "cbar": cb, "FS": Sig / np.trace(Sig), "d512": np.nan, "theta": np.nan,
               "vol": float(np.nanstd(lr[s - W + 1:s + 1]))}
        try:
            sh = build_shell(win, seed=20261009 + k)
            if prev is not None:
                sg = signature(prev, sh, seed=20261009 + 7 * k)
                rec["d512"] = np.nan if sg.get("distance_512") is None else float(sg["distance_512"])
                rec["theta"] = np.nan if sg.get("theta_deg") is None else float(sg["theta_deg"])
            prev = sh
        except Exception:
            prev = None
        out.append(rec)
        if k % 60 == 0: print(f"  [{tag}] mapa {k}", flush=True)
    return out


def ang(a, b):
    va = np.linalg.eigh(a)[1][:, -1]; vb = np.linalg.eigh(b)[1][:, -1]
    return float(np.degrees(np.arccos(min(1.0, abs(va @ vb)))))


def series(M):
    n = len(M); s = {k: np.full(n, np.nan) for k in ("dFD", "angD", "dcbar", "dFS", "angS", "d512", "theta")}
    for k in range(1, n):
        a, b = M[k - 1], M[k]
        s["dFD"][k] = np.linalg.norm(b["FD"] - a["FD"]); s["angD"][k] = ang(a["FD"], b["FD"]); s["dcbar"][k] = abs(b["cbar"] - a["cbar"])
        s["dFS"][k] = np.linalg.norm(b["FS"] - a["FS"]); s["angS"][k] = ang(a["FS"], b["FS"]); s["d512"][k] = b["d512"]; s["theta"][k] = b["theta"]
    s["vol"] = np.array([m["vol"] for m in M])
    return s


def lagcorr(s, days, rng, B=1000):
    out = {}
    for a, b in PARES:
        for j in (-2, -1, 0, 1, 2):
            x = s[a]; y = np.roll(s[b], -j)
            if j > 0: y[-j:] = np.nan
            if j < 0: y[:-j] = np.nan
            m = np.isfinite(x) & np.isfinite(y)
            r = float(spearmanr(x[m], y[m]).correlation)
            ud = np.unique(days[m]); grp = [np.where(m & (days == d))[0] for d in ud]; bs = []
            for _ in range(B):
                idx = np.concatenate([grp[i] for i in rng.integers(0, len(grp), len(grp))])
                bs.append(spearmanr(x[idx], y[idx]).correlation)
            out[f"{a}×{b}@{j:+d}"] = {"rho": round(r, 3), "ic95": [round(float(np.nanpercentile(bs, 2.5)), 3), round(float(np.nanpercentile(bs, 97.5)), 3)]}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = PERIODOS[a.periodo]
    kl = carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp(fim, tz="UTC")
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    i0 = int(np.argmax((ts >= pd.Timestamp(ini, tz="UTC")).to_numpy())); i1 = len(kl)
    rng = np.random.default_rng(2026); day = ts.dt.floor("D").to_numpy(); perm = np.arange(len(kl))
    for dd in np.unique(day[i0:]):
        sel = np.where(day == dd)[0]; sel = sel[sel >= i0]; perm[sel] = rng.permutation(sel)
    lc = np.log(kl.close.values); lr = np.diff(lc, prepend=lc[0]); hi = np.log(kl.high.values) - lc; lo = lc - np.log(kl.low.values)
    lv = np.log(kl.volume.values); frac = kl.taker_buy.values / kl.volume.values; c2 = np.exp(lc[0] + np.cumsum(lr[perm]))
    kln = pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]), "close": c2,
                        "volume": np.exp(lv[perm]), "taker_buy": frac[perm] * np.exp(lv[perm])})
    out = {"periodo": a.periodo, "inicio": ini, "fim": fim, "espacos": {}}; rb = np.random.default_rng(20261015)
    for sp in ("flow", "orig"):
        raw = COORDS[sp](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]
        def gauss(rw):
            G = np.full_like(rw, np.nan); g = np.isfinite(rw).all(1); G[g] = gaussianize(anchor, rw[g]); return G
        res = {}
        for tag, G, lrr in (("real", gauss(raw), lr), ("nula", gauss(COORDS[sp](kln)), lr[perm])):
            M = mapas(G, i0, i1, lrr, f"{sp} {tag}"); s = series(M)
            days = np.array([str(ts.iloc[m["s"]].date()) for m in M])
            res[tag] = {"lags": lagcorr(s, days, rb), "serie": {k: [None if not np.isfinite(v) else round(float(v), 6) for v in s[k]] for k in s},
                        "dias": days.tolist()}
        out["espacos"][sp] = res
        print(f"\n== {sp} [{a.periodo}] Spearman de Δforma(D)_k com Δforma(casca)_(k+j); j > 0: D antecede", flush=True)
        for key in res["real"]["lags"]:
            r, n = res["real"]["lags"][key], res["nula"]["lags"][key]
            print(f"  {key:>18}: real {r['rho']:+.3f} [{r['ic95'][0]:+.3f}, {r['ic95'][1]:+.3f}] | nula {n['rho']:+.3f} [{n['ic95'][0]:+.3f}, {n['ic95'][1]:+.3f}]", flush=True)
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"forma_D_casca_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
