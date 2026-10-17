# SGV: a trajetória da pesquisa

Oct 16, 2026 · @Ana Rigel

## Em uma página

O SGV começou em meados de 2026 como um sistema de trading em BTCUSDT a 1 minuto, com uma hipótese fundadora: o mercado é um campo informacional, e entender a geometria dos estados revelaria a direção do preço. Em outubro de 2026 ele é um programa de pesquisa em geometria da informação, com repositório versionado (`ana-rigel/sgv-geometria`), \~90 ramos de experimentos, pré-registros com julgamento único e nulas que separam mercado de artefato.

**O que ficou de pé.** O mercado pode ser traduzido num espaço de estados 3D com campo (deriva, agitação), cascas de densidade (HDR50/HDR95) e trajetória. Essa geometria é **real** (passa pelas nulas que destroem a estrutura do mercado) e **não é especial** (quase toda ela é a forma geométrica de fatos já conhecidos: memória curta, surtos de volatilidade, caudas pesadas). A conclusão da Ana em 15/10: é uma linguagem nova e válida para ver os mesmos fatos.

**O que caiu.** Direção não existe a 1–15 minutos, por nenhum caminho testado (sete tentativas independentes). Lucro no 1 minuto é inviável: borda \~0,01 % por trade contra custo de 0,04–0,20 %. A geodésica da métrica Hessiana não descreve o movimento. As formas das cascas, como previsoras, falharam em todos os testes.

**O que se descobriu sobre o espaço.** A dimensão escondida do cubo 3D é a volatilidade, em várias escalas (minutos, horas, dias). Ela age como um zoom: a borda do cubo é a camada quente, e medidas em unidades de volatilidade, as temperaturas colapsam no mesmo objeto. O campo é de difusão com saltos, não difusão pura.

**O que decide o próximo capítulo.** Quatro testes confirmatórios congelados julgam outubro/2026 em 3 de novembro: H-DIF-01, H-DIR-01, H-FORMA-D-01/02 e H-VOL-01. São os primeiros julgamentos num mês nunca visto por nenhuma exploração.

## Fase 0 (27/2 a 17/3/2026): a origem

Esta fase foi reconstruída em 17/10/2026 a partir do arquivo `sgv_runtime.zip` (pasta `scripts/testes_sgv`, 200 scripts Python e 171 CSVs, datados de 27/2 a 17/3/2026), lido na íntegra. É a história de como o SGV nasceu, em dezenove dias, antes de qualquer regra de método. Os números abaixo são os que os próprios scripts gravaram; nenhum foi recalculado. Nada desta fase conta no placar: não havia pré-registro, nulos governando, nem períodos reservados. Ela está aqui porque explica tudo o que veio depois.

**Em uma frase.** Em três semanas a Ana inventou o vocabulário inteiro do projeto, escolheu três variáveis que sobreviveram a tudo, escreveu o primeiro nulo no sexto dia e, no último, chamou de "final" um backtest de 37 trades com 81 % de acerto. A diferença entre março e outubro não é a cabeça; é quem manda nela.

### 27/2: a semente não era mercado

O SGV começou como um motor geral de "inferência geométrica" (`sgv/core/runtime.py`): um laço Percepção → Ação → Memória → Organização em que um vetor de memória M resiste a mudar (parâmetro **rigidez**, taxa de aprendizado = 1 − rigidez), é puxado devagar por um vetor de organização O (`org_pull`), e a **tensão** é ‖F − M‖: a distância entre o que se vê e o que se lembra. Um detector de regime classifica STABLE, TRANSITION e RUPTURE por limiares sobre a média móvel da tensão, com histerese de três passos. Os símbolos são funções de distância com sinal (SDF) combinadas por união, interseção e subtração.

Os quatro primeiros scripts aplicam isso à vida, não ao preço:

- `projeto_liberdade.py`, "Monitor de Transição para o Sítio": objetivo = \[custo do doutorado 50.000, reserva para o sítio 200.000\], rigidez 0,95 ("você é resiliente, aguentou o doutorado e a prefeitura"), seis meses de licença simulados, saída chamada **"Tensão com o Sonho"**.
- `sgv_decisor.py`: saldo de −5.000 contra alvo de 2.000; tensão > 1,5 = "regime instável, corte imediato de despesas, bloquear novas licitações por 30 dias"; > 0,5 = contingenciamento; senão manter o plano.
- `dashboard_financeiro.py`: doze meses de receita e despesa com "estouro no mês 10"; plota o "nível de tensão semântica do orçamento".
- `sgv_auditor.py`: grava cada decisão com hash SHA-256. O `auditoria_decisoes.csv` tem uma linha: 27/2/2026 18:52:43, REGIME INSTÁVEL, tensão 5000, corte de 50 %, hash a5257ec8d82fa17b. É a primeira decisão auditada do projeto, e a ideia de auditar antes de confiar nasceu aqui.

