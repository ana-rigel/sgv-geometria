# SGV-M27 — Leitura: o funcionamento muda ao longo do dia

**Execução:** GitHub Actions run 38178976608 (44 jobs, todos com sucesso). **84/84 origens válidas.** Só dados exploratórios. Recontagem independente a partir dos shards confere (primário A: vol_5 10×0, vol_30 12×0; primário B: vol_5 9×1, vol_30 16×0, hsic_5 10×1, hsic_30 22×1).
Engenharia pós-protocolo registrada em `reports/m27/ENGENHARIA.md` (diagnóstico descritivo `ar1_nu` acrescentado; nenhum critério mudou).

## 1. Resultado

| | HARLMFX (global, M26) | HXNOISE (local, ruído) | **HXLOC (local, real)** | BL |
|---|---|---|---|---|
| M11 / Fisher–Rao / energy | 18 / 14 / 18% | 15 / 8 / 20% | **11 / 8 / 8%** | 7 / 10 / 11% |
| lin 1/5/30 | 12 / 20 / 26% | 12 / 25 / 39% | **7 / 18 / 21%** | 10 / 11 / 15% |
| **vol 1/5/30** | 18 / 21 / 21% | 12 / 19 / 26% | **8 / 10 / 7%** | 10 / 8 / 11% |
| HSIC 1/5/30 | 19 / 30 / 31% | 19 / 38 / 52% | **17 / 27 / 27%** | 11 / 12 / 14% |

- **Leitura pré-registrada: não estacionariedade apoiada em `vol_5` e `vol_30`.** Os parâmetros locais derrubam os alarmes de volatilidade (21→10% e 21→7%; 10×0 e 12×0 discordantes) e vencem o controle de ruído nas mesmas estatísticas.
- **O ganho não vem de referências mais largas.** O controle de ruído (mesmo pipeline sobre um prefixo sintético estacionário) **não** reduz alarmes em relação ao modelo global — em geral aumenta. Ressalva: isso torna o primário B mais fácil de vencer; a evidência principal é o primário A combinado com o fato de o ruído sozinho não ajudar.
- **Veredito pré-registrado: "não fecha a lacuna"** — mas por pouco: o HXLOC é estatisticamente indistinguível do BL em **10 das 12** estatísticas (inclusive M11, acoplamento, massa e volatilidade em todas as defasagens). Só fica pior em **HSIC_5 e HSIC_30** (27% contra 12–14%). `lin_5` está no limite (6×0, p = 0,016, acima de 0,0042).

## 2. O que isso diz sobre o BTC
A "memória de volatilidade em 5–30 min" que resistiu de M23 a M26 **não era um mecanismo faltando: era o funcionamento mudando ao longo do dia.** Um modelo com as mesmas peças do M26, mas com parâmetros de ~13 h em vez de ~3,5 dias, reproduz a volatilidade tão bem quanto os blocos reais.
Os parâmetros que mais mudam de verdade entre trechos (dispersão real maior que a do ruído) são a **persistência de 1 min do volume** (73% das origens, p = 2·10⁻⁵), o **termo de resiliência agressão←retorno** (65%, p = 0,003) e a **persistência da variância do volume** (64%, p = 0,006). A persistência da variância do retorno **não** muda além do ruído (50%).
A resiliência da liquidez é robusta a isso: o termo agressão←retorno sai negativo em **97% dos 504 trechos locais** (84 origens × 6). O que muda é a **intensidade**, não o sinal.

## 3. O que sobra
Uma única coisa: **dependência não linear nas defasagens de 5 e 30 min que não é volatilidade** (HSIC alto com `vol` já adequado). Candidatos, todos ainda hipóteses: assimetria de sinal (queda e alta afetando o futuro de forma diferente), dependência via forma condicional, ou dependência em alguma combinação das coordenadas que |x| não capta. Isso é uma pergunta nova, não testada aqui.

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| Primário A em ≥ 1 (55%) | sim (vol_5, vol_30) | ✅ |
| Primário B em ≥ 1 (30%) | sim (as quatro) | ✅ (contra a aposta) |
| Não estacionariedade apoiada (25%) | sim | ✅ (contra a aposta) |
| Ruído sozinho ajuda (45%) | não | ✅ |
| "Equivalente ao BL" (20%) | não (por 2 estatísticas) | ✅ |
| "Adequação plena" (5%) | não | ✅ |
| Dispersão real > sintética na persistência da variância (65%) | volume sim, retorno não | ½ |

Subestimei a não estacionariedade: dei 25% e ela apareceu com força.
