# Predição do teste 58 (calibração da lente, etapa 2: a v0 distingue sincronização parcial de ruído e de rigidez sem saber o que olha?)

23/10/2026 · escrita antes de rodar (só a fumaça do mundo M4, o trivial, foi rodada para confirmar que o pipeline fecha, como o protocolo manda) · mundos sintéticos, nenhum dado real · Ana Rigel

## De onde vem

Do protocolo "Protocolo IA geométrica — Etapas 1 e 2 (calibração da lente)" (Claude Doc, 23/10/2026). A Ana traça paralelos entre galáxia, mercado, IA e a IA geométrica, e quer entender por que o padrão do micro se repete no macro. Antes de apontar a lente para qualquer sistema real, calibra-se a lente em sistemas de resposta conhecida.

A pergunta é uma só: **a lente da v0 distingue sincronização parcial de ruído e de rigidez, sem ser informada de qual sistema está olhando?**

O que os testes anteriores já respondem e entra aqui como desenho:
- os andares da v0 guardam o parâmetro de ordem complexo (testes 37–42): há fase por corpo, não se precisa de Hilbert;
- com laço de autoconsistência, a lente confundiu o piso do ruído com ordem e travou tudo (teste 38): **aqui a lente é só leitura, sem laço**;
- o piso de |Z| no ruído não é zero (defeito 51): **o piso de κ é medido por permutação**, nunca fixado;
- o mesmo número sai de muitas formas (testes 34 e 37): κ igual entre sistemas não prova mecanismo igual.

## A lente (congelada)

A cascata da v0 como está (testes 37–57), sem laço e sem aprendizado: três registros complexos
R_j ← R_j + λ_j (R_{j−1} − R_j), com R_0 = o sinal do mundo e λ_j = 0,15 · 10^{−(j−1)}.
Os três corpos são os três andares: campo (j = 1), memória (j = 2), organização (j = 3). Nascem vazios (convenção de Juara).

**κ, o índice de acoplamento:** para cada par de corpos, a coerência de fase na janela de leitura,
R_{ab} = |⟨ e^{i(φ_a − φ_b)} ⟩|, com φ_j = arg R_j; κ = média dos três R_{ab}. Está entre 0 e 1.
Janela de leitura: a segunda metade da corrida. Os primeiros 50 passos de cada andar (quando |R_j| ainda é pequeno) ficam fora da média.

**O que a lente recebe:** uma única coluna anônima de números complexos por mundo, o sinal do mundo Z(t) = (1/N) Σ e^{iθ_k(t)}. Não recebe K, nem o nome do mundo, nem a semente.

Isto é uma emenda ao protocolo escrito no Doc, feita antes de rodar: lá se dizia que a lente receberia três séries (um terço dos osciladores cada). Ao escrever o instrumento ficou claro que isso faria κ medir o mundo, não a lente. A lente tem três corpos próprios; o mundo entra por uma porta só. A referência clássica (abaixo) é o que mede o mundo.

## Os mundos (congelados; semente 58; 30 sementes por mundo e por ponto de K)

- **M1 Kuramoto varrido:** N = 100 osciladores, frequências naturais ω_k ~ N(1, 1) (rotação média Ω₀ = 1, comum a M1, M3 e M4: sem rotação, a fase do sinal travado quase não anda em 100 unidades de tempo e o embaralhamento do M5 não teria o que destruir, achado na fumaça em miniatura), dt = 0,01, 10 000 passos, ruído de fase D = 0,01; K varrido em 20 pontos de 0 a 2 K_c, com K_c = 2 σ √(2/π) ≈ 1,596 (fórmula de Kuramoto para a gaussiana). Fases iniciais uniformes.
- **M2 ruído branco:** θ_k(t) independentes e uniformes a cada passo (o sinal do mundo é um ponto aleatório perto da origem).
- **M3 passeio aleatório:** θ_k(t) = θ_k(t−1) + √(2D′) ξ, com D′ = 0,005 (a fase se perde em ~100 passos) e a mesma rotação média Ω₀ = 1 (memória sem acoplamento).
- **M4 travado:** todos os θ_k iguais, rotação uniforme Ω₀ = 1 (|Z| = 1 sempre).
- **M5 Kuramoto embaralhado:** o sinal do M1 em K = 1,5 K_c com o tempo embaralhado (nula de pipeline).

**Piso de permutação:** para o M2, 200 embaralhamentos temporais do próprio sinal; percentil 95 de κ. É o piso de "nada a ver".

**Referência clássica:** R_K = ⟨|Z(t)|⟩ na mesma janela, das fases verdadeiras, sem passar pela lente.

## Os critérios (do protocolo, com o piso por permutação)

| | critério | α |
|---|---|---|
| **T1** localiza a transição | o K em que κ cruza 0,5 (interpolado na média das sementes) cai em ±20 % de K_c; o intervalo bootstrap (30 sementes) contém K_c | 5 % |
| **T2** ordena os regimes | κ(M4) > κ(M1, 2K_c) > κ(M1, 0) ≈ κ(M2) ≈ κ(M3), ordem mantida em ≥ 27 das 30 sementes | — |
| **T3** muda no ruído | κ(M2) e κ(M3) dentro do piso de permutação; Mann-Whitney M2 vs M3 com p > 0,05 | 5 % |
| **T4** nula de pipeline | κ(M5) dentro do piso; Mann-Whitney M5 vs M2 com p > 0,05 | 5 % |

Aprovação exige os quatro. Resultado parcial permitido: T2–T4 sem T1 registra "lente ordena, não mede", e a etapa 4 fica proibida.

**Referência clássica obrigatória:** correlação de Spearman entre κ e R_K ao longo da varredura do M1. Se > 0,95 em todos os mundos, a lente é leitora de R_K e não mede nada além dele; fica registrado.

## Critério de morte

Reprovar em T3 (ou em T2 e T4) fecha a linha "um padrão para todos os sistemas". Sem segunda rodada, sem ajustar a lente e repetir.

## Apostas (antes de rodar)

| quem | aprovação total | teste mais provável de falhar | observação |
|---|---|---|---|
| Ana | 50 % | T3 (passeio aleatório) | idem |
| Claude | 35 % | T3 (passeio aleatório) | a cascata foi feita sobre tensão e memória; a aposta é que o andar 3, lento, guarda uma fase morta no M3 e os pares com ele saem do piso. T1 ~70 %, T4 ~70 %, T2 ~80 % |

Por critério, a aposta de Claude: T1 70 %, T2 80 %, T3 40 %, T4 70 %.

## Execução (barata)

`python ia-geometrica/teste58.py --fumaca` roda só o M4 (confirmação de que o pipeline fecha; nenhum outro mundo é olhado). `python ia-geometrica/teste58.py` roda tudo e grava `resultados_teste58.json`. O workflow `calibracao-etapa2.yml` roda o teste no GitHub Actions e grava o JSON no ramo, para não gastar crédito de conversa rodando. A leitura é escrita depois, em um turno, a partir do JSON.
