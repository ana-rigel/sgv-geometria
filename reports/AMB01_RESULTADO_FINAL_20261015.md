# SGV-AMB01 — RESULTADO FINAL: memória ambiental versus memória interna

Data 15/10/2026. Ramo `research/sgv-amb01-memoria-ambiental-20261015`. **Instrumento sintético APROVADO; agosto–setembro EXPLORATÓRIOS sem evidência de ganho direcional ambiental.** Outubro e novembro intocados. Main, SGV-D01, SGV-ID4 e demais resultados históricos preservados.

## Cronologia verificável

1. Hipóteses, geradores, quatro braços, métricas, unidades de bootstrap e gates publicados antes do código em `reports/AMB01_PROTOCOLO_20261015.md`, commit `c615db37515749a3a673d3fd9815cddb2187e135`.
2. Código `pipeline/sgv_amb01_memoria_ambiental.py`, Git blob SHA1 `b90f1ba2e3e4151094a9b79c8b76f96401fb1163`; dez testes de integridade em `tests/test_sgv_amb01_memoria_ambiental.py`, Git blob `784481f7a7ce141fb04f7b50ab9acac3690a40b2`.
3. Workflow de treinamento `38832323216`: **success**. Oito trajetórias sintéticas IDs 0–7 e 85.760 retornos válidos de junho–julho, com maio como âncora. Quatro trajetórias 8–11 usadas só para validação de engenharia. Modelos congelados `resultados/amb01_modelos_congelados.json`, Git blob `a1c4f58e7a85a8b4f6c1062a7ff9a870a9356f40`. SHA-256 dos exemplos de treino: `1f541915e9522d60071748b68973fc279108f74d80ef5b911eb7cb1a1f86ca70`. Arquivo `reports/AMB01_FREEZE_ANTES_TESTE_20261015.md` registrado antes do teste.
4. Workflow final `38832497729`: **success**. Todos os hashes validados; registro `resultados/amb01_TEST_RELEASE.txt` escrito e commitado **antes** de gerar os oito pares de IDs 12–19. O código e pesos não foram alterados. Agosto/setembro baixados com SHA-256 verificado. Logs e JSONs registrados separadamente com `set -euo pipefail` (sem mascarar falhas com pipe `tee`).
5. Auditoria dos JSONs arquivados: 8 IDs sintéticos únicos 12–19 em cada uma de quatro condições; médias de ganho reproduzidas a partir dos detalhes por trajetória; nove semanas financeiras somam exatamente 82.683 exemplos e os efeitos semanais ponderados reproduzem todos os números agregados.

## Mecanismos e hipóteses

- Canais de inspiração Paper A: **ambiental persistente** (condição E; fator AR `a=.985`, duas observações ruidosas) vs **interno** (condição I; sinal com ligação ao atraso t−20 ao prever t+1). Condição EI ambos. Condição N nenhum. **Não** aplicamos ou testamos o teorema/platô/orçamento informacional do Paper A.
- Magnitudes e caminho de volatilidade exatos entre condições por ID. Números positivos de memória direcional ambiental podem resultar da inferência imperfeita de Z; histórico de sinais pode carregar indiretamente informação ambiental.
- Quatro modelos: A0 (história curta dos preços, volatilidade rápida/lenta, SGV 3D e ambiente atual), AE (+ histórico ambiental até 120 min), AI (+ histórico interno de sinais até 60 min), AEI (ambos).
- Efeito `D_E=loss(A0)-loss(AE)`. Efeito `D_I_given_E=loss(AE)-loss(AEI)`; bootstrap percentil por trajetória independente (sintético) ou por semana completa (BTC), 2.000 sorteios. Positivo = redução de perda; não confundir pequeno ganho com causalidade.

## Controle sintético final: oito trajetórias seladas POR condição, uma abertura

| Condição | D_E média | D_E IC95 | D_I_given_E média | D_I_given_E IC95 |
|---|---:|---|---:|---|
| N: nenhuma memória | −0,00017886 | [−0,00028562; −0,00005260] | −0,00003810 | [−0,00016274; +0,00008102] |
| E: ambiente | **+0,01135026** | [+0,00945737; +0,01345879] | +0,00304319 | [+0,00150147; +0,00480086] |
| I: interna | −0,00022378 | [−0,00041534; −0,00004523] | **+0,21943174** | [+0,21467038; +0,22441443] |
| EI: ambas | **+0,01422809** | [+0,01106488; +0,01854345] | **+0,11143292** | [+0,10165898; +0,12127300] |

