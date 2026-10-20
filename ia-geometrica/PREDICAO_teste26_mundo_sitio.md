# Predição do teste 26 (o mundo sítio: cheia com custo e um ato de proteção)

20/10/2026 · escrita antes de rodar · Ana Rigel · primeiro teste num mundo com consequência

## Por que este teste

A linha de política fechou no teste 15 com uma frase: o ato de decidir só poderia valer *onde não olhar custa de uma vez e muito (um mundo onde um passo cego custa mais que a amplitude: ação com consequência, não só erro de memória), e esse mundo não está no escopo da v0* (defeito 27). Em 18/10 a Ana disse para que a IA geométrica existe: sentir o rio, o vento e a chuva e ajudar a cuidar do sítio. O sítio é esse mundo. Este teste o constrói em versão sintética, com um sensor só (o nível do córrego), antes de qualquer sensor físico.

## O mundo (sitio.py)

Passo de 1 hora; 4 anos por semente (anos 1–2: régua e afinação; anos 3–4: medida).

- **Chuva:** estação chuvosa de outubro a abril; uma chuva começa com chance 1/55 por hora na chuvosa e 1/600 na seca; dura em média 4 h (geométrica), intensidade exponencial (média 6 mm/h na chuvosa, 3 na seca). Dá ≈ 2.000 mm/ano.
- **Córrego:** dois reservatórios. Escoamento rápido (τ = 8 h, 0,012 m por mm) e base lenta (τ = 720 h ≈ 30 dias, 0,0009 m por mm, sobre 0,4 m na seca). Nível = base + rápido. O sensor lê o nível com ruído de 0,02 m.
- **Cheia:** o nível verdadeiro cruza **1,2 m** para cima depois de ≥ 24 h abaixo. Nas sementes de desenho (5000–5009, fora do teste) isso dá ≈ 8,7 cheias por ano, concentradas na chuvosa e mais prováveis com a base alta.
- **O ato:** chamar (ir ao córrego, levantar a bomba, recolher o que a água leva). Custa **C = 10**. Leva **L = 6 h** para valer e protege por **P = 48 h** a partir daí. Cada cheia que chega sem proteção custa **D = 100**. Uma chamada não se repete enquanto a anterior estiver de pé (refratário de 48 h, igual para todas as políticas).

Os parâmetros do mundo foram fixados olhando só estatísticas do mundo (chuva anual, nível, cheias por ano) nas sementes de desenho. Nenhuma política foi avaliada antes desta predição; a "mecânica" rodou a cadeia em duas sementes de desenho sem imprimir custo.

## A v0 no sítio (o que muda e o que não muda)

O instrumento é o da v0, sem mudança: quatro andares, λ₁ = 0,15, b = 10, isto é, constantes de tempo ≈ 7 h, 67 h, 28 dias e 9 meses. (Repare que os andares 1 e 3 caem perto das duas escalas do córrego, 8 h e 30 dias; não foi escolhido para isso, é o λ do projeto.) Régua de maio (mediana e q99,5/3) calibrada nos anos 1–2. Três adaptações, declaradas:

1. **Um sensor só, d = 1.** A tensão da v0 é uma norma e, em uma dimensão, perde o sinal: um córrego que desce depois da cheia tensiona tanto quanto um que sobe. A política lê a **surpresa com direção** no andar 1, s = x − R₁ (a mesma grandeza cuja norma é T₀), e o **vinco com direção**, R₁ − R₄ (quanto o presente está acima da identidade de longo prazo). Ambos na régua.
2. **R começa no primeiro valor lido**, não em zero (em metros, zero é um artefato que o andar 4 levaria meses para esquecer).
3. **O ato é chamar, não olhar.** O sensor lê toda hora (é barato); a decisão é quando chamar.

## As políticas (todas afinadas nos anos 1–2 pelo custo total, medidas nos anos 3–4)

