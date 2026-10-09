# Plano — teste da camada de geometria informacional

**Hipótese em teste.** A geometria da distribuição de estados do mercado tem informação própria sobre o comportamento seguinte do preço, além da volatilidade e além da simples posição do estado na distribuição. Geometria aqui significa a métrica de informação sobre as coordenadas do SGV (E = v²+a², jerk, memory_flux) e sua curvatura.

**Regras da casa:**

- Nenhuma vitória não conquistada será anunciada.
- Toda hipótese é pré-registrada antes de olhar o resultado.
- O código legado fica congelado em `legacy/`.
- Os diagnósticos não olham retorno futuro.
- O período confirmatório não é carregado antes do pré-registro.

## Fases

| Fase | O que entrega | Portão para seguir | Estado |
| --- | --- | --- | --- |
| 0 — Fundação | Repositório; legado congelado com proveniência; núcleo exato (`sgvgeo/`) com testes; diagnósticos D1–D8 calibrados em dados sintéticos e revisados por um revisor independente | Testes passando; o nulo GARCH não passa no G1 | **Concluída em 08/10/2026** |
| 1 — Diagnóstico em dado real | D7 primeiro (fixa a largura de banda); depois D1–D8 com `SGV_DATA` nos klines de exploração, em 1m e 1h | Portão G1, abaixo | **Concluída em 09/10/2026: G1 reprovado** (1m e 1h) |
| 2 — Pré-registro | Documento congelado: variável primária, alvo, controles, teste, α, placebo e aposta | Revisão da Ana e do colaborador antes de qualquer dado confirmatório | **Não executada** (linha encerrada em 09/10/2026) |
| 3 — Confirmatório | Julgamento único no período reservado | Resultado do pré-registro | — |
| 4 — Integração | Só se a Fase 3 confirmar: a variável entra numa camada de decisão com custos reais | Novo pré-registro de utilidade econômica | — |

## Portão G1 — existência e mensurabilidade (Fase 1)

A grandeza primária é **ΔF** = slog R(F) − slog R(Fref): a curvatura da métrica de Fisher local além da curvatura de uma gaussiana ajustada à mesma janela. A configuração é gaussianização causal por postos, janela de 1.500 barras e reajuste a cada 60. Os quatro critérios precisam passar nos dados reais de exploração, na escala de tempo escolhida:

1. **Mensurável:** a confiabilidade de ΔF entre metades da janela (D7) é ≥ 0,8. A largura de banda é o menor múltiplo de Scott, entre 2× e 4×, que atinge isso. Ela é fixada antes de rodar D4, D5 e D8 (`SGV_HMULT`).
2. **Além da posição:** a correlação de postos entre ΔF e a distância de Mahalanobis ao centro da janela (D4) tem módulo < 0,5.
3. **Existe:** a **média de ΔF** difere da de 39 substitutos GARCH ajustados com p ≤ 0,05 (p-valor por postos, bilateral, D8 com `SGV_K_GARCH=39`).
4. **Não é só volatilidade:** o R² de ΔF explicado pela volatilidade (D5) é ≤ 0,5.

**Calibração do portão.** No GARCH sintético, onde não há geometria além da volatilidade, a regra escolhe 3× e ΔF passa só no critério 1 (0,95). Ele falha no 2 (0,62), no 3 (p = 0,85) e no 4 (R² = 0,85). O portão não deixa passar o nulo.

Se G1 falhar no dado real, a geometria destas coordenadas não tem conteúdo próprio. A linha para, ou recebe **uma** reformulação de coordenadas, pré-registrada antes de ser rodada.

## Registro da Fase 1

**08/10/2026 — D7 no período de exploração inteiro** (240 barras sorteadas entre todas; saídas em `reports/real_1m/` e `reports/real_1h/`). Confiabilidade de ΔF (gaussianização por postos):

| Largura (× Scott) | 0,5× | 1× | 2× | 3× | 4× |
| --- | --- | --- | --- | --- | --- |
| 1m | −0,03 | 0,36 | **0,83** | 0,97 | 0,98 |
| 1h | 0,00 | 0,28 | **0,85** | 0,97 | 0,98 |

Pela regra do G1, a largura fica em **2× Scott nas duas escalas** (`SGV_HMULT=2`). **Critério 1 aprovado em 1m e em 1h.** No GARCH de calibração, o mesmo número foi 0,77.

