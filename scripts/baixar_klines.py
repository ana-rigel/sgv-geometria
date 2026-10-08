#!/usr/bin/env python3
"""Baixa os klines de EXPLORAÇÃO da Fase 1 (BTCUSDT spot) de data.binance.vision.

Uso (na raiz do repositório, Linux/WSL/Windows, só biblioteca padrão do Python):

    python3 scripts/baixar_klines.py            # baixa 1m (mai–jul/2026) e 1h (2020–2024)
    python3 scripts/baixar_klines.py --so 1m    # só o 1m
    python3 scripts/baixar_klines.py --so 1h    # só o 1h

Os arquivos vão para data/ (fora do git). Cada .zip é conferido com o SHA-256
publicado pela Binance (.CHECKSUM) e testado como zip; arquivo corrompido é
apagado e baixado de novo (até 3 tentativas). Arquivos já baixados e íntegros
são pulados, então pode rodar de novo à vontade.

PERÍODO RESERVADO: o script se recusa a baixar meses do período confirmatório
(1m a partir de 2026-08; 1h a partir de 2025-01). Esses dados não devem ser
abertos antes do pré-registro (PLANO.md).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://data.binance.vision/data/spot/monthly/klines"
SYMBOL = "BTCUSDT"

# Exploração (Fase 1) — proposta do PLANO.md
EXPLORACAO = {
    "1m": ("2026-05", "2026-07"),
    "1h": ("2020-01", "2024-12"),
}
# Início do período reservado ao confirmatório: nunca baixar antes do pré-registro
RESERVADO_A_PARTIR = {"1m": "2026-08", "1h": "2025-01"}

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data"


def months(start: str, end: str) -> list[str]:
    y, m = map(int, start.split("-"))
    ye, me = map(int, end.split("-"))
    out = []
    while (y, m) <= (ye, me):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "sgv-geometria/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_good(path: Path, expected: str | None) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    if expected and sha256(path) != expected:
        return False
    try:
        with zipfile.ZipFile(path) as z:
            return z.testzip() is None
    except zipfile.BadZipFile:
        return False


def download_month(interval: str, month: str) -> str:
    name = f"{SYMBOL}-{interval}-{month}.zip"
    url = f"{BASE}/{SYMBOL}/{interval}/{name}"
    path = DEST / name
    try:
        expected = fetch(url + ".CHECKSUM").decode().split()[0].strip()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"NÃO EXISTE   {name} (mês ainda não publicado?)"
        expected = None
    except Exception:
        expected = None

    if is_good(path, expected):
        return f"já estava ok {name}"

    last: Exception | None = None
    for attempt in range(1, 4):
        try:
            data = fetch(url)
            path.write_bytes(data)
            if is_good(path, expected):
                tag = "ok          " if expected else "ok (sem checksum)"
                return f"{tag} {name} ({len(data) / 1e6:.1f} MB)"
            path.unlink(missing_ok=True)
        except Exception as e:  # rede instável: tenta de novo
            path.unlink(missing_ok=True)
            last = e
        time.sleep(2 * attempt)
    return f"FALHOU       {name} ({last or 'checksum ou zip inválido'})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--so", choices=sorted(EXPLORACAO), help="baixar só um intervalo")
    args = ap.parse_args()

    DEST.mkdir(exist_ok=True)
    intervals = [args.so] if args.so else list(EXPLORACAO)
    failures = 0
    for interval in intervals:
        start, end = EXPLORACAO[interval]
        lista = months(start, end)
        bloqueados = [m for m in lista if m >= RESERVADO_A_PARTIR[interval]]
        if bloqueados:
            print(f"ERRO: {interval} inclui meses do período reservado: {bloqueados}", file=sys.stderr)
            return 2
        print(f"\n== {SYMBOL} {interval}: {start} a {end} ({len(lista)} meses) -> {DEST}")
        for m in lista:
            msg = download_month(interval, m)
            failures += msg.startswith(("FALHOU", "NÃO EXISTE"))
            print("  " + msg, flush=True)

    print("\nResumo:", "tudo íntegro." if failures == 0 else f"{failures} arquivo(s) com problema — rode de novo.")
    print("Próximo passo: anexe os .zip de data/ na conversa (ou, no seu computador:")
    print("  export SGV_DATA=$(ls data/BTCUSDT-1m-*.zip | paste -sd:)")
    print("  python3 diagnostics/run_all.py d7_confiabilidade )")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
