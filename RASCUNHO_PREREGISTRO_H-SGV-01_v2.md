> **SUPERADO** em 15/10/2026 por `PREREGISTRO_H-SGV-01.md` (congelado, opção C). Este rascunho v2 fica só como histórico.

# RASCUNHO v2: Pré-registro H-SGV-01. O SGV original complementa o espaço de fluxo?

**Estado: rascunho, NÃO congelado.**
- Preparado em 15/10/2026, a pedido de Ana.
- Substitui o rascunho v1 (`RASCUNHO_PREREGISTRO_H-SGV-01.md`, mantido para histórico) depois da checagem de ago–set e do teste de complementaridade (`LEITURA_sgv_original_complemento.md`).
- O congelamento só ocorre com o OK de Ana, antes de existir o arquivo mensal de outubro (só sai depois de 31/10).

**Há uma decisão em aberto:** o desenho de períodos. Está na seção 7, com o poder de cada opção.

**Quem julgará:** `pipeline/confirmatorio_sgv.py`, no GitHub Actions, sem edição depois do congelamento. Hashes em `referencia/HASHES_H-SGV-01.txt`, gerados no congelamento.

**Regra da casa:** nenhuma vitória não conquistada será anunciada.

## 1. A pergunta

O espaço de fluxo vê **participação**: volume, agressão e retorno normalizado. O SGV original vê **a posição do preço em relação ao próprio caminho**: o esticamento E_norm, o jerk e quão comum é esse lugar.

Pergunta: **o original carrega informação sobre a amplitude futura que o fluxo não carrega?** Por isso as duas hipóteses primárias são testadas **com o espaço de fluxo inteiro nos controles**.

## 2. O que motiva (exploração)

O alvo é o mesmo em todas as linhas: log Range dos 5 min seguintes, ρ parcial de Spearman por semana.

| | jun–jul (8 semanas) | ago–set (9 semanas, fora da amostra) | Nula de pipeline |
|---|---|---|---|
| Raridade no plano (E_norm, jerk), controles primários | −0,079 (8 de 8) | −0,107 (9 de 9) | −0,005 / −0,003 |
| Raridade, **com o fluxo nos controles** | **−0,064** (81%) | **−0,092** (86%) | −0,006 / −0,002 |
| `mem_e`, controles primários | −0,027 (8 de 8) | −0,018 (8 de 9) | −0,003 / +0,008 |
| `mem_e`, **com o fluxo nos controles** | **−0,026** (95%) | **−0,017** (97%) | −0,003 / +0,008 |
| `mem_e` com retornos de 1 h, 4 h e 1 dia | −0,028 (100%) | −0,019 (106%) | |
| Deslocamento, controles primários | +0,031 | +0,061 | |
| Deslocamento com o campo do original | −0,030 (inverte) | +0,001 (some) | |

As colunas de nula trazem jun–jul / ago–set.

**Ressalvas:**
- jun–set é um único regime de mercado.
- A raridade do original é em boa parte redundante com o campo do **próprio** original. Com o campo original nos controles, sobram 25% a 49%. Só em relação ao fluxo ela é informação nova.
- `mem_e` é pequena: frações de ponto percentual de R².
- O ensaio com o código deste pré-registro reproduz exatamente os números de jun–jul (seção 6).

## 3. Hipóteses

### Primárias: família m = 2, Holm, α = 0,05, unilaterais, com os controles "fluxo"

- **H-SGV-01a, raridade:** ρ_parcial(log `rho_field`, log Range_{t+5} | fluxo) **< 0**. Estados comuns na última semana, no plano (E_norm, jerk), antecedem menos amplitude, além do que o fluxo já sabe.
- **H-SGV-01b, memória do esticamento:** ρ_parcial(`mem_e`, log Range_{t+5} | fluxo) **< 0**. Preço que vem abaixo da sua média há 20–40 min antecede mais amplitude, além do que o fluxo já sabe.

### Secundárias: informativas, BH com m = 9, não entram no veredito

| Nome | Variável | Controles | Sinal |
|---|---|---|---|
| raridade_prim | log ρ | primários | − |
| esticamento_prim | `mem_e` | primários | − |
| raridade_campo_orig | log ρ | primários + log ρ e log tr D do campo do H-DIF-01 no **original** | − |
| esticamento_campo_orig | `mem_e` | idem | − |
| esticamento_retornos_lentos | `mem_e` | primários + retornos com sinal de 60, 240 e 1.440 min | − |
| deslocamento_prim | deslocamento informacional | primários | + |
| deslocamento_fluxo | deslocamento informacional | fluxo | + |
| basin_fluxo | `terrain_basin_depth` | fluxo | − |
| n_obs_fluxo | log(1 + `force_cell_n_obs`) | fluxo | − |

## 4. Definições congeladas

- **Variáveis do SGV original:** `vendor/sgv_original` @ ac6b986, `SGVConfig()` padrão (causal), pelas funções de `pipeline/explorar_sgv_original.py`, alinhadas por timestamp.
  - log `rho_field`: KDE 2D de (E_norm, jerk), banda 0,35, 7 dias anteriores, reajuste a cada 60 min.
  - `mem_e` = EMA₀,₀₅(E_norm).
  - `terrain_*` e `force_cell_n_obs` como no rascunho v1.
