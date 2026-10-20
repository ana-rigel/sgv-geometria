# Predição do teste 40 (etapa 40-A: os ramos de equilíbrio do disco, sem controlador)

20/10/2026 · escrita antes de calcular · modelo de teste37.py (12 anéis, m = 5, 200 km/s), sem memória e sem laço · Ana Rigel

## De onde vem

Da leitura do teste 39 e do texto do colaborador de 20/10 ("NCG-40"). O colaborador mostrou que a condição de equilíbrio não basta e que é preciso demonstrar estabilidade dinâmica (defeito 58). Ele propôs fazer a análise matemática antes de qualquer novo controlador, começando por: **há algum equilíbrio de coerência intermediária, com autovalores estáveis, no sistema sem controlador?** (etapa 40-A). Ele também corrigiu uma afirmação da leitura 39: um controlador "mais lento que o disco" não é uma condição geral, porque se a ordem cresce sozinha perto do equilíbrio (a > 0), o laço lento viola ελ > a.

Este teste é só a etapa 40-A. Não há controlador nem memória.

## O sistema

```
dθᵢ/dt = Δωᵢ + (K/N) Σⱼ sen(θⱼ − θᵢ),   N = 12,  Δωᵢ = m(V/rᵢ − média)·1,0227×10⁻³ rad/Myr
```

No referencial que gira com a fase média, um equilíbrio é um estado **totalmente travado**: sen(θᵢ − ψ) = Δωᵢ/(KC) para todo i, com C dado pela autoconsistência

  C = (1/N) Σᵢ sᵢ √(1 − (Δωᵢ/(KC))²),  sᵢ = ±1.

Com u = KC ≥ max|Δωᵢ|, cada escolha de sinais dá uma curva K(u) = u/C(u). O ramo com todos os sᵢ = +1 é o candidato a estável. Os ramos com um sᵢ = −1 são os candidatos a sela. O limiar de travamento K_L é o menor K em que o ramo todo positivo existe; C_L é a coerência nesse ponto.

**Estabilidade:** jacobiano Jᵢⱼ = (K/N) cos(θⱼ − θᵢ) para i ≠ j, Jᵢᵢ = −Σⱼ≠ᵢ Jᵢⱼ. Ele tem um autovalor nulo, o da rotação global de fase, que não conta. Estável significa todos os outros autovalores < 0.

**Abaixo de K_L não há equilíbrio.** O disco fica num regime que se move (anéis que escorregam), e o que se mede é a média de C no tempo. Ela é calculada por simulação sem ruído, de 1.000 a 3.000 Myr, numa grade K/K_c = 0,50 a 1,60 com passo 0,01, partindo de duas condições iniciais: **coerente** (fases N(0; 0,15)) e **sorteada** (fases uniformes, 20 sorteios, semente 40). Relatado também com o ruído D = 2,5 × 10⁻⁴ rad²/Myr (20 sementes).

K_c = 2(max Δω − min Δω)/π ≈ 25,8 mrad/Myr, como nos testes 37–39. Faixa da NGC 628: [0,527; 0,727].

## Conta prévia (só teoria, antes de calcular)

- Para frequências distribuídas de modo uniforme (N → ∞), a transição de Kuramoto é **descontínua**: em K_c, a coerência salta de 0 para π/4 ≈ 0,785, e o ramo estável não passa por valores intermediários. As nossas frequências (Ω ∝ 1/r, raios igualmente espaçados) são quase uniformes, um pouco mais densas nos anéis externos.
- Com 12 frequências discretas, o travamento total exige KC ≥ max|Δωᵢ|. Espero K_L perto de K_c, entre 1,0 e 1,15 K_c, e **C_L acima de 0,70**. Se isso se confirmar, 0,627 não é um equilíbrio deste disco: só aparece como média de um regime em movimento, abaixo de K_L.
- Pelo teorema de Mirollo e Strogatz (2005), o estado travado com todos os cos(θᵢ − ψ) > 0 é estável quando existe, e os estados com um cosseno negativo são instáveis.
- Transições descontínuas costumam ter **histerese**: perto de K_L, partir coerente ou sorteado pode levar a regimes diferentes.
- A curva C̄(K) deve ser íngreme na faixa: o intervalo de K que põe C̄ entre 0,527 e 0,727 deve ser estreito. Isso é ajuste fino, a mesma doença que derrubou a TAR.

## Critérios

**J1, 0,627 não é um equilíbrio:** a coerência no limiar de travamento, C_L, é **≥ 0,70** (o ramo estável começa acima da faixa da NGC 628).

**J2, o ramo travado é estável e as selas são instáveis:** em todos os K da grade com K ≥ K_L, o estado todo positivo tem os autovalores não nulos < 0, e os estados com um sᵢ = −1, onde existem, têm algum autovalor > 0.

**J3, a faixa pede ajuste fino:** sem ruído e partindo coerente, o conjunto de K em que C̄ cai em [0,527; 0,727] tem largura total **< 0,10 K_c**.

**J4, há histerese:** existe algum K da grade em que C̄ partindo coerente e C̄ médio partindo sorteado diferem em **> 0,2**.

Relatado: K_L/K_c, C_L, a curva K(u) dos dois ramos, o maior autovalor não nulo ao longo do ramo, as curvas C̄(K) das duas condições iniciais com e sem ruído, e a largura da janela com ruído.

## Apostas (Claude, antes de calcular)

- **J1: 80 %.** A transição quase descontínua põe o começo do ramo perto de π/4.
- **J2: 95 %.** É o teorema; o risco é numérico, perto de K_L.
- **J3: 60 %.**
- **J4: 50 %.**

## O que fecha

- **J1 passa:** neste modelo, uma coerência de 0,627 **não é um estado de equilíbrio do disco**. É a média de um regime em movimento abaixo do travamento. Nenhum controlador pode "estabilizar o equilíbrio de 0,627", porque esse equilíbrio não existe. O que um controlador poderia fazer é manter o disco **num regime** cuja média é intermediária, o que é outro problema e muda a lei de realimentação que o 40-C procuraria.
- **J1 reprova:** existe um ramo travado e estável que passa pela faixa, e o 40-B e o 40-C podem procurar a região de parâmetros que o estabiliza com memória.
- **J3 passa:** mesmo como regime, a faixa da NGC 628 exige K dentro de menos de 10 % de K_c. Ela é um caso de ajuste fino neste modelo, e não um resultado robusto.
- **J4 passa:** o disco tem memória própria (histerese), sem v0 nenhuma: o regime depende de onde se começou. É um candidato natural ao papel de "memória lenta" que o modelo procurava fora do disco.

Um julgamento por hipótese; sem emenda. Instrumento: teste40.py, escrito depois do commit desta predição.
