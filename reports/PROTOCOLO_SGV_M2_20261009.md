# SGV-M2 — Protocolo de Não Convexidade e Tensão Informacional (09/10/2026)

**Status:** protocolo exploratório registrado antes de analisar novos resultados. **Ramo:** `research/m2-nao-convexidade-tensao`, sem alterar `main`. Nenhum período BTC confirmatório reservado será aberto.

## Pergunta principal
A não convexidade das isosuperfícies das distribuições de `X=(z,iota,nu)` pode ser medida com precisão e está associada à discrepância condicional entre retorno normalizado e fluxo agressor/atividade, sem confundir a forma estatística com causalidade?

## Dois instrumentos distintos
1. **Índice geométrico M2-G**: sobre malha Marching Cubes da densidade tridimensional estimada, usar gradiente e Hessiana analíticos de `p(x)`, **projetados no plano tangente** à isosuperfície. Os autovalores relevantes são as duas curvaturas principais (`k1,k2`), não os três autovalores brutos da Hessiana. `K=k1*k2`. Definir `r=(3V/(4*pi))^(1/3)` e `D_alpha=(1/A) integral_surface max(0,-K)*r^2 dA`. Registrar também proporção de área com `K*r² < -0.1` e `1-V/V(convex hull)`. São medidas de não convexidade dependentes de coordenadas, modelo e nível HDR; não são fluxo causal nem tensão financeira comprovada.
2. **Discrepância independente M2-T**: no primeiro trecho **30% anterior** de cada janela de candles fechados, estimar `z ~ 1+iota+nu` com regularização leve. Nas duas metades posteriores da janela, medir RMSE dos resíduos divididos pelo desvio-padrão dos resíduos do treino, **sem recalibrar** o modelo. Comparar `delta T` com `delta D` de uma mesma janela. Essa é uma discrepância contemporânea condicional, não uma previsão de preço, nem prova de divergência direcional.
3. **Associação M2-G × M2-T**: Spearman exploratório entre mudanças de forma e discrepância nas janelas válidas. **Não gerar p-value confirmatório** nem um único oscilador de “estresse” até demonstrar estabilidade, controles e condicionamento adequado.

## Controles e portas
- Gaussiana elipsoidal: `D≈0` por curvatura implícita (teste de falso negativo de curvatura da malha); convex hull deficit próximo de zero.
- Superfície aberta/truncada ou massa da grade insuficiente: rejeitar a métrica, não inventar valores.
- Perturbar apenas dados futuros: parâmetros de discrepância e fotografia do primeiro trecho não podem se alterar.
- Ressorteio circular em blocos de 15 (1m) e 12 (1h), com transformação marginal fixa no prefixo, para sondar estabilidade de M2-G. A rodada inicial é **piloto de engenharia**, com no máximo 10 reamostragens em duas janelas por resolução, não inferência estatística calibrada.
- Testar HDR25/HDR50/HDR75, normal 3D e GMM2. Primeiro executar simulações de controle; replays BTCUSDT apenas em meses exploratórios com allowlist e checksum.
- Só chamar o índice de “tensão informacional” se mostrar associação robusta após controlar volatilidade, regime, nível de atividade, sazonalidade e correlações convencionais. Caso contrário permanece descritor geométrico.

## Evidência científica anterior (contexto, não resultado novo)
O módulo M1 encontrou no subconjunto exploratório de HDR50: área mediana com `K<0` analítico de 16,7% (1m) e 21,4% (1h) em GMM2, contra 0% em Gauss. São deformações **da densidade ajustada**; não provam lóbulos, nova lei, pânico/euforia, nem tensão preço–fluxo. O controle SF1 teve deficiências na memória de atividade em lag10. Esses problemas motivam controles adicionais.

## Limitações
A curvatura positiva/negativa é extrínseca à superfície de nível em coordenadas gaussianizadas, não a curvatura intrínseca Fisher–Rao. O deficit do envoltório convexo não é um indicador de profundidade individual de depressão. Uma correlação positiva entre M2-G e M2-T pode ser causada por heterocedasticidade ou regime comum. A comparação não identifica direção causal. Malhas/estimadores dependem de domínio e grade.

## Links de reprodução
- Base M1: `experiments/isosuperficies_morfometria.py`.
- Código M2: `experiments/m2_nao_convexidade_tensao.py`.
- Testes: `tests/test_m2_nao_convexidade_tensao.py`.
- Workflow: `.github/workflows/m2-nao-convexidade-tensao.yml`.
