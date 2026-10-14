# SGV-C01 — Portão 2, piloto de estimação independente (14/10/2026)

**Status:** engenharia exploratória local. Nenhum BTC, nenhum dado financeiro, nenhuma classificação final nem inspeção da partição `test`.

## O que foi implementado
- `experiments/c01_estimacao_independente.py`: SHA-256 seeds por split/caso/réplica/papel; 750 observações A e 750 observações B independentes; ajuste GMM3 separado por braço com parâmetros congelados (3 componentes, `n_init=3`, `reg_covar=1e-4`, `tol=1e-4`, `max_iter=300`). A partição `test` gera exceção neste módulo.
- Medidas convencionais: diferenças vetoriais de médias e covariâncias, delta logdet, delta de entropia estimado por MC, Fisher–Rao gaussiano de covariâncias, Fisher–Rao ambiente da densidade e energy distance dos dados.
- HDR50 e HDR95 com limiares MC independentes da validação de cobertura e malhas 35³; centros, áreas, volumes, topologia, perda de sobreposição dos voxels numa grade comum e diferença entre tensores de forma das regiões HDR. Estes descritores são **extrínsecos** e não devem ser confundidos com o M11 após registro.
- `tests/test_c01_estimacao.py`: 11 testes de engenharia; `scripts/c01_portao2_piloto.py`: piloto de quatro classes, duas réplicas por classe; workflow CI próprio.

## Evidência de execução local

O ambiente de execução local continha `numpy`, `scipy`, `scikit-learn`, `scikit-image`, `trimesh`, `pytest`. Reexecutado `PYTHONPATH=. python -m pytest -q tests/test_c01_oraculo.py tests/test_c01_instrumentacao.py tests/test_c01_estimacao.py` — **29 testes aprovados**. O piloto `python scripts/c01_portao2_piloto.py --out reports/c01_piloto_estimacao.json --mc 4000` concluiu oito ajustes pares (16 GMM), todos convergentes.

| Caso | Distância de centros HDR50, réplica 0 / 1 | Perda de IoU de volume HDR50, réplica 0 / 1 | Diferença de tensor de forma HDR50, réplica 0 / 1 |
|---|---|---|---|
| T0 identidade | 0,05724 / 0,08830 | 0,19508 / 0,21687 | 0,10101 / 0,11108 |
| T1 translação | 0,63250 / 0,66425 | 0,49541 / 0,49374 | 0,09422 / 0,06614 |
| T3 rotação | 0,12346 / 0,09569 | 0,47706 / 0,51550 | 0,26665 / 0,28665 |
| T6 modo raro | 0,19365 / 0,09196 | 0,26496 / 0,22976 | 0,17081 / 0,11250 |

Os exemplos não são amostra suficiente para estimar poder, falso alarme, ou vantagem estatística; **os números T0 mostram que o estimador pode criar diferenças mesmo com a verdade inalterada**. A distinção em T3 entre centro pequeno e forma mudada sustenta manter medidas de orientação e sobreposição na engenharia, sem selecionar a hipótese por desempenho final.

## Gate remoto
O workflow C01 de fase 1 e o workflow C01 de estimação foram criados no ramo. A ferramenta GitHub disponível nesta sessão não fornece listagem de execuções *push/workflow_dispatch* por workflow; a consulta por commit somente mostra jobs de PR. A tentativa de consultar o endpoint de workflow por URL foi rejeitada pelo conector. **Logo, não há prova de execução remota concluída**. Conferir pelo painel Actions antes de registrar CI como aprovado.

## Pendências antes da avaliação final
1. Alinhar a dimensão e o significado do bloco HDR do pré-registro (incluindo os dois descritores de engenharia agora adicionados); não alterar silenciosamente critérios ou usar observações do piloto para otimizar limiares finais.
2. Auditar caso T0 sob mais seeds e aumentar Monte Carlo para medir erro de cobertura; auditar o modelo GMM3 quando a distribuição real tem 2 componentes.
3. Completar instrumentação comparativa de treinamento/validação, congelar código, manifesto e políticas de falha. **Ainda não criar nem ler a partição de teste selada**, nem produzir conclusão sobre ganho de log-loss.
4. Dados de mercado, ramas main/M8–M11/M15/M35, U03 e períodos reservados permanecem fora do experimento.