A ideia-mãe, "a distância entre o observado e o lembrado mede a crise", está no painel de hoje sem alteração: o eixo `memory_flux` do cubo é a variação da E\_norm suavizada, isto é, o quanto o preço está se afastando da própria memória.

### O que a semente virou fora do mercado: o vinco, o Paper A e os estudos que vieram depois

A figura dos três corpos não nasceu do trading e não terminou nele. A Ana a sonhou no sítio como uma **IA geométrica**: observação, lembrança e identidade como três pontos num plano, e inteligência como o jeito de os três se moverem um atrás do outro sem se colarem. O script `visualizar_ia.py` (4/3/2026; `visualizar_ia_novo.py` com mapa de calor e campo vetorial no mesmo dia) é o desenho dessa mente, e está reconstruído ao vivo na página **Teste B do SGV** (`visual/teste-b-mente-geometrica.html`): o campo ∘ teleporta sem aviso, a memória □ corre atrás com rigidez 0,85, a organização ⋄ segue a memória com `org_pull` 0,05, e o regime é a tensão comparada ao próprio passado.

Lida de outubro, a figura contém em escala de brinquedo o que os estudos seguintes formalizaram:

- **Cegueira espectral (Paper A).** Memória com rigidez é um filtro passa-baixa: com rigidez 0,85 ela só acompanha o que muda em escalas maiores que \~7 passos; a organização, com `org_pull` 0,05, é cega a tudo mais rápido que \~20 passos. O alvo do Teste B teleporta a cada 20: o mundo foi posto exatamente na frequência de corte da identidade, e por isso a organização nunca chega, por construção. É o enunciado do Paper A antes de ser teorema: um registro interno autoconsistente tem uma banda do espectro que não pode ver, e a banda é definida pela própria rigidez; a cegueira não é defeito do registro, é o preço de ele ser um registro. O Paper A ("Environmental Memory as a Resource for Self-Consistency: Information-Theoretic Limits of Internal Observers", com o colaborador matemático) levou isso ao caso linear-gaussiano fechado: cegueira graduada via complemento de Schur, fronteira persistência × resolução, e o platô do rastreador puro como máximo global exato.
- **O vinco da identidade como invariante.** Se o mundo salta e a memória corre, o que permanece é o que não respondeu ao salto: a organização, lenta demais para ser arrastada. Identidade, nessa leitura, não é o que a mente acredita; é o que nela não se moveu quando tudo se moveu. Um vinco, a marca que fica no papel depois que a dobra se desfaz. O invariante é uma lentidão, e o seu preço é a cegueira: o mesmo parâmetro que faz o vinco durar faz o registro não ver. O programa do vinco é a leitura do Paper A pelo lado do que sobra.
- **Paper B** levou a pergunta a redes recorrentes treinadas, com pré-registro: a hipótese que sobreviveu à auditoria de literatura (H1) mede o perfil de inacessibilidade do registro interno à própria dinâmica por frequência, exatamente a curva que o Teste B desenha com dois corpos e duas rigidezes.
- **Paper C** (ancoragem representacional com histerese) formaliza a parte em que a organização resiste: inferência bayesiana correta cujo canal de evidência é filtrado pela própria representação produz uma fase ancorada, com fronteira de fase em forma fechada; é a histerese de três passos do detector de regime de 27/2 virando teorema. Dele derivaram a teoria de reparo e corrigibilidade de sistemas autorreferenciais e a linha de crédito causal sem oráculo.
- **OBS-01** (14/10/2026) fecha o laço com o SGV: o protocolo para medir o ponto cego do observador interno em IAs combina o Paper A com o campo D(x) e a nula de pipeline deste repositório. O instrumento que foi feito para o cubo serve para a mente.
- **Reobservar versus lembrar** e o **EM-AI** são a mesma pergunta levada ao custo e ao hardware: quando reobservar o mundo custa menos que lembrar, e como uma memória ambiental se materializa num chip. No Teste B essa pergunta já está posta: a memória que corre atrás do campo é a que paga para lembrar; o campo é o que se reobserva de graça.

