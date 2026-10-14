"""Testes sem dados reais da integração científica M11-I ↔ U03 ↔ RTT ↔ M35.

Verificam que os objetos e estados de pesquisa foram documentados sem
modificar instrumentos já congelados. Não são testes de hipótese.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "reports" / "SGV_PROGRAMA_INTEGRADO_M11I_U03_M35_RTT_20261013.md"
M35_PLAN = ROOT / "reports" / "m35" / "PLANO_M35_PASSO1_20261013.md"
M35_MODEL = ROOT / "experiments" / "m35_instrumento.py"
M35_SCRIPT = ROOT / "scripts" / "m35_passo1.py"


def test_program_and_frozen_measurement_plan_exist():
    assert PROGRAM.is_file() and M35_PLAN.is_file()
    a, b = PROGRAM.read_text(encoding="utf-8"), M35_PLAN.read_text(encoding="utf-8")
    assert "confiabilidade" in a.lower() and ("≥ 0,6" in b or ">= 0,6" in b)
    assert "Spearman" in b and "0,7" in b
    assert "R²" in b and "0,5" in b


def test_instruments_are_not_replaced_by_unrelated_models():
    txt = PROGRAM.read_text(encoding="utf-8")
    for label in ("M11-I", "U03", "M35", "RTT", "H-GEO", "H-J"):
        assert label in txt
    assert "não" in txt.lower() and "holdout" in txt.lower()


def test_m35_frozen_variants_are_present_and_engineering_only():
    b = M35_PLAN.read_text(encoding="utf-8")
    mod = M35_MODEL.read_text(encoding="utf-8")
    runner = M35_SCRIPT.read_text(encoding="utf-8")
    for v in ("V0", "V1", "V2", "V3", "V4", "V4n"):
        assert re.search(r"\b" + v + r"\b", b), v
    for v in ("V0", "V1", "V2", "V3", "V4"):
        assert f"variant=='{v}'" in mod, v
    assert "m35_instrumento" in runner
    assert "rv_future_15" not in runner
    assert "qlike" not in runner.lower()


def test_ledger_preserves_confirmatory_data_status():
    a = PROGRAM.read_text(encoding="utf-8")
    for token in ("BTC 1m agosto–setembro/2026", "ETH 1m junho–setembro/2026",
                  "SOL 1m junho–setembro/2026", "BNB 1m junho–setembro/2026",
                  "BTC 1m outubro–dezembro/2026"):
        assert token in a
    assert "RESERVADO" in a
