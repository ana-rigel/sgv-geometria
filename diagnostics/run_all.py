"""Roda D1–D8 e as figuras em sequência.

    python diagnostics/run_all.py                         # calibração em dados sintéticos
    SGV_DATA=data/BTCUSDT-1m-2026-05.zip:data/BTCUSDT-1m-2026-06.zip \
    SGV_TAIL=6000 python diagnostics/run_all.py           # dados reais (últimas 6000 barras)

Tempo aproximado (CPU comum): 20–30 min no total, a maior parte em D3 e D8.
"""
import runpy
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

STEPS = ["d1_inventario_legado", "d2_numerica_grade_vs_exata", "d3_vazamento_futuro",
         "d4_geometria_exata", "d5_volatilidade", "d6_equacao_de_campo",
         "d7_confiabilidade", "d8_existencia", "figuras"]

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for s in STEPS:
        if only and s not in only:
            continue
        t = time.time()
        print(f"\n=== {s} ===", flush=True)
        runpy.run_path(str(HERE / f"{s}.py"), run_name="__main__")
        print(f"--- {s}: {time.time() - t:.0f}s", flush=True)
