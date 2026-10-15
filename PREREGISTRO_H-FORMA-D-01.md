# Pré-registro H-FORMA-D-01 (forma do campo de difusão)

**Congelado em:** 15/10/2026, antes de qualquer acesso aos dados de outubro e de novembro de 2026. O arquivo mensal de outubro da Binance ainda não existe nesta data.

**Decisão de Ana (15/10/2026):** congelar. Julgamento em **outubro/2026**, junto com o H-DIF-01. **Replicação em novembro/2026**, com o mesmo código e sem nenhuma mudança.

**Quem julga:** `pipeline/confirmatorio_forma.py`, executado no GitHub Actions deste repositório, sem edição depois deste commit. Os hashes estão em `referencia/HASHES_H-FORMA-D-01.txt`.
- Julgamento: `--periodo confirmatorio`.
- Replicação: `--periodo replicacao`.

**Regra da casa:** nenhuma vitória não conquistada será anunciada. O que não passar aqui não passou.

Nada do H-DIF-01 nem do H-DIR-01 foi alterado. Este ramo só acrescenta arquivos.

## O que foi visto na exploração (jun–jul/2026) e motiva o teste

O Navegador SGV (pesquisa D, passos 1 a 2c, 15/10/2026) usou o mesmo estimador de D(x) do H-DIF-01, com paridade semana a semana.

- O excesso de amplitude além da memória tem uma parte que nem a raridade (log ρ) nem o tamanho da agitação (log tr D) explicam.
- Nos dois espaços, a **forma** de D carrega informação. Dados log ρ e log tr D, a agitação concentrada num eixo antecede mais amplitude nos 5 minutos seguintes.
- Contra a nula de pipeline, a relação não sai das fórmulas:

| | real | nula |
|---|---|---|
| fluxo | +0,085 (8/8 semanas) | −0,018 |
| original | +0,047 (8/8) | −0,001 |

A anisotropia do original vem em boa parte da construção do jerk (uma segunda diferença). A relação entre forma e amplitude futura, não.

**Ressalvas da exploração:**
- A medida c(x) foi escolhida depois de ver os coeficientes de quatro modelos e de várias medidas de forma, no mesmo período.
- Os efeitos do programa encolheram 40–65% da exploração para o confirmatório (H-σRTT-01).

## Hipóteses

### H-FORMA-D-01: família de 2 testes, Holm, α = 0,05

Para cada espaço, com o campo da semana k−1 avaliado nos minutos da semana k:

> c(x) = log(tr D(x) / 3) − (1/3) Σ_j log D_jj(x)

c(x) é a concentração da agitação num eixo. É ≥ 0 e vale 0 quando a agitação é igual nos três eixos.

- **H-FORMA-D-01/fluxo** (z, ι, ν): ρ_parcial(c(x_t), log Range_{t+5} | controles) **> 0**.
- **H-FORMA-D-01/original** (E_norm, jerk, memory_flux): a mesma correlação **> 0**.

### Secundárias: informativas, BH com m = 3; não entram no veredito

| Espaço | Medida | Sinal registrado |
|---|---|---|
| Fluxo | fração de tr D no eixo z | + |
| Original | fração de tr D em jerk | + |
| Original | fração de tr D em E_norm | − |

## Definições congeladas

- **Coordenadas, gaussianização e âncora:** idênticas às do H-DIF-01.
  - Fluxo: `flow_coordinates` do M11-I.
  - Original: E_norm e jerk do `build_btc_90d_input_sgv` (sgv_original ac6b986) e memory_flux = Δ EMA₀,₀₅(E_norm).
  - Gaussianização por postos com âncora congelada em maio/2026.
- **Campo:** o estimador do H-DIF-01. Núcleo gaussiano isotrópico, h = 0,45, sobre os pares (x_t, s_t = x_{t+1} − x_t) da semana anterior, sem corte por massa efetiva.
  - D_jj(x) = E_w[s_j²] − E_w[s_j]².
  - tr D = Σ_j D_jj.
  - log ρ(x) = log(massa do núcleo / n).
- **Alvo:** log(máx high − mín low dos 5 min seguintes + 1e-9), em janelas não sobrepostas de 5 min.
- **Controles:**
  - log σ de 10/30/60 min;
  - log σ de 1 dia e de 1 semana (HAR);
  - retornos com sinal de 5 e 30 min;
  - log-volume médio de 10 e 60 min;
  - dummies de hora UTC;
  - memória de amplitude: médias móveis do log-range de 1 min em 1, 5, 10, 30, 60 e 1.440 min;
  - log ρ(x_t) e log tr D(x_t).
