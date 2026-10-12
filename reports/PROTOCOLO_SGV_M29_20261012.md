# SGV-M29 — O relógio do volume (pré-registro)

**Data:** 12/10/2026. **Ramo:** `research/m29-relogio-volume` (a partir de `research/m28-dependencia-nao-linear`). **`main` intocada. Só dados exploratórios** (1m mai–jul/2026).
**Ritmo:** 1º experimento do dia 12/10, a pedido da Ana ("Continue, vamos conseguir").
**Antes deste documento:** só o diagnóstico abaixo, sem modelo. Nenhum código do HXCLK escrito ou ajustado em dado real.

## De onde vem a hipótese
O pós-hoc do M28 mostrou que, tirando o volume, a dependência não linear entre instantes já está reproduzida; o excesso de HSIC mora na dinâmica própria do volume (~30 min).
**Diagnóstico exploratório sem modelo** (`scripts/m29_diag_relogio_volume.py`, saída em `reports/m29diag/`), só nas **janelas observadas das 42 origens pares**:
- **Relógio do minuto da hora:** o volume sobe no minuto **:00** (+0,39 em escore normal, ~12 erros-padrão), no **:30** (+0,22), e cai em **:57–:58** (−0,26), logo antes da virada da hora.
- **Picos de dependência nas defasagens do relógio:** a autocorrelação do volume em 5, 15, 20, 30, 45 e 60 min fica acima da média das vizinhas em 64–74% das janelas (contra 29–52% em 14, 16, 29, 31, 61); o HSIC volume→volume tem pico em 30 min (0,00317 contra 0,00286 em 29 e 0,00245 em 31).
Leitura: parte do volume do BTC segue o **relógio** (fechamento de candles, execuções programadas em minutos redondos, notícias em :00/:30). Os blocos reais (BL) carregam esse relógio sem saber (500 minutos consecutivos preservam a fase); o modelo explícito não tem relógio. O relógio do M17 era outro (hora do dia, 24 posições), não o minuto da hora.

## Modelo
**`HXCLK`** = HXACT (M28) + um **perfil de minuto da hora** no volume:
- **Estimação (só no prefixo):** volume (coordenada gaussianizada, depois da camada lenta) menos sua média móvel centrada de 60 min; média por minuto da hora (60 posições); centrado em zero; **encolhimento de James–Stein (parte positiva)** com variância de ruído estimada pelos resíduos dentro de cada posição.
- O perfil é tirado do volume antes do ajuste local (HAR, variância cruzada, fator de atividade) e **somado de volta dentro da simulação**, junto com o bloco lento real, nas posições do relógio dos **minutos reais da janela futura** (o calendário é conhecido de antemão). Assim o fator de atividade do M28 também vê o relógio (volume alto no :00 → retorno mais volátil e agressão mais equilibrada no :01).
- Relógio só na média do volume — nada no retorno ou na agressão diretamente.

Referências pareadas: **`HXACT`** (M28) e **`BL`**. Mesmas 12 estatísticas, 39 referências, posto conservador, alarme p ≤ 0,05. Roda nas 84 origens.

## Critérios pré-registrados
Conjunto de teste: as **42 origens ímpares** (o diagnóstico só olhou janelas pares; as ímpares já foram usadas no teste do M28, mas sem olhar o relógio — registrado).
1. **Primário (ímpares):** HXCLK alarma menos que HXACT em `hsic_5` e `hsic_30` (McNemar exato pareado, unilateral, α = 0,05/2 cada).
2. **Veredito do HXCLK (84 origens):** "adequação plena" (nenhuma das 12 com Wilson inferior > 7%) / "equivalente ao BL" (nenhuma significativamente pior, α = 0,05/12) / "não fecha a lacuna". Também reportado só nas ímpares.
3. **Não piorar (descritivo):** nenhuma das 10 estatísticas restantes deve piorar contra o HXACT (McNemar bilateral, α = 0,05/12); alerta se ocorrer.
4. **Mecanismo (descritivo, ímpares):** fração de origens em que o perfil estimado no prefixo tem o **:00 como a posição mais alta**; fator de encolhimento mediano; correlação mediana entre o perfil do prefixo e o perfil do diagnóstico das pares.

## Ressalvas
- 42 origens: pouco poder; queda grande sem significância = "direção certa, sem poder".
- As origens pares e ímpares são vizinhas no tempo; a confirmação de verdade é em dado virgem.
- O perfil é estimado em ~3,5 dias (≈83 observações por minuto da hora): ruidoso, por isso o encolhimento.

## Apostas de Claude (antes de qualquer código)
| Item | Aposta |
|---|---|
| Primário significativo em `hsic_30` | ≈ 35% |
| Primário significativo em `hsic_5` | ≈ 20% |
| Primário significativo em ≥ 1 das 2 | ≈ 40% |
| Veredito "equivalente ao BL" nas 84 | ≈ 35% |
| Veredito "adequação plena" nas 84 | ≈ 10% |
| Alguma estatística piora significativamente | ≈ 10% |
| :00 é a posição mais alta do perfil em > 50% das ímpares | ≈ 75% |
