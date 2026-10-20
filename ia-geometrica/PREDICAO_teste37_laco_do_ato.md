# Predição do teste 37 (o laço do ato, teste A: a organização aprende com a consequência do que faz)

20/10/2026 · escrita antes de rodar nas sementes do teste (1000–1099) · desenho: DESENHO_laco_do_ato.md (dca9879) · parâmetros: PREDICAO_teste37_parametros.json · Ana Rigel

## De onde vem

O teste 36 deu à v0 o primeiro laço de erro: o relógio μ, que aprende com o erro de **previsão**, um evento por ano. O 36b mostrou que esse relógio prevê com menos viés que o calendário, mas com ganho pequeno, porque um evento por ano é pouco. Este teste é o teste A do desenho do laço do ato: a organização ⋄ aprende com o erro da **decisão**, o custo do que fez, no mundo sítio de cheias. Nesse mundo a cheia vem quer a placa aja, quer não, então depois de cada consequência ela sabe o que cada marca teria custado.

## O órgão (instrumento teste37.py)

- **Leitura (sem mudança):** a régua da v0 dos testes 27–28, calibrada nos anos 1–2: surpresa da chuva z_c (pluviômetro) e vinco do córrego z_v.
- **Marcas:** 36 regras "agir se z_c ≥ θc ou z_v ≥ θv", com θc ∈ {1, 2, 3, 4, 6, ∞} e θv ∈ {0,5, 1, 2, 3, 4, ∞}. A marca (∞, ∞) é "nunca agir".
- **Memória do órgão:** para cada marca, o custo que ela teria pago (C por chamada no instante da chamada; D por cheia sem proteção no instante da cheia), descontado com meia-vida **h = 1 ano**. São 36 números.
- **Decisão:** em cada hora, o órgão age pela marca de menor custo descontado até a hora anterior. Na partida, todas valem zero, e o desempate vai para a marca do meio da grade. Ninguém afina o órgão de fora.

Isso difere do esboço do desenho em três pontos, decididos antes desta predição: 36 marcas em vez de 8, porque são duas leituras; nenhum buffer, porque o custo de cada marca se conhece no instante em que acontece; e o controle D trocado (ver a fumaça).

## O mundo

`sitio.py` sem mudança, 8 anos por mundo, passo de 1 hora, D = 100, proteção P = 48 h. Sementes 1000–1099.

## A fumaça (sementes de desenho 5000–5009, antes desta predição; a saída está no commit)

- **Regime pela regra do desenho** (a melhor marca fixa em retrospecto ≥ 20 % abaixo de "nunca" e de "a cada chuva"), nos anos 3–8:

| regime | nunca | a cada chuva | melhor marca fixa | passa a regra |
|---|---|---|---|---|
| L 1 h, C 10 | 54.200 | 35.340 | 18.310 (2, ∞) | **sim** (−66 %, −48 %) |
| L 3 h, C 10 | 54.200 | — | 36.420 | não (−14 % da mais nervosa) |
| L 1 h, C 3 | 54.200 | 12.772 | 7.026 | sim |
| L 3 h, C 3 | 54.200 | — | 19.687 | não (−2 % da mais nervosa) |

  **Escolhido: L = 1 h, C = 10.** É o mesmo custo de chamar dos testes 26–27 e o regime em que mais se perde errando a marca. Há ≈ 8,9 cheias por ano.

- **Mudança:** "o córrego assoreia" (a cheia passa a ser a 1,0 m do 5º ano em diante). A melhor marca muda de (2, ∞) para (1, ∞), e a antiga custa 17 % a mais nos anos 6–8. "O ato encarece" (C × 2) muda de forma parecida (+18 %); escolhi o assoreamento porque é uma mudança do mundo, não do preço.
- **h:** na condição com mudança, o órgão com h ∈ {0,25; 0,5; 1; 2; 4} anos custou 17.300 / 16.550 / **16.280** / 16.420 / 17.040 nos anos 6–8. **h = 1 ano.**
- **Controle:** o controle do esboço (consequências de outro mundo) não é controle. Um sítio igual que também assoreou ensina quase o mesmo (ganho sobre a afinada de 36 %, contra 44 % com as próprias consequências). O controle julgado passa a ser **D, sem a mudança**: o órgão age no mundo que assoreou, mas recebe as consequências do mesmo mundo sem o assoreamento. Comparar B com D usa os mesmos sorteios e não diverge (lição do defeito 50). O "outro sítio" fica como E, relatado.
- **Valores nas sementes de desenho** (vistos, não julgados): razão órgão / melhor fixa nos anos 2–8 de 1,03 a 1,20 (6 de 10 ≤ 1,10); ganho sobre a afinada nos anos 6–8: C 6,6 %, B 44,3 %, D 15,6 %, E 36,4 %.

