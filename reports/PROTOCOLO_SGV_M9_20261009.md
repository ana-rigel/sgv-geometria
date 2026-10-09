# SGV-M9 — Simetrias, orientação identificável e deformação 3D sem eixos

**Data do registro pré-execução:** 09/10/2026. **Ramo exclusivo:** `research/m9-simetrias-registro-3d`. A `main` e os períodos confirmatórios reservados permanecem intactos.

## Hipótese instrumental

No SGV-M8 a rotação obtida pela mudança dos eixos principais do sólido HDR50 apresentou grandes variações sob reamostragem, inclusive ângulos próximos de 172°. A distância de deformação dependia da identificação desses eixos. O M9 separa:

(A) **Mudança da orientação dos eixos principais**, sobre o espaço quociente de simetrias de um triedro ortonormal de eixos sem direção. A orientação relativa entre sólidos com três autovalores de inércia bem separados é determinada até inversão de dois sinais, representada pelo grupo de quatro matrizes diagonais `D2`. O ângulo reportado é a **menor distância geodésica** entre os quatro alinhamentos equivalentes, e somente quando os dois espectros satisfazem gap relativo mínimo 0,07.

(B) **Deformação residual independente da escolha dos eixos principais**, definida por registro rígido de superfícies centradas e normalizadas pelo raio da esfera de volume equivalente. A rotação de alinhamento é obtida por *ICP* simétrico com multistart e **pontos de treino independentes dos pontos de avaliação** (holdout). Relatar distância Chamfer simétrica no conjunto não usado para otimizar. O registro pode produzir distância residual mesmo quando os eixos de inércia são degenerados; nesse caso **não** há ângulo de rotação interpretável.

(C) **Estabilidade da orientação:** fracionar as reamostragens em eixos distinguíveis e não distinguíveis; comparar a distribuição do ângulo no quociente, fração de ângulos acima de 90° e amplitude q90-q10. Este piloto não assegura intervalos calibrados; um critério conservador impede declarações de rotação precisa se menos de 75% das reamostragens tiverem eixos identificáveis ou se `q90-q10 > 45°`. Um valor angular elevado em dados reamostrados não é interpretado automaticamente como giro material.

## Registro rígido independente dos eixos

1. Extrair malhas GMM2 HDR50 fechadas pelo método M1, com massa de grade >=95%, sem truncamento e volume positivo; preservar transformação marginal congelada a partir dos primeiros 30% da janela.
2. Centrar pelo centro de massa do **volume sólido**, dividir pela escala `r=(3V/(4π))^(1/3)`.
3. Amostrar por área dois conjuntos independentes em cada casca: treino (360 pontos) e holdout (360 pontos), sementes fixadas antes da comparação; não calcular erro final nos pontos usados para escolher a rotação.
4. Gerar inícios de registro pelo triedro dos eixos (se disponível) e por rotações fixas (identidade, 90° nos eixos, 180° nos eixos) para evitar que a métrica fique indisponível em cascas quase esféricas. Ajustar pelo algoritmo ICP simétrico via correspondência de vizinho mais próximo e Kabsch, máximo 14 iterações por início. Escolher pelo erro **de treino** e medir Chamfer simétrico **no holdout**; documentar mínimos locais e possível sobreajuste residual.
5. A distância residual minimizada não é material, não é distância de transporte ótimo e não identifica por si só direção causal. Não identificar rotação pelo registro livre no caso de simetrias.

## Calibração pré-BTC
- Esfera rotacionada e transladada: eixos não identificáveis, mas **deformação rigidamente alinhada pequena**, sem valor angular físico.
- Elipsoide de três eixos distintos rigidamente rotacionado e escalado: ângulo-quociente compatível com rotação conhecida e deformação pequena.
- Um elipsoide realmente deformado, com razões de semieixos alteradas: residual maior que no caso rigidamente equivalente.
- Toro/forma quase simétrica: o alinhamento deve continuar definido sem forçar uma rotação de eixos.
- Controle de erro com a mesma malha e holdout não utilizado no treino; versão antiga M8 conservada para comparações descritivas.

## Replay BTC exploratório

BTCUSDT spot 1m (maio a julho/2026) e 1h (2020 a 2024); 6 origens por escala, escolhidas deterministicamente entre segmentos contínuos, sem sobreposição dos períodos avaliados. Prefixos 5000/2000 candles; fotografias 1500/1008; três simulações pareadas por origem/modelo (SF1 original, M5 independente, M6 acoplado), com 1700 barras de aquecimento. Mesmos caminhos sintéticos de preço e `iota` e ajuste de parâmetros **somente no prefixo anterior**. Comparar erros da mediana sintética versus observação real para deslocamento, `log(Vb/Va)`, ângulo-quociente **quando identificável** e residual Chamfer holdout. No mínimo 2 de 3 realizações válidas para calcular erro; se menos de 4 origens pareadas válidas, declarar comparação indisponível. Não selecionar vencedor global a partir de uma única métrica.

Duas origens por escala (primeira e última) recebem: bootstrap circular de **8 reamostragens por blocos** (1m L=15, 1h L=12), com a âncora marginal congelada, e comparação de grades 35³ versus 49³. Quantis bootstrap são **diagnósticos**, não intervalos de confiança calibrados.

## Limitações
A geometria é a casca extrínseca das estimativas de densidade no espaço observacional gaussianizado, **não** curvatura Fisher–Rao intrínseca. A remoção de translação e escala destrói informação sobre direção de preço e amplitude de negociação e serve exclusivamente à medida de mudança de forma. A rotação otimizada do registro não é uma medida física de giro; os modelos nulos ainda não reproduzem necessariamente os regimes e caudas. Não há inferência confirmatória, lei do mercado, tensão financeira nem alpha.

**Artefatos previstos:** `experiments/m9_registro_simetrico_3d.py`, `tests/test_m9_registro_simetrico_3d.py`, `.github/workflows/m9-registro-simetrico-3d.yml`, arquivos `reports/SGV_M9_*.json`/CSV e relatório interpretativo.