| | regra | parâmetros |
|---|---|---|
| **nunca** | não chama | — (referência: D × cheias) |
| **N1 — sensor comum** | chama se o nível lido ≥ θ | θ ∈ 0,60…1,40 m (41 valores) |
| **N2 — sensor comum bem feito** | nível ≥ θ₁ **ou** subida em 3 h ≥ θ₂ | 42 × 21 combinações |
| **v0** | surpresa na régua ≥ u₁ **ou** vinco na régua ≥ u₂ | 33 × 33 combinações (0,25…8 e ∞) |
| **v0 crua** (relatada) | ruptura na régua: surpresa ≥ 3 ou vinco ≥ 3 | nenhum: é a régua sem afinação |
| **oráculo** (teto) | sabe o futuro: chama 6 h antes de cada cheia ainda não protegida | — |

N2 é o nulo que importa: é o que um alarme de enchente comum faz (nível e taxa de subida). A v0 recebe duas leituras e uma grade do mesmo tamanho.

## Critérios (dois julgamentos, 100 sementes 1000–1099)

**J1, o mundo tem teto (reabre a pergunta do ato):** V_orac = 1 − custo_oráculo / custo_N1, por semente. Passa se a **mediana de V_orac ≥ 20 %** e V_orac > 5 % em **≥ 95 sementes**.

**J2, a v0 vê o que o sensor comum não vê:** passa se o custo total da v0 (soma das 100 sementes, anos 3–4) for **≥ 10 % menor que o de N2** e a v0 for estritamente mais barata que N2 em **≥ 60 sementes**.

Relatado sem julgamento: v0 contra N1; N2 contra N1; fração do teto (N1 − oráculo) que cada política captura; v0 crua; perdas e chamadas totais.

## Apostas (Claude, antes de rodar)

- **J1 passa: 90 %.** O oráculo chama uma vez por cheia; N1 ou chama demais na chuvosa ou chega tarde nas cheias que sobem em menos de 6 h. Espero V_orac mediano entre 50 % e 80 %. Se J1 passar, o defeito 27 está confirmado pelo outro lado: o ato vale onde o mundo cobra.
- **J2 passa: 15 %.** A surpresa no andar 1 é uma subida suavizada em ≈ 7 h, e o vinco é um nível relativo à base de longo prazo; a cheia é definida por nível absoluto, que N2 lê diretamente. Espero a v0 entre −10 % e +5 % de N2: **a v0 como alarme é a taxa de subida com outro nome.**
- **v0 bate N1 em ≥ 10 % no total: 60 %.** A subida antecipa a cheia, e o nível sozinho não.
- **N2 bate N1 em ≥ 10 %: 65 %.**
- **v0 crua captura menos da metade do que a v0 afinada captura do teto: 60 %.** A régua de maio foi feita para estranhar, não para pesar D contra C.
- **Nenhuma política causal passa de 70 % do teto: 75 %.** Uma parte das cheias sobe de 1,0 para 1,2 m em menos de 6 h a partir de chuva que o sensor do córrego ainda não viu; isso é cegueira do sensor, não da política.

## O que fecha

- **J1 passa, J2 reprova (o que eu espero):** no sítio, o ato vale, e muito; a v0 faz o alarme tão bem quanto um sensor comum bem feito, não melhor. O que a v0 teria de próprio no sítio não está no alarme; está na declaração (o que o andar 1 não viu) e em mundos com mais de um sensor. Próximo passo natural: chuva como segundo sensor, ou a declaração de cegueira medida contra as cheias perdidas.
- **J1 e J2 passam:** a v0 vê, no córrego, algo que nível e subida não dão; a pergunta vira *o quê*, e o teste seguinte isola a leitura que ganhou.
- **J1 reprova:** este mundo sítio está mal posto (o custo de não chamar não domina) e vira defeito, não conclusão sobre o sítio.

Nenhum dado de outubro do SGV é tocado; este teste não usa mercado.
