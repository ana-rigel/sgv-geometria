# SGV — Programa integrado M11-I ↔ U03 ↔ M35 ↔ RTT
**Registro de integração científica — 13/10/2026.** Ramo de trabalho: `research/integracao-m11i-u03-rtt-m35`, originado **sem alteração** de `research/m35-traducao-geometrica` @ `dac529b4`.

## Propósito e regra-mãe
Unificar a cadeia **medição geométrica → compreensão humana → dinâmica temporal → teste incremental** sem misturar endpoints, reabrir holdouts ou transformar cada resultado negativo em outra otimização do mesmo experimento. Este documento registra fatos e ações futuras. **Não é pré-registro, não roda novos testes de mercado, não dá acesso a novos dados**.

Três alegações diferentes exigem três evidências distintas:
1. **Medição**: uma estatística de deformação das distribuições é numericamente estável, repetível e não trivialmente recuperável por momentos usuais.
2. **Interpretação**: visualizar geometrias melhora o reconhecimento humano de transformações em comparação justa com projeções/estatísticas convencionais.
3. **Dinâmica temporal**: uma medida da assimetria das transições reais excede nulos temporais fortes e, se alegada previsão, melhora proper scoring no futuro. Nenhuma das três implica as outras, e nenhuma implica lucro.

## Trilha A — U03 original e v2: validade humana da visualização
**Fonte operacional**: `SGV_U03_V2_EVOLUIDO_COMPLETO_20261013.zip` produzido separadamente do repositório. Proveniência (SHA-256):
- ZIP original `SGV_Navegador_U03_Completo_20261013(1).zip`: `f8998b28cd3431636eabacc325de0b6171a3406d0fbdca378fbd8cda8df36506`;
- ZIP completo v2: `fca6bbcd4c8f9c581825f1340c79d2eaa61e1ba2b88f3541a363c3c7efa4de38`;
- ZIP patch v2: `dd38f293b9fbcb39aec4ee825605515c6b51521750a286fa36cf79e4c0d81828`.

**Fatos auditados localmente neste registro**: 14 casos sintéticos com IDs opacos e gabarito offline, 2 braços (3D geométrico vs 2D/estatístico), mesmos casos v1/v2; HDR50 original preservada, HDR90 GMM2 adicionada na v2; centros, seta e laboratório disponíveis apenas fora da sessão cega. Arquivos `navegador_sgv/u03/PROTOCOLO_U03.md`, `u03/PROTOCOLO_U03_V2_ENGENHARIA.md`, `LEIA-ME_U03_V2_EVOLUCAO.md`. Testes reproduzidos: `test_u03_v2.py` **6/6**, `test_u03.py` **3/3**, `test_u03_v2_js.cjs` **8/8**. **Não houve validação visual automatizada nem estudo real com participantes**. O protótipo WebGL autônomo do Lovable tem estímulos diferentes e não substitui o protocolo original.

**Próximas ações (SEM coleta oficial ainda):**
A1. Auditoria visual manual, casos 01–14, em Windows/Linux e navegadores distintos: caudas, pequenas translações, rotação 3D, transparência, webcam? não aplicável; verificar zoom, latência, legibilidade. Registrar defeitos e capturas, sem reclassificar casos após ver respostas.
A2. Pré-piloto de usabilidade com casos de treino fora dos 14 oficiais; nenhuma interpretação estatística de acerto.
A3. Congelar um protocolo de estudo humano com hipóteses e efeito primário (taxa de acerto), alocação entre braços, randomização, tamanho de amostra/poder, análise que trate participantes e itens como agrupamentos, consentimento/ética conforme aplicável e plano para dados faltantes. O braço convencional também mudou de enquadramento na v2; **não atribuir diferença v1×v2 exclusivamente à HDR90**. Evitar agregar respostas v1/v2.
A4. Após congelamento e ética aplicável, executar coleta; nunca expor o ZIP com gabarito aos participantes.

**Gate A**: não alegar que a geometria melhora a compreensão sem comparação humana adequada. O valor de uma interface não confirma previsibilidade de BTC.

