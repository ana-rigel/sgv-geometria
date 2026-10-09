#!/usr/bin/env python3
"""Baixa de data.binance.vision os dados da Fase 1 (só biblioteca padrão).

  klines spot 1h  BTCUSDT e ETHUSDT, 2020-01 a 2026-07  -> data/<SYM>/klines/
  funding USDT-M  BTCUSDT e ETHUSDT, 2020-01 a 2026-07  -> data/<SYM>/funding/

Cada zip é conferido com o SHA-256 publicado (.CHECKSUM) e extraído. Arquivo
já íntegro é pulado. Uso: python3 scripts/baixar_dados_fase1.py
"""
from __future__ import annotations

import hashlib
import io
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://data.binance.vision/data"
SYMBOLS = ("BTCUSDT", "ETHUSDT")
START, END = "2020-01", "2026-07"
ROOT = Path(__file__).resolve().parents[1] / "data"


def months(a: str, b: str) -> list[str]:
    y, m = map(int, a.split("-")); ye, me = map(int, b.split("-")); out = []
    while (y, m) <= (ye, me):
        out.append(f"{y:04d}-{m:02d}"); m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "sgv-operavel/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def get(url: str, dest_dir: Path) -> str:
    name = url.rsplit("/", 1)[1]
    csv_name = name.replace(".zip", ".csv")
    if (dest_dir / csv_name).exists():
        return f"já estava ok {name}"
    try:
        expected = fetch(url + ".CHECKSUM").decode().split()[0]
    except urllib.error.HTTPError as e:
        return f"NÃO EXISTE   {name} ({e.code})"
    for attempt in range(1, 4):
        try:
            data = fetch(url)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("checksum")
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(dest_dir)
            return f"ok           {name}"
        except Exception as e:  # rede instável: tenta de novo
            last = e
            time.sleep(2 * attempt)
    return f"FALHOU       {name} ({last})"


def main() -> int:
    falhas = 0
    for sym in SYMBOLS:
        for kind, url_dir in (("klines", f"{BASE}/spot/monthly/klines/{sym}/1h"),
                              ("funding", f"{BASE}/futures/um/monthly/fundingRate/{sym}")):
            dest = ROOT / sym / kind
            dest.mkdir(parents=True, exist_ok=True)
            for mo in months(START, END):
                fname = f"{sym}-1h-{mo}.zip" if kind == "klines" else f"{sym}-fundingRate-{mo}.zip"
                msg = get(f"{url_dir}/{fname}", dest)
                falhas += msg.startswith(("FALHOU", "NÃO EXISTE"))
                print(f"{sym} {kind:7s} {msg}", flush=True)
    print("Resumo:", "tudo íntegro." if not falhas else f"{falhas} arquivo(s) com problema.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
