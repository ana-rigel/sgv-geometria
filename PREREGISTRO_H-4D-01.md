# Pré-registro H-4D-01 — a temperatura como quarta coordenada: forma da fatia e inclinação da nuvem

**Registrado em:** 16/10/2026, antes de escrever o código e antes de calcular qualquer coisa. O arquivo mensal de outubro da Binance ainda não existe nesta data.

**Decisão da Ana (16/10/2026):** "registre os testes e faça a paridade com os meses já abertos para testarmos de fato em outubro".

**Origem:** as páginas "Hipercubo SGV" e "Fatia 4D do SGV" (projeção e corte, no espírito do Miegakure), feitas com dados simulados. Elas reformularam dois testes que a rodada de fatias por tercis (`PREDICAO_fatias_volatilidade.md`) não permitia: a forma da fatia como função contínua da temperatura, e a inclinação da nuvem em 4D. As páginas não são evidência de nada: usam a receita do sintético M, em que o colapso é garantido por construção.

**Quem julga:** `pipeline/confirmatorio_4d.py --julgamento`, uma única vez no GitHub Actions, por disparo manual, sem edição depois do congelamento. Os hashes ficam em `referencia/HASHES_H-4D-01.txt`, gravados depois da paridade.

**Regra da casa:** nenhuma vitória não conquistada será anunciada.

**Ramo:** `confirmatorio/H-4D-01`, a partir de `exploracao/fatias-volatilidade@7d73d7b`.

## Espaço e quarta coordenada

- **Estado:** x_t = (E_norm, jerk, memory_flux) do sgv_original, na régua de caudas com âncora em maio (mediana e q99,5 de |x − mediana| ÷ 3), pelo mesmo código das rodadas anteriores (`explora_geometria_residual.regua`).
- **Temperatura:** σ̂ = `har` (`explora_volatilidade_escondida.estimativas`), causal, a raiz da média das variâncias realizadas de 10, 60 e 240 min.
- **Quarta coordenada:** w_t = log σ̂_t, na **mesma régua** (mediana de maio e q99,5 de |w − mediana| em maio ÷ 3). Com isso os quatro eixos são comparáveis e a nuvem é um objeto 4D.
- **Fatias:** 7 faixas de w pelos quantis 1/7, …, 6/7 de maio (limites fixos para todos os períodos e séries). Uma fatia numa semana é o conjunto de minutos daquela semana com w naquela faixa.
- **Semanas:** blocos de 7 dias (`explora_geometria_residual.semanas`). Nada é treinado numa semana e avaliado em outra: todas as medidas são feitas dentro da semana.

## Séries

- **Real:** BTCUSDT spot 1 min, Binance, SHA-256 conferido.
- **M**, o sintético multiescala da 3ª rodada de volatilidade (`explora_volatilidade_multiescala.gerar_m`), 5 réplicas, sementes 4026 a 4030, gerado a partir de 01/06 com os parâmetros da própria semana. Nele a volatilidade é, por construção, a única variável escondida. As coordenadas e w do M são calculadas pelo mesmo código que as do real, inclusive a estimativa `har` (não o oráculo), para que a comparação seja entre instrumentos iguais.

Não há nula de permutação: a pergunta não é "há associação?" mas "há mais do que num processo em que a temperatura é só zoom?".

## H-4D-01a — a forma da fatia muda com a temperatura?

- **Medida por fatia e semana:** C_jk = covariância 3 × 3 dos estados da fatia j na semana k, exigindo n_jk ≥ 300 minutos. Autovalores λ₁ ≥ λ₂ ≥ λ₃. **Alongamento** s_jk = log(λ₁ / λ₃). É adimensional: não muda se a nuvem inteira for multiplicada por uma constante, então o zoom da temperatura não entra nele.
- **Estatística:** ρ_forma = Spearman entre o índice da fatia j (1 a 7) e s_jk, com todos os pares (j, k) válidos do período agrupados.
- **Validade:** uma semana é válida se tiver ≥ 5 das 7 fatias com n_jk ≥ 300. O período é válido se tiver ≥ 3 semanas válidas, para o real e para cada réplica M. Senão, **INCONCLUSIVO**.
- **Hipótese:** ρ_forma(real) > máximo das 5 réplicas M. A forma da fatia depende da temperatura além do que um processo de volatilidade pura produz.
- **Veredito (outubro, único):**
  - **CONFIRMADA** se ρ_forma(real) > max_M.
  - **NÃO CONFIRMADA** se ρ_forma(real) ≤ max_M. Leitura: a forma que a temperatura "muda" é a mesma que o M muda; a 4ª dimensão é zoom também na forma.
