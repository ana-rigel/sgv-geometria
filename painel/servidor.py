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


def serie(res):
    """Vetores da resolução res (1, 5, 15); arquivos antigos sem prefixo valem como 1 min."""
    p = f"r{res}_"
    if p + "timestamp" in D: return {k[len(p):]: v for k, v in D.items() if k.startswith(p)}
    return D if res == 1 else None


def fatiar(i, n, res=1):
    S_ = serie(res)
    if S_ is None: return {"erro": f"resolução {res} não exportada"}
    N = len(S_["timestamp"]); i = max(0, min(int(i), N - 1)); n = max(1, min(int(n), MAXN)); j = min(i + n, N)
    sel = slice(i, j); x = S_["x"][sel]; nn = lambda v: np.where(np.isfinite(v), v, None).tolist()  # noqa: E731
    return {"i": i, "n": j - i, "res": res, "N": N, "timestamp": S_["timestamp"][sel].tolist(), "close": S_["close"][sel].round(2).tolist(),
            "x": np.where(np.isfinite(x), x, None).tolist(), "w": nn(S_["w"][sel]), "fatia": S_["fatia"][sel].tolist(), "ext": nn(S_["ext"][sel]),
            "D": nn(S_["D"][sel]) if "D" in S_ else None}


class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode(); self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/meta": return self._json({**META, "n": int(len(serie(1)["timestamp"]))})
        res = int(q.get("res", 1))
        if u.path == "/estado": return self._json(fatiar(q.get("i", 0), q.get("n", 1440), res))
        if u.path == "/janela":
            S_ = serie(res); N = len(S_["timestamp"]) if S_ else 0
            n = int(q.get("n", 1440)); fim = int(q.get("fim", N)); return self._json(fatiar(fim - n, n, res))
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
    print(f"replay: {len(serie(1)['timestamp'])} minutos de {META['primeiro']} a {META['ultimo']} em http://localhost:{a.porta}/  (ao vivo: desligado)")
    HTTPServer(("0.0.0.0", a.porta), H).serve_forever()


if __name__ == "__main__":
    main()
