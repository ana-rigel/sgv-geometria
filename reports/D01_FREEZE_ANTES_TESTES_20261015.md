# SGV-D01 — Registro de congelamento anterior às duas avaliações

Data: 15/10/2026. **Treinamento e preflight encerrados.** Run GitHub Actions [38829672104](https://github.com/ana-rigel/sgv-geometria/actions/runs/38829672104) status `success`. Primeira tentativa run `38829564103` falhou em um teste de sanidade que equivocadamente esperava que o *alvo futuro* não mudasse quando se invertia o futuro; assertiva corrigida antes de qualquer treino, preservando código científico, hipóteses e regras.

- Pré-registro Git blob: `6bc9f44538ccd3a802dc40b62f8bed12a8d7c88f`.
- Errata de indexação formal, anterior ao código: Git blob `162d602fb2267fdffa0df87bf7cc348094994bf5`.
- Código de treinamento/eval Git blob: `c7ef72ae2e6d72f79c7dade06013a3c7add0cdc8`.
- Testes corrigidos Git blob: `202f381ff6078bc0e08b38a8b0930141e826315e`.
- Modelos congelados `resultados/d01_modelos_congelados.json` Git blob: `142f4ffafa3c9b8fdb676fa271a5306a37acd736`.
- Treino BTC: 85.760 rótulos, retornos de junho e julho com ancoragem maio; checksum SHA-256 dos dados/features de treinamento embutido no freeze: `3992d0cc21ce5a292a55312a0cc77cfd9f70767fe9c1e7c29f84df307a60d238`.
- Sintéticos: treino em pares IDs 0–11, validação somente de desenvolvimento IDs 12–15; teste final dos oito pares IDs 16–23 **não foi aberto**.
- Validação DESCRITIVA após congelamento sem ajustes: `D_hist_null≈−0.00007209`, `D_hist_direction≈+0.21915120` nats/observação.
- Nenhum dado de agosto, setembro, outubro ou novembro entrou no congelamento deste workflow. Junho/julho já examinados noutros experimentos e agosto/setembro são avaliação **exploratória**, não holdout científico intacto.

**Liberação futura:** um segundo workflow verificará hashes acima, ausência de marcador de liberação, registrará o marcador **antes** de executar o teste sintético IDs 16–23 e a avaliação financeira agosto–setembro. Não ajustar código, modelos ou gates depois da liberação. Em caso de falha, preservar a falha sem repetir o teste sintético como novo.

**Novembro:** sem leitura, sem execução e sem reserva automática de outros holdouts. Repetição nova apenas após encerramento de novembro e congelamento explícito da versão usada.
