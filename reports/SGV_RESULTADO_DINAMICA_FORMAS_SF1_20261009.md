# SGV — Dinâmica das formas sob SF1 ajustado ao passado
**Data:** 09/10/2026. **Ramo:** `research/dinamica-formas-sf1`. **Execução:** GitHub Actions #37940491529, três jobs concluídos com sucesso.

## Pergunta observacional
As mudanças em regiões de densidade tridimensional de (retorno normalizado, fluxo agressor, atividade relativa) observadas entre duas metades cronológicas podem ser reproduzidas por trajetórias sintéticas SF1 ajustadas apenas ao histórico anterior da janela?

## Procedimento
- SF1 via `fit_sf1`, a partir de prefixo de **2000 candles anteriores**; em seguida, janela observada W=1500 (1m) ou W=1008 (1h).
- Dentro da janela, primeiros 30% definem marginais gaussianizadas comuns. Duas metades posteriores de 35%/35% estimam Gaussianas e misturas GMM2 3D independentemente. HDR25/50/75 na grade [-3,3]^3.
- Para cada janela observada, **quatro simulações SF1** de W+1700 candles com aquecimento. As simuladas são transformadas em coordenadas SGV e medidas pelo mesmo algoritmo HDR, cada simulação com âncora própria anterior às duas metades.
- Até doze origens de janelas equiespaçadas por índice, stride W/2: avaliações **sobrepostas**. Qualquer gap de timestamp ou não finito invalida a janela. Estimativa exploratória sem p-valores confirmatórios, somente contrastes descritivos.
- Dados BTCUSDT spot em períodos exploratórios: 1m maio-julho/2026 e 1h 2020–2024, com allowlist de arquivos e checksum no downloader. Holdouts anteriores não foram abertos.

## Controles
**5 testes automatizados aprovados.** A mudança artificial no fluxo após o prefixo reduziu Jaccard da GMM HDR50 de 0,79325 a 0,63793 sem alterar parâmetros de fit SF1 nem simulações nulas com mesma seed. A invariância temporal do ajuste passou.

## Resultados

Jaccard mediano das HDRs GMM2 entre duas metades:

| Métrica | 1m (12 janelas válidas) | 1h (7 janelas válidas) |
|---|---:|---:|
| HDR25 observado | 0,42474 | 0,34708 |
| HDR25 SF1 (mediana por janela) | 0,69966 | 0,62872 |
| HDR50 observado | 0,57453 | 0,48336 |
| HDR50 SF1 (mediana por janela) | 0,78798 | 0,72810 |
| HDR75 observado | 0,65402 | 0,50612 |
| HDR75 SF1 (mediana por janela) | 0,81344 | 0,76574 |
| Fração observação HDR50 menos estável que todas 4 simulações | 11/12 | 5/7 |

Para a gaussiana simples, HDR50 observado e SF1 foram: 1m 0,63129 versus 0,84473; 1h 0,51425 versus 0,80566. Logo o contraste não depende exclusivamente de ajustar GMM2 flexível.

**Resultado descritivo:** os estados observados oscilaram morfologicamente mais entre as duas metades do que os gerados pelo SF1 prefix-only ajustado, no conjunto selecionado de amostras. É uma discrepância entre representações **sujeita à inadequação do modelo nulo**, não confirmação de novas leis ou fluxo causal.

## Limitações decisivas
- Apenas quatro simulações SF1 por janela: probabilidade de extremos simulados muito imprecisa; não produzir p de rejeição.
- Janelas sucessivas sobrepostas e selecionadas por índice, não independentes; percentuais são descritivos.
- SF1 ajustado a 2.000 candles e aplicado ao futuro pode perder mudanças de regime e sazonalidade, clusters de volatilidade ou dependências condicionais reais. **Ainda não auditamos se reproduz distribuições marginais, autocorrelação e mudanças de regime** com fidelidade suficiente.
- SF1 gera resíduos pareados amostrados; adequação em escala 1h, onde foram só sete origens sem gaps, deve ser conferida.
- HDRs são modelos estimados em um espaço de observáveis; não são curvatura Fisher–Rao intrínseca, topologia universal, causalidade informacional ou retorno futuro.
- Sem livro de ordens, notícias, cancelamentos ou dados de trades individuais.

## Diagnóstico científico atual

**Sim:** conseguimos ajustar um nulo temporalmente causal e avaliar deformações HDR em janelas deslizantes; observamos desvios dos padrões de estabilidade do SF1 em 1m e 1h.

**Ainda não:** não sabemos se são propriedades da organização informacional que escapam a modelos comuns melhor calibrados ou diferenças triviais de nível de volatilidade, mudanças de regime e insuficiência de SF1. Não foram identificadas duas regiões desconectadas estáveis, curvatura própria ou capacidade de previsão.

## Próxima execução proposta (ainda não realizada)

1. Auditoria de calibração SF1: confrontar amostras observadas e simuladas para quantis/caudas de z, iota, nu, correlação cruzada e ACFs de |r|/volume/fluxo.
2. Controles sazonais e estacionariedade local, repetição com comprimento de prefixo alternativo sem abrir períodos reservados.
3. Trajetórias mais longas e simulações suficientes para intervalos, respeitando que as janelas se sobrepõem.
4. Estudar modelos não gaussianos condicionais à atividade sem identificar componente do GMM como estado físico.

## Reprodutibilidade
- `experiments/dinamica_formas_sf1.py`
- `tests/test_dinamica_formas_sf1.py`
- `.github/workflows/dinamica-formas-sf1.yml`
- `reports/PROTOCOLO_DINAMICA_FORMAS_SF1.md`
- Execução: https://github.com/ana-rigel/sgv-geometria/actions/runs/37940491529
- Artefatos JSON e CSV por escala disponíveis na execução.
- `main` preservada.
