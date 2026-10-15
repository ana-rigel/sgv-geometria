"""H-CASCA-01 — a feature de caudas das cascas (HDR95 − HDR50) acompanha a cauda real dos retornos. Código congelado.

    python pipeline/confirmatorio_casca.py --paridade-btc        # BTC jun–jul: +0,638 (desenho do relatório) e +0,656 (este desenho)
    python pipeline/confirmatorio_casca.py --simbolo LTCUSDT     # julgamento: LTC jun–set/2026

Definições em PREREGISTRO_H-CASCA-01.md.
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
for p in ("vendor/sgv_original", "vendor/m11i", "vendor/u031"):
    sys.path.insert(0, str(ROOT / p))
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402
import u031_casca  # noqa: E402
from u031_casca import build_shell, hdr_mesh  # noqa: E402

u031_casca.OUTER_EXTENT = 10.0
u031_casca.OUTER_GRID = 61
W, SEED_GMM, B_PERM, SEED_PERM, SEED_NULL = 1500, 20261009, 10000, 20261015, 2026
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trades", "taker_buy", "taker_buy_quote", "ignore"]


def sha_esperado(nome):
    chk = ROOT / "dados" / (nome + ".CHECKSUM")
    if chk.exists():
        return chk.read_text().split()[0]
    for linha in (ROOT / "dados" / "SHA256SUMS").read_text().splitlines():
        if linha.strip() and linha.split()[1].lstrip("*") == nome:
            return linha.split()[0]
    sys.exit(f"Sem SHA-256 publicado para {nome}")


def carregar(simbolo, meses):
    partes = []
    for m in meses:
        nome = f"{simbolo}-1m-{m}.zip"; caminho = ROOT / "dados" / nome
        if not caminho.exists():
            sys.exit(f"Falta dados/{nome}")
        if hashlib.sha256(caminho.read_bytes()).hexdigest() != sha_esperado(nome):
            sys.exit(f"SHA-256 não confere: {nome}")
        with zipfile.ZipFile(caminho) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
        if not str(df.open_time.iloc[0]).isdigit():
            df = df.iloc[1:].astype({c: float for c in COLS[1:6]}).astype({"open_time": "int64"})
        if df.open_time.iloc[0] > 1e14:
            df["open_time"] //= 1000
        partes.append(df); print(f"{nome}: SHA-256 conferido", flush=True)
    df = pd.concat(partes, ignore_index=True)
    df["timestamp"] = df.open_time.astype("int64")
    if (np.diff(df.timestamp.values) != 60000).any():
        sys.exit("Série com buracos ou duplicatas")
    return df[["timestamp", "open", "high", "low", "close", "volume"]].reset_index(drop=True)


def coords(df):
    raw = pd.DataFrame({"timestamp": df["timestamp"].to_numpy(),
                        "datetime": pd.to_datetime(df["timestamp"], unit="ms", utc=True).astype(str).to_numpy()})
    for c in ("open", "high", "low", "close", "volume"):
        raw[c] = pd.to_numeric(df[c]).to_numpy()
    inp = build_btc_90d_input_sgv(raw, SGVConfig()); assert len(inp) == len(df)
    e = inp["E_norm"]; mf = e.ewm(alpha=0.05, adjust=False).mean().diff()
    return np.column_stack((e.to_numpy(), inp["jerk"].to_numpy(), mf.to_numpy()))


def regua(raw, may):
    ok = np.isfinite(raw).all(1); anc = raw[may & ok]
    med = np.median(anc, 0); esc = np.quantile(np.abs(anc - med), 0.995, axis=0) / 3.0
    G = np.full_like(raw, np.nan); G[ok] = (raw[ok] - med) / esc
    return G, med, esc


def nula(kl, ts, i0):
    rng = np.random.default_rng(SEED_NULL); day = ts.dt.floor("D").to_numpy(); r0 = np.log(kl.close.values)
    lr = np.diff(r0, prepend=r0[0]); hi = np.log(kl.high.values) - r0; lo = r0 - np.log(kl.low.values); perm = np.arange(len(kl))
    for d_ in np.unique(day[i0:]):
        s = np.where(day == d_)[0]; s = s[s >= i0]; perm[s] = rng.permutation(s)
    c2 = np.exp(r0[0] + np.cumsum(lr[perm])); lv = np.log(kl.volume.values.astype(float))
    return pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]),
                         "close": c2, "volume": np.exp(lv[perm])})


def mapa(G, absr, a, sementes=(SEED_GMM,)):
    """Janela [a, a+W): cascas (uma por semente), curtose de E_norm e peso da cauda de |r|."""
    X = G[a:a + W]; X = X[np.isfinite(X).all(1)]; r = absr[a:a + W]; r = r[np.isfinite(r)]
    z = (X - X.mean(0)) / X.std(0)
    m = {"kurt": float((z[:, 0] ** 4).mean() - 3), "med": float(np.median(r)), "q999": float(np.quantile(r, .999)),
         "q99": float(np.quantile(r, .99)), "max": float(r.max()), "v": []}
    for sd in sementes:
        try:
            if len(X) < 0.95 * W:
                raise ValueError("janela incompleta")
            inner = build_shell(X, seed=sd, n=25); outer, _ = hdr_mesh(inner.params, .95)
            m["v"].append((float(abs(inner.mesh.volume)), float(abs(outer.volume))))
        except Exception as e:
            m["v"].append(None); m.setdefault("erro", str(e)[:60])
    return m


def medidas(A, B, s=0):
    v50 = np.log(B["v"][s][0] / A["v"][s][0]) / 3; v95 = np.log(B["v"][s][1] / A["v"][s][1]) / 3
    return {"caudas": v95 - v50, "v50": v50, "v95": v95,
            "ref": np.log((B["q999"] / B["med"]) / (A["q999"] / A["med"])),
            "ref_q99": np.log((B["q99"] / B["med"]) / (A["q99"] / A["med"])),
            "ref_max": np.log(B["max"] / A["max"]), "ref_kurt": np.log((B["kurt"] + 3) / (A["kurt"] + 3))}


def preparar(kl, fim):
    ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may))
    G, med, esc = regua(coords(kl), may)
    absr = np.abs(np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan))
    n_fim = int(np.searchsorted(kl.timestamp.values, pd.Timestamp(fim, tz="UTC").value // 10**6))
    inicios = [i0 + k * 28 * 60 for k in range(10**4) if i0 + k * 28 * 60 + W <= n_fim]
    return G, absr, ts, i0, inicios, med, esc


def pares_disjuntos(G, absr, inicios, sementes=(SEED_GMM,)):
    M = [mapa(G, absr, a, sementes) for a in inicios]
    P = [(A, B) for A, B in zip(M[0::2], M[1::2]) if A["v"][0] and B["v"][0]]
    return M, P


def rho(P, x, y="ref", s=0):
    m = [medidas(A, B, s) for A, B in P]
    return float(spearmanr([d[x] for d in m], [d[y] for d in m])[0])


def p_perm(P):
    m = [medidas(A, B) for A, B in P]; f = np.array([d["caudas"] for d in m]); r = np.array([d["ref"] for d in m])
    obs = spearmanr(f, r)[0]; rng = np.random.default_rng(SEED_PERM)
    cnt = sum(spearmanr(f, rng.permutation(r))[0] >= obs for _ in range(B_PERM))
    return float(obs), float((cnt + 1) / (B_PERM + 1))


def paridade():
    kl = carregar("BTCUSDT", ["2026-05", "2026-06", "2026-07"])
    G, absr, ts, i0, inicios, _, _ = preparar(kl, "2026-08-01")
    # desenho do relatório: um mapa a cada 240 min desde 01/06 (janela termina no mapa), pares a 28 h = 7 mapas
    snaps = list(range(i0, len(G), 240))
    Mr = {k: mapa(G, absr, s - W) for k, s in enumerate(snaps)}
    Pr = [(Mr[k], Mr[k + 7]) for k in Mr if k + 7 in Mr and Mr[k]["v"][0] and Mr[k + 7]["v"][0]]
    _, Pd = pares_disjuntos(G, absr, inicios)
    res = {"modo": "paridade", "relatorio": {"mapas_validos": sum(bool(m["v"][0]) for m in Mr.values()), "pares": len(Pr),
                                             "rho": rho(Pr, "caudas")},
           "disjunto": {"pares": len(Pd), "rho": rho(Pd, "caudas")}}
    res["confere"] = abs(res["relatorio"]["rho"] - 0.638) < 0.01 and abs(res["disjunto"]["rho"] - 0.656) < 0.01
    return "BTCUSDT", res


def julgamento(sym):
    kl = carregar(sym, ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"])
    G, absr, ts, i0, inicios, med, esc = preparar(kl, "2026-10-01")
    sementes = tuple(SEED_GMM + i for i in range(5))
    M, P = pares_disjuntos(G, absr, inicios, sementes)
    r, p = p_perm(P)
    res = {"hipotese": "H-CASCA-01", "simbolo": sym, "modo": "julgamento",
           "regua": {"mediana_maio": med.tolist(), "escala": esc.tolist()},
           "janelas": len(M), "janelas_validas": sum(bool(m["v"][0]) for m in M), "pares_possiveis": len(M) // 2,
           "pares_validos": len(P), "rho": r, "p_permutacao": p,
           "erros": sorted({m["erro"] for m in M if "erro" in m})}
    res["secundarios"] = {"rho_curtose_E": rho(P, "caudas", "ref_kurt"), "rho_q99": rho(P, "caudas", "ref_q99"),
                          "rho_max": rho(P, "caudas", "ref_max"), "rho_so_v50": rho(P, "v50"), "rho_so_v95": rho(P, "v95")}
    F = np.array([[medidas(A, B, s)["caudas"] if A["v"][s] and B["v"][s] else np.nan for s in range(5)] for A, B in P])
    ok = np.isfinite(F).sum(1) >= 2
    res["secundarios"]["confiabilidade_sementes"] = float(1 - np.nanmean(np.nanvar(F[ok], 1)) / np.var(F[:, 0]))
    res["secundarios"]["rho_por_semente"] = [rho([pq for pq in P if pq[0]["v"][s] and pq[1]["v"][s]], "caudas", s=s) for s in range(5)]
    Gn, _, _ = regua(coords(nula(kl, ts, i0)), (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy())
    kn = nula(kl, ts, i0); absr_n = np.abs(np.diff(np.log(kn.close.values.astype(float)), prepend=np.nan))
    _, Pn = pares_disjuntos(Gn, absr_n, inicios)
    res["secundarios"]["nula_pipeline"] = {"pares": len(Pn), "rho": rho(Pn, "caudas")}
    valido = len(P) >= 25
    res["valido"] = valido
    res["veredito"] = "INCONCLUSIVO" if not valido else ("CONFIRMADA" if (p < 0.05 and r >= 0.40) else "NÃO CONFIRMADA")
    return sym, res


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--paridade-btc", action="store_true"); g.add_argument("--simbolo")
    a = ap.parse_args()
    sym, res = paridade() if a.paridade_btc else julgamento(a.simbolo)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    out = ROOT / "resultados" / f"H-CASCA-01_{sym}_{res['modo']}.json"; out.parent.mkdir(exist_ok=True)
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if a.paridade_btc and not res["confere"]:
        sys.exit("Paridade falhou")


if __name__ == "__main__":
    main()
