# M27 — Registro de engenharia (depois do protocolo, antes de qualquer posto)

- **Diagnóstico descritivo `ar1_nu` acrescentado.** O teste unitário com troca plantada de persistência mostrou que a soma dos coeficientes HAR do volume (`harpers_nu`, citada no protocolo) é dominada por ruído de colinearidade entre os termos de 1/15/60 min (dispersão maior na série estacionária do que na série com troca). Mantive `harpers_nu` como pré-registrado e acrescentei `ar1_nu` (coeficiente de 1 min), que recupera a troca plantada. Os dois são só descritivos; nenhum critério muda.
- Piloto local (origem 0, 2 referências): sem problemas, 31 s. Nenhum posto ou diagnóstico de dado real foi inspecionado.
- Workflow: mesmo esquema do M26 (42 shards de 2 origens), tempo limite 120 min por shard.
