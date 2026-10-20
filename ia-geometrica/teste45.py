"""Teste 45 (43-G): um warp geométrico (PA e inclinação variando com o raio a partir de 250″), com o centro deslocado e o feixe
do THINGS, produz o A₅ da NGC 628 no pipeline do preprint? Mapas sintéticos na grade e máscara do MOM1 NA.
Predição: PREDICAO_teste45_warp_e_m5.md (commit 3d16a90), escrita antes deste arquivo.

    python ia-geometrica/teste45.py <diretório com NGC_628_NA_MOM1_THINGS.FITS>
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "ngc628"))
import analysis_pipeline as P
import teste43 as T43

GP = P.GALAXY_PARAMS["NGC 628"]; INC, PA, DIST = GP["inc"], GP["pa"], GP["dist"]
V_ROT, SIGMA, NREAL = 184.0, 1.83, 30
NUCLEO = (24.17385, 15.78364)
DPAS, DIS = [0.0, 10.0, 20.0, 40.0], [-3.0, 0.0, 3.0]
A5_OBS_LO = 1.43


def coords(h):
    nx, ny = int(h["NAXIS1"]), int(h["NAXIS2"]); c1, c2 = float(h["CRPIX1"]), float(h["CRPIX2"])
    d1, d2 = float(h["CDELT1"]), abs(float(h["CDELT2"])); IY, IX = np.indices((ny, nx))
    kpd = DIST * 1000 * np.pi / 180
    return (IX - (c1 - 1)) * d1 * kpd, (IY - (c2 - 1)) * d2 * kpd, kpd    # x leste, y norte, em kpc


def modelo(h, dpa, di, centro_nucleo, vz5=0.0):
    x, y, kpd = coords(h)
    if centro_nucleo:
        ra0, de0 = float(h["CRVAL1"]), float(h["CRVAL2"])
        x = x - (NUCLEO[0] - ra0) * np.cos(np.radians(de0)) * kpd; y = y - (NUCLEO[1] - de0) * kpd
    kpc_as = kpd / 3600.0
    f = lambda r: np.clip((r / kpc_as - 250.0) / 150.0, 0.0, 1.0)
    r = np.hypot(x, y)
    for _ in range(8):
        pa = np.radians(PA + dpa * f(r)); inc = np.radians(INC + di * f(r))
        X = x * np.sin(pa) + y * np.cos(pa); Y = (-x * np.cos(pa) + y * np.sin(pa)) / np.cos(inc)
        r = np.hypot(X, Y)
    th = np.arctan2(Y, X)
    return GP["vsys_obs"] + V_ROT * np.sin(inc) * np.cos(th) + vz5 * np.cos(5 * th) * np.cos(inc)


def main(dados):
    assert (ROOT / "PREDICAO_teste45_warp_e_m5.md").exists(), "sem predição, sem teste"
    v, m, h = P.read_fits_moment1(f"{dados}/{GP['na_file']}", GP["v_min"], GP["v_max"])
    GP["vsys_obs"] = float(np.nanmedian(v[m]))
    R, psi = P.sky_to_galactic_plane(h, INC, PA, DIST)
    rb = T43.aneis(T43.FEIXE["NA"][0] * T43.PC_AS); dr = (rb[1] - rb[0]) / 2
    zona = m & (np.abs(R[..., None] - rb).min(-1) < dr)
    K = T43.kernel_feixe(v.shape, *T43.FEIXE["NA"])
    conv = lambda a: np.fft.irfft2(np.fft.rfft2(a) * K, s=a.shape)
    rng = np.random.default_rng(4500); ruidos = []
    for _ in range(NREAL):
        n = conv(rng.normal(size=v.shape)); ruidos.append(n * SIGMA / n[zona].std())

    def medir(mapa):
        vs = np.where(zona, mapa, np.nan)
        f = P.fourier_decomposition(vs, R, psi, zona, rb, INC, GP["vsys_obs"], N=10)
        o = T43.medidas(f); z = (f["r"] >= 9) & (f["r"] <= 14)
        o["fase_m1_graus"] = float(np.degrees(np.angle(np.mean(np.exp(1j * f["theta1"][z])))))
        return o

    res = {"configs": {}}
    for cn in (True, False):
        for dpa in DPAS:
            for di in DIS:
                base = conv(modelo(h, dpa, di, cn)); semr = medir(base)
                a5 = np.array([medir(base + n)["A5"] for n in ruidos])
                k = f"centro_{'nucleo' if cn else 'refpix'}_dPA{dpa:g}_di{di:+g}"
                res["configs"][k] = {"A5_sem_ruido": semr["A5"], "A_modos_sem_ruido": semr["A_modos"], "fase_m1": semr["fase_m1_graus"],
                                     "A5_mediana": float(np.median(a5)), "A5_q95": float(np.quantile(a5, .95))}
                print(f"{k:34s} A5 sem ruído {semr['A5']:.4f} | A3 {semr['A_modos'][3]:.4f} | A2 {semr['A_modos'][2]:.3f} | fase m1 {semr['fase_m1_graus']:+.1f}° | com ruído: mediana {np.median(a5):.3f} q95 {np.quantile(a5,.95):.3f}", flush=True)
    base = conv(modelo(h, 40.0, 3.0, True, vz5=1.55))
    a5p = np.array([medir(base + n)["A5"] for n in ruidos])
    res["positivo_vertical"] = {"A5_mediana": float(np.median(a5p)), "frac_1.35_1.75": float(np.mean((a5p >= 1.35) & (a5p <= 1.75)))}
    res["u_no_plano_equivalente_kms"] = 1.51 / np.sin(np.radians(INC))
    C = res["configs"]
    warp = [k for k in C if not k.endswith("dPA0_di+0")]
    J = {"J1": C["centro_refpix_dPA0_di+0"]["A5_mediana"] <= 0.4,
         "J2": all(c["A5_q95"] < A5_OBS_LO for c in C.values()),
         "J3": all(C[k]["A_modos_sem_ruido"][3] >= C[k]["A5_sem_ruido"] for k in warp),
         "J4": res["positivo_vertical"]["frac_1.35_1.75"] >= 0.9}
    res["J"] = {k: bool(v) for k, v in J.items()}
    print("positivo vertical:", res["positivo_vertical"], "| u no plano equivalente:", round(res["u_no_plano_equivalente_kms"], 1), "km/s")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste45.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
