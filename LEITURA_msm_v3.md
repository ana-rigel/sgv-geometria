# Leitura: MSM v3, ciclo diário removido (jun–jul e ago–set/2026) — INCONCLUSIVO

**Predição:** PREDICAO_msm_v3.md com Emendas 1 e 2, registradas antes de cada rodada. **Rodadas:** local jun–jul (instrumento original), Actions 39001860521 (ago–set, ajuste degenerado), 39005824801 (Emenda 1, abortou na validação por filtro errado), 39007912458 (Emenda 2: ago–set falhou no real, jun–jul cancelado pela matriz).

## Veredito

**INCONCLUSIVO.** Em ago–set, a série dessazonalizada por variância não admite ajuste regular do MSM-t: todas as tentativas terminam com m₀ no teto (2,0) ou ν no piso (2,16 na primeira rodada; abaixo de 2,3 com a Emenda 2), as duas degenerações que explodem a verossimilhança. A cláusula da Emenda 2 encerra a v3 sem classe. Só um período tem ajuste regular, e um período não conta.

## O que ficou medido (sem valer como veredito)

**Jun–jul, instrumento original (f95c0e5), validação aprovada (k = 2 e 3 recuperados com a grade até 5):** k* = 5; escalas 4,7 min · 42 min · 6,9 h · 2,9 d · 28 d; b = 9,9; m₀ 1,52; ν 6,8; ΔBIC 5362 / 1735 / 906 / 321. Lido com cuidado: o degrau intermediário saiu de 16 h (v2) para 6,9 h, fora da faixa 8–16 h, e o ganho do 4º degrau não caiu (906 vs 908). Dessazonalizar não derrubou um andar; deslocou um e abriu outro no topo, com a ressalva de que uma escala de 28 dias em 61 dias de dados troca de estado duas vezes e é fronteira de amostra.

**Ago–set:** o instrumento não ajusta. Causa provável: a dessazonalização por divisão deixa os retornos nulos exatos (minutos sem mudança de preço) e os retornos das horas vazias, divididos por s(h) pequeno, com cauda mais gorda que a Student-t com ν ≥ 2,3 comporta; na v2 (sem dessazonalizar) ago–set já tinha ν = 2,75, o período mais gordo. O MSM binomial com t padronizada não é instrumento para essa série.

## Defeitos de desenho registrados nesta versão

1. Dessazonalização por divisão sem tratamento dos retornos nulos (Emenda 1 tratou o sintoma, não a causa).
2. Filtro de degeneração da Emenda 1 amplo demais (corrigido na Emenda 2).
3. Matriz do Actions com fail-fast: a falha de um período cancelou o outro. Para futuras rodadas em matriz, `fail-fast: false`.

## Apostas (não julgadas: INCONCLUSIVO)

A aposta principal (65 % em "escada fica de pé" nos dois períodos) não pode ser lida. Em jun–jul, isoladamente, ela teria acertado; a de 55 % em "degrau intermediário sai de 8–16 h" também; a de 50 % em "ganho do 4º degrau cai menos que pela metade", também. Nada disso conta sem ago–set.

## O que seria preciso

Uma v4 com inovação de cauda mais gorda que a t (por exemplo, mistura de duas gaussianas ou t com ν por componente), tratamento explícito dos retornos nulos, e `fail-fast: false`. Não pedida; registrada como item aberto.

Em nenhum caso há direção, previsão ou lucro.
