"""Teste 50: o padrão do H I da NGC 628 além de 310″ — rígido (a predição congelada do teste 49) ou cisalhando?
Tremaine–Weinberg radial (Eq. 1 de Speights et al. 2025) generalizado para anéis inclinados (warp), no momento 0 e no
momento 1 NA do THINGS; Tikhonov de 2ª ordem com λ por GCV; porta sintética com a morfologia real e o resíduo real.
Predição: PREDICAO_teste50_padrao_externo.md (commit b588add), escrita antes deste arquivo.

    python ia-geometrica/teste50.py <momento0.fits[.gz]> <NGC_628_NA_MOM1_THINGS.FITS> [figura.png]
"""
import json, sys, time
from pathlib import Path
import numpy as np
from scipy import ndimage
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path(__file__).resolve().parent
PIX = 1.5; KPC_AS = 0.0342                       # ″ por pixel; kpc por ″ (escala de Speights et al.)
CENTRO = SkyCoord("01h36m41.747s", "+15d47m01.18s", frame="fk5", equinox="J2000")
VSYS_SPEIGHTS, PA_SPEIGHTS, I_SPEIGHTS = 655.9, 21.8, 6.0
DR_ANEL, DR_PA, DY0, DSUB = 7.5, 15.0, 3.0, 0.75
Z0, Z1, RMAX_SP, R_STAR, R_CR = 310.0, 395.0, 310.0, 278.0, 330.0
NREAL, SEMENTE = int(__import__("os").environ.get("NREAL", 100)), 50
PIX_POR_FEIXE = 1.1331 * 11.88 * 9.30 / PIX ** 2


# ---------------------------------------------------------------- dados e coordenadas do céu
def carregar(p0, p1):
    h0 = fits.open(p0)[0]; h1 = fits.open(p1)[0]
    m0 = np.nan_to_num(np.asarray(h0.data, float).squeeze(), nan=0.0)
    m1 = np.asarray(h1.data, float).squeeze()[: m0.shape[0]] / 1e3            # m/s → km/s; as linhas cortadas no norte
    for k in ("CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2", "CDELT1", "CDELT2"):
        assert h0.header[k] == h1.header[k], k
    w = WCS(h0.header, naxis=2)
    return m0 / np.nanmax(m0), m1, w


def _afim(w):
    """Afim pixel ↔ deslocamento no céu (″, leste e norte) em torno do centro; a não linearidade da projeção SIN
    a 700″ é < 1e-5 relativa."""
    xc, yc = w.world_to_pixel(CENTRO); M = w.pixel_scale_matrix * 3600.0          # (RA, Dec) por (x, y)
    return float(xc), float(yc), M, np.linalg.inv(M)


def ceu_para_pixel(w, leste, norte):
    """Deslocamentos no plano do céu (″, leste e norte a partir do centro) → (linha, coluna) da imagem."""
    xc, yc, M, Mi = _afim(w)
    dx = Mi[0, 0] * leste + Mi[0, 1] * norte; dy = Mi[1, 0] * leste + Mi[1, 1] * norte
    return yc + dy, xc + dx


def offsets_dos_pixels(w, shape):
    xc, yc, M, _ = _afim(w); yy, xx = np.mgrid[: shape[0], : shape[1]]
    return M[0, 0] * (xx - xc) + M[0, 1] * (yy - yc), M[1, 0] * (xx - xc) + M[1, 1] * (yy - yc)


# ---------------------------------------------------------------- geometria de anéis inclinados
class Geo:
    def __init__(self, rg, pa, inc, s=1):
        self.rg, self.pa, self.inc, self.s = np.asarray(rg, float), np.asarray(pa, float), np.asarray(inc, float), s

    def at(self, r):
        return np.radians(np.interp(r, self.rg, self.pa)), np.radians(np.interp(r, self.rg, self.inc))

    def disco_para_ceu(self, r, th):
        pa, i = self.at(r); a = r * np.cos(th); b = self.s * r * np.sin(th) * np.cos(i)
        return a * np.sin(pa) + b * np.cos(pa), a * np.cos(pa) - b * np.sin(pa)    # leste, norte

    def ceu_para_disco(self, e, n, it=20):
        r = np.hypot(e, n)
        for _ in range(it):
            pa, i = self.at(r); a = e * np.sin(pa) + n * np.cos(pa); b = self.s * (e * np.cos(pa) - n * np.sin(pa))
            r = np.hypot(a, b / np.cos(i))
        return r, np.arctan2(b / np.cos(i), a)


