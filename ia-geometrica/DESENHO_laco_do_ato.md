# Desenho: o laço do ato (a organização ⋄ aprende com a consequência do que fez)

20/10/2026 · desenho, não predição · nada aqui foi rodado · Ana Rigel (proposta de Claude, sessão "IA geométrica: diferença v0 × OBS-01")

## De onde vem

Na conversa de 20/10 sobre "a IA geométrica não aprende?", separamos três coisas: memória (guardar), calibração (saber o que é normal) e aprender com a consequência (errar, perceber e mudar a forma de responder). Os testes 32 e 33 deram à organização ⋄ a calibração do ano. O teste 36, feito em outra sessão, deu à v0 o primeiro laço de erro: o relógio μ, que aprende com o **erro de previsão** de um evento do mundo (a entrada das águas, um por ano).

Este desenho cobre o que ainda falta: aprender com o **erro do ato**. É o caso em que o que se paga depende do que a própria v0 decidiu fazer. Há três diferenças em relação ao teste 36:

| | relógio do teste 36 | laço do ato |
|---|---|---|
| o que erra | a previsão de quando o mundo muda | a decisão de agir ou não |
| o erro | o − μ (dias) | o custo pago menos o custo da melhor decisão possível (arrependimento) |
| frequência | 1 evento por ano | dezenas por ano (≈ 76 chuvas/ano no mundo sítio) |
| o que esconde | nada: a entrada acontece de qualquer jeito | quando o ato muda o mundo, a v0 não vê o que teria acontecido sem ele |

## Princípio (o que os testes 32, 33 e 36 já ensinaram)

1. **A régua não aprende.** Ela é o instrumento: fica fixa, para continuar auditável e servir ao OBS-01. O que aprende são as **marcas de decisão** postas sobre a régua: em que leitura agir.
2. **Aprender o normal é perigoso; aprender a consequência é seguro.** O normal é uma escolha de referência: no teste 32 a placa aprendeu a seca como normal. A consequência não é escolha: é o que de fato custou. O laço do ato aprende só com ela.
3. **A organização é o corpo que age.** O campo ∘ observa, a memória □ lembra, a organização ⋄ decide e responde pelo que decidiu.

## O órgão

- **Leitura:** a mesma da v0 nos testes 27–28, com os andares e a régua sem mudança. É um escore s_t na régua (surpresa da chuva e vinco do córrego), já calculado hoje.
- **Marcas candidatas:** K = 8 limiares θ₁ < … < θ₈ na régua. Cada marca define uma regra: agir quando s_t ≥ θ_k.
- **Memória do órgão:** para cada marca, o custo acumulado que ela **teria** pago, com esquecimento de meia-vida h. São 8 números, mais um buffer das últimas L + P horas de decisões pendentes, porque a consequência só se conhece depois. No total, menos de 100 números: cabe na placa.
- **Decisão:** a placa age pela marca de menor custo acumulado (no empate, a do meio).
- **Erro:** ao fim de cada janela de consequência, o órgão soma a cada marca o custo que ela teria pago naquela janela. O erro da placa é o custo que ela pagou menos o da melhor marca. É isso que move a escolha.

## Teste A: o ato com consequência visível (o mundo sítio de cheias)

No sítio dos testes 26–28, a cheia acontece quer a placa aja, quer não. Só a perda depende do ato. Então, depois de cada janela, o órgão sabe o que **cada** marca teria custado, inclusive as que não usou. É aprendizado com informação completa, o caso fácil, e deve vir primeiro.

**Escolha do regime antes da predição (fumaça do mundo, sementes de desenho 5000–5009):** escolher (L, C) no mapa do teste 28 onde a melhor marca fixa, escolhida olhando para trás, fique ≥ 20 % abaixo tanto de "nunca" quanto de "a cada chuva". Onde "a cada chuva" já resolve (ato barato), não há o que aprender. Onde nada se paga (ato caro e lento, teste 27), também não.

**Condições (100 mundos cada), copiando as quatro assinaturas do teste 36:**

