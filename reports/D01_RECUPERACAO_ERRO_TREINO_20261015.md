# SGV-D01 — Registro de recuperação observacional após falha instrumental

O teste sintético dos oito pares foi **aberto uma única vez**, em GitHub Actions run `38829840815`, e retornou `PASS_SYNTHETIC_INSTRUMENT`; recuperado do artefato da própria run, sem gerar novamente os pares, no workflow `38830071935`. O JSON final está em `resultados/d01_sinteticos_teste_final.json`.

A avaliação BTC ago-set da mesma run falhou no CHECK `training features mismatch after additional months`; o pipeline usava `python ... | tee ...` sem `set -o pipefail` e portanto a etapa remota apareceu como `success` apesar da exceção Python. O `git add` de quatro arquivos juntos deixou de adicionar o resultado sintético porque o JSON de mercado não existia. **O sucesso daquela run não vale como sucesso da etapa BTC**.

Os scripts de auditoria, **sem ajustar ou testar qualquer modelo**, foram executados em `38830071935` e `38830231993`. Resultados `resultados/d01_diagnostico_paridade.json` e `resultados/d01_diagnostico_paridade_hash.json`:
- 85.760 rótulos e seus índices idênticos com prefixos maio–julho e maio–setembro;
- 19/19 colunas bitwise idênticas (zero divergência);
- SHA-256 dos dados de treino recalculado em cada comprimento **igual** ao checksum congelado: `3992d0cc21ce5a292a55312a0cc77cfd9f70767fe9c1e7c29f84df307a60d238`.
- A discrepância da primeira run NÃO se reproduziu na auditoria. Não atribuir causa definitiva sem diagnóstico adicional.

**Decisão:** autorizar somente nova execução da etapa financeira **exploratória já usada**, mantendo o código blob `c7ef72ae2e6d72f79c7dade06013a3c7add0cdc8` e freeze blob `142f4ffafa3c9b8fdb676fa271a5306a37acd736`. O workflow executará diagnóstico hash na mesma run antes de rodar `--stage market`, com `set -euo pipefail` para revelar todas as falhas, e arquivará individualmente os arquivos existentes. **Não refazer o sintético final e não usar outubro/novembro**. Agosto–setembro permanece exploração, sem novo status confirmatório.
