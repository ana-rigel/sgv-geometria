# Predição do teste 36b (adendo ao 36: o relógio que aprende prevê melhor que o calendário no mundo real?)

20/10/2026 · escrita antes da conta · dados: resultados_teste36.json (0b14619), sem rodar nada de novo · Ana Rigel

## De onde vem

O J3 do teste 36 mostrou que, nos seis lugares de MT, μ **andou** de +10 a +25 dias de 2018 a 2025, na direção do atraso das águas. Mas não mediu se as **previsões** do relógio que aprende erraram menos que as do calendário fixo (μ₀ = média das entradas de 2010–2017, o calendário do teste 35). Essa é a pergunta da placa: prever aprendendo é melhor do que não aprender?

**Declaração:** as entradas de 2018–2025 e as previsões do relógio já estão publicadas em resultados_teste36.json e foram vistas ao abrir o arquivo. A comparação com o calendário não foi calculada. O laço e η = 0,3 são os do teste 36, sem mudança.

## Medida

- Para cada lugar e cada ano y de **2019 a 2025** (7 anos × 6 lugares = 42 previsões): o erro do relógio é e_y = entrada_y − p_y, com p_y = μ antes de ver a entrada y; o erro do calendário é c_y = entrada_y − μ₀. O ano de 2018 fica fora, porque ali p = μ₀.
- **EAM** = média de |erro|. **Viés** = média do erro.
- Intervalo por bootstrap **sobre os anos** (os 7 anos sorteados com reposição, os mesmos para os seis lugares, porque o ano é clima comum aos lugares), 10.000 reamostras, semente 361.

## Conta prévia (com as conclusões do 35 e do 36, sem a comparação)

O calendário tem viés de ≈ −13 dias (as águas entraram ≈ 13 dias mais tarde em 2018–2025) e espalhamento σ ≈ 15–20 dias entre anos. O relógio vai removendo esse viés aos poucos, com fração 1 − 0,7ⁿ, mas treme ≈ 0,42σ ≈ 6–8 dias e corre atrás dos anos extremos: depois de um ano muito tardio, ele espera tarde demais no ano seguinte. Com σ maior que o viés, o ganho no EAM deve ser pequeno, de 1 a 4 dias. Com 7 anos, o intervalo deve ser largo.

## Critérios

**J1, prevê melhor:** EAM(relógio) − EAM(calendário) nas 42 previsões **≤ −2 d**, com o limite superior do intervalo **< 0**.

**J2, prevê melhor por lugar:** EAM(relógio) < EAM(calendário) em **≥ 4 dos 6** lugares.

Relatado: viés dos dois por lugar e no total; a diferença ano a ano (média nos lugares).

## Apostas (Claude, antes da conta)

- **J1 passa: 20 %.** O ganho deve aparecer na média, mas 7 anos dificilmente fecham o intervalo.
- **Diferença no EAM total ≤ −2 d (só a primeira metade do J1): 50 %.**
- **J2 passa: 55 %.**
- **O viés do relógio fica menor em módulo que o do calendário no total: 85 %.** É o que o μ andando significa.

## O que fecha

- **J1 passa:** o relógio que aprende já é útil para a placa em MT, além de ser a assinatura de aprendizado do 36.
- **J1 reprova, viés menor:** ele aprende na direção certa, mas com um evento por ano o ganho ainda se perde no ruído entre anos. Para a placa, isso reforça o caminho dos eventos frequentes (desenho do laço do ato).
- **Viés não menor:** o μ andou e mesmo assim não corrigiu o viés das previsões, porque correu atrás dos anos extremos. O passo η precisaria ser reavaliado com dados reais.
