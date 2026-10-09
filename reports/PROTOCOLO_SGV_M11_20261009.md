# SGV-M11 — Distância à superfície e controle temporal do erro do estimador

**Pré-registro de engenharia, 09/10/2026.** `research/m11-distancia-superficie-nulos-temporais`. A `main` e os períodos confirmatórios reservados permanecem intocados.

## Problema
O M10 demonstrou que a Chamfer de pontos amostrados sofre piso >0 mesmo quando a malha é exatamente a mesma. Precisamos de uma medida de distância mais próxima da superfície contínua, separando três erros: (a) amostragem de pontos, (b) aproximação numérica/grade, (c) ajuste de densidade com candles finitos e temporalmente dependentes.

## Desenho do novo instrumento

1. Construir duas malhas HDR50 GMM2 em grades 35³, usando a mesma transformação marginal ancorada nos primeiros 30% da janela; duas fotografias nos 35% e 35% restantes. Somente malhas fechadas, sem truncamento, massa de domínio adequada.
2. Retirar translação e escala de volume das malhas. Estimar uma rotação **de registro geométrico** por ICP multistart com 360 amostras de treino. Nunca interpretar a rotação de registro como giro físico.
3. Medir **distância de pontos determinísticos de quadratura da malha A à superfície triangular da malha B**, mais a direção inversa. Para cada amostra, calcular a distância euclidiana ao triângulo mais próximo, usando busca de candidatos com **limite geométrico conservador** para não omitir triângulos distantes do centro mas próximos do ponto. A seleção de pontos é sistemática por área de triângulo, sem sorteio. Média simétrica das duas distâncias (não é distância de transporte; quadratura finita pode ter erro).
4. Comparar 256 e 512 pontos de quadratura. A diferença entre os dois é um diagnóstico de convergência da integração. Comparar também 35³ versus 49³ em duas janelas por escala; o alinhamento pode mudar de ótimo local, razão para testes sintéticos.
5. **Controles geométricos sintéticos:** mesma malha contra si mesma → distância praticamente zero em alinhamento identidade; malha rigidamente girada → distância pós-registro pequena; esfera/elipsoide deformado deve conservar distância positiva. Esses controles são necessários, mas não bastam para provar convergência em toda superfície.
6. **Nulo temporal exploratório:** em duas janelas por escala, juntar as metades A+B após fixar o mapa de coordenadas e gerar dois grupos por bootstrap circular em blocos a partir da mistura. O nulo representa a hipótese simplificada de duas metades amostradas de uma **mesma distribuição temporalmente estacionária**, preservando dependência apenas dentro do bloco. Não preserva regimes lentos, agrupamentos >L nem sazonalidade: não é nulo de mercado calibrado.
7. Fazer 12 replicações do nulo pooled, mais 12 reamostragens separadas A/B para sensibilidade da observação. Nulo e bootstrap serão relatados com quantis 10/50/90, taxas de malhas válidas e zero significância inferencial. Usar L=15 (1m) e L=12 (1h). **Não escolher p-value**, com tão poucas replicações.
8. Medir seis janelas exploratórias não sobrepostas por escala; comparar superfície-direta (n=256/512) com Chamfer amostrada antiga (M9) em duas janelas para aferir o efeito da amostragem de pontos, sem declarar que todo resíduo adicional é sinal real.

## Dados e integridade
BTCUSDT spot: 1m maio–julho de 2026 e 1h 2020–2024. Arquivos de período exploratório exclusivamente via downloader SHA256 e allowlist; sem abrir confirmação. Cada fotografia processa apenas candles disponíveis até seu próprio fechamento. Uma comparação de metades pode ser reportada ao fim da segunda metade; não usá-la para atribuir informação ao começo da primeira.

## Decisões prévias
- Se qualquer malha não passar gates, não substituí-la; reportar exclusão.
- Se a distância A→B e B→A divergir muito ou a integração 256→512 for instável, a medida fica **não convergida** para tal caso.
- Se o nulo temporal pooled reproduzir distâncias similares às observadas, não alegar evolução extraordinária.
- Exceder o q90 do nulo *simplificado* será descrito como resultado exploratório, **não rejeição estatística da estabilidade do mercado**.
- Uma medida geométrica estável é útil como ferramenta de observação independentemente de sinais de trading, tensão econômica, novidade física ou causalidade.

## Artefatos
`experiments/m11_distancia_superficie_nulos.py`; `tests/test_m11_distancia_superficie_nulos.py`; `.github/workflows/m11-distancia-superficie-nulos.yml`; JSON e CSV por escala e relatório científico.
