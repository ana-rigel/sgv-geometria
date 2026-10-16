<!-- Exportado do Claude Doc 'SGV: a trajetória da pesquisa', rev 19, 16/10/2026. O diagrama dos pontos de virada é um widget e não exporta. -->

# SGV: a trajetória da pesquisa

Oct 16, 2026 · @Ana Rigel

## Em uma página

O SGV começou em meados de 2026 como um sistema de trading em BTCUSDT a 1 minuto, com uma hipótese fundadora: o mercado é um campo informacional, e entender a geometria dos estados revelaria a direção do preço. Em outubro de 2026 ele é um programa de pesquisa em geometria da informação, com repositório versionado (`ana-rigel/sgv-geometria`), \~90 ramos de experimentos, pré-registros com julgamento único e nulas que separam mercado de artefato.

**O que ficou de pé.** O mercado pode ser traduzido num espaço de estados 3D com campo (deriva, agitação), cascas de densidade (HDR50/HDR95) e trajetória. Essa geometria é **real** (passa pelas nulas que destroem a estrutura do mercado) e **não é especial** (quase toda ela é a forma geométrica de fatos já conhecidos: memória curta, surtos de volatilidade, caudas pesadas). A conclusão da Ana em 15/10: é uma linguagem nova e válida para ver os mesmos fatos.

**O que caiu.** Direção não existe a 1–15 minutos, por nenhum caminho testado (sete tentativas independentes). Lucro no 1 minuto é inviável: borda \~0,01 % por trade contra custo de 0,04–0,20 %. A geodésica da métrica Hessiana não descreve o movimento. As formas das cascas, como previsoras, falharam em todos os testes.

**O que se descobriu sobre o espaço.** A dimensão escondida do cubo 3D é a volatilidade, em várias escalas (minutos, horas, dias). Ela age como um zoom: a borda do cubo é a camada quente, e medidas em unidades de volatilidade, as temperaturas colapsam no mesmo objeto. O campo é de difusão com saltos, não difusão pura.

**O que decide o próximo capítulo.** Quatro testes confirmatórios congelados julgam outubro/2026 em 3 de novembro: H-DIF-01, H-DIR-01, H-FORMA-D-01/02 e H-VOL-01. São os primeiros julgamentos num mês nunca visto por nenhuma exploração.

## Fase 1 (mai–set/2026): o sistema de trading e a exaustão honesta do 1 minuto

O SGV nasceu como motor de decisão: um estado do mercado lido por variáveis geométricas (σ torção, OIT curvatura, ψ emissão, η maturidade espectral, terreno TENSIONED/COHERENT/TRANSITION\_EDGE), um runner v5 na Binance Testnet e um motor de saídas (PSI\_EMITIDO, SIGMA\_COLAPSO, BE\_STOP, STOP\_LOSS). Entre junho e setembro foram 1.113 trades ao vivo, analisados sessão a sessão.

**O que a análise dos logs encontrou, em ordem.**

1. **Taxa de acerto alta, lucro nulo.** WR de 54–76 % conforme a sessão, mas payoff baixo e borda bruta de \~0,01 % por trade. O custo realista de ida e volta (0,04–0,20 %) torna o sistema negativo em qualquer cenário. Confirmado três vezes: 124 trades, 268 trades e 307 trades.
2. **A "célula de ouro" morreu fora da amostra.** O filtro η < 0,03 ∧ σ ≥ 0,70 tinha \~89 % de acerto na calibração e caiu para 47 % em 17 trades prospectivos. O mesmo aconteceu com IIT ≥ 0,30 (inverteu de 61 % para 49 %) e com os grupos de entrada por terreno, que trocaram de sinal entre a 1ª e a 2ª quinzena.
3. **Nada conhecido na entrada prevê o destino do trade.** 74 features na entrada: AUC fora da amostra ≤ 0,5, zero sobreviventes de FDR. O único "achado" de uma varredura era um vazamento (close\_chg era o 1º minuto de P&L do próprio trade), descoberto por uma pergunta da Ana: "em que momento close\_chg é conhecido?".
4. **A entrada do SGV é um detector de volatilidade, não de direção.** Trajetórias pós-entrada: retorno forward nulo em todos os horizontes, mas amplitude (MFE) elevada. E com controle pareado por volatilidade pré-entrada, até o excesso de amplitude some: o SGV entra quando a volatilidade já está 1,22× a mediana.
5. **O placebo.** Entradas aleatórias com a mesma mecânica de saída produzem o mesmo WR. O alfa real (+1,83 %) cai dentro da banda do placebo (p = 0,13). Com um mês, o SGV é indistinguível de entradas ao acaso.
6. **O julgamento da fila de 8 candidatos (02/09).** Pré-registrados com limiares congelados e apostas declaradas, julgados em 239 trades confirmatórios: zero sobreviventes de Benjamini-Hochberg. O programa exploratório do v5.3 foi encerrado "por exaustão honesta".

**O que sobrou de positivo.** Uma família de efeitos de amplitude estável entre quinzenas (σ, e≡j, s\_capote negativos; g\_t, iit, ψ positivos, ρ ≈ 0,05–0,08 contra Range T+5 sob controle rígido de volatilidade) e o bloco dinâmico Δ3 nas entradas reais. Virou a H-DYN3-AMP, congelada em 31/08 para julgamento em outubro. Magnitude: R² incremental de \~0,6 %. Real cientificamente, irrelevante economicamente.

**A assimetria de percepção.** O sistema enxerga os eventos dos quais lucra (PSI e SIGMA têm assinatura de campo clara) e é cego aos que lhe custam (STOP\_LOSS é só queda de preço, sem nenhuma assinatura). Esse achado de 01/09 descreve melhor que qualquer outro por que o SGV não podia funcionar como estava.

## Fase 2 (ago/2026): a auditoria, o portfólio operável e a hipótese fundadora

