# Resultado H-CASCA-01 — NÃO CONFIRMADA (ligação positiva e significativa, abaixo do limiar de fidelidade)

Julgamento único, rodado pelo GitHub Actions (run 38671024284, commit 2b262ef), com o pré-registro (incluindo a emenda 1) e o código conferidos por hash (`referencia/HASHES_H-CASCA-01.txt`).

**Paridade (BTC jun–jul), refeita no runner:**
- desenho do relatório: 329 mapas, 291 pares, ρ = +0,638;
- pares disjuntos: 20 pares, ρ = +0,656.

## LTCUSDT, 01/06 a 01/10/2026

| | valor |
|---|---|
| janelas válidas | 89 de 104 (15 inválidas por cobertura da HDR50 < 0,95) |
| pares válidos | 41 de 52 (válido: ≥ 25) |
| **ρ (caudas, Δlog q99,9/mediana de \|r\|)** | **+0,348** |
| p (permutação, unilateral) | 0,013 |
| critério | p < 0,05 **e** ρ ≥ 0,40 |
| **veredito** | **NÃO CONFIRMADA** |

**Secundários (só leitura):**

| | LTC | BTC (exploração, pares disjuntos) |
|---|---|---|
| ρ contra Δlog curtose de E_norm | +0,53 | +0,73 |
| ρ contra Δlog q99/mediana | +0,18 | +0,81 |
| ρ contra Δlog máx \|r\| | +0,25 | +0,55 |
| só núcleo (log V50) | −0,12 | −0,55 |
| só envelope (log V95) | +0,11 | +0,21 |
| confiabilidade entre 5 sementes do GMM | 0,956 | 0,9997 |
| ρ por semente | 0,34 / 0,37 / 0,38 / 0,34 / 0,40 | 0,63–0,67 |
| nula de pipeline | **+0,33** (48 pares) | +0,08 (25 pares) |

## Leitura

1. **A ligação existe, mas é frouxa.** No LTC, quando a cauda dos retornos engorda, a feature de caudas tende a subir (p = 0,013). Mas ρ = 0,35 é metade do BTC e fica abaixo do limiar de 0,40, que foi registrado justamente porque a pergunta era de fidelidade. Pela regra, não está confirmada. A casca não serve como medidor de cauda confiável fora do BTC.
2. **O veredito está na beira do limiar.** Nas cinco sementes do GMM, ρ vai de 0,34 a 0,40. A semente registrada (20261009) dá 0,35, e só uma das outras quatro tocaria 0,40. A semente foi fixada antes, e o resultado vale como saiu. Com 41 pares, o erro-padrão de ρ é ~0,14: o efeito verdadeiro no LTC é compatível com qualquer valor entre ~0,1 e ~0,6.
3. **A emenda 1 não se sustentou.** No BTC, a nula de pipeline derrubava o ρ (+0,08), o que sugeria que a casca lia caudas produzidas por episódios agrupados no tempo. No LTC, a nula dá +0,33, praticamente igual ao real. A ligação que sobra no LTC vem do conjunto de retornos de cada dia, não da ordem deles. Com 20–48 pares, as duas nulas são imprecisas, e nenhuma das duas leituras fica estabelecida.
4. **A referência interna segura melhor que as externas.** Contra a curtose de E_norm, ρ = +0,53. Contra as medidas de preço: +0,35 (q99,9), +0,25 (máximo) e +0,18 (q99). A casca acompanha a cauda da própria coordenada melhor que a cauda do preço. A tradução de "cauda de E_norm" para "cauda de retorno" é onde a fidelidade se perde fora do BTC.
5. **O LTC também cobre pior a grade.** 15 % das janelas falharam por cobertura da HDR50 (grade ±3,5 do M11-I), contra 10 % no BTC. Com caudas mais pesadas, menos janelas cabem no instrumento.

A aposta registrada era de ~75 % de confirmação. Pela regra, não há segunda tentativa com outro ativo, semente, janela, nível de casca ou período.
