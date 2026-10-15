# Pré-registro H-FORMA-D-02 (desacoplamento entre a forma de D e a forma da casca)

**Congelado em:** 15/10/2026, antes de qualquer acesso aos dados de outubro e de novembro de 2026. O arquivo mensal de outubro da Binance ainda não existe nesta data.

**Decisão de Ana (15/10/2026):** "registre e congele".
- Julgamento em **outubro/2026**, como no H-FORMA-D-01.
- **Replicação em novembro/2026**, com o mesmo código e sem nenhuma mudança.

**Quem julga:** `pipeline/confirmatorio_forma_casca.py`, executado no GitHub Actions deste repositório, sem edição depois deste commit. Os hashes estão em `referencia/HASHES_H-FORMA-D-02.txt`.
- Julgamento: `--periodo confirmatorio`.
- Replicação: `--periodo replicacao`.

**Regra da casa:** nenhuma vitória não conquistada será anunciada. O que não passar aqui não passou.

Nada do H-DIF-01, do H-DIR-01 nem do H-FORMA-D-01 foi alterado. Este ramo só acrescenta arquivos ao ramo `exploracao/forma-D-casca`, onde está a exploração que motiva o teste.

## A hipótese, em uma frase

No espaço de fluxo, a forma de D (para onde o mercado é empurrado) e a forma da casca (onde o mercado fica) mudam juntas **menos** no mercado real do que a própria construção dos dados obriga.

## O que foi visto na exploração e motiva o teste

O Navegador SGV (pesquisa D, 15/10/2026) mediu a forma do tensor de difusão D e a forma da casca a cada 4 h. Depois mediu as mudanças entre mapas consecutivos. Em cada período, a nula de pipeline teve uma única réplica (semente 2026).

| Espaço, dFD×dFS no mesmo mapa | jun–jul real | jun–jul nula | ago–set real | ago–set nula |
|---|---|---|---|---|
| Fluxo | +0,627 [0,55; 0,70] | +0,878 [0,83; 0,91] | +0,639 [0,56; 0,70] | +0,896 [0,87; 0,92] |
| Original | +0,198 | +0,117 | +0,362 [0,28; 0,44] | +0,120 [0,02; 0,22] |

- Em ago–set a previsão foi registrada antes da rodada (`PREDICAO_forma_D_casca_agoset.md`, commit f5e638b).
  - No fluxo, ela **repetiu** pelo critério registrado: ICs sem sobreposição.
  - No original, ela **errou**: a previsão era "sem diferença", e o real acoplou mais que a nula.
- Nos dois espaços e nos dois períodos, nenhuma defasagem com D antecedendo a casca ficou acima da nula.

**Ressalvas da exploração:**
- **Ago–set não é fora da amostra no sentido estrito.** Esses meses tinham sido abertos em 13/10 para o H-σRTT-01, mas ninguém mediu forma de D ou de casca neles antes da previsão.
- **Quatro meses são um único regime de mercado de 2026.**
- **O efeito no original mudou de tamanho** entre os dois períodos.
  - Com uma réplica: +0,08 e +0,24.
  - Com as 20 réplicas, jun–jul dá +0,11 (abaixo).
  - Por isso o original entra só como secundária.
- **A nula permuta dentro do dia** e destrói a ordem temporal intradiária. Uma confirmação diz que o desacoplamento depende dessa ordem, e não identifica o mecanismo.

## Hipóteses

### H-FORMA-D-02, primária: um teste, α = 0,05 unilateral

No espaço de fluxo (z, ι, ν), mudanças de forma entre mapas consecutivos de 4 h, no mesmo mapa (j = 0):

> Δ = ρ_S(dFD, dFS)_real − média das 20 réplicas de ρ_S(dFD, dFS)_nula **< 0**

### Secundárias: Holm com m = 2, informativas; não mudam o veredito da primária

| Espaço | Medida | Sinal registrado de Δ |
|---|---|---|
| Fluxo | angD×angS@0 (ângulo do eixo principal) | real < nula |
| Original | dFD×dFS@0 | real > nula (acopla mais) |

### Só leitura, sem veredito

D antecede a casca além da nula? dFD×dFS@+1 e @+2, nos dois espaços, com p para real > nula. Expectativa registrada, pela exploração: **não**.