Em agosto a Ana pediu uma auditoria crítica independente do SGV, enviando código completo, documento de pesquisa e logs, com uma motivação declarada: renda extra modesta para reduzir de quatro empregos para cerca de dois. A auditoria separou o que era fenômeno do que era metáfora.

**O que a auditoria estabeleceu.**

| Alegação do SGV | O que os dados mostraram |
| --- | --- |
| Eventos de "vácuo/colapso" (OIT → 0) antecipam agrupamento de volatilidade | Real e replicável (p = 1,6 × 10⁻²⁸ em 45.860 velas), mas OIT → 0 é um **surto** de volatilidade (AUC 0,725), não uma "seca de atividade" como a narrativa toroidal dizia |
| Métricas contínuas (σ, iit, ψ, einstein) carregam informação | AUC 0,517 em validação cruzada: ruído. Excluídas de tudo o que veio depois |
| O cluster T2 amplifica o sinal | O único amplificador robusto (AUC 0,62 fora da amostra) |
| A topologia toroidal faz trabalho matemático | Não faz: o que opera é um Markov-switching com transições logísticas. O toro é narrativa |

**O portfólio operável.** O código foi reescrito do zero (`sgv_operavel v1.0`, 643 linhas no lugar de \~140 arquivos) e testado em 6,6 anos de dados reais, com portas pré-registradas e critérios de morte. A Sleeve B, que era o DNA do SGV (eventos de colapso), **reprovou** em BTC e ETH: Sharpe \~0, drawdowns de 40–57 %. Sobreviveram a tendência em ETH e o carry de funding: +17 %/ano histórico, expectativa forward honesta de 8–12 %/ano depois de documentar o decaimento do prêmio de funding (31 % em 2021 → \~2 % em 2026). O paper trading da Fase 2 segue em outra conversa.

**O ponto de virada ontológico.** Foi nesta fase que a hipótese fundadora ganhou o seu diagnóstico. Nas palavras da análise de setembro: o campo informacional que o SGV tentava mapear não é um campo sobre o qual os agentes se movem; é um campo **feito das previsões dos agentes sobre o próprio campo**. A geometria descrevia a sombra fielmente; o projetor é que se reconfigura ao ser observado. A hipótese não errou a matemática, errou a ontologia do objeto. E, por ironia, esse objeto (um sistema de registros autoconsistentes) é vizinho direto do Paper A e do TAR, que a Ana estuda em outro lugar.

**A regra que nasceu daqui.** Toda hipótese de trading passou a precisar responder, antes de entrar na fila: *quem está do outro lado e por que continua pagando?* Hipótese sem resposta boa é ineficiência com prazo de validade; com resposta boa é um equilíbrio (prêmio de risco, carry, provisão de liquidez), e equilíbrios não são arbitrados embora.

## Fase 3 (8–13/10/2026): geometria da informação como pesquisa própria

Em 8 de outubro a Ana reativou o projeto com outra pergunta. Em vez de "o SGV lucra?", ela quis testar a camada geométrica em si (tensores 3D, Ricci, Einstein, campo) sob a ótica de física da informação, e criou o repositório `ana-rigel/sgv-geometria`. Em 9/10 corrigiu o objetivo em uma frase que organizou tudo o que veio depois: **não é compreender a direção do mercado, é compreender o funcionamento do mercado pela geometria da informação.** E acrescentou: não quer que a ferramenta seja "especial".

**Primeiro: a camada legada não media nada.** A auditoria do código de abril mostrou que a métrica Hessiana do SGV era ruído numérico onde curva e trivialmente plana onde estável, que o motor nunca conseguia abrir posição por dois bugs independentes, e que o pipeline offline vazava futuro. Uma reescrita com derivadas analíticas exatas (validadas contra espaços planos e esferas) deu base sólida; a linha Fisher–Rao (ΔF contra substitutos GARCH) foi testada e **reprovou no portão de existência** em 1m e 1h, encerrada pela regra. O repositório `sgv_original` ganhou uma reimplementação dos 10 scripts com 65 testes de paridade, causalidade e geometria.

**Segundo: a geometria das superfícies (M8–M35).** A linha mais longa do programa, feita com o colaborador GPT e com Claude como executor:

| Etapa | O que resolveu |
| --- | --- |
| M8–M9 | Decompor a mudança entre duas superfícies de densidade em posição, tamanho, orientação e forma; registro rígido por ICP; ângulo indefinido para formas quase esféricas |
| M10–M11 | O **piso de amostragem**: duas malhas idênticas davam distância positiva só pelo sorteio de pontos (\~0,10, contra \~0,13 "reais"). Resolvido com distância exata ponto-triângulo: superfície contra si mesma = 10⁻¹⁷ |
| M11-I | Assinatura única G(A→B) = (Δc, log V, θ, R, D\_A, D\_B, ΔD); integrada ao painel |
| M12–M14 | Nulas temporais e calibração de alarmes com taxa de falso alarme conhecida |
| M15–M18 | Persistência e forma importam ambas; o que mais falta nos modelos simulados é **memória de longo alcance da atividade**; acoplamento dinâmico (DCC) não explica, memória longa explica |
| M17 | Markov de várias escalas reduz a lacuna (46 % → 30 %), envelhecimento e relógio não acrescentam; sobram \~30 % apontando para acoplamento que muda no tempo |
| M23–M30 | VAR+GARCH e HAR fecham parte da distância; sobram volatilidade multiescala e não estacionariedade. M26: resiliência de liquidez (83 de 83 origens) |
| Dicionário / M35 | \~1/3 das medidas geométricas não se reduz a escalas tradicionais, mas o M35 não achou a tradução; em um teste, o acoplamento tradicional foi mais confiável |

