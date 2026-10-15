"""H-FORMA-D-02: no espaço de fluxo, a forma de D e a forma da casca mudam juntas menos no mercado real do que na nula
de pipeline? (secundária: no original, mudam juntas mais do que na nula?)

Pré-registro: PREREGISTRO_H-FORMA-D-02.md. Hashes: referencia/HASHES_H-FORMA-D-02.txt. Não editar depois do congelamento.

    python pipeline/confirmatorio_forma_casca.py --periodo exploracao     # ensaio de paridade em jun–jul/2026
    python pipeline/confirmatorio_forma_casca.py --periodo confirmatorio  # julgamento: outubro/2026
    python pipeline/confirmatorio_forma_casca.py --periodo replicacao     # replicação: novembro/2026

Medidas idênticas às de pipeline/explora_forma_D_casca.py (exploração de jun–jul e ago–set/2026):
régua gaussianizada com âncora congelada em maio; mapas a cada 240 min, janela de 1.500 min; forma de D = D̄/tr D̄
(núcleo h = 0,45, 400 estados da janela); forma da casca = Σ_mix/tr Σ_mix do GMM2 (semente 20261009 + k).
dFD, dFS = norma de Frobenius da mudança de forma entre mapas consecutivos; angD, angS = ângulo do eixo principal.

Nula de pipeline com R = 20 réplicas: retornos, sombras, volume e agressão permutados dentro de cada dia a partir do
início do período, sementes 2026 … 2045 (a réplica 0, semente 2026, é a nula da exploração).
Estatística: Δ = ρ_real − média das réplicas de ρ_nula, Spearman no mesmo mapa (j = 0).
Teste: bootstrap pareado por blocos de dia (B = 2.000, semente 20261016), os mesmos dias para o real e para as 20
réplicas; p unilateral = (1 + #{Δ* do lado contrário de 0}) / (B + 1).
"""
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
from sklearn.mixture import GaussianMixture

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "m11i")); sys.path.insert(0, str(ROOT / "vendor" / "sgv_original"))
from sgv_m11i.instrument import flow_coordinates, gaussianize, build_shell, signature  # noqa: E402
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402

H, W, SNAP, NP = 0.45, 1500, 240, 400
R_NULA, SEMENTE_NULA, B_BOOT, SEMENTE_BOOT = 20, 2026, 2000, 20261016
ALFA = 0.05
PERIODOS = {
    "exploracao": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
    "confirmatorio": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"], "2026-10-01", "2026-11-01"),
    "replicacao": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11"], "2026-11-01", "2026-12-01"),
}
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades", "taker_buy", "taker_buy_quote", "ignore"]
# (espaço, x, y, sinal registrado de Δ = real − nula)
PRIMARIA = ("flow", "dFD", "dFS", -1)
SECUNDARIAS = [("flow", "angD", "angS", -1), ("orig", "dFD", "dFS", +1)]
# Só leitura, sem veredito: D antecede a casca além da nula? (exploração: não)
LEITURA = [("flow", "dFD", "dFS", 1), ("flow", "dFD", "dFS", 2), ("orig", "dFD", "dFS", 1), ("orig", "dFD", "dFS", 2)]
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


def mapas(G, i0, i1, lr, tag, assin):
    out = []; prev = None
    for k, s in enumerate(range(i0, i1, SNAP)):
        win = G[s - W + 1:s + 1]; win = win[np.isfinite(win).all(1)]
        Db, cb = dbar(win)
        gm = GaussianMixture(2, covariance_type="full", reg_covar=1e-4, max_iter=100, n_init=2, random_state=20261009 + k).fit(win)
        mu = (gm.weights_[:, None] * gm.means_).sum(0)
        Sig = sum(w * (C + np.outer(m, m)) for w, C, m in zip(gm.weights_, gm.covariances_, gm.means_)) - np.outer(mu, mu)
        rec = {"k": k, "s": s, "FD": Db / np.trace(Db), "cbar": cb, "FS": Sig / np.trace(Sig), "d512": np.nan, "theta": np.nan,
               "vol": float(np.nanstd(lr[s - W + 1:s + 1]))}
        if assin:
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


def defasa(x, y, j):
    y = np.roll(y, -j)
    if j > 0: y[-j:] = np.nan
    if j < 0: y[:-j] = np.nan
    return x, y


