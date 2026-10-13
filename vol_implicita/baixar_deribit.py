"""Baixa da Deribit (API pública, sem chave) o que a E-VOL-01 precisa, para mai–jul/2026:
  (a) DVOL (índice de vol implícita de 30 dias do BTC) em resolução de 60 s → vol_implicita/dados/dvol.csv
  (b) todos os negócios de opções de BTC, com a vol implícita de cada negócio → vol_implicita/dados/opcoes_trades.csv.gz
Uso: python vol_implicita/baixar_deribit.py --inicio 2026-05-01 --fim 2026-08-01
"""
import argparse
import gzip
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HIST = "https://history.deribit.com/api/v2/public/"
LIVE = "https://www.deribit.com/api/v2/public/"


def get(base, metodo, **params):
    url = base + metodo + "?" + urllib.parse.urlencode(params)
    for tent in range(6):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                js = json.loads(r.read().decode())
            if "result" in js:
                time.sleep(0.15); return js["result"]
            print("resposta sem result:", str(js)[:300], flush=True); time.sleep(3 + 3 * tent)
        except Exception as e:  # noqa: BLE001
            corpo = getattr(e, "read", lambda: b"")()
            print(f"erro ({tent}): {e} {corpo[:200]!r} — {url[:160]}", flush=True); time.sleep(3 + 3 * tent)
    sys.exit(f"Deribit: sem resposta em {metodo}")


def ms(s):
    return int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)


def baixar_dvol(t0, t1):
    linhas = []; t = t0
    while t < t1:
        r = get(LIVE, "get_volatility_index_data", currency="BTC", start_timestamp=t, end_timestamp=min(t + 1000 * 60000, t1), resolution=60)
        dados = r.get("data", [])
        if not dados:
            t += 1000 * 60000; continue
        linhas.extend(dados); t = dados[-1][0] + 60000
        if len(linhas) % 20000 < 1000: print(f"DVOL: {len(linhas)} pontos até {pd.Timestamp(t, unit='ms', tz='UTC')}", flush=True)
    df = pd.DataFrame(linhas, columns=["ts", "open", "high", "low", "close"]).drop_duplicates("ts").sort_values("ts")
    df.to_csv(ROOT / "vol_implicita" / "dados" / "dvol.csv", index=False); print(f"DVOL: {len(df)} minutos")


def baixar_opcoes(t0, t1):
    out = gzip.open(ROOT / "vol_implicita" / "dados" / "opcoes_trades.csv.gz", "wt")
    out.write("ts,instrument,price,iv,index_price,amount,direction\n")
    t = t0; n = 0; ultimo_id = None
    while t < t1:
        r = get(HIST, "get_last_trades_by_currency_and_time", currency="BTC", kind="option", start_timestamp=t, end_timestamp=t1, count=1000, sorting="asc")
        trades = r.get("trades", [])
        if not trades:
            break
        for tr in trades:
            if tr["trade_id"] == ultimo_id: continue
            out.write(f"{tr['timestamp']},{tr['instrument_name']},{tr['price']},{tr.get('iv', '')},{tr.get('index_price', '')},{tr['amount']},{tr['direction']}\n"); n += 1
        ultimo_id = trades[-1]["trade_id"]; t_novo = trades[-1]["timestamp"]
        t = t_novo if t_novo > t else t + 1
        if len(trades) < 1000 and r.get("has_more") is False:
            t = t_novo + 1
        if n % 100000 < 1000: print(f"opções: {n} negócios até {pd.Timestamp(t, unit='ms', tz='UTC')}", flush=True)
        time.sleep(0.05)
    out.close(); print(f"opções: {n} negócios")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--inicio", required=True); ap.add_argument("--fim", required=True); a = ap.parse_args()
    (ROOT / "vol_implicita" / "dados").mkdir(parents=True, exist_ok=True)
    baixar_dvol(ms(a.inicio), ms(a.fim)); baixar_opcoes(ms(a.inicio), ms(a.fim))