Também só leitura: o posto do ρ real entre as 20 réplicas da nula (p mínimo 1/21) e a tabela descritiva completa (5 pares × 5 defasagens, real e réplica 0).

## Definições congeladas

As medidas são idênticas às de `pipeline/explora_forma_D_casca.py`. A paridade está conferida abaixo.

- **Coordenadas, gaussianização e âncora:** as do H-DIF-01.
  - Fluxo: `flow_coordinates` do M11-I.
  - Original: E_norm e jerk do `build_btc_90d_input_sgv` (sgv_original ac6b986) e memory_flux = Δ EMA₀,₀₅(E_norm).
  - Gaussianização por postos com âncora congelada em maio/2026.
- **Mapas:** a cada 240 min a partir de 00:00 UTC do primeiro dia do período, com janela dos últimos 1.500 min (fechados no minuto do mapa).
  - **Forma de D:** D̄ / tr D̄, onde D̄ é a média do tensor D(x) em 400 estados da janela, igualmente espaçados. Núcleo gaussiano h = 0,45 sobre os pares (x_t, x_{t+1} − x_t) da própria janela.
  - **Forma da casca:** Σ_mix / tr Σ_mix, a covariância total do GMM de 2 componentes (covariância cheia, reg 1e-4, n_init 2, semente 20261009 + k).
- **Mudanças entre o mapa k−1 e o mapa k:**
  - dFD e dFS = norma de Frobenius da diferença das formas;
  - angD e angS = ângulo entre os eixos principais.
- **Nula de pipeline:** 20 réplicas, sementes 2026 a 2045.
  - Em cada réplica, retornos, sombras, volume e fração de agressão são permutados dentro de cada dia UTC a partir do início do período.
  - Mesmas fórmulas, mesma âncora, mesmos mapas.
  - A réplica 0 (semente 2026) é a nula da exploração.
- **Estatística:** Δ = ρ de Spearman real − média dos 20 ρ de Spearman das réplicas, sobre os mapas em que todas as séries são finitas.
- **Teste:** bootstrap pareado por blocos de dia UTC.
  - B = 2.000, semente 20261016.
  - Em cada reamostragem, os mesmos dias entram no real e nas 20 réplicas.
  - p unilateral = (1 + nº de Δ* do lado contrário de 0) / (B + 1).
  - O bootstrap usa a mesma semente em sequência para a primária, as secundárias e as leituras, nessa ordem.
- **Períodos:**
  - **Julgamento:** mapas de 01/10 00:00 a 31/10 20:00 UTC, cerca de 186 mapas e 185 mudanças. Setembro entra só na janela dos primeiros mapas e no aquecimento dos filtros causais.
  - **Replicação:** mapas de 01/11 a 30/11, mesmo código. Outubro entra só como aquecimento.
- **Sem:** exclusão de dias, winsorização, troca de h, de janela, de número de componentes, de medida ou de número de réplicas depois de ver os dados.

## Como se lê

- **Outubro decide.** A primária é *confirmada* se p < 0,05 em outubro.
- **Novembro replica.** O mesmo critério, rodado em novembro, diz se a confirmação se *replica*. O resultado de novembro é relatado à parte e não muda o veredito de outubro.
- **Confirmada (e replicada):** no fluxo, a forma do empurrão local e a forma da região ocupada têm um grau de liberdade próprio, que a construção dos dados não impõe e que depende da ordem temporal dentro do dia. O desacoplamento passa a ser grandeza descritiva do programa.
- **Refutada:** o acoplamento entre as duas formas no fluxo é o que as fórmulas impõem, dentro do que 31 dias conseguem distinguir.
- **Em nenhum caso há previsão, direção ou lucro.**
  - A hipótese é de acompanhamento no mesmo mapa, não de antecedência.
  - A exploração não achou D antecedendo a casca.

## Ensaio de paridade (jun–jul/2026), referência congelada

Os números estão em `referencia/H-FORMA-D-02_exploracao_referencia.json`, gerado por este mesmo código com as 20 réplicas.

As séries do real e da réplica 0 batem com `resultados/forma_D_casca_junjul.json`, da exploração original. A diferença máxima está em `referencia/H-FORMA-D-02_paridade_exploracao.txt`.

A diferença foi **0** em todas as séries: dFD, dFS, angD, angS, dcbar, d512, θ e vol, real e réplica 0, nos dois espaços.

