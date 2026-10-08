"""Figuras do relatório (lê os JSON/CSV de reports/<fonte>/)."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import out_path  # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False,
})


def fig_confiabilidade():
    t = pd.read_csv(out_path("d7_confiabilidade_rank_gauss.csv"))
    rel = t.pivot(index="multiplicador_h", columns="grandeza", values="confiabilidade")
    mag = t.pivot(index="multiplicador_h", columns="grandeza", values="mediana_abs")
    x = rel.index.values
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 5.0))
    for col, color, lab in [("H slog R", BLUE, "Curvatura R — métrica H (legado)"),
                            ("F slog R", ORANGE, "Curvatura R — métrica F (Fisher local)"),
                            ("ΔF", AQUA, "ΔF: curvatura de F além da referência gaussiana")]:
        a1.plot(x, rel[col], color=color, lw=2, marker="o", ms=8, mec=SURF, mew=2, label=lab)
    a1.axhline(0.8, color=INK2, lw=1, ls=(0, (4, 3)))
    a1.text(x[0], 0.82, "0,8 = mínimo para um teste", color=INK2, fontsize=9)
    a1.set_xscale("log", base=2); a1.set_xticks(x, [f"{v:g}×" for v in x])
    a1.set_ylim(-0.1, 1.05); a1.set_xlabel("largura de banda (× Scott da janela de 1500)")
    a1.set_title("Confiabilidade entre metades da janela", loc="left", color=INK, fontsize=11)
    a1.set_ylabel("correlação de postos A×B")
    a1.legend(loc="upper left", bbox_to_anchor=(0.0, -0.17), fontsize=8.5)
    for col, color in [("H slog R", BLUE), ("F slog R", ORANGE)]:
        a2.plot(x, np.expm1(mag[col]), color=color, lw=2, marker="o", ms=8, mec=SURF, mew=2)
    a2.set_xscale("log", base=2); a2.set_yscale("log"); a2.set_xticks(x, [f"{v:g}×" for v in x])
    a2.set_xlabel("largura de banda (× Scott da janela de 1500)"); a2.set_ylabel("|R| mediano")
    a2.set_title("Tamanho da curvatura", loc="left", color=INK, fontsize=11)
    a2.annotate("H achata: tende ao espaço plano", (x[-1], np.expm1(mag["H slog R"].iloc[-1])),
                xytext=(-10, 14), textcoords="offset points", ha="right", color=INK2, fontsize=9)
    a2.annotate("F não achata (mas boa parte é posição: ver ΔF)", (x[-1], np.expm1(mag["F slog R"].iloc[-1])),
                xytext=(-10, 10), textcoords="offset points", ha="right", color=INK2, fontsize=9)
    fig.suptitle("D7 — Confiabilidade e tamanho da curvatura por largura de banda (gaussianização por postos)",
                 x=0.01, ha="left", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path("fig_d7_confiabilidade.png"), dpi=150)


def fig_numerica():
    d = json.loads(out_path("d2_numerica.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.0), sharey=True)
    for ax, key, title in [(axes[0], "legado", "Escala do legado (h = 0,45)"),
                           (axes[1], "padronizada", "Coordenadas padronizadas (h de Scott)")]:
        m = pd.DataFrame(d[key]["malhas"])
        cells = m["malha"].tolist()
        xs = np.arange(len(cells))
        ax.plot(xs, m["erro_mediano_abs"], color=BLUE, lw=2, marker="o", ms=8, mec=SURF, mew=2,
                label="erro da malha vs. exato (mediana)")
        exact = d[key]["R_exato"]["mediana_abs"]
        ax.axhline(exact, color=ORANGE, lw=2, label="|R| exato (mediana)")
        ax.set_ylim(1e-10, 1e8)
        ax.set_yscale("log"); ax.set_xticks(xs, cells); ax.set_xlabel("resolução da malha")
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        for xi, c in zip(xs, m["correlacao_postos_com_exato"]):
            ax.annotate(f"r={c:+.2f}", (xi, m["erro_mediano_abs"].iloc[xi]), xytext=(0, 9),
                        textcoords="offset points", ha="center", color=INK2, fontsize=8.5)
    axes[0].set_ylabel("curvatura escalar |R|")
    axes[0].legend(loc="center left", fontsize=8.5)
    fig.suptitle("D2 — A curvatura da malha do legado não converge para a exata (r = correlação de postos)",
                 x=0.01, ha="left", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path("fig_d2_malha_vs_exata.png"), dpi=150)


if __name__ == "__main__":
    fig_confiabilidade()
    fig_numerica()