- **Secundários (só leitura):** ρ_forma com s = log(λ₁/λ₂) e log(λ₂/λ₃); a orientação do eixo principal (|cosseno| com cada eixo do cubo) por fatia; a taxa de zoom, inclinação de ½·log det C_jk sobre w médio da fatia (descreve quanto a nuvem incha por unidade de temperatura; no M deve ser ≈ 1).

## H-4D-01b — quanto da quarta dimensão já está no cubo?

- **Medida por semana:** R²_k da regressão linear de w_t sobre (x₁, x₂, x₃, 1) com os minutos da semana k (n ≥ 2.000). É a parte da temperatura que é "inclinação" da nuvem: o quanto σ̂ é redundante com os três eixos.
- **Estatística:** R²_tilt = média de R²_k sobre as semanas válidas do período.
- **Validade:** ≥ 3 semanas válidas para o real e para cada réplica. Senão, INCONCLUSIVO.
- **Hipótese:** min_M ≤ R²_tilt(real) ≤ max_M. A temperatura entra no cubo do mesmo jeito que num processo em que ela é a única variável escondida.
- **Veredito (outubro, único):**
  - **CONFIRMADA** se R²_tilt(real) estiver dentro do envelope das 5 réplicas M.
  - **NÃO CONFIRMADA, mais entrelaçada** se estiver acima do máximo: o real liga temperatura e cubo mais do que o M.
  - **NÃO CONFIRMADA, menos entrelaçada** se estiver abaixo do mínimo: há mais temperatura fora do cubo no real do que no M.
- **Secundários (só leitura):** Spearman(w, x_i) por eixo e semana; R² com termos quadráticos e cruzados (inclinação não linear); o mesmo R² com `ew10` no lugar de `har`.

## Julgamento (outubro/2026)

- **Semanas julgadas:** 01–08, 08–15, 15–22 e 22–29/10. 29–31/10 fica de fora.
- Maio a setembro entram só como âncora da régua, dos quantis das fatias e aquecimento dos sintéticos. Nenhum valor deles é julgado.
- **Sem segunda execução,** sem trocar estimativa, fatias, limiares de n, réplicas, semanas ou mês.
- As duas hipóteses são julgadas cada uma pela sua regra. Não há correção entre elas nem com as outras famílias de outubro (H-DIF, H-DIR, H-FORMA-D, H-VOL, H-SGV-01a), que são independentes e pré-registradas por si.
- Não há p-valor: o critério é o envelope das 5 réplicas, como no H-VOL-01. É um critério fraco contra ruído de amostra, e a leitura precisa dizer isso.

## Meses abertos (paridade e aquecimento)

Antes de outubro, o mesmo script roda jun–jul (localmente) e ago–set (no GitHub Actions), com `--periodo`. Eles servem para:
1. ver se as apostas abaixo estão razoáveis e registrar, por emenda datada, o que elas mudariam. **Os critérios de outubro não mudam.**
2. gravar `resultados/H-4D-01_exploracao_junjul.json`, que o `--paridade` precisa reproduzir exatamente (diferença < 1e-9) antes de o julgamento baixar outubro.

## Apostas de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| a: ρ_forma(real) > 0 (fatia quente mais alongada) | ~65 % |
| a: CONFIRMADA (real acima do envelope M) | ~35 % |
| a: real dentro do envelope M | ~45 % |
| b: CONFIRMADA (dentro do envelope) | ~50 % |
| b: mais entrelaçada que o M | ~30 % |
| b: menos entrelaçada | ~20 % |
| R²_tilt(real) entre 0,2 e 0,5 | ~60 % |
| jun–jul e ago–set dão a mesma classe em a | ~60 % |

