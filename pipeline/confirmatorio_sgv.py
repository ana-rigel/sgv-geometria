"""H-SGV-01: o SGV original complementa o espaço de fluxo?

Pré-registro: PREREGISTRO_H-SGV-01.md. Sem edição depois do congelamento; hashes em referencia/HASHES_H-SGV-01.txt.
Calendário (opção C, decisão de Ana em 15/10/2026):

    python pipeline/confirmatorio_sgv.py --periodo exploracao     # ensaio de paridade em jun–jul/2026
    python pipeline/confirmatorio_sgv.py --periodo confirmatorio  # outubro/2026: julga H-SGV-01a
    python pipeline/confirmatorio_sgv.py --periodo replicacao     # novembro/2026: replica H-SGV-01a
    python pipeline/confirmatorio_sgv.py --periodo conjunto       # outubro + novembro/2026: julga H-SGV-01b (Holm com o p de a de outubro)
    python pipeline/confirmatorio_sgv.py --periodo replicacao_b   # dezembro/2026: replica H-SGV-01b

Família primária (m = 2, Holm, α = 0,05), sinal registrado NEGATIVO nas duas, com o espaço de FLUXO nos controles:
    H-SGV-01a  raridade no plano (E_norm, jerk) do sgv_original: log rho_field   (julgada em outubro)
    H-SGV-01b  memória do esticamento: mem_e = EMA_0,05(E_norm)                  (julgada em outubro + novembro)
Holm com calendários diferentes: em outubro, a é confirmada se p_a < α/2 (isso a confirma pelo Holm qualquer que seja
p_b). Se p_a ≥ α/2, o veredito de a espera p_b. Com p_a (outubro) e p_b (outubro + novembro), o Holm m = 2 dá os vereditos finais.
Alvo log Range dos 5 min seguintes; 1 minuto a cada 5; ρ parcial de Spearman sobre os pares de resíduos agrupados das
semanas julgadas; p por permutação do par dentro de cada dia (B = 5.000), unilateral (funções do H-FORMA-D-01).
Controles "fluxo": os primários do H-FORMA-D-01 sem log ρ e log tr D (σ 10/30/60, HAR 1d/1s, r5/r30, logvol 10/60,
hora, memória de amplitude 1/5/10/30/60/1.440) + log ρ, log tr D e c(x) do campo do H-DIF-01 no espaço de fluxo
(semana anterior) + ν(t). Variáveis do sgv_original pelas funções de explorar_sgv_original.py (vendor ac6b986).
Secundárias informativas (BH): ver SECUNDARIAS abaixo. Nula de pipeline só para leitura.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import confirmatorio_forma as F  # noqa: E402  (carregar, Campo, residuos, rho_parcial, semanas, gaussianize, COORDS, p_blocos, p_semanas, holm, bh)
import explorar_sgv_original as XS  # noqa: E402  (variaveis_sgv)

ALPHA, SEED_BOOT = 0.05, 20261013
VI = {v: j for j, v in enumerate(XS.VARS)}           # log_rho, basin, disp, n_obs, mem_e
PRIMARIAS = [("H-SGV-01a", "log_rho", "fluxo", -1), ("H-SGV-01b", "mem_e", "fluxo", -1)]
SECUNDARIAS = [("raridade_prim", "log_rho", "prim", -1), ("esticamento_prim", "mem_e", "prim", -1),
               ("raridade_campo_orig", "log_rho", "orig", -1), ("esticamento_campo_orig", "mem_e", "orig", -1),
               ("esticamento_retornos_lentos", "mem_e", "ret", -1),
               ("deslocamento_prim", "disp", "prim", +1), ("deslocamento_fluxo", "disp", "fluxo", +1),
               ("basin_fluxo", "basin", "fluxo", -1), ("n_obs_fluxo", "n_obs", "fluxo", -1)]
MEDIDAS = PRIMARIAS + SECUNDARIAS
_M = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11", "2026-12"]
PERIODOS = {
    "exploracao": F.PERIODOS["exploracao"],
    "confirmatorio": F.PERIODOS["confirmatorio"],     # outubro: semanas 01, 08, 15 e 22/10 (treino 24/09)
    "replicacao": F.PERIODOS["replicacao"],           # novembro: semanas 01, 08, 15 e 22/11 (treino 25/10)
    "conjunto": {"meses": _M[:7], "inicio": "2026-10-01", "fim": "2026-12-01", "treino0": "2026-09-24"},   # 9 semanas: 01/10 … 26/11–01/12
    "replicacao_b": {"meses": _M[:8], "inicio": "2026-12-01", "fim": "2027-01-01", "treino0": "2026-11-24"},  # dezembro
}
JULGA = {"confirmatorio": ["H-SGV-01a"], "replicacao": ["H-SGV-01a"], "conjunto": ["H-SGV-01b"], "replicacao_b": ["H-SGV-01b"], "exploracao": []}


def controles(kl, hour_d):
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
    RET = np.column_stack([rs.rolling(w, min_periods=w // 2).sum() for w in (60, 240, 1440)])
    return y, C, RET


def analisar(V, Go, Gf, kl, ts, wk, hour_d, label):
    y, C, RET = controles(kl, hour_d); dia = ts.dt.floor("D").to_numpy()
    sem = {m[0]: [] for m in MEDIDAS}; pares = {m[0]: ([], [], []) for m in MEDIDAS}
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        s5 = te[np.arange(len(te)) % 5 == 0]
        ex = {}
        for nome, G in (("orig", Go), ("fluxo", Gf)):
            Cf = F.Campo(G, tr); X = G[s5]; okx = np.isfinite(X).all(1)
            cc, lt, lr_ = (np.full(len(s5), np.nan) for _ in range(3))
            c_, _, lt_, lrr = Cf.at(X[okx]); cc[okx] = c_; lt[okx] = lt_; lr_[okx] = lrr
            ex[nome] = (cc, lt, lr_)
        Cs = {"prim": C[s5], "orig": np.column_stack([C[s5], ex["orig"][2], ex["orig"][1]]),
              "fluxo": np.column_stack([C[s5], ex["fluxo"][2], ex["fluxo"][1], ex["fluxo"][0], Gf[s5, 2]]),
              "ret": np.column_stack([C[s5], RET[s5]])}
        for nome, var, cj, _ in MEDIDAS:
            x = V[s5, VI[var]]
            sem[nome].append(F.rho_parcial(x, y[s5], Cs[cj]))
            xr, yr, ok = F.residuos(x, y[s5], Cs[cj])
            pares[nome][0].append(xr); pares[nome][1].append(yr); pares[nome][2].append(dia[s5][ok])
    out = {}
    for nome, _, _, _ in MEDIDAS:
        v = np.array(sem[nome], float)
        out[nome] = {"rho_semanal": [round(float(x), 4) for x in v], "rho_media": float(np.nanmean(v)),
                     "pares": tuple(np.concatenate(p) for p in pares[nome])}
    print(label.ljust(9), " | ".join(f"{n}: {out[n]['rho_media']:+.4f}" for n, *_ in PRIMARIAS), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True)
    a = ap.parse_args(); P = PERIODOS[a.periodo]
    kl = F.carregar(P["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp(P["fim"], tz="UTC") and ts.iloc[-1] >= pd.Timestamp(P["inicio"], tz="UTC") + pd.Timedelta(days=5)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    wk = F.semanas(ts, P["treino0"], P["inicio"], P["fim"])
    hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
    rng_null = np.random.default_rng(F.SEED_NULL); rng = np.random.default_rng(SEED_BOOT)
    i_perm = wk[0][0]; day = ts.dt.floor("D").to_numpy(); perm = np.arange(len(kl))
    for d in np.unique(day[i_perm:]):
        s = np.where(day == d)[0]; s = s[s >= i_perm]; perm[s] = rng_null.permutation(s)
    lc = np.log(kl.close.values); lr = np.diff(lc, prepend=lc[0]); hi = np.log(kl.high.values) - lc; lo = lc - np.log(kl.low.values)
    lv = np.log(kl.volume.values.astype(float)); frac = kl.taker_buy.values / kl.volume.values
    c2 = np.exp(lc[0] + np.cumsum(lr[perm]))
    kl_null = pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]),
                            "close": c2, "volume": np.exp(lv[perm]), "taker_buy": frac[perm] * np.exp(lv[perm])})
    res = {}
    for label, K in (("real", kl), ("pipeline", kl_null)):
        G = {}
        for sp in ("orig", "flow"):
            raw = F.COORDS[sp](K); ok = np.isfinite(raw).all(1)
            anc = F.COORDS[sp](kl); anc = anc[may & np.isfinite(anc).all(1)]
            G[sp] = np.full_like(raw, np.nan); G[sp][ok] = F.gaussianize(anc, raw[ok])
        res[label] = analisar(XS.variaveis_sgv(K), G["orig"], G["flow"], K, ts, wk, hour_d, label)
    out = {"hipotese": "H-SGV-01", "periodo": a.periodo, "semanas_julgadas": [str(ts.iloc[w[0]].date()) for w in wk[1:]],
           "congelado": {"alpha": ALPHA, "B_perm": F.B_PERM, "B_boot": F.B_BOOT, "seed_boot": SEED_BOOT, "seed_null": F.SEED_NULL,
                         "p_primario": "permutacao do par dentro do dia (p_blocos do H-FORMA-D-01)"}, "medidas": {}}
    for nome, var, cj, sg in MEDIDAS:
        r = res["real"][nome]; v = np.array(r["rho_semanal"], float)
        p, rho_pool = F.p_blocos(*r["pares"], sg, rng); p2 = F.p_semanas(v, sg, rng)
        out["medidas"][nome] = {"variavel": var, "controles": cj, "sinal_registrado": sg, "rho_semanal": r["rho_semanal"], "rho_media": r["rho_media"],
                                "rho_agrupado": float(rho_pool), "p_blocos_dia": float(p), "p_semanas_secundario": float(p2),
                                "nula_pipeline": {"rho_semanal": res["pipeline"][nome]["rho_semanal"], "rho_media": res["pipeline"][nome]["rho_media"]}}
    print(f"\nH-SGV-01 [{a.periodo}] {len(wk) - 1} semanas; espaço de fluxo nos controles; julga aqui: {JULGA[a.periodo] or 'nada (ensaio)'}")
    out["veredito"] = {}
    for nome, var, _, _ in PRIMARIAS:
        e = out["medidas"][nome]; p = e["p_blocos_dia"]
        if a.periodo == "exploracao":
            rot = f"ensaio, não julga (p {p:.4f})"; v = None
        elif nome not in JULGA[a.periodo]:
            rot = f"só leitura neste período (p {p:.4f}); julgada em outro período"; v = None
        elif a.periodo == "confirmatorio":     # a: confirmada já se p_a < α/2; senão espera p_b
            v = "CONFIRMADA" if p < ALPHA / 2 else "pendente: Holm com p_b de outubro + novembro"; rot = f"p {p:.4f} (limiar α/2 = {ALPHA / 2}) → {v}"
        elif a.periodo == "conjunto":          # b: Holm m = 2 com p_a de outubro
            pa_out = json.load(open(ROOT / "resultados" / "H-SGV-01_confirmatorio.json", encoding="utf-8"))["medidas"]["H-SGV-01a"]["p_blocos_dia"]
            adj = F.holm(np.array([pa_out, p]))
            v = {"H-SGV-01a": "CONFIRMADA" if adj[0] < ALPHA else "não confirmada", "H-SGV-01b": "CONFIRMADA" if adj[1] < ALPHA else "não confirmada"}
            out["holm_final"] = {"p_a_outubro": float(pa_out), "p_b_conjunto": float(p), "p_holm_a": float(adj[0]), "p_holm_b": float(adj[1]), "vereditos": v}
            rot = f"p {p:.4f}; Holm final com p_a(outubro) {pa_out:.4f}: a {adj[0]:.4f} → {v['H-SGV-01a']}; b {adj[1]:.4f} → {v['H-SGV-01b']}"; v = v[nome]
        else:                                  # replicações: p < α unilateral, relatadas à parte
            v = "REPLICADA" if p < ALPHA else "não replicada"; rot = f"p {p:.4f} → {v}"
        out["veredito"][nome] = {"p": float(p), "resultado": v}
        print(f"  {nome} ({var}): ρ agrupado {e['rho_agrupado']:+.4f} (ρ̄ semanal {e['rho_media']:+.4f}; nula {e['nula_pipeline']['rho_media']:+.4f}) {rot}")
    qs = F.bh([out["medidas"][n]["p_blocos_dia"] for n, *_ in SECUNDARIAS])
    out["secundarias_BH"] = {n: {"rho_media": out["medidas"][n]["rho_media"], "p": out["medidas"][n]["p_blocos_dia"], "p_bh": float(q)} for (n, *_), q in zip(SECUNDARIAS, qs)}
    for n, d in out["secundarias_BH"].items(): print(f"  secundária {n}: ρ̄ {d['rho_media']:+.4f} p_bh {d['p_bh']:.4f}")
    dest = ROOT / "resultados" / f"H-SGV-01_{a.periodo}.json"; dest.parent.mkdir(exist_ok=True)
    json.dump(out, open(dest, "w", encoding="utf-8"), indent=1, ensure_ascii=False); print(f"→ {dest}")


if __name__ == "__main__":
    main()
