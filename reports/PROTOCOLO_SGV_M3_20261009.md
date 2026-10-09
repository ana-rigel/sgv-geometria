# SGV-M3 — Precisão da Não Convexidade das Isosuperfícies (09/10/2026)

**Registro pré-execução.** Pesquisa observacional independente; a `main` e as amostras confirmatórias reservadas permanecem inalteradas.

## Decisão científica

O indicador de não convexidade (`D`) é **um descritor geométrico das distribuições estimadas**, não um oscilador de tensão ou estresse do mercado. A hipótese de associação com discrepância preço–fluxo no M2 foi fraca (+0,091 em 1m; −0,176 em 1h, com dez janelas por escala) e não será rebatizada. A etapa M3 testa **a precisão de D**, sem retestar correlação com retorno ou fluxo.

## Variáveis e objeto

`X_t=(z_t,iota_t,nu_t)` são retorno normalizado por passado, desequilíbrio contemporâneo do fluxo agressor e atividade relativa em volume. Para cada janela fechada: primeiros 30% definem CDFs marginais compartilhadas e congeladas; as duas metades posteriores (35%+35%) são tratadas como dois estados observados, sem futuro na primeira fotografia. Modelo de densidade principal: mistura de duas gaussianas 3D (GMM2); controle geométrico: gaussiana única.

Os limiares `tau_alpha` de HDR25/50/75 são calculados a partir da massa discreta no cubo `[-3.5,3.5]^3`. Marching Cubes produz a casca triangular. Exigir ausência de truncamento, malha fechada, cobertura de massa >=95% e volume positivo.

## Métricas e hipóteses

**Índice principal de não convexidade:**
`D_alpha = integral max(0,-K(x))*r² dA / A`
com `K` calculado a partir da Hessiana da densidade **projetada no plano tangente** e `r=(3V/4pi)^(1/3)`. A intensidade normalizada é adimensional, mas depende do sistema de coordenadas e do nível HDR.

**Controles complementares:**
- `F_alpha = area(K*r² < -0.1)/area_total`, rejeitando falsos sinais negativos muito próximos do zero.
- `C_alpha = 1-V(HDR)/V(convex_hull)`: déficit de convexidade volumétrico, que mede uma propriedade global distinta de K.
- Uma gaussiana elipsoidal possui K>=0. Uma GMM2 ajustada a dados gaussianos pode produzir D>0 devido a variação amostral: por isso precisamos de nulos **ajustados**, não só gaussiana como família de referência.
- Não inferir lóbulos por `K<0` sem testes geométricos adicionais.

## Bateria predefinida

1. **Calibração sintética:** amostras gaussianas, amostras elípticas Student-t e misturas com dependência conjunta não gaussiana; verificar integridade da malha e comportamento básico dos descritores, sem assumir detecção perfeita.
2. **Estabilidade de grade:** comparar resoluções 25³, 35³ e 49³ em uma seleção fixa de três janelas por escala, medir variação relativa de D e C, e identificar casos em que uma malha deixa de ser válida. Uma auditoria insuficiente não autoriza afirmar precisão total.
3. **Bootstrap circular em blocos:** na mesma seleção de três janelas, reamostrar separadamente cada metade por 29 replicações, com dois comprimentos de bloco (1m: 8/20 candles; 1h: 6/16), mantendo congeladas as transformações marginais anteriores. Intervalos obtidos têm caráter **diagnóstico**, não cobertura nominal garantida. Identificar instabilidade de D entre estimações e variação da diferença D(B)-D(A).
4. **Controle de sobreajuste do GMM2:** por metade auditada, gerar 29 conjuntos gaussianos e 29 Student-t elípticos com média/covariância ajustadas na própria metade (nulos meramente morfológicos). Ajustar **a mesma GMM2** e comparar D HDR50 observado com a distribuição de D gerado a partir de formas teoricamente convexas. Nulos não preservam persistência temporal, regimes nem clusters de volatilidade; não substituem SF1 estendido.
5. **Replays reais:** BTCUSDT spot, apenas exploratórios, 1m maio–julho 2026 e 1h 2020–2024, dados validáveis por checksum. Até 20 janelas disjuntas e sem gaps por escala; para nulos/grade/bootstrap usar três selecionadas determinística e uniformemente por índice, sem olhar resultados.
6. Resultados em JSON/CSV e GitHub Actions com logs e causas explícitas de descartes. Não calcular probabilidades confirmatórias, não misturar escalar D com indicador de estresse.

## Critérios de leitura

- **Precisão numérica:** similaridade entre n=25,35,49; se houver grandes diferenças, a grade ainda é insuficiente.
- **Incerteza estatística:** dispersão do bootstrap entre amostras fechadas; se intervalos amplos, não afirmar deformação precisa.
- **Adequação dos nulos:** valores altos de D sob gaussiana ou Student-t ajustados impedem alegar singularidade morfológica a partir de D real isolado.
- **Estabilidade temporal e causalidade:** o fluxo de dados permanece no fechamento do candle; mudanças entre metades não provam transferência causal de informação nem vantagem preditiva.

## Artefatos

`experiments/m3_precisao_nao_convexidade.py`, `tests/test_m3_precisao_nao_convexidade.py`, `.github/workflows/m3-precisao-nao-convexidade.yml` e relatórios `reports/SGV_M3_*.json`.

**Nota:** o método mede cascas de densidade em coordenadas gaussianizadas, não a curvatura intrínseca da variedade Fisher–Rao.