A ordem verdadeira dos acontecimentos, portanto: o sonho deu a figura; o SGV foi o primeiro corpo onde a figura encostou em dados, e o corpo respondeu que o mundo salta sem aviso e a mente corre atrás com quatro andares de memória e nenhuma direção; o Paper A perguntou o que a figura implica para qualquer registro que se mantém, e achou a cegueira; o vinco é a identidade vista pelo lado do que sobra; os demais estudos são a mesma ideia em outras línguas. O que falta ao Teste B para merecer o nome de inteligência, e que nenhum dos estudos ainda mediu, está anotado como item aberto: uma organização que guarde regularidade em vez de posição (aprender que o mundo salta a cada vinte e baixar a tensão antes do salto) e uma rigidez modulada pela surpresa (rigidez = f(E\_norm), o que o motor de memória de 13/3 fez à mão sem fechar o laço). Os dois têm nulos naturais: o alvo sem ritmo; a rigidez fixa.

### 4 a 6/3: a explosão (semana 1)

Em 4/3 o motor recebe BTC pela primeira vez: 13.529 ticks de \~8 s (2 a 4/3), com entrada U = \[retorno, volatilidade EWMA, momento rápido, momento lento\]. No mesmo dia nascem o **mapa de fase** (E\_norm × log tensão, colorido por regime), o **atrator** (densidade de ocupação no plano), o **fluxo de fase** (média de (dE, dT) por célula) e o **mapa de lucro** (retorno futuro médio por célula). `estrategia_mapa_lucro.py` traz o primeiro corte treino/teste (70 %, células com mínimo de 80 pontos) e o primeiro baseline (comprar e segurar).

Em 5/3 vem a família dos índices de criticalidade: CI = 0,4·tensão + 0,4·vibração + 0,2·(1 − coerência); CI2 = tensão × vibração; CI-STRUCT ("tectônico"), CI-A (com aceleração), CI-ULTRA ("crise perfeita" = tensão × aceleração × estrutura), CI-ALIGN, CI-ELASTIC. A pergunta era: qual combinação separa melhor a volatilidade futura alta? Com o comentario no código: `Q_CRITICAL = 0.98 # Onde o Ratio bateu 1.72`. A pergunta já era sobre **tamanho** do movimento futuro; a direção entrou como segundo passo.

Em 6/3 nascem o **jerk** (segunda diferença da tensão; `z_abs_jerk` em janela de 100 com deslocamento de 1, sem olhar o futuro), o "estalo", a **nucleação** (dois eventos extremos em cinco candles), a "tempestade perfeita" (jerk junto com CI extremo), a energia liberada e a magnitude elástica. E, no mesmo dia, os **dois primeiros nulos do projeto**: `teste_sgv_shuffle.py` (mantém as direções dos trades, permuta os retornos futuros mil vezes, pergunta se o win rate real é melhor que o acaso) e `teste_sgv_random_baseline.py` (sorteia o mesmo número de candles e usa a direção deles). O primeiro nulo tem a mesma idade que a primeira hipótese; ele só não mandava ainda.

Os números gravados em 6/3: CI no topo q99, 63 trades, 55,6 % de acerto, fator de lucro 1,92; q99,5, 42 trades, 64,3 %, 2,50; q99,9, 12 trades, 58,3 %, 1,03. O "atuador de elite" (stop 0,15 %, alvo 0,25 %): 24 trades, 75 %, fator 3,48. O painel de replay do dia já trazia a frase "CONFIGURAÇÃO DE ELITE (71,6 % acc)" e "ALVO DETECTADO: SALTO DO ÁTOMO". Todos esses quantis foram calculados sobre a amostra inteira, e nenhum desses números tinha nulo ao lado.

### 7 a 13/3: a física (semana 2)

Em 7/3 o motor vai para o tempo real (Binance, candles de 1 min, paper trading) e a lógica vira de momento para **reversão**: vende quando a tensão sobe, compra quando cai, com gatilhos CI ≥ 0,85 e jerk ≥ 1,5. Em 8 e 9/3 aparece a taxonomia do **colapso**: VACUUM (CI ≥ 0,90, score ≤ 0,15), WHIP ("chicote"), SINGULARITY (CI ≥ 0,97, jerk ≥ 6) e as fases VACUUM → IGNITION → SINGULARITY → WHIP, cada classe com sua política de stop e alvo. Os logs reais de paper trading: 23 trades (8 a 9/3), 56,5 %, fator 1,90; 17 trades (10 a 11/3), 58,8 %, fator 1,96. A palavra "colapso" foi escolhida aqui, meses antes de significar invariância de escala.

Em 10/3 entram as metáforas: espaço de estado (dT, jerk) com raio r; **rigidez λ** como taxa local de contração; **energia** V = −log P(vitória) por KDE; **força restauradora** F = −∇V; uma simulação dinâmica que integra a trajetória no potencial; e o `experimento_lorenz.py`, que é um gráfico de dispersão dos trades sobre a nuvem do campo, "estilo Lorenz, coração da borboleta". O `validar_motor_probabilistico.py` aplicou o motor a 10 trades: 3 aceitos (100 % de acerto), 7 bloqueados (42,9 %), com a superfície de probabilidade construída sobre os mesmos 10 trades.