def sp_rank(rx, ry):
    rx = rx - rx.mean(); ry = ry - ry.mean(); return float((rx * ry).sum() / np.sqrt((rx * rx).sum() * (ry * ry).sum()))


def contraste(real, nulas, a, b, j, days, sinal, rng):
    """Δ = ρ_real − média_r ρ_nula_r, com bootstrap pareado por dia (os mesmos dias no real e nas réplicas)."""
    xs = [defasa(s[a], s[b], j) for s in [real] + nulas]
    m = np.ones(len(days), bool)
    for x, y in xs: m &= np.isfinite(x) & np.isfinite(y)
    idx_ok = np.where(m)[0]
    rho = [float(spearmanr(x[m], y[m]).correlation) for x, y in xs]
    delta = rho[0] - float(np.mean(rho[1:]))
    ud = np.unique(days[idx_ok]); grp = [idx_ok[days[idx_ok] == d] for d in ud]; bs = np.empty(B_BOOT)
    for t in range(B_BOOT):
        ii = np.concatenate([grp[i] for i in rng.integers(0, len(grp), len(grp))])
        r = [sp_rank(rankdata(x[ii]), rankdata(y[ii])) for x, y in xs]
        bs[t] = r[0] - np.mean(r[1:])
    p = (1 + int(np.sum(sinal * bs <= 0))) / (B_BOOT + 1)
    abaixo = int(np.sum(np.array(rho[1:]) < rho[0])); acima = int(np.sum(np.array(rho[1:]) > rho[0]))
    p_rank = (1 + (abaixo if sinal < 0 else acima)) / (len(rho))  # só leitura: posto do real entre as réplicas
    return {"rho_real": round(rho[0], 4), "rho_nula_media": round(float(np.mean(rho[1:])), 4),
            "rho_nula_replicas": [round(r, 4) for r in rho[1:]], "delta": round(delta, 4),
            "ic90_delta": [round(float(np.percentile(bs, 5)), 4), round(float(np.percentile(bs, 95)), 4)],
            "ic95_delta": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
            "p_unilateral": round(p, 5), "sinal_registrado": "real < nula" if sinal < 0 else "real > nula",
            "p_posto_replicas_leitura": round(p_rank, 4), "n_mapas": int(m.sum()), "n_dias": int(len(ud))}


