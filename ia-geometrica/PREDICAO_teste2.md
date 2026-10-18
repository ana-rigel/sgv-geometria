# Predição do teste 2 (custo de olhar)

18/10/2026 · escrita antes de rodar · instrumento v0.py (c79df9a) · o teste 1 reprovou e ensinou (LEITURA_teste1.md)

## Pergunta

A única ação da v0 é decidir quando olhar o mundo. A política v0 é a mais simples possível: olha se a última tensão T₀ lida está acima de θ na régua, ou se passaram n_max passos sem olhar. **Com a mesma fração de olhadas, essa política deixa a memória mais perto do mundo do que olhar em ritmo fixo?**

## Mundo

`mundo_deriva(φ = 0,9, d = 2)`, N = 8.000 passos por semente, 100 sementes (1000–1099). Janelas: [0, 2.000) calibração da régua (observador olhando sempre); [2.000, 4.000) afinação de θ; [4.000, 8.000) medida. O custo c não entra no mundo: entra como orçamento, 25 % de olhadas.

## Instrumento

- Registros: k = 4, λ₁ = 0,15, b = 10, iguais em todas as políticas (o teste é da política, não da pilha; o teste 1 já disse que λ₁ = 0,15 é cego à escala de um passo deste mundo, e isso vale igualmente para todos os braços).
- Régua: mediana e q99,5 ÷ 3 de T₀ na janela de calibração, com o observador olhando sempre.
- Política v0: n_max = 8 (piso de 12,5 % de olhadas); θ afinado por bissecção na janela de afinação até a fração de olhadas ficar em 25 % ± 1 pp; θ fica fixo na medida. Quando não olha, T₀ não se atualiza (é o que a v0 faz: só sabe a tensão quando paga para vê-la).
- Nulo justo: olhar a cada 4 passos (25 % exatos).
- Teto: olhar sempre.
- Medida: erro de predição e = média de ‖x_t − R₁,t−1‖ na janela de medida (a memória **antes** de ver x_t; não depende de ter olhado em t). Vantagem por semente V = 1 − e_v0 / e_periódico.

## Critério (um julgamento)

Passa se, nas 100 sementes, o envelope de V (mínimo a máximo) estiver inteiro acima de zero, e a fração de olhadas da v0 na medida ficar em 25 % ± 3 pp em ≥ 95 sementes (as outras são excluídas e contadas). Sanidade, não critério: o teto deve ter erro menor que os dois.

## Apostas

- No projeto (17/10) apostei 60 % em passar. Depois do teste 1 e de reler a política, aposto **35 %**: quando a v0 não olha ela fica cega por até 8 passos, enquanto o periódico nunca fica mais de 3; num AR(1) de φ = 0,9 a tensão lida num instante diz pouco sobre a tensão daqui a 5 passos. A política ganha só se os episódios de tensão alta forem persistentes o bastante para valer a troca.
- V média entre −5 % e +5 % (70 %).
- Fração de olhadas calibrável em 25 % ± 3 pp em ≥ 95 sementes (85 %).

## O que fecha

Reprovar: a tensão lida não serve, nesta política e neste mundo, para decidir quando olhar; o único ato da mente não vale o nome **nesta forma**. Fica registrado como candidato a defeito de desenho (política sem previsão de tensão), não como emenda deste teste. Passar: a v0 tem um ato que vale alguma coisa num mundo com memória.