**5/5 gates de controle passaram, inclusive energia pareada exatamente igual.** A melhora interna de 0,003 no caso E, apesar de não haver mecanismo interno independente, é um achado conceitual: atraso do sinal pode transmitir informação sobre o ambiente latente não resolvida pelos proxies. Portanto `D_I_given_E>0` não prova autorretenção intrínseca.

Fonte bruta imutável: `resultados/amb01_synthetic_final.json`, Git blob `521081d6904b51cf3716f96b6e21e46bcfb2e8b3`.

## BTCUSDT 1m agosto–setembro de 2026: avaliação SOMENTE EXPLORATÓRIA

**82.683 exemplos, 9 semanas, modelos treinados exclusivamente em junho–julho, checksum de treino verificado no ambiente estendido.** Variáveis ambientais observadas: volume de BTC na barra 1m e agressão líquida normalizada (`taker_buy / volume`), contemporâneas até o fechamento t. A análise não procura causalidade exógena.

| Modelo | Log-loss | Acurácia |
|---|---:|---:|
| A0: base com estado, vol, curto e ambiente atual | 0,69337658 | 50,6815% |
| AE: A0 + histórico ambiental | 0,69352568 | 50,5231% |
| AI: A0 + histórico interno longo | 0,69338043 | 50,6815% |
| AEI: ambos históricos | 0,69352779 | 50,6307% |

| Efeito | Média ponderada por semana | IC95 bootstrap nove semanas |
|---|---:|---:|
| D_E: ambiente adicional após base | **−0,00014910** | [−0,00022022; −0,00007304] |
| D_I: interno adicional após base | −0,00000385 | [−0,00006130; +0,00005566] |
| D_I_given_E: interno após ambiente | −0,00000211 | [−0,00004257; +0,00004472] |
| D_E_given_I: ambiente após interno | **−0,00014737** | [−0,00022534; −0,00006442] |

**Leitura:** o acréscimo de história ambiental, dentro da regressão logística definida e do corte temporal usado, piorou a previsão probabilística. O acréscimo de história interna de sinais não produziu ganho detectável. Nove semanas são poucas unidades independentes, e agosto–setembro foram usados anteriormente; nenhum IC aqui é evidência confirmatória do mundo externo, e diferenças tão pequenas não têm implicação de lucro.

**Não provamos ausência de memória ambiental.** Variáveis de mercado omitidas, não linearidade, horizonte maior, mudança de regime, ruído de medição ou canal ambiental sem informação direcional podem deixar o teste negativo. Volatilidade do retorno, por ser derivada do próprio preço, não equivale a um ambiente exógeno.

Fonte bruta: `resultados/amb01_btc_agoset_exploratorio.json`, Git blob `792e8a45d353c8e31b7e8da432efc8a99e183498`.

## Errata de métrica secundária e auditoria

O JSON automático do BTC contém `zero_ret_fraction: 0`, calculado como `1-len(yt)/sum(te)`, com `te` já filtrado por rótulos não-zero; isso é circular e **NÃO mede a fração de retornos zero da série bruta**. Não citar 0 como resultado empírico; a fração não foi corretamente estimada nesta rodada e fica marcada **INVÁLIDA/NÃO REPORTADA**. Isso não afeta modelos, seleções, perdas, ganhos, ICs ou resultados principais. Corrigir numa versão futura antes do experimento de novembro, com nova pré-documentação e sem reutilizar o holdout sintético.

## Decisão e próxima etapa

AMB01 é positivo em validade instrumental dos **quatro mecanismos específicos** e negativo quanto a ganhos ambientais direcionais na avaliação BTC já explorada. **Não** transformar resultado negativo em escolha adaptativa de lags ou proxies para novembro. Reservar novembro para versão congelada nova, após o encerramento do mês, checagem de colisão com outros holdouts e controle de mudanças formais. Outubro e novembro jamais lidos por esta rodada. Não reabrir casos sintéticos IDs 12–19.

Workflow de execução: https://github.com/ana-rigel/sgv-geometria/actions/runs/38832497729
