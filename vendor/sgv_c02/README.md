# SGV C02 — Gerador sintético e testes matemáticos iniciais

Protocolo científico pré-registrado em `research/c02-crossfamily-nonlinear-20261014`.

Esta pasta contém **somente instrumentação inicial**: gerador de cinco famílias, sete transformações e sete testes de sanidade. Não há modelos treinados, dados financeiros, abertura de OOD ou resultado confirmatório.

Comandos locais:

```bash
python -m pip install numpy pytest
PYTHONPATH=. python -m pytest -q tests/test_c02_generators.py
```

A geração `split='ood_test'` é bloqueada. Famílias OOD apenas podem ser inspecionadas por amostras sintéticas de calibração, não usadas em treinamento/validação.

O C01 encerrado não é retreinado nem reaberto.
