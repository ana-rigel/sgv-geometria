# SGV-D01 — Errata operacional pós-falha (avaliação financeira exploratória)

**Registrada ANTES de obter qualquer log-loss em agosto–setembro.** O teste sintético final foi consumido uma vez e não será reaberto. Esta errata se aplica exclusivamente à tentativa da avaliação financeira em meses já examinados e **não** torna o resultado confirmatório.

A guarda da versão original comparava SHA-256 dos bytes de uma matriz float64 construída na máquina do treino com os bytes reconstruídos em outra máquina GitHub Actions. A assinatura congelada foi `3992d0cc...d238`. As auditorias `d01_diagnostico_paridade_hash.json` e `d01_diagnostico_pre_btc.json` mostram:
1. Para cada máquina, maio–julho e maio–setembro produzem **índices, labels e todas as 19 colunas exatamente idênticos bit a bit** no trecho de treino.
2. Em uma máquina, o SHA de treino recomputado é o congelado; noutra, é `f010821974fd4753c45cef721e0622e21d54f18ba543a49cae9c11018e0b15cb`, apesar da invariância de prefixo. Os principais pacotes pip relatados são iguais; a operação responsável pela divergência entre execuções ainda não foi identificada.

**Nova guarda técnica exclusiva da avaliação financeira:** exigir índices/labels e 19 features **exatamente iguais dentro da mesma execução** ao acrescentar meses; exigir mesmos 85.760 rótulos; confrontar média e escala `StandardScaler` de cada braço B0,B1,B2 recomputadas no prefixo com os valores dos modelos congelados por `atol=rtol=1e-8`. Se alguma falhar, ABORTAR. Comparar e relatar ambos os SHA-256 de treino, sem mascarar divergência binária entre runs.

Para reaproveitar `test_market` **sem reimplementar qualquer métrica ou retreinar**, um adaptador poderá ajustar **apenas a chave de checksum de integridade em uma cópia em memória** do objeto `frozen`, após todas as guardas passarem. **Não altera** o arquivo congelado, seus parâmetros, modelos, hiperparâmetros, fontes, estatísticas, regras de decisão, período ou código original; guardará o valor original e o recálculo no JSON final. Executar com `pipefail`, falhas explícitas e sem reabrir dados sintéticos finais.

Isto é um reparo de engenharia após falha de execução, não uma aposta nova ou um teste científico cego. Agosto–setembro são historicamente exploratórios, novembro e outubro intocados.
