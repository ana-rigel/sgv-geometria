# Execução da versão GitHub
```bash
git fetch origin
git switch research/m11i-integracao-instrumental
python -m pip install -r requirements_m11i.txt
python -m pytest -q tests/test_m11i_integrated.py
python -m sgv_m11i.integrated --synthetic --out reports/m11i/outputs
python -m sgv_m11i.integrated --csv seu_arquivo.csv --window 1500 --stride 1500 --out reports/m11i/meu_csv
```
CSV: timestamp ms, close, volume, taker_buy, barras fechadas.
A versão ZIP autocontida para Windows também está disponível
na conversa que entregou esta implementação, contendo
`sgv_m11i/instrument.py`; a versão Git usa diretamente
os módulos históricos do projeto para eliminar duplicações.
O GitHub Actions não baixa preços reais.
