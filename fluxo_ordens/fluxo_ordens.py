"""E-FLX-01 — direção no fluxo de ordens em escala de segundos (exploração, jun–jul/2026, BTCUSDT spot).

    python fluxo_ordens/fluxo_ordens.py --dias 2026-06-02 2026-06-08 ...   # lê fluxo_ordens/dados/BTCUSDT-aggTrades-<dia>.zip

Para cada dia:
  (a) autocorrelação do sinal dos negócios em tempo de evento (lags 1..100) — real e nula;
  (b) desequilíbrio de fluxo F_k(t) = Σ volume assinado nos últimos k s (k = 1, 5, 15, 60), avaliado 1×/s;
      alvo: retorno log do preço de execução (primeiro negócio depois de t + L) até o último negócio ≤ t + L + h,
      L ∈ {0, 100, 250, 500, 1000} ms, h ∈ {1, 5, 15, 60} s;
      ρ de Spearman F_k × r_h, acurácia do sinal, retorno médio condicionado ao decil extremo de |F_k|,
      líquido de custo (ida e volta) 0,20 %, 0,15 % e 0 %;
  (c) nulas: (1) lado do agressor permutado dentro de cada minuto (destrói a memória abaixo do minuto, mantém o
      fluxo líquido do minuto — e por isso ainda "prevê" parte do retorno do próprio minuto: é o piso, não zero);
      (2) série de lados deslocada circularmente em 1 h (mantém toda a memória do fluxo, quebra a ligação com o preço).
      O real tem de passar das duas.
Agrega por dia; saída fluxo_ordens/resultados/E-FLX-01.json.
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

ROOT = Path(__file__).resolve().parents[1]
KS, HS, LS = (1, 5, 15, 60), (1, 5, 15, 60), (0, 100, 250, 500, 1000)
CUSTOS = {"taker_0.10%": 0.0020, "taker_0.075%": 0.0015, "maker_0": 0.0}
COLS = ["agg_id", "price", "qty", "first_id", "last_id", "ts", "is_buyer_maker", "best_match"]


def carregar(dia):
    nome = f"BTCUSDT-aggTrades-{dia}.zip"; caminho = ROOT / "fluxo_ordens" / "dados" / nome
    chk = caminho.with_name(nome + ".CHECKSUM")
    if chk.exists() and hashlib.sha256(caminho.read_bytes()).hexdigest() != chk.read_text().split()[0]:
        sys.exit(f"SHA-256 não confere: {nome}")
    with zipfile.ZipFile(caminho) as z:
        df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS, dtype=str)
    if not df.agg_id.iloc[0].isdigit():
        df = df.iloc[1:]
    df = pd.DataFrame({"ts": df.ts.astype("int64"), "price": df.price.astype(float), "qty": df.qty.astype(float),
                       "buyer_maker": df.is_buyer_maker.str.strip().str.lower().isin(["true", "1"])})
    if df.ts.iloc[0] > 1e14:
        df["ts"] //= 1000
    df = df.sort_values("ts", kind="stable").reset_index(drop=True)
    df["sign"] = np.where(df.buyer_maker, -1.0, 1.0)   # buyer_maker=True → agressor vendeu
    return df


def autocorr_sinais(sign, lags=100):
    s = sign - sign.mean(); v = (s * s).mean()
    return [float((s[:-l] * s[l:]).mean() / v) for l in range(1, lags + 1)]


def analisar(df, sign, label):
    ts = df.ts.values; px = df.price.values; sv = df.qty.values * sign; lp = np.log(px)
    t0 = (ts.min() // 1000) * 1000; grid = np.arange(t0 + 60000, ts.max() - 70000, 1000)   # 1×/s, margens
    cum = np.concatenate([[0.0], np.cumsum(sv)])
    def soma_ate(t):  # Σ volume assinado de negócios com ts ≤ t
        return cum[np.searchsorted(ts, t, side="right")]
    F = {k: soma_ate(grid) - soma_ate(grid - 1000 * k) for k in KS}
    out = {"ac_sinais": autocorr_sinais(sign)[:], "n_trades": int(len(df)), "ρ": {}, "acc": {}, "dec": {}}
    for L in LS:
        i_exec = np.searchsorted(ts, grid + L, side="left"); i_exec = np.minimum(i_exec, len(ts) - 1)   # primeiro negócio ≥ t+L
        p_exec = lp[i_exec]
        for h in HS:
            i_fim = np.searchsorted(ts, grid + L + 1000 * h, side="right") - 1
            r = lp[i_fim] - p_exec
            for k in KS:
                f = F[k]; ok = np.isfinite(r) & (i_fim > i_exec)
                key = f"L{L}_h{h}_k{k}"
                out["ρ"][key] = float(stats.spearmanr(f[ok], r[ok])[0])
                nz = ok & (f != 0) & (r != 0)
                out["acc"][key] = float((np.sign(f[nz]) == np.sign(r[nz])).mean())
                q = np.quantile(np.abs(f[ok]), 0.9); ext = ok & (np.abs(f) >= q)
                bruto = float((np.sign(f[ext]) * r[ext]).mean())   # segue o sinal do fluxo
                out["dec"][key] = {"bruto": bruto, **{c: bruto - v for c, v in CUSTOS.items()}, "n": int(ext.sum())}
    print(label.ljust(9), f"trades {len(df):,}  ac1 {out['ac_sinais'][0]:+.3f} ac10 {out['ac_sinais'][9]:+.3f}  "
          + "  ".join(f"L{L}/h{h}/k{k}: ρ {out['ρ'][f'L{L}_h{h}_k{k}']:+.3f} acc {out['acc'][f'L{L}_h{h}_k{k}']:.3f} dec {out['dec'][f'L{L}_h{h}_k{k}']['bruto']*1e4:+.2f}bp"
                      for L, h, k in ((0, 1, 1), (0, 5, 5), (250, 5, 5), (1000, 15, 15), (0, 60, 60))), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dias", nargs="+", required=True); a = ap.parse_args()
    rng = np.random.default_rng(2026); res = {"dias": {}, "desenho": __doc__}
    for dia in a.dias:
        df = carregar(dia); print(f"\n== {dia}")
        real = analisar(df, df.sign.values, "real")
        minuto = df.ts.values // 60000; s2 = df.sign.values.copy()
        for m in np.unique(minuto):
            idx = np.where(minuto == m)[0]; s2[idx] = rng.permutation(s2[idx])
        nulo = analisar(df, s2, "nula")
        i_shift = int(np.searchsorted(df.ts.values, df.ts.values[0] + 3_600_000)); s3 = np.roll(df.sign.values, i_shift)
        nulo2 = analisar(df, s3, "nula2")
        res["dias"][dia] = {"real": real, "nula": nulo, "nula2": nulo2}
    # agregação: média entre dias
    agg = {}
    for lab in ("real", "nula", "nula2"):
        agg[lab] = {"ac_sinais": np.mean([res["dias"][d][lab]["ac_sinais"] for d in a.dias], axis=0).round(4).tolist()}
        for campo in ("ρ", "acc"):
            agg[lab][campo] = {k: float(np.mean([res["dias"][d][lab][campo][k] for d in a.dias])) for k in real[campo]}
        agg[lab]["dec"] = {k: {c: float(np.mean([res["dias"][d][lab]["dec"][k][c] for d in a.dias])) for c in ("bruto", *CUSTOS)} for k in real["dec"]}
    res["media"] = agg
    print("\n== média entre dias (real | nula permutada | nula deslocada)")
    print("ac sinais lags 1,2,5,10,50,100:", [agg["real"]["ac_sinais"][i - 1] for i in (1, 2, 5, 10, 50, 100)], "|", [agg["nula"]["ac_sinais"][i - 1] for i in (1, 2, 5, 10, 50, 100)])
    print(f"{'L ms':>5} {'h s':>4} {'k s':>4} {'ρ':>7} {'acc':>6} {'bruto bp':>9} {'taker.10':>9} {'taker.075':>10} {'maker':>8} | {'ρ nula':>7} {'acc nula':>8} {'ρ nula2':>8}")
    for L in LS:
        for h in HS:
            for k in KS:
                key = f"L{L}_h{h}_k{k}"; d = agg["real"]["dec"][key]
                print(f"{L:5d} {h:4d} {k:4d} {agg['real']['ρ'][key]:+7.3f} {agg['real']['acc'][key]:6.3f} {d['bruto']*1e4:+9.2f} {d['taker_0.10%']*1e4:+9.2f} {d['taker_0.075%']*1e4:+10.2f} {d['maker_0']*1e4:+8.2f} | {agg['nula']['ρ'][key]:+7.3f} {agg['nula']['acc'][key]:8.3f} {agg['nula2']['ρ'][key]:+8.3f}")
    out = ROOT / "fluxo_ordens" / "resultados" / "E-FLX-01.json"; out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out, "w"), indent=1); print(f"\n→ {out}")


if __name__ == "__main__":
    main()
