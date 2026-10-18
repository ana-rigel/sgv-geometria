"""Teste 25 (OBS-01 etapa dois v2: redes treinadas até perto do ótimo). Predição: PREDICAO_teste25_rede_treinada_v2.md."""
import json, sys
from pathlib import Path
import numpy as np, torch
from scipy.signal import lfilter
sys.path.insert(0, str(Path(__file__).resolve().parent)); import teste22 as T

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste25_rede_treinada_v2.md").exists(), "sem predição, sem teste"
torch.set_num_threads(2)
N_TREINO, N_AVAL, BLOCO, PASSOS, NH = 60000, 200000, 2000, 4000, 32
REDES = range(1, 9); AVAL = range(1001, 1006); FAIXA = (1 / 1400, 1 / 35); AMPS = (0.5, 2.0)


def mundo_comp(n, seed):
    """escada-3 com as componentes separadas: devolve x (soma) e s (componente τ = 700)."""
    rng = np.random.default_rng(seed); comps = []
    for tau in (7, 70, 700):
        phi = 1 - 1 / tau; e = rng.normal(0, 1.0, n) * np.sqrt(1 - phi ** 2); comps.append(lfilter([1.0], [1, -phi], e))
    return sum(comps), comps[2]


class Rede(torch.nn.Module):
    def __init__(self):
        super().__init__(); self.rnn = torch.nn.RNN(1, NH, nonlinearity="tanh", batch_first=True); self.out = torch.nn.Linear(NH, 1)
    def forward(self, x, h=None):
        o, h = self.rnn(x, h); return self.out(o), h


def treinar(seed):
    torch.manual_seed(seed); rede = Rede(); inicial = Rede(); inicial.load_state_dict(rede.state_dict())
    x, s = mundo_comp(N_TREINO, seed); X = torch.tensor(x, dtype=torch.float32)[None, :, None]; S = torch.tensor(s, dtype=torch.float32)[None, :, None]
    opt = torch.optim.Adam(rede.parameters(), lr=3e-3); rng = np.random.default_rng(seed); perdas = []
    for p in range(PASSOS):
        i = int(rng.integers(0, N_TREINO - BLOCO)); yhat, _ = rede(X[:, i:i + BLOCO]); perda = ((yhat[:, 200:] - S[:, i + 200:i + BLOCO]) ** 2).mean()
        opt.zero_grad(); perda.backward(); torch.nn.utils.clip_grad_norm_(rede.parameters(), 1.0); opt.step(); perdas.append(float(perda.detach()))
    return rede, inicial, float(np.mean(perdas[-30:])), float(np.var(s))


@torch.no_grad()
def saida(rede, x):
    y, _ = rede(torch.tensor(x, dtype=torch.float32)[None, :, None]); return y[0, :, 0].numpy().astype(float)


def medir(rede, x):
    y = saida(rede, x); f, Sxx, H, coh = T.regua(x, y); fc, nu, eps = T.medidas(f, Sxx, H); return fc, nu, eps, float(Sxx[coh >= 0.5].sum() / Sxx.sum()), (Sxx, H)


def main():
    out = {"redes": {}}; est_ok = faixa_ok = 0; sem_fora = 0; d2_acima = 0
    for s in REDES:
        rede, inicial, perda, var_s = treinar(s); fcs, nus, epss, cobs = [], [], [], []
        for a in AVAL:
            x, _ = T.mundo(a), None; fc, nu, eps, cob, _ = medir(rede, x); fcs.append(fc); nus.append(nu); epss.append(eps); cobs.append(cob)
        fcs = np.array(fcs); cv = float(np.nanstd(fcs) / np.nanmean(fcs)) if np.all(np.isfinite(fcs)) else float("inf"); fmed = float(np.nanmedian(fcs))
        x0 = T.mundo(1001); _, _, _, _, (S0, H0) = medir(rede, x0); den = (S0 * np.abs(H0) ** 2).sum(); D = {}
        for A in AMPS:
            y = saida(rede, A * x0); f, Sa, Ha, _ = T.regua(A * x0, y); D[str(A)] = float((S0 * np.abs(Ha - H0) ** 2).sum() / den)
        fc0, nu0, eps0, cob0, _ = medir(inicial, x0)
        ok_a = cv < 0.2; ok_b = FAIXA[0] <= fmed <= FAIXA[1]; est_ok += ok_a; faixa_ok += ok_b; d2_acima += D["2.0"] > 0.05; sem_fora += not (FAIXA[0] <= fc0 <= FAIXA[1]) if np.isfinite(fc0) else 1
        out["redes"][str(s)] = {"perda_final_relativa": perda / var_s, "cortes": fcs.tolist(), "cv_corte": cv, "corte_mediano": fmed, "nu_mediano": float(np.median(nus)), "eps_mediano": float(np.median(epss)), "cobertura": float(np.median(cobs)),
                                "D": D, "sem_treino": {"corte": fc0, "nu": nu0, "eps": eps0, "cobertura": cob0}, "a": bool(ok_a), "b": bool(ok_b)}
        print(f"  rede {s}: perda rel {perda/var_s:.3f} | corte mediano {fmed:.2e} (cv {cv:.2f}) {'ok' if ok_a and ok_b else ''} | ν̂ {np.median(nus):.2f} ε̂ {np.median(epss):.2f} cob {np.median(cobs):.2f} | D(0,5×) {D['0.5']:.3f} D(2×) {D['2.0']:.3f} | sem treino: corte {fc0:.2e}", flush=True)
    R = out["redes"]; validas = [k for k in R if R[k]["perda_final_relativa"] <= 0.45]; ok = [k for k in validas if R[k]["a"] and R[k]["b"]]
    exigido = {6: 5, 7: 6, 8: 7}.get(len(validas), None); inconclusivo = len(validas) < 6; passa = (not inconclusivo) and len(ok) >= exigido
    out["resumo"] = {"validas": validas, "ok": ok, "exigido": exigido, "inconclusivo": bool(inconclusivo), "passa": bool(passa), "D2_acima": d2_acima, "sem_treino_fora_da_faixa": sem_fora}
    print(f"\n== teste 25: válidas {len(validas)}/8 (perda ≤ 0,45) | estáveis e na faixa entre as válidas: {len(ok)} (exigido {exigido}) → {'INCONCLUSIVO' if inconclusivo else ('PASSA' if passa else 'REPROVA')}")
    (ROOT / "resultados_teste25.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
