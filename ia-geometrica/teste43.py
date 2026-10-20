"""Teste 43 (43-0): o sinal do m = 5 da NGC 628 sobrevive à correlação do feixe? Pipeline do preprint (ngc628/analysis_pipeline.py,
sem mudança) com anéis da largura do feixe, bootstrap por blocos de 12″, nulo de mapas de ruído convolvidos com o feixe e
controle das fases dos outros modos. Predição: PREDICAO_teste43_auditoria_feixe.md (commit b56ad9c).

    python ia-geometrica/teste43.py <diretório com NGC_628_NA_MOM1_THINGS.FITS e NGC_628_RO_MOM1_THINGS.FITS>
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "ngc628"))
import analysis_pipeline as P

GP = P.GALAXY_PARAMS["NGC 628"]; INC, PA, DIST, ZONA = GP["inc"], GP["pa"], GP["dist"], GP["zone"]
PIX_AS = 1.5; PC_AS = DIST * 1e6 * np.pi / (180 * 3600) / 1e3          # kpc por segundo de arco
FEIXE = {"NA": (11.88, 9.30, -70.34), "RO": (6.85, 5.57, -61.43)}       # FWHM maior, menor (″), BPA (°), do HISTORY
NBOOT, NNULO, BLOCO = 1000, 300, 8


def aneis(w_kpc):
    n = int(np.floor((ZONA[1] - ZONA[0]) / w_kpc)); return ZONA[0] + w_kpc / 2 + w_kpc * np.arange(n)


def medidas(f):
    z = (f["r"] >= ZONA[0]) & (f["r"] <= ZONA[1]) & (f["n_pts"] > 50)
    A5 = f["A5"][z]; base = np.concatenate([f[f"A{m}"][z] for m in range(2, 11) if m != 5])
    Z = (A5.mean() - base.mean()) / (base.std() / np.sqrt(z.sum()))
    C = {m: float(np.abs(np.mean(np.exp(1j * f[f"theta{m}"][z])))) for m in range(2, 11)}
    return {"A5": float(A5.mean()), "base": float(base.mean()), "Z": float(Z), "C": C, "N": int(z.sum()),
            "A_modos": {m: float(np.mean(f[f"A{m}"][z])) for m in range(1, 11)}}


def ajuste_anel(psi_r, v_r, vsys, N=10):
    A = np.zeros((len(psi_r), 1 + 2 * N)); A[:, 0] = np.sin(np.radians(INC)) * np.cos(psi_r)
    for n in range(1, N + 1): A[:, 2 * n - 1] = np.cos(n * psi_r); A[:, 2 * n] = np.sin(n * psi_r)
    c = np.linalg.lstsq(A, v_r - vsys, rcond=None)[0]; return A, c


def bootstrap_blocos(v, R, psi, mask, rb, vsys, rng):
    dr = (rb[1] - rb[0]) / 2; IY, IX = np.indices(v.shape); bid = (IY // BLOCO) * 10000 + (IX // BLOCO)
    aneis_d = []
    for rc in rb:
        sel = mask & (np.abs(R - rc) < dr) & np.isfinite(v)
        b = bid[sel]; ub, inv = np.unique(b, return_inverse=True)
        aneis_d.append((psi[sel], v[sel], inv, len(ub)))
    out = []
    for _ in range(NBOOT):
        a5 = []
        for ps, vv, inv, nb in aneis_d:
            esc = rng.integers(0, nb, nb); cont = np.bincount(esc, minlength=nb)
            w = cont[inv]; idx = np.repeat(np.arange(len(vv)), w)
            _, c = ajuste_anel(ps[idx], vv[idx], vsys); a5.append(np.hypot(c[9], c[10]))
        out.append(np.mean(a5))
    return np.array(out)


def kernel_feixe(shape, fmaj, fmin, bpa):
    sy, sx = (fmaj / 2.3548) / PIX_AS, (fmin / 2.3548) / PIX_AS
    ny, nx = shape; y = np.fft.fftfreq(ny) * ny; x = np.fft.fftfreq(nx) * nx; X, Y = np.meshgrid(x, y)
    t = np.radians(bpa); ux, uy = -np.sin(t), np.cos(t)                  # eixo maior em pixels (leste = −x, norte = +y)
    a = X * ux + Y * uy; b = -X * uy + Y * ux
    k = np.exp(-0.5 * ((a / sy) ** 2 + (b / sx) ** 2)); return np.fft.rfft2(k / k.sum())


def main(dados):
    assert (ROOT / "PREDICAO_teste43_auditoria_feixe.md").exists(), "sem predição, sem teste"
    res = {}
    for nome in ("NA", "RO"):
        v, m, h = P.read_fits_moment1(f"{dados}/{GP[nome.lower() + '_file']}", GP["v_min"], GP["v_max"])
        if nome == "NA": vsys = float(np.nanmedian(v[m])); hNA = h
        R, psi = P.sky_to_galactic_plane(hNA, INC, PA, DIST)
        w = FEIXE[nome][0] * PC_AS; rb = aneis(w)
        f = P.fourier_decomposition(v, R, psi, m, rb, INC, vsys, N=10)
        res[nome] = {"largura_anel_kpc": w, **medidas(f)}
        if nome == "NA": vNA, mNA, R_NA, psi_NA, rbNA, fNA = v, m, R, psi, rb, f
    rng = np.random.default_rng(43)
    boot = bootstrap_blocos(vNA, R_NA, psi_NA, mNA, rbNA, vsys, rng)
    res["NA"]["bootstrap_blocos_IC95"] = [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))]
    res["NA"]["bootstrap_blocos_dp"] = float(boot.std())

    # modelo axissimétrico + resíduo
    dr = (rbNA[1] - rbNA[0]) / 2; modelo = np.full(vNA.shape, np.nan); resid = np.full(vNA.shape, np.nan); zona = np.zeros(vNA.shape, bool)
    for rc in rbNA:
        sel = mNA & (np.abs(R_NA - rc) < dr) & np.isfinite(vNA); A, c = ajuste_anel(psi_NA[sel], vNA[sel], vsys)
        modelo[sel] = vsys + A[:, :3] @ c[:3]; resid[sel] = vNA[sel] - vsys - A @ c; zona |= sel
    sig = float(np.nanstd(resid[zona])); res["sigma_residuo"] = sig
    r0 = np.where(zona, resid, 0.0); F = np.fft.rfft2(r0); ac = np.fft.irfft2(np.abs(F) ** 2, s=r0.shape); ac /= ac[0, 0]
    perfil = [float(np.mean([ac[0, d], ac[d, 0], ac[0, -d], ac[-d, 0]])) for d in range(0, 31)]
    res["autocorrelacao_residuo_por_pixel"] = perfil
    res["meia_altura_residuo_arcsec"] = float(PIX_AS * np.argmax(np.array(perfil) < 0.5))

    K = kernel_feixe(vNA.shape, *FEIXE["NA"]); rng2 = np.random.default_rng(4300); nulo = []
    for _ in range(NNULO):
        ruido = np.fft.irfft2(np.fft.rfft2(rng2.normal(size=vNA.shape)) * K, s=vNA.shape)
        ruido *= sig / ruido[zona].std()
        vs = np.where(zona, modelo + ruido, np.nan)
        nulo.append(medidas(P.fourier_decomposition(vs, R_NA, psi_NA, zona, rbNA, INC, vsys, N=10)))
    nA5 = np.array([o["A5"] for o in nulo]); nC5 = np.array([o["C"][5] for o in nulo]); nZ = np.array([o["Z"] for o in nulo])
    res["nulo"] = {"A5_q50_q99": [float(np.quantile(nA5, .5)), float(np.quantile(nA5, .99))],
                   "C5_q50_q95": [float(np.quantile(nC5, .5)), float(np.quantile(nC5, .95))],
                   "Z_q50_q99": [float(np.quantile(nZ, .5)), float(np.quantile(nZ, .99))]}
    na = res["NA"]; C = na["C"]
    J = {"J1": na["Z"] >= 3, "J2": res["NA"]["bootstrap_blocos_IC95"][0] > na["base"],
         "J3": na["A5"] > res["nulo"]["A5_q50_q99"][1], "J4": C[5] > res["nulo"]["C5_q50_q95"][1],
         "J5": all(C[5] > C[k] for k in range(3, 11) if k != 5)}
    res["J"] = {k: bool(v) for k, v in J.items()}
    for nome in ("NA", "RO"):
        o = res[nome]
        print(f"{nome}: anel {o['largura_anel_kpc']:.3f} kpc, {o['N']} anéis | ⟨A5⟩ {o['A5']:.3f} | base {o['base']:.3f} | Z {o['Z']:.2f}")
        print("    A por modo:", {k: round(v, 3) for k, v in o["A_modos"].items()})
        print("    C_φ por modo:", {k: round(v, 3) for k, v in o["C"].items()})
    print(f"bootstrap por blocos (NA): IC95 {na['bootstrap_blocos_IC95']} dp {na['bootstrap_blocos_dp']:.3f}")
    print(f"σ do resíduo {sig:.2f} km/s | meia-altura da autocorrelação do resíduo {res['meia_altura_residuo_arcsec']}″ (ruído do feixe ≈ 7,4″)")
    print("nulo:", res["nulo"])
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste43.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
