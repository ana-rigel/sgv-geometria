"""Servidor mínimo do painel de replay (sem dependências além da biblioteca padrão + numpy).

    python painel/servidor.py --arquivo painel/dados/replay_2026-05_2026-07.npz --porta 8765

Rotas (JSON):
  /meta                         metadados da âncora e do instrumento
  /estado?i=<inicio>&n=<qtd>    minutos [i, i+n): timestamp, close, x, w, fatia, ext   (n ≤ 20160 = 2 semanas)
  /janela?fim=<i>&n=<qtd>       os n minutos que terminam em i (o que o painel mostra "agora")
  /                             a página de replay (painel/replay.html)
O modo ao vivo não existe: a rota /vivo responde 403 com a data em que será ligada.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = {}; META = {}; MAXN = 20160


def fatiar(i, n):
    i = max(0, min(int(i), len(D["timestamp"]) - 1)); n = max(1, min(int(n), MAXN)); j = min(i + n, len(D["timestamp"]))
    sel = slice(i, j); x = D["x"][sel]
    return {"i": i, "n": j - i, "timestamp": D["timestamp"][sel].tolist(), "close": D["close"][sel].round(2).tolist(),
            "x": np.where(np.isfinite(x), x, None).tolist(), "w": np.where(np.isfinite(D["w"][sel]), D["w"][sel], None).tolist(),
            "fatia": D["fatia"][sel].tolist(), "ext": np.where(np.isfinite(D["ext"][sel]), D["ext"][sel], None).tolist()}


class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode(); self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/meta": return self._json({**META, "n": int(len(D["timestamp"]))})
        if u.path == "/estado": return self._json(fatiar(q.get("i", 0), q.get("n", 1440)))
        if u.path == "/janela":
            n = int(q.get("n", 1440)); fim = int(q.get("fim", len(D["timestamp"]))); return self._json(fatiar(fim - n, n))
        if u.path == "/vivo": return self._json({"ligado": False, **META.get("ao_vivo", {})}, 403)
        if u.path in ("/", "/replay.html"):
            b = (ROOT / "painel" / "replay.html").read_bytes(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); return self.wfile.write(b)
        self._json({"erro": "rota desconhecida"}, 404)

    def log_message(self, *a): pass


def main():
    global D, META
    ap = argparse.ArgumentParser(); ap.add_argument("--arquivo", required=True); ap.add_argument("--porta", type=int, default=8765); a = ap.parse_args()
    z = np.load(a.arquivo); D = {k: z[k] for k in z.files}; META = json.loads(Path(a.arquivo.replace(".npz", ".json")).read_text())
    print(f"replay: {len(D['timestamp'])} minutos de {META['primeiro']} a {META['ultimo']} em http://localhost:{a.porta}/  (ao vivo: desligado)")
    HTTPServer(("0.0.0.0", a.porta), H).serve_forever()


if __name__ == "__main__":
    main()