Como **previsor**, quase tudo falhou: H-DOM (dominância de lobo: 34,5 % de acerto, p 0,99), M19/H-RUP (alarme de ruptura, não apoiada em ago–set), M20 (direção escondida, portões sintéticos predominantemente negativos), M31 (ETH), M32 (SOL) e M33 (BNB) (forma e curvatura da casca não acrescentam ao HAR-X: skill −0,08 a +0,02 %, todos dentro do IC), M34 (a assinatura geométrica não supera o estado + memória). A exceção foi o **C01**: com holdout aberto uma única vez, os 12 descritores HDR melhoraram a classificação de transformações sintéticas (Δ +0,057 nats/par, IC \[+0,041; +0,075\]), aprovado só dentro do experimento predefinido. O primeiro portão do C02 (generalizar para famílias de caudas pesadas) foi **bloqueado** por falha do extrator em grade (volume do HDR variando até 246 % entre malhas), o que gerou a emenda C02.1 sem malha, julgada na Fase 4. Como **microscópio**, a linha mostrou onde os modelos clássicos erram, e apontou a memória como peça central desde o M16, antes de o campo confirmar isso; o M30 foi o primeiro nulo equivalente aos blocos reais de 8 h, e o dicionário geométrico resumiu a casca numa frase: ela expande quando o mercado esvazia (deslocamento explicado em 94 % pelo nível de atividade).

**Terceiro: as cascas e a leitura humana (U01–U03, C01–C02).** A pergunta mudou de "a máquina lê melhor?" (U2, W-HDR: não, o convencional é igual ou melhor) para "uma pessoa consegue ler a transformação olhando as cascas?" (U03, Lovable). No caminho: o **HDR50 sozinho confunde caudas com contração**; o envelope HDR95 separa as duas; e o gerador do U03 tinha um vazamento (B = T(A) com os mesmos pontos, curtose exatamente igual), documentado com correção. O C02.1, em dados sintéticos com famílias nunca vistas, deu o maior resultado positivo do programa: +0,62 nats por par, concentrado na família de caudas pesadas.

**Quarto: o Navegador SGV.** Em 13/10 a Ana definiu a visão: juntar campo/trajetória, superfície e régua RTT num único mapa 3D que ela possa ver acontecendo. O pacote foi montado nos dois espaços (fluxo e original), com as nulas ao lado de cada instrumento. Foi ele que deu a lista das perguntas em aberto que a Fase 4 respondeu.

## Fase 4 (13–16/10/2026): o campo informacional, do que sobreviveu ao que caiu

Em quatro dias, a pergunta "o campo informacional existe?" foi decomposta e respondida pedaço por pedaço, sempre com nulas e previsão registrada antes de rodar. A ordem importa, porque cada resultado mudou o seguinte.

**1. Medir o campo de verdade, em vez do campo da KDE.** A varredura das 188 métricas do `sgv_original` mostrou que nenhuma carrega informação forte sobre amplitude futura além da volatilidade (maior |ρ| = 0,08); a única família com conteúdo próprio era a densidade local no plano (E\_norm, jerk). A Ana mandou medir então o campo real: deriva μ(x), agitação D(x), persistência, potencial. A deriva deu praticamente zero em todo lugar. A agitação D(x) sobreviveu: carrega amplitude dos 5 minutos seguintes além dos controles fortes (−0,065 no fluxo, +0,046 no original), e sobreviveu também à volatilidade implícita (E-VOL-01). Virou o **H-DIF-01**, congelado em 13/10 para outubro.

**2. Direção e dinheiro, fechados.** Teste direcional de 1 a 15 min: nada. Fluxo de ordens com latência (E-FLX-01): real, mas 0,2 bp contra 20 bp de custo. A regra "fluxo como filtro" de outro colaborador (R1, R3): testada, não ajudou. O **H-DIR-01** foi registrado com expectativa de nulo, para que "não há direção" seja um resultado e não uma ausência.

**3. A armadilha das réguas.** A gaussianização por postos (M11-I, aplicada pelo `build_space.py`, não pelo `sgv_original`) apaga as caudas: curtose 11,4 → \~0, teto |4,23|. A régua de caudas da Ana (`cascas_btc.py`, orig\_raw) as preserva. Com ela, a agitação cresce **×10,6** do núcleo à faixa 5–10, contra ×2,3 na nula de permutação, e o estimador localmente linear com correção por ESS (ajustes 1 e 2 do OBS-01) é o único monotônico. Dois erros meus foram corrigidos em público: o +0,21 da faixa 3–5 era a mais favorável de cinco subamostras (corrigido para +0,06 a +0,12), e a tabela de quintis não estava residualizada.

**4. Dois testes em ativos nunca usados, os dois não confirmados.** H-CAUDA-01 (XRP, 2.143 janelas): a agitação dos extremos antecipa amplitude? ρ = +0,003. H-CASCA-01 (LTC, 41 pares): a casca de caudas acompanha a cauda real? ρ = +0,35, abaixo do limiar de fidelidade 0,40. A casca acompanha melhor a cauda da própria coordenada (+0,53) do que a do preço.

**5. A geometria residual: o teste que mudou a leitura.** Um mercado sintético com apenas memória linear de 1 min e o caminho real de volatilidade reproduziu a borda agitada (×5,2–6,9 contra ×6,5–6,8 no real), a persistência da orientação das cascas e a assinatura de caudas. O ×10,6 contra ×2,3 era em boa parte ilusão de uma nula fraca que destruía os surtos. Sobra um resíduo pequeno e consistente (agitação 9–14 % acima do sintético; cascas um pouco mais estáveis), não estável pelo critério. A Ana concluiu: **a geometria é real e não especial; é uma linguagem nova para ver os mesmos fatos.**

**6. Saltos e Markov.** Pelo critério de Pawula (curtose condicional), o campo tem saltos em todas as regiões, reproduzidos pelas caudas dos choques; os saltos reais são menos surpreendentes que choques ao acaso. A memória que quebra Markov em 3D tem o tamanho da de um processo de volatilidade pura.