# ---------------------------------------------------------------- PA(r) e rotação do momento 1
def ajuste_harmonico(m1, E, N, geo, rmax):
    r, _ = geo.ceu_para_disco(E, N); phi = np.arctan2(E, N); ok = np.isfinite(m1)
    out = []
    for r0 in np.arange(DR_PA / 2, rmax, DR_PA):
        sel = ok & (np.abs(r - r0) < DR_PA / 2)
        if sel.sum() < 30: continue
        p = phi[sel]; X = np.c_[np.ones(sel.sum()), np.cos(p), np.sin(p), np.cos(2 * p), np.sin(2 * p)]
        c, *_ = np.linalg.lstsq(X, m1[sel], rcond=None); res = m1[sel] - X @ c
        cov = np.linalg.inv(X.T @ X) * res.var() * PIX_POR_FEIXE
        A = np.hypot(c[1], c[2]); pa = np.degrees(np.arctan2(c[2], c[1])) % 360
        spa = np.degrees(np.sqrt((c[2] ** 2 * cov[1, 1] + c[1] ** 2 * cov[2, 2]) / A ** 4))
        out.append([r0, pa, spa, A, c[0], int(sel.sum())])
    return np.array(out)


def desenrola_pa(t):
    p = t[:, 1].copy()
    for k in range(1, len(p)):
        p[k] = p[k - 1] + ((p[k] - p[k - 1] + 180) % 360 - 180)
    t = t.copy(); t[:, 1] = p; return t


def geometria_ajustada(m1, E, N, rmax):
    geo = Geo([0, rmax], [PA_SPEIGHTS, PA_SPEIGHTS], [8.5, 8.5])
    t0 = desenrola_pa(ajuste_harmonico(m1, E, N, geo, rmax))
    if abs(((np.median(t0[:5, 1]) - PA_SPEIGHTS + 180) % 360) - 180) > 90:    # o lado que se afasta
        geo = Geo([0, rmax], [PA_SPEIGHTS + 180] * 2, [8.5, 8.5])
    for _ in range(2):
        t = desenrola_pa(ajuste_harmonico(m1, E, N, geo, rmax))
        geo = Geo(t[:, 0], t[:, 1], np.full(len(t), 8.5))
    return t


def perto(pa_ref, pa):
    return pa if abs(((pa - pa_ref + 180) % 360) - 180) <= 90 else pa + 180


def aniyan():
    f = json.loads((ROOT / "ngc628" / "aniyan2018_fig13.json").read_text())
    def med(lst):
        d = {}
        for p in lst:
            if p[0] >= 10: d.setdefault(round(p[0]), []).append(p[1])
        k = np.array(sorted(d)); return k.astype(float), np.array([np.median(d[x]) for x in k])
    return med(f["PA_preto"]), med(f["incl_preto"])


# ---------------------------------------------------------------- disco desempenado e o sistema TW
def desempenar(m0, m1, w, geo, rb):
    n = int(np.ceil(rb / PIX)); ax = np.arange(-n, n + 1) * PIX
    X, Y = np.meshgrid(ax, ax); R = np.hypot(X, Y); TH = np.arctan2(Y, X)
    e, nn = geo.disco_para_ceu(R, TH); li, co = ceu_para_pixel(w, e, nn)
    I = ndimage.map_coordinates(m0, [li, co], order=1, cval=0.0)
    ok = np.isfinite(m1); v0 = np.where(ok, m1, 0.0)
    vm = ndimage.map_coordinates(v0, [li, co], order=1, cval=0.0); mm = ndimage.map_coordinates(ok.astype(float), [li, co], order=1, cval=0.0)
    V = np.where(mm > 0.5, vm / np.maximum(mm, 1e-9), np.nan)
    _, inc = geo.at(R); I = I * np.cos(inc); I[R > rb] = 0.0
    fora = (li < 0) | (li > m0.shape[0] - 1) | (co < 0) | (co > m0.shape[1] - 1)
    return ax, I, V, inc, R, fora


