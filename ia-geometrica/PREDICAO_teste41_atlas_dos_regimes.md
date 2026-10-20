# Predição do teste 41 (41-B/C/D: o atlas dos regimes em movimento)

20/10/2026 · escrita antes de rodar · disco de teste40.py, sem memória e sem controlador · Ana Rigel

## De onde vem

Do teste 40 e do segundo texto do colaborador (20/10). O teste 40 mostrou que, abaixo do travamento (K_L = 1,115 K_c), não há equilíbrio e a coerência da NGC 628 só aparece como média de um regime em movimento, numa janela de K/K_c ≈ 0,96–1,03. A enumeração dos 4.096 ramos (correção da leitura 40) mostrou um único equilíbrio estável em todo K, e selas com C ≈ 0,627 só de ≈ 1,6 K_c para cima. Isso cumpre a 41-A. O colaborador mudou o objeto de "equilíbrio" para **regime estatisticamente estacionário** e pediu para separar três casos: (1) uma média que ainda está mudando devagar; (2) uma média estável produzida por um regime persistente; (3) uma média que só aparece numa faixa estreita de K. Ele também pediu medir o escorregamento das fases, e não só C.

Um dado conhecido entra na conta prévia: num Kuramoto finito com frequências quase igualmente espaçadas, o regime abaixo do travamento pode ser **caótico** ("caos de fase", Popovych, Maistrenko e Tass, Phys. Rev. E 71, 065201, 2005, para N ≥ 4).

## O sistema

O mapa dos testes 37–40, sem ruído (o modelo é o mapa de passo 1 Myr):

```
θᵢ ← θᵢ + Δωᵢ + K C sen(ψ − θᵢ),   Z = C e^{iψ} = média de e^{iθ}
Δωᵢ = m(V/rᵢ − média) · 1,0227×10⁻³,  rᵢ = linspace(9, 14, N),  K_c = 2(max Δω − min Δω)/π
```

Grade fina: K/K_c = 0,90 a 1,12, passo 0,005 (45 valores). 20.000 Myr por trajetória; os primeiros 4.000 são transiente. **Condições iniciais:** uma coerente (N(0; 0,15)) e 20 sorteadas (semente 41).

**Medidas, por K:**
- **C̄** nos 16.000 Myr finais, e em quatro janelas de 4.000 Myr; **deriva** = maior − menor das quatro.
- **Frequência efetiva** de cada anel, Ωᵢ = (θᵢ(fim) − θᵢ(4.000))/16.000, contada no referencial que gira com o anel de maior aglomerado; **aglomerado travado** = o maior grupo de anéis com Ωᵢ iguais a menos de 10⁻⁴ rad/Myr.
- **Maior expoente de Lyapunov** do mapa (vetor tangente renormalizado a cada passo, com a direção da rotação global de fase projetada fora), condição coerente.
- **Espalhamento entre condições iniciais:** maior − menor C̄ entre as 21.

**A janela da faixa:** os K da grade em que C̄ (condição coerente) cai em [0,527; 0,727].

**41-D, robustez em N:** a mesma grade e as mesmas medidas de C̄ para N = 8, 16 e 24 (r de 9 a 14 kpc), condição coerente, e a largura da janela em K/K_c.

Relatado: a curva C̄(K) com as 21 condições; Ω de cada anel; λ_max(K); a mesma janela com o ruído D = 2,5 × 10⁻⁴ (5 sementes).

## Conta prévia

- Pelo teste 40, a janela de N = 12 fica perto de 0,96–1,03 (≈ 15 pontos da grade).
- Abaixo de K_L não há ponto fixo; todo regime tem escorregamento. A pergunta útil é a **estrutura**: um aglomerado grande travado com poucos anéis escorregando (sincronização parcial) ou um movimento sem aglomerado.
- Perto de K_c, na janela, espero um aglomerado dos anéis centrais e os anéis das pontas (9 e 14 kpc, as maiores |Δω|) escorregando.
- Pelo caos de fase, espero λ_max > 0 em boa parte da janela, mais perto do lado de baixo (mais anéis escorregando, mais graus de liberdade).
- Com N maior, as frequências ficam mais densas e mais próximas do uniforme, e a transição fica mais abrupta: a janela deve **estreitar** com N.
- Com 20.000 Myr e o tempo de relaxação de ≈ 380 Myr perto do limiar, 4.000 Myr de transiente bastam para a média sair da origem; se a deriva entre janelas ficar alta, é sinal de intermitência.

## Critérios

**J1, a média persiste:** em **≥ 80 %** dos K da janela, a deriva de C̄ entre as quatro janelas é **≤ 0,02**.

**J2, sincronização parcial:** em **≥ 80 %** dos K da janela, o aglomerado travado tem **≥ 6 anéis** e há **≥ 1 anel** escorregando.

**J3, caos de fase:** em **≥ 50 %** dos K da janela, λ_max > **5 × 10⁻⁴ /Myr**.

**J4, um só atrator estatístico:** em **≥ 80 %** dos K da janela, o espalhamento de C̄ entre as 21 condições iniciais é **≤ 0,03**.

**J5, a janela estreita com N:** a largura da janela em K/K_c decresce de N = 8 para 12, 16 e 24 (estritamente, nos quatro).

## Apostas (Claude, antes de rodar)

- **J1: 70 %.** 16.000 Myr bastam para uma média estável, a menos que o regime seja intermitente perto das bordas da janela.
- **J2: 55 %.** Pode haver K da janela em que o maior aglomerado tem menos de 6 anéis.
- **J3: 55 %.**
- **J4: 70 %.** O teste 40 não viu histerese que contasse.
- **J5: 55 %.** A tendência deve existir, mas com 0,005 de passo e janelas de poucos pontos, a monotonia estrita é exigente.

## O que fecha

- **J1 e J4 passam:** é o caso (2) do colaborador. A coerência intermediária é um regime estatisticamente estacionário, o mesmo para qualquer ponto de partida. Se J2 passa, é sincronização parcial; se J3 passa, é caótica. Isso abre o Caminho A dele: uma memória que amplie a região de atração ou a largura da janela, sem alvo.
- **J1 reprova:** a média ainda muda em 16 Gyr, ou o regime é intermitente; é o caso (1), e nada se pode dizer sobre 0,627 neste modelo sem tempos maiores.
- **J5 passa:** o caso (3) piora com N. Um disco com mais anéis (mais perto do contínuo) precisa de ajuste mais fino para ficar na faixa, e o Caminho B (mudar a física) ganha prioridade.

Um julgamento por hipótese; sem emenda. Instrumento: teste41.py, escrito depois do commit desta predição.