**7. A quarta dimensão, fechada em três rodadas.** A 1ª foi INCONCLUSIVA: nem a volatilidade verdadeira tirava a memória do sintético, porque a medida usava o passo das coordenadas, dominado (96 %) pela terceira diferença do preço, que tem memória por construção. A 2ª, medida no retorno do preço dado o estado 3D, validou (o oráculo apaga 98–100 % da memória) e deu "sobra além de volatilidade de escala única". A 3ª, com volatilidade lenta real × rápida calibrada, deu **FECHADO e robusto**: o real fica entre dois processos de volatilidade pura, com quatro estimativas e dois períodos. A sobra era a escala rápida (minutos), não as lentas como eu supus antes de corrigir.

**8. A volatilidade vista na geometria.** Fatiando o cubo por temperatura: **a borda é a camada quente** (zero extremos nas fatias calma e média); e medido em unidades de volatilidade, o campo das três fatias colapsa no mesmo objeto (C = 0,88 e 0,92, igual ao sintético onde isso é verdade por construção). A temperatura é um zoom: muda o tamanho do cubo, não a forma.

**9. Em paralelo, o colaborador GPT** validou instrumentos multiescala para saltos, mostrou que um observador quadrático não vê memória direcional (SGV-ID4), e testou direção (SGV-D01) e memória ambiental do Paper A (SGV-AMB01) no BTC: nada em 82.683 observações. Duas análises independentes, com códigos e sintéticos diferentes, chegaram ao mesmo lugar.

## Os pontos de virada

&#91;embedded content: marcos do SGV · ago–nov/2026, três lanes\]

Cada lane é uma pergunta diferente feita ao mesmo objeto; a linha tracejada é o julgamento de outubro, o primeiro em dados que nenhuma exploração viu.

**As frases que mudaram o rumo, na ordem em que foram ditas:**

1. **"Quero uma auditoria crítica, não uma revisão favorável"** (ago/2026). Abriu a porta para separar fenômeno de metáfora. Sem isso, o toro teria continuado a fazer trabalho que não fazia.
2. **"Em que momento close\_chg é conhecido?"** (20/08). Uma pergunta da Ana derrubou o único achado de uma varredura de 74 features: era vazamento. Virou regra: toda variável precisa dizer quando passa a existir.
3. **"Quem está do outro lado e por que continua pagando?"** (ago/2026). Campo obrigatório de todo pré-registro. Separou ineficiências com prazo de validade de equilíbrios que duram.
4. **"A hipótese errou a ontologia, não a matemática"** (set/2026). O mercado não é um campo sobre o qual os agentes se movem; é feito das previsões dos agentes. Reposicionou o SGV ao lado do Paper A e do TAR.
5. **"Não é compreender a direção, é compreender o funcionamento. Não quero que a ferramenta seja especial"** (9/10). A reformulação que tornou o programa uma pesquisa de geometria da informação, e não uma busca de sinal.
6. **"O relatório do campo usou coordenadas gaussianizadas também no espaço original"** (14/10). A correção da Ana sobre a régua. Levou à descoberta de que a gaussianização apagava as caudas e ao campo nos extremos.
7. **"Pegue outro ativo e teste"** (14/10). Levou os dois testes em XRP e LTC, os dois não confirmados, que impediram que o +0,125 do BTC virasse achado.
8. **"Isso para mim foi ponto: a geometria é real e não especial. Pode não valer nada no mercado, mas para mim é importante"** (15/10). O fechamento da pergunta que abriu o SGV, nos termos da Ana.
9. **"Precisamos fechar a questão da volatilidade"** (15/10). Três rodadas, uma inconclusiva por erro meu de medida, até o fechamento robusto.

## O que aprendemos de fato

Dois tipos de aprendizado se acumularam: sobre o mercado, visto pelo cubo, e sobre como fazer a pesquisa. Cada linha abaixo diz o que se sabe, de onde vem e com que força.

### Sobre o mercado

