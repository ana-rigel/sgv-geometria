# Emenda / v2 do MSM: correção da escala da Student-t (registrada antes de rodar a v2)

**Registrada em:** 16/10/2026, depois de a validação da v1 reprovar em jun–jul (sintético k = 2 → k* = 4; log em resultados/msm_v1_junjul_INCONCLUSIVO.log) e antes de rodar a v2. A v1 fica **INCONCLUSIVA** pelo critério registrado; o real não foi lido (a rodada foi interrompida na validação).

**Defeito encontrado:** o gerador dos sintéticos usa Student-t padronizada (variância 1); a verossimilhança usava a t crua, de variância ν/(ν−2). Com σ̄ fixo no desvio-padrão amostral, o modelo ajustado tinha variância implícita errada por um fator ν/(ν−2) (= 2 para ν = 4) e compensava com m₀ e componentes extras. Defeito de instrumento, não de hipótese.

**Correção (única mudança):** na verossimilhança, a escala da inovação passa a ser vol·√((ν−2)/ν), de modo que E[r²] = σ̄² exatamente como no gerador e no dado. Tudo o mais (modelo, grade k = 1…4, BIC, validação com k = 2 e 3, sementes 8026/8027, parâmetros m₀ = 1,4, b = 3, γ_k = 0,5, ν = 4, classes, apostas) fica como em PREDICAO_msm.md. As apostas da v1 valem para a v2 sem alteração.

## Emenda 2 (registrada antes de rodar jun–jul e ago–set com a v2)

A fumaça da v2 mostrou que os parâmetros de validação de PREDICAO_msm.md (b = 3, γ_k = 0,5) geram componentes em ~2 e ~5 min (k = 2) e ~2, ~5, ~13 min (k = 3): escalas quase indistinguíveis, que um k menor com escala intermediária ajusta igual (verificado: nll k1 −112261,0 vs k2 −112260,5 num sintético de 20 mil pontos). Não é defeito da verossimilhança (nos parâmetros verdadeiros ela vence os degenerados); é teste de validação mal posto.

**Mudança (única):** parâmetros do sintético de validação passam a **b = 25, γ_k = 0,5** (m₀ = 1,4 e ν = 4 mantidos), o que dá escalas de ~2 min e ~50 min (k = 2) e ~2 min, ~50 min e ~21 h (k = 3), separadas por uma ordem de grandeza como as do v3. Sementes, grade, BIC, classes e apostas inalterados. Esta é a última emenda: se a validação reprovar com escalas separadas, o instrumento é declarado incapaz e a exploração encerra INCONCLUSIVA.
