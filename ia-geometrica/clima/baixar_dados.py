"""Baixa os dados de clima de Juara/MT para o teste 30 (seca silenciosa). Só baixa, confere e conta linhas: não olha valores.

Fontes:
  1. ERA5-Land (reanálise, Copernicus) via API de arquivo da Open-Meteo, horário, ponto em Juara (centro da cidade, aproximado,
     até a Ana dar as coordenadas do sítio): chuva, temperatura, umidade do ar, VPD, radiação, ET0 e as quatro camadas de umidade do solo.
  2. INMET, arquivos históricos anuais (todas as estações automáticas): extrai a(s) estação(ões) com JUARA no nome e lista as de MT.

Uso: python ia-geometrica/clima/baixar_dados.py   (roda no GitHub Actions; a rede do workspace não alcança estas fontes)
"""
import csv, gzip, hashlib, io, json, sys, time, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "dados"
LAT, LON = -11.255, -57.520          # Juara/MT, centro urbano aproximado
ANOS_ERA5 = range(2010, 2026)
ANOS_INMET = range(2008, 2026)
VARS = ["precipitation", "temperature_2m", "relative_humidity_2m", "vapour_pressure_deficit", "shortwave_radiation",
        "et0_fao_evapotranspiration", "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm"]
UA = {"User-Agent": "sgv-geometria/ia-geometrica (pesquisa; github.com/ana-rigel/sgv-geometria)"}


def get(url, tentativas=4, timeout=300):
    for k in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r: return r.read()
        except Exception as e:
            print(f"    tentativa {k+1} falhou: {e}", flush=True); time.sleep(10 * (k + 1))
    return None


def era5():
    """Na Open-Meteo, o modelo era5_land não traz chuva, radiação nem ET0 (vieram vazias na 1ª rodada, run 39360875918):
    essas três vêm do ERA5 (models=era5, mesma reanálise, grade de ≈ 25 km); o resto do ERA5-Land (≈ 9 km)."""
    DO_ERA5 = {"precipitation", "shortwave_radiation", "et0_fao_evapotranspiration"}
    grupos = {"era5_land": [v for v in VARS if v not in DO_ERA5], "era5": [v for v in VARS if v in DO_ERA5]}
    linhas = []; falhas = []
    for a in ANOS_ERA5:
        h = {}
        for modelo, vs in grupos.items():
            url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}&start_date={a}-01-01&end_date={a}-12-31"
                   f"&hourly={','.join(vs)}&models={modelo}&timezone=America%2FCuiaba")
            b = get(url)
            if b is None: falhas.append(f"{a}:{modelo}"); break
            hh = json.loads(b)["hourly"]
            if "time" in h and hh["time"] != h["time"]: falhas.append(f"{a}:tempo"); break
            h.update(hh); time.sleep(2)
        if any(str(a) in f for f in falhas): continue
        n = len(h["time"]); vazios = {v: sum(x is None for x in h[v]) for v in VARS}
        for i in range(n): linhas.append([h["time"][i]] + [h[v][i] for v in VARS])
        print(f"  {a}: {n} horas; campos vazios {sum(vazios.values())}", flush=True)
    out = ROOT / "era5land_juara_horario.csv.gz"
    with gzip.open(out, "wt", newline="") as f:
        w = csv.writer(f); w.writerow(["tempo_local"] + VARS); w.writerows(linhas)
    return {"arquivo": out.name, "linhas": len(linhas), "anos_falhos": falhas, "lat": LAT, "lon": LON, "modelo": "era5_land (solo, temperatura, umidade, VPD) + era5 (chuva, radiação, ET0), Open-Meteo archive API"}


def inmet():
    d = ROOT / "inmet"; d.mkdir(parents=True, exist_ok=True); achados = []; mt = set(); falhas = []
    for a in ANOS_INMET:
        b = get(f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{a}.zip", timeout=900)
        if b is None: falhas.append(a); continue
        z = zipfile.ZipFile(io.BytesIO(b))
        for nome in z.namelist():
            base = nome.split("/")[-1]
            if "_MT_" in base.upper(): mt.add("_".join(base.split("_")[3:5]))
            if "JUARA" in base.upper():
                (d / base).write_bytes(z.read(nome)); achados.append(base)
        print(f"  INMET {a}: {len(b)/1e6:.0f} MB; Juara: {[x for x in achados if str(a) in x]}", flush=True)
    (d / "estacoes_MT.txt").write_text("\n".join(sorted(mt)) + "\n")
    return {"arquivos_juara": achados, "anos_falhos": falhas, "estacoes_MT": len(mt)}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    man = {"baixado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "nota": "só download e contagem; nenhum valor foi lido"}
    print("ERA5-Land:", flush=True); man["era5"] = era5()
    print("INMET:", flush=True); man["inmet"] = inmet()
    man["sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name != "MANIFESTO.json"}
    (ROOT / "MANIFESTO.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in man.items() if k != "sha256"}, ensure_ascii=False, indent=1))
    if man["era5"]["linhas"] == 0: sys.exit("ERA5-Land não baixou nada")


if __name__ == "__main__":
    main()