| Insight | De onde vem | Força |
| --- | --- | --- |
| O cubo (E\_norm, jerk, memory\_flux) mede **agitação**, não direção. O campo D(x) sobrevive a controles fortes e a nulas de pipeline; o sinal do retorno não sobrevive a nenhum teste. | H-DIF-01 exploração, M8–M35, H-DOM, D01 e AMB01 do GPT, H-CAUDA-01 em XRP, H-CASCA-01 em LTC | Alta: 8 testes independentes, 3 ativos, 2 pesquisadores |
| Lucrar no 1 min é inviável com esse sinal. O alfa do SGV original estava dentro do acaso e a entrada funcionava como detector de surto de volatilidade. | Auditoria OIT→0, placebo, fila de 8 hipóteses de 2/09, E-FLX-02 (fluxo como filtro não ajuda) | Alta: exaustão honesta, zero sobreviventes |
| A geometria é **real e não especial**: um sintético com memória linear (AR(1)) e o caminho real de volatilidade reproduz a razão borda/núcleo (R real 6,8 vs sintético 5,7–6,9). A nula antiga (2,7) era pobre demais e fazia o real parecer único. | Geometria residual, jun–jul e ago–set | Alta: repetiu nos dois períodos |
| O campo é **volume + raridade**. Controlando ν e log ρ, a "geografia" residual do cubo (correlação com \|E\_norm\| ou \|jerk\|) some ou fica abaixo da nula: era artefato da medida. | Dimensão do campo, original-ν, jerk-original (3 leituras, 2 períodos) | Alta: três tentativas de achar geografia própria, nenhuma estável |
| O campo é **difusão com saltos**, não difusão pura: a 4ª derivada de Kramers–Moyal (curtose condicional) não some, e o teste de Chapman–Kolmogorov falha. O processo no cubo não é markoviano **dado o cubo**; o controle do GPT mostrou que uma proxy imperfeita de volatilidade basta para deixar memória aparente, o que foi o que o multiescala depois fechou. | Saltos/Markov; Saltos V2 controles (GPT, 8/8 portões) | Alta: repetiu; coincide com a literatura (jump-diffusion) |
| A dimensão escondida é a **volatilidade multiescala**. Com σ̂ em várias escalas (ew10, c60, ew30, har), a memória da surpresa do real cabe dentro do sintético M, e as quatro estimativas concordam. A unicidade não é identificável por um observador só de energia (ID4). | Volatilidade v2 (SOBRA) → multiescala (FECHADO robusto, validação 0,99); ID4 do GPT | Alta: robusto nas 4 estimativas, 5 réplicas, 2 períodos |
| A volatilidade age como **zoom**: medido em unidades de σ̂, o campo das três fatias de temperatura colapsa (C ≈ 0,9). A borda agitada é, em grande parte, a fatia quente. | Fatias de volatilidade, teste 2 | Média-alta: repetiu, mas é exploração |
| O **desacoplamento forma-de-D × casca** (o efeito do H-FORMA-D-02) é explicado por memória linear de 1 min: F = 1,09 e 1,01 contra a nula VAR(1). A nula de permutação intradiária destrói memória linear, não estrutura de campo. | Memória-D, jun–jul e ago–set | Alta como ressalva: muda como ler o julgamento de 3/11 |
| A régua importa. A gaussianização (M11-I) apagava as caudas; a régua de caudas (mediana e q99,5 de maio ÷ 3) preserva o que o campo vê. O GMM2 lê caudas espúrias em sintéticos pesados (RB-01: nenhum candidato aprovado), mas em BTC a ligação casca↔cauda (+0,64) não é artefato da régua (DG-01). | Comparação 14/10; RB-01, DG-01 | Alta: mudou o resultado de todos os testes seguintes |
| A ligação casca↔cauda é **validade de instrumento, não estrutura temporal**: sobrevive à troca de régua e independe da ordem dos minutos. Por isso a queda em LTC (+0,35 com nula +0,33) é do LTC, não da régua, e as caudas em XRP não carregam nada além da agitação local. | DG-01; H-CAUDA-01 (ρ +0,003); H-CASCA-01 | Alta como negativa: dois julgamentos registrados |
| O **excesso de σ da régua RTT** é propriedade estática (assimetria sinal × tamanho dos retornos), não dinâmica: H1 confirmada (D +0,0125, p < 0,0001) mas H2 (flecha do tempo) não (p 0,18). Nenhuma corrente direcional demonstrada; H-J perdeu 0/30 blocos para a matriz reversibilizada. | H-σRTT-01 (confirmatório, 13/10); ponte RTT↔M11-I | Alta: julgamento registrado |
| A geometria sem malha (HDR por orçamento, 6 feições retidas) **generaliza para fora da distribuição**: Δlog-loss +0,62 \[0,48; 0,75\] em OOD, com ganho concentrado no regime BS35. | C02.1, treino/validação/OOD com liberação selada | Alta: OOD liberado uma vez, hashes congelados |

### Sobre o método

| Insight | Como apareceu |
| --- | --- |
| **A ontologia erra antes da matemática.** A fila de 8 hipóteses de trading morreu inteira; a pergunta "o SGV lucra?" era a pergunta errada para o objeto. Reformular para "o que a geometria mede?" destravou tudo. | Virada de setembro |
| **Nula pobre fabrica descoberta.** Um sintético fraco (2,7) fazia o real (6,8) parecer único. A nula certa (memória + volatilidade) mostrou que a geometria é reproduzível. Toda vitória precisa de uma nula que saiba o que já se sabe. | Geometria residual |
| **A medida precisa estar na variável certa.** A rodada v1 de volatilidade mediu surpresa nos passos de coordenada, dominados pelo jerk (3ª diferença), e deu INCONCLUSIVO. Medir no retorno do preço (v2) deu resposta. | Volatilidade v1 → v2 |
| **Previsão antes do dado, com probabilidades.** Cada rodada registra apostas numéricas antes do código. As erradas (nula de pipeline em H-CASCA-01, "sobra = escalas lentas") ficaram escritas e corrigidas por emenda, não apagadas. | Toda PREDICAO\_\*.md |
| **Um julgamento, uma chance.** Confirmatórios rodam uma vez, em período reservado, com hashes congelados. Não há segunda tentativa, e a leitura pré-registrada é a que vale. | H-CAUDA-01, H-CASCA-01, C02.1 OOD |
| **O ceticismo do GPT valeu.** A régua alta dele forçou a nula multiescala e o sintético M. O que sobrou depois disso é mais sólido do que seria sem a pressão. | Rodadas de volatilidade |
| **Replicar em outro ativo e outro pesquisador.** XRP, LTC, e os experimentos independentes do GPT (ID4, D01, AMB01) chegaram ao mesmo lugar: agitação sim, direção não. | Outubro |

## Placar

Tudo que foi julgado ou está agendado, com o veredito pré-registrado. "Não confirmada" é resultado, não fracasso: pela regra da casa, uma hipótese que não passa fica registrada com o mesmo peso de uma que passa.

### Confirmatórios (uma chance, hashes congelados)