Em 11/3, o dia mais denso: embedding de Takens (τ = 5, m = 3), teste de **SOC** (histograma log-log das rupturas com "−3 < inclinação < −1 → possível SOC"), potencial de mercado V(r) = −∫F(r)dr, elasticidade, escala de variância, densidade de fase, índice de instabilidade (0,35·r + 0,25·|dr| + 0,25·(1 − λ) + 0,15·|jerk|), regimes por quantil (PRESSÃO q70, INSTÁVEL q90, RUPTURA q97) e a **matriz de transição** entre regimes: P(ruptura em 5 min | regime RUPTURA) = 0,82; em 15 min, 0,91; a partir de ESTÁVEL, 0,012. É a primeira medida do projeto de que a volatilidade tem memória, sete meses antes de o v3 da memória dizer quanto (duas exponenciais) e o MSM dizer em quantas escalas (pelo menos quatro). O `bootstrap_sgv4.py` não é um bootstrap estatístico: é um gerador do pacote `sgv4/` com essas probabilidades fixas no código. O backtest do SGV-4 (direção por EMA20, sinal deslocado em 1): base 422 trades, 36,7 %, fator 1,03; com o filtro, 397 trades, 36,5 %, fator 1,06.

Em 12/3 os "mapas mestres": campo, estabilidade e borda sobre os 23 trades da reversão v2. As células têm de 1 a 3 trades; o próprio código marca todas como `stable = False` (mínimo 5) e `edge_class = incerta`, e ainda assim nasce a **"rota de ouro"**, λ = 0,0078·r − 0,86, ajustada aos vencedores. Em 13/3, sete dias de 1 min (10.080 candles, zero lacunas), r redefinido como distância à SMA40, motor de memória com α adaptativo, E\_norm reformulada como energia por z-scores robustos (MAD), matrizes de stress (P(ruptura) de 0,13 a 0,54 conforme E e jerk), radares v5 a v7.1 (as "células de ouro" com acurácia ≥ 0,60 e n ≥ 25 ficaram **vazias**) e o primeiro backtest com custo (0,10 % por trade): 46 trades, 52,2 % bruto, **13,0 % líquido**, retorno −4,99 %.

### 15 a 17/3: o campo informacional (semana 3)

Em 15/3, o **terreno**: estado x = \[E\_norm, jerk\], atrator local por média exponencial, deslocamento de Mahalanobis até ele, KDE global com gradiente e Hessiana, profundidade de bacia, histerese, e quatro estados por quantil (COHERENT, TENSIONED, TRANSITION\_EDGE, RUPTURE\_CORRIDOR). A validação deu correlação 0,376 e lift 28,7 entre decis extremos, mas o alvo (E\_norm ou jerk acima de q95 no passo seguinte) era feito das mesmas variáveis que entravam no score: uma variável contra si mesma. O **campo de força** F = ∇(profundidade de bacia) e o alinhamento cos(F, movimento): 59,6 % positivos, cosseno médio 0,085.

Em 16/3, a geometria: densidade ρ por KDE, potencial φ = −log ρ, métrica g = Hess φ, símbolos de Christoffel, aceleração e resíduo geodésico, e uma camada 3D (E, jerk, memória) com tensor de Ricci, curvatura escalar, **tensor de Einstein**, "gravidade informacional" e **memory\_flux**. O detector de singularidade combina 1/λ, 1/det g, ‖Γ‖ e curvaturas num `sgv_singularity_score` e num `sgv_criticality_score` ("estado metastável pré-singularidade"). A validação desse dia é o número mais importante da fase: para "evento extremo no próximo minuto" (base 20,0 %), o criticality\_score acima de q99 tem precisão 42,6 %, **lift 2,13**; em três minutos, 79,2 % contra base 43,4 %. Sem nulo e sem régua, é a mesma coisa que o campo de caudas mediu em 14/10 com nulo e régua (D cresce ×10,6 do núcleo aos extremos, contra ×2,3 do nulo): **a cauda é outro objeto**. O sinal existia em março; o que faltava era saber que ele é tamanho, não direção. E a direção já estava respondida no mesmo CSV: os modelos de direção (gravidade, gradiente, consenso) deram de 46 % a 52 % de acerto em 1 minuto.

Em 17/3, tudo em 90 dias (129.346 candles, 17/12/2025 a 16/3/2026), com o comentário da própria Ana no terreno v2: "exploratório/global; não é causal rolling". E a escada de backtests v15 → v23, todos com quantis calculados sobre os 90 dias inteiros:

