# Predição do teste 44 (43-D: a forma da curva de rotação decide a janela?)

20/10/2026 · escrita antes de rodar · mapa de Kuramoto dos testes 41–42, sem memória (α = 0) · Ana Rigel

## De onde vem

Do teste 42: com as frequências de 12 anéis igualmente espaçadas, a janela de sincronização parcial é praticamente zero em qualquer N; com Ω ∝ 1/r (curva plana), ela tem ≈ 0,14 K_c. Daí a hipótese registrada pelo colaborador: **a persistência da sincronização parcial depende da distribuição radial das frequências, induzida pela curva de rotação.** O plano dele chamou isto de 43-D. A Ana pediu, em 20/10, para continuar os testes da rotação.

Do teste 43 e da busca de 20/10: a zona estável (254″–395″) cai no disco externo, onde Aniyan et al. (2018) modelam um warp a partir de 250″, e a curva de CO do PHANGS acaba em 6,4 kpc (a 9,8 Mpc), longe da zona. A forma de v(r) na zona não está medida. O 0,627 perdeu o vínculo observacional (teste 43); este teste não o usa.

## O sistema

O mapa dos testes 41–42, sem memória:

```
θᵢ ← θᵢ + Δωᵢ + K C sen(ψ − θᵢ)
```

Curvas em lei de potência v ∝ r^β, logo Ω ∝ r^(β−1), anéis igualmente espaçados em r de 9 a 14 kpc. As frequências são **reescaladas para a mesma abertura (max − min) da curva plana**, para que K_c e as escalas de tempo sejam as mesmas e só a **forma** mude.

β ∈ {−0,4; −0,2; 0; +0,2; +0,4} (de curva caindo a curva subindo). N ∈ {12, 24, 48}. K/K_c de 0,90 a 1,20, passo 0,005. 20.000 Myr, 4.000 de transiente. 10 condições iniciais N(0; 0,15) (semente 440).

**Medidas, por (β, N):**
- **janela de sincronização parcial:** os K em que, na maioria das condições, o maior aglomerado travado tem ≥ N/2 anéis e ≥ 1 anel escorrega; largura = pontos × 0,005;
- **K_L:** o menor K em que todos os anéis travam em todas as condições;
- **K de entrada:** o menor K da janela.

## Contas prévias (antes de rodar)

- **Representações.** Para v ∝ r^β, κ = Ω√(2(1 + β)), e Ω − κ/m = Ω[1 − √(2(1 + β))/m] ∝ r^(β−1): a frequência da onda cinemática tem a mesma forma de Ω. Depois da normalização por K_c, as duas dão a mesma janela. A do padrão espiral (Speights et al. 2025) não foi lida e fica fora.
- **Warp como β.** A frequência inferida dos dados é v_obs/(r sen i). Com i ≈ 8,5°, δ ln Ω ≈ −cot i · δi. Uma inclinação que muda Δi graus de 9 a 14 kpc muda o β inferido em ≈ −cot(8,5°) · Δi (rad) / ln(14/9) ≈ **−0,26 por grau**. A grade de β = ±0,4 cobre ≈ ±1,5° de warp na zona.
- **Forma.** Com r uniforme e Ω ∝ r^(β−1), a densidade de frequências é p(Ω) ∝ Ω^(−1 − 1/(1−β)). Quanto menor β, mais assimétrica (densa nas frequências baixas, dos anéis externos). Para β → 1 (rotação sólida), Ω ∝ r^(β−1) ≈ linear em ln r, e ln r é quase uniforme em [9, 14]: a distribuição tende à uniforme, cuja janela é ≈ 0 (teste 42). **Espero a janela encolhendo com β:** curvas que sobem, janela estreita; curvas que caem, janela larga.
- **Escala.** Para distribuições assimétricas, a janela deve sobreviver ao aumento de N (o teste 41 viu a da curva plana parar de estreitar em ≈ 0,065 na janela da faixa).

## Critérios

**J1, recuperação:** com β = 0 e N = 12, a janela de sincronização parcial fica a ≤ 0,02 de **0,14** (teste 42, α = 0).

**J2, a forma importa:** com N = 12, a maior largura entre os cinco β é **≥ 2 ×** a menor.

**J3, a direção prevista:** com N = 12, a largura **decresce** com β (correlação de Spearman entre β e largura ≤ **−0,9**).

**J4, a janela sobrevive em N para curvas planas e descendentes:** para β ∈ {−0,4; −0,2; 0}, a largura em N = 48 é **≥ 0,5 ×** a largura em N = 12.

Relatado: todas as larguras (β × N), K_L e K de entrada; a largura em função do warp equivalente (Δi = −β/0,26 graus).

## Apostas (Claude, antes de rodar)

- **J1: 85 %.**
- **J2: 75 %.**
- **J3: 75 %.**
- **J4: 60 %.**

## O que fecha

- **J2 e J3 passam:** a forma da curva de rotação decide a janela, na direção prevista. Para a NGC 628, isso significa que a janela não pode ser lida dos dados atuais: um warp de 1° na zona muda β em ≈ 0,26 e muda a janela. A pergunta deixa de ser só do modelo e passa a pedir uma medida de i(r) e v(r) na zona.
- **J4 passa:** a sincronização parcial de discos com curva plana ou caindo não é efeito de poucos anéis.
- **J2 reprova:** a forma importa pouco nesta faixa de β; a janela é robusta à incerteza da curva, e o que a estreita é a proximidade da distribuição uniforme, não a curva real.

Um julgamento por hipótese; sem emenda. Instrumento: teste44.py, escrito depois do commit desta predição.
