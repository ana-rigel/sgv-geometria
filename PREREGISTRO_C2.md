# Pré-registro — Reformulação C2: geometria do estado preço–fluxo

**Registrado em 09/10/2026, antes de qualquer cálculo com as novas coordenadas em dado real.** Este documento é a **única reformulação** que o `PLANO.md` permite depois da reprovação do G1 com as coordenadas do legado (C1). Se o G1 também reprovar aqui, **a linha geométrica do SGV se encerra**, sem novas reformulações.

## 1. Por que reformular assim

As três coordenadas de C1 (E = v²+a², jerk, memory_flux) são todas derivadas do preço. A geometria delas é, por construção, quase toda volatilidade, e foi isso que o G1 encontrou: não houve diferença contra GARCH.

C2 troca o espaço de estados por um que contém informação que o preço sozinho não tem: **o fluxo de ordens agressoras e a atividade**, ambos presentes nos klines que já foram baixados (colunas `taker_buy_base` e `volume`). A hipótese passa a ser sobre a geometria da relação entre preço e fluxo. Em linguagem de microestrutura, é a geometria da formação de preço.

## 2. Coordenadas C2 (por barra t, todas conhecidas no fechamento de t)

| | Definição | Leitura |
| --- | --- | --- |
| x₁ | r_t = log(close_t / close_{t−1}) | movimento do preço, **com sinal** |
| x₂ | ι_t = 2·taker_buy_base_t / volume_t − 1, em [−1, 1] (0 se volume = 0) | desequilíbrio do fluxo agressor |
| x₃ | ℓ_t = log(volume_t) | atividade |

Escala: gaussianização causal por postos (janela das 1.500 barras anteriores), igual a C1.

## 3. O que não muda em relação a C1

- Métrica de Fisher local (F), referência gaussiana (Fref) e grandeza **ΔF = slog R(F) − slog R(Fref)**.
- Janela de ajuste de 1.500 barras, com reajuste a cada 60.
- Largura de banda: o menor múltiplo de Scott, entre 2× e 4×, com confiabilidade de ΔF ≥ 0,8 em D7.
- Dados: os mesmos períodos de exploração travados em 08/10/2026 (1m: mai–jul/2026; 1h: 2020–2024).
- Janelas de cada diagnóstico:
    - D7: período inteiro, 240 barras sorteadas.
    - D4 e D5: as últimas 6.000 barras.
    - D8: as últimas 4.500 barras.
- Controles de volatilidade de D5 (volatilidade realizada de 10, 30 e 60 barras, |v| e |a|).
- Os critérios 1, 2 e 4 do G1 e seus limiares.

## 4. Nulo novo para o critério 3: "GARCH + lei de impacto estacionária"

O nulo de C1 só gerava preço. Para C2, o nulo precisa gerar preço **e** fluxo, reproduzindo tudo o que já é conhecido e banal:

- volatilidade agrupada e caudas pesadas;
- a relação estática entre o tamanho e o sinal do movimento e o fluxo (curva de impacto);
- a relação entre volatilidade e atividade;
- a sazonalidade intradiária do fluxo.

Construção, refeita em cada segmento analisado:

1. Ajustar um GARCH(1,1)-t aos retornos do segmento. Filtrar σ_t e calcular z_t = r_t / σ_t.
2. Dividir as barras reais em células: 10 faixas de z (quantis), 3 faixas de log σ (tercis) e 6 blocos de 4 horas do dia (UTC). Se uma célula tiver menos de 5 barras, usar só z × σ; se ainda faltar, só z.
3. Cada réplica:
    1. Simular r* e σ* com o GARCH ajustado (semente própria) e calcular z* = r*/σ*.
    2. A barra simulada i herda o horário da barra real i.
    3. Sortear, entre as barras reais da mesma célula, um par (ι, ℓ) para a barra simulada.
    4. Montar o OHLCV com volume = e^ℓ e taker_buy_base = (ι + 1)/2 · volume.

O que este nulo **destrói**: qualquer mudança no tempo da relação preço–fluxo que não seja explicada pela volatilidade, pelo horário e pelo próprio movimento. Rejeitar o nulo significa que a forma local da distribuição conjunta preço–fluxo muda de um jeito que a volatilidade não explica. Essa é a "geometria própria" que interessa.