| Versão | O que mudou | Resultado gravado |
| --- | --- | --- |
| v15 | entradas CORE e EXTREME; saída por alinhamento, stress ou máximo 20 min | CORE 5.191 trades, fator 1,18; EXTREME 1.767, 1,31 |
| v16 | só stress q90 + criticalidade q90 | 3.906 trades, fator 0,96, −14,1 % |
| v16.1 | criticalidade ≥ q95 + stress ≥ q95 | 44 trades, fator 2,06 |
| v17 | saída dinâmica por alinhamento e stress | dinâmica 2,07; **saída fixa de 15 min: 79,5 %, fator 5,67** |
| v18 | trailing de 0,15 % a 0,35 % | melhor 0,25 %, fator 2,93; fixa de 15 min, 5,69 |
| v20 "final" | trailing adaptativo pelo stress | adaptativo 39 trades, 56,4 %, fator 3,35; **fixa de 15 min: 37 trades, 81,1 %, fator 5,98** |
| v22.1 | só estado TENSIONED, alinhamento > 0,5 | 11 trades, 90,9 %, fator 12,4 |
| v23 | "convicção de elite" ≥ 95 | idêntico à base: 44 trades, 5,67 |

A conclusão de fato da escada, gravada pela própria v20: em todas as versões de v17 a v20, **a saída fixa de 15 minutos vence todas as saídas "físicas"** (dissipação, trailing, adaptativa). A física não acrescentava nada ao relógio. E 37 trades com 81 % de acerto em 90 dias, com limiares escolhidos olhando os mesmos 90 dias, é o retrato exato de uma vitória não conquistada: foi esse tipo de número que, dois meses depois, fez a casa reservar outubro e nunca olhar antes de registrar.

### O que sobreviveu, visto de outubro

1. **As variáveis.** E\_norm (preço contra a própria média móvel, em z robusto), jerk (segunda diferença) e a distância à memória (memory\_flux) são os três eixos do cubo, sem alteração. Sobreviveram a nove testes de direção e a dezenas de nulos como *descrição* do mercado.
2. **A cauda é outro objeto.** O lift 2,1 do criticality\_score (16/3) é o R borda/núcleo do campo de caudas (14/10) sem régua e sem nulo.
3. **A volatilidade tem memória.** A matriz de transição (11/3) é a vista grossa do que o v3 da memória e o MSM mediram em outubro.
4. **O nulo.** `teste_sgv_shuffle.py`, 6/3. A regra da casa não foi uma conversão tardia; estava no sexto dia, como um script entre duzentos.
5. **A auditoria.** O hash de 27/2 virou os `HASHES_*.txt` dos pré-registros congelados.

### O que morreu, e como

A crença de que o campo aponta. Em 16/3 os três modelos de direção já davam 46 % a 52 %; em 17/3 a saída fixa vencia a física em todas as versões. O SGV original tinha a resposta em março nos seus próprios CSVs; o que não tinha era a disciplina de acreditar nela em vez de abrir mais uma versão. Os defeitos recorrentes, todos corrigidos pelo método da casa a partir de agosto: quantis sobre a amostra inteira (limiar que só se conhece no fim); alvo construído com as mesmas variáveis do sinal; células de 1 a 3 trades viradas em "rota de ouro"; nenhum período guardado; nenhuma hipótese escrita antes dos dados; e o nulo, que existia, sem poder de veto.

**Registro.** Fonte: `sgv_runtime.zip` (parte 1 a 8), pasta `scripts/testes_sgv`, 408 arquivos. Esta seção foi escrita em 17/10/2026 e exportada para `docs/FASE_0_ORIGEM.md` no repositório.

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

## Fase 5 (16/10): a quarta dimensão vista, e o que ela não é

Um dia só, depois de fechar a revisão dos 98 ramos. Começou com uma pergunta simples da Ana ("por que virou um cubo?") e terminou com três confirmatórios novos congelados para outubro, três explorações lidas, cinco páginas visuais e dois erros de desenho reconhecidos por escrito. A ordem importa, porque cada passo saiu do anterior.

**1. Ver o hipercubo.** Depois de atualizar o navegador ("Navegador SGV hoje", `visual/navegador-estado-atual.html`: o cubo com campo, trajetória, casca, a temperatura σ̂ como cor e fatias, mais a tabela "navegador de 13/10 × hoje"), a Ana perguntou por que a quarta dimensão "não dá para desenhar". A resposta virou três páginas. "Hipercubo SGV" (`hipercubo-sgv.html`) projeta o objeto 4D com perspectiva: em 0° é o cubo de ontem com uma sombra atrás; girando, σ̂ troca de lugar com um eixo visível e a nuvem se organiza, calma de um lado, quente do outro. "Cubo versus hipercubo" (`cubo-vs-hipercubo.html`) põe os dois lado a lado girando juntos. "Fatia 4D do SGV" (`fatia-4d-sgv.html`) faz o que o Miegakure e o 4D Toys fazem: corta em vez de projetar, e andar pela temperatura mostra só os minutos daquela fatia, sem deformação. Os pontos dessas páginas são simulados com a receita do sintético M, e isso está escrito nelas: servem para treinar o olho, não para concluir. O que a Ana viu e descreveu ("as linhas saem da tela e a nuvem fica no centro") era a leitura certa: a perspectiva na direção que a tela não tem, e o mercado morando perto da origem em qualquer número de eixos.

