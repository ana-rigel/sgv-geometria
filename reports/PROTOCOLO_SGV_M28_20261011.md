# SGV-M28 — A atividade governa a escala (pré-registro)

**Data:** 11/10/2026. **Ramo:** `research/m28-dependencia-nao-linear` (a partir de `research/m27-nao-estacionariedade`). **`main` intocada. Só dados exploratórios** (1m mai–jul/2026).
**Nota de ritmo:** 8º experimento do dia, a pedido da Ana ("Continue, vamos conseguir"), contra a regra de 1–2 por dia (registrado).

## De onde vem a hipótese
Depois do M27, o modelo local (HXLOC) empata com os blocos reais em 10 de 12 estatísticas; só a dependência não linear (HSIC) em 5 e 30 min sobra (27% contra 12–14%).
**Diagnóstico exploratório** (`scripts/m28_diag_dependencia.py`, saída em `reports/m28diag/diag_pares.json`) feito **só nas 42 origens pares** (0, 2, …, 82), observado contra 19 referências do HXLOC, decompondo a dependência por par de coordenadas:
- **Volume alto agora → agressão mais equilibrada depois:** corr(ν_t, |ι_{t+5}|) observada −0,10, abaixo do modelo em **95% das origens** (z mediano −2,2); em 30 min, −0,08 (86%).
- **Retorno grande agora → volume maior depois:** corr(|z_t|, ν_{t+5}) acima do modelo em **93%**.
- A volatilidade própria (|z|→|z|, |ι|→|ι|) **já está certa** (z mediano ≈ 0).

Leitura: o modelo liga a variância aos **choques recentes** (r²), mas não ao **nível de atividade**. No BTC, a escala do retorno e da agressão depende de quanto se negocia: com mais negócios, o desequilíbrio relativo ι = (compra − venda)/volume se concentra perto de zero (lei dos grandes números) — e é a hipótese clássica da mistura de distribuições (Clark, 1973; Tauchen e Pitts, 1983), em que o volume mede o "relógio" da informação.
**As 41–42 origens ímpares não foram olhadas** e são o conjunto de teste deste protocolo. Nenhum ajuste do novo modelo foi feito em dado real antes deste documento.

## Modelo
**`HXACT`** = HXLOC (M27: 6 trechos, parâmetros locais, blocos de 500, inovações reais filtradas do trecho) com a variância de cada coordenada multiplicada por um fator de atividade:
h*_j,t = h_j,t · g_j,t,  g_j,t = exp(γ_j · (ν_{t−1} − ν̄)) / média do trecho,
onde ν_{t−1} é o volume **completo** do minuto anterior (incluindo o bloco lento real) e h_j,t é a variância cruzada do M26. γ_j é estimado por quase-verossimilhança em cada trecho, depois da variância cruzada (dois estágios), com |γ| ≤ 2. Na simulação, o bloco lento real entra dentro do laço (para que g veja o volume completo), inclusive no aquecimento.
Referências pareadas: **`HXLOC`** (M27) e **`BL`**. Mesmas 12 estatísticas, 39 referências, posto conservador, alarme p ≤ 0,05. Roda nas 84 origens; **os testes primário e de mecanismo usam só as ímpares.**

## Critérios pré-registrados
1. **Mecanismo (origens ímpares, teste do sinal unilateral, α = 0,05 cada):** γ_ι (mediana dos 6 trechos por origem) **negativo** na maioria das origens; γ_z **positivo** na maioria.
2. **Primário (origens ímpares):** HXACT alarma menos que HXLOC em `hsic_5` e `hsic_30` (McNemar exato pareado, unilateral, α = 0,05/2 cada).
3. **Veredito do HXACT (84 origens, para comparar com M25–M27):** "adequação plena" / "equivalente ao BL" (nenhuma das 12 significativamente pior, α = 0,05/12) / "não fecha a lacuna". Reporto também o mesmo veredito só nas ímpares.
4. **Não piorar:** descritivo — nenhuma das 10 estatísticas já adequadas no M27 deve piorar significativamente contra o HXLOC (McNemar bilateral, α = 0,05/12), registrado como alerta se ocorrer.

## Ressalvas
- A hipótese nasceu das origens pares; as ímpares são vizinhas no tempo (janelas sobrepostas parcialmente), então o "teste" é mais honesto que no M26, mas não independente. Confirmação de verdade só em dado virgem.
- 42 origens dão pouco poder para McNemar: um primário não significativo com queda grande será lido como "direção certa, sem poder", não como refutação.
- Dois estágios (variância cruzada, depois γ) não são a máxima verossimilhança conjunta.

## Apostas de Claude (antes de qualquer código)
| Item | Aposta |
|---|---|
| γ_ι negativo na maioria das ímpares (sinal significativo) | ≈ 85% |
| γ_z positivo na maioria das ímpares (sinal significativo) | ≈ 60% |
| Primário significativo em `hsic_5` | ≈ 35% |
| Primário significativo em ≥ 1 das 2 | ≈ 45% |
| Veredito "equivalente ao BL" (84 origens) | ≈ 35% |
| Veredito "adequação plena" (84 origens) | ≈ 8% |
| Alguma estatística já adequada piora significativamente | ≈ 10% |
