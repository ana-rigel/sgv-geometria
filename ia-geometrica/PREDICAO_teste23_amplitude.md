# Predição do teste 23 (o teste de amplitude: a régua declara não linearidade)

18/10/2026 · escrita antes de rodar · corrige o defeito 34 do teste 22, e só ele

## Pergunta

No teste 22 uma rede saturada errou o corte em 70 % com coerência 0,91: a régua não soube dizer que estava fora do regime em que vale. Como no OBS-01 a entrada é nossa, a régua pode medir a mesma rede com duas amplitudes. **A diferença entre as funções de transferência estimadas em duas amplitudes separa redes lineares de redes não lineares, sem depender da coerência?**

## O índice (declarado antes)

Para uma rede e um mundo x, estimam-se Ĥ_A em amplitudes A ∈ {0,1; 0,3; 1; 3} (a entrada é A·x; o mundo é o mesmo). Índice de não linearidade entre a amplitude de referência A₀ = 0,1 e outra A:

D(A) = Σ_f S_xx |Ĥ_A − Ĥ_{A₀}|² / Σ_f S_xx |Ĥ_{A₀}|², com os Ĥ **não** normalizados (a normalização pelo ganho estático esconderia uma mudança de ganho, que é parte do que se procura).

Para um observador linear com ruído na saída, D é só o ruído de estimação; para um não linear, D cresce com A. Ruído branco σ = 0,05 somado à saída em todas as versões, para que D tenha piso (sem ruído, D de uma rede linear é zero por construção e o teste seria vazio).

## Redes, mundo, instrumento

As 100 redes do teste 22 (mesmas sementes), nas versões linear e tanh; mundo escada-3; Welch 8.192; N = 200.000.

## Critério (um julgamento)

Limiar fixado antes: **D = 0,05**. Passa se (a) na rede linear D(3) < 0,05 em ≥ 95 sementes, **e** (b) na rede tanh D(3) > 0,05 em ≥ 95 sementes. Relatado: D(0,3) e D(1) nas duas versões (onde a não linearidade começa a aparecer), e a mediana de D(3) em cada versão.

## Apostas

- **Passar: 70 %.** A favor: com ruído de 0,05 e 200.000 passos, o piso de D numa rede linear deve ficar em 10⁻³; a tanh a 3 deforma tanto que D deve passar de 0,3. Contra: se a saída de alguma rede linear tiver ganho estático muito pequeno (r quase ortogonal aos modos lentos), o ruído relativo sobe e D(3) pode ultrapassar 0,05 em poucas sementes; 95 de 100 é exigente.
- D(0,3) da tanh já acima de 0,05 em ≥ 50 sementes (50 %): a não linearidade aparece cedo.
- D(3) mediano da tanh entre 0,3 e 2 (60 %).

## O que fecha

Passar: a régua tem um detector de regime que não depende da coerência, e o protocolo do OBS-01 passa a ter um passo obrigatório antes de qualquer leitura: medir em duas amplitudes e declarar D. Reprovar em (a): o índice é sensível ao ruído, e precisa de normalização pelo piso estimado (outro instrumento). Reprovar em (b): a saturação não muda Ĥ o bastante na banda em que o mundo tem potência, e aí a régua não tem como ver não linearidade por fora.

## Emenda 1 (18/10/2026, antes da segunda rodada) — defeito de instrumento

A primeira rodada (242b205) estimou Ĥ_A = S_yx / S_xx com x (o mundo) no denominador, quando a entrada que a rede recebeu foi A·x. Para uma rede linear isso dá Ĥ_A = A·H, e o índice mede ((A − A₀)/A₀)² em vez de não linearidade: D(3) na rede linear deu 836 ≈ 29². Resultado da primeira rodada registrado como inválido (resultados_teste23_INVALIDO.json). Conserto: Ĥ_A estimado com a entrada efetiva A·x (S_{y,Ax} / S_{Ax,Ax}). Nada mais muda: mesmo índice, mesmo limiar, mesmas apostas. Cláusula de última emenda: se reprovar de novo, fica reprovado.
