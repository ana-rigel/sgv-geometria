# Auditoria do M11-I (pacote ZIP / ramo research/m11i-integracao-instrumental)

BTC 1m mai–jul/2026 (já gasto); nenhum alvo de mercado. Script: `scripts/m35_auditoria_m11i.py`
(executado com o diretório do ZIP como 1º argumento). Resultados: `audit_m11i.json`, `audit_rows.csv`.

- Fidelidade: gaussianização/split e coordenadas (z, ι, ν) idênticas ao original (diferença 0); D idêntico ao M2 (4e-16).
- R_M11 vs M11 original (60 origens): Spearman 0,993; auditoria de registro escolheu eixos em 18/59; R_M11 ≤ M11 em 88% (viés leve para baixo — não misturar valores).
- Ruído (20 origens × 4 sementes / 4 reamostras): confiabilidade R_M11 0,33 (M11 0,37); ~37% do ruído é semente, ~63% amostragem.
  Teto aproximado sem ruído de semente ≈ 0,44 → o M11 com ~525 pontos por metade não chega a 0,6 só com engenharia do algoritmo.
- Pendências do M11-I: controles sintéticos não testam a estimação de densidade nem D em casca não convexa (D=0 em toda a demo);
  semente do modo CSV depende da ordem das linhas; ZIP rejeita arquivo com lacunas (original segmenta); workflow do ZIP aponta para requirements_m11i.txt.
