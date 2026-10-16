# SGV-AMB01 — Freeze científico pré-teste, 15/10/2026

Pré-registro `reports/AMB01_PROTOCOLO_20261015.md` commit `c615db3`, antes do código e de qualquer resultado AMB01. Run de treinamento [38832323216](https://github.com/ana-rigel/sgv-geometria/actions/runs/38832323216) concluída com sucesso: **10 testes unitários**, sintéticos treino IDs 0–7, validação IDs 8–11, sintéticos finais IDs 12–19 **não abertos**; mercado: 85.760 observações de junho–julho, maio apenas âncora/aquecimento.

Hashes imutáveis antes do teste final:
- Protocolo Git blob `4e9a5a4b08e561ec660f4a23509cc6b93114f3cc`
- Código `pipeline/sgv_amb01_memoria_ambiental.py` Git blob `b90f1ba2e3e4151094a9b79c8b76f96401fb1163`
- Testes `tests/test_sgv_amb01_memoria_ambiental.py` Git blob `784481f7a7ce141fb04f7b50ab9acac3690a40b2`
- Modelos + parâmetros congelados `resultados/amb01_modelos_congelados.json` Git blob `a1c4f58e7a85a8b4f6c1062a7ff9a870a9356f40`
- SHA-256 matriz treino BTC, embutido no freeze: `1f541915e9522d60071748b68973fc279108f74d80ef5b911eb7cb1a1f86ca70`.

Validação **descritiva**, observada após treino e **sem alteração subsequente** de hipótese, código, features ou limiares:

| Condição | Delta_E | Delta_I_given_E |
|---|---:|---:|
| N | -0.00025990 | -0.00015553 |
| E | +0.01067023 | +0.00486969 |
| I | -0.00016221 | +0.21570458 |
| EI | +0.02099261 | +0.11343500 |

O gatilho da etapa seguinte só pode executar após comparar Git blobs exatos, verificar que `resultados/amb01_TEST_RELEASE.txt` e `resultados/amb01_synthetic_final.json` não existem, e commitar o registro de liberação **antes** de simular teste IDs 12–19. Os modelos congelados nunca serão reajustados ao desempenho do teste. Se o instrumento falhar, o resultado negativo será preservado e a análise BTC será reportada como **somente descritiva**.

BTC agosto/setembro já foram usados em vários trabalhos anteriores, logo continuam **exploratórios**. Novembro e outubro não foram usados e não serão acessados aqui. Nenhuma condição de orçamento informacional do Paper A foi implementada ou testada; AMB01 é uma transposição de ideias, não uma confirmação do teorema.
