# SGV-M10 — Piso de amostragem do registro 3D e precisão das mudanças de forma

**Pré-registro: 09/10/2026.** Código e resultados somente em `research/m10-piso-amostragem-registro`. `main` não será alterada; nenhuma observação dos intervalos confirmatórios reservados (1m a partir de agosto/2026; 1h a partir de janeiro/2025).

## Problema

O M9 separou rotação dos eixos principais (`SO(3)/D2`, somente se distinguíveis) de deformação residual por ICP multistart e Chamfer simétrica em pontos de teste independentes. Entretanto, mesmo duas malhas exatamente equivalentes dão uma distância > 0 porque pontos são amostrados independentemente na superfície. O M10 quantifica esse **piso de amostragem condicionado à malha e ao número de pontos** antes de interpretar pequenas variações como deformações reais.

## Observável e controles

- Reutilizar `compare_meshes` do M9 com treino independente do teste, rotação `SO(3)` por ICP/Kabsch, translação por centro de massa e escala pelo raio volumétrico equivalente.
- `d(A,B;n,s)` é o Chamfer holdout no número `n` de pontos para treino **e** `n` para teste, com semente `s`.
- **Piso nulo:** `d(A,A;n,s)` e `d(B,B;n,s)`, amostragens independentes por lado e por semente, usando a própria malha. Também controles rigidamente transformados `d(A,R(A);n,s)` e deformados por mudança de eixos `d(A,T(A);n,s)`, calibrados antes de olhar BTC.
- `d_observado` = mediana sobre seis sementes independentes. Piso local conservador `F_n=max(Q90[d(A,A)],Q90[d(B,B)])`, com **seis réplicas por controle**; reportar `E_n = max(0, mediana(d(A,B))-F_n)`, mas **E_n não é uma distância corrigida sem viés nem teste de significância**. Pode censurar diferenças reais e não controla a taxa de falsos positivos sem calibração independente.
- **Diagnóstico de detectabilidade:** `mediana(d(A,B)) > F_n`, interpretado exclusivamente como exceder o controle de amostragem nas seis sementes. Reportar variação entre sementes, amplitude bootstrap e casos nulos sem forçar diferença.
- **Precisão por resolução de amostragem:** três pontos de trabalho pré-fixados `n=180,360,720`, mantendo o método de alinhamento constante, cinco ou seis sementes por condição. Aumentar n deve reduzir o piso em geral, mas monotonicidade estrita em cada realização não é esperada.
- **Precisão de malha:** comparar grade Marching Cubes de 35³ versus 49³ em três janelas por escala. Separar efeito da malha do efeito de amostragem usando mesmas sementes.
- **Bootstrap temporal da fotografia real:** 16 reamostragens circulares em blocos por metade (1m, bloco L=15; 1h, L=12), mantendo mapa marginal original; descrever quantis p10/p50/p90 de `d(A',B')` e de seu excesso sobre pisos locais (cada bootstrap usa **três** sementes e um controle self por lado). Bootstrap é diagnóstico de incerteza do estimador, **não** intervalo de confiança calibrado.
- Auditoria da rotação por quociente `SO(3)/D2` nas mesmas 16 reamostragens: fração identificável, quantis e ângulos >90°. Não correlacionar automaticamente rotação com causalidade ou tensão.

## Amostragem BTC pré-fixada
Somente BTCUSDT spot exploratório do downloader com allowlist e checksum: 1m maio–julho/2026; 1h 2020–2024. Candidatas não sobrepostas, contínuas e com candles completos, elegibilidade verificada por timestamp. **Seis janelas por escala**, selecionadas em índices equiespaçados sem olhar os resultados. Três janelas auditadas com múltiplas amostragens/resoluções e bootstrap (primeira, intermediária e última); as seis têm medição e piso local com seis sementes em n=360. As fotografias A e B compartilham mapa marginal fixado nos primeiros 30% da janela (M1–M9). Não reajustar o mapa em dados futuros.

## Portas de qualidade
- Malha fechada, não truncada, massa da grade >=95%, volume positivo. Em caso contrário não emitir geometria nem piso fabricados.
- Não relatar detectabilidade se menos de quatro de seis controles válidos, modelo de registro falhou ou não há malha válida.
- Registro ICP com múltiplos inícios e score em pontos *holdout* independentes. Rotação por eixos apenas se ambos os sólidos tiverem lacuna espectral >=0,07; caso contrário ângulo `null`, mas deformação pode ser mensurada.
- Relatar diferença entre o nulo da mesma malha e o caso rigidamente equivalente, para evitar confundir erro de estimação geométrica com piso de pontos.
- Não escolher “modelo de mercado vencedor” nesta etapa: SGV-M10 calibra o **instrumento de registro**; a comparação SF1/M5/M6 com medidas corrigidas fica para etapa posterior, após congelar o critério.

## O que podemos e não podemos dizer
É legítimo inferir um **piso operacional aproximado** da métrica com dados e malhas fixos, separado da incerteza de ajuste GMM e da amostragem temporal. Exceder esse piso não constitui prova estatística de uma mudança real na densidade geradora; exceder o nulo de malha também não prova fenômeno financeiro especial. A superfície é extrínseca à densidade estimada em coordenadas gaussianizadas, não curvatura intrínseca Fisher–Rao. Sem interpretação como oscilador de estresse, lei física ou vantagem de negociação.

## Entregáveis
`experiments/m10_piso_amostragem_registro.py`; `tests/test_m10_piso_amostragem_registro.py`; `.github/workflows/m10-piso-amostragem-registro.yml`; artefatos JSON/CSV e relatório científico interpretativo.