**2. O corte reformulou dois testes.** A rodada de fatias por tercis perguntava "as três fatias colapsam?"; o corte contínuo mostrou que a pergunta certa é "como a forma da fatia varia com σ̂?" (uma curva, não três números), e que a nuvem 4D pode estar inclinada (σ̂ parcialmente projetado sobre um eixo do cubo, o que explicaria por que ela ficou escondida no original). Virou o **H-4D-01**, pré-registrado antes do código, rodado em jun–jul e ago–set como paridade, emendado e congelado (d1f48d0). Nos meses abertos: a forma da fatia muda com a temperatura **menos** no real do que no M (ρ\_forma +0,14 e +0,10 contra 0,38–0,42 e 0,20–0,47); a inclinação linear é quase zero por simetria (E\_norm e jerk têm sinal), e o entrelaçamento está nos termos pares (R² quadrático 0,25–0,29). O critério linear ficou registrado como fraco; não se conserta depois de ver os dados.

**3. A temperatura não está compactada; está projetada e borrada.** A Ana perguntou se a volatilidade era uma dimensão "compactada" no sentido de Kaluza–Klein. Não: ela varia tanto quanto os outros eixos. O que a escondia do cubo eram duas coisas medidas: ela entra por termos pares (infla a nuvem para todos os lados, sem direção) e é latente (nenhum minuto traz a própria temperatura; só a janela traz), o que a torna uma temperatura no sentido da termodinâmica. O que parece compacto, na faixa de densidade da página de fatias, é ocupação: o mercado passa quase todo o tempo morno.

**4. Invariância de escala: em amplitude sim, no tempo não.** A Ana leu o colapso como fractal ("o mesmo caroço em tamanhos diferentes"). A distinção: o colapso é invariância na **amplitude** (fixado σ̂, o mesmo objeto); fractal é invariância no **tempo** (o mesmo objeto em 1, 5, 15 min). A segunda foi testada na exploração de **auto-similaridade temporal**: o cubo refeito em 5 e 15 min, com o mesmo instrumento em barras. Resultado estável nos dois períodos: o colapso sobrevive ao relógio (C 0,70–0,93 nas três resoluções), mas a borda agitada é um objeto de 1 minuto (R 6,8 → 5,5 → 4,6 e 6,5 → 6,0 → 2,4). A frase que ficou: *o cubo do SGV é um instrumento de 1 minuto com uma quarta dimensão que vale em qualquer minuto.* A página "Cubo por resolução" (`cubo-por-resolucao.html`) é a primeira em que a figura e o número medido estão na mesma tela: três cubos com os anéis do campo marcados pelo R do BTC, e os gráficos de R e C por resolução. De brinde, uma limitação do M apareceu: em 1 min de ago–set ele deu R 12–15, o dobro do real, por causa do teto de calibração da escala rápida.

**5. Dois testes que saíram da página.** Olhando o cubo de 15 min com o anel ×10 vazio, a leitura foi: se a borda some ao somar, ela é feita de minutos que se cancelam, isto é, saltos seguidos de reversão parcial (o "bounce" da microestrutura). E a pergunta da Ana sobre leis de potência na memória pedia um teste próprio. Os dois viraram o **H-TEMPO-01** (congelado em 574363d, na tarefa de 3/11): (a) a autocorrelação de |r| de 1 min a 1 dia é mais reta em log-log que a do M? (b) a borda reverte mais que o núcleo, além do M? Nos meses abertos, nenhum dos dois repetiu: (a) passou por 0,008 em jun–jul e ficou dentro do M em ago–set; (b) em jun–jul a borda reverteu de verdade (φ −0,023 contra +0,019 do núcleo, M todo acima) e em ago–set sumiu. Apostas revistas para 20 % e 30 %.

