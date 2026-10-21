# Leitura do teste 54 (a sentinela sabe quando aprendeu?): J1 REPROVADO; J2 e J3 PASSARAM. Ela nunca declarou um ritmo que não existe, mas só teve certeza do ano a tempo em 3 dos 6 lugares; com as decisões dela, previu as águas dentro da margem do calendário local

**Predição:** PREDICAO_teste54_sabe_quando_aprendeu.md e sentinela.py (310e0c3), antes de rodar no dado real. **Instrumento:** teste54.py (720ef00). **Resultado:** resultados_teste54.json. **Diagnóstico depois do julgamento:** diagnostico_teste54_pos_julgamento.txt. Três julgamentos; sem emenda.

## Resultados

**Quando ela declarou** (mediana dos 20 inícios; a fração mostra quantos inícios declararam o andar 2 até o fim de 2025):

| lugar | andar 2 declara | ω₂/Ω na declaração | inícios que declararam | andares 1, 3, 4 | nulo sem estações | controle sem aprendizado |
|---|---|---|---|---|---|---|
| Juara | **13/06/2018** (8,5 anos) | 0,996 | 90 % | nunca | nenhum andar, nenhum início | declara em 5,8 anos |
| Sinop | **16/07/2018** (8,5 anos) | 0,997 | 75 % | nunca | nenhum andar, nenhum início | 4,6 anos |
| Cuiabá | não declara | (fim: 1,015) | 45 % | nunca | nenhum andar, nenhum início | 6,3 anos |
| Barra do Garças | **11/04/2018** (8,3 anos) | 1,012 | 90 % | nunca | nenhum andar, nenhum início | 4,9 anos |
| Alta Floresta | 11/12/2019 (9,9 anos) | 0,993 | 65 % | nunca | nenhum andar, nenhum início | 4,6 anos |
| Rondonópolis | não declara | (fim: 1,009) | 45 % | nunca | nenhum andar, nenhum início | 5,9 anos |

**As previsões das águas**, 2019–2025, 42 previsões (erro = entrada − previsão):

| braço | EAM | viés |
|---|---|---|
| **sentinela** (decisões dela) | **21,9** | +12,4 |
| C, calendário local escrito (36b) | 20,0 | +16,9 |
| V1, relógio v1 (36b) | 18,8 | +9,7 |
| calendário regional (um só para os seis lugares) | 21,2 | +16,9 |
| S do teste 53 (silêncio em 2018 escolhido por nós) | 21,2 | −6,2 |
| controle sem aprendizado | 194,3 | +48,1 |

| | resultado | critério | |
|---|---|---|---|
| **J1** o andar 2 declara antes de 1/9/2019, ω₂ a ≤ 5 % | 3 de 6 (Juara, Sinop, Barra do Garças) | ≥ 5 de 6 | **reprovado** |
| **J2** no mundo sem estações, nenhum andar declara | 6 de 6, e nenhum dos 120 inícios declarou | ≥ 5 de 6 | **passou** |
| **J3** EAM ≤ C + 3 | 21,9 contra 23,0 | | **passou** |

Piloto refeito dentro do instrumento, com sementes determinísticas: com ano, 100 % declaram em ≈ 4,6 anos; sem ano, 0 %, e 0 % com memória longa. A tabela da predição dava 5 % no "sem ano"; ela usou `hash()` como semente e não é reprodutível (defeito 76).

Apostas: J1 (50 %) errada; J2 (65 %) certa; J3 (40 %) errada; os três juntos (15 %), certa a falha; o controle declara em ≥ 5/6 (55 %), certa (6/6).

## O que o resultado diz

**1. Ela não inventou ritmo nenhum.** No mundo sem estações, com as secas, os anos anômalos e as oscilações reais que o sintético não tinha, nenhum dos 120 inícios (6 lugares × 20) declarou ritmo em nenhum andar, em 16 anos. No mundo real, o andar 1 também nunca declarou. A régua sequencial, calibrada só no sintético, sobreviveu ao dado real. É a parte que um filtro e um registrador de datas não têm: **dizer "aqui não há ritmo" e estar certa.**

**2. Quando declarou, o que tinha aprendido era o ano.** Nos quatro lugares que declararam, ω₂ estava a 0,3–1,2 % de Ω no dia da declaração. Ninguém escreveu o ano nela.

