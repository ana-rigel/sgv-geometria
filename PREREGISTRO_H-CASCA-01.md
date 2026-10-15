# Pré-registro H-CASCA-01: a feature de caudas das cascas acompanha a cauda real dos retornos, num ativo nunca visto

**Registrado em 14/10/2026, antes do código confirmatório e de qualquer download de dados do ativo.**
- **Ramo:** `confirmatorio/H-CASCA-01-ltc`, criado a partir de `confirmatorio/H-DIF-01@174a0bb`.
- **O que não muda:** H-DIF-01, H-CAUDA-01 e C02.1 (pausado) não são alterados.

## O que este teste é, e o que não é

É um teste de **validade de instrumento**. Pergunta se a mudança de forma entre duas cascas (HDR50 + HDR95) mede a mudança no peso da cauda dos retornos de 1 minuto, calculado direto do preço, sem passar pelo SGV.

**Não é um teste de previsão.** As duas medidas descrevem as mesmas janelas. Uma confirmação diria "a casca lê a cauda". Não diria "a casca antecipa algo", nem diria que existe uma dinâmica própria do mercado.

## Origem da hipótese

O pacote `SGV_Navegador_COMPLETO_U031_mercado_20261014.zip` (SHA-256 `f1c7effc…7aae`) tem o relatório `mercado/RELATORIO_assinaturas_BTC_parte2.md`. Ele mediu, no espaço original bruto (régua de caudas), BTCUSDT jun–jul/2026, pares de janelas a 28 h:
- ρ = +0,64 entre a feature de caudas e Δlog(q99,9/mediana de |r|);
- ρ = +0,75 contra a curtose de E_norm (que não é externa).

O relatório propôs este pré-registro.

O script daquela validação não veio no pacote. Reconstruí o cálculo no BTC jun–jul (exploração, `exploracao_cascas/`):
- mesmos 329 de 366 mapas válidos;
- ρ = **+0,638** nos 291 pares de 28 h (o +0,64 do relatório);
- +0,466 contra o máximo |r| (relatório: +0,47);
- +0,753 contra a curtose (relatório: +0,75).

**Mesmo efeito no desenho deste pré-registro (BTC jun–jul):**
- pares sem nenhuma janela repetida: 20 pares, ρ = **+0,656**;
- só o envelope (log V95): ρ = +0,21;
- só o núcleo (log V50): ρ = −0,55, a armadilha do núcleo: cauda engordando parece contração;
- confiabilidade da feature entre 5 sementes do GMM: 0,999.

Os pares do relatório reaproveitam janelas, então o p = 3×10⁻¹²⁷ citado lá não vale como evidência; a evidência efetiva é bem menor. Este desenho usa cada janela uma vez só.

## Dados

- **Ativo:** LTCUSDT spot, klines de 1 minuto da Binance (`data.binance.vision`), SHA-256 conferido pelos arquivos `.CHECKSUM`. Nenhum commit ou arquivo do repositório usa LTC até esta data.
- **Âncora da régua:** maio/2026. Só fornece mediana e escala; nenhuma janela é medida em maio.
- **Julgamento:** 01/06/2026 00:00 UTC a 01/10/2026 00:00 UTC.

## Definições congeladas

- **Coordenadas:** idênticas ao H-CAUDA-01.
  - E_norm e jerk vêm de `build_btc_90d_input_sgv` com `SGVConfig()` (`vendor/sgv_original`, ac6b986).
  - memory_flux = E_norm.ewm(α = 0,05, adjust = False).mean().diff().
- **Régua de caudas** (Ana, `cascas_btc.py`, modo `orig_raw`): por coordenada, (x − mediana de maio) / (q99,5 de |x − mediana| em maio / 3), linear.
- **Janelas:** a janela k cobre os minutos [T₀ + k·28 h, T₀ + k·28 h + 1.500 min), com T₀ = 01/06/2026 00:00 UTC. Entram as janelas que terminam até 01/10/2026 00:00 UTC.
- **Pares:** (janela 2m, janela 2m+1). Cada janela entra em um único par, e há 3 h de intervalo entre A e B.
- **Cascas** (código do pacote, sem alteração; vendorizado em `vendor/u031/u031_casca.py`):
  - **HDR50:** `build_shell(X, seed = 20261009, n = 25)` do M11-I (`vendor/m11i`, instrument.py `15ee5a5d…`).
  - **HDR95:** vem dos mesmos parâmetros GMM2, via `hdr_mesh`, com grade 61³ e extensão ±10.
  - **Validade da janela:** é inválida se tiver menos de 95 % de pontos finitos ou se qualquer casca falhar (cobertura, toque na borda da grade, malha aberta). Não há imputação. Um par vale só se as duas janelas valem.
