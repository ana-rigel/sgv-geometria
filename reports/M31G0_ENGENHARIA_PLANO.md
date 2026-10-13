# M31-G0 — Auditoria de viabilidade causal antes do pré-registro M31-G

**Situação: ENGENHARIA/PROTÓTIPO, NÃO PRÉ-REGISTRO, NÃO TESTE CONFIRMATÓRIO.**
Base `research/m30-volume-reage-choques`; branch `research/m31g0-engenharia-causal`.
Contexto: [Issue #3](https://github.com/ana-rigel/sgv-geometria/issues/3), crítica externa M31.

## Objetivo imediato

Verificar que um cálculo causal de proxies "cone/cintura" pode ser obtido de
candles de BTC 1m **já explorados** e inserido num baseline HAR-X sazonal
sem observar `RV_15` antes de t. Somente engenharia, falta confirmar que
os proxies correspondem às medidas geométricas originais do colaborador.
**NÃO atribuir status de achado do SGV às proxies até receber código+SHA
das medidas de abertura/cintura usadas na investigação de 12/10.**

## Origem, coordenadas e memória

Na barra FECHADA t, `r_t = log(close_t/close_(t-1))`,
`sigma_t = std(r_(t-60)..r_(t-1))`, `z_t=r_t/sigma_t`,
`iota_t = 2*taker_buy_t/volume_t-1`,
`nu_t=log(volume_t)-median(log(volume_(t-1500)..volume_(t-1)))`.
Usar `sgvgeo.flow.flow_coordinates` existente e bloquear dados
descontínuos, timestamps duplicados, volumes negativos e ausentes.
`z_t` e `nu_t` são calculados na mesma barra FECHADA t,
sem usar t+1. A geometria de 6h exige **360 valores finitos**;
em particular 1500 de aquecimento de nu + 360 da janela,
logo o mínimo seguro é >=1860 barras (mais r inicial).

**Duas proxies definidas aqui apenas para auditoria:**
- `cone_proxy_t = sd(z | nu >= q_(2/3)(nu_360)) /
                   sd(z | nu <= q_(1/3)(nu_360))`.
- `waist_proxy_t = P(|iota| <= 0.1 | nu >= q_(2/3)(nu_360))`.
- `cone_volume_proxy_t = log(cone_proxy_t) * nu_t`.
Regra de desempate nos tercis: usar <= e >=, exigir mínimo 60 por cauda.
Se desvios não positivos ou faltantes, registrar *inválido*
(sem backfill). O uso de `log(cone)` em vez da abertura original é
uma convenção de protótipo, NÃO foi aprovado pelo colaborador.
A cintura é massa central de fluxo, NÃO curva/índice topológico.

## Alvo e modelo de engenharia

`RV_15(t)=Σ_(j=1)^15 r_(t+j)^2`. Origem fechada a cada 15 minutos UTC,
sem sobreposição de alvo, primeiro origin após warmup de 1861 candles.
HAR-X B0 de regressoras causais:
log RV passada em 15/60/240/1440 minutos, log média volume 15/60,
|iota_t|, nu_t, fase da hora e do dia sen/cosseno, dummies
de dia da semana. B1 acrescenta log(cone_proxy), waist_proxy,
log(cone_proxy)*nu_t. Todos os transformadores de escala e
hiperparâmetros fit exclusivamente ao passado; B0 e B1 usam
mesmo algoritmo e mesma janela de treino, para comparação justa.
Baseline B0 NÃO garante ainda ser o baseline "mais forte possível".

A implantação de engenharia usa regressão Ridge (λ=1 fixo)
em log(RV), predição de nível com correção de retransf. (smearing)
ajustada NO PASSADO; prevê `E[RV|F_t]` aproximada,
não `exp(E[log RV])` sem correção. Janela móvel máxima 7 dias
de **origens treináveis com alvos já vencidos**.
Nenhum ajuste em t pode usar alvo que termina após t.
Este protótipo utiliza `log(RV+epsilon)` com epsilon fixo em
1e-12 em unidades de retornos log (sem conversão a porcentagens),
somente para engenharia; escala e pisos deverão ser revisados e
congelados antes de teste em dados virgens.

## Saídas sem escolha retroativa

1. Testes de sanidade em dados sintéticos: causalidade point-in-time,
   reação das proxies às perturbações plantadas, rótulo amadurecido,
   invariância de diferença de QLIKE e deviança a mudança de unidade.
2. Se a execução de engenharia em BTC maio–julho for viável,
   reportar cobertura e invalidade de features, custo de cálculo,
   quantidade de origens e rastreabilidade. **Não usar QLIKE
   exploratória para otimizar regras ou declarar vitória.**
3. Distinguir `B0 + proxies` de contribuição de geometria **genuína**.
   Para confirmação futura, comparar ainda com `B0+` que incorpora
   controles condicionais tradicionais com mesma capacidade:
   condicionamento RV×volume e concentração de fluxo.

**Pendente:** receber do colaborador o commit e fórmulas exatas do
estudo “cone 2,1×, persistência 0,51; cintura episódica”, confirmar
status ETHUSDT 1m em outros projetos e escolher holdout com acesso
controlado. Nenhum destes dados será tocado no M31-G0.

Não reabrir resultados H-FR M22 nem BTC out–dez reservado, e não
confundir engineering pilot com ciência confirmatória.