**3. Ela é lenta e, onde o ano é difícil, não chega a ter certeza.** Ela levou 8,3–9,9 anos para declarar, contra 4,6 no piloto (o piloto do 52 também subestimou: 2–4 anos contra 6–7). Em Cuiabá e Rondonópolis, os lugares onde o teste 53 viu a fase escorregar ≈ 100 dias em anos isolados, só 45 % dos inícios declararam: a maioria ainda não tinha certeza em 2025, embora ω₂ estivesse a 0,9–1,5 % do ano. A régua exige que a fase fique presa ao ano durante um ano inteiro, e nesses lugares os anos anômalos a soltam. **Para uma placa, dez anos para aprender o ano é tempo demais.** O J1 diz isso com número.

**4. Com as decisões dela, a previsão ficou na margem.** 21,9 contra 20,0 do calendário local, que exige 8 anos de histórico escritos à mão, e o mesmo que o S do teste 53 (21,2), onde quem escolheu o silêncio fomos nós. Ela não supera o calendário, o v1 nem o calendário regional. **Nota:** o calendário regional (21,2) quase empata com o local, porque as entradas dos seis lugares são parecidas. "Aprender o lugar" vale pouco onde os lugares não diferem.

**5. O controle mostra um defeito da declaração.** Sem aprender (ω fixo em 419 d), o relógio do andar 2 também declarou, e **mais cedo** (4,6–6,3 anos), porque com A₂ ≈ 0,85 ele trava no ano por arrasto de fase mesmo com a frequência errada. Depois parou de ouvir, girou a 419 dias e errou as águas por 194 dias em média. A declaração detecta "estou preso a um ritmo", não "guardei o período desse ritmo". Na sentinela que aprende, as duas coisas coincidiram (ω₂ a ≤ 1,2 %), mas a régua não sabe disso. A correção natural é exigir também que a frequência guardada seja a ouvida: ω_j ≈ a taxa média de φ_j na janela (defeito 75).

## Diagnóstico depois do julgamento (não conta para o veredito)

Pergunta: a declaração de cada início separa as previsões confiáveis das outras? Uma previsão conta como "já tinha declarado" se o início declarou antes de 1/09 daquele ano.

| | n (início × ano) | EAM | mediana |
|---|---|---|---|
| já tinha declarado | 540 | **23,9** | 20,2 |
| ainda ouvindo | 300 | 230,2 | 55,4 |

Nos seis lugares, a mesma direção (Cuiabá: 31,9 contra 658,5; Juara: 22,7 contra 26,6). Isso é coerente com o teste 53, onde a fase que ouve o campo erra muito. Mas também quer dizer que o "ainda não sei" dela coincide com o "não confie em mim". Ressalvas: os 20 inícios dividem os mesmos dados, então as 840 previsões não são independentes, e esta divisão foi escolhida depois de ver o resultado. Fica como candidata a teste com predição própria: **uma sentinela que se abstém antes de declarar erra menos nas previsões que faz?**

## O que fecha

- **A honestidade da declaração está de pé** no dado real, no mundo sem estações e nos andares que não ouvem o ano (J2). É a primeira propriedade da v0 que passa no dado real e que nenhum dos concorrentes triviais tem.
- **A velocidade não está** (J1). Ela leva 8–10 anos para ter certeza do ano e, onde o ano é irregular, não chega lá. Como sentinela de um sítio, isso a desqualifica para ritmos anuais. Pode servir para ritmos curtos (dias, semanas), onde 3 janelas cabem em meses. Isso é outro teste.
- **A previsão com as decisões dela empata com a nossa** (J3, e S do 53), mas não supera nenhum calendário.
- **A declaração precisa de uma segunda condição** (defeito 75) para não confundir arrasto de fase com aprendizado.

## Para a lista de defeitos de desenho

75. A declaração do andar mede o travamento da fase (Q) e a estabilidade de ω, mas não compara ω com a frequência realmente ouvida. Um relógio arrastado pelo ano com ω errado (o controle, a 419 d) declara com confiança e depois, no silêncio, deriva ≈ 47 dias por ano. Correção candidata: exigir |ω_j − ⟨dφ_j/dt⟩_janela| ≤ 5 %.
76. O piloto da predição usou `hash(nome)` de Python como semente, que muda a cada processo. A tabela não é reprodutível bit a bit. O instrumento usa `zlib.crc32` e relata o piloto refeito (sem ano: 0 % contra os 5 % da tabela).
77. O piloto sintético subestimou de novo o tempo de aprender (4,6 contra 8,3–9,9 anos; no 52, 2–4 contra 6–7). O ruído AR(1) não tem os anos que soltam a fase (53), que são o que atrasa a trava real. A conta prévia leu o 52 corretamente (7–10 anos) e mesmo assim apostou 50 % no J1. A informação estava lá.

Placar: 54 testes numerados (o 25 sem resultado), mais o teste do ato A. 54: J2 e J3 passaram, J1 reprovou. 77 defeitos nesta numeração, 1 emenda.
