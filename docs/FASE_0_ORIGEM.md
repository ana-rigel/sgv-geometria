# SGV, Fase 0 (27/2 a 17/3/2026): a origem

Trecho do documento "SGV: a trajetória da pesquisa" (rev 29, 17/10/2026). Reconstruído a partir de `sgv_runtime.zip`, pasta `scripts/testes_sgv`.

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

