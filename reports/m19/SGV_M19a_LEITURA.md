# SGV-M19a — Os alarmes do nulo de blocos longos são choques de volatilidade? (exploratório)

**Dados:** só os resultados já commitados do M18 (nulo BL, 84 origens 1m exploratórias, mai–jul/2026) e os klines exploratórios. Nenhum mês reservado foi tocado. Script: `experiments/m19a_alarmes_vs_volatilidade.py`; tabela por origem: `reports/m19/SGV_M19a_alarmes_BL_vs_volatilidade.csv`. **Análise descritiva, feita antes de qualquer pré-registro confirmatório, para orientar o desenho do M19.**

## Taxas de base (BL, 1m)
- alarme em ≥1 régua: **20,2%** das janelas;
- alarme em ≥2 réguas: **6,0%**;
- nas 3 réguas: 0%.

## Relação com características da janela (Spearman contra o nº de réguas em alarme)
| Característica | ρ | p |
|---|---|---|
| razão de volatilidade (janela / prefixo) | −0,07 | 0,55 |
| maior retorno horário absoluto (em desvios do prefixo) | +0,04 | 0,75 |
| volume médio (log, janela / prefixo) | −0,01 | 0,93 |
| deslocamento líquido do preço na janela | −0,22 | 0,04 (sem correção para 4 testes) |

Por terço de razão de volatilidade, alarmes em ≥2 réguas: 7% (vol. baixa), 7% (média), 4% (alta).

## Leitura
**Os alarmes do nulo de blocos longos não acompanham volatilidade, movimentos extremos nem volume.** O que eles medem é outra coisa: uma configuração das três coordenadas que o repertório recente não contém.
**Consequência para o desenho do M19:** definir "evento" de forma mecânica por movimento grande de preço **não** testaria a hipótese das rupturas; seria esperar correlação onde já vemos que não há. Os eventos precisam ser **estruturais e externos** (notícias, decisões, colapsos), fixados antes de abrir os dados — e o teste deve controlar a volatilidade de qualquer forma.
