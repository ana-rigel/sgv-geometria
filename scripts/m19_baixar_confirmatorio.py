#!/usr/bin/env python3
"""Única porta de entrada para os meses RESERVADOS do M19 (BTCUSDT 1m 2026-08 e 2026-09).

Recusa-se a baixar qualquer coisa se o protocolo do M19 não estiver congelado
("STATUS: CONGELADO") ou se o SHA-256 informado não bater com o arquivo.
Uso:  python scripts/m19_baixar_confirmatorio.py --protocol-sha <sha256>
"""
from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from experiments.m19_rupturas import protocol_gate,CONFIRMATORY_MONTHS
import baixar_klines as bk


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--protocol-sha',required=True)
    a=ap.parse_args()
    sha=protocol_gate(a.protocol_sha)
    print(f'Protocolo congelado conferido: {sha}')
    bk.DEST.mkdir(exist_ok=True);ok=True
    for m in CONFIRMATORY_MONTHS:
        msg=bk.download_month('1m',m);print(msg)
        ok&=msg.startswith(('ok','já estava ok'))
    return 0 if ok else 1


if __name__=='__main__':sys.exit(main())
