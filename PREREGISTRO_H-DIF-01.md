# Pré-registro H-DIF-01 (campo de difusão) e H-DIR-01 (direção)

**Congelado em:** 13/10/2026, antes de qualquer acesso aos dados de outubro de 2026.
**Período de julgamento:** 01/10/2026 a 31/10/2026 (BTCUSDT spot, klines 1m da Binance, SHA-256 conferido).
**Quem julga:** `pipeline/confirmatorio_dif.py --periodo confirmatorio`, executado no GitHub Actions deste repositório, sem edição depois deste commit (hashes em `referencia/HASHES_PREREGISTRO.txt`).
**Regra da casa:** nenhuma vitória não conquistada será anunciada. O que não passar aqui não passou.

## O que foi visto na exploração (jun–jul/2026) e motiva o teste

Em dois espaços de estados a 1 minuto — fluxo (z, ι, ν) e original (E_norm, jerk, memory_flux) — o campo de difusão D(x) (variância local do passo, estimado por núcleo na semana anterior) carrega informação sobre a amplitude dos 5 minutos seguintes que a volatilidade escalar não carrega: ρ parcial de Spearman de log tr D(x_t) com log Range_{t+5}, com controles fortes e log ρ(x_t), de **−0,065 no fluxo** e **+0,046 no original** (8 semanas, todas do mesmo sinal), contra ≈ +0,01 na nula de pipeline. Nenhuma medida direcional sobreviveu a nenhuma etapa (régua, varredura, deriva, direção simulada: todas ≈ 0, dentro da faixa das nulas).

## Hipóteses

### H-DIF-01 — família de 2 testes, Holm, α = 0,05

Para cada espaço, com o campo da semana k−1 avaliado nos minutos da semana k:

- **H-DIF-01/fluxo:** ρ_parcial(log tr D(x_t), log Range_{t+5} | controles, log ρ(x_t)) **< 0**.
- **H-DIF-01/original:** a mesma correlação **> 0**.

Os sinais opostos são os observados na exploração e fazem parte da hipótese: no fluxo as regiões mais agitadas do espaço "gastam" a amplitude; no original, as regiões agitadas são as do preço já em deslocamento, onde o Range seguinte é maior.

### H-DIR-01 — família de 2 testes, Holm, α = 0,05 — expectativa registrada: NULO

- Para cada espaço: ρ_parcial(μ_r(x_t), r_{t→t+15} | controles direcionais) ≠ 0 (bilateral), onde μ_r(x) = E[r_{t+1} | x] estimado por núcleo na semana anterior.

Registra-se este teste para que o resultado "não há direção" seja um resultado, não uma ausência. Na exploração: fluxo +0,004 (p 0,75), original +0,021 (p 0,13), nulas com a mesma magnitude.

## Definições congeladas

- **Coordenadas:** fluxo = `flow_coordinates` do M11-I (vendor/m11i); original = E_norm e jerk do `build_btc_90d_input_sgv` do sgv_original ac6b986 (vendor/sgv_original) e memory_flux = Δ EMA₀,₀₅(E_norm). Gaussianização por postos (`gaussianize`) com âncora congelada em maio/2026.
- **Campo:** núcleo gaussiano isotrópico, h = 0,45. tr D(x) = E_w[|s|²] − |E_w[s]|², com s o passo de 1 min; log ρ(x) = log(massa do núcleo / n); μ_r(x) = E_w[r_{t+1}]. Treino: todos os minutos da semana anterior.
- **Semanas:** blocos de 7 dias a partir de 24/09/2026 (só treino) → julgadas 01–08, 08–15, 15–22, 22–29/10; o resto de outubro (< 5 dias) fica de fora. Agosto–setembro entram apenas como aquecimento dos filtros causais e como campo da semana 0; nenhum valor deles é julgado.
- **Alvo H-DIF:** log(max high − min low dos 5 min seguintes), em janelas não sobrepostas de 5 min.
- **Controles H-DIF (fortes):** log σ de 10/30/60 min; log σ de 1 dia e 1 semana (HAR); retornos com sinal de 5 e 30 min; log-volume médio de 10 e 60 min; dummies de hora UTC; log ρ(x_t). Correlação parcial de Spearman: postos de x e y regredidos nos controles (MQO) e correlacionados.
- **Alvo H-DIR:** retorno log dos 15 min seguintes, janelas não sobrepostas de 15 min. **Controles:** retornos 5/30 min, log σ 10/30/60, hora, ι médio de 5 min.
- **Estatística primária:** ρ de Spearman sobre os pares de resíduos agrupados das 4 semanas (cada semana centrada em si). p por permutação do alvo dentro de cada dia (B = 5.000, semente 20261013), unilateral no sinal registrado; bilateral para H-DIR. Holm com m = 2 dentro de cada família.
- **Secundário (só leitura):** bootstrap da série de ρ semanais; nula de pipeline (retornos, sombras, agressão e volume permutados dentro de cada dia a partir de 24/09, mesmas fórmulas, semente 2026).
- **Sem** exclusão de dias, sem winsorização, sem ajuste de h ou dos controles depois de ver outubro.

## Poder e aposta (antes dos dados)

Com ≈ 8.000 janelas de 5 min, o erro-padrão de ρ sob a nula é ≈ 0,011. Se o efeito se mantiver (0,046/−0,065) o poder é > 95 % nos dois espaços; se encolher pela metade, ≈ 55 % (original) e ≈ 85 % (fluxo).

Aposta de Claude: H-DIF-01 **original 55 %, fluxo 60 %, ambos 40 %**. H-DIR-01: **70 % nenhum confirmado, 25 % um (provavelmente o original, frágil), 5 % os dois**.

## O que confirma e o que não

- H-DIF-01 confirmada em um espaço: D(x) carrega informação geométrica própria sobre a amplitude futura naquele espaço (0,2–0,4 % de R² além do melhor modelo escalar de vol) — descritiva, não lucrativa a 1 min. Refutada: o campo de difusão continua um objeto descritivo válido (forma e persistência não dependem deste teste), sem informação própria sobre o futuro.
- H-DIR-01 confirmada: seria a primeira evidência direcional do programa e exigiria replicação em novo período antes de qualquer uso. Não confirmada (esperado): "sem direção a 1–15 min" passa a ser resultado registrado.

## Ensaio de paridade

`referencia/H-DIF-01_exploracao_referencia.json` é a saída do mesmo script em jun–jul/2026. O workflow refaz esse ensaio antes de abrir outubro e exige diferença < 1e-6 nos ρ semanais.

## Quando rodar

O arquivo mensal `BTCUSDT-1m-2026-10.zip` da Binance só existe depois do fim do mês. O workflow é de disparo manual (`workflow_dispatch`), para que nenhum push a este ramo leia outubro por acidente.