| condição | o que acontece | assinatura |
|---|---|---|
| A, começo errado | o órgão começa pela marca mais nervosa | aprende: o custo anual chega perto do da melhor marca fixa |
| B, o mundo muda | no 5º ano o córrego assoreia (cheia crítica de 1,2 m para 1,0 m) ou o ato encarece (C dobra) | readapta: a marca anda para a nova melhor; uma marca afinada de fora nos anos 1–2 (o jeito dos testes 26–28) fica para trás |
| C, nada muda | mesmo mundo do começo ao fim | não aprende ruído: a marca não deriva e o custo não fica pior que o da afinada |
| D, consequência trocada | o órgão recebe as consequências de outro mundo da mesma condição B | depende do erro: sem a consequência certa, não readapta. Controle estável, comparado com e sem mudança nos mesmos sorteios (lição do defeito 50) |

**Julgamentos a fixar na predição (esboço):**
- J1 (A): custo do 3º ano ≤ 1,10 × o da melhor marca fixa em hindsight, em ≥ 80 de 100.
- J2 (B): custo dos anos 6–8 do órgão ≥ 10 % abaixo do da marca afinada nos anos 1–2, em ≥ 60 de 100. **Este é o julgamento que importa:** é o único lugar em que aprender pode bater uma regra bem afinada, porque a regra foi afinada num mundo que deixou de existir.
- J3 (C): custo ≤ 1,05 × o da afinada, e marca final dentro de ±1 posição da inicial ótima, em ≥ 90 de 100.
- J4 (D): readaptação de D ≤ metade da de B, comparando com e sem mudança nos mesmos sorteios.

**Conta prévia a fazer antes da predição:** quantas janelas de consequência por ano existem no regime escolhido, e qual a meia-vida h que deixa o arrependimento cair à metade em ≤ 2 anos depois da mudança. Com ≈ 76 chuvas/ano, o laço deve ser 10–50 vezes mais rápido que o relógio do teste 36.

## Teste B: o ato que esconde a consequência (depois do A, só se o A passar)

Aqui está o problema verdadeiro de quem age. Mundo **irrigação**, sobre o solo dos dados reais de MT: quando o solo seca, a placa pode irrigar (custo C em água). Se a planta fica X dias abaixo do ponto de murcha, perde D. **Se a placa irriga, ela nunca vê se a chuva teria chegado a tempo.** O próprio ato apaga o contrafactual.

A previsão é que um órgão que aprende só com o que pagou caia numa **superstição**: irriga sempre, porque toda vez que irrigou a planta viveu, e nunca vê que a chuva a teria salvado. É uma cegueira criada pelo ato, um parente direto da cegueira do Paper A. O registro não vê a banda que a própria rigidez apaga; a organização não vê o mundo que o próprio ato substitui.

**O que o teste B mede:**
- **A cegueira do ato, declarada:** a fração das decisões cujo contrafactual ficou sem ser visto. A régua pode declarar isso como declara a cegueira dos andares (ponte com o OBS-01).
- **Três órgãos:** (i) informação completa, como se visse o contrafactual (teto, impossível na placa real); (ii) ingênuo, só com o que pagou; (iii) explorador, que de vez em quando não irriga num dia de risco baixo para ver o que acontece, a uma taxa ε fixada na predição.
- **Julgamentos a fixar:** J1, o ingênuo fica preso acima da melhor marca (superstição); J2, o explorador chega a ≤ 1,15 × o custo do de informação completa; J3, o custo de explorar (perdas nos dias em que não irrigou) é declarado e menor que o ganho.

## O que este desenho não é

- Não mexe nos λ, na régua nem no relógio μ do teste 36. Ele soma um segundo laço, em outro lugar da organização.
- Não reabre a política de olhar, que segue fechada: aqui se decide agir, não olhar.
- Não é mercado. Mas se o teste B mostrar a superstição e a saída pela exploração, essa é exatamente a pergunta que o SGV nunca pôde fazer em produção: quanto do que ele aprende é consequência do que ele mesmo fez.

## Regras da casa

Um teste por vez, só quando a Ana pedir. Cada um com a sua predição escrita e commitada antes, critérios com números, nulo justo (a marca afinada de fora) e apostas de Claude. O teste A precisa da fumaça do regime antes da predição. O B só existe se o A passar.
