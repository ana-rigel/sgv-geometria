# Predição do teste 7 (a política de expectativa)

18/10/2026 · escrita antes de rodar · corrige o defeito 4 do teste 2, e só ele

## Pergunta

No teste 2 a v0 decidia olhar pela **última** tensão vista e dormia cega até n_max passos; perdeu por 1,9 % do periódico. A candidata: decidir pela tensão **esperada agora**, dado o que viu por último e há quanto tempo não olha. **Com a mesma fração de olhadas, a política de expectativa deixa a memória mais perto do mundo do que olhar em ritmo fixo?**

## O que muda e o que não muda

- **Expectativa aprendida na calibração.** Com o observador olhando sempre em [0, 2.000), para cada n = 1 … n_max ajusta-se por mínimos quadrados E[‖x_{t+n} − R₁,t‖ | T₀,t] = a_n + b_n · T₀,t: o erro que a memória **congelada** por n passos terá, dado a tensão da última olhada. É o que a linha "reobservar versus lembrar" chama de custo de não olhar, aprendido do próprio mundo e só com o que a v0 vê.
- **Política.** No passo t, com n passos desde a última olhada e T_última a tensão lida nela: olha se (a_n + b_n · T_última) na régua ≥ θ, ou se n ≥ n_max. n_max = 16 (o dobro do teste 2: a expectativa é quem deve dizer quando acordar, e o teto de passos fica só como segurança).
- **Tudo o mais igual ao teste 2:** `mundo_deriva(φ = 0,9)`, N = 8.000, 100 sementes, k = 4, λ₁ = 0,15, b = 10, régua de T₀ na calibração, θ afinado por bissecção em [2.000, 4.000) para 25 % ± 1 pp, medida em [4.000, 8.000), erro de predição ‖x_t − R₁,t−1‖, nulo periódico a cada 4, teto olhar sempre, V = 1 − e_v0 / e_periódico.

## Critério (um julgamento)

O do teste 2: envelope de V acima de zero nas sementes válidas, e fração em 25 % ± 3 pp em ≥ 95 sementes.

## Apostas

- **Passar: 40 %.** A favor: a expectativa cresce com n e com T_última, então a política acorda cedo depois de uma tensão alta e tarde depois de uma baixa, que é o que o periódico não faz. Contra: num AR(1) de φ = 0,9 a informação de T_última decai rápido (b_n → 0 em poucos passos), e a partir daí a expectativa é só a_n, que é função de n: a política vira periódica com outro nome. Se b_n for pequeno já em n = 3, aposto no empate.
- V média entre 0 e +4 % (55 %); envelope cruzando zero (60 %: ganha na média e reprova no critério, que é estrito).
- b_n > 0 em todos os n (90 %); b_n cai abaixo de 0,2 antes de n = 5 (65 %).

## O que fecha

Passar: o único ato da v0 vale alguma coisa quando ela tem expectativa; o custo de não olhar é uma grandeza que ela consegue aprender e usar. Reprovar com V média positiva: a expectativa ajuda e o critério de envelope é estrito; fica reprovado assim mesmo, e a leitura diz o tamanho. Reprovar com V ≤ 0: neste mundo a tensão não carrega informação útil sobre quando olhar, e a política de olhar precisa de outro insumo (a cegueira declarada, por exemplo), com predição própria.
