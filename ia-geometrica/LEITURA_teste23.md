# Leitura do teste 23 (o teste de amplitude) — PASSOU, com Emenda 1

**Predição:** PREDICAO_teste23_amplitude.md (242b205; Emenda 1 em 2a97635, antes da segunda rodada). **Resultado:** resultados_teste23.json (a primeira rodada, inválida por defeito de instrumento, está em resultados_teste23_INVALIDO.json). Um julgamento; uma emenda, de instrumento, registrada antes de rodar de novo, a primeira do projeto em 23 testes.

| versão | D(0,3) mediano · > 0,05 em | D(1) mediano · > 0,05 em | D(3) mediano · > 0,05 em |
|---|---|---|---|
| linear (+ ruído 0,05) | 0,0061 · 5 | 0,0055 · 5 | **0,0055 · 5** |
| tanh (+ ruído 0,05) | 0,081 · 81 | 0,44 · 100 | **0,75 · 100** |

Critério: (a) linear D(3) < 0,05 em ≥ 95: **sim, 95** (no limite); (b) tanh D(3) > 0,05 em ≥ 95: **sim, 100**. **Passou.** Quarta passagem do projeto. Apostas: 70 % em passar, certa; D(0,3) da tanh acima do limiar em ≥ 50 (certa: 81); D(3) mediano da tanh entre 0,3 e 2 (certa: 0,75).

## O que o resultado diz

**A régua, por ser também o mundo, consegue perguntar à rede se ela é linear, e a rede responde.** Numa rede linear o índice fica no piso do ruído (0,006) em qualquer amplitude; numa rede tanh ele cresce com a amplitude (0,08 → 0,44 → 0,75) e já passa do limiar em 81 de 100 redes com entrada 0,3, onde a saturação mal começou. A coerência (teste 22) não via nada disso; o teste de amplitude vê, e vê cedo.

As 5 redes lineares acima do limiar são as que a predição temia: leitura r quase ortogonal aos modos que o mundo excita, ganho estático pequeno, ruído relativo alto; D(0,3), D(1) e D(3) iguais nelas (0,006 mediano em todas as amplitudes) confirmam que é piso de ruído, não não linearidade. O critério passou por uma semente; o índice precisa de piso declarado (medir D com a **mesma** amplitude duas vezes, com ruído independente, e usar esse D₀ como referência) para que o limiar não dependa do ganho da rede. Fica como defeito 35, não corrigido aqui.

**A emenda.** A primeira rodada estimou Ĥ com o mundo no denominador em vez da entrada efetiva A·x; numa rede linear isso dá Ĥ_A = A·H e D(3) = ((3 − 0,1)/0,1)² = 841, que foi o que saiu (836). O número denunciou o erro antes de qualquer leitura; a emenda consertou o estimador e nada mais, e está escrita antes da segunda rodada, com a cláusula de última emenda. É o primeiro uso da regra 2 da casa neste projeto, e o caso em que ela foi feita para ser usada.

## O que fecha e o que não

- Fecha: o protocolo do OBS-01 ganha um passo obrigatório antes de qualquer leitura: medir em duas amplitudes e declarar D; se D passa do limiar, o observador não é linear e as cláusulas 1–5 valem só por amplitude (e a régua deve então ser lida na amplitude em que o modelo opera).
- Não fecha: o piso de D por rede (defeito 35); e a pergunta seguinte do OBS-01, que é a etapa dois: uma rede **treinada**, sem verdade analítica, onde a régua só tem consistência (corte estável entre sementes de entrada, D declarado, embaralhado zerando a coerência).

## Para a lista de defeitos de desenho do projeto

35. Limiar fixo de D sem piso por rede: redes de ganho pequeno sobem o ruído relativo; o piso deve ser medido na mesma amplitude com ruído independente.

Vinte e três testes, dezenove reprovações, **quatro passagens**, trinta e cinco defeitos, uma emenda. Sexta cláusula do OBS-01 testada e de pé.
