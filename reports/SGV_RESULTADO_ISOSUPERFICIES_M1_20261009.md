# SGV — Resultado M1: extração de isosuperfícies e morfometria 3D

**Data:** 09/10/2026. **Ramificação:** `research/isosuperficies-morfometria`. **Execução definitiva:** https://github.com/ana-rigel/sgv-geometria/actions/runs/37945591837 — três jobs concluídos com sucesso. **13 testes matemáticos aprovados**. Nenhuma alteração na `main`.

## 1. Questão e objeto matemático

Reconstruir geometricamente a fronteira das regiões de densidade mais alta da distribuição observável tridimensional `X=(z,iota,nu)`: retorno de preço normalizado por histórico anterior, fluxo agressor contemporâneo e atividade relativa contemporânea.

**O objeto extraído é a superfície extrínseca de nível da densidade estimada `p(x)=tau_alpha`, NÃO a curvatura intrínseca da variedade estatística de Fisher–Rao**. HDRs de 25%, 50% e 75% usam limiares derivados de massa de densidade, nunca `p(x)=0.25` por definição.

## 2. Método

- Cada janela histórica fechada contém W=1500 candles (1m) ou W=1008 candles (1h).
- Os primeiros 30% fixam a transformação marginal de postos para scores gaussianizados, que é compartilhada por duas metades posteriores (aproximadamente 35% + 35%). Ajustes em uma metade não leem a outra.
- Modelo normal 3D e modelo de mistura GMM2: estimar `p(x)` em grade cúbica de **35³** pontos no domínio `[-3.5,3.5]^3`, com validação de resolução **49³** em subconjunto predefinido.
- Definir limiar `tau_alpha` via massa discreta dentro da grade; Marching Cubes gera vértices, faces triangulares, malha fechada e objeto GLB.
- Verificar incidência de duas faces por aresta, ausência de truncamento, massa de densidade coberta >=95%, volume positivo, centroide e Euler/gênero por componente. Uma superfície inválida **não** gera volume/gênero inventados.
- Curvaturas: (a) curvatura discreta por ângulos dos triângulos, registrada para auditoria; (b) curvatura calculada analiticamente a partir do gradiente e da Hessiana da **densidade ajustada** nos vértices, que corrige falsos negativos de curvatura no elipsoide gaussiano.
- Decomposição entre fotografias: translação do centro volumétrico, mudança de volume, rotação dos eixos principais quando identificáveis e resíduo Chamfer após normalizar centro/escala/orientação. Os eixos principais não têm sinal definido; rotação é comparada entre orientações equivalentes, não contabilizando inversão artificial de 180°.
- Seleção *ex ante*: seis janelas equiespaçadas entre janelas completas e sem gaps por escala; duas verificações por escala em 49³.
- Apenas BTCUSDT spot exploratório: **1m maio–julho 2026; 1h 2020–2024**, downloader com checksum e allowlist; períodos confirmatórios não acessados.

## 3. Calibração analítica

Os controles aprovados compreendem:
- Esfera: uma componente, gênero 0, área≈4π e volume≈4π/3, curvatura gaussiana positiva no campo analítico;
- Toro: uma componente, gênero 1 e curvatura negativa em regiões interiores; **K negativo não implica dois lóbulos**;
- Duas esferas: duas componentes, gênero 0 em cada;
- Superfície truncada: qualidade insuficiente, gênero e volume omitidos;
- Elipsoide transladado/expandido: recuperação de deslocamento e escala, rotação alinhada sem falso 180°;
- Gaussiana 3D: curvatura analítica não negativa mesmo quando triangulação discreta produz falsos sinais negativos;
- Movimento não identificável: medidas derivadas anuladas, sem valores fabricados.

**13 testes unitários aprovados.** A revisão do instrumento foi necessária porque a estimativa direta de curvatura pelos ângulos dos triângulos produzia falsa curvatura negativa em superfícies gaussianas convexas. A correção usa o campo diferencial de densidade e passou pelo controle gaussiano. A falha anterior do replay 1h quando a orientação não era identificável também foi corrigida, com emissão de `None` quando inexequível.

## 4. Resultados de BTCUSDT real

| Medida | 1 minuto | 1 hora |
|---|---:|---:|
| Janelas contínuas disponíveis (candidatas) | 87 | 31 |
| Janelas efetivamente amostradas | 6 | 6 |
| Superfícies extraídas (Gauss/GMM, HDR25/50/75, duas metades) | 72 | 72 |
| Superfícies que passaram controle geométrico | **72** | **71** |
| HDR50 válidas, gaussiana | 12/12 | 12/12 |
| HDR50 válidas, mistura | 12/12 | 12/12 |
| Fração com componentes múltiplas nas superfícies válidas | 0% | 0% |
| Fração com gênero positivo nas superfícies válidas | 0% | 0% |

