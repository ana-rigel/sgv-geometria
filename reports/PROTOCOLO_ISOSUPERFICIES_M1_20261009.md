# SGV — Protocolo M1: isosuperfícies HDR e morfometria tridimensional

**Data:** 2026-10-09  
**Ramo:** `research/isosuperficies-morfometria`  
**Natureza:** pesquisa observacional de distribuições dos dados públicos, não preditiva. A `main` não será alterada.

## Objetivo

Reconstruir as superfícies trianguladas correspondentes às fronteiras de regiões de maior densidade (`HDR25/50/75`) de `X=(z, iota, nu)`, medir características da forma e decompor mudanças entre duas fotografias. A superfície `p(x)=tau` é uma **superfície extrínseca de nível de densidade no espaço de observações**, não a variedade estatística de Fisher–Rao ou seu tensor de curvatura intrínseca.

## Definição causal

Dentro da janela fechada de W=1500 candles 1m ou W=1008 candles 1h:
- Primeiros 30%: calibrar, no passado relativo às metades seguintes, mapas marginais de postos que convertem as três coordenadas em scores gaussianizados.
- Duas metades restantes, separadas cronologicamente (aproximadamente 35%+35%): ajustar independentemente normal 3D e mistura de duas normais 3D; **usar a mesma transformação de marginais**, congelada no primeiro segmento.
- Modelos não acessam os períodos confirmatórios.
- Reconstruir densidades em grade 35³, com checagem de resolução 49³ em subconjunto predefinido. Domínio `[-3.5,3.5]^3` na escala de scores.

## Marching Cubes, corretamente

Defina `tau_alpha` pela ordenação de valores `p_i` da grade até que a massa discreta da região acima do limiar some alpha vezes a **massa total dentro do domínio discretizado**. Então:
`HDR_alpha = {x : p(x) >= tau_alpha}`.
Extraia `p(x)=tau_alpha` pelo Marching Cubes; grave vértices e faces triangulares. Registrar a massa de grade `sum p_i * delta^3`: se inferior a 95%, **rejeitar** qualquer interpretação definitiva de volume e gênero, porque a HDR está condicionada a um domínio truncado. Massa maior que 1.05 também rejeitada como problema numérico.
O valor de tau corresponde à HDR discretizada, não à probabilidade alpha como valor da função p.

## Controles de qualidade geométrica

- Diagnosticar se a superfície encosta na borda `p>=tau` ou vértices coincidem com borda do domínio.
- Para cada aresta não orientada exigir exatamente duas faces incidentes; classificar malha fechada (*watertight*).
- Definir componentes conexas na estrutura vértice-aresta, testar orientação e área/volume válidos; fechar normais antes de calcular volume.
- Calcular Euler por componente `chi=V-E+F` e gênero `g=(2-chi)/2`, **somente** para superfície fechada, orientável e sem truncamento.
- Curvatura gaussiana local discreta `K_i=(2pi-soma_angulos_i)/A_i`; curvatura média em módulo via Laplaciano cotangente, com áreas baricêntricas. A média e o sinal podem ser sensíveis à triangulação: testar resolução.
- Verificação Gauss–Bonnet `sum K_i A_i≈2pi chi` e dados de curvatura negativa. **K negativo não prova lobulação**: um toro possui K negativo e não é dois lóbulos conectados.

## Quatro movimentos entre formas

1. **Translação:** deslocamento entre centros de massa volumétricos de cada HDR, em unidades das três coordenadas transformadas. Não equivale a mudança direcional pura do preço.
2. **Expansão:** `V_b/V_a` e `log(V_b/V_a)`, medidos em unidades cúbicas de scores. Mudança volumétrica não implica exclusivamente volatilidade.
3. **Rotação:** autovetores do tensor de segundo momento do **sólido**, calculado a partir do momento de inércia volumétrico. Eixos são indefinidos quando dois autovalores são muito próximos: não relatar ângulo nesse caso; lidar com troca de sinais dos autovetores.
4. **Deformação residual:** comparar amostras de superfície após remover translação, escala isotrópica e rotação rigidamente alinhadas. Relatar distância Chamfer simétrica normalizada pelo raio volumétrico. É um resíduo de forma **não material**, não correspondência de partículas e nem deformação causal. 

## Calibração analítica antes do mercado

- Esfera unitária: 1 componente, gênero 0, volume 4pi/3, área 4pi, K≈1, Gauss–Bonnet, orientação não identificável.
- Toro: 1 componente, gênero 1 e áreas com K negativo, refutando inferência automática de lóbulos a partir de K negativo.
- Duas esferas separadas: 2 componentes, gênero 0 cada, sem confundir GMM2 com dois modos necessariamente.
- Esfera cortada pela fronteira: desabilitar gênero, volume e movimentos que exigem casca válida.
- Elipsoide transladado/expandido: checar movimento conhecido e recuperação dos eixos.

## Execução com BTC real

Amostras **exclusivamente exploratórias**, BTCUSDT spot 1m maio–julho/2026 e 1h janeiro/2020–dezembro/2024, arquivo aprovado por allowlist e downloader com checksum. Selecionar 6 janelas distribuídas por índices entre janelas completas e contínuas; duas delas para checagem multi-resolução. Gerar JSON de agregados, CSV de medidas por superfície e movimentos, e GLB para visualização das HDRs 25/50/75 de duas fotografias representativas. Se uma malha falhar qualquer porta geométrica, conservar motivo e não preencher métricas com estimativa inventada.

## Escopo das conclusões

Neste protocolo será demonstrada a implementação geométrica, mas **não** automaticamente a confiabilidade ao longo de sessões de streaming reais, existência de dois núcleos, curvatura intrínseca especial, número universal de modos, causalidade informacional ou geração de retorno. A estabilidade de descritores sob reamostragem em blocos e controles SF1 temporalmente adequados permanece tarefa posterior.

## Reprodutibilidade

- `experiments/isosuperficies_morfometria.py`
- `tests/test_isosuperficies_morfometria.py`
- `.github/workflows/isosuperficies-morfometria.yml`
- GitHub Actions na ramificação `research/isosuperficies-morfometria`.