## O que confirma e o que não

- **a confirmada:** a quarta dimensão não é só zoom: a nuvem muda de forma com a temperatura mais do que a volatilidade explica. Seria a primeira estrutura "própria" do cubo a sobreviver a uma nula informada, e pediria explicação (acoplamento retorno–volume que muda com σ̂ é a candidata, pelo M35).
- **a não confirmada:** a forma também colapsa; fecha o quadro da rodada de fatias: temperatura = zoom, em tamanho e em forma.
- **b confirmada:** o jeito como a temperatura "vaza" para dentro do cubo (principalmente por E_norm) é o mesmo de um processo de volatilidade pura. Explica por que ela ficou escondida no original: parte dela já estava projetada num eixo.
- **b não confirmada:** o entrelaçamento entre temperatura e cubo difere do M; a direção (mais/menos) diz onde procurar.
- **Em nenhum caso há direção, previsão ou lucro.** São medidas descritivas de geometria, como todas desta linha.

## Emenda 1 (16/10/2026, depois dos meses abertos, antes de outubro)

Jun–jul rodou localmente (`resultados/H-4D-01_exploracao_junjul.json`) e ago–set no Actions (run 38911836311). **Nenhum critério acima muda.** O que muda é a expectativa.

| | jun–jul | ago–set |
|---|---|---|
| ρ_forma real | +0,141 | +0,096 |
| ρ_forma M (mín–máx) | +0,378 a +0,421 | +0,199 a +0,471 |
| classe de a | abaixo do M | abaixo do M |
| R²_tilt linear real | 0,022 | 0,032 |
| R²_tilt linear M | 0,012 a 0,024 | 0,009 a 0,033 |
| classe de b | dentro (CONFIRMADA) | dentro (CONFIRMADA), rente ao máximo |
| R² quadrático real / M | 0,288 / 0,293–0,324 | 0,250 / 0,253–0,279 |
| taxa de zoom real / M | 1,38 / 1,22–1,28 | 1,31 / 1,24–1,30 |

**O que isso diz, antes de outubro:**

1. **a:** a forma da fatia muda com a temperatura *menos* no real do que no M. A aposta "real acima do M" (~35 %) estava errada nos dois períodos; a direção ρ_forma > 0 acertou. Expectativa para outubro: **NÃO CONFIRMADA, abaixo do M** (~75 %). Leitura se repetir: a temperatura é zoom na forma também, e com folga; o M, por ter escala rápida AR(1) com choques gaussianos, produz fatias quentes mais alongadas que o real.
2. **b:** o R² linear é quase zero em todas as séries (0,01 a 0,03). Pela simetria das coordenadas (E_norm e jerk têm sinal), a temperatura não se inclina linearmente sobre o cubo: ela se liga a ele por termos pares, e o R² quadrático (secundário) é que carrega o entrelaçamento, 0,25 a 0,29 no real, no limite inferior ou abaixo do envelope M. O critério primário de b, tal como registrado, é portanto **fraco**: "dentro do envelope" é quase garantido quando todos estão perto de zero, e em ago–set o real ficou a 0,0004 do máximo. Isso fica registrado como defeito de desenho, não se conserta agora. Expectativa para outubro: CONFIRMADA (~60 %), com a ressalva de que confirma pouco. O secundário quadrático será relatado ao lado e é o que vale ler.
3. **Zoom:** a nuvem real incha mais por unidade de temperatura (1,31–1,38) do que o M (1,22–1,30). É descritivo, sem critério, mas aponta para onde o M fica aquém: no real, "mais quente" é um pouco mais "maior" do que a volatilidade estimada sugere.

**Apostas revistas (outubro):**

| Aposta | Antes | Agora |
|---|---|---|
| a CONFIRMADA | ~35 % | ~10 % |
| a abaixo do M | — | ~75 % |
| b CONFIRMADA | ~50 % | ~60 % |
| R² quadrático real abaixo do mínimo M | — | ~55 % |
| taxa de zoom real acima do máximo M | — | ~55 % |
