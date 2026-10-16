# Pré-registro H-TEMPO-01 — memória da volatilidade em lei de potência (a) e reversão na borda do cubo (b)

**Registrado em:** 16/10/2026, antes de escrever o código e antes de calcular qualquer coisa. O arquivo mensal de outubro da Binance ainda não existe nesta data.

**Decisão da Ana (16/10/2026):** "sim registre e também esse [...] faça como o anterior a paridade e depois outubro".

**Origem:** duas perguntas que ficaram da rodada de auto-similaridade temporal (`LEITURA_autosimilaridade_temporal.md`): (a) a memória da volatilidade que o sintético M fecha em 10 minutos é exponencial por construção; o real é lei de potência em horas? (b) a borda agitada do cubo some ao agregar para 15 min, o que sugere que ela é feita de sequências de minutos que se cancelam: os minutos da borda revertem mais que os do núcleo?

**Quem julga:** `pipeline/confirmatorio_tempo.py --julgamento`, uma única vez no GitHub Actions, por disparo manual, sem edição depois do congelamento. Hashes em `referencia/HASHES_H-TEMPO-01.txt`, gravados depois da paridade.

**Regra da casa:** nenhuma vitória não conquistada será anunciada.

**Ramo:** `confirmatorio/H-TEMPO-01`, a partir de `exploracao/autosimilaridade-temporal@efd0d9b`.

## Séries

- **Real:** BTCUSDT spot 1 min, Binance, SHA-256 conferido. r_t = retorno log de 1 min do fechamento.
- **M**, o sintético multiescala (`explora_volatilidade_multiescala.gerar_m`), 5 réplicas, sementes 4026 a 4030, gerado a partir de 01/06. Nele a memória da volatilidade é, por construção, a soma de duas exponenciais (escala lenta = caminho real suavizado em 61 min; escala rápida AR(1)) e os choques são gaussianos sem reversão. Ele é a nula informada dos dois testes.

## H-TEMPO-01a — a memória da volatilidade é lei de potência?

- **Série de memória:** a_t = |r_t| / s(h_t), em que s(h) é a mediana de |r| por minuto do dia (1.440 valores) estimada em **maio** (âncora). Isso tira a sazonalidade intradiária, que faria a autocorrelação ter um calombo em 24 h. A mesma s(h) de maio é usada para o real e para o M.
- **Autocorrelação:** ρ(τ) de a_t nos atrasos τ de uma grade geométrica fixa: 1, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45, 64, 91, 128, 181, 256, 362, 512, 724, 1024, 1440 minutos (21 atrasos), estimada sobre o período inteiro agrupado (não por semana), ignorando pares que cruzam buracos.
- **Ajustes, por mínimos quadrados em log ρ, só nos atrasos com ρ > 0:**
  - **Potência:** log ρ = a − β·log τ. Guarda β e R²_pot.
  - **Exponencial:** log ρ = a − τ/θ. Guarda θ e R²_exp.
- **Estatística primária:** Δ_R² = R²_pot − R²_exp. Positivo = a reta em log-log explica melhor que a exponencial.
- **Validade:** ρ(τ) > 0 em ≥ 15 dos 21 atrasos para o real e para cada réplica M. Senão, INCONCLUSIVO.
- **Hipótese:** Δ_R²(real) > máximo das 5 réplicas M **e** 0,1 ≤ β(real) ≤ 0,6. O real é mais lei-de-potência do que um processo de duas exponenciais, com expoente na faixa da literatura.
- **Veredito (outubro, único):**
  - **CONFIRMADA** se as duas condições valerem.
  - **NÃO CONFIRMADA** senão, dizendo qual falhou.
- **Secundários (só leitura):** β, θ, R²_pot e R²_exp de cada série; o primeiro atraso em que ρ_real sai do envelope das 5 réplicas M (onde o M "descola"); o mesmo ajuste com log σ̂ (`har`) no lugar de a_t.

## H-TEMPO-01b — a borda do cubo reverte mais que o núcleo?

