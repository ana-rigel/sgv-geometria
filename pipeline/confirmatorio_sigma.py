"""H-σRTT-01 — confirmatório do excesso de σ da régua no espaço original do SGV.

Pergunta: no espaço (E_norm, jerk, memory_flux) do sgv_original, o giro σ da régua
RTT do mercado real fica acima do que a mesma régua mede quando a direção de cada
retorno é sorteada (mesmos |retornos|, mesma ordem, mesmo agrupamento de vol)?

Uso:
    python pipeline/confirmatorio_sigma.py --periodo exploracao     # ensaio em jun–jul/2026
    python pipeline/confirmatorio_sigma.py --periodo confirmatorio  # julgamento em ago–set/2026

Tudo o que define o teste está congelado neste arquivo (ver PREREGISTRO_H-sigmaRTT-01.md):
  coordenadas  sgv_original ac6b986: E_norm do construtor do input, jerk, memory_flux = Δ EMA_0,05(E_norm)
  âncora       gaussianização por postos com âncora de maio/2026 (fixa)
  régua        20 nós ajustados em maio/2026 (KMeans, random_state=0), janela 1.440 min, σ com a = 0,5
  família confirmatória (m = 2, Holm, α familiar = 0,05), estatística por dia d:
    H1  e_d = σ_real,d − média de K=20 réplicas de sinais sorteados
        (excesso além do agrupamento de vol)
    H2  e_d = σ_real,d − σ do mesmo dia tocado de trás para frente
        (flecha do tempo na sequência de retornos)
    D = média de e_d; p unilateral (D > 0) por bootstrap circular em blocos de 3 dias (B=20.000)
  descritivos  mesmo teste contra a pipeline (minutos permutados no dia, K=20);
               fração de dias com real > máx de 8 réplicas de sinais
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "m11i"))
sys.path.insert(0, str(ROOT / "vendor" / "sgv_original"))
sys.path.insert(0, str(ROOT / "pipeline"))
from sgv_m11i.instrument import gaussianize  # noqa: E402
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402
from sgv_rtt_operator import TopologyGraphOperator, entropy_production, transition_counts  # noqa: E402

N_NODES, W_RULER, K_FLIP, K_PIPE, K_MAX = 20, 1440, 20, 20, 8
BLOCK, B_BOOT, ALPHA = 3, 20000, 0.05
SEED = 20261013
PERIODOS = {
    "exploracao": {"meses": ["2026-05", "2026-06", "2026-07"], "inicio": "2026-06-01", "fim": "2026-08-01"},
    "confirmatorio": {"meses": ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "inicio": "2026-08-01", "fim": "2026-10-01"},
}
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trades", "taker_buy", "taker_buy_quote", "ignore"]


def sha_esperado(nome):
    chk = ROOT / "dados" / (nome + ".CHECKSUM")
    if chk.exists():
        return chk.read_text().split()[0]
    for linha in (ROOT / "dados" / "SHA256SUMS").read_text().splitlines():
        if linha.strip() and linha.split()[1].lstrip("*") == nome:
            return linha.split()[0]
    sys.exit(f"Sem SHA-256 publicado para {nome}: coloque {nome}.CHECKSUM (da Binance) em dados/")


def carregar(meses):
    partes = []
    for m in meses:
        nome = f"BTCUSDT-1m-{m}.zip"
        caminho = ROOT / "dados" / nome
        if not caminho.exists():
            sys.exit(f"Falta dados/{nome}")
        h = hashlib.sha256(caminho.read_bytes()).hexdigest()
        if h != sha_esperado(nome):
            sys.exit(f"SHA-256 não confere: {nome}")
        with zipfile.ZipFile(caminho) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
        if df.open_time.iloc[0] > 1e14:
            df["open_time"] //= 1000
        partes.append(df)
        print(f"{nome}: SHA-256 conferido")
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
    inp = build_btc_90d_input_sgv(raw, SGVConfig())
    assert len(inp) == len(df)
    e = inp["E_norm"]
    mf = e.ewm(alpha=0.05, adjust=False).mean().diff()
    return np.column_stack((e.to_numpy(), inp["jerk"].to_numpy(), mf.to_numpy()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periodo", choices=list(PERIODOS), required=True)
    a = ap.parse_args()
    P = PERIODOS[a.periodo]
    kl = carregar(P["meses"])
    ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    i0 = int(np.argmax((ts >= pd.Timestamp(P["inicio"], tz="UTC")).to_numpy()))
    i1 = int(np.argmax((ts >= pd.Timestamp(P["fim"], tz="UTC")).to_numpy())) if ts.iloc[-1] >= pd.Timestamp(P["fim"], tz="UTC") else len(kl)
    assert i1 == len(kl), "o período avaliado deve terminar no fim dos dados carregados"
    day = ts.dt.floor("D").to_numpy()

    raw_real = coords(kl)
    ok = np.isfinite(raw_real).all(1)
    anchor = raw_real[may & ok]

    def gauss(raw):
        G = np.full_like(raw, np.nan)
        g = np.isfinite(raw).all(1)
        G[g] = gaussianize(anchor, raw[g])
        return G

    G_real = gauss(raw_real)
    op = TopologyGraphOperator(n_nodes=N_NODES, window_size=W_RULER).fit_codebook(G_real[may & ok])

    def daily_sigma(G):
        nodes = np.zeros(len(G), dtype=int)
        g = np.isfinite(G).all(1)
        nodes[g] = op.predict_node(G[g])
        counts = transition_counts(nodes[i0 - W_RULER - 1: i0], N_NODES)
        sig = np.empty(len(G) - i0)
        for n_, t in enumerate(range(i0, len(G))):
            counts[nodes[t - 1], nodes[t]] += 1
            counts[nodes[t - W_RULER - 1], nodes[t - W_RULER]] -= 1
            sig[n_] = entropy_production(counts, op.sigma_pseudocount)
        return pd.Series(sig).groupby(day[i0:]).mean()

    r = np.log(kl.close.values)
    lr = np.diff(r, prepend=r[0])

    def from_returns(lr2):
        close = np.exp(r[0] + np.cumsum(lr2))
        df = kl.copy()
        df["close"] = close
        df["open"] = df["high"] = df["low"] = close
        return gauss(coords(df))

    rng = np.random.default_rng(SEED)
    s_real = daily_sigma(G_real)
    dias = [str(d)[:10] for d in s_real.index]
    print(f"σ real calculado para {len(dias)} dias ({dias[0]} a {dias[-1]})", flush=True)

    flips = []
    for k in range(K_FLIP):
        lr2 = lr.copy()
        lr2[i0:] = lr[i0:] * rng.choice([-1.0, 1.0], size=len(lr) - i0)
        flips.append(daily_sigma(from_returns(lr2)).values)
        print(f"sinais sorteados {k + 1}/{K_FLIP}", end="\r", flush=True)
    flips = np.vstack(flips)

    pipes = []
    days_eval = np.unique(day[i0:])
    for k in range(K_PIPE):
        perm = np.arange(len(kl))
        for d_ in days_eval:
            sel = np.where(day == d_)[0]
            sel = sel[sel >= i0]
            perm[sel] = rng.permutation(sel)
        pipes.append(daily_sigma(from_returns(lr[perm])).values)
        print(f"pipeline {k + 1}/{K_PIPE}      ", end="\r", flush=True)
    pipes = np.vstack(pipes)

    lr3 = lr.copy()
    for d_ in days_eval:
        sel = np.where(day == d_)[0]
        sel = sel[sel >= i0]
        lr3[sel] = lr[sel][::-1]
    rev = daily_sigma(from_returns(lr3)).values
    print()

    def boot_p(e):
        """p unilateral de média(e) > 0, bootstrap circular em blocos (série centrada)."""
        e = np.asarray(e, float)
        n = len(e)
        D = e.mean()
        c = e - D
        nb = int(np.ceil(n / BLOCK))
        brng = np.random.default_rng(SEED + 1)
        starts = brng.integers(0, n, size=(B_BOOT, nb))
        idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n
        means = c[idx.reshape(B_BOOT, -1)[:, :n]].mean(1)
        return float((1 + (means >= D).sum()) / (B_BOOT + 1)), float(D)

    real = s_real.values
    e_flip = real - flips.mean(0)
    p_flip, D_flip = boot_p(e_flip)
    p_pipe, D_pipe = boot_p(real - pipes.mean(0))
    p_rev, D_rev = boot_p(real - rev)
    above = float((real > flips[:K_MAX].max(0)).mean())

    # Holm com m = 2
    ps = {"H1": p_flip, "H2": p_rev}
    ordem = sorted(ps, key=ps.get)
    conf, ainda = {}, True
    for j, h in enumerate(ordem):
        ainda = ainda and ps[h] < ALPHA / (2 - j)
        conf[h] = bool(ainda)
    res = {
        "hipotese": "H-sigmaRTT-01", "periodo": a.periodo, "dias": dias, "n_dias": len(dias),
        "familia": {"H1_sinais": {"D": D_flip, "p": p_flip, "confirmado": conf["H1"],
                                  "sd_diario": float(e_flip.std(ddof=1)), "autocorr_lag1": float(pd.Series(e_flip).autocorr(1))},
                    "H2_invertido": {"D": D_rev, "p": p_rev, "confirmado": conf["H2"],
                                     "sd_diario": float((real - rev).std(ddof=1)), "autocorr_lag1": float(pd.Series(real - rev).autocorr(1))},
                    "metodo": "Holm m=2, alfa familiar 0,05, bootstrap circular em blocos de 3 dias, unilateral"},
        "descritivos": {"D_pipeline": D_pipe, "p_pipeline": p_pipe,
                        "frac_dias_real_acima_max_8_sinais": above},
        "medias": {"real": float(real.mean()), "sinais": float(flips.mean()), "pipeline": float(pipes.mean()),
                   "invertido": float(rev.mean())},
        "series": {"real": np.round(real, 5).tolist(), "sinais_media": np.round(flips.mean(0), 5).tolist(),
                   "pipeline_media": np.round(pipes.mean(0), 5).tolist(), "invertido": np.round(rev, 5).tolist()},
    }
    out = ROOT / "resultados" / f"H-sigmaRTT-01_{a.periodo}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    f = res["familia"]
    print(f"\nH-σRTT-01 [{a.periodo}] {len(dias)} dias (Holm, m = 2, α = 0,05)")
    for h, rot in (("H1_sinais", "H1 real − sinais sorteados"), ("H2_invertido", "H2 real − dia invertido")):
        print(f"  {rot}: D = {f[h]['D']:+.4f}, p = {f[h]['p']:.4f} → " + ("CONFIRMADA" if f[h]["confirmado"] else "NÃO confirmada"))
    s = res["descritivos"]
    print(f"  (descritivo) real − pipeline: D = {s['D_pipeline']:+.4f}, p = {s['p_pipeline']:.4f}")
    print(f"  (descritivo) dias com real > máx de 8 réplicas de sinais: {s['frac_dias_real_acima_max_8_sinais']:.1%} (acaso ≈ 11,1%)")
    print(f"  resultado gravado em {out}")


if __name__ == "__main__":
    main()
