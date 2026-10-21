# Leitura do teste 51 (andares com ritmo): J1, J2 e J3 REPROVADOS; J4 passou pela letra e não diz nada. Os relógios se organizaram entre si, num ritmo de 151 dias que é a média das próprias frequências, e ficaram surdos ao ano. Aprender com o próprio erro gera consenso, não conhecimento do mundo

**Predição:** PREDICAO_teste51_andares_com_ritmo.md (8d9b5c5), antes de simular. **Instrumento:** teste51.py (7187e8a). **Resultado:** resultados_teste51.json. **Diagnóstico depois do julgamento:** diagnostico_teste51_pos_julgamento.txt. Quatro julgamentos; sem emenda.

## Resultados

| | resultado | critério | |
|---|---|---|---|
| **J1** a teoria prevê quem trava | **14 %** das 90 células iguais (só K ≤ 0,01) | ≥ 85 % | **reprovado** |
| **J2** aprender recruta todos para o ano | ω_j/Ω = **2,31–2,38** nos quatro andares, nos seis lugares | ≤ 5 % de Ω | **reprovado** |
| **J3** a organização sobrevive ao silêncio | com aprendizado: **154–158 dias**; controle: 404–407 dias | ≤ 5 % de 365 / > 5 % | **reprovado** (o controle passou) |
| **J4** nulo sem estações | **150–156 dias** | > 10 % de 365 | passou, **não conta** |

Apostas: J1 (55 %), J2 (50 %) e J3 (60 %) erradas; J4 (85 %) certa pela letra.

Frequências realizadas sem aprendizado, em Juara (mediana de 20 inícios; por Ω):

| K | andar 1 | andar 2 | andar 3 | andar 4 |
|---|---|---|---|---|
| 0 | 8,70 | **0,995** | 0,074 | 0,008 |
| 0,01 | 8,69 | **0,991** | 0,075 | 0,076 |
| 0,02 | 8,66 | 0,43 | 0,29 | 0,29 |
| 0,1 | 6,98 | 0,91 | 0,91 | 0,91 |
| 0,2 – 0,4 | 2,41 | 2,41 | 2,41 | 2,41 |

## O que o resultado diz

**1. A teoria que escrevi estava errada num ponto preciso (defeito 71).** Fixei o referencial girando com o ano e perguntei, andar por andar, quem trava ali. Mas, somando as equações de fase, o acoplamento mútuo se cancela:

  Σ dφ_j/dt = Σ ω_j − ε Σ s_j sen φ_j.

O acoplamento entre andares **não muda a frequência média do aglomerado**; só a forçante do mundo muda. Para os andares 2–4 girarem com o ano, a forçante teria de pagar Σ(ω_j − Ω) = −0,035 rad/dia, e ela só oferece ΣF = 0,0048. Os andares 3 e 4 quase não ouvem o ano. Quando se acoplam ao 2, eles o arrastam para fora do ano em vez de serem arrastados para dentro: com K = 0,02, o andar 2 cai de 0,99 Ω para 0,43 Ω.

O solver do teste 46 resolvia a frequência do referencial; a minha adaptação a fixou. A conta prévia foi feita, como pediam os defeitos 66 e 70, mas não foi conferida com uma única simulação curta antes dos critérios.

**2. O achado principal: com aprendizado, os andares se organizam, mas em torno de si mesmos.**
- Ao fim de 2017, os quatro relógios têm a **mesma** frequência, nos seis lugares: ≈ 2,32 Ω, um período de ≈ 157 dias.
- Esse ritmo é a média das frequências naturais dos quatro andares, 2,42 Ω (151 dias), dominada pelo andar 1.
- **Ele persiste no silêncio** (154–158 dias): quando a v0 para de olhar, o ritmo fica.
- **Ele aparece igual no mundo sem estações** (150–156 dias).

É auto-organização no sentido estrito: um ritmo comum que nenhum andar tinha, que nasce do acoplamento e do aprendizado e se mantém sem o mundo. Mas não tem nada do mundo. Por isso o J4 passou sem dizer nada: o mundo real e o nulo dão o mesmo resultado, e em nenhum dos dois o ano foi aprendido (defeito 72).

**3. Por que: o erro era medido contra ela mesma.** A regra ω ← ω + η(Δφ − ω) compara o que o relógio esperava com o que ele próprio fez. Quando os relógios se puxam uns aos outros, cada um aprende a girar como o grupo, e o grupo gira na média deles. No teste 36, o erro era medido contra o mundo: o dia em que as águas de fato entraram menos o dia esperado. Ali a v0 aprendeu o mundo; aqui aprendeu a si mesma. É o mesmo padrão dos testes 38 e 39 na galáxia: uma regra sem referência externa encontra um ponto fixo próprio (lá, travar tudo; aqui, o consenso) e se fecha.

**4. A escada da v0 não sobrevive ao acoplamento.** Com b = 10, o andar 1 gira dez vezes mais rápido que o 2, e a frequência média de qualquer aglomerado que o inclua é praticamente a dele dividida por quatro. Acoplados, os andares lentos, que são a identidade da v0, perdem a lentidão e passam a girar a cada 151 dias. Acoplar os andares desmancha justamente o que os distingue.

**5. O que a galáxia ensinou e este teste confirmou de outro modo.** A coordenação depende da distribuição dos ritmos, mas há uma regra a mais: **o acoplamento mútuo conserva o ritmo médio**, e só uma força externa o desloca. Na galáxia, o aglomerado girava no ritmo dos anéis densos porque não havia força externa. Na v0, para o grupo girar com o ano, o ano tem de chegar a todos os membros com força suficiente, ou o aprendizado tem de medir o erro contra o mundo.

## O que isso sugere (não testado)

- O mesmo relógio com o erro medido contra o mundo: ω_j ← ω_j − η s_j sen φ_j, a regra dos osciladores de frequência adaptativa. Ela só muda ω pelo torque que o mundo exerce.
- Ou os relógios desacoplados entre si e acoplados só ao próprio registro. Cada andar então aprenderia o ritmo que lhe chega e guardaria a sua escala.

As duas são predições para um próximo teste, com a conta conferida numa simulação curta antes dos critérios.

## Para a lista de defeitos de desenho

71. A teoria fixou o referencial na frequência da forçante e testou o travamento andar por andar. Isso ignora que o acoplamento mútuo conserva a frequência média do aglomerado (a soma das equações de fase), e o solver do teste 46 a resolvia. A conta prévia não foi conferida com uma simulação curta, que teria mostrado o andar 2 saindo do ano já em K = 0,02.
72. O nulo do J4 só distingue "ano vindo do mundo" de "ano vindo da arquitetura". Não previu a terceira possibilidade, que foi a que ocorreu: nenhum ano, um ritmo de consenso igual nos dois mundos. O J4 deveria ter sido condicionado ao J2.

Placar: 51 testes numerados (o 25 sem resultado), mais o teste do ato A. 51: J1, J2, J3 reprovaram; J4 passou pela letra, sem valor. 72 defeitos nesta numeração, 1 emenda.