**6. O erro no (a), e as três rodadas para consertá-lo.** Ao ler jun–jul ficou claro que o pré-registro do (a) tinha uma premissa errada: o M não é "duas exponenciais por construção", porque sua escala lenta é o caminho real suavizado, então ele herda a memória longa do real e também parece lei de potência. Ficou na Emenda 1, sem mexer no critério. O teste certo foi feito à parte, como exploração **memória em lei de potência**, com um sintético E2 de escala lenta ajustada, e precisou de três versões: a v1 (até 1 dia) deu "potência" no real mas o E2 reprovou a validação em ago–set; a v2 (até 5 dias) reprovou nos três períodos e mostrou dois defeitos meus, a grade pisando nos múltiplos de um dia e a divisão por s(h) imprimindo o ciclo diário nos sintéticos, mais o E2 re-ancorado no real toda semana; a v3, com grade limpa, dessazonalização por diferença, E2 gerado de uma vez e 10 réplicas, validou 30 de 30 e deu o veredito **estável: duas exponenciais**, θ₁ de 10–50 min e θ₂ de 1–3 dias, com ΔAIC de +34 a +58 contra a reta até 4,5 dias. O β ≈ 0,15 da v1 era o ajuste de uma reta a uma curva que, vista até 5 dias, dobra. Foi a minha aposta de menor probabilidade (15 %), e por isso está registrada com as outras.

**7. O que isso muda no painel.** Nada de histórico longo. As escalas que importam cabem em dias: a âncora de maio (fixa), duas semanas rolantes de aquecimento e o fluxo ao vivo. A falta de auto-similaridade no tempo é o que permite o painel ser pequeno; a invariância em amplitude é o que permite um só objeto com um botão de zoom. Se o cubo fosse invariante nas duas, seria bonito e inviável.

**Registro.** Ramos `confirmatorio/H-4D-01`, `confirmatorio/H-TEMPO-01`, `exploracao/autosimilaridade-temporal`, `exploracao/memoria-potencia` (v1, v2 e v3 no mesmo ramo) e `visual/hipercubo-4d` (as cinco páginas em `visual/` e este documento exportado em `docs/`). A tarefa de 3/11 passou de dois para sete julgamentos. Nada de outubro foi lido.

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
| Memória em lei de potência v1 e v2 (16/10) | Entre 1 min e 1 dia (v1) ou 5 dias (v2), a memória de \|r\| é lei de potência ou duas exponenciais? | **NÃO ESTÁVEL (v1) e INCONCLUSIVO (v2)**: o instrumento reprovou. Defeitos reconhecidos: grade nos múltiplos de 1 dia, divisão por s(h) imprimindo o ciclo nos sintéticos, E2 re-ancorado no real toda semana |
| Memória em lei de potência v3 (16/10) | ...corrigidos os três defeitos, até 4,5 dias, jun–set agrupado? | **DUAS EXPONENCIAIS, estável.** E2 valida 30/30; real 2exp nos três períodos (ΔAIC +34 a +58 até 4,5 d), θ₁ 10–50 min, θ₂ 1–3 dias. Até 1,5 dia a reta ainda ganha: a "potência" da v1 era a janela curta. O real tem mais memória que o E2 em todos os atrasos (descola em 1 min); a forma é de poucas escalas, as constantes do E2 não são as do real |
| Assimetria da nuvem (16/10, uma tentativa) | A nuvem do cubo é torta (terceiro momento em E\_norm, jerk, memory\_flux), relativo ao M? A casca HDR50 é simétrica por construção e não responde. | **Simétrica dentro do ruído** nos três eixos, dois períodos. Duas excursões "torta sem lado" (jerk em jun–jul, memory\_flux em ago–set) não repetem no mesmo eixo. p⁺ na borda 0,46–0,57, sem lado; nuvem quente não é mais torta. Correção de leitura registrada: os três eixos têm sinal (E\_norm = preço vs. EMA). Não testa direção; ramo exploracao/assimetria-nuvem @415d8c6 |
| Multifractal ζ(q) (16/10) | A concavidade κ = 2ζ(2) − ζ(4) dos retornos agregados (1 min a 4 h) excede a do M e a da série embaralhada? | **Monofractal dentro do ruído** (classe registrada), dois períodos: κ real 0,24/0,23, embaralhado 0,29–0,58, M −0,15 a +0,30. Defeito de desenho registrado: caudas gordas i.i.d. bastam para ζ(q) côncava (TCL), então κ mede cauda, não cascata; o agrupamento reduz a concavidade. Aposta de 90 % errada. H ≈ 0,49. Ramo exploracao/multifractal @3f738c5 |
| Multifractal v2 (16/10) | Cascata ou cauda? κ₁ = 2ζ(1) − ζ(2) dos retornos brutos, e espectro de z = r/σ̂ causal (HAR 10/60/240) contra o z embaralhado. | **Sem cascata além da cauda; σ̂ absorve a cascata**, dois períodos. O espectro de z é indistinguível do de z embaralhado (κ₁(z) 0,03 dentro de 0,03–0,05; κ(z) 0,26–0,28 dentro/abaixo). Segundo defeito registrado: κ₁ também é positivo para i.i.d. de cauda gorda (previsão de sinal errada). Leitura final: concavidade estável (κ ≈ 0,23), explicada por cauda gorda + σ̂ de três escalas; sem hierarquia residual. Sem v3. @13f0771 |
| MSM, k = 1…4 (16–17/10) | Quantas componentes de volatilidade (Calvet–Fisher, inovação Student-t) o BTC de 1 min pede, por BIC, com validação em sintéticos de k = 2 e 3? | **Muitas escalas (≥ 4)**, dois períodos, instrumento validado (k = 2 e 3 recuperados). Escada geométrica ×≈10: 7–9 min · 1–1,5 h · 10–16 h · 4–7,5 d; ganho de BIC ainda grande no 4º degrau (fronteira). Contraria a aposta principal (55 % em 2–3). Não contradiz o v3: duas exponenciais são a vista grossa da escada. Correção registrada: o M herda a escada lenta real (não é "duas escalas"). v1 INCONCLUSIVA (escala da t), Emenda 2 (validação com escalas separadas). Ramo exploracao/msm @29d1f29 |
| MSM v3, ciclo diário removido (17/10) | Dessazonalizando por variância diária (âncora maio), k = 1…5: a escada fica de pé ou cai para três? | **INCONCLUSIVO**: ago–set não admite ajuste regular (m₀ no teto / ν no piso). Observação em jun–jul (validado): k\* = 5, escalas 4,7 min · 42 min · 6,9 h · 2,9 d · 28 d; o degrau intermediário saiu de 16 h para 6,9 h sem o ganho do 4º degrau cair. Três defeitos de desenho registrados. @1b1df3c |
| MSM v4, relógio de volume (17/10) | Em barras de volume igual (\~26 mil barras por período), a escada encolhe? | **INCONCLUSIVO**: validação reprovou duas vezes (amostra curta não resolve k ≥ 3). Descritivo sem veredito: a cauda afina muito no relógio de volume (ν 6,3 → 10,9 e 2,75 → 12,9), como Clark/Ané–Geman preveem. Precisa de barras abaixo do piso de 1 min. @1b1df3c |
| MSM v5, volume na observação (17/10) | r = σ̄ (v/v̄)^δ (ΠM)^½ ε no tempo cronológico: quantas escalas sobram depois que o volume do minuto absorve o que é dele? | **Sem veredito** (só um período lêdo). Jun–jul, validado: hierarquia própria, k\* = 4 com δ̂ 0,47 e ν̂ 33,6 (o volume absorve a cauda, não a escada: 15 min · 3 h · 1,8 d · 23 d). Ago–set INCONCLUSIVO: ajuste degenerado (m₀ no teto, ν no piso), terceira vez neste período; hipótese registrada: retornos exatamente nulos. Próximo instrumento precisa tratar o zero. @f755f34 |

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

