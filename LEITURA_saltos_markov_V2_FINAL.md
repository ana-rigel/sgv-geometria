# SGV — Reteste saltos × memória V2: leitura final após ambos os períodos

Data: 15/10/2026. **Estado: novo controle sintético validado; reanálise financeira exclusivamente exploratória.** Ramo isolado `research/saltos-markov-v2-controles-20261015`. Nenhuma alteração na V1 ou na `main`. Nenhuma leitura de outubro ou holdouts reservados.

## Cronologia e proveniência

1. Registrado `PREDICAO_saltos_markov_V2.md` antes do código/execução V2. Oito gates de controle sintético pré-definidos.
2. Commitado o código e testes sintéticos antes da execução, GitHub Actions `38818887579` **success**, nove testes de sanidade e oito gates passaram. Dados numéricos em `resultados/saltos_markov_v2_controles_20261015.json`; relato `LEITURA_saltos_markov_V2_controles.md`.
3. **Depois**, registrado `PROTOCOLO_saltos_markov_V2b_mercado.md` antes da reanálise V2b, declarando *a priori* que junho–setembro já foram examinados e são apenas exploratórios.
4. Executado código V2b e seis testes de sanidade, GitHub Actions `38819410611`: **success**, download de agosto/setembro e SHA-256, junho–julho e agosto–setembro concluídos, JSONs e logs commitados.
5. V2b mantém as coordenadas originais `(E_norm,jerk,memory_flux)` na memória (teste B), mas usa **log-retornos brutos** na análise multiescala de caudas (teste A) para evitar que as transformações diferenciais da coordenada SGV confundam a interpretação. Consequentemente, valores do teste A V1 e V2b NÃO são diretamente comparáveis.

## Controles sintéticos que passaram

- Trajetórias com deriva zero: difusão contínua (dX=\sigma(t)dW) apresentou intercepto multiescala `M4(dt)/dt` **−0,000999** (IC95 [−0,002671;0,000611]); processo com saltos genuínos Poisson composto apresentou **+0,361556** ([0,335424;0,389182]), contra valor analítico `lambda E[J⁴]=0,36864`.
- AR(1) com volatilidade latente conhecida: Spearman da memória quadrática normalizada **0,389738** sem controle, **0,127676** com proxy causal de 60 passos, **0,000961** com volatilidade verdadeira; controle homocedástico ≈0. Não é prova geral de Markov, só validação deste observador em processos simulados.

## V2b, teste A: caudas em escalas finitas, retornos brutos

Nove semanas em cada período. Métrica = **mediana semanal de M4(h)/h**, em unidades de `10^-12`, para h=1,2,4,8 minutos. Sintéticos são ajustados somente à semana **anterior**: AR1 de retornos e AR1 de logvol causal; para a semana de avaliação, G usa choques gaussianos e S amostra choques padronizados empíricos da semana anterior, três sementes. Nenhum `rolling(center=True)`.

| Período | h min | Real (×10⁻¹²) | G mínimo–máximo (×10⁻¹²) | S mínimo–máximo (×10⁻¹²) |
|---|---:|---:|---:|---:|
| Jun–jul | 1 | 1,743 | 0,171–0,247 | 0,825–1,272 |
| Jun–jul | 2 | 2,406 | 0,338–0,529 | 1,046–1,594 |
| Jun–jul | 4 | 4,265 | 0,758–1,091 | 1,581–2,101 |
| Jun–jul | 8 | 6,396 | 1,533–2,466 | 2,401–3,296 |
| Ago–set | 1 | 1,223 | 0,084–0,089 | 0,207–0,356 |
| Ago–set | 2 | 1,955 | 0,161–0,181 | 0,315–0,445 |
| Ago–set | 4 | 3,893 | 0,317–0,364 | 0,433–0,755 |
| Ago–set | 8 | 9,088 | 0,677–0,765 | 0,632–1,551 |

Em ambas as datas, o real está acima dos três G e três S nesse resumo multiescala. **A diferença do resultado V1 é explicável em parte pela mudança de controle e de variável observada**: V1 comparava curtose local de incrementos de `E_norm` a controles com o próprio caminho de volatilidade contemporâneo/reconstruído por janela centrada; V2b compara o quarto momento dos retornos logarítmicos crus a sintéticos gerados causalmente da semana anterior. Não interpretar a ordenação V2b como `saltos além das caudas` ou como refutação das caudas conhecidas: a distribuição de choques, a volatilidade e os movimentos entre semanas são diferentes sob os dois nulls. Três sementes não constituem teste estatístico do desvio.

As distribuições de retornos de 1 min não contêm observações subminuto, portanto **não identificam o coeficiente infinitesimal de Kramers–Moyal**; valores positivos de curtose e `M4(h)/h` para h≥1 não demonstram descontinuidade das trajetórias.

## V2b, teste B: proxy causal no mesmo SGV 3D da V1

Usa exatamente o campo de energia normalizada da V1 e os mesmos estados de avaliação, agora três proxies de volatilidade `rolling(n).std().shift(1)`, n=30,60,120, com âncora de maio.

| Período | M3D | M4D(30) / redução | M4D(60) / redução | M4D(120) / redução |
|---|---:|---:|---:|---:|
| Jun–jul | 0,220881 | 0,132154 / **40,17%** | 0,138224 / **37,42%** | 0,151173 / **31,56%** |
| Ago–set | 0,333837 | 0,226675 / **32,10%** | 0,238651 / **28,51%** | 0,255427 / **23,49%** |

Os valores do proxy de 60 min **reproduzem a V1**, como verificação de paridade: jun–jul `M4D≈0.1382236`, ago–set `≈0.2386509`. As reduções são estáveis em sinal, mas nenhum proxy elimina a estatística M. O 30 min apresentou maior redução nos dois períodos estudados; **não escolher 30 min como vencedor confirmado**, pois os meses já foram explorados e a estatística pode ser sensível à janela por razões mecânicas.

O contraste com o controle sintético conhecido mostra que uma proxy imperfeita pode deixar grande parte da memória aparente mesmo quando a **única variável latente do gerador é a volatilidade**. Assim a V1 não tinha poder de descartá-la. Mas **não demonstramos que seja a única dimensão omitida do mercado** e tampouco que 3D ou 4D sejam processos Markov verdadeiros.

## Decisão

- **V2 sintética:** instrumentos passam nos mecanismos conhecidos sob os critérios registrados. Isso corrige uma limitação da V1, não comprova teoria geral.
- **V2b histórica:** evidência descritiva de caudas mais fortes que dois modelos causais específicos e de redução parcial de dependência ao acrescentar proxies de volatilidade.
- **Nenhum resultado confirmatório financeiro, causal ou de presença física de saltos.** Não reclassificar V1 com força indevida; deixar ambos os conjuntos no repositório, com as fórmulas e diferenças explícitas.
- Um teste de saltos no sentido infinitesimal exigiria dados de resolução maior e desenho de microestrutura/ruído; um estudo da dimensão escondida exigiria testes condicionais próprios e controles latentes endógenos mais diversos, em **dados novos**, sob protocolo separado.

Links para reprodutibilidade: `pipeline/reteste_saltos_markov_v2.py`, `pipeline/reteste_saltos_markov_v2_mercado.py`, `resultados/saltos_markov_v2_controles_20261015.json`, `resultados/saltos_markov_v2b_junjul.json`, `resultados/saltos_markov_v2b_agoset.json`, workflows GitHub Actions `38818887579` e `38819410611`.