**Uma** isosuperfície GMM HDR75 no 1h não passou o gate de qualidade; não foi incluída em medidas que exigem volume e topologia válidos. O motivo individual está no CSV completo da execução.

### Morfometria HDR50 — medianas no subconjunto exploratório

| Medida | BTC 1m Gauss | BTC 1m GMM2 | BTC 1h Gauss | BTC 1h GMM2 |
|---|---:|---:|---:|---:|
| Volume em unidades³ de scores | 11.303 | 11.011 | 12.462 | 10.792 |
| Deslocamento do centro volumétrico | 0.583 | 0.619 | 0.492 | 0.593 |
| Fator isotrópico de escala B/A | 0.968 | 0.958 | 1.057 | 1.075 |
| Deformação residual (Chamfer normalizado) | 0.0800 | 0.0967 | 0.0839 | 0.1268 |
| Área relativa com K<0 **analítico** | **0.0%** | **16.7%** | **0.0%** | **21.4%** |

O campo gaussiano é elipsoidal e convexo: o controle analítico identificou corretamente **0% de área com K negativo**. A geometria da mistura estimada apresentou **16,7%** (1m) e **21,4%** (1h) da área com curvatura negativa, apontando trechos localmente de sela/não convexos que a gaussiana única não representa. Isto é **evidência descritiva de deformação do contorno de nível da densidade estimada**, sujeita à sensibilidade à amostra, ao modelo GMM e à resolução. **Não comprova dois lóbulos, singularidades, buracos, uma lei física ou um fluxo causal de informação.**

Para comparação, a curvatura derivada dos ângulos de triângulos da malha gaussiana na HDR50 foi falsamente negativa em 13,7% (1m) e 12,4% (1h) da área, evidenciando por que o estimador por triangulação **NÃO deve ser interpretado sem controle analítico**. Permanecem registradas as duas versões para auditoria.

### Outros níveis

No 1m a fração mediana K<0 analítico para GMM foi 16,2% (HDR25) e 15,6% (HDR75), ambas com gênero zero nas malhas válidas. No 1h, 23,1% (HDR25) e 20,8% (HDR75, com uma superfície rejeitada). Não há evidência neste subconjunto de túnel persistente ou volumes múltiplos separados. A inexistência de componentes no recorte atual NÃO exclui fenômenos em outros limiares, modelos ou períodos.

## 5. Visualização 3D efetiva

O experimento exporta arquivos `GLB` com HDRs 25%, 50%, 75% da GMM de duas metades da última janela selecionada. Os dois objetos são separados por translação **apenas visual** no palco 3D; nenhuma medição usa esse deslocamento. Os arquivos de malha e os CSV/JSON estão nos artefatos do Actions:
- `sgv-isosuperficies-1m`
- `sgv-isosuperficies-1h`

Os objetos GLB são um **resultado calculado a partir do BTC real exploratório**, não ilustrações genéricas.

## 6. Limites e próximos passos

1. Seis janelas selecionadas por escala são insuficientes para inferência de frequência, estabilidade ou significância estatística da não convexidade. A região K<0 **não está ainda sob bootstrap em blocos e análise de sensibilidade aprofundada**.
2. A grade passou duas verificações por escala, mas ainda não foi certificada a convergência de todas as curvaturas em todas as janelas; curvatura diferencial próxima de zero requer tolerância e controle.
3. A posição e a forma dependem das coordenadas gaussianizadas, do domínio truncado, da HDR e do ajuste GMM2. Não são um sólido físico absoluto.
4. A decomposição em quatro movimentos é convencional e depende do alinhamento. A variação do ângulo de rotação só é significativa quando os eixos principais são distinguíveis.
5. Não se demonstrou medição estável por 24 horas em WebSocket real; o streaming REST anterior tinha duas barras novas.
6. O SF1 calibrado pelo histórico anterior falhou em reproduzir a persistência de atividade em lag10. É necessário aprimorar o controle temporal para atribuir discrepâncias geométricas.
7. Próximo experimento decisivo: bootstrap de curvatura analítica K<0 com blocos temporalmente correlacionados, permutações/nulos SF1 aperfeiçoados, convergência com grade e HDR, e visualização seriada com um número maior de janelas.

## Reprodutibilidade

- Código: `experiments/isosuperficies_morfometria.py`
- Testes: `tests/test_isosuperficies_morfometria.py`
- Protocolo: `reports/PROTOCOLO_ISOSUPERFICIES_M1_20261009.md`
- Workflow: `.github/workflows/isosuperficies-morfometria.yml`
- Actions, revisão final: https://github.com/ana-rigel/sgv-geometria/actions/runs/37945591837
- `main` intacta; períodos confirmatórios reservados preservados.
