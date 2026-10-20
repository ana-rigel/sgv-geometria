"""Teste 29 (a declaração no sítio): a cada cheia, a v0 declara a cegueira do andar 1 na janela antes dela; a declaração separa as cheias que o alarme comum perdeu das que ele protegeu? Predição: PREDICAO_teste29_declaracao_no_sitio.md.

    python ia-geometrica/teste29.py --contagem   # sementes de desenho: só quantas cheias perdidas e protegidas há; nenhuma declaração é avaliada
    python ia-geometrica/teste29.py              # o teste (exige a predição)
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import sitio as S; import teste28 as T28

ROOT = Path(__file__).resolve().parent
N, AFIN, SEEDS, D, P = T28.N, T28.AFIN, T28.SEEDS, T28.D, T28.P
L_J, C_J, W = 6, 3.0, 48                               # ponto julgado; janela da declaração (h)
RELATADOS = [(3, 3.0), (1, 1.0)]
LAM1 = 0.15                                            # andar 1 da v0 (o mesmo dos testes 1–28)


def ganho2(lam, f):
    return lam ** 2 / (1 - 2 * (1 - lam) * np.cos(2 * np.pi * f) + (1 - lam) ** 2)


def declarada(seg, lam=LAM1):
    """Regra dos testes 9 e 16: fração da potência da entrada do andar que o ganho do andar não deixa passar."""
    v = seg - seg.mean(); Pw = np.abs(np.fft.rfft(v)) ** 2; f = np.fft.rfftfreq(len(v)); tot = Pw[1:].sum()
    return float((Pw[1:] * (1 - ganho2(lam, f[1:]))).sum() / tot) if tot > 0 else 0.0


def cheias_rotuladas(s, L, C):
    """Para cada cheia dos anos 3–4: perdida (1) ou protegida (0) pelo alarme comum N3 afinado em (L, C), e as leituras feitas na janela antes dela."""
    r, ev, fam, ini = T28.leituras(s); xs = fam["N3_chuva_nivel"][1]
    a, b, ga, gb = fam["N3_chuva_nivel"]; forma, ta, tb, cond = T28.afinar(a, b, ga, gb, ev, L, C)
    ch = S.chamadas(cond, P); out = []
    for t in ev[ev >= AFIN]:
        perdida = int(not np.any((ch + L <= t) & (t <= ch + L + P)))
        seg = xs[t - W:t + 1]; subida = seg[-1] - seg.min()
        out.append({"t": int(t), "perdida": perdida, "declaracao_v0": declarada(seg),
                    "subida_L": float(xs[t] - xs[t - L]), "fracao_subida_L": float((xs[t] - xs[t - L]) / subida) if subida > 0 else 0.0})
    return out, forma


def auc(score, y):
    """Área sob a curva ROC (Mann–Whitney), empates contados pela metade."""
    score, y = np.asarray(score), np.asarray(y); pos, neg = score[y == 1], score[y == 0]
    if len(pos) == 0 or len(neg) == 0: return float("nan")
    m = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean(); return float(m)


def semente(s):
    o = {}
    for L, C in [(L_J, C_J)] + RELATADOS:
        ev, forma = cheias_rotuladas(s, L, C); o[f"L{L}_C{int(C)}"] = {"forma_N3": forma, "cheias": ev}
    return s, o


def contagem():
    for s in range(5000, 5005):
        ev, _ = cheias_rotuladas(s, L_J, C_J); y = [e["perdida"] for e in ev]
        print(f"  s{s}: {len(y)} cheias nos anos 3–4 | perdidas {sum(y)} | protegidas {len(y)-sum(y)}")
    print("contagem: nenhuma declaração avaliada")


def julgar(E, rng):
    y = np.array([e["perdida"] for e in E]); sem = np.array([e["semente"] for e in E])
    leit = {k: np.array([e[k] for e in E]) for k in ("declaracao_v0", "subida_L", "fracao_subida_L")}
    A = {k: auc(v, y) for k, v in leit.items()}
    comum = max(("subida_L", "fracao_subida_L"), key=lambda k: A[k])
    # bootstrap por semente (as cheias de uma semente andam juntas)
    us = np.unique(sem); idx = {u: np.flatnonzero(sem == u) for u in us}; bv, bd = [], []
    for _ in range(1000):
        pick = np.concatenate([idx[u] for u in rng.choice(us, len(us))])
        av = auc(leit["declaracao_v0"][pick], y[pick]); bv.append(av); bd.append(av - auc(leit[comum][pick], y[pick]))
    perm = [auc(leit["declaracao_v0"], rng.permutation(y)) for _ in range(1000)]
    return {"n_cheias": int(len(y)), "perdidas": int(y.sum()), "auc": A, "comum_mais_forte": comum,
            "auc_v0_ic95": [float(np.quantile(bv, .025)), float(np.quantile(bv, .975))],
            "dif_v0_menos_comum": float(A["declaracao_v0"] - A[comum]), "dif_ic95": [float(np.quantile(bd, .025)), float(np.quantile(bd, .975))],
            "permutacao_q95": float(np.quantile(perm, .95)),
            "media_declaracao": {"perdidas": float(leit["declaracao_v0"][y == 1].mean()), "protegidas": float(leit["declaracao_v0"][y == 0].mean())}}


def main():
    assert (ROOT / "PREDICAO_teste29_declaracao_no_sitio.md").exists(), "sem predição, sem teste"
    from multiprocessing import Pool
    out = {"sementes": {}}
    with Pool(2) as pool:
        for s, o in pool.imap_unordered(semente, list(SEEDS)):
            out["sementes"][str(s)] = o
            if (s - 1000) % 10 == 0: print(f"  s{s} pronto", flush=True)
    rng = np.random.default_rng(29); res = {}
    for cel in [f"L{L}_C{int(C)}" for L, C in [(L_J, C_J)] + RELATADOS]:
        E = [dict(e, semente=int(s)) for s in out["sementes"] for e in out["sementes"][s][cel]["cheias"]]
        res[cel] = julgar(E, rng)
    J = res[f"L{L_J}_C{int(C_J)}"]
    j1 = bool(J["auc"]["declaracao_v0"] >= 0.70 and J["auc_v0_ic95"][0] > J["permutacao_q95"])
    j2 = bool(J["dif_v0_menos_comum"] >= 0.03 and J["dif_ic95"][0] > 0)
    out["resumo"] = {"celulas": res, "J1": j1, "J2": j2}
    for cel, r in res.items():
        print(f"== {cel}: {r['n_cheias']} cheias, {r['perdidas']} perdidas | AUC v0 {r['auc']['declaracao_v0']:.3f} (IC {r['auc_v0_ic95'][0]:.3f}–{r['auc_v0_ic95'][1]:.3f}; perm q95 {r['permutacao_q95']:.3f}) | subida_L {r['auc']['subida_L']:.3f} | fração_L {r['auc']['fracao_subida_L']:.3f} | v0 − comum {r['dif_v0_menos_comum']:+.3f} (IC {r['dif_ic95'][0]:+.3f}; {r['dif_ic95'][1]:+.3f}) | declaração média perdidas {r['media_declaracao']['perdidas']:.2f} protegidas {r['media_declaracao']['protegidas']:.2f}")
    print(f"   J1 a declaração separa perdidas de protegidas: {'PASSA' if j1 else 'REPROVA'} | J2 melhor que a medida comum: {'PASSA' if j2 else 'REPROVA'}")
    (ROOT / "resultados_teste29.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--contagem", action="store_true")
    contagem() if ap.parse_args().contagem else main()
