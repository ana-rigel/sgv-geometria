# Predição do teste 24 (OBS-01, etapa dois: a rede treinada)

18/10/2026 · escrita antes de rodar · primeiro observador sem verdade analítica

## Pergunta

Nas etapas anteriores a régua foi conferida contra uma função de transferência conhecida. Um modelo treinado não tem essa verdade: os pesos são o que o treino fez deles. **Sobre uma rede recorrente treinada, a régua dá um corte estável, coerente com a tarefa que a rede aprendeu, e declara o seu regime?** O que se exige aqui é consistência, não acerto contra uma verdade.

## A rede e a tarefa

RNN tanh de 32 unidades (PyTorch), treinada por gradiente para **ler a componente lenta** (τ = 700) do mundo escada-3 a partir da soma das três componentes (τ 7, 70, 700). É uma tarefa de separação de escalas: a rede tem de deixar passar o lento e barrar o rápido. Treino: 60.000 passos, BPTT truncada em blocos de 2.000, Adam, 300 passos de otimização; 20 redes (sementes 1–20), cada uma com o seu mundo de treino. Depois do treino os pesos congelam.

**O que a tarefa implica, antes de olhar:** a melhor leitura linear da componente lenta é um filtro de Wiener cujo corte cai onde a potência do lento iguala a do resto, entre 1/700 e 1/70 ciclos/passo. Uma rede que aprendeu a tarefa deve ter corte nessa faixa; é a única "verdade" disponível, e é uma faixa, não um número.

## O que a régua faz

Para cada rede treinada, com 5 mundos de avaliação novos (sementes de entrada 1001–1005, N = 200.000, amplitude de treino): Ĥ por espectro cruzado, corte (primeira travessia de ½ do ganho normalizado), "não ver" ν̂ e "errar" ε̂. Teste de amplitude (teste 23): D entre a amplitude de treino e 0,5× e 2× dela, no primeiro mundo de avaliação. Nulo relatado: a mesma arquitetura **sem treino** (pesos iniciais), medida igual.

## Critério (um julgamento)

(a) **Estabilidade:** para ≥ 16 das 20 redes, o coeficiente de variação do corte entre os 5 mundos de avaliação é < 0,2. (b) **Coerência com a tarefa:** para ≥ 16 das 20 redes, o corte mediano cai em [1/1.400, 1/35] (a faixa de Wiener com folga de 2× para cada lado). Os dois. Relatado, sem critério: ν̂, ε̂, D(0,5×), D(2×), coerência, e os mesmos números na rede sem treino.

## Apostas

- **Passar: 55 %.** A favor: a tarefa força um passa-baixa e o espectro cruzado o vê; o corte de um filtro é estável entre mundos do mesmo espectro. Contra: (i) a rede pode aprender só parte da tarefa em 300 passos e ficar com corte alto, fora da faixa (aposto 30 % nisso em ≥ 5 redes); (ii) com tanh e amplitude de treino em escala 1, a rede pode operar não linear o bastante para o corte variar com o mundo; (iii) "primeira travessia" com ressonâncias de 32 unidades.
- D(2×) acima de 0,05 em ≥ 10 redes (55 %): a rede treinada é não linear na banda em que trabalha.
- A rede sem treino tem corte fora da faixa em ≥ 15 (70 %): o treino move o corte para onde a tarefa pede, e a régua vê o treino.

## O que fecha

Passar: a régua lê um observador treinado sem conhecer os pesos, dá um corte estável e coerente com o que ele aprendeu, e declara o regime; a etapa dois do OBS-01 está feita em rede pequena, e a três é um modelo de pesos abertos lido por camada. Reprovar em (a): a rede treinada não é um observador linear estável o bastante para esta régua, e o OBS-01 precisa de régua por amplitude e por mundo. Reprovar em (b) com (a) passando: ou a rede não aprendeu (o erro de treino dirá), ou o corte que a régua lê não é o da tarefa, e aí a "coerência com a tarefa" precisa de outra definição.

## Nota de fumaça (18/10/2026, antes da rodada oficial)

Uma rede (semente 1) foi treinada como fumaça do instrumento, antes da rodada. Com 300 passos a perda relativa ficou em 0,77 e o perfil de ganho saiu quase plano (corte indefinido: a régua não tem o que cortar numa rede que ainda não aprendeu). Com 1.500 passos a perda caiu a 0,60 e o perfil virou um passa-baixa raso (|H| 0,36 no lento, 0,13 no rápido), com corte definido perto de 10⁻³. Decisão, antes de rodar e sem mudar critério, faixa ou apostas: **1.000 passos de otimização** por rede (compromisso entre aprender e o tempo de máquina: 20 redes × ≈ 2,5 min). A perda relativa final de cada rede é relatada; uma rede com perda relativa > 0,9 é marcada "não aprendeu" e contada no resultado como está (o critério não a exclui). A semente 1 permanece no conjunto.
