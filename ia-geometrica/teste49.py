"""Teste 49: a geometria da janela (rígido por fora, deslizando por dentro) contra as velocidades de padrão do H I medidas
por Speights, Aust & Lu (2025, ApJ 981, 115), Figura 12d (PCM), na sobreposição com a zona estável (254″–310″).
Predição: PREDICAO_teste49_velocidade_de_padrao.md (commit f099a9c), escrita antes deste arquivo.

A Figura 12 do artigo é uma imagem JPEG (página 12 do PDF); este instrumento a digitaliza por cor:

    python ia-geometrica/teste49.py <PDF de Speights et al. 2025>   # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste47 as T47
import teste46 as T46
import teste48 as T48

ROOT = Path(__file__).resolve().parent
PC_POR_AS = 34.2                      # Speights et al., Tabela 2
Z0, Z1, RMAX = 254.0, 395.0, 310.0    # zona estável; r_max do H I no PCM (Tabela 4)
NANEIS, PASSO_K = 400, 0.0025
# calibração da Figura 12d na imagem 1334×1486 (traços dos eixos, medidos no instrumento):
X_KPC = ([113.5, 224.5, 336.5, 447.5, 559.5, 671.5], [0, 2, 4, 6, 8, 10])
Y_OM = ([979.5, 1057.0, 1134.5, 1212.5, 1290.5, 1368.5], [100, 80, 60, 40, 20, 0])
CAIXA = (104, 712, 960, 1404)         # x0, x1, y0, y1 do painel (d), dentro dos eixos


def imagem(pdf):
    import pymupdf
    d = pymupdf.open(pdf); pg = d[11]; xref = pg.get_images()[0][0]
    pix = pymupdf.Pixmap(d, xref)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].astype(int)
    assert a.shape[:2] == (1486, 1334), a.shape
    return a


def digitalizar(a):
    px = np.polyfit(*X_KPC, 1); py = np.polyfit(*Y_OM, 1)
    x0, x1, y0, y1 = CAIXA; R, G, B = a[..., 0], a[..., 1], a[..., 2]
    # Ωp: cada barra de erro vermelha; o valor é o meio da barra (barras simétricas), o erro é meia barra
    red = ((R > 120) & (G < 90) & (B < 90))[y0:y1, x0:x1]
    cols = np.flatnonzero(red.sum(0) > 15); grupos = np.split(cols, np.flatnonzero(np.diff(cols) > 2) + 1)
    pts = []
    for g in grupos:
        c = g[np.argmax(red[:, g].sum(0))]; ys = np.flatnonzero(red[:, c])
        top, bot = ys.min() + y0, ys.max() + y0; xc = c + x0
        pts.append([float(np.polyval(px, xc)), float(np.polyval(py, 0.5 * (top + bot))), float(abs(np.polyval(py, top) - np.polyval(py, bot)) / 2)])
    # Ω: os pontos da curva pontilhada preta (centroides dos pontos)
    blk = (a.max(2) < 90)[y0:y1, x0:x1].copy(); blk[-40:, 480:] = False   # tira o rótulo "(d) H I"
    blk[:, :3] = False; blk[-3:, :] = False
    from scipy import ndimage
    lab, n = ndimage.label(blk); om = []
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == k; s = m.sum()
        if 3 <= s <= 40:
            yy, xx = np.nonzero(m); xc, yc = xx.mean() + sl[1].start + x0, yy.mean() + sl[0].start + y0
            om.append([float(np.polyval(px, xc)), float(np.polyval(py, yc))])
    om = np.array(sorted(om)); pts = np.array(pts)
    om = om[(om[:, 0] < 10.62) & (om[:, 1] > 0) & (om[:, 1] < 99)]          # tira traços dos eixos
    for _ in range(2):                                                       # tira manchas fora da curva
        viz = lambda i: np.median(om[(np.abs(om[:, 0] - om[i, 0]) < 0.45) & (np.arange(len(om)) != i), 1])
        om = om[[abs(om[i, 1] - viz(i)) < 1.5 for i in range(len(om))]]
    return pts, om


def modelo(rq, vq):
    om = vq / rq; dw = om - om.mean(); esc = dw.max() - dw.min(); dw = dw / esc
    K, rho, f = T47.ramo(dw); rk, fk = T47.no_K(K, rho, f)
    jan = (fk >= 0.5) & (fk < 1 - 1e-12); trav = fk >= 1 - 1e-12
    ini, KL = float(T47.KGF[jan][0]), float(T47.KGF[trav][0])
    sob = rq <= RMAX; linhas = []
    for k in np.arange(ini, KL + 1e-9, PASSO_K):
        r, o, lk = T46.resolver(dw, k * T47.KC)
        if lk is None: continue
        a_ = k * T47.KC * r; d = dw - o
        weff = np.where(lk, o, o + np.sign(d) * np.sqrt(np.clip(d * d - a_ * a_, 0, None)))
        atraso = dw - weff
        S = np.polyfit(rq[sob], weff[sob], 1)[0] / np.polyfit(rq[sob], dw[sob], 1)[0]
        linhas.append({"K": float(k), "rho": float(r), "a": float(a_), "frac_trav": float(lk.mean()),
                       "r_estrela": float(rq[lk].min()) if lk.any() else None, "sobreposicao_desliza": bool(not lk[sob].any()),
                       "S_sobreposicao": float(S), "atraso_max_sobrep": float(atraso[sob].max()),
                       "inclinacao_atraso_sobrep": float(np.polyfit(rq[sob], atraso[sob], 1)[0])})
    ks = [l["K"] for l in linhas if l["sobreposicao_desliza"]]
    k310 = max(ks) if ks and linhas[0]["sobreposicao_desliza"] else ini
    return {"inicio": ini, "K_L": KL, "largura": KL - ini, "K_310": k310, "frac_janela_compativel": (k310 - ini) / (KL - ini),
            "escala_dw_em_Omega": float(esc), "perfil": linhas}


def main():
    assert (ROOT / "PREDICAO_teste49_velocidade_de_padrao.md").exists(), "sem predição, sem teste"
    a = imagem(sys.argv[1]); pts, om = digitalizar(a)
    (ROOT / "ngc628" / "speights2025_fig12d.json").write_text(json.dumps(
        {"fonte": "Speights, Aust & Lu 2025, ApJ 981, 115, Figura 12d (H I, PCM); digitalizada por cor (teste49.py)",
         "Omega_p_r_kpc_valor_erro": pts.round(3).tolist(), "Omega_r_kpc_valor": om.round(3).tolist()}, ensure_ascii=False, indent=1))
    print(f"{len(pts)} pontos de Ωp, {len(om)} pontos de Ω digitalizados")
    k0, k1 = Z0 * PC_POR_AS / 1e3, RMAX * PC_POR_AS / 1e3
    s = (pts[:, 0] >= k0) & (pts[:, 0] <= k1); P = pts[s]
    Om_p = np.interp(P[:, 0], om[:, 0], om[:, 1])
    S_dados = np.polyfit(P[:, 0], P[:, 1], 1)[0] / np.polyfit(P[:, 0], Om_p, 1)[0]
    gap = Om_p - P[:, 1]
    dados = {"n_pontos_sobreposicao": int(s.sum()), "r_kpc": P[:, 0].tolist(), "Omega_p": P[:, 1].tolist(), "erro": P[:, 2].tolist(),
             "Omega": Om_p.tolist(), "S": float(S_dados), "frac_abaixo": float(np.mean(gap > 0)),
             "inclinacao_atraso_kms_kpc2": float(np.polyfit(P[:, 0], gap, 1)[0]), "atraso_medio": float(gap.mean())}
    print("dados:", {k: v for k, v in dados.items() if not isinstance(v, list)})
    rq = np.linspace(Z0, Z1, NANEIS); plano = modelo(rq, np.ones_like(rq))
    inc, v, sv = T48.dados(); rq2 = np.linspace(Z0, 350.0, NANEIS)
    aniyan = modelo(rq2, np.interp(rq2, v[:, 0], v[:, 1]))
    for nome, m in (("plana", plano), ("Aniyan", aniyan)):
        p0 = m["perfil"][0]
        print(f"{nome}: janela {m['inicio']:.4f}–{m['K_L']:.4f}; K_310 {m['K_310']:.4f}; fração compatível {m['frac_janela_compativel']:.3f}; "
              f"no começo: r* {p0['r_estrela']}, a {p0['a']:.3f}, S {p0['S_sobreposicao']:.3f}, atraso máx {p0['atraso_max_sobrep']:.3f}, "
              f"inclinação do atraso {p0['inclinacao_atraso_sobrep']:+.2e}")
    J = {"J1": dados["S"] >= 0.5, "J2": plano["frac_janela_compativel"] <= 1 / 3,
         "J3": dados["frac_abaixo"] >= 0.8, "J4": dados["inclinacao_atraso_kms_kpc2"] > 0}
    res = {"dados": dados, "modelo_plana": plano, "modelo_aniyan": aniyan, "J": {k: bool(x) for k, x in J.items()}}
    print("== " + " | ".join(f"{k} {'PASSA' if x else 'REPROVA'}" for k, x in res["J"].items()))
    (ROOT / "resultados_teste49.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    if len(sys.argv) > 2:                                   # sobreposto para conferência visual
        from PIL import Image, ImageDraw
        im = Image.fromarray(a.astype(np.uint8)); dr = ImageDraw.Draw(im)
        ix = np.polyfit(X_KPC[1], X_KPC[0], 1); iy = np.polyfit(Y_OM[1], Y_OM[0], 1)
        for r_, w_, e_ in pts:
            X, Y = np.polyval(ix, r_), np.polyval(iy, w_); dr.ellipse([X - 3, Y - 3, X + 3, Y + 3], outline=(0, 160, 255), width=2)
        for r_, w_ in om:
            X, Y = np.polyval(ix, r_), np.polyval(iy, w_); dr.rectangle([X - 2, Y - 2, X + 2, Y + 2], fill=(0, 200, 0))
        im.crop((60, 940, 740, 1450)).save(sys.argv[2])


if __name__ == "__main__":
    main()
