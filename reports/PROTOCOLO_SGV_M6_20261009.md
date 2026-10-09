# SGV-M6 — Acoplamento das inovações volume–fluxo e controle morfológico HDR

**Data:** 2026-10-09. **Registro antes da execução.** Ramo `research/m6-acoplamento-residual-hdr`, sem modificar `main` ou abrir períodos confirmatórios reservados.

## Hipótese instrumental

O M5 identificou que o SF1 estendido com memória de log-volume e primeiro harmônico diário reduziu a perda de adequação conjunta nas escalas 1m e 1h. Entretanto, reamostrava separadamente as inovações de volume e não preservava necessariamente as dependências entre os resíduos do fluxo agressor e do volume. O M6 verifica se condicionar inovações de volume às inovações de fluxo melhora essa dependência **sem destruir a melhoria temporal do M5**.

## Modelos comparados

1. **SF1 base**: simulador SF1 original sem extensão.
2. **M5 independentes**: modelo de volume com memória e sazonalidade, inovações de volume sorteadas independentemente da inovação do fluxo.
3. **M6 acoplado**: mesmas equações e coeficientes de volume do M5, mas sorteio da inovação de volume de **resíduos históricos emparelhados**: dada a inovação de fluxo `e1_t` gerada na trajetória SF1, escolher o estrato quantílico de `e1` estimado no prefixo e reamostrar o residual de volume emparelhado com esse estrato (16 estratos). O método preserva aproximadamente dependência condicional não linear, sem exigir que o efeito econômico seja causal.

Para manter comparabilidade, os três modelos têm **mesma trajetória de preço e desequilíbrio relativo de agressão `iota`**, por semente. A extensão altera volume e a quantidade absoluta `taker_buy`, preservando a razão `iota=2*taker_buy/volume-1`. A recuperação de `e1_t` sintético usa a recursão GARCH e a equação do `iota*` do SF1. Os pares de resíduos do treino são alinhados por índice temporal antes da estimação.

## Medição

- Ajuste a prefixo estritamente passado: **1m 5000 candles**, **1h 2000 candles**; avaliação com 1500 (1m) e 1008 (1h) candles posteriores, mais 1700 candles sintéticos de aquecimento.
- Somente BTCUSDT spot, meses de **exploração** (1m maio–julho/2026; 1h 2020–2024), allowlist de arquivos e downloader com SHA-256. Quatro origens equiespaçadas entre prefixos/janelas completos e contínuos, sem acesso aos períodos reservados.
- **Seis réplicas** sintéticas por origem/modelo, pareadas pela mesma semente de fluxo. Não gerar inferência confirmatória com tão poucas réplicas.
- Diagnósticos principais: `rho(iota,nu)`, `rho(|z|,nu)`, `acf(nu,1)`, `acf(nu,10)`, `std(nu)`, e perda conjunta normalizada com pesos previamente estabelecidos no M5 para memória/dispersão/retorno–atividade; perda de dependência fluxo–atividade (|diferença de rho(iota,nu)|) reportada separadamente.
- A melhoria do acoplamento deve ser testada por comparação pareada **M6 versus M5 independente**, não inferida apenas porque e1/e2 exibem correlação no treino.
- **Teste geométrico exploratório** em duas origens por escala, com até três réplicas por variante, exclusivamente HDR50 da GMM2: intensidade de `K<0` e déficit convexo, além da diferença `D(B)-D(A)` entre as duas metades. Mesmos limiares/grade/gates de M1–M3. Reportar quantos objetos foram invalidados por truncamento/gates. Esse piloto de formas não estabelece topologia intrínseca Fisher–Rao, causalidade ou tensão do BTC.

## Controles de integridade obrigatórios

- Séries simuladas têm o mesmo preço, `z` e desequilíbrio `iota` em M5 e M6.
- Calibração e pares de resíduos são extraídos **somente do prefixo**, e alteração posterior não muda os coeficientes.
- Verificação em dados sintéticos com residual de fluxo/volume fortemente acoplado: M6 deve recuperar melhor a covariância do que reamostragem independente.
- Se o sinal for fraco, a distribuição empírica insuficiente, houver lacunas ou simulação explosiva, registrar indisponibilidade; não preencher com valores fictícios.
- Teste de área HDR e volumes só com malhas fechadas sem truncamento.

## Limites e decisão

As inovações podem ser contemporaneamente correlacionadas sem que uma cause a outra. Esse acoplamento não incorpora livro de ofertas, liquidez oculta, cancelamentos, outros ativos ou regime exógeno. Mesmo melhorar correlações médias não garante reproduzir caudas conjuntas, trajetórias geométricas ou eventos extremos.

Se M6 não superar M5 independentemente em várias origens e métricas, preservar M5 como referência; se superar, promover apenas a **candidato a nulo estatístico**, não a modelo comprovado do mercado. `D` permanece descritor de não convexidade e **não** oscilador validado de estresse financeiro.

## Reproduzir
- `experiments/m6_acoplamento_residual_hdr.py`
- `tests/test_m6_acoplamento_residual_hdr.py`
- `.github/workflows/m6-acoplamento-residual-hdr.yml`
