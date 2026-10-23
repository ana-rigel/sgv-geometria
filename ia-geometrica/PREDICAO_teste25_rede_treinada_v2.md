# Predição do teste 25 (OBS-01 etapa dois, v2: redes treinadas até perto do ótimo)

18/10/2026 · escrita antes de rodar · corrige o defeito 36 do teste 24, e só ele

**Pergunta:** a do teste 24, com a condição de treino como pré-requisito. **O que muda:** 8 redes (sementes 1–8), 4.000 passos de otimização cada (lr 3e-3, BPTT em blocos de 2.000); uma rede só entra no julgamento se a perda relativa final for ≤ 0,45 (o ótimo linear é 0,31); se menos de 6 das 8 chegarem lá, o teste é **INCONCLUSIVO** (a régua não foi testada). Tudo o mais igual ao 24: 5 mundos de avaliação, corte por primeira travessia do ganho normalizado, faixa de Wiener [1/1.400, 1/35], teste de amplitude 0,5× e 2×, rede sem treino como nulo relatado.

**Critério (um julgamento):** entre as redes válidas, ≥ 5 de 6 (ou ≥ 6 de 7, ≥ 7 de 8) com cv do corte < 0,2 **e** corte mediano na faixa.

**Apostas:** ≥ 6 redes chegam a 0,45 (60 %); passar, dado que chegam (65 %): o teste 24 mostrou que as redes que viraram filtro já eram estáveis e na faixa (7 de 7 das que tinham ν̂ ≈ 0,5); D(2×) > 0,05 em ≥ 5 das válidas (60 %).

**O que fecha:** passar: etapa dois do OBS-01 feita em rede pequena. INCONCLUSIVO: custo de treino, não a régua; repetir com mais máquina. Reprovar com redes válidas: a régua não lê um observador treinado de forma estável, e o OBS-01 precisa de régua por mundo.

## Emenda 1 (23/10/2026, antes da segunda rodada) — defeito de instrumento (37: receita de treino)

A primeira rodada (19/10) foi INCONCLUSIVA: 0 de 8 redes chegaram à perda relativa ≤ 0,45 com a receita do teste 24 (RNN tanh, BPTT em blocos de 2.000 sem estado carregado). Fumaça de receita em 23/10, uma rede (semente 1), 1.500 passos, estado carregado entre blocos consecutivos e taxa com decaimento cosseno: RNN tanh 0,472; **GRU 0,336** (ótimo linear 0,31). Conserto: a rede treinada passa a ser uma GRU de 32 unidades com essa receita (1.500 passos; blocos de 2.000 com estado carregado; Adam 3e-3 com cosseno; clipping 1). O observador medido muda de classe (GRU em vez de RNN tanh) e isso fica declarado: a pergunta é sobre a régua num observador treinado, não sobre a arquitetura. Nada mais muda: critério, faixa, pré-requisito (≤ 0,45), 8 redes, 5 mundos, apostas. Cláusula de última emenda.