Com 20 réplicas, jun–jul dá:

| Medida | real | nula: média de 20 réplicas [mín; máx] | Δ | IC 95% de Δ | p unilateral (Holm) |
|---|---|---|---|---|---|
| **Primária**, fluxo dFD×dFS@0 | +0,627 | +0,871 [0,841; 0,903] | **−0,244** | [−0,320; −0,168] | 0,0005 |
| Secundária, fluxo angD×angS@0 | +0,632 | +0,824 [0,783; 0,858] | −0,192 | [−0,277; −0,118] | 0,0005 (0,0010) |
| Secundária, original dFD×dFS@0 | +0,198 | +0,091 [0,024; 0,173] | +0,107 | [+0,011; +0,201] | 0,0155 (0,0155) |

Leituras "D antecede", com Δ para real > nula:

| Espaço | @+1 | @+2 |
|---|---|---|
| Fluxo | −0,058 | −0,145 |
| Original | −0,081 | −0,003 |

Nenhuma é positiva.

**O que as 20 réplicas mudaram em relação à leitura de uma réplica só:**
- No fluxo, o ρ real fica abaixo das 20 réplicas, nas duas medidas.
- No original, o ρ real de jun–jul fica acima das 20 réplicas. Com uma réplica só, esse caso parecia "sem diferença clara".
- O desvio-padrão entre as réplicas é de cerca de 0,013 no fluxo. A variabilidade da nula é pequena perto de Δ.

Estes números são exploração: os mesmos dados que motivaram a hipótese. Não contam como evidência confirmatória.

O workflow refaz este ensaio antes de baixar qualquer mês posterior a julho. Ele exige diferença < 2e-6 nas séries dFD, dFS, angD e angS (real e réplica 0) e nos 21 ρ da primária.

## Poder

Simulado só com as séries da exploração (`pipeline/poder_forma_casca.py`, `referencia/H-FORMA-D-02_poder.json`):
- 31 dias sorteados com reposição dos 122 dias de jun–set;
- o mesmo teste, com B = 1.000;
- 400 réplicas;
- encolhimento = deslocamento de Δ em direção à nula.

A simulação usa uma só réplica da nula, então é conservadora.

Probabilidade de p < 0,05 em 31 dias:

| Efeito encolhido em | Primária, fluxo dFD×dFS (Δ̂ = −0,259) | Fluxo angD×angS (Δ̂ = −0,181) | Original dFD×dFS (Δ̂ = +0,174) |
|---|---|---|---|
| 0% | 1,00 | 0,99 | 0,62 |
| 40% | 0,95 | 0,76 | 0,32 |
| 65% | 0,59 | 0,41 | 0,17 |
| 80% | 0,26 | 0,18 | 0,11 |

- **Primária:** poder alto se o efeito encolher até ~40%. Ele já se repetiu do mesmo tamanho em dois períodos (−0,25 e −0,26). Com o encolhimento típico do programa, 40–65%, o poder fica entre 0,6 e 0,95.
- **Original:** poder baixo mesmo sem encolhimento. Uma refutação no original não distingue efeito nulo de efeito pequeno.
- **Replicação:** novembro tem 30 dias, poder praticamente igual.

## Dependências

- **Com o H-FORMA-D-01 e o H-DIF-01:** em outubro, os três usam os mesmos minutos, mas medem coisas diferentes.
  - O H-DIF-01 e o H-FORMA-D-01 testam se tamanho e forma de D antecedem amplitude nos 5 min seguintes.
  - Este testa como a forma de D muda junto com a forma da casca a cada 4 h.
  - Os vereditos são relatados separadamente, sem correção conjunta entre pré-registros.
- **Com o ajuste de régua em teste em outro chat:** este teste usa a régua gaussianizada (âncora de maio) e a covariância do GMM2. Não usa a régua de caudas, nem as cascas HDR, nem o limiar MC. A assinatura M11-I (d512, θ) entra só na tabela descritiva.

## Aposta de Claude, antes dos dados

| | Outubro | Replicar em novembro, dado outubro confirmado |
|---|---|---|
| Primária (fluxo, dFD×dFS) | ~80% | ~85% |
| Secundária fluxo angD×angS | ~65% | — |
| Secundária original (acopla mais) | ~30% | — |
