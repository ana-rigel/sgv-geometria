"""Serviço de coordenadas ao vivo do painel 4D. DESLIGADO por padrão: obedece painel/LIBERACAO.json.

    python painel/vivo.py --porta 8766                       # recusa partir se LIBERACAO.ligado for false
    python painel/vivo.py --porta 8766 --simular painel/dados/replay_2026-05_2026-07.npz   # ensaio: alimenta minuto a minuto dos dados abertos

O que faz, quando liberado:
  1. carrega a âncora de maio (régua, quantis) do .json do replay; nunca recalcula a âncora;
  2. busca klines 1 min da Binance por REST (api.binance.com/api/v3/klines) SÓ dentro de janelas_liberadas, e o fluxo corrente SÓ se
     ao_vivo_desde <= agora; qualquer candle fora disso é descartado antes de entrar no buffer;
  3. mantém um buffer rolante de 2 semanas + 1 dia (aquecimento do instrumento = 1.441 barras) e recalcula as coordenadas com o
     pipeline do repositório a cada candle fechado;
  4. serve as mesmas rotas do replay (/meta, /janela) mais /vivo com o estado da liberação.
O caminho de rede não foi testado nesta sessão (o ambiente não alcança a Binance); o caminho de cálculo foi, via --simular.
"""
import argparse
import json
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline")); sys.path.insert(0, str(ROOT / "painel"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_escondida as V  # noqa: E402
import servidor as S  # noqa: E402

E = GR.E
AQUECIMENTO, JANELA = 1441, 20160
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "qav", "n", "taker_buy", "tbq", "ign"]


def liberacao():
    L = json.loads((ROOT / "painel" / "LIBERACAO.json").read_text())
    jan = [(pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")) for a, b in L.get("janelas_liberadas", [])]
    vivo = pd.Timestamp(L["ao_vivo_desde"], tz="UTC") if L.get("ao_vivo_desde") else None
    return bool(L.get("ligado")), jan, vivo


def permitido(ts, jan, vivo):
    """Candle com open_time ts pode entrar? Só se estiver numa janela liberada ou depois de ao_vivo_desde."""
    if any(a <= ts < b for a, b in jan): return True
    return vivo is not None and ts >= vivo


def buscar_binance(inicio_ms, limite=1000):
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={int(inicio_ms)}&limit={limite}"
    with urlopen(url, timeout=20) as r: rows = json.load(r)
    df = pd.DataFrame(rows, columns=COLS)
    for c in ("open", "high", "low", "close", "volume", "taker_buy"): df[c] = df[c].astype(float)
    df["timestamp"] = df.open_time.astype("int64"); return df[["timestamp", "open", "high", "low", "close", "volume", "taker_buy"]]


class Vivo:
    def __init__(self, meta):
        self.meta = meta; self.reg = meta["regua"]; self.lock = threading.Lock(); self.kl = pd.DataFrame(); self.est = None
        self.ligado, self.jan, self.vivo_desde = liberacao()

    def ingerir(self, df):
        ts = pd.to_datetime(df.timestamp, unit="ms", utc=True); ok = np.array([permitido(t, self.jan, self.vivo_desde) for t in ts])
        df = df[ok]
        if not len(df): return 0
        with self.lock:
            self.kl = pd.concat([self.kl, df]).drop_duplicates("timestamp").sort_values("timestamp").tail(JANELA + AQUECIMENTO).reset_index(drop=True)
            self.recalcular()
        return int(len(df))

    def recalcular(self):
        kl = self.kl
        if len(kl) < AQUECIMENTO + 10: self.est = None; return
        raw = E.coords_orig(kl); med = np.array(self.reg["mediana"]); esc = np.array(self.reg["escala"])
        G = (raw - med) / esc
        lw = np.log(V.estimativas(kl)["har"]); w = (lw - self.reg["w_mediana"]) / self.reg["w_escala"]
        q1, q2 = self.meta["tercis_limites"]; fat = np.full(len(w), -1, np.int8); fin = np.isfinite(w); fat[fin] = np.digitize(w[fin], [q1, q2])
        self.est = {"timestamp": kl.timestamp.values.astype(np.int64), "close": kl.close.values.astype(np.float32), "x": G.astype(np.float32),
                    "w": w.astype(np.float32), "fatia": fat, "ext": np.nanmax(np.abs(G), axis=1).astype(np.float32)}
        S.D = self.est

    def laco_binance(self):
        inicio = max([a for a, _ in self.jan] + ([self.vivo_desde] if self.vivo_desde else []))
        cursor = int(inicio.timestamp() * 1000)
        while True:
            try:
                df = buscar_binance(cursor)
                if len(df): n = self.ingerir(df); cursor = int(df.timestamp.iloc[-1]) + 60000; print(f"{datetime.now(timezone.utc):%H:%M} +{n} candles, buffer {len(self.kl)}", flush=True)
                time.sleep(5 if len(df) >= 1000 else 60)
            except Exception as ex:
                print("erro de rede:", ex, flush=True); time.sleep(60)

    def laco_simulado(self, npz):
        z = np.load(npz); ts = z["timestamp"]; close = z["close"]
        # o ensaio precisa de OHLCV: reconstrói candles planos a partir do fechamento (só para exercitar o laço, não para medir)
        for i in range(0, len(ts), 60):
            j = min(i + 60, len(ts)); c = close[i:j].astype(float)
            df = pd.DataFrame({"timestamp": ts[i:j], "open": np.r_[c[0], c[:-1]], "high": c, "low": c, "close": c, "volume": 1.0, "taker_buy": 0.5})
            n = self.ingerir(df)
            if (i // 60) % 240 == 0: print(f"simulado: +{n}, buffer {len(self.kl)}, estado {'ok' if self.est is not None else 'aquecendo'}", flush=True)
            time.sleep(0.01)
            if i > 60 * 24 * 20: break   # 20 dias bastam para o ensaio


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--porta", type=int, default=8766); ap.add_argument("--meta", default=str(ROOT / "painel/dados/replay_2026-05_2026-09.json"))
    ap.add_argument("--simular", help="npz dos meses abertos; ignora LIBERACAO e a rede (ensaio local)"); a = ap.parse_args()
    meta = json.loads(Path(a.meta).read_text()); v = Vivo(meta)
    if a.simular:
        v.jan = [(pd.Timestamp("2026-05-01", tz="UTC"), pd.Timestamp("2026-10-01", tz="UTC"))]; v.vivo_desde = None
        threading.Thread(target=v.laco_simulado, args=(a.simular,), daemon=True).start()
    else:
        if not v.ligado:
            sys.exit("ao vivo DESLIGADO em painel/LIBERACAO.json (outubro reservado até 3/11, novembro até 1/12). Nada foi buscado.")
        threading.Thread(target=v.laco_binance, daemon=True).start()
    S.META = {**meta, "ao_vivo": {"ligado": bool(a.simular) or v.ligado, "janelas": [[str(x.date()), str(y.date())] for x, y in v.jan], "desde": str(v.vivo_desde) if v.vivo_desde else None,
                                  "modo": "simulado" if a.simular else "binance"}}
    S.D = {"timestamp": np.array([], np.int64), "close": np.array([], np.float32), "x": np.zeros((0, 3), np.float32), "w": np.array([], np.float32), "fatia": np.array([], np.int8), "ext": np.array([], np.float32)}
    print(f"vivo em http://localhost:{a.porta}/ · modo {'simulado' if a.simular else 'binance'}", flush=True)
    HTTPServer(("0.0.0.0", a.porta), S.H).serve_forever()


if __name__ == "__main__":
    main()
