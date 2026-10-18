# Predição do teste 4 (escada livre)

18/10/2026 · escrita antes de rodar · instrumento v0.py (c79df9a) · testes 1–3 reprovados

## Pergunta

A escada b = 10 é da mente ou do mundo? **Deixando os ganhos λ_j livres, a v0 reencontra a escada de um mundo que tem escada, e, num mundo com uma escala só, aceita um andar fora do passo?**

## Mundos

N = 20.000 passos, d = 2, 100 sementes (1000–1099). Calibração (ajuste) em [0, 10.000); medida em [10.000, 20.000).

- escada-2: `mundo_escada(taus = [7, 70])`; observador com k = 2.
- escada-3: `taus = [7, 70, 700]`; k = 3.
- escada-4: `taus = [7, 70, 700, 7000]`; k = 4.
- cíclico: `mundo_ciclico(período 300)`, senoide forte mais ruído branco fraco; k = 4.

## Instrumento

- Leitura: pesos w por mínimos quadrados sobre os k registros R_{t−1} (a memória antes de ver x_t), como no teste 1; erro de predição e = média ‖x_t − Σ_j w_j R_{j,t−1}‖ na medida. O mau condicionamento do teste 1 (defeito 3) é tratado aqui com ridge pequeno (α = 10⁻⁶ · traço), declarado.
- Ajuste livre: λ = sigmoide(u), u ∈ ℝ^k, minimizando o erro de leitura na calibração (Nelder–Mead, 3 partidas: escada b = 10 com λ₁ ∈ {0,5; 0,15; 0,05}; fica a melhor na calibração). Registros por `scipy.signal.lfilter` em cascata (idêntico à recursão do v0, só mais rápido).
- Nulo: escada fixa λ₁ = 0,15, b = 10 (os λ da v0), mesma leitura.
- Escada recuperada: λ ordenados em ordem decrescente; razões r_j = λ_j / λ_{j+1}. "Recupera" = todas as k − 1 razões em [7, 13] (10 ± 30 %). Relata-se também λ_j · τ_j (seria 1 se o andar caísse na constante de tempo do mundo).

## Critério (um julgamento)

Passa se: (a) em cada mundo-escada, as razões ficam em [7, 13] em ≥ 80 das 100 sementes; (b) no cíclico, ≥ 80 sementes têm alguma razão fora de [7, 13] **e** o ajuste livre tem erro menor que a escada fixa em ≥ 80 sementes. Sanidade, não critério: nos mundos-escada o livre não deve perder da fixa.

## Apostas

- Passar: **25 %** (o projeto apostou 50 %). A razão para baixar, escrita antes de rodar: a soma de k processos AR(1) é um ARMA(k, k−1), e o seu melhor preditor linear de um passo tem polos nas raízes da parte MA, não nos φ_j do mundo. O ajuste que minimiza erro de predição não tem por que pôr os andares nas constantes de tempo do mundo; ele os põe onde a predição melhora. Se for isso, a v0 "reencontra" uma escada que é da predição, não do mundo, e (a) reprova mesmo com a mente funcionando. Este é um defeito possível do teste como o projeto o escreveu, nomeado antes do resultado, e não corrigido para não mudar o teste depois de pensado.
- (a) passa na escada-2 (45 %), na escada-3 (30 %), na escada-4 (20 %): quanto mais andares, mais a leitura se afasta das constantes do mundo.
- (b) passa (65 %): a senoide de período 300 pede um andar perto de λ ≈ 2π/300 ≈ 0,02 e nada em outras escalas; a progressão deve quebrar.
- Livre ≤ fixa em todos os mundos (90 %).

## O que fecha

Reprovar (a): a auto-similaridade da v0 é projeção **ou** o teste mede a coisa errada (ver aposta); a leitura distingue os dois pelo λ_j · τ_j. Reprovar (b): a escada fixa não é pior num mundo sem escada, e então a escada não custa nada e também não diz nada. Passar: a escada é do mundo, e a v0 a lê.