- **Correlação parcial de Spearman:** os postos de c e de y são regredidos nos controles por MQO, e os resíduos são correlacionados.
- **Semanas:** blocos de 7 dias.
  - **Julgamento:** a partir de 24/09/2026 (só treino). Semanas julgadas: 01–08, 08–15, 15–22 e 22–29/10. O resto de outubro (menos de 5 dias) fica de fora. Agosto e setembro entram apenas como aquecimento dos filtros causais.
  - **Replicação:** a partir de 25/10/2026 (só treino). Semanas julgadas: 01–08, 08–15, 15–22 e 22–29/11. O resto de novembro fica de fora. Agosto a outubro entram apenas como aquecimento.
- **Estatística primária:** a do H-DIF-01.
  - ρ de Spearman sobre os pares de resíduos agrupados das 4 semanas.
  - p por permutação do alvo dentro de cada dia (B = 5.000, semente 20261013), unilateral positivo.
  - Holm com m = 2.
- **Secundário, só leitura:**
  - bootstrap da série de ρ semanais;
  - nula de pipeline: retornos, sombras, agressão e volume permutados dentro de cada dia a partir do início do treino da semana 0, mesmas fórmulas, semente 2026.
- **Sem:** exclusão de dias, winsorização, troca de h, de controles, da medida ou do alvo depois de ver os dados.

## Como se lê

- **Outubro decide.** Uma hipótese é *confirmada* se p de Holm < 0,05 em outubro.
- **Novembro replica.** O mesmo critério, rodado em novembro, diz se a confirmação se *replica*. O resultado de novembro é relatado à parte e não muda o veredito de outubro.
- **Confirmada (e replicada):** a forma de D, e não só o seu tamanho, passa a ser grandeza do programa. A agitação concentrada num eixo antecede amplitude além da volatilidade, da memória de amplitude, da raridade e do tamanho de D.
- **Refutada:** a forma de D continua um objeto descritivo, com anisotropia e eixo principal, sem informação própria sobre o futuro.
- **Em nenhum caso há direção ou lucro.** O ganho esperado é uma fração de ponto percentual de R² sobre a volatilidade.

## Ensaio de paridade (jun–jul/2026), referência congelada

Os números estão em `referencia/H-FORMA-D-01_exploracao_referencia.json`, gerado por este mesmo código.

| ρ̄ semanal | real | semanas > 0 | nula de pipeline |
|---|---|---|---|
| fluxo, c(x) | +0,0849 | 8/8 | −0,0175 |
| original, c(x) | +0,0469 | 8/8 | −0,0008 |

Secundárias (real / nula):

| | real | nula |
|---|---|---|
| fração em z | +0,091 | +0,004 |
| fração em jerk | +0,035 | −0,003 |
| fração em E_norm | −0,064 | −0,005 |

O workflow refaz este ensaio e exige diferença < 1e-6 nos ρ semanais antes de abrir os dados de julgamento.

## Poder

Simulado com a estrutura de dias real de jun–jul: 28 dias reamostrados, sinal atenuado, permutação dentro de cada dia (500), 300 réplicas.

| Efeito encolhido em | Fluxo (p ≤ 0,025 / ≤ 0,05) | Original (p ≤ 0,025 / ≤ 0,05) |
|---|---|---|
| 0% | 1,00 / 1,00 | 0,90 / 0,96 |
| 40% | 0,97 / 0,99 | 0,62 / 0,75 |
| 65% | 0,74 / 0,85 | 0,29 / 0,42 |

Com o encolhimento típico do programa, o fluxo tem poder alto. O original fica entre 30% e 75%: uma refutação no original não distingue efeito nulo de efeito pequeno.

## Dependência com o H-DIF-01

Em outubro, os dois testes usam os mesmos minutos. c(x) é testado com log tr D, a medida do H-DIF-01, entre os controles, o que reduz a dependência, mas não a elimina. Os dois vereditos são relatados separadamente. A replicação em novembro é independente do H-DIF-01.

## Aposta de Claude, antes dos dados

| | Outubro | Replicar em novembro, dado outubro confirmado |
|---|---|---|
| Fluxo | ~65% | ~70% |
| Original | ~40% | ~55% |
| Os dois | ~30% | — |
