"""Baixa, para os lugares do teste 31, a série horária 2010–2025 das três grandezas da página Cérebro de Juara:
umidade do solo 28–100 cm e VPD (ERA5-Land), chuva e ET0 (ERA5), via API de arquivo da Open-Meteo. Agrega por dia e grava um CSV por lugar.
Só baixa, confere e conta: não olha valores. Roda no GitHub Actions."""
import csv, hashlib, json, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "dados" / "lugares"
LUGARES = {   # fixados na predição do teste 31, antes de qualquer download
    "sinop": (-11.86, -55.50), "cuiaba": (-15.60, -56.10), "barra_do_garcas": (-15.89, -52.26),
    "alta_floresta": (-9.88, -56.09), "rondonopolis": (-16.47, -54.64),
    "porto_alegre": (-30.03, -51.23), "curitiba": (-25.43, -49.27), "petrolina": (-9.39, -40.50),
    "manaus": (-3.12, -60.02), "belem": (-1.46, -48.49)}
GRUPOS = {"era5_land": ["soil_moisture_28_to_100cm", "vapour_pressure_deficit"], "era5": ["precipitation", "et0_fao_evapotranspiration"]}
UA = {"User-Agent": "sgv-geometria/ia-geometrica (pesquisa; github.com/ana-rigel/sgv-geometria)"}


def get(url, tentativas=5, timeout=600):
    for k in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r: return r.read()
        except Exception as e:
            print(f"    tentativa {k+1} falhou: {e}", flush=True); time.sleep(15 * (k + 1))
    return None


def lugar(nome, lat, lon):
    h = {}
    for modelo, vs in GRUPOS.items():
        for a0, a1 in ((2010, 2017), (2018, 2025)):
            url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={a0}-01-01&end_date={a1}-12-31"
                   f"&hourly={','.join(vs)}&models={modelo}&timezone=auto")
            b = get(url)
            if b is None: return {"erro": f"{modelo} {a0}-{a1}"}
            hh = json.loads(b)["hourly"]
            for k, v in hh.items(): h.setdefault(f"{modelo}:{k}", []).extend(v)
            time.sleep(3)
    t = h["era5_land:time"]
    if t != h["era5:time"]: return {"erro": "tempos diferentes entre modelos"}
    dias = {}
    for i, s in enumerate(t):
        d = dias.setdefault(s[:10], {"n": 0, "P": 0.0, "E": 0.0, "S": 0.0, "V": 0.0, "vazio": 0})
        vals = [h["era5:precipitation"][i], h["era5:et0_fao_evapotranspiration"][i], h["era5_land:soil_moisture_28_to_100cm"][i], h["era5_land:vapour_pressure_deficit"][i]]
        if any(v is None for v in vals): d["vazio"] += 1; continue
        d["n"] += 1; d["P"] += vals[0]; d["E"] += vals[1]; d["S"] += vals[2]; d["V"] += vals[3]
    out = ROOT / f"{nome}.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["dia", "chuva_mm", "et0_mm", "solo_28_100", "vpd_kpa", "horas"])
        for s in sorted(dias):
            d = dias[s]; n = max(d["n"], 1); w.writerow([s, round(d["P"], 3), round(d["E"], 3), round(d["S"] / n, 4), round(d["V"] / n, 4), d["n"]])
    return {"dias": len(dias), "dias_incompletos": sum(1 for d in dias.values() if d["n"] < 24), "lat": lat, "lon": lon}


def main():
    ROOT.mkdir(parents=True, exist_ok=True); man = {"baixado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "nota": "só download e contagem; nenhum valor foi lido"}
    for nome, (lat, lon) in LUGARES.items():
        print(nome, flush=True); man[nome] = lugar(nome, lat, lon); print("  ", man[nome], flush=True)
    man["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob("*.csv"))}
    (ROOT / "MANIFESTO.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
