"""Confirmatório H-DIF-01 (campo de difusão) e H-DIR-01 (direção) — código congelado.

    python pipeline/confirmatorio_dif.py --periodo exploracao     # ensaio de paridade em jun–jul/2026
    python pipeline/confirmatorio_dif.py --periodo confirmatorio  # julgamento em outubro/2026

Tudo que importa está em PREREGISTRO_H-DIF-01.md. Resumo:

H-DIF-01 (família m = 2, Holm, α = 0,05), um teste por espaço:
    log tr D(x_t), estimado por núcleo (h = 0,45) na semana anterior e avaliado no estado atual, tem correlação
    parcial de Spearman com log Range_{t+5} além dos controles fortes (σ 10/30/60 min, HAR 1 dia e 1 semana,
    retornos com sinal 5 e 30 min, log-volume 10 e 60 min, hora) e de log ρ(x_t):
        H-DIF-01/fluxo:    ρ_parcial < 0   (espaço (z, ι, ν))
        H-DIF-01/original: ρ_parcial > 0   (espaço (E_norm, jerk, memory_flux))
H-DIR-01 (família m = 2, Holm, α = 0,05), um teste por espaço, expectativa registrada: NULO:
    μ_r(x_t) = E[r_{t+1} | x] estimado na semana anterior tem correlação parcial de Spearman com o retorno
    com sinal dos 15 min seguintes além dos controles (retornos 5/30 min, σ 10/30/60, hora, ι de 5 min):
        bilateral, nos dois espaços.
Estatística: ρ parcial por semana fora da amostra (semana k testa com o campo da semana k−1); janelas não
sobrepostas de 5 min (H-DIF) e 15 min (H-DIR). p primário: permutação em blocos de dia dos pares de resíduos em
postos (os resíduos de cada semana ficam centrados na própria semana; o alvo é permutado dentro de cada dia,
B = 5.000, semente fixa), unilateral no sinal registrado (bilateral para H-DIR). p secundário (informativo, e
anti-conservador com poucas semanas): bootstrap sobre a série de ρ semanais (B = 20.000).
Nula de pipeline (retornos, sombras, agressão e volume de cada dia permutados, mesmas fórmulas, semente 2026):
só para leitura, não entra no julgamento.
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "m11i"))
sys.path.insert(0, str(ROOT / "vendor" / "sgv_original"))
from sgv_m11i.instrument import flow_coordinates, gaussianize  # noqa: E402
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402

H, HMIN, ALPHA, B_BOOT, B_PERM = 0.45, 30.0, 0.05, 20000, 5000
SEED_NULL, SEED_BOOT = 2026, 20261013
PERIODOS = {
    "exploracao": {"meses": ["2026-05", "2026-06", "2026-07"], "inicio": "2026-06-01", "fim": "2026-08-01", "treino0": "2026-06-01"},
    # outubro: a primeira semana julgada (1–8/10) usa o campo de 24/9–1/10 (setembro já aberto por H-σRTT-01);
    # ago–set entram só como aquecimento dos filtros causais (HAR semanal, EMA do E_norm) e campo da semana 0.
    "confirmatorio": {"meses": ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"], "inicio": "2026-10-01", "fim": "2026-11-01", "treino0": "2026-09-24"},
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
        nome = f"BTCUSDT-1m-{m}.zip"; caminho = ROOT / "dados" / nome
        if not caminho.exists():
            sys.exit(f"Falta dados/{nome}")
        if hashlib.sha256(caminho.read_bytes()).hexdigest() != sha_esperado(nome):
            sys.exit(f"SHA-256 não confere: {nome}")
        with zipfile.ZipFile(caminho) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
        if df.open_time.iloc[0] > 1e14:
            df["open_time"] //= 1000
        partes.append(df); print(f"{nome}: SHA-256 conferido")
    df = pd.concat(partes, ignore_index=True)
    df["timestamp"] = df.open_time.astype("int64")
    if (np.diff(df.timestamp.values) != 60000).any():
        sys.exit("Série com buracos ou duplicatas")
    return df[["timestamp", "open", "high", "low", "close", "volume", "taker_buy"]].reset_index(drop=True)


def coords_orig(df):
    raw = pd.DataFrame({"timestamp": df["timestamp"].to_numpy(),
                        "datetime": pd.to_datetime(df["timestamp"], unit="ms", utc=True).astype(str).to_numpy()})
    for c in ("open", "high", "low", "close", "volume"):
        raw[c] = pd.to_numeric(df[c]).to_numpy()
    inp = build_btc_90d_input_sgv(raw, SGVConfig()); assert len(inp) == len(df)
    e = inp["E_norm"]; mf = e.ewm(alpha=0.05, adjust=False).mean().diff()
    return np.column_stack((e.to_numpy(), inp["jerk"].to_numpy(), mf.to_numpy()))


def coords_flow(df):
    return flow_coordinates(df[["timestamp", "close", "volume", "taker_buy"]])


COORDS = {"flow": coords_flow, "orig": coords_orig}


def kernel_w(X, P):
    d2 = (P ** 2).sum(1)[:, None] + (X ** 2).sum(1)[None, :] - 2 * P @ X.T
    return np.exp(-0.5 * np.maximum(d2, 0) / H ** 2)


class Campo:
    """Estatísticas por núcleo da semana de treino: tr D, log ρ, μ_r."""
    def __init__(self, G, sel, r):
        X = G[sel[:-1]]; S = G[sel[1:]] - G[sel[:-1]]; rn = r[sel[:-1] + 1]
        ok = np.isfinite(X).all(1) & np.isfinite(S).all(1) & np.isfinite(rn)
        self.X, self.S, self.r = X[ok], S[ok], rn[ok]; self.S2 = (self.S ** 2).sum(1)

    def at(self, P):
        trD = np.zeros(len(P)); logrho = np.zeros(len(P)); mu_r = np.zeros(len(P))
        for a in range(0, len(P), 1500):
            W = kernel_w(self.X, P[a:a + 1500]); n = np.maximum(W.sum(1), 1e-12)
            mu = (W @ self.S) / n[:, None]
            trD[a:a + 1500] = (W @ self.S2) / n - (mu ** 2).sum(1)
            logrho[a:a + 1500] = np.log(n / len(self.X) + 1e-12)
            mu_r[a:a + 1500] = (W @ self.r) / n
        return np.log(np.maximum(trD, 1e-9)), logrho, mu_r


def residuos(x, y, C):
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(C).all(1)
    xr = stats.rankdata(x[ok]); yr = stats.rankdata(y[ok]); A = C[ok]
    xr = xr - A @ np.linalg.lstsq(A, xr, rcond=None)[0]; yr = yr - A @ np.linalg.lstsq(A, yr, rcond=None)[0]
    return xr, yr, ok


def rho_parcial(x, y, C):
    xr, yr, _ = residuos(x, y, C)
    return float(stats.spearmanr(xr, yr)[0]) if len(xr) >= 200 else np.nan


def semanas(ts, treino0, inicio, fim):
    """Semanas de 7 dias a partir de treino0; a primeira é só treino. Semanas incompletas (< 5 dias) no fim ficam de fora."""
    out = []; s = pd.Timestamp(treino0, tz="UTC"); fim = pd.Timestamp(fim, tz="UTC")
    while s < fim:
        e = min(s + pd.Timedelta(days=7), fim)
        if e - s < pd.Timedelta(days=5):
            break
        out.append(np.where((ts >= s).to_numpy() & (ts < e).to_numpy())[0]); s = e
    assert ts.iloc[out[0][0]] == pd.Timestamp(treino0, tz="UTC") and ts.iloc[out[1][0]] >= pd.Timestamp(inicio, tz="UTC")
    return out


def analisar(G, kl, ts, wk, label, hour_d):
    close, high, low, vol, tk = (kl[c].values.astype(float) for c in ("close", "high", "low", "volume", "taker_buy"))
    lc, hi, lo = np.log(close), np.log(high), np.log(low); n = len(lc)
    r = np.diff(lc, prepend=np.nan); rs = pd.Series(r)
    rng5 = np.full(n, np.nan)
    for t in range(n - 5):
        rng5[t] = hi[t + 1:t + 6].max() - lo[t + 1:t + 6].min()
    y_dif = np.log(rng5 + 1e-9)
    y_dir = np.full(n, np.nan); y_dir[:-15] = lc[15:] - lc[:-15]
    lvol = pd.Series(np.log(vol))
    sig = [np.log(rs.rolling(w).std() + 1e-9) for w in (10, 30, 60)]
    C_dif = np.column_stack([np.ones(n)] + sig + [
        np.log(rs.rolling(1440, min_periods=720).std() + 1e-9), np.log(rs.rolling(10080, min_periods=2880).std() + 1e-9),
        rs.rolling(5).sum(), rs.rolling(30).sum(), lvol.rolling(10).mean(), lvol.rolling(60).mean(), hour_d])
    iota5 = pd.Series(np.clip(2 * tk / vol - 1, -1, 1)).rolling(5).mean().to_numpy()
    C_dir = np.column_stack([np.ones(n), rs.rolling(5).sum(), rs.rolling(30).sum()] + sig + [hour_d, iota5])
    semanal = {"dif": [], "dir": []}; pares = {"dif": ([], [], []), "dir": ([], [], [])}
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        F = Campo(G, tr, r)
        X = G[te]; okx = np.isfinite(X).all(1); idx = te[okx]
        logD, logrho, mu_r = F.at(X[okx])
        s5 = np.arange(len(idx)) % 5 == 0; s15 = np.arange(len(idx)) % 15 == 0
        Cd = np.column_stack([C_dif[idx], logrho])
        semanal["dif"].append(rho_parcial(logD[s5], y_dif[idx][s5], Cd[s5]))
        semanal["dir"].append(rho_parcial(mu_r[s15], y_dir[idx][s15], C_dir[idx][s15]))
        for nome, x, y, C, s in (("dif", logD, y_dif[idx], Cd, s5), ("dir", mu_r, y_dir[idx], C_dir[idx], s15)):
            xr, yr, ok = residuos(x[s], y[s], C[s]); d = ts.dt.floor("D").to_numpy()[idx][s][ok]
            pares[nome][0].append(xr); pares[nome][1].append(yr); pares[nome][2].append(d)
    out = {}
    for nome in ("dif", "dir"):
        v = np.array(semanal[nome], float)
        out[nome] = {"rho_semanal": [round(float(x), 4) for x in v], "rho_media": float(np.nanmean(v)), "n_semanas": int(np.isfinite(v).sum()),
                     "pares": tuple(np.concatenate(p) for p in pares[nome])}
    print(label.ljust(9), " ".join(f"{nome}: ρ̄ {out[nome]['rho_media']:+.4f} semanas {out[nome]['rho_semanal']}" for nome in ("dif", "dir")), flush=True)
    return out


def p_semanas(v, sinal, rng):
    """Bootstrap sobre as semanas: fração de reamostras com média do lado contrário (sinal=0: bilateral)."""
    v = v[np.isfinite(v)]; m = rng.choice(v, size=(B_BOOT, len(v)), replace=True).mean(1)
    if sinal > 0: return float((m <= 0).mean())
    if sinal < 0: return float((m >= 0).mean())
    return float(2 * min((m <= 0).mean(), (m >= 0).mean()))


def p_blocos(xr, yr, dias, sinal, rng):
    """Bootstrap circular em blocos de dia sobre os pares de resíduos: reamostra dias, recalcula ρ de Spearman."""
    ud = np.unique(dias); grp = {d: np.where(dias == d)[0] for d in ud}; obs = stats.spearmanr(xr, yr)[0]
    # ρ sob a hipótese nula: centrado ao reembaralhar o par dentro de cada dia (quebra a ligação x–y, preserva o bloco)
    rr = np.empty(B_PERM)
    for b in range(B_PERM):
        yp = yr.copy()
        for d in ud: yp[grp[d]] = yr[rng.permutation(grp[d])]
        rr[b] = stats.spearmanr(xr, yp)[0]
    if sinal > 0: return float((rr >= obs).mean()), float(obs)
    if sinal < 0: return float((rr <= obs).mean()), float(obs)
    return float((np.abs(rr) >= abs(obs)).mean()), float(obs)


def holm(ps):
    ordem = np.argsort(ps); adj = np.empty(len(ps)); run = 0.0
    for i, j in enumerate(ordem):
        run = max(run, (len(ps) - i) * ps[j]); adj[j] = min(run, 1.0)
    return adj


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True)
    a = ap.parse_args(); P = PERIODOS[a.periodo]
    kl = carregar(P["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp(P["fim"], tz="UTC") and ts.iloc[-1] >= pd.Timestamp(P["inicio"], tz="UTC") + pd.Timedelta(days=5)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    i_av = int(np.argmax((ts >= pd.Timestamp(P["inicio"], tz="UTC")).to_numpy()))
    wk = semanas(ts, P["treino0"], P["inicio"], P["fim"])
    hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
    rng_null = np.random.default_rng(SEED_NULL); rng_boot = np.random.default_rng(SEED_BOOT)
    # nula de pipeline: permuta dentro de cada dia a partir do início do período avaliado (treino da semana 0 incluído)
    i_perm = wk[0][0]; day = ts.dt.floor("D").to_numpy(); perm = np.arange(len(kl))
    for d in np.unique(day[i_perm:]):
        s = np.where(day == d)[0]; s = s[s >= i_perm]; perm[s] = rng_null.permutation(s)
    lc = np.log(kl.close.values); lr = np.diff(lc, prepend=lc[0]); hi = np.log(kl.high.values) - lc; lo = lc - np.log(kl.low.values)
    lv = np.log(kl.volume.values.astype(float)); frac = kl.taker_buy.values / kl.volume.values
    c2 = np.exp(lc[0] + np.cumsum(lr[perm]))
    kl_null = pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]),
                            "close": c2, "volume": np.exp(lv[perm]), "taker_buy": frac[perm] * np.exp(lv[perm])})
    resultado = {"hipoteses": ["H-DIF-01", "H-DIR-01"], "periodo": a.periodo, "semanas_julgadas": [str(ts.iloc[w[0]].date()) for w in wk[1:]],
                 "n_minutos_avaliados": int(len(kl) - i_av), "congelado": {"h": H, "n_eff_min": HMIN, "alpha": ALPHA, "B_boot": B_BOOT,
                 "seed_null": SEED_NULL, "seed_boot": SEED_BOOT, "B_perm": B_PERM, "p_primario": "permutacao_blocos_dia", "controles_dif": "σ10/30/60, HAR 1d/1s, r5/r30, logvol10/60, hora, logρ",
                 "controles_dir": "r5/r30, σ10/30/60, hora, ι5"}, "espacos": {}}
    sinais = {"dif": {"flow": -1, "orig": +1}, "dir": {"flow": 0, "orig": 0}}
    for sp in ("flow", "orig"):
        raw = COORDS[sp](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]

        def gauss(rw):
            G = np.full_like(rw, np.nan); g = np.isfinite(rw).all(1); G[g] = gaussianize(anchor, rw[g]); return G

        print(f"\n== espaço {sp}")
        real = analisar(gauss(raw), kl, ts, wk, "real", hour_d)
        nulo = analisar(gauss(COORDS[sp](kl_null)), kl_null, ts, wk, "pipeline", hour_d)
        resultado["espacos"][sp] = {}
        for nome in ("dif", "dir"):
            sg = sinais[nome][sp]; v = np.array(real[nome]["rho_semanal"], float)
            p2 = p_semanas(v, sg, rng_boot); p1, rho_pool = p_blocos(*real[nome]["pares"], sg, rng_boot)
            resultado["espacos"][sp][nome] = {"sinal_esperado": sg, "rho_semanal": real[nome]["rho_semanal"], "rho_media": real[nome]["rho_media"],
                                              "rho_agrupado": rho_pool, "p_blocos_dia": p1, "p_semanas_secundario": p2,
                                              "nula_pipeline": {"rho_semanal": nulo[nome]["rho_semanal"], "rho_media": nulo[nome]["rho_media"]}}
    for nome, hip in (("dif", "H-DIF-01"), ("dir", "H-DIR-01")):
        ps = np.array([resultado["espacos"][sp][nome]["p_blocos_dia"] for sp in ("flow", "orig")]); adj = holm(ps)
        resultado[hip] = {}
        print(f"\n{hip} [{a.periodo}] {len(wk) - 1} semanas (Holm, m = 2, α = {ALPHA})")
        for sp, p, pa in zip(("flow", "orig"), ps, adj):
            e = resultado["espacos"][sp][nome]; conf = bool(pa < ALPHA)
            resultado[hip][sp] = {"p": float(p), "p_holm": float(pa), "confirmada": conf}
            print(f"  {sp:5s} ρ agrupado {e['rho_agrupado']:+.4f} (ρ̄ semanal {e['rho_media']:+.4f}; nula {e['nula_pipeline']['rho_media']:+.4f})  "
                  f"p {p:.4f}  Holm {pa:.4f}  [p semanas, secundário {e['p_semanas_secundario']:.4f}]  → {'CONFIRMADA' if conf else 'não confirmada'}")
    out = ROOT / "resultados" / f"H-DIF-01_{a.periodo}.json"; out.parent.mkdir(exist_ok=True)
    json.dump(resultado, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False); print(f"\n→ {out}")


if __name__ == "__main__":
    main()