- **Estado:** x_t = (E_norm, jerk, memory_flux) na régua de caudas com âncora em maio (`explora_geometria_residual.regua`). Extremidade = max |x_i|.
- **Grupos, por semana:** **borda** = minutos com extremidade ≥ 3; **núcleo** = minutos com extremidade < 1.
- **Reversão por grupo e semana:** φ_g = Σ r_t·r_{t+1} / Σ r_t², com t no grupo g. É o coeficiente AR(1) restrito ao grupo; negativo = reversão.
- **Estatística:** Δφ = φ_borda − φ_núcleo, agrupando as semanas válidas do período com peso pelo número de minutos da borda.
- **Validade:** ≥ 100 minutos de borda por semana; ≥ 3 semanas válidas para o real e para cada réplica. Senão, INCONCLUSIVO.
- **Hipótese:** Δφ(real) < mínimo das 5 réplicas M. A borda reverte mais do que um processo com os mesmos estados e choques gaussianos sem reversão.
- **Veredito (outubro, único):**
  - **CONFIRMADA** se Δφ(real) < min_M.
  - **NÃO CONFIRMADA** senão: a borda não tem reversão própria além da que a construção do cubo já produz no M.
- **Secundários (só leitura):** φ por grupo em cada série; o mesmo com borda ≥ 5; reversão a 5 min (Σ r_t·R_{t+1..t+5} / Σ r_t²); fração de trocas de sinal por grupo; Δφ por semana.

**Ressalva registrada:** a extremidade em t inclui r_t (E_norm é energia dos retornos), então a borda é, em parte, "minutos de retorno grande", e reversão depois de retorno grande é efeito conhecido de microestrutura (bounce). O M tem a mesma construção de estado, por isso a comparação é justa: a pergunta é se há reversão **além** da que a construção impõe.

## Julgamento (outubro/2026)

- **Semanas:** 01–08, 08–15, 15–22 e 22–29/10. Para (a), as 4 semanas são agrupadas numa série só (≈ 40 mil minutos; o atraso de 1.440 min cabe).
- Maio a setembro entram só como âncora (s(h), régua) e aquecimento dos sintéticos. Nenhum valor deles é julgado.
- **Sem segunda execução,** sem trocar grade de atrasos, limiares, réplicas, semanas ou mês.
- As duas hipóteses são julgadas cada uma pela sua regra, sem correção entre elas nem com as outras famílias de outubro. Não há p-valor: o critério é o envelope das 5 réplicas, como no H-VOL-01 e no H-4D-01, e isso é um critério fraco contra ruído de amostra.

## Meses abertos (paridade e aquecimento)

Jun–jul localmente e ago–set no Actions, com `--periodo`. Servem para rever as apostas por emenda datada (critérios não mudam) e para gravar `resultados/H-TEMPO-01_exploracao_junjul.json`, que o `--paridade` reproduz exatamente (diferença < 1e-9) antes de outubro.

## Apostas de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| a: real com Δ_R² > 0 (log-log mais reto que exponencial) | ~75 % |
| a: β real entre 0,1 e 0,6 | ~65 % |
| a: CONFIRMADA (acima do envelope M e β na faixa) | ~50 % |
| a: o M descola do real antes de 2 h | ~60 % |
| b: Δφ real < 0 (borda reverte mais que o núcleo) | ~75 % |
| b: CONFIRMADA (abaixo do envelope M) | ~55 % |
| b: Δφ do M ≈ 0 (|Δφ_M| < 0,05 em todas as réplicas) | ~60 % |

## O que confirma e o que não

