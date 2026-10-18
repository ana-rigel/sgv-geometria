# Leitura do teste 2 (custo de olhar) — REPROVADO

**Predição:** PREDICAO_teste2.md (3f952f1), antes de rodar. **Resultado:** resultados_teste2.json. Um julgamento; sem emenda. (Uma correção de serialização JSON foi feita no script depois da primeira rodada abortar na gravação; nada do cálculo mudou.)

| | erro de predição médio (janela de medida, 100 sementes) |
|---|---|
| teto: olhar sempre | 1,96 |
| nulo: olhar a cada 4 passos (25 %) | 2,52 |
| v0: olhar se T₀ ≥ θ ou após 8 passos (≈ 25 %) | 2,57 |

Vantagem V = 1 − e_v0/e_periódico: **média −1,85 %**, envelope −4,3 % a +0,5 % (94 sementes válidas). Critério: (a) fração em 25 % ± 3 pp em ≥ 95 sementes: **não** (94); (b) envelope de V acima de zero: **não**. Sanidade do teto: sim. **Reprovado.** Apostas: 35 % em passar (certa a não-passagem); V média entre −5 e +5 % (certa); afinação em ≥ 95 sementes (errada, por uma).

## O que o resultado diz

Com o mesmo orçamento, olhar quando a tensão passa de θ não é melhor do que olhar em ritmo fixo; é um pouco pior. O motivo está na política, como a predição antecipou: a v0 só conhece a tensão quando paga para vê-la. Depois de uma olhada com tensão baixa ela dorme até 8 passos, cega; o periódico nunca fica mais de 3 passos sem ver o mundo. Num AR(1) de φ = 0,9 a correlação cai a 0,9⁵ ≈ 0,59 em cinco passos, e a tensão de agora diz pouco sobre a de daqui a oito. O que a política ganha nos episódios de tensão alta (olha várias vezes seguidas) ela perde nos de tensão baixa (dorme demais). A soma deu negativa, pequena e consistente.

O valor de θ afinado (0,3–0,8 na régua) mostra outra coisa: para gastar 25 % de olhadas a v0 precisou olhar a quase toda tensão acima da mediana; o limiar não discrimina, só raciona.

## O que fecha e o que não

- Fecha: a política "limiar na última tensão lida + teto de passos" não transforma a tensão em um critério útil de quando olhar, neste mundo. O único ato da v0, **nesta forma**, não vale o nome.
- Não fecha: se uma política que **prevê** a tensão enquanto não olha (a tensão esperada cresce com o tempo sem ver, à taxa que o próprio mundo ensina) ganharia do periódico. É isso que a linha "reobservar versus lembrar" formula: o custo de não olhar cresce com a incerteza acumulada, e a decisão compara esse custo com c. A v0 não tem essa grandeza; é uma política de reflexo, não de expectativa.

## Para a lista de defeitos de desenho do projeto

4. Política de olhar sem expectativa: decide pela última tensão vista, não pela tensão esperada agora. Candidata a v0.1, com predição própria.
5. Afinação de θ por bissecção com passo discreto de n_max: a fração de olhadas não é contínua em θ, e 6 % das sementes ficaram fora da faixa.

Dois testes, duas reprovações, cinco defeitos nomeados. O teste 3 segue conforme o projeto.