## 5. Estatística primária do critério 3 (muda, com motivo declarado)

O nulo preserva, por construção, a distribuição conjunta estática. Por isso a média de ΔF, que foi a estatística de C1, tenderia a coincidir com o nulo quase por definição e não testaria nada. A estatística primária passa a ser a **variabilidade temporal da geometria**:

> **S = desvio-padrão, entre os blocos de reajuste (60 barras), da média de ΔF no bloco.**

O critério 3 passa se S do BTC diferir do nulo com **p ≤ 0,05**, usando 39 réplicas e p-valor por postos bilateral (o mesmo cálculo do D8). A média de ΔF é reportada como secundária e não decide.

## 6. Portão G1-C2

| Critério | Regra |
| --- | --- |
| 1. Mensurável (D7) | confiabilidade de ΔF ≥ 0,8 na largura escolhida |
| 2. Além da posição (D4) | \|ρ(ΔF, distância de Mahalanobis)\| < 0,5 |
| 3. Existe (D8-C2) | S ≠ nulo "GARCH + lei de impacto", p ≤ 0,05 (39 réplicas) |
| 4. Além da volatilidade (D5) | R² de ΔF pela volatilidade ≤ 0,5 |

O G1-C2 passa numa escala de tempo (1m ou 1h) se os quatro critérios passarem nela. Se passar em ao menos uma, a linha segue para a Fase 2 (pré-registro preditivo) nessa escala. Se não passar em nenhuma, **a linha geométrica se encerra**.

## 7. Calibração antes do dado real (sem tocar o BTC)

Antes de rodar no BTC, o mesmo procedimento roda em duas séries sintéticas com fluxo, de semente fixa:

- **(a) Sem geometria própria:** GARCH-t, com ι = tanh(0,8·z + 0,6·u) e ℓ = 2 + log(σ/σ̃) + 0,35·|z| + 0,4·w, sendo u e w ruídos independentes. O resultado exigido é que o critério 3 **não rejeite**.
- **(b) Com geometria plantada:** a mesma série, mas com um regime oculto de Markov (permanência de 0,998, independente da volatilidade). O regime troca a curva de impacto (0,8·z vira 1,4·z ou 0,2·z) e acopla ι e ℓ (ℓ += 0,5·ι no regime 1). O resultado desejado é que o critério 3 **rejeite**, mostrando que o teste tem poder.

**Emendas permitidas**, só antes da primeira rodada em dado real e registradas abaixo com o motivo:

- o tamanho do bloco de S;
- o esquema de células do nulo.

Se (a) rejeitar (falso positivo), o nulo ou a estatística são corrigidos. Se (b) não rejeitar, o teste é declarado sem poder para esse tipo de estrutura: isso fica registrado, e a rodada real acontece mesmo assim, com essa ressalva.

## 8. Quem paga e por que continua pagando?

**Ainda não se aplica:** o G1 é um teste de existência estrutural, não de lucro.

**Hipótese provisória**, a ser cobrada na Fase 2: se a geometria preço–fluxo tiver conteúdo próprio, ela reflete a composição do fluxo, ou seja, episódios em que o fluxo agressor carrega informação contra episódios de fluxo de liquidez. Quem pagaria é o fluxo de liquidez desinformado e impaciente. Ele continuaria pagando porque sua necessidade de executar é pouco sensível a preço. Esta resposta fica registrada como fraca até a Fase 2.

## 9. Aposta do Claude (registrada antes dos dados)

| Desfecho | Probabilidade |
| --- | --- |
| G1-C2 passa em pelo menos uma escala | ~25% |
| G1-C2 passa nas duas escalas | ~10% |

Raciocínio: o fluxo agressor tem estrutura de regime conhecida na literatura (episódios informados, liquidações), o que favorece o critério 3. Mas ℓ (atividade) é muito ligada à volatilidade, o que ameaça o critério 4, e o histórico do projeto é de zero sobreviventes prospectivos.

## 10. Emendas

*(nenhuma até o momento)*