- **a confirmada:** a volatilidade do BTC tem memória de longo alcance que duas exponenciais não imitam no intervalo de 1 min a 1 dia. Não contradiz o H-VOL-01, que mede a memória *dado o estado e σ̂* numa janela de 10 min; diz que, em horas, o M é um sintético incompleto e que o fechamento de 10 min não se estende.
- **a não confirmada:** até 1 dia, duas exponenciais bastam; a lei de potência, se existir, está em escalas que estes dados não alcançam.
- **b confirmada:** a borda agitada é feita de impacto transitório: minutos grandes seguidos de reversão parcial. Explica por que ela some ao agregar e liga o cubo à microestrutura.
- **b não confirmada:** a borda some ao agregar só por suavização estatística; não há reversão própria.
- **Em nenhum caso há direção, previsão ou lucro.** A reversão da borda, se existir, é de frações de ponto base por minuto e já é conhecida da literatura; não é sinal operável, e a fila de 2/09 já mostrou isso.

## Emenda 1 (16/10/2026, depois dos meses abertos, antes de outubro)

Jun–jul local (`resultados/H-TEMPO-01_exploracao_junjul.json`), ago–set no Actions (run 38926616887). **Nenhum critério muda.**

| | jun–jul | ago–set |
|---|---|---|
| a: ΔR² real / M (mín–máx) | +0,547 / +0,503 a +0,539 → **acima** | +0,498 / +0,488 a +0,532 → dentro |
| a: β real / M | 0,13 / 0,15–0,16 | 0,18 / 0,24–0,26 |
| a: veredito pela regra | CONFIRMADA (por 0,008) | NÃO CONFIRMADA |
| b: Δφ real / M | −0,042 / −0,006 a +0,061 → **abaixo** | +0,001 / −0,067 a +0,021 → dentro |
| b: φ_borda / φ_núcleo real | −0,023 / +0,019 | +0,025 / +0,025 |
| b: veredito pela regra | CONFIRMADA | NÃO CONFIRMADA |

**Erro de desenho no (a), reconhecido:** o pré-registro diz que a memória do M é "soma de duas exponenciais por construção". Está errado. A escala lenta do M é o **caminho real de volatilidade suavizado em 61 min**, então o M herda do real toda a memória de horas e dias. Por isso o M também parece lei de potência (ΔR² 0,49–0,54, β 0,15–0,26) e o real só se distingue dele pela escala rápida e pela distribuição dos choques. O teste (a), como registrado, não compara lei de potência com exponencial; compara o real com um processo que já tem a memória longa do real. Ele fica, porque a regra da casa não permite trocar o critério depois de ver os dados, mas a leitura em outubro precisa dizer que "CONFIRMADA" ou "NÃO CONFIRMADA" aqui fala da escala rápida, não da forma da memória longa. O teste certo, para outra rodada: comparar o real com um sintético cuja escala lenta seja um AR(1) **ajustado**, não o caminho real; ou ajustar diretamente a ρ(τ) do real às três formas e comparar por critério de informação.

**Descritivo que vale guardar:** ρ(τ) do real cai de 0,27–0,31 em τ = 1 para 0,08–0,09 em τ = 1.024 min, com β 0,13–0,18 (abaixo dos 0,2–0,4 da literatura para ações, mas na faixa dos registros para cripto em 1 min), e sobe para 0,16 em τ = 1.440: o perfil s(h) de maio não remove toda a sazonalidade diária dos períodos seguintes. O `har` dá β 0,12 e ΔR² de +0,14 a −0,05: em log σ̂ a diferença entre as formas é pequena.

**Leitura do (b) antes de outubro:** em jun–jul a borda reverte de verdade (−0,023 contra +0,019 do núcleo, e −0,070 em 5 min), e o M não. Em ago–set a reversão sumiu (φ_borda = φ_núcleo = +0,025). Ou a reversão da borda é de regime (jun–jul teve microestrutura diferente), ou o jun–jul foi acaso. Outubro decide com uma só chance e critério fraco. Se não confirmar, "a borda some ao agregar só por suavização" é a leitura, e a hipótese do bounce fica sem apoio.

**Apostas revistas (outubro):**

| Aposta | Antes | Agora |
|---|---|---|
| a: CONFIRMADA | ~50 % | ~20 % |
| a: β real entre 0,1 e 0,6 | ~65 % | ~85 % |
| b: Δφ real < 0 | ~75 % | ~55 % |
| b: CONFIRMADA | ~55 % | ~30 % |
