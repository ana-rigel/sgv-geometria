"""E-FLX-02 — o fluxo de segundos como filtro (R1: rompimento; R3: aborto). Desenho em PREREGISTRO_E-FLX-02.md.

    python fluxo_ordens/filtro_fluxo.py --dias 2026-06-02 ...
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fluxo_ordens"))
from fluxo_ordens import carregar  # noqa: E402

LAT, CUSTO = 250, 20.0                     # ms, bp por ida e volta
HS_R1 = {"5s": 5, "60s": 60, "5min": 300, "15min": 900, "60min": 3600}
LS = (15, 60); TAUS = (15, 30); QS = (0.50, 0.60, 0.75); HS_R3 = {"15min": 900, "60min": 3600}
N_ALEAT = 300; B = 5000; SEED = 20261013


def preparar(df):
    ts = df.ts.values; lp = np.log(df.price.values); sv = df.qty.values * df.sign.values; v = df.qty.values
    t0 = (ts[0] // 86_400_000) * 86_400_000; nsec = 86_400
    sec = np.clip((ts - t0) // 1000, 0, nsec - 1)
    hi = np.full(nsec, np.nan); lo = np.full(nsec, np.nan)
    np.fmax.at(hi, sec, lp); np.fmin.at(lo, sec, lp)
    fim = t0 + (np.arange(nsec) + 1) * 1000                      # fim de cada segundo
    idx_last = np.searchsorted(ts, fim, side="right") - 1
    LPs = np.where(idx_last >= 0, lp[np.maximum(idx_last, 0)], np.nan)
    hi = np.where(np.isnan(hi), LPs, hi); lo = np.where(np.isnan(lo), LPs, lo)
    cs = np.concatenate([[0.0], np.cumsum(sv)]); cv = np.concatenate([[0.0], np.cumsum(v)])
    S = cs[idx_last + 1]; V = cv[idx_last + 1]
    def F(k):
        num = S - np.concatenate([np.full(k, np.nan), S[:-k]]); den = V - np.concatenate([np.full(k, np.nan), V[:-k]])
        return np.where(den > 0, num / np.maximum(den, 1e-12), 0.0)
    def lp_em(t_ms, primeiro_apos=False):
        if primeiro_apos:
            i = np.minimum(np.searchsorted(ts, t_ms, side="left"), len(ts) - 1)
        else:
            i = np.maximum(np.searchsorted(ts, t_ms, side="right") - 1, 0)
        return lp[i]
    return {"t0": t0, "fim": fim, "LPs": LPs, "hi": hi, "lo": lo, "F": {k: F(k) for k in (1, 5, 15)}, "lp_em": lp_em}


def r1_eventos(P, dia):
    out = []
    for L in LS:
        w = L * 60
        hmax = pd.Series(P["hi"]).rolling(w, min_periods=w).max().shift(1).to_numpy()
        hmin = pd.Series(P["lo"]).rolling(w, min_periods=w).min().shift(1).to_numpy()
        valido = np.zeros(86_400, bool); valido[3600:86_400 - 3600 - 5] = True
        for lado, cond, nivel in ((+1, P["hi"] > hmax, hmax), (-1, P["lo"] < hmin, hmin)):
            ultimo = -10 ** 9
            for s in np.where(cond & valido)[0]:
                if s - ultimo < 300:
                    continue
                ultimo = s; t = P["fim"][s]; ent = P["lp_em"](t + LAT, True)
                rec = {"dia": dia, "L": L, "s": int(s), "lado": lado, "F1": lado * P["F"][1][s], "F5": lado * P["F"][5][s], "F15": lado * P["F"][15][s]}
                for nome, h in HS_R1.items():
                    rec["r_" + nome] = lado * (P["lp_em"](t + LAT + 1000 * h) - ent) * 1e4
                rec["falso"] = bool(lado * (P["lp_em"](t + LAT + 300_000) - nivel[s]) < 0)
                out.append(rec)
    return out


def r3_entradas(P, dia, rng, eventos):
    out = []
    aleat = rng.choice(np.arange(3600, 86_400 - 3600 - 5), N_ALEAT, replace=False)
    fontes = [("aleatoria", s, 0) for s in aleat] + [("rompimento60", e["s"], e["lado"]) for e in eventos if e["L"] == 60]
    for fonte, s, lado_nat in fontes:
        t = P["fim"][s]; ent = P["lp_em"](t + LAT, True); u = rng.random()
        rec = {"dia": dia, "fonte": fonte, "s": int(s), "u": u, "lado_nat": lado_nat, "rnd_lado": 1 if rng.random() < 0.5 else -1}
        for tau in TAUS:
            rec[f"lp_tau{tau}"] = P["lp_em"](t + LAT + 1000 * tau) - ent                  # movimento até τ
            rec[f"lp_exit{tau}"] = P["lp_em"](t + 1000 * tau + LAT, True) - ent           # saída (mercado, com latência)
            rec[f"F5_tau{tau}"] = P["F"][5][s + tau]
        for nome, h in HS_R3.items():
            rec[f"lp_H{nome}"] = P["lp_em"](t + LAT + 1000 * h) - ent
        out.append(rec)
    return out


def boot_dia(df, fn):
    dias = df.dia.unique(); rng = np.random.default_rng(SEED); g = {d: df[df.dia == d] for d in dias}
    vals = [fn(pd.concat([g[d] for d in rng.choice(dias, len(dias))])) for _ in range(B)]
    return [round(float(q), 3) for q in np.nanquantile(vals, [0.025, 0.975])]


def analisar_r1(ev):
    res = {}
    for L in LS:
        d = ev[ev.L == L]; fav = d.F5 > 0; q1, q2 = d.F5.quantile([1 / 3, 2 / 3])
        res[f"L{L}"] = {"n_eventos": int(len(d)), "frac_fluxo_a_favor": round(float(fav.mean()), 3), "horizontes": {}}
        for nome in HS_R1:
            c = "r_" + nome
            dif = lambda x, c=c: x[x.F5 > 0][c].mean() - x[x.F5 <= 0][c].mean()  # noqa: E731
            res[f"L{L}"]["horizontes"][nome] = {
                "a_favor_bp": round(float(d[fav][c].mean()), 3), "contra_bp": round(float(d[~fav][c].mean()), 3),
                "dif_bp": round(float(dif(d)), 3), "ic95": boot_dia(d, dif),
                "tercil_sup_menos_inf_bp": round(float(d[d.F5 >= q2][c].mean() - d[d.F5 <= q1][c].mean()), 3),
                "rho_F5": round(float(stats.spearmanr(d.F5, d[c])[0]), 4),
                "liquido_a_favor_bp": round(float(d[fav][c].mean() - CUSTO), 2), "liquido_contra_bp": round(float(d[~fav][c].mean() - CUSTO), 2)}
        dfl = lambda x: x[x.F5 > 0].falso.mean() - x[x.F5 <= 0].falso.mean()  # noqa: E731
        res[f"L{L}"]["falso"] = {"a_favor": round(float(d[fav].falso.mean()), 3), "contra": round(float(d[~fav].falso.mean()), 3),
                                 "dif_pp": round(100 * float(dfl(d)), 2), "ic95_pp": [100 * x for x in boot_dia(d, dfl)]}
    return res


def analisar_r3(en):
    res = {}
    for fonte in ("aleatoria", "rompimento60"):
        d0 = en[en.fonte == fonte]
        for nome in HS_R3:
            for tau in TAUS:
                total = d0[f"lp_H{nome}"].to_numpy(); resto = total - d0[f"lp_tau{tau}"].to_numpy()
                variantes = {"V1": total, "V2": resto} if fonte == "aleatoria" else {"natural": None}
                for var, alvo in variantes.items():
                    for q in (QS if fonte == "aleatoria" else (None,)):
                        if fonte == "aleatoria":
                            lado = np.where(d0.u.to_numpy() < q, np.sign(alvo), -np.sign(alvo)); lado[lado == 0] = d0.rnd_lado.to_numpy()[lado == 0]
                        else:
                            lado = d0.lado_nat.to_numpy()
                        mov = lado * d0[f"lp_tau{tau}"].to_numpy(); fl = lado * d0[f"F5_tau{tau}"].to_numpy()
                        aborta = (mov <= 0) & (fl <= 0)
                        segurar = lado * total * 1e4 - CUSTO
                        abortar = np.where(aborta, lado * d0[f"lp_exit{tau}"].to_numpy() * 1e4, lado * total * 1e4) - CUSTO
                        dd = d0.assign(seg=segurar, abo=abortar)
                        chave = f"{fonte}|H{nome}|tau{tau}|{var}" + (f"|q{q:.2f}" if q is not None else "")
                        res[chave] = {"n": int(len(d0)), "frac_abortada": round(float(aborta.mean()), 3),
                                      "rho_aborto_resto": round(float(stats.spearmanr(aborta, lado * resto)[0]), 4),
                                      "segurar_bp": round(float(segurar.mean()), 2), "abortar_bp": round(float(abortar.mean()), 2),
                                      "abortar_menos_segurar_bp": round(float((abortar - segurar).mean()), 2),
                                      "ic95": boot_dia(dd, lambda x: (x.abo - x.seg).mean()),
                                      "vantagem_plantada_bp": round(float(segurar.mean() + CUSTO), 2)}
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dias", nargs="+", required=True); a = ap.parse_args()
    rng = np.random.default_rng(SEED); ev_all, en_all = [], []
    for dia in a.dias:
        P = preparar(carregar(dia)); ev = r1_eventos(P, dia); en = r3_entradas(P, dia, rng, ev)
        ev_all += ev; en_all += en; print(f"{dia}: {len(ev)} rompimentos, {len(en)} entradas R3", flush=True)
    ev = pd.DataFrame(ev_all); en = pd.DataFrame(en_all)
    out = {"R1": analisar_r1(ev), "R3": analisar_r3(en)}
    resd = ROOT / "fluxo_ordens" / "resultados"; resd.mkdir(exist_ok=True)
    ev.to_csv(resd / "E-FLX-02_eventos.csv.gz", index=False)
    json.dump(out, open(resd / "E-FLX-02.json", "w"), indent=1, ensure_ascii=False)
    print("\n== R1: rompimentos, fluxo dos 5 s anteriores a favor vs contra (bp, no sentido do rompimento)")
    for L, r in out["R1"].items():
        print(f"{L}: {r['n_eventos']} eventos, {r['frac_fluxo_a_favor']:.0%} com fluxo a favor; rompimento falso a favor {r['falso']['a_favor']:.1%} contra {r['falso']['contra']:.1%} (dif {r['falso']['dif_pp']:+.1f} pp, IC {r['falso']['ic95_pp']})")
        for h, x in r["horizontes"].items():
            print(f"   {h:6s} a favor {x['a_favor_bp']:+7.2f}  contra {x['contra_bp']:+7.2f}  dif {x['dif_bp']:+6.2f} IC {x['ic95']}  ρ {x['rho_F5']:+.3f}  líquido {x['liquido_a_favor_bp']:+.1f} / {x['liquido_contra_bp']:+.1f}")
    print("\n== R3: abortar em τ se não andou e o fluxo sumiu (bp por operação, líquido de 20 bp)")
    for k, x in out["R3"].items():
        print(f"{k:42s} abortadas {x['frac_abortada']:.0%}  ρ(aborto, resto) {x['rho_aborto_resto']:+.3f}  vantagem {x['vantagem_plantada_bp']:+6.1f}  segurar {x['segurar_bp']:+6.1f}  abortar {x['abortar_bp']:+6.1f}  dif {x['abortar_menos_segurar_bp']:+5.1f} IC {x['ic95']}")


if __name__ == "__main__":
    main()