def holm(ps):
    o = np.argsort(ps); adj = np.empty(len(ps)); run = 0.0
    for i, k in enumerate(o): run = max(run, min(1.0, (len(ps) - i) * ps[k])); adj[k] = run
    return adj.tolist()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = PERIODOS[a.periodo]
    kl = carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp(fim, tz="UTC"), "dados além do fim do período"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    i0 = int(np.argmax((ts >= pd.Timestamp(ini, tz="UTC")).to_numpy())); i1 = len(kl)
    day = ts.dt.floor("D").to_numpy()
    lc = np.log(kl.close.values); lr = np.diff(lc, prepend=lc[0]); hi = np.log(kl.high.values) - lc; lo = lc - np.log(kl.low.values)
    lv = np.log(kl.volume.values); frac = kl.taker_buy.values / kl.volume.values
    perms = []
    for r in range(R_NULA):
        rng = np.random.default_rng(SEMENTE_NULA + r); perm = np.arange(len(kl))
        for dd in np.unique(day[i0:]):
            sel = np.where(day == dd)[0]; sel = sel[sel >= i0]; perm[sel] = rng.permutation(sel)
        perms.append(perm)

    def nula_df(perm):
        c2 = np.exp(lc[0] + np.cumsum(lr[perm]))
        return pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]), "close": c2,
                             "volume": np.exp(lv[perm]), "taker_buy": frac[perm] * np.exp(lv[perm])})

    out = {"hipotese": "H-FORMA-D-02", "periodo": a.periodo, "inicio": ini, "fim": fim, "R_nula": R_NULA, "B_boot": B_BOOT, "espacos": {}}
    S = {}
    for sp in ("flow", "orig"):
        raw = COORDS[sp](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]

        def gauss(rw):
            G = np.full_like(rw, np.nan); g = np.isfinite(rw).all(1); G[g] = gaussianize(anchor, rw[g]); return G
        M = mapas(gauss(raw), i0, i1, lr, f"{sp} real", True); real = series(M)
        days = np.array([str(ts.iloc[m["s"]].date()) for m in M])
        nulas = []
        for r, perm in enumerate(perms):
            Mn = mapas(gauss(COORDS[sp](nula_df(perm))), i0, i1, lr[perm], f"{sp} nula {r}", r == 0); nulas.append(series(Mn))
        S[sp] = (real, nulas, days)
        ser = lambda s, ks: {k: [None if not np.isfinite(v) else round(float(v), 6) for v in s[k]] for k in ks}
        out["espacos"][sp] = {"dias": days.tolist(), "serie_real": ser(real, list(real)), "serie_nula0": ser(nulas[0], list(nulas[0])),
                              "serie_nulas": [ser(n, ["dFD", "dFS", "angD", "angS"]) for n in nulas]}

    rb = np.random.default_rng(SEMENTE_BOOT)
    sp, x, y, sg = PRIMARIA; prim = contraste(S[sp][0], S[sp][1], x, y, 0, S[sp][2], sg, rb)
    prim["confirmada"] = bool(prim["p_unilateral"] < ALFA)
    sec = []
    for sp, x, y, sg in SECUNDARIAS:
        c = contraste(S[sp][0], S[sp][1], x, y, 0, S[sp][2], sg, rb); c["espaco"] = sp; c["medida"] = f"{x}×{y}@+0"; sec.append(c)
    for c, ph in zip(sec, holm([c["p_unilateral"] for c in sec])): c["p_holm"] = round(ph, 5); c["passa"] = bool(ph < ALFA)
    lei = []
    for sp, x, y, j in LEITURA:
        c = contraste(S[sp][0], S[sp][1], x, y, j, S[sp][2], +1, rb); c["espaco"] = sp; c["medida"] = f"{x}×{y}@{j:+d} (D antecede)"; lei.append(c)
    desc = {}
    for sp in ("flow", "orig"):
        real, nulas, days = S[sp]
        for xa, yb in PARES:
            for j in (-2, -1, 0, 1, 2):
                xr, yr = defasa(real[xa], real[yb], j); xn, yn = defasa(nulas[0][xa], nulas[0][yb], j)
                mr = np.isfinite(xr) & np.isfinite(yr); mn = np.isfinite(xn) & np.isfinite(yn)
                desc[f"{sp} {xa}×{yb}@{j:+d}"] = {"real": round(float(spearmanr(xr[mr], yr[mr]).correlation), 4),
                                                   "nula0": round(float(spearmanr(xn[mn], yn[mn]).correlation), 4)}
    out["primaria"] = {"espaco": "flow", "medida": "dFD×dFS@+0", **prim}
    out["secundarias_holm"] = sec; out["leitura_antecede"] = lei; out["descritivo_nula0"] = desc
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"H-FORMA-D-02_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False))

    print(f"\n== H-FORMA-D-02 [{a.periodo}: {ini} a {fim}] Δ = ρ_real − média de {R_NULA} réplicas da nula", flush=True)
    p = out["primaria"]
    vered = ("CONFIRMADA" if p["confirmada"] else "NÃO CONFIRMADA") if a.periodo != "exploracao" else \
        ("critério atingido no ensaio de jun–jul (exploração, não julga)" if p["confirmada"] else "critério não atingido no ensaio (exploração, não julga)")
    print(f"PRIMÁRIA fluxo dFD×dFS@0: real {p['rho_real']:+.3f} | nula {p['rho_nula_media']:+.3f} "
          f"[{min(p['rho_nula_replicas']):+.3f}, {max(p['rho_nula_replicas']):+.3f}] | Δ {p['delta']:+.3f} IC90 {p['ic90_delta']} "
          f"| p = {p['p_unilateral']:.4f} → {vered}", flush=True)
    for c in sec:
        print(f"secundária {c['espaco']} {c['medida']} ({c['sinal_registrado']}): real {c['rho_real']:+.3f} | nula {c['rho_nula_media']:+.3f} "
              f"| Δ {c['delta']:+.3f} | p {c['p_unilateral']:.4f} | Holm {c['p_holm']:.4f} → {'passa' if c['passa'] else 'não passa'}", flush=True)
    for c in lei:
        print(f"leitura {c['espaco']} {c['medida']}: real {c['rho_real']:+.3f} | nula {c['rho_nula_media']:+.3f} | Δ {c['delta']:+.3f} | p(real > nula) {c['p_unilateral']:.4f}", flush=True)


if __name__ == "__main__":
    main()