## Trilha B — M11-I existente → M35: qualidade do instrumento
**Fonte**: `research/m11i-integracao-instrumental` @ `f3d8796`; `research/m35-traducao-geometrica` @ `dac529b4`. M11-I já implementa registro e assinatura de cascas. Não recriar M11-I.

**Auditoria M11-I concluída** `reports/m35/auditoria_m11i/LEIA.md` e `audit_m11i.json`:
- correlação Spearman M11-I/M11 original **0,993** em 60 origens; D concorda com M2 até 4,44e-16 para pares válidos;
- confiabilidade da distância M11-I ~**0,33**, do M11 original ~**0,37**; estimativa de 37% do ruído devido às sementes e 63% à reamostragem;
- correção de rastreabilidade: auditoria JSON contém `flow_erro` na comparação da série; **NÃO** declarar a equivalência do fluxo reproduzida integralmente; o *split* foi idêntico e outras verificações passaram.
- Observações sobre sensibilidade à semente, diferença de tratamento de lacunas e limitação de amostras de ~525 pontos por metade devem ser preservadas.

**M35 passo 1 NÃO concluído**: plano de variantes V0–V4/V4n foi fixado em `reports/m35/PLANO_M35_PASSO1_20261013.md`, código `experiments/m35_instrumento.py`, `scripts/m35_passo1.py`, 5 testes em `tests/test_m35_instrumento.py`. Commit `dac529b4` diz explicitamente **“run interrupted, no results”**; não inventar `passo1.json`. A primeira ação é encerrar **somente** esse teste instrumental usando BTCUSDT 1m mai–jul/2026 já explorado + dados sintéticos, sem alvos futuros e sem varredura de hiperparâmetros guiada por score.

**Critérios fixos do M35** (sem mudança):
- sucesso sintético: Spearman >= 0,7 com deformação plantada e piso estável;
- não redutibilidade: R² nos momentos < 0,5;
- escolher maior confiabilidade entre variantes válidas e não redutíveis; meta >= 0,6. Se nenhuma passar, registrar falha; estimar fontes de ruído;
- preservar V0 e o restante do histórico, inclusive nulos e casos negativos.

**Próximas ações**: B1 preflight do script e dependências/caminhos, melhoria de execução reentrante sem alterar as medidas ou regra do plano; B2 execução instrumental no BTC *já gasto*, com auditoria de saída e testes; B3 sensibilidade da estimativa de confiabilidade ao bootstrap temporal e ao número de origens, sem seleção ex-post. B4 somente se alguma variante passar: documentar identidade geométrica, versão congelada e preparar **novo** protocolo para aplicação em dados externos não consumidos.

**Gate B**: nenhum teste preditivo em novo ativo antes da validade sintética, confiabilidade, informação distinta dos momentos e comparação justa com controles não geométricos. Não confundir “não redutível por R²” com causalidade ou informação preditiva.

## Trilha C — RTT: direcionalidade temporal, não risco RV15
**Confirmatório já executado**, e deve permanecer encerrado: ramo isolado `confirmatorio/H-sigmaRTT-01` @ `4b9a298b`; `RESULTADO_H-sigmaRTT-01.md` e `resultados/H-sigmaRTT-01_confirmatorio.json`. Julgamento BTC 1m ago–set/2026 (61 dias):
- H1 giro real vs sinais sorteados: D=+0,01253, p<0,0001, **passou**, porém quase todo efeito é explicado por **assimetria estática de retorno/sinal/amplitude**;
- H2 giro real vs dia invertido: D=+0,00334, p=0,18, **não passou**;
- real vs permutação de minutos dentro de dia (descritivo): D=+0,00178, p=0,31.
Logo NÃO demonstramos flecha do tempo própria, nem informação preditiva incremental. Não transformar H1 em prova de irreversibilidade de dinâmica.

**Ponte RTT ↔ M11-I já testada em exploração**, ramo `research/ponte-rtt-m11i-hj-hgeo` @ `a65b240`, `reports/SGV_PONTE_RTT_M11I_20261013.md`:
- H-J 30 blocos disjuntos BTC mai–jul: log score RTT original menos reversível **−0,07742** nats/transição, RTT venceu 0/30;
- H-GEO 3 blocos: RTT vs reversível vs shuffle vs IID com perdas similares, sem vitória específica do fluxo direcional. Comparação engenheirada, **não confirmatória**.

