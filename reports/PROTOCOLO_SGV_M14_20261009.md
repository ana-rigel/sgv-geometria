# SGV-M14 — Calibração aninhada da distância geométrica sob nulos estimados

**Pré-registro: 09/10/2026.** Referência: \`reports/SGV_REFERENCIA_CIENTIFICA_M1_M12_20261009.md\` e \`reports/PROTOCOLO_SGV_M13_20261009.md\`.  
**Ramo:** \`research/m14-calibracao-aninhada-nulos\`; nenhuma alteração em \`main\`; **proibida leitura dos períodos confirmatórios BTC**. M14 utiliza **somente dados sintéticos**, nenhum BTC sequer exploratório.

## Questão e correção do M13

O M13 parte A utilizou observação e referências produzidas pelos parâmetros verdadeiros conhecidos. A permutabilidade daí resultante valida a regra de posto **sob oracle**, mas não mede o erro de estimação de parâmetros na vida real. Na parte BTC, nulos N0–N3 ajustados ao prefixo em geral NÃO produzem trajetórias permutáveis com a observação. O M14 mede a taxa de ultrapassagens **do pipeline completo**, de gerar prefixo, ajustar família, simular controle e reconstruir a geometria, sob verdades sintéticas estáveis conhecidas.

## Cenários congelados, sem pós-seleção

| Código | Verdade geradora conhecida | Família de ajuste (prefixo somente) | Objetivo |
|---|---|---|---|
| VAR_fit | VAR(1) gaussiano estável 3D | VAR(1) gaussiano 3D estimado OLS/Σ | Erro por estimação sob família correta |
| HMM_fit | Markov 2 estados, emissões gaussianas 3D independentes condicionalmente ao estado | GaussianHMM 2 estados, covariâncias completas, EM com inicializações fixadas | Erro por estimação/local ótimo sob família correta |
| HMM_to_VAR | Mesmo Markov 2 estados | VAR(1) gaussiano OLS/Σ | Inadequação de regimes sob nulo sem regimes |
| HMM_to_blocks | Mesmo Markov 2 estados | Blocos circulares multivariados curtos do prefixo (L=15) | Sensibilidade a nulo não paramétrico sem durações longas |

A verdade HMM é um processo **estacionário** com regime oculto de Markov persistente, mas nenhuma mudança na lei geradora entre prefixo e janela observada. "Alarme falso" vale estritamente contra a hipótese de *estabilidade da lei geradora*; no caso mal especificado é uma **excedência por inadequação**, não erro tipo I de um nulo matemático falso.

## Cada ensaio externo (unidade estatística independente)

1. Simular, de parâmetros verdadeiros **fixados antes do ensaio**, uma trajetória contínua com prefixo de 2000 e janela de avaliação de 1500 triplas \`(z,iota,nu)\`. Não são barras BTC: scores sintéticos abstratos e não dados de mercado.
2. Ajustar VAR/HMM ou catálogo de blocos **exclusivamente às primeiras 2000 observações**. Nenhuma coordenada futura participa do ajuste.
3. Simular R=19 janelas independentes de 1500 com o **nulo estimado**. Simulação paramétrica produz trajetória estacionária incondicional da família estimada; no mesmo desenho o verdadeiro observável vem de prefixo contínuo (condicionado à sua última história), **portanto a inicialização condicional versus estacionária é uma fonte explícita de descalibração medida neste protocolo**.
4. Medir em observada e em cada referência o exato instrumento M11: transformação de âncora histórica \`split_historical\`, GMM2 ajustada separadamente às metades, HDR50 malhas 35³, ICP multistart, quadratura determinística 512 e distância direta a triângulos. **Não simplificar a medição nas etapas principais.**
5. Calcular posto \`p_rank=(1+#(D_ref>=D_obs))/20\`; "alarme" quando \`p_rank<=0.05\`. Esse número, com parâmetros estimados, é somente **estatística ranqueada** até ser validado em repetições aninhadas.
6. Falhas de convergência/HDR são registradas com contagem e motivo; ensaio com menos de 19 referências válidas **não é elegível para avaliar posto**. Não eliminar ensaios silenciosamente nem substituir por números.
7. Repetir **500 ensaios externos independentes por cenário**, distribuídos em 20 shards × 25 ensaios por cenário. Monte Carlo 19 controles + 1 observação → ~40.000 avaliações da geometria HDR de M11 nos quatro cenários, além de calibração.
8. O relatório agregador deve contabilizar resultados de todos os shards, garantir que cada ID foi produzido uma única vez e reportar taxa de alarme como \`n_alarm/n_valid\`, intervalo Wilson bilateral 95%, \`n_invalid\`, \`n_requested=500\`, e limites por piores casos de falha \`[n_alarm/500,(n_alarm+n_invalid)/500]\`. Nunca chamar taxa de 0/500 evidência exata sem intervalo.

## Portão inicial de engenharia (pipeline separado)

Executar um **piloto pequeno com 2 ensaios por cenário** para validar fitting, seed, geometria e arquivos. A etapa de 500 ensaios somente deve iniciar se todos os testes e 8 pilotos tiverem gerado resultados elegíveis, com convergência e métricas finitas. Se piloto não passar, **não** iniciar a bateria grande nem alterar os critérios estatísticos de forma oportunista; corrigir bug instrumental e registrar commit.

## Modelos e limites

- VAR(1) 3D com covariância conjunta positiva definida, intercepto e matriz de transição; OLS no prefixo e estabilidade espectral auditada (não ajustar em observada).
- HMM 2 estados 3D com covariâncias completas, estados não identificados por rótulo (permuta admissível); algoritmo EM tem máximos locais, reinicializações determinísticas fixas, parâmetros regulares e falhas explícitas de convergência.
- Nulo por blocos usa apenas linhas multivariadas do prefixo e quebra durações de regime maiores que 15.
- Não escolher a família pelo desempenho nas trajetórias observadas; usar a tabela cruzada de cenários pré-registrados.
- **Erro amostral da taxa:** em 500 ensaios independentes, p=0.05 dá SE≈0.00975 e margem normal 95%≈±1.9 pontos percentuais. Wilson é o intervalo publicado.
- Esse protocolo não identifica relação de preço e fluxo, causalidade, tensão física/financeira, ganho de trading ou curvatura Fisher–Rao intrínseca. Nulo rejeitado = **mecanismo insuficiente para reproduzir a distribuição das deformações geométricas nesta experiência**. Após auditoria, BTC só poderá receber o rótulo "inadequação deste nulo", nunca "mercado em tensão" por consequência automática.
- Uso de múltiplas famílias e futura busca de melhor ajuste exige calibração adicional de seleção/multiplicidade. O M14 calibra **cada procedimento isoladamente**.

## Artefatos e integridade

- Código: \`experiments/m14_calibracao_aninhada.py\`; testes \`tests/test_m14_calibracao_aninhada.py\`.
- Workflow único com dependência obrigatória piloto → shards → agregação: \`.github/workflows/m14-calibracao-aninhada.yml\`.
- Saída por shard: JSON e CSV sob \`reports/\`, em artefatos Actions; agregador \`scripts/m14_agregar_resultados.py\` consumindo arquivos e validando cobertura de IDs.
- Não editar \`main\` nem usar dados reservados. SHA de código, versões e configuração registrados em GitHub Actions. O protocolo permanece congelado antes da primeira leitura de resultados M14.
