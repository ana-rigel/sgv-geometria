# SGV-ID4 — Resultado da identificação da memória direcional, 15/10/2026

**Conclusão: TESTE SINTÉTICO APROVADO; unicidade da volatilidade NÃO IDENTIFICÁVEL por observador de energia.** Ramo `research/identificabilidade-4d-memoria-direcional-20261015`; `main` e todos os experimentos anteriores preservados. Nenhum BTC, nenhuma série financeira ou holdout financeiro acessado. A avaliação final sintética foi aberta **uma vez**, não repetida depois.

## Cronologia e fontes

- Pré-registro prospectivo `PREDICAO_ID4_VOL_VS_DIRECAO_20261015.md`, commit `c24d750`, antes de escrever o código.
- Código `pipeline/id4_vol_direction.py`, Git blob congelado SHA1 `471070b3d179d9bad50aaab3756ac1484008bd15`, nove controles em `tests/test_id4_vol_direction.py`.
- Workflow de preflight/treinamento/validação, GitHub Actions `38826542962`: **success**, 9 testes, modelos treinados apenas nos 12 IDs 0–11, seis IDs 12–17 usados só em validação. Modelos salvos em `resultados/id4_modelos_congelados.json`, Git blob SHA1 `d99568bd2f4998a0f1ca8e6411ca6afa44135c4b`; SHA256 exato no resultado `8a29b35c292d43cdd4cbb56858f8df3f49363cd0662b3ce1247c9618f4c62538`.
- Registro `reports/ID4_FREEZE_PRE_TESTE_20261015.md` antecede a liberação.
- Workflow de teste único, GitHub Actions `38826726949`: **success**. Gravou `resultados/id4_TEST_RELEASE.txt` **antes** da geração de IDs 18–29. Resultado bruto `resultados/id4_resultado_teste_unico.json`, Git blob SHA1 `134fdbb979f8d74c789c9ac795075d4d583ae7c0`.
- Auditoria independente **somente leitura**, sem regenerar teste, workflow `38826900450`: **success**. Leu código, modelos, liberação e resultado; verificou hashes de blobs, identificadores, cálculos de perdas e reproduziu bootstrap 2.000 vezes por trajetória. Saída `resultados/id4_auditoria_somente_leitura.json`, estado `READ_ONLY_AUDIT_PASSED`. O checksum SHA1 correto dos modelos conforme arquivo/auditor é `d99568bd2f4998a0f1ca8e6411ca6afa44135c4b`.

## Geradores, observador e características

30 **pares de trajetórias** de 10.000 observações sintéticas cada: 12 treinamento, 6 validação e 12 teste. Mesmos caminhos latentes de volatilidade lenta/rápida e **mesmas magnitudes de choque em cada par**.

- Nulo `VOL_ONLY`: sinal iid ±1, volatilidade multiplicativa de dois AR(1) e magnitude gaussiana absoluta.
- Alternativa `VOL_PLUS_DIRECTION`: sinal `s[t]` repete o de `t−4` com probabilidade 0,85; sinal marginal equiprovável. Como as magnitudes e `sigma` são idênticas, **`r_null[t]²=r_direction[t]²` exatamente** para cada instante.
- Coordenadas 3D de cada trajetória calculadas separadamente: `E_norm` (desvio de preço da EMA 0,05, com ancoragem robusta só no prefixo), `jerk` (segunda diferença do retorno simples), `memory_flux=ΔEMA_0.05(E_norm)`. São representações sintéticas equivalentes em essência, **não** reprodução bit a bit da configuração SGV no BTC.
- Base mais forte que 3D+vol: `E_norm,jerk,memory_flux,h_slow,h_fast,s[t],s[t−1],s[t−2]`. Ampliado acrescenta apenas `s[t−3]`, que é o sinal lag4 relevante para prever `s[t+1]`. Ambos usam `StandardScaler+LogisticRegression(C=1)` treinados e congelados antes do teste; resultados não são forecasts de BTC.
- Observador quadrático limpo `U[t]=r[t]²/sigma[t]²` é matematicamente igual nos dois processos. Sua correlação com as dez energias anteriores é, portanto, idêntica por construção. Não se substituiu o original de 200 vizinhos `m_r(X_t)`; esse teste demonstrou a impossibilidade para observadores exclusivamente de energia e um comparador direcional explícito.

## Regras e resultado confirmatório

A hipótese passa se `Delta_direction>=0.05` nats/observação, IC bootstrap por trajetórias inteiras 95% (2.000) com limite inferior >0, `abs(Delta_null)<=0.015`, e a identidade da energia nos pares. 12 pares inéditos consumidos, IDs 18–29, sem treinamento adicional e sem seleção após validação.

| Condição | Log-loss base | Log-loss base + lag4 | Delta = base − ampliado |
|---|---:|---:|---:|
| Somente volatilidade | 0,69316960 | 0,69318536 | −0,00001576 |
| Volatilidade + memória direcional | 0,66021832 | **0,42069291** | **+0,23952540** |

- IC95 do `Delta_direction`: **[+0,23418861; +0,24501016]**.
- IC95 do `Delta_null`: [−0,00004044; +0,00000643].
- Acurácia da alternativa direcional: base **60,64%**, ampliado **85,12%**.
- Acurácia do nulo: ambos próximos de 50%.
- Estatística quadrática de memória, Spearman, próxima de zero nos 12 pares devido às magnitudes iid. Isso não prova por si só todos os tipos de dependência condicional nula, mas o desenho dá identidade exata das energias.

**3/3 gates previstos aprovados; auditoria read-only integral aprovada.**

## Interpretação e limites

Este contraexemplo construtivo demonstra: **dois sistemas podem compartilhar exatamente o mesmo caminho de volatilidade e os mesmos retornos ao quadrado e, ainda assim, diferir fortemente na estrutura de direção e previsibilidade do sinal.** Qualquer observador que seja apenas funcional desses dados de energia e da volatilidade é incapaz de distinguir os dois. O observador direcional, com atraso adequado, distingue a memória plantada mesmo condicionado ao estado 3D e aos estados verdadeiros das duas escalas de volatilidade.

Isso NÃO revela que o BTC contém essa memória direcional; NÃO prova que `h_slow+h_fast` seja a única dimensão adicional; NÃO é demonstração de que o espaço original 3D+volatilidade seja markoviano; NÃO invalida a utilidade da volatilidade como mecanismo explicativo para a memória da agitação; NÃO corrige retroativamente o teste de G/S/M histórico. O estimador original de surpresa por 200 vizinhos não foi reproduzido literalmente nesta V1 de ID4, logo nenhuma superioridade quantitativa sobre ele foi testada.

**Decisão:** encerrar ID4 como validação instrumental sintética positiva e prova de **não identificabilidade por energia apenas**. Não reabrir os 12 pares de teste para novo ajuste. Para questionar unicidade em dados reais, construir desenho diferente, controles de memorias alternativas, escore condicional direcional e novas séries historicamente não consumidas, preservando dados reservados.
