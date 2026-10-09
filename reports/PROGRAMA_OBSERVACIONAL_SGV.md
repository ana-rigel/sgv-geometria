# SGV — Programa observacional: fotografia de estados e geometria dos fluxos

**Data:** 09/10/2026 · **Status:** novo objetivo científico, independente dos pré-registros preditivos já julgados.

## Pergunta

É possível representar de modo matematicamente definido, consistente e causal o **estado das informações públicas disponíveis no mercado no instante t** por uma geometria estatística? Uma vez obtida essa representação, é possível estudar como ela muda no tempo?

**Não** exigimos que supere GARCH, HAR, preço ou volatilidade para ser considerada uma representação fiel. Comparações preditivas só terão lugar se uma hipótese preditiva separada for proposta mais tarde.

## 1. Definir exatamente o observável

A primeira projeção usa apenas as informações conhecidas após o fechamento de um candle BTCUSDT spot:

- z = retorno log de 1 candle / volatilidade histórica anterior de 60 candles;
- iota = 2*taker_buy_base/volume_base-1;
- nu = log(volume_base) - mediana histórica anterior de 1500 candles.

X_t = (z_t, iota_t, nu_t). Não contém livro de ordens, cancelamentos, open interest, funding, intenções dos participantes ou informação privada.

Qualquer alegação sobre a informação TOTAL do mercado seria indevida: mede-se somente a informação projetada em X_t. A resolução presente é **candle fechado**; não é fluxo de eventos tick-by-tick.

## 2. O retrato geométrico

Em uma janela passada causal de W observações, ajusta-se uma aproximação gaussiana N(mu_t, Sigma_t). Para a família de translações mantendo Sigma fixa, a informação de Fisher é:

    g_t = Sigma_t^{-1}

Este é o significado estrito de `fisher_location`. É distinto da curvatura local ΔF dos experimentos C1/R1 e da curvatura geodésica da trajetória FR-EWMA. A matriz de covariância Sigma é positiva definida nas janelas válidas.

A aproximação de duas distribuições consecutivas é quantificada com distância de Bhattacharyya. A representação armazena mu, Sigma, correlações, condicionamento, logdet e distância a uma janela não sobreposta. **Atenção:** g e as distâncias são funções das estatísticas observadas e não contêm informação milagrosa ou necessariamente extra.

A futura geometria do **espaço das distribuições gaussianas completas** pode ser abordada pela métrica:

    ds² = dmuᵀ Sigma⁻¹ dmu + 1/2 tr(Sigma⁻¹ dSigma Sigma⁻¹ dSigma).

Ela só será interpretada dinamicamente após comprovar reprodutibilidade, erro amostral e estabilidade das fotografias. Curvatura da trajetória é etapa posterior, não pré-requisito.

## 3. Validação correta de um instrumento de observação

- **Causalidade:** a saída do instante t não muda ao acrescentar dados de t+1 em diante; timestamp de disponibilidade é o fechamento da última barra, nunca sua abertura.
- **Casos conhecidos:** simulações com relações preço/fluxo invertidas e marginais semelhantes devem gerar fotografias distinguíveis.
- **Fidelidade interna:** a métrica deve satisfazer Sigma*g = I (erro de ponto flutuante); distâncias de distribuição iguais devem ser nulas; invariância sob a mesma transformação afim nas duas distribuições.
- **Reprodutibilidade amostral:** metades pares/ímpares devem retratar estados semelhantes, com incertezas adequadas ao W; confiabilidade alta sozinha não prova que a estimativa acompanha mudanças efetivas.
- **Falhas declaradas:** dado faltante, gaps, matrizes degeneradas e não linearidades ignoradas pela gaussianidade.
- **Atualidade:** medir latência processamento+publicação sob streaming real; o replay histórico causal NÃO é ainda um monitor online.
- **Sensibilidade e especificidade:** medir identificação de mudanças sintéticas sob nulos estacionários e heterocedásticos; determinar resolução mínima sem superajuste.

O protótipo atual grava fotografias amostradas a cada 60 candles 1m e a cada 24 candles 1h. Essa cadência reduz custo na primeira auditoria histórica; não deve ser chamada de atualização contínua.

## 4. O que seria estudar o fluxo de informação

Após as fotos terem validade observacional:

1. Descrever trajetórias t -> (mu_t, Sigma_t) e distâncias sucessivas em múltiplas escalas, com bandas de incerteza por reamostragem.
2. Comparar fotografias onde volatilidade e volume são similares mas relações condicionais preço/fluxo diferem; isso mede organização, não previsão.
3. Acrescentar séries de *trade prints*, spread, profundidade, cancelamentos, open interest e funding, cada uma com timestamp de **disponibilidade**, se houver fontes históricas/live confiáveis.
4. Estudar orientação temporal da dependência usando defasagens e modelos condicionais. Contemporaneidade e taker imbalance NÃO demonstram transmissão causal de informação.
5. Verificar se a representação preserva estruturas lineares e não lineares, usando testes de transformação, permutação condicionada e casos ocultos plantados. Generalização a ativos e regimes diferentes é avaliação independente.

## 5. Relação com hipóteses negativas anteriores

O G1 de C1/R1 testava unicidade da curvatura comparada a modelos estilizados e falhou. FR-EWMA testava incremento preditivo de κ e falhou. Essas falhas NÃO demonstram que uma distribuição estimada não represente fielmente os dados; mostram apenas que as proposições originais não foram sustentadas. A fotografia observacional é um problema novo, com critérios adequados a um instrumento de observação.

**Sem novo pré-registro confirmatório preditivo, sem carregar os períodos reservados e sem modificar o histórico de resultados.**