| Hipótese | Ativo e período | Pergunta | Veredito | Números |
| --- | --- | --- | --- | --- |
| H-σRTT-01 | BTC, 1/08–30/09 (61 dias) | O giro σ da régua RTT vem só da vol e das fórmulas (H1), e há flecha do tempo (H2)? | **H1 CONFIRMADA; H2 NÃO CONFIRMADA** | H1 D +0,0125, p < 0,0001; H2 D +0,0033, p 0,18; real − pipeline +0,0018 (p 0,31) |
| C01 | Sintético, holdout único | 12 descritores HDR melhoram a classificação de 7 transformações? | **APROVADA** (só no sintético) | Δ +0,0568 nats/par \[+0,041; +0,075\]; erros 5/280 → 0/280 |
| H-CAUDA-01 | XRP, jun–set | As caudas dos passos preveem Δlog q99,9 além da agitação local? | **NÃO CONFIRMADA** | ρ parcial +0,003, p 0,52, 2.143 janelas; paridade +0,125 |
| H-CASCA-01 | LTC, jun–set | A rotação da casca HDR50 prevê Δlog q99,9? | **NÃO CONFIRMADA** | ρ +0,348, p 0,013, 41 pares, mas a nula de pipeline dá +0,33 (Emenda 1) |
| C02.1 OOD | Gerador oficial C02, treino/validação/OOD | As 6 feições HDR sem malha melhoram o log-loss fora da distribuição? | **SUCESSO** | Δ +0,618 \[0,482; 0,749\]; BS35 +1,06, R7 +0,18; controle de dimensão −0,019 |
| H-DIF-01 | BTC, outubro reservado | log tr D(x) carrega amplitude de 5 min além de vol e log ρ? | **Agendado 3/11** | exploração: fluxo −0,065, original +0,046 (8/8 semanas); apostas 60 % / 55 % |
| H-DIR-01 | BTC, outubro reservado | μ\_r(x) prevê o retorno de 15 min? | **Agendado 3/11** | expectativa registrada: nulo (70 %) |
| H-FORMA-D-01 | BTC, outubro; réplica em novembro | A concentração c(x) da agitação antecede a amplitude? | **Agendado 3/11; réplica dez** | exploração: fluxo +0,085, original +0,047; poder no original só 0,29–0,42 |
| H-FORMA-D-02 | BTC, outubro; réplica em novembro | Forma de D e forma da casca mudam juntas menos que a nula de pipeline? | **Agendado 3/11; réplica dez** | ago–set repetiu no fluxo (Δ −0,24, p 0,0005); errou no original. Ressalva memória-D entra no relatório |
| H-VOL-01 | BTC, outubro reservado (24/09–29/10) | A volatilidade multiescala fecha a memória em dado novo? | **Agendado 3/11** | paridade jun–jul registrada; 11 arquivos com hash |
| H-SGV-01 | BTC, (a) outubro; (b) outubro + novembro | O SGV original (log ρ, mem\_e) acrescenta sobre log Range\_{t+5} além do espaço de fluxo? | **(a) Agendado 3/11; (b) dezembro** | exploração: 5/5 apostas acertaram; mem\_e complementar ao fluxo (−0,026 / −0,017); apostas a 80 %, b 45 % |
| H-4D-01 | BTC, outubro (semanas 1–29/10) | (a) A forma da fatia de temperatura muda com σ̂ mais que no M? (b) A inclinação da nuvem 4D fica no envelope do M? | **Agendado 3/11** (congelado 16/10, d1f48d0) | meses abertos: (a) real +0,14 / +0,10 **abaixo** do M; (b) R² linear ≈ 0,02 dentro do M, fraco por simetria (Emenda 1); quadrático 0,29 / 0,25; zoom real 1,38 / 1,31 vs M 1,22–1,30. Apostas revistas: a \~10 %, b \~60 % |
| H-TEMPO-01 | BTC, outubro (semanas 1–29/10) | (a) A memória de \|r\| é mais lei de potência que o M, com β em 0,1–0,6? (b) A borda do cubo reverte mais que o núcleo, além do M? | **Agendado 3/11** (congelado 16/10, 574363d) | meses abertos: (a) ΔR² real 0,55 / 0,50 vs M 0,50–0,54 (acima por 0,008; depois dentro), β 0,13 / 0,18; erro de desenho na Emenda 1: o M herda a memória longa do real. (b) Δφ −0,042 (borda reverte, M não) / +0,001 (dentro do M). Apostas revistas: a \~20 %, b \~30 % |

### Portões e testes pré-registrados da Fase 2–3 (BTC jun–set ou sintético)

| Teste | Pergunta | Veredito |
| --- | --- | --- |
| R1 (portão G1′, 9/10) | A geometria ΔF do estado (z, ι, ν) tem conteúdo além dos fatos estilizados (SF1)? | **Reprova em 1m e 1h**; linha geométrica do SGV original encerrada pela regra (p 0,25 / 0,10) |
| L2 (9/10) | A velocidade Fisher–Rao antecede mudança de regime de vol? | **Sem poder** (0 % em 1m e 1h): não refutada, não testável; confirmatório não rodou |
| C2 (9/10) | Geometria preço–fluxo vs GARCH + lei de impacto | **Retirado**, nunca rodado (só uma reformulação permitida; Ana escolheu R1) |
| FR-EWMA (9/10) | A curvatura Fisher–Rao da trajetória EWMA prevê log range além de GARCH? | **Não passa** em 1m (p 0,21) nem 1h (p 0,65); confirmatório ficou virgem |
| H-DOM (12/10) | A dominância de lóbulo acerta o sinal do retorno de 60 min? | **Não apoiada**: 34,5 % (20/58), p 0,994 |
| M19 / H-RUP (ago–set) | O alarme M11 antecede rupturas? | **Não apoiada**: 2/15 vs 1/43, p 0,155 |
| M31, M32, M33 (ETH, SOL, BNB) | Forma e curvatura da casca acrescentam skill ao HAR-X? | **Falha** nos três: −0,07 %, +0,02 %, −0,08 % (ICs cruzam zero) |
| M34 (13/10) | A assinatura M11-I prevê o próximo nó do estado? | **B-GEO não supera B0** (log-loss 2,949 vs 2,880); não liberar confirmação |
| M35 P1–P3 (14–15/10) | Existe medida de deformação só geométrica com confiabilidade ≥ 0,6? | **Não**: melhor candidata 0,37; a não-elipticidade é imagem do acoplamento \|retorno\|–volume |
| C02 portão V1 (14/10) | O extrator HDR em grade é estável em caudas pesadas? | **Bloqueado**: 8/28 checagens fora de 10 %, volume até 246 % → emenda C02.1 |
| C02.1b/1c portão (15/10) | O extrator HDR sem malha é confiável? | **Passa**, 6 feições retidas (W₂ do HDR50 em 0,5016, rente ao corte) |

### Explorações (jun–jul e ago–set, sem outubro)