**Declarado antes de rodar o resto da bateria:** D1–D6 e D8 usam exatamente a mesma janela de cada script na calibração (as últimas N barras do período de exploração: 6.000 em D4/D5/D6, 4.500 em D8), sem `SGV_TAIL`. Em 1m isso cobre os últimos ~3–4 dias de julho/2026; em 1h, os últimos ~6–8 meses de 2024. D8 usa 39 réplicas GARCH e 19 de cada outro nulo. O resultado de D7 acima não é recalculado.

**09/10/2026 — Bateria completa e julgamento do G1** (`reports/FASE1_PORTAO_G1.md`): **G1 NÃO PASSA em 1m nem em 1h.**

| Critério | 1m | 1h |
| --- | --- | --- |
| 1. Mensurável | 0,83 ✓ | 0,85 ✓ |
| 2. Além da posição | 0,20 ✓ | 0,23 ✓ |
| 3. Existe (média de ΔF vs. GARCH, 39 réplicas) | p = 0,40 ✗ | p = 0,175 ✗ |
| 4. Além da volatilidade | 0,495 ✓ | 0,571 ✗ |

Pela regra, a linha para ou recebe **uma** reformulação de coordenadas pré-registrada. Decisão pendente da Ana.

**09/10/2026 — Reformulação única (R1, coordenadas de fluxo) julgada** (`reports/R1_PORTAO_G1.md`). A Ana escolheu a R1, e a C2, proposta em paralelo, foi retirada sem rodar. O pré-registro foi congelado no commit `6dcd828`. **G1′ reprovado em 1m (critério 3: p = 0,25) e em 1h (critério 3: p = 0,10).**

**LINHA GEOMÉTRICA ENCERRADA (09/10/2026).** Pela regra fixada antes dos dados, nem as coordenadas de preço (C1) nem as de fluxo (R1) mostram geometria de curvatura além dos fatos estilizados (GARCH, impacto, persistência do fluxo e volume–volatilidade). As Fases 2 a 4 não serão executadas.

## Escolhas já feitas pela calibração (detalhes em `reports/DIAGNOSTICO.md`)

- **Métrica:** Fisher local (F). A Hessiana do legado é ruído onde tem curvatura e plana onde é estável.
- **Grandeza:** ΔF, e não a curvatura de F sozinha, que é sobretudo posição (correlação de 0,83 com a referência gaussiana) e volatilidade (R² de 0,80).
- **Escala:** gaussianização causal por postos.
- **Fora do teste:**
    - o índice `field_gravity` e o par G/T, porque G = κT não se sustenta (D6);
    - a troca de assinatura de H como evento de ruptura, porque ela inverte a cada 2 barras (D4).

## Decisões abertas (da Ana)

1. **Escala de tempo primária.** As opções são 1m (memória curta, D4) ou 1h (6 anos já baixados). Proposta: rodar G1 nas duas e escolher pelo portão, sem olhar retorno.
2. **Períodos — TRAVADOS em 08/10/2026** (aprovados pela Ana; os klines de exploração foram baixados pelo workflow e conferidos por SHA-256, sem nenhum mês do período reservado):
    - **1m:** exploração de 01/05/2026 a 31/07/2026 (132.480 barras, sem lacunas); confirmatório de 01/08/2026 a 31/10/2026, mais réplica prospectiva em novembro e dezembro de 2026.
    - **1h:** exploração de 01/01/2020 a 31/12/2024 (43.817 barras; 15 lacunas de manutenção da Binance); confirmatório de 01/01/2025 em diante.
3. **Alvo do confirmatório.** Primário: amplitude futura (Range T+5 em 1m, ou T+4 em 1h), residualizada por volatilidade e hora, como na H-DYN3-AMP. Secundário: direção.

## Dados necessários para a Fase 1

Klines BTCUSDT de spot, no formato de `data.binance.vision`, colocados em `data/`:

- **1m:** maio, junho e julho de 2026 (exploração).
- **1h:** de 2020 a 2024 (exploração).

O ambiente onde o Claude roda não alcança a Binance, então os arquivos precisam ser anexados.

```bash
python3 scripts/baixar_klines.py      # baixa só a exploração, confere SHA-256; recusa o período reservado

# ordem da Fase 1 (exemplo em 1m)
export SGV_DATA=data/BTCUSDT-1m-2026-05.zip:data/BTCUSDT-1m-2026-06.zip:data/BTCUSDT-1m-2026-07.zip
python diagnostics/run_all.py d7_confiabilidade             # 1) fixa a largura de banda
export SGV_HMULT=2   # ou 3, 4 — o menor múltiplo com confiabilidade de ΔF ≥ 0,8
SGV_K_GARCH=39 python diagnostics/run_all.py                 # 2) bateria completa
```