**Painel de replay 4D** (ramo `painel/replay-4d`, 16/10). O painel alternativo nasceu do que a Fase 5 fechou: instrumento de 1 minuto, quarta dimensão por cortes, sem direção, nula ao lado, duas semanas rolantes mais a âncora de maio. Está em modo **replay** sobre maio–setembro (exportador sobre o pipeline, servidor REST mínimo, página de replay). O serviço **ao vivo** está escrito e **desligado**: obedece `painel/LIBERACAO.json`, recusa partir com a chave fechada, e só aceita candles dentro das janelas que a Ana liberar. Decisões que ficam com ela: em 3/11, liberar outubro (julgado) e marcar `ao_vivo_desde` para 1/12; e, antes de ligar, testar o caminho de rede da Binance, que não foi testado em 16/10.

### O que o Claude recomendaria, se perguntado

1. Esperar 3/11 sem abrir nada novo em BTC. Quatro hipóteses no mesmo mês já é muita coisa para julgar bem.
2. Depois do julgamento, escrever a leitura conjunta: agitação + saltos + volatilidade multiescala é uma descrição coerente do campo; se H-VOL-01 passar, ela está fechada em dado novo.
3. Só então decidir entre o teste do fluxo e C03. Os dois são explorações; não há pressa.

### Onde está cada coisa

- Repositório: `ana-rigel/sgv-geometria`, um ramo por estudo.
- Documento técnico de C02.1: "Campo informacional do SGV", rev 25.
- Tarefa agendada de 3/11: "Julgamentos de outubro/2026: H-DIF-01 e H-VOL-01".
- Este documento: a trajetória, para reler quando a pergunta voltar a ser "o que a geometria é".