- **Feature:**
  > caudas = log(V95_B / V95_A)/3 − log(V50_B / V50_A)/3

  Os volumes são os das malhas (trimesh), como em `mercado/assinaturas.py`.
- **Referência externa:**
  > Δlog(q99,9 de |r| / mediana de |r|) entre B e A

  r é o retorno logarítmico de 1 minuto do close, nos mesmos 1.500 minutos de cada janela.

## Hipótese e julgamento (único)

**H-CASCA-01:** ρ de Spearman (caudas, referência) > 0, sobre os pares válidos.

- **p primário:** permutação da referência entre os pares (10.000 réplicas, semente 20261015), unilateral.
- **Confirmada** se p < 0,05 **e** ρ ≥ 0,40.
  - O limiar de 0,40 está ali porque a pergunta é de fidelidade: só existir uma ligação não basta, já que parte dela é mecânica (E_norm é feito do preço).
  - Caso contrário, não confirmada.
- **Validade:** pelo menos 25 pares válidos; abaixo disso, INCONCLUSIVO.
- Sem segunda tentativa com outro ativo, janela, nível de casca ou período.

**Secundários (só leitura, sem julgamento):**
- ρ da feature contra:
  - Δlog curtose de E_norm;
  - Δlog(q99/mediana de |r|);
  - Δlog máx |r|.
- ρ de log V50 sozinho e de log V95 sozinho contra a referência.
- Confiabilidade da feature entre 5 sementes do GMM (20261009 a 20261013).
- Fração de janelas válidas.
- **Nula de pipeline:** retornos, sombras e volume permutados dentro de cada dia a partir de junho, mesma régua e âncora, semente 2026.
  - Ela preserva a distribuição diária de |r|, então espera-se que o ρ **continue alto** nela.
  - Isso não enfraquece o teste: confirma que a leitura é sobre a distribuição dentro da janela, não sobre a ordem dos minutos.

## Ensaio de paridade

Antes de baixar o LTC, o mesmo script roda em BTCUSDT jun–jul (modo `--paridade-btc`). Ele precisa reproduzir:
- o desenho do relatório: mapas a cada 240 min desde 01/06, pares a 28 h, ρ = +0,638 com diferença < 0,01;
- o desenho deste registro no BTC: +0,656 com diferença < 0,01.

## Poder e aposta (antes dos dados)

Com ~40 pares válidos (52 pares possíveis, ~87 % de janelas válidas no BTC), o erro-padrão de ρ fica em ~0,10–0,12:
- ρ verdadeiro = 0,60: chance de ρ̂ ≥ 0,40 de ~95 %;
- ρ verdadeiro = 0,50: ~80 %;
- ρ verdadeiro = 0,40: ~50 %.

**Aposta de Claude: ~75 % de confirmação.** A ligação é em parte mecânica e apareceu igual nos dois desenhos do BTC. Os riscos são:
- o LTC ter caudas que tirem muitas janelas da grade (menos pares);
- a relação ser mais fraca num ativo de menor liquidez.

## Emenda 1 (14/10/2026, antes de qualquer dado do LTC): a expectativa sobre a nula de pipeline estava errada

O ensaio a seco do caminho do julgamento rodou no BTC jun–jul (exploração; dois meses, 20 pares, por isso INCONCLUSIVO pelo mínimo de 25). Ele mostrou o contrário do que escrevi nos secundários:

- a nula de pipeline dá ρ = **+0,08** (25 pares), contra +0,66 no real;
- ρ por semente do GMM: 0,63 a 0,67; confiabilidade 0,9997;
- só núcleo −0,55; só envelope +0,21;
- curtose de E_norm +0,73; q99 +0,81; máximo +0,55.

A permutação dentro do dia mantém o conjunto de retornos de cada dia e destrói a ordem. Se a casca lesse só a distribuição de |r| na janela, o ρ deveria continuar alto. Ele cai, então a ligação passa pelo arranjo no tempo: retornos grandes em sequência, que deslocam E_norm e memory_flux.

Com 20–25 pares a diferença é imprecisa (z ≈ 2,2), e por isso fica como leitura, não como resultado.

**O que muda e o que não muda:**
- **Não muda:** hipótese primária, estatística, limiares, ativo, período e mínimo de pares.
- **Muda:** a frase "espera-se que o ρ continue alto" na nula de pipeline fica retirada. A nula continua secundária e só de leitura.
- **Muda:** se a H-CASCA-01 for confirmada e a nula do LTC também cair, a leitura correta passa a ser "a casca lê a cauda produzida por episódios agrupados no tempo", não "a casca lê a distribuição de |r|".
