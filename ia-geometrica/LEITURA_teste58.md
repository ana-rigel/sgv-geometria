# Leitura do teste 58 (calibração da lente, etapa 2): T4 PASSOU; T1, T2, T3 REPROVADOS. A lente vê sincronização parcial onde só há memória de fase sem acoplamento. Linha "um padrão para todos os sistemas" FECHADA pelo critério de morte

**Predição:** PREDICAO_teste58_calibracao_lente.md (7418bdc), antes do instrumento. **Instrumento:** teste58.py. **Resultado:** resultados_teste58.json e .log (rodada única no GitHub Actions, run 40023801616, 85 s). 30 sementes, N = 100, T = 10 000. Sem emenda depois de rodar.

| | resultado | critério | |
|---|---|---|---|
| **T1** localiza a transição | κ cruza 0,5 em K = 0,27 K_c; IC95 [0,02; 0,34] K_c, não contém K_c | ±20 % de K_c | **reprovado** |
| **T2** ordena os regimes | 0 de 30 sementes na ordem; κ(M1, K=0) = 0,486 e κ(M3) = 0,514 ficam longe de κ(M2) = 0,178 | ≥ 27 de 30 | **reprovado** |
| **T3** muda no ruído | κ(M2) = 0,178 ≤ piso 0,194 (passa); κ(M3) = 0,514 ≫ piso; M2 vs M3 p = 3×10⁻¹¹ | ambos no piso, p > 0,05 | **reprovado** |
| **T4** nula de pipeline | κ(M5) = 0,181 ≤ piso; M5 vs M2 p = 0,80 | no piso, p > 0,05 | **passou** |
| referência clássica | Spearman(κ, R_K) na varredura = 0,994 | > 0,95 → lente só lê R_K | **lente só lê R_K** (deslocado) |

Apostas: Ana 50 % de aprovação, T3 o mais provável de falhar — certa no T3. Claude 35 %, T3 — certa no T3; errou T1 (70 %) e T2 (80 %), ambos reprovados.

## O que o resultado diz

**1. κ mede persistência de fase, não acoplamento.** No passeio aleatório (M3), as fases dos 100 osciladores se perdem umas das outras (R_K = 0,089, quase zero), mas a fase do sinal Z(t) anda devagar. Os três andares da cascata, que são filtros passa-baixa, seguem essa fase devagar juntos, e saem coerentes entre si: κ = 0,51. É exatamente a confusão que a predição temia: "a lente lê persistência como acoplamento". O mesmo ocorre no Kuramoto sem acoplamento (K = 0, κ = 0,49): nada se acopla, e a lente vê metade da escala.

**2. A transição que a lente vê não é a de Kuramoto.** κ cruza 0,5 em 0,27 K_c, bem antes da transição real (1,0 K_c). A curva de κ é monotônica em R_K (Spearman 0,994), então a lente ordena os regimes como R_K ordena, mas com um deslocamento de ~0,5 vindo da persistência. O salto real aparece: entre 0,95 e 1,05 K_c, κ pula de 0,73 para 0,95, no lugar certo. Mas o critério não pode pescar isso depois de ver os dados.

**3. O que passou vale.** No ruído branco a lente fica muda (0,178 ≤ 0,194) e a nula de pipeline funciona (embaralhar o Kuramoto a derruba ao chão). A lente não inventa padrão em ruído sem memória. Ela inventa em ruído com memória.

**4. Para o paralelo galáxia–mercado–IA.** O padrão que a lente da v0 vê nos quatro sistemas é, em boa parte, "este sinal tem fase persistente". Galáxia, mercado e redes neurais têm memória de fase; a lente veria sincronização parcial em todos mesmo que não houvesse acoplamento algum. Pela regra de morte pré-registrada, a linha "um padrão para todos os sistemas" fecha nesta forma. Não fecha a pergunta sobre o universo; fecha o uso desta lente como instrumento dela.

**5. O que sobra.** T4 mostra que o pipeline de nula é bom. Uma lente que separe acoplamento de persistência precisaria comparar a coerência entre andares com a coerência esperada de um sinal com a MESMA memória de fase e nenhum acoplamento — o próprio M3 como nula pareada por autocorrelação, a mesma lição da H-AMP-01 do SGV (controle pareado por pré-vol eliminou o excesso). Isso seria outro teste, com outra predição, não uma repetição deste.

## Para a lista de defeitos de desenho

84. A rotação média comum Ω₀ = 1 (emenda antes de rodar) dá a M1 (K = 0), M3 e M4 uma fase que anda junto por construção; parte do κ = 0,49 em K = 0 pode vir dela. Não muda o veredito (M3 sem Ω₀ ainda tem fase lenta), mas o M1 em K = 0 e o M3 não separam "persistência do mundo" de "rotação comum". O desenho certo teria um M3 sem rotação como célula adicional.
85. O T1 fixou o cruzamento em κ = 0,5 supondo piso ≈ 0. Com o piso da persistência em ≈ 0,5, o critério estava condenado antes de rodar; o cruzamento deveria ser relativo ao piso medido em K = 0.

Placar: 58 testes numerados (o 25 sem resultado), mais o teste do ato A; 58: T4 passou, T1–T3 reprovaram; 85 defeitos nesta numeração, 1 emenda.