## Condições (100 mundos cada, as mesmas sementes)

| | mundo onde age | consequências com que aprende |
|---|---|---|
| **C** | constante (cheia a 1,2 m nos 8 anos) | as próprias |
| **B** | assoreia no 5º ano | as próprias |
| **D** (controle) | assoreia no 5º ano | as do mesmo mundo sem assorear |
| E (relatado) | assoreia no 5º ano | as de outro sítio igual que também assoreou |

**Afinada:** a marca de menor custo nos anos 1–2 do próprio mundo, fixada daí em diante. É o jeito dos testes 26–28 e o adversário justo, porque usa os mesmos dados sem continuar aprendendo.

## Critérios

**J1, aprende (C):** custo do órgão nos anos 2–8 ≤ **1,10 ×** o da melhor marca fixa em retrospecto nos mesmos anos, em **≥ 80 de 100** mundos.

**J2, readapta (B):** nos anos 6–8, o ganho total do órgão sobre a afinada é **≥ 10 %**, é **≥ 10 pontos** maior que o ganho em C nos mesmos anos (para não contar como readaptação o que é só o defeito de afinar com 2 anos), e o órgão fica ≥ 10 % abaixo da afinada em **≥ 60 de 100**.

**J3, não perde de quem não aprende (C):** custo total do órgão nos anos 3–8 ≤ **1,05 ×** o da afinada, e ≤ 1,05 × em **≥ 70 de 100**.

**J4, depende da consequência (D):** o ganho extra de D sobre C nos anos 6–8 é **≤ metade** do ganho extra de B sobre C, e o órgão de B é mais barato que o de D em **≥ 70 de 100**.

Relatado: E (aprender com outro sítio); custos por ano de cada condição; a melhor marca fixa e "nunca" nos anos 6–8 de B; a marca escolhida por ano.

## Conta prévia

Há ≈ 8,9 cheias por ano e dezenas de chamadas por marca nervosa. Com h = 1 ano, a memória do órgão guarda ≈ 13 cheias de peso efetivo. Depois do assoreamento, as cheias passam a ser mais numerosas, e as marcas que perdem as novas cheias acumulam ≈ 100 por perda. Em meio ano a diferença entre a marca antiga e a nova deve passar o custo acumulado de antes. O relógio do 36 precisava de 3–4 eventos, que ali eram 3–4 anos; aqui são semanas a meses. No mundo constante, o órgão troca de marca às vezes pelo ruído, e cada troca custa. Por isso ele não deve encostar na melhor marca em retrospecto em todos os mundos, e o J1 é o critério mais duro.

## Apostas (Claude, antes de rodar)

- **J1 passa: 30 %.** Nas sementes de desenho, só 6 de 10 ficaram ≤ 1,10.
- **J2 passa: 85 %.**
- **J3 passa: 85 %.**
- **J4 passa: 75 %.** No desenho, D ganhou 9 pontos sobre C, e B 38.
- **E fica mais perto de B que de D: 80 %.**

## O que fecha

- **J2, J3 e J4 passam:** a organização aprende com o erro do ato, readapta quando o mundo muda, não perde de quem foi afinado e não aprende sem a consequência certa. É o primeiro laço da v0 em que aprender **vale mais** que uma regra afinada. O teste B (o ato que esconde a consequência) fica autorizado pelo desenho.
- **J2 reprova:** com consequência visível e ≈ 9 cheias por ano, a placa ainda não readapta melhor que uma regra afinada uma vez. Antes do teste B, a pergunta volta para o órgão (h, marcas).
- **J4 reprova:** o órgão ganha por outra razão que não a consequência do mundo dele, e a leitura precisa achar qual.
- **J1** sozinho não fecha nada: mede o preço de trocar de marca num mundo que não muda.
