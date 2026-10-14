# SGV-C01 — FREEZE pré-holdout e autorização separada da avaliação final

**14/10/2026 — congelamento técnico concluído, teste final NÃO executado.**

## Estado auditado

- **Branch documental:** `research/c01-freeze-pre-holdout-20261014`, fundada exatamente sobre `research/hdr-fisher-entropia-controle-sintetico@c0aa64170d2ec2d1eec185729c4af200d7133a38`; a `main` e os ramos anteriores continuam intocados.
- **Dados:** exclusivamente sintéticos T0–T6. Treinamento **560 pares**, validação **140**, teste final **280 pares/40 por classe**, **não gerado, não consultado, não pontuado**. 750 observações A e B independentes e GMM3 por braço.
- **Confronto fixo:** 14 variáveis base (momentos, entropia, Fisher–Rao de covariância, Fisher–Rao ambiente e energy distance) versus as mesmas 14 + 12 descritores HDR50/HDR95. Sem seleção de descritores nem alteração dos hiperparâmetros depois de ver validação.
- **Resultado meramente descritivo já conhecido:** log-loss validação 0,09533925344059234 (base) e 0,024105028179630193 (base+HDR). Nenhum resultado confirmatório e nenhuma alegação financeira.
- **Modelos treinados somente nos 560 pares:** coeficientes e `StandardScaler` de ambos os classificadores persistidos em JSON, sem pickle; o calculador independente reproduz exatamente o log-loss da validação e probabilidade softmax do scikit-learn.
- **Verificação:** 44 testes locais aprovados (incluindo 6 do preflight congelado), e o pacote ZIP foi extraído em outra pasta e verificado novamente com 6 testes, sem abertura do conjunto final.
- **Identificador verificável do congelamento:** SHA-256 do `FREEZE_MANIFEST.json` = `9e880cb7606743f52d6213ece44278aceb5395dae8d76f855c8b7cbba7811fd2`.
- **Modelos JSON SHA-256:** `78e50f211f6d22ce61bc68de726c7cc198a15502b95f2338112e65d312557e6c`.
- **ZIP integral do freeze SHA-256:** `ed4c0307b64462f8f1292179b1a403070898422baae29384688be887b476d746`. Pacote 320.662 bytes com 30 arquivos; preservado em conversa/backup Library, não transferido integralmente para este commit GitHub.
- **ZIP original de treino/validação SHA-256:** `824334f0683585455bcad964b1fd1433532add433de3fefa2d5bc39fed78bf80`, nove hashes de shards auditados.
- **Limitação de proveniência CRÍTICA:** algumas versões locais efetivamente executadas divergem **em bytes** dos caminhos publicados no ramo GitHub de desenvolvimento. Os scripts supervisionados no freeze são idênticos aos presentes no ZIP original de resultados. Portanto, **o commit GitHub sozinho não constitui fonte executável certificada**. O ZIP do congelamento, identificado por seu SHA-256 e manifesto de fonte, é a referência operacional para o teste futuro. Não executar o GitHub Actions antigo como substituto do freeze.
- **Ambiente congelado:** Python 3.13.5, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0, scikit-image 0.26.0, trimesh 4.11.1 e pytest 9.0.2. Executor se recusa a liberar o teste se versões, fonte, modelos ou shards divergem.
- **Não foi verificado sucesso remoto de GitHub Actions.**

## Contrato confirmatório congelado

O teste final consistirá numa única sequência de 280 pares sintéticos, com sementes independentes `test`, 40 por classe. Nenhum caso inválido pode ser regenerado com outra semente. Verificar ≥38 válidos por classe (95%), senão resultado `INCONCLUSIVE` sem inferência primária. Se válido, obter `Δ = logloss(base) - logloss(base+HDR)`. A hipótese primária passa **somente se** o ganho médio for ≥0,03 nats/par **e** o limite inferior do intervalo bootstrap pareado estratificado percentil de 95% for >0 (2000 réplicas, semente 202610142800).

`executor_teste_unico.py` está presente **no ZIP congelado**, não no ramo de desenvolvimento. Por padrão, `--verify-only` compara hashes e reprodução da validação **sem gerar casos de teste**. `--execute` exige **liberação manual explícita**, SHA-256 exato do manifesto e diretório novo inexistente; cria registro de liberação antes de gerar as 280 observações e recusa execução normal repetida no mesmo caminho. Este bloqueio é **procedimental**, não criptográfico: a geração sintética é determinística e conhecida. Uma tentativa de execução interrompida deve ser tratada como consumida/inconclusiva até auditoria de integridade; sem repetição oportunista.

## Escopo e interpretação

A HDR é uma função da densidade estimada: qualquer ganho confirmatório seria melhoria do diagnóstico com um **conjunto de resumos e classificador limitados**, não informação além da densidade completa. Não transferir para BTC, trading, curvatura intrínseca Fisher–Rao de misturas, estudo humano U03 ou vantagem econômica.

**Decisão em 14/10/2026:** freeze preparado/verificado e backup concluído; **não liberar o teste confirmatório nesta etapa**. Sua abertura deverá ser ato separado após checar o arquivo congelado pela soma de verificação, sem reabrir a validação para escolhas adicionais.