- **Alvo:** log(máx high − mín low dos 5 min seguintes + 1e-9). Um minuto a cada 5 das semanas julgadas.
- **Controles primários:**
  - σ de 10, 30 e 60 min (log);
  - HAR de 1 dia e 1 semana;
  - retornos com sinal de 5 e 30 min;
  - log-volume médio de 10 e 60 min;
  - dummies de hora;
  - memória de amplitude: 1, 5, 10, 30, 60 e 1.440 min.
- **Controles "fluxo":** os primários mais as variáveis do espaço de fluxo do M11-I, gaussianizado com a âncora de maio:
  - log ρ, log tr D e c(x) do campo do H-DIF-01 (núcleo h = 0,45, pares da semana anterior);
  - ν(t).
- **Estatística primária:** a do H-FORMA-D-01.
  - Pares de resíduos de postos agrupados das semanas julgadas.
  - p por permutação do par dentro de cada dia (B = 5.000), unilateral no sinal registrado.
  - Bootstrap das semanas como leitura secundária.
  - Semente 20261013.
- **Nula de pipeline:** só leitura, com semente 2026. Retornos, sombras, volume e agressão são permutados dentro do dia a partir do treino da semana 0.
- **Sem:** exclusão de dias, winsorização, troca de variável, de banda, de controles ou de alvo depois de ver os dados.

## 5. Como se lê

- **a confirmada:** a raridade no plano do SGV original antecede amplitude além da volatilidade, da memória de amplitude **e de todo o espaço de fluxo**. É a peça mais antiga do SGV a passar num confirmatório, e a primeira prova de complementaridade.
- **b confirmada:** a memória do esticamento é informação própria do original, ausente do fluxo e dos retornos lentos (pela secundária).
- **Refutada:** o que o original parecia acrescentar ao fluxo não se sustenta fora da amostra.
- **Em nenhum caso há direção ou lucro.** Os ganhos esperados são frações de ponto percentual de R².

## 6. Ensaio de paridade (jun–jul/2026)

`resultados/H-SGV-01_exploracao.json` foi gerado por este código. No congelamento ele vira a referência. O workflow refaz o ensaio e exige diferença < 1e-6 nos ρ semanais antes de abrir o reservado.

| | ρ̄ semanal | ρ agrupado | p (permutação dentro do dia) | Nula |
|---|---|---|---|---|
| H-SGV-01a | −0,0638 | −0,0630 | < 0,0002 | −0,0058 |
| H-SGV-01b | −0,0260 | −0,0244 | 0,0066 | −0,0032 |

Os ρ semanais batem exatamente (diferença 0) com `resultados/sgv_original_complemento_junjul.json`.

## 7. Poder e a decisão de períodos (aberta)

Simulação (`pipeline/poder_sgv.py`, `referencia/H-SGV-01_poder*.json`):
- dias de jun–jul sorteados com reposição;
- sinal atenuado;
- p pela aproximação normal da permutação dentro do dia;
- 2.000 réplicas.

O encolhimento de 35% é o tamanho de `mem_e` em ago–set em relação a jun–jul.

| Efeito encolhido em | a, 4 semanas | b, 4 semanas | a, 8 semanas | b, 8 semanas |
|---|---|---|---|---|
| 0% | 1,00 | 0,55 | 1,00 | 0,83 |
| 35% (≈ ago–set) | 0,95 | **0,34** | 1,00 | 0,56 |
| 40% | 0,92 | 0,32 | 1,00 | 0,50 |
| 65% | 0,58 | 0,17 | 0,83 | 0,26 |

Os valores são o poder com p ≤ 0,05.

**O Holm quase não custa nada aqui.** A raridade tem poder alto. Se ela passar com p muito pequeno, b é julgada praticamente a α = 0,05.

**As opções:**

- **Opção A, como os outros confirmatórios:** outubro decide (4 semanas), novembro replica.
  - Poder de b ≈ 0,3 a 0,55.
  - Uma refutação de b em outubro **não** distingue efeito nulo de efeito pequeno. Isso fica escrito antes.
- **Opção B, mais poder para b:** outubro e novembro juntos decidem (8 semanas), com o veredito no começo de dezembro.
  - Poder de b ≈ 0,5 a 0,8.
  - Custo: não sobra um mês independente para replicar, a não ser dezembro, com o veredito final em janeiro.
- **Opção C, misto:** a pela opção A; b pela opção B.
  - É coerente com o poder de cada uma.
  - Mas são dois calendários num pré-registro só.

## 8. Dependências

Outubro já julga o H-DIF-01, o H-FORMA-D-01 e o H-FORMA-D-02 nos mesmos minutos. O H-SGV-01 seria a quarta família.
- Cada família tem a sua correção.
- Os vereditos são relatados separadamente.
- As famílias **não** são independentes. "Vitórias" não se somam.

O H-SGV-01 usa o campo do H-DIF-01 do espaço de fluxo como **controle**. Uma confirmação do H-SGV-01 não depende do resultado do H-DIF-01.

## 9. Aposta de Claude, antes de outubro

| | Opção A (outubro) | Opção B (outubro + novembro) |
|---|---|---|
| a | ~80% | ~85% |
| b | ~30% | ~45% |
| as duas | ~25% | ~40% |