**Próximas ações**: C1 encerrar documentação de H-σRTT-01 sem ajuste de gate; C2 desenhar nulos fortes para hipótese genuinamente NOVA (incluindo relação sinal×magnitude, agrupamento de volatilidade, reversibilidade de P condicionada ao regime); C3 exigir endpoint preditivo causal de transições/distribuições, blocos não sobrepostos, score próprio, orçamento igual entre referências; C4 validar em sintético com processos reversíveis/irreversíveis antes de qualquer novo dado real. Só pré-registrar uma nova hipótese se superar logicamente H1/H2 e H-J; **não reusar os mesmos dados como confirmação**.

**Gate C**: não inferir flecha temporal a partir de giro de uma projeção, e não equiparar irreversibilidade estatística com rentabilidade.

## Livro de dados — prevenção de reutilização confirmatória
- BTC 1m maio–julho/2026: **explorado/gasto**, permitido para engenharia e sintéticos.
- BTC 1m agosto–setembro/2026: **consumido na H-σRTT-01** para confirmação, não tratar como virgem.
- ETH 1m junho–setembro/2026: **consumido no M31**.
- SOL 1m junho–setembro/2026: **consumido no M32**.
- BNB 1m junho–setembro/2026: **consumido no M33**.
- BTC 1m outubro–dezembro/2026: **RESERVADO** ao protocolo H-FR/M22; não tocar, nem negociar uso por esta integração.
- Outras séries futuras: status desconhecido até inventário explícito. Não chamar ETH/SOL/BNB “replicações independentes no tempo” se compartilharam o mesmo período e choques macro.

## Sequência operacional (a partir desta integração)
0. **Feito:** auditar ramos, proveniência local U03 e as leituras negativas/positivas da RTT; preservar status histórico.
1. **Em execução somente de engenharia:** preparar retomada verificável M35 passo 1 no BTC gasto, sem alterar seleção e sem calcular lucro/risco futuro.
2. **Paralelo, sem coleta:** piloto gráfico controlado U03 v2; anotar defeitos de interface, não interpretar como resultados humanos.
3. **Somente desenho:** propor nulidade temporal melhor que os controles de H1/H2 e H-J; nenhuma confirmação antes de um protocolo novo.
4. Decisão na próxima reunião: caso B falhe, encerrar esta linha de instrumento em vez de multiplicar métricas; caso B passe, congelar medida e discutir o primeiro alvo adicional em dados verdadeiramente novos. U03 pode prosseguir independentemente.

## Regra anti-divagação e anti-repetição
A cada hipótese: indicar **objeto → definição operacional → comparador forte → dado já usado/virgem → previsão antes dos números → regra de fracasso**. Uma falha não autoriza nova tentativa no mesmo holdout. O histórico negativo é evidência, não obstáculo administrativo. Nenhum commit deste ramo altera código de confirmação M31/M32/M33/RTT, nem a `main`.

## Links de referência
- [M11-I](https://github.com/ana-rigel/sgv-geometria/tree/research/m11i-integracao-instrumental)
- [Auditoria M11-I](https://github.com/ana-rigel/sgv-geometria/blob/research/m35-traducao-geometrica/reports/m35/auditoria_m11i/LEIA.md)
- [Plano M35](https://github.com/ana-rigel/sgv-geometria/blob/research/m35-traducao-geometrica/reports/m35/PLANO_M35_PASSO1_20261013.md)
- [Resultado RTT](https://github.com/ana-rigel/sgv-geometria/blob/confirmatorio/H-sigmaRTT-01/RESULTADO_H-sigmaRTT-01.md)
- [Ponte RTT ↔ M11-I](https://github.com/ana-rigel/sgv-geometria/blob/research/ponte-rtt-m11i-hj-hgeo/reports/SGV_PONTE_RTT_M11I_20261013.md)
