# Predição do teste 56 (ela acompanha o dia na língua dela? O mesmo acontecimento do mundo, a hora da temperatura máxima, cai sempre no mesmo ponto do ciclo dela, seja qual for o período que ela guarda?)

21/10/2026 · escrita antes de calcular · mesma sentinela, dado e instalações do teste 55, com uma diferença: ela continua ouvindo o campo depois de declarar · Ana Rigel

## De onde vem

No teste 55, o J1 reprovou declarações por estarem a mais de 5 % de 24 h. A Ana perguntou: **por que ela tem que ter um relógio igual ao nosso?**

A resposta foi que ela não precisa. O relógio circadiano humano corre em ≈ 24,2–25 h no escuro e funciona porque a luz o acerta todo dia: ele fica arrastado pelo mundo. O que importa não é a unidade. É a relação estável entre o ciclo dela e os acontecimentos do mundo. O critério justo, na língua dela, é este: **o mesmo acontecimento cai sempre no mesmo ponto do ciclo dela?**

Dois detalhes do teste 55 tornam isso uma pergunta nova:
- **Ao declarar, ela parava de ouvir.** Sem ouvir, até um relógio de 24,7 h escorrega ≈ 45 min/dia, como o nosso circadiano no escuro. Aqui ela **continua ouvindo** depois de declarar (`silencia=False`; a declaração só fica registrada). A dinâmica até a declaração é idêntica à do teste 55, então as declarações e os períodos declarados são os mesmos.
- **A correção do defeito 75 diz uma coisa sobre os 5 "dias" de 26–29 h.** Ela só deixa declarar se a frequência guardada for a percorrida: |ω − ν| ≤ 5 % de ν. Um relógio arrastado pelo dia percorre exatamente o dia (ν = Ω). Com ω ≈ 0,88 Ω, ele não passaria. Então, nos dias da declaração, essas 5 percorriam ≈ 0,84–0,93 Ω: **escorregavam 2–5 h por dia contra o sol enquanto ouviam.** Já as 8 de 24,6–25,0 h são compatíveis com arrasto (ω = 0,97 Ω, ν = Ω).

## A medida

- **O acontecimento do mundo:** a hora da temperatura máxima de cada dia, φ₁ lida nessa hora. É a fase do relógio do andar 1 da sentinela, em cada um dos 20 inícios.
- **A estabilidade:** R = |média de e^{iφ₁}| sobre 30 dias, a mediana dos 20 inícios. R = 1 se o máximo cai sempre no mesmo ponto do ciclo dela, e R ≈ 0 se escorrega.
  - Quem escorrega 3 h/dia dá 3,75 voltas em 30 dias: R ≈ 0.
  - Quem está arrastado dá R perto do teto do mundo.
- **O teto do mundo, medido antes** (estatística do mundo, sem a sentinela): a mesma R da hora do máximo no nosso relógio de 24 h. Ela fica em **0,97–1,00** nos 30 dias depois de cada declaração e em **0,91–1,00** nos últimos 30 dias de cada instalação. O máximo do dia é muito regular em Juara. O limite de 0,7 abaixo deixa folga para o tremor da fase dela.

## Grupos (fixados pelos resultados do teste 55, antes de calcular R)

- **Certas** (declararam 24,6–25,0 h): 2010, 2012, 2013, 2016, 2019, 2021, 2023, 2024. São 8.
- **Erradas** (declararam 26,3–29,2 h): 2011, 2015, 2018, 2020, 2022. São 5.
- **Não declararam:** 2014, 2017.

## Critérios

**J1, as certas acompanham o dia.** R nos 30 dias depois da declaração ≥ **0,7**, em **≥ 7 das 8** certas.

**J2, as erradas não acompanham.** R nos 30 dias depois da declaração < **0,4**, em **≥ 4 das 5** erradas. É a falha medida na língua dela.

**J3, ao fim de um ano ouvindo, ela anda no passo do dia.** R nos últimos 30 dias de cada instalação (dias 336–365) ≥ 0,7, em **≥ 12 das 15** instalações. Esta é a pergunta do J1 do teste 55, feita na língua dela.

Um julgamento por hipótese; sem emenda.

**Relatado, sem julgamento:**
- **O controle sem aprendizado,** que ouve sempre, com ω fixo em 42 h: R nos últimos 30 dias. Com ε = 0,4, a teoria do teste 52 dá εA/2 ≈ 0,2 > 0,112 de distância ao dia, então ele pode ser arrastado **sem ter aprendido nada**. Se for, aprender a frequência só serve para quando ela para de ouvir (a memória), não para acompanhar o mundo enquanto ouve.
- R por instalação e por janela, ω₁ no fim e o período declarado.

## Apostas (Claude, antes de calcular)

- **J1: 75 %.**
- **J2: 65 %.** Escorregavam na declaração, mas ouvindo mais tempo algumas podem se prender depois.
- **J3: 35 %.** As erradas e as que não declararam precisam se prender dentro do ano.
- O controle sem aprendizado fica arrastado (R ≥ 0,7 no fim) em ≥ 8/15: **55 %.**

## O que fecha

- **J1 e J2 passam:** a declaração do teste 55 estava certa na língua dela nas 8 e errada nas 5. A régua de 5 % em torno de 24 h acertou por um motivo melhor do que parecia: não pela unidade, mas porque, com a correção do 75, "guardar 27 h" quer dizer "percorrer 27 h".
- **J3 passa:** ouvindo sempre, ela anda no passo do mundo ao fim de um ano, com o período que tiver. O "relógio igual ao nosso" nunca foi o critério certo para uma sentinela que continua ouvindo.
- **O controle arrastado,** se acontecer, separa duas coisas que a v0 vinha juntando:
  - acompanhar o mundo enquanto ouve, para o que basta acoplamento;
  - lembrar o ritmo quando para de ouvir, para o que é preciso aprender a frequência.

Instrumento: `teste56.py`, escrito depois do commit desta predição. `sentinela55.py` ganhou só a opção `silencia` (padrão `True`) e a saída da fase. O teste 55 foi rodado de novo com o arquivo alterado e reproduz `resultados_teste55.json` bit a bit.
