# SGV-M13 — Calibração de falsas excedências e adequação dos nulos (pré-registro)

**Data:** 09/10/2026. **Base científica:** \`reports/SGV_REFERENCIA_CIENTIFICA_M1_M12_20261009.md\`. **Ramo:** \`research/m13-calibracao-alarmes-regimes\`; \`main\` intocada.

## Pergunta
Quantas falsas excedências a distância M11 produziria sob um mecanismo **conhecidamente estável**? E, em dados BTC exploratórios, como os postos e a adequação das quatro famílias temporais mudam quando usamos mais replicações de referência?

## Separação obrigatória de duas avaliações

### A. Calibração sob verdade geradora conhecida
Gerar trajetórias estacionárias **independentes e permutáveis por realização** sob dois geradores 3D conhecidos:
1. VAR(1) gaussiano com correlação contemporânea entre z, iota e nu e memória em nu;
2. regimes binários de Markov persistentes com diferentes médias/escala de ruído, mesmos parâmetros entre realizações.

Em cada gerador e trial, sortear 1 trajetória independente como "observada" e 19 trajetórias sintéticas independentes como referências, todas com 1500 candles (1m sintético) e **os mesmos parâmetros**. Em cada trajetória, reconstruir ambas cascas HDR50 com **GMM2 reestimada** e transformação marginal ancorada ao 30% inicial. Calcular exatamente o mesmo instrumento M11 de distância à superfície triangular (512 pontos). Tratar falhas explícitas e **não substituir** distância inválida. Usar no mínimo 6 trials por gerador, 19 controles por trial. A baixa amostra de trials constitui prova de execução e diagnóstico; não afirmaremos taxa de falso positivo com precisão, e não garantiremos uniformidade geral.

Para cada trial com todas as 20 geometrias válidas, calcular o posto de Monte Carlo unilateral conservador:
\`p_rank = (1 + sum(d_nulo >= d_observada)) / (R + 1)\`, R=19.
Sob amostras IID/exchangeable do mesmo gerador **conhecido**, esse posto é válido como p-value conservador para aquele gerador, mesmo após reestimar GMM. Ele não se transporta automaticamente a nulos com parâmetros estimados em um prefixo histórico real. Calcular contagem com \`p_rank <= 0.05\` apenas para os trials sintéticos e intervalo de Wilson 95% descritivo. Resultado com zero alarmes em 6 trials **não comprova taxa menor que 5%**. Empates contam como \`>=\` (conservador).

Como checagem barata e separada, validar 1000 trials de ranking com escalares IID gaussianos; não confundir essa validação algébrica de postos com calibração geométrica.

### B. BTC real — diagnósticos de nulos ajustados
Três origens cronológicas disjuntas, contínuas e escolhidas por índice dentre as elegíveis, por timeframe: BTCUSDT spot 1m (05–07/2026) e 1h (2020–2024), prefixos 5000/3500 e janela 1500/1008. Mesmos quatro controles pré-existentes N0/N1/N2/N3 de M12, ajustados **exclusivamente ao prefixo**, com 19 trajetórias por nulo por origem. Reportar erro temporal ACF(nu,1/10), ACF(|z|,1), std(nu), corr(iota,nu), perfil 6h e também quantis extremos/desvio de cauda ν; duração de regime **não será inferida de um nulo que não foi validado nesse atributo**.

Distância observada HDR50 medida com instrumento M11, comparada ao conjunto de distâncias dos controles com rank \`p_rank\`. **NÃO chamar p_rank calculado após fit real de p-value calibrado do BTC** e NÃO sinalizar teste confirmatório. Com quatro famílias e duas escalas, 19 referências não permitem sequer resolver limiares de Bonferroni ~0.00625; reportar exclusivamente **ranks descritivos** e limites de calibração.

Critérios instrumentais: todos os modelos devem registrar >=19 trajetórias válidas para o posto; nenhum fallback silencioso. Simulações preservam a escala temporal e as regras do projeto. A soma de simulações não substitui o número de origens independentes.

## Portas de engenharia
- Testes de \`rank_pvalue\` para posição extrema, empate, erro de amostra insuficiente; ausência de "valor p" no BTC.
- Teste de dois geradores independentes, fit GMM2 real, destino e gates de geometria; cálculos sintéticos de recuperação de estado.
- Arquivos BTC por downloader allowlist/SHA-256; exclusão de meses confirmatórios explícita. Nunca ler \`main\` para escrita nem abrir holdouts.
- GitHub Actions: primeiro testes e calibração sintética, depois replays BTC em jobs separados; publicar JSON/CSV com IDs de origem e motivos de invalidez.
- Valores de p_rank passam de nulo descritivo para inferência de tipo I **somente** quando o gerador sintético é conhecido e as 20 trajetórias são permutáveis. Fora disso, mantenha rótulo descritivo.

## Decisão após execução
Se o mecanismo sob verdade conhecida reproduzir a propriedade de posto nos testes, o **método de calibração** estará implementado, ainda que sem poder para medir erro tipo I precisamente. Se adequação temporal real for fraca ou contraditória, não declarar mudança estatisticamente extraordinária da forma. Priorizar maior N, validação de nulos com regimes de duração/cauda e subsequente plano confirmatório pré-congelado.
