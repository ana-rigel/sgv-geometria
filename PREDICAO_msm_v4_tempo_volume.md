# Previsão registrada antes de calcular (MSM v4): o relógio de volume desmonta a escada?

**Registrada em:** 17/10/2026 (UTC), antes de escrever o código e de rodar qualquer período; em paralelo com a v3 (ciclo diário), que ainda roda.

**Pedido da Ana:** "o teste de mudar o relógio do modelo para o Tempo de Volume".

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já abertos. Nada de outubro. Um julgamento por período.

**Ramo:** `exploracao/msm` (continuação).

## A ideia

Clark (1973) e Ané–Geman (2000): se o "tempo de negociação" θ(t) do MMAR for aproximado pelo volume acumulado, os retornos medidos em barras de volume igual devem ser mais gaussianos e menos agrupados que em barras de tempo igual. Se a escada do MSM v2 é, no fundo, o ritmo do volume, **no relógio de volume ela deve encolher**: menos componentes, inovações menos gordas.

## Instrumento

- **Barras de volume:** acumula minutos consecutivos até que a soma do volume atinja V\*; a barra fecha no minuto em que isso ocorre (volume da barra ≥ V\*). V\* = 2 × volume médio por minuto no período (alvo de ~2 min em média; barras de 1 min nos minutos cheios, de muitos minutos nos vazios).
- Retorno por barra = log(close da última barra-minuto) − log(close da anterior). Série de ~30–45 mil barras por período (declarado: amostra menor que os 87 mil minutos; o BIC é comparável só dentro da v4).
- **Limitação declarada:** o piso de 1 minuto. Um minuto com volume ≫ V\* vira uma só barra; o relógio de volume fica truncado nas horas cheias. Isso enfraquece o efeito esperado (o relógio não corre tão rápido quanto deveria nos surtos); se o resultado for "escada intacta", parte da culpa pode ser do piso, e a leitura dirá.
- Sem dessazonalização (o relógio de volume absorve o ciclo diário por construção).
- MSM Student-t padronizada, k = 1…5, BIC, validação com sintéticos k = 2 e 3 (mesmos parâmetros e sementes das v2/v3, comprimento igual ao da série de barras).

## Classificação (por período; só vale se repetir)

Comparação com o k\* e o ν da **v2** (relógio de tempo, mesmos períodos):

- **"Relógio de volume encolhe a escada":** validação passa, k\*_vol ≤ k\*_tempo − 1 (isto é, ≤ 3).
- **"Escada intacta":** validação passa, k\*_vol ≥ 4.
- **"Relógio de volume alonga a escada":** k\*_vol = 5 com ganho do 5º degrau maior que o do 4º na v2 (descritivo; não esperado).
- Descritivos: ν_vol vs ν_tempo; escalas 1/γ_i em barras e seu equivalente médio em minutos; fração de barras de 1 minuto (medida do truncamento).

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| "Encolhe a escada" (k\* ≤ 3) nos dois períodos | ~40 % |
| "Escada intacta" (k\* ≥ 4) nos dois períodos | ~50 % |
| ν_vol > ν_tempo nos dois períodos (cauda mais fina no relógio de volume) | ~70 % |
| Fração de barras de 1 minuto > 40 % (truncamento forte) | ~60 % |
| Ganho de BIC do último degrau menor que na v2, em barras por observação | ~65 % |

Os 50 % em "intacta" vêm do piso de 1 minuto e de que a escada lenta (meio dia, dias) não é ritmo de volume intradiário, é regime; o volume acumulado não corre mais rápido numa semana quente inteira do que numa calma na proporção certa.

## O que confirma e o que não

- **Encolhe:** o tempo de negociação do BTC é, em boa parte, tempo de volume; a escada rápida é ritmo de negociação, não dinâmica própria. Leitura à la Clark.
- **Intacta:** o volume de 1 min não é o relógio certo (ou o piso o estraga); a hierarquia lenta sobrevive a qualquer relógio intradiário.
- Em nenhum caso há direção, previsão ou lucro.

## Emenda 1 (registrada depois da primeira rodada reprovar na validação, antes de rodar de novo)

Primeira rodada (Actions run 38997729029; logs em resultados/msm_v4_{junjul,agoset}_INCONCLUSIVO_emenda1.log): validação reprovou nos dois períodos (sintético k = 3 → k\* = 2). Causa: as escalas do sintético de validação ficaram as da v2/v3 (2, 50 e 1250 **barras**), e com ~26 mil barras a escala de 1250 troca de estado ~20 vezes, insuficiente para o BIC a distinguir. Erro de desenho (escalas pensadas em minutos num relógio de barras), não de hipótese.

**Mudança (única):** parâmetros do sintético de validação passam a **b = 8,5, γ_k = 0,5** → escalas de ~2, ~17 e ~145 barras (≈ 7 min, 1 h e 8 h ao ritmo médio de 3,4 min por barra), separadas por ~8,5× e todas com dezenas a milhares de trocas na amostra. Nada mais muda. Os descritivos da rodada reprovada (ν 10,9 e 12,9; k\* = 5 com ganhos finais de 27–117 de BIC) ficam registrados como observação, não como veredito. Última emenda: se reprovar de novo, a v4 encerra INCONCLUSIVA.