def sistema(ax, I, V, inc, vsys, rb, y0max=None):
    n = len(ax) // 2; aneis = np.arange(0, rb, DR_ANEL); K = len(aneis)
    rs = np.arange(DSUB / 2, rb, DSUB); L, B, A, ys = [], [], [], []
    passo = int(round(DY0 / PIX))
    for j in range(0, n + 1, passo):
        for sg in ((1,) if j == 0 else (1, -1)):
            y0 = sg * j * PIX
            if y0max is not None and abs(y0) > y0max: continue
            row = n + sg * j; Ii = I[row]; Vy = (V[row] - vsys) / np.sin(inc[row])
            L.append(np.nansum(np.where(Ii > 0, Ii * Vy, 0.0)) * PIX)
            B.append(np.sum(Ii / np.sin(inc[row])) * PIX)
            r = rs[rs > abs(y0)]; xx = np.sqrt(r ** 2 - y0 ** 2)
            ii = lambda x: ndimage.map_coordinates(I, [np.full_like(x, row, dtype=float), x / PIX + n], order=1, cval=0.0)
            d = (ii(xx) - ii(-xx)) * r * DSUB
            a = np.zeros(K); np.add.at(a, np.minimum((r // DR_ANEL).astype(int), K - 1), d); A.append(a); ys.append(y0)
    return np.array(L), np.array(B), np.array(A), aneis + DR_ANEL / 2, np.array(ys)


def resolver(L, B, A, livre_vsys=True):
    X = np.c_[A, B] if livre_vsys else A; K = A.shape[1]
    D = np.zeros((K - 2, X.shape[1])); i = np.arange(K - 2); D[i, i], D[i, i + 1], D[i, i + 2] = 1, -2, 1
    s = np.linalg.norm(X[:, :K]) / np.sqrt(K); n = len(L); melhor = None
    for lam in s * np.logspace(-4, 1, 60):
        M = X.T @ X + lam ** 2 * D.T @ D; Mi = np.linalg.pinv(M); b = Mi @ X.T @ L
        tr = np.trace(X @ Mi @ X.T); g = n * np.sum((L - X @ b) ** 2) / (n - tr) ** 2
        if melhor is None or g < melhor[0]: melhor = (g, lam / s, b)
    _, lam, b = melhor
    return b[:K], (b[K] if livre_vsys else 0.0), lam


def omega_em(t, inc_deg, rc):
    """Ω (km/s/″) nos centros rc, de A(r) do ajuste harmônico e da inclinação."""
    A = np.interp(rc, t[:, 0], t[:, 3]); i = np.radians(np.interp(rc, *inc_deg) if isinstance(inc_deg, tuple) else inc_deg)
    return A / np.sin(i) / rc


def q_de(rc, wp, om):
    s = (rc >= Z0) & (rc <= Z1)
    return float(np.polyfit(rc[s], wp[s], 1)[0] / np.polyfit(rc[s], om[s], 1)[0]), s


def corrotacao(rc, wp, om, lo=250.0, hi=Z1):
    s = (rc >= lo) & (rc <= hi); d = (om - wp)[s]; r = rc[s]; k = np.flatnonzero(d[:-1] * d[1:] <= 0)
    return [float(r[j] + d[j] / (d[j] - d[j + 1]) * (r[j + 1] - r[j])) for j in k]


def medir(m0, m1, w, geo, vsys, rb, y0max=None, livre=True):
    ax, I, V, inc, R, fora = desempenar(m0, m1, w, geo, rb)
    L, B, A, rc, ys = sistema(ax, I, V, inc, vsys, rb, y0max)
    wp, dv, lam = resolver(L, B, A, livre)
    return rc, wp / KPC_AS, dv, lam, (ax, I, V, inc, R, fora)


# ---------------------------------------------------------------- sintéticos
def sintetico_base(m0, w, geo, t, rb, vsys):
    """Σ polar (morfologia real desempenada), Ω suavizada e o fluxo radial rΣv_r para os dois cenários."""
    rr = np.arange(PIX, rb, PIX); th = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    Rg, Tg = np.meshgrid(rr, th, indexing="ij")
    e, n = geo.disco_para_ceu(Rg, Tg); li, co = ceu_para_pixel(w, e, n)
    S = ndimage.map_coordinates(m0, [li, co], order=1, cval=0.0) * np.cos(geo.at(Rg)[1])
    om_anel = t[:, 3] / np.sin(np.radians(8.5)) / t[:, 0]
    om_s = np.convolve(np.r_[om_anel[0], om_anel, om_anel[-1]], np.ones(3) / 3, "valid")    # média corrida de 30″
    Om = np.interp(rr, t[:, 0], om_s)
    D = np.interp(R_STAR, rr, Om) - np.interp(R_CR, rr, Om)
    dS = (np.roll(S, -1, 1) - np.roll(S, 1, 1)) / (2 * (th[1] - th[0]))
    cen = {"R": np.where(rr < R_STAR, Om - D, np.interp(R_CR, rr, Om)), "S": Om - D}
    # Continuidade: (1/r)∂(r f_r)/∂r + (1/r)∂f_θ/∂θ = (Ωp − Ω) ∂Σ/∂θ, com f = Σ v − Σ rΩ θ̂. A integração radial de
    # dentro para fora deixa um fluxo C(θ) saindo pela borda; ele é devolvido por um fluxo azimutal f_θ = w′(r) G(θ),
    # com w(r) a massa acumulada (w(R_borda) = 1) e G = ∫C dθ, para que nada atravesse a borda (correção, defeito 69).
    wr = np.cumsum(rr * S.mean(1)); wr = wr / wr[-1]; dw = np.gradient(wr, rr)
    flux = {}
    for k, wp in cen.items():
        g = rr[:, None] * (wp - Om)[:, None] * dS
        Fin = np.concatenate([np.zeros((1, len(th))), np.cumsum(0.5 * (g[1:] + g[:-1]) * PIX, 0)])
        C = Fin[-1]; G = np.cumsum(C) * (th[1] - th[0]); G = G - G.mean()
        flux[k] = ((Fin - wr[:, None] * C[None, :]) / rr[:, None], dw[:, None] * G[None, :])   # (Σ v_r, Σ v_θ′)
    return rr, th, S, Om, flux, cen, D


def mom1_sintetico(base, cen, geo, E, N, mask, vsys, ruido):
    rr, th, S, Om, flux, _, _ = base
    r, t_ = geo.ceu_para_disco(E, N); _, i = geo.at(r)
    ir = np.clip((r - rr[0]) / PIX, 0, len(rr) - 1); it = ((t_ + np.pi) / (th[1] - th[0])) % len(th)
    mc = lambda F: ndimage.map_coordinates(F, [ir, it], order=1, mode="grid-wrap")
    s_, fr, ft = mc(S), mc(flux[cen][0]), mc(flux[cen][1])
    vr = np.where(s_ > 1e-4, fr / np.maximum(s_, 1e-4), 0.0); vt = np.where(s_ > 1e-4, ft / np.maximum(s_, 1e-4), 0.0)
    om = np.interp(r, rr, Om)
    v = vsys + np.sin(i) * ((r * om + vt) * np.cos(t_) + vr * np.sin(t_)) + ruido
    return np.where(mask, v, np.nan)


def ruido_girado(res, ang, rng, sig):
    ok = np.isfinite(res); a = ndimage.rotate(np.where(ok, res, 0.0), ang, reshape=False, order=1)
    m = ndimage.rotate(ok.astype(float), ang, reshape=False, order=1)
    g = ndimage.gaussian_filter(rng.normal(size=res.shape), 11.88 / PIX / 2.355)
    g *= sig / g.std()
    return np.where(m > 0.5, a / np.maximum(m, 1e-9), g)


# ---------------------------------------------------------------- principal
def main():
    assert (ROOT / "PREDICAO_teste50_padrao_externo.md").exists(), "sem predição, sem teste"
    t0 = time.time(); m0, m1, w = carregar(sys.argv[1], sys.argv[2]); E, N = offsets_dos_pixels(w, m0.shape)
    res = {"checagens": {}}
    borda = np.r_[m0[0], m0[-1], m0[:, 0], m0[:, -1]]
    res["checagens"]["fluxo_na_borda_da_imagem"] = float(borda.sum() / m0.sum())
    res["checagens"]["frac_m0_pos_sem_m1"] = float(np.mean(~np.isfinite(m1[m0 > 0])))
    # geometria G1 provisória para R_borda
    t = geometria_ajustada(m1, E, N, 700.0)
    g1 = Geo(t[:, 0], t[:, 1], np.full(len(t), 8.5))
    r_, th_ = g1.ceu_para_disco(E, N); cob = []
    for r0 in np.arange(DR_ANEL / 2, 900, DR_ANEL):
        sel = np.abs(r_ - r0) < DR_ANEL / 2
        if not sel.any(): break
        h = np.histogram(th_[sel & (m0 > 0)], bins=36, range=(-np.pi, np.pi))[0]
        cob.append((r0, float(np.mean(h > 0))))
    cob = np.array(cob); rb = float(cob[cob[:, 1] >= 0.5, 0].max() + DR_ANEL / 2)
    res["checagens"]["R_borda"] = rb
    res["checagens"]["fluxo_alem_de_R_borda"] = float(m0[r_ > rb].sum() / m0.sum())
    t = geometria_ajustada(m1, E, N, rb); vsys = float(np.median(t[t[:, 0] < 300, 4]))
    res["ajuste_harmonico"] = t.round(4).tolist(); res["vsys_ajustado"] = vsys
    print(f"R_borda {rb:.1f}″, V_sis {vsys:.1f}, fluxo na borda {res['checagens']['fluxo_na_borda_da_imagem']:.2e}, "
          f"m0>0 sem m1 {res['checagens']['frac_m0_pos_sem_m1']:.3f}", flush=True)
    # sentido de y: braços arrastados
    g1 = Geo(t[:, 0], t[:, 1], np.full(len(t), 8.5), 1)
    ax, I, V, inc, R, fora = desempenar(m0, m1, w, g1, rb); TH = np.arctan2(*np.meshgrid(ax, ax)[::-1])
    fases = []
    for r0 in np.arange(60, 250, 7.5):
        s = np.abs(R - r0) < 3.75; fases.append(0.5 * np.arctan2(np.sum(I[s] * np.sin(2 * TH[s])), np.sum(I[s] * np.cos(2 * TH[s]))))
    f = np.unwrap(2 * np.array(fases)) / 2; incl_fase = float(np.polyfit(np.arange(60, 250, 7.5), f, 1)[0])
    S_Y = 1 if incl_fase < 0 else -1; res["sentido_y"] = {"inclinacao_fase_m2_com_s+1": incl_fase, "s": S_Y}
    print(f"fase m=2: inclinação {incl_fase:+.4f} rad/″ com s=+1 → s = {S_Y}", flush=True)
    (pa_a_r, pa_a), (i_a_r, i_a) = aniyan()
    pa_ref = float(np.median(t[:5, 1])); pa_a = np.array([perto(pa_ref, p) for p in pa_a])
    i_suav = np.array([np.mean(i_a[np.abs(i_a_r - x) <= 15]) for x in i_a_r])
    rgf = np.r_[t[:, 0], rb + 50]; extend = lambda y: np.r_[y, y[-1]]
    G = {"G1": Geo(rgf, extend(t[:, 1]), np.full(len(rgf), 8.5), S_Y),
         "G2": Geo(rgf, extend(t[:, 1]), np.interp(rgf, i_a_r, i_suav), S_Y),
         "G3": Geo(np.r_[pa_a_r, rb + 50], np.r_[pa_a, pa_a[-1]], np.full(len(pa_a_r) + 1, 8.5), S_Y),
         "G4": Geo(rgf, extend(t[:, 1] + t[:, 2]), np.full(len(rgf), 8.5), S_Y),
         "G5": Geo(rgf, extend(t[:, 1] - t[:, 2]), np.full(len(rgf), 8.5), S_Y),
         "G6": Geo([0, rb + 50], [perto(pa_ref, PA_SPEIGHTS)] * 2, [I_SPEIGHTS] * 2, S_Y)}
    incs = {"G1": 8.5, "G2": (rgf, np.interp(rgf, i_a_r, i_suav)), "G3": 8.5, "G4": 8.5, "G5": 8.5, "G6": I_SPEIGHTS}
    # J1: reprodução de Speights et al. em G6
    rc, wp, dv, lam, _ = medir(m0, m1, w, G["G6"], VSYS_SPEIGHTS, rb, y0max=RMAX_SP, livre=False)
    sp = json.loads((ROOT / "ngc628" / "speights2025_fig12d.json").read_text())["Omega_p_r_kpc_valor_erro"]
    sp = np.array(sp); ra = sp[:, 0] / KPC_AS; sel = (ra >= 100) & (ra <= 310)
    nosso = np.interp(ra[sel], rc, wp); dentro = np.abs(nosso - sp[sel, 1]) <= sp[sel, 2]
    res["J1_detalhe"] = {"r_as": ra[sel].tolist(), "speights": sp[sel, 1].tolist(), "erro": sp[sel, 2].tolist(), "nosso": nosso.tolist(),
                         "frac_dentro": float(dentro.mean()), "lambda": lam}
    print(f"J1: {dentro.mean():.2f} dos pontos de Speights dentro da barra ({time.time()-t0:.0f}s)", flush=True)
    # medida real nas seis geometrias
    res["geometrias"] = {}
    for k, g in G.items():
        rc, wp, dv, lam, _ = medir(m0, m1, w, g, vsys, rb)
        om = omega_em(t, incs[k], rc) / KPC_AS; q, s = q_de(rc, wp, om)
        ii = incs[k] if not isinstance(incs[k], tuple) else np.interp(rc[s], *incs[k])
        nivel = float(np.mean(wp[s] * np.sin(np.radians(ii)) / np.sin(np.radians(I_SPEIGHTS))))
        res["geometrias"][k] = {"r": rc.tolist(), "Omega_p": wp.tolist(), "Omega": om.tolist(), "q": q, "nivel_unid_speights": nivel,
                                "corrotacao": corrotacao(rc, wp, om), "dV": float(dv), "lambda": lam}
        print(f"{k}: q = {q:+.3f}, nível (i=6°) {nivel:.2f}, corrotação {corrotacao(rc, wp, om)}, δV {dv:+.2f}, λ {lam:.2e}", flush=True)
    # sintéticos
    gs = G["G1"]; mask = (m0 > 0) & np.isfinite(m1)
    rr_, th_2 = gs.ceu_para_disco(E, N); _, ii_ = gs.at(rr_)
    mod = np.interp(rr_, t[:, 0], t[:, 4]) + np.interp(rr_, t[:, 0], t[:, 3]) * np.cos(np.arctan2(E, N) - np.radians(np.interp(rr_, t[:, 0], t[:, 1])))
    resid = np.where(mask, m1 - mod, np.nan); sig = float(np.nanstd(resid))
    base = sintetico_base(m0, w, gs, t, rb, vsys); rng = np.random.default_rng(SEMENTE)
    res["sinteticos"] = {"rms_residuo": sig, "Delta": float(base[6]), "R": [], "S": []}
    print(f"resíduo rms {sig:.2f} km/s; Δ = {base[6]/KPC_AS:.2f} km/s/kpc", flush=True)
    sistem = {}
    for j in range(NREAL):
        ang = rng.uniform(0, 360); nz = ruido_girado(resid, ang, rng, sig)
        for cen in ("R", "S"):
            v = mom1_sintetico(base, cen, gs, E, N, mask, vsys, nz)
            rc, wp, dv, lam, _ = medir(m0, v, w, gs, vsys, rb)
            om = omega_em(t, 8.5, rc) / KPC_AS; q, _ = q_de(rc, wp, om); res["sinteticos"][cen].append(q)
            if j < 3:
                for kk in ("G3", "G6"):
                    rc2, wp2, *_ = medir(m0, v, w, G[kk], vsys, rb); om2 = omega_em(t, incs[kk], rc2) / KPC_AS
                    sistem.setdefault(f"{cen}_{kk}", []).append(q_de(rc2, wp2, om2)[0])
        if j % 10 == 0: print(f"  sintético {j}: q_R {res['sinteticos']['R'][-1]:+.2f} q_S {res['sinteticos']['S'][-1]:+.2f} ({time.time()-t0:.0f}s)", flush=True)
    res["sinteticos"]["outras_geometrias"] = sistem
    qR, qS = np.array(res["sinteticos"]["R"]), np.array(res["sinteticos"]["S"])
    res["sinteticos"].update({"frac_R_rigido": float(np.mean(qR < 0.5)), "frac_S_cisalha": float(np.mean(qS >= 0.5)),
                              "mediana_R": float(np.median(qR)), "mediana_S": float(np.median(qS))})
    g = res["geometrias"]; cls = lambda k: g[k]["q"] < 0.5
    J = {"J1": res["J1_detalhe"]["frac_dentro"] >= 0.70,
         "J2": res["sinteticos"]["frac_R_rigido"] >= 0.84 and res["sinteticos"]["frac_S_cisalha"] >= 0.84,
         "J3": g["G1"]["q"] < 0.5, "J4": abs(g["G1"]["nivel_unid_speights"] - 17) <= 3,
         "J5": sum(cls(k) == cls("G1") for k in ("G1", "G2", "G3", "G4", "G5")) >= 4}
    res["J"] = {k: bool(v) for k, v in J.items()}
    print(f"sintéticos: R rígido {res['sinteticos']['frac_R_rigido']:.2f} (mediana {np.median(qR):+.2f}); "
          f"S cisalha {res['sinteticos']['frac_S_cisalha']:.2f} (mediana {np.median(qS):+.2f})")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste50.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    if len(sys.argv) > 3:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), dpi=120)
        a = axs[0]
        for k, c in zip(G, ["#b3261e", "#e08a00", "#1f7a4d", "#999", "#999", "#5b3aa0"]):
            rc = np.array(g[k]["r"]); s = (rc > 150) & (rc < 450)
            a.plot(rc[s], np.array(g[k]["Omega_p"])[s], "-", color=c, lw=2 if k == "G1" else 1, label=f"Ωp {k}")
        rc = np.array(g["G1"]["r"]); s = (rc > 150) & (rc < 450); a.plot(rc[s], np.array(g["G1"]["Omega"])[s], "k:", lw=2, label="Ω (G1)")
        a.axvspan(Z0, Z1, color="#eee", zorder=0); a.set_xlabel("raio (″)"); a.set_ylabel("km/s/kpc (i da geometria)"); a.legend(fontsize=7)
        b = axs[1]; b.hist(qR, 30, alpha=0.6, label="sintético R (rígido)"); b.hist(qS, 30, alpha=0.6, label="sintético S (cisalha)")
        b.axvline(0.5, color="k", lw=0.8); b.axvline(g["G1"]["q"], color="#b3261e", lw=2, label="dado real (G1)")
        b.set_xlabel("q = inclinação de Ωp / inclinação de Ω em 310″–395″"); b.legend(fontsize=8)
        plt.tight_layout(); plt.savefig(sys.argv[3])


if __name__ == "__main__":
    main()