| Rodada | Pergunta | Leitura |
| --- | --- | --- |
| Dimensão do campo (3 leituras) | Há geografia própria no cubo além de ν e log ρ? | **Não estável / artefato da medida** nas três tentativas (campo, original-ν, jerk) |
| Memória-D | A memória linear de 1 min explica o desacoplamento dFD–dFS? | **Explica** (F 1,09 e 1,01); previsão do eixo errou (ι, não ν) |
| RB-01 / DG-01 | A casca GMM2 lê caudas espúrias? O +0,64 casca↔cauda é artefato? | RB-01: **nenhum candidato aprovado**; DG-01: **não é artefato** (ρ 0,56–0,64 em 5 réguas) |
| Campo de caudas (14/10) | D(x) cresce com a extremidade na régua de caudas? | ×10,6 do núcleo aos extremos (nula ×2,3); ρ parcial corrigido de +0,21 para +0,06–0,12 |
| U2 / W-HDR | A máquina rotula mecanismos melhor que o painel convencional? | **Não** (F1 0,43 vs 0,64); W-HDR detecta forma melhor que M11-I, mas não acrescenta ao convencional |
| E-FLX-02 | Fluxo de segundos como filtro de entrada ou aborto? | **As duas regras não funcionam**: 96 % dos rompimentos já têm fluxo a favor |
| E-VOL-01 | D(x) sobrevive à vol implícita (Deribit)? | Sim: fluxo −0,065 → −0,065; original +0,046 → +0,041 |
| Geometria residual | Há geometria própria além de memória linear + volatilidade? | **Nenhuma própria estável.** R real 6,83/6,48 dentro do sintético 5,7–6,9 / 5,2–6,3 |
| Saltos/Markov | Difusão pura e markoviana? | **Não e não.** Pawula falha, Chapman–Kolmogorov falha |
| Saltos V2 controles (GPT) | O instrumento distingue saltos de difusão e vol latente de homocedasticidade? | **8/8 portões**; proxy imperfeita de vol deixa memória aparente |
| Volatilidade v1 | A volatilidade explica a memória nos passos do cubo? | **INCONCLUSIVO** (medida na variável errada, dominada pelo jerk) |
| Volatilidade v2 | ...e no retorno do preço? | **SOBRA** além da volatilidade de uma escala |
| Volatilidade multiescala | ...com escala rápida calibrada por semana? | **FECHADO, robusto.** 4 estimativas concordam; validação 0,99 |
| Fatias de volatilidade | Fixando a temperatura, a geometria simplifica? | **Colapsa** (C ≈ 0,9) no teste 2; 1a explica em parte; 1b não informativo (erro de desenho reconhecido) |
| Auto-similaridade temporal (16/10) | O cubo é o mesmo em 1, 5 e 15 min, relativo ao M? | **Colapso auto-similar** (C 0,70–0,93 nas três resoluções, dois períodos); **borda muda de escala** (R 6,8→4,6 e 6,5→2,4): a borda agitada é um objeto de 1 minuto. M instável em ago–set 1 min (R 12–15), limitação registrada |
| Memória em lei de potência v1 (16/10) | Entre 1 min e 1 dia, a memória de \|r\| é lei de potência ou duas exponenciais (sintético E2 com escala lenta ajustada)? | **NÃO ESTÁVEL.** Real prefere a reta log-log nos dois períodos (ΔAIC ≈ −6, β 0,13–0,18), mas o E2 reprova a validação em ago–set: duas exponenciais com τ de 5–12 h parecem potência até 1 dia |
| Memória em lei de potência v2 (16/10) | ...e até 5 dias, com jun–set agrupado? | **INCONCLUSIVO nos três períodos: o instrumento reprovou.** Dois defeitos de desenho reconhecidos: a grade pisa nos múltiplos de 1 dia e a divisão por s(h) imprime o ciclo diário nos sintéticos (ρ do E2: 0,00 em 2.048 min, 0,16 em 2.880); e o E2 é re-ancorado no real toda semana. v3 especificada, não rodada. Sobrevive: β ≈ 0,15 do real e mais memória curta que qualquer sintético de duas escalas |

### Do GPT, independentes

| Experimento | Leitura |
| --- | --- |
| SGV-ID4 | Unicidade da volatilidade **não identificável** por observador de energia (Δ +0,24 nats/obs); 3/3 portões |
| SGV-D01 | Direção ausente, com nula própria |
| SGV-AMB01 | Ambiguidade de sinal confirmada; repete em 1/12 |
| Saltos V2 controles | 8/8 portões, 9/9 sanidades; sem resultado confirmatório financeiro |

### Contagem

- Julgados com hashes congelados: 5 (H-σRTT-01 parcial, C01 aprovada, H-CAUDA-01 e H-CASCA-01 não confirmadas, C02.1 OOD sucesso).
- Portões e testes pré-registrados da Fase 2–3: 11, com 1 aprovado (C02.1 portão), 1 sem poder (L2), 1 retirado (C2), 8 negativos.
- Explorações com previsão registrada: 14, mais 4 do GPT.
- Agendados: 5 hipóteses em 3/11 (H-DIF, H-DIR, H-FORMA-D-01/02, H-VOL), H-SGV-01 em out/nov, 1 réplica em dezembro, 1 repetição do GPT em 1/12.
- Trading no 1 min: 8 hipóteses de 2/09, zero sobreviventes.

## O método da casa

A regra que governa tudo: **nenhuma vitória não conquistada será anunciada.** O que ela virou, na prática, entre agosto e outubro:

1. **Previsão antes do dado.** Cada rodada começa com um `PREDICAO_*.md` ou `PREREGISTRO_*.md` commitado antes do código: espaço, régua, estatística, critério de classificação e apostas com probabilidade. Quando a previsão erra, entra uma emenda datada; nada é reescrito.
2. **Fumaça em maio, sem imprimir.** O código roda primeiro num período de calibração com as estatísticas suprimidas. Prova que roda sem mostrar resultado.
3. **Dois períodos ou nada.** Uma exploração só conta se repetir em jun–jul e ago–set. Um período só é "não estável".
4. **Períodos reservados intocados.** Outubro de BTC é dos confirmatórios (H-DIF, H-DIR, H-FORMA, H-VOL); novembro é da réplica de H-FORMA-D-02. Todo script tem `assert ts < 2026-10-01`. Os julgamentos rodam só por `workflow_dispatch`, uma vez, em 3/11.
5. **Hashes congelados.** Antes do julgamento, cada arquivo do pipeline tem SHA-256 em `referencia/HASHES_*.txt`. O resultado cita o commit e os hashes. C02.1 foi além: modelos congelados em pickle com `CONGELAMENTO.sha256`, e o OOD liberado por uma troca selada de `seed_for`, uma única vez, com "AUTORIZADO" da Ana.
6. **Nulas que sabem o que já se sabe.** Permutação dentro do dia, nula de pipeline (o mesmo código em dado embaralhado), e sintéticos G, S e M que carregam memória linear e o caminho real de volatilidade. Uma nula pobre fabrica descoberta; a boa nula é metade do teste.
7. **Nunca em `main`.** Um ramo por estudo (`confirmatorio/...`, `exploracao/...`, `research/...`), commit de pré-registro primeiro, workflow disparado pelo push do próprio arquivo.
8. **Leitura separada do resultado.** `RESULTADO_*.md` traz os números; `LEITURA_*.md` traz o que eles significam, com a classificação pré-registrada aplicada mecanicamente. Nada de "quase", "tendência" ou segunda tentativa.
9. **Erros ficam escritos.** A rodada v1 de volatilidade (INCONCLUSIVO, variável errada), o teste 1b de fatias (não informativo, erro de desenho) e a nula de pipeline de H-CASCA-01 (expectativa errada, retratada antes do dado de LTC) estão no repositório com a explicação.
10. **Dois juizes.** O GPT replica com nulas próprias (D01, AMB01) e mantém a régua alta. Quando ele e o Claude discordam, o teste seguinte é desenhado para decidir, não para convencer.

O custo desse método é velocidade: três confirmatórios julgados em dois meses. O ganho é que cada linha do placar pode ser lida sem desconto.

## O que está aberto

### Calendário

| Data | O quê | Quem |
| --- | --- | --- |
| até 29/10 | Outubro de BTC fecha. Nenhum script lê esse mês até lá. | — |
| **3/11, 10h (Brasília)** | Julgamento de H-DIF-01, H-DIR-01, H-FORMA-D-01/02 e H-VOL-01 em outubro. Tarefa agendada, roda sozinha, avisa por push e e-mail. H-SGV-01 (a) também usa outubro e pode ser julgado no mesmo dia. | Claude (agendado) |
| novembro | Reservado para a réplica de H-FORMA-D-01/02 e para H-SGV-01 (b). Intocado. | — |
| 1/12 | GPT repete D01 e AMB01. Precisa respeitar a reserva de novembro: usar dados até outubro ou esperar dezembro. | GPT, Ana decide |
| dezembro | Réplica de H-FORMA-D-01/02; julgamento de H-SGV-01 (b); memória no espaço original (mem\_e). | Claude |

### Perguntas que a Ana ainda não respondeu

- **Como ler H-FORMA-D-02 em 3/11.** A rodada memória-D mostrou que a nula de permutação intradiária destrói memória linear, não estrutura de campo, e que um VAR(1) reproduz o desacoplamento (F ≈ 1,0–1,1). Se H-FORMA-D-02 passar, o resultado é compatível com "memória linear de 1 min" e não prova geometria própria. Vale registrar essa leitura antes do julgamento, não depois.
- **H-SGV-01.** Congelado em 15/10. A parte (a), outubro, entrou na tarefa agendada de 3/11 em 16/10 (decisão da Ana). A parte (b), o `conjunto` out + nov, e as replicações ficam para dezembro.
- **H-FORMA-D-01/02.** Congelados para outubro, mas **não estão na tarefa agendada de 3/11** (ela cobre H-DIF-01/H-DIR-01, H-VOL-01 e H-SGV-01a). Decidir se entram nela ou rodam à parte.
- **M34.** Reabrir ou arquivar. O resultado de 13/10 (B-GEO não supera B0) sugere arquivar.
- **PR #1 em `sgv_original`.** A reescrita exata da métrica legada espera revisão. Não toca `main` até ela aprovar.
- **U03.2 e RB-02.** Pendentes do navegador; nenhum dos dois foi pré-registrado. RB-01 não aprovou candidato de casca na régua bruta; RB-02 precisaria consertar os defeitos de desenho apontados (G5 teto 0,87, G1 no limite do Monte Carlo).
- **L2.** Não refutada, só não testável com o desenho atual (atraso estrutural ≈ W/2). Se voltar, precisa de outro contraste, não de outra janela.
- **Teste do fluxo.** Proposto em 15/10: medir a volatilidade como 4ª coordenada no espaço de fluxo (passos), não no de posição. Não registrado. A opinião do Claude: vale um `PREDICAO` curto, exploratório, jun–jul e ago–set, só depois de 3/11.
- **C03.** Próximo módulo do programa C02. Depende de C02.1 OOD, que passou; falta a Ana dizer o escopo.

### O que o Claude recomendaria, se perguntado

1. Esperar 3/11 sem abrir nada novo em BTC. Quatro hipóteses no mesmo mês já é muita coisa para julgar bem.
2. Depois do julgamento, escrever a leitura conjunta: agitação + saltos + volatilidade multiescala é uma descrição coerente do campo; se H-VOL-01 passar, ela está fechada em dado novo.
3. Só então decidir entre o teste do fluxo e C03. Os dois são explorações; não há pressa.

### Onde está cada coisa

- Repositório: `ana-rigel/sgv-geometria`, um ramo por estudo.
- Documento técnico de C02.1: "Campo informacional do SGV", rev 25.
- Tarefa agendada de 3/11: "Julgamentos de outubro/2026: H-DIF-01 e H-VOL-01".
- Este documento: a trajetória, para reler quando a pergunta voltar a ser "o que a geometria é".
