# SGV-M8 — Transformações tridimensionais das cascas HDR50

**Registro pré-execução — 09/10/2026.** Ramificação `research/m8-transformacoes-forma-3d`. Não alterar `main`, nem acessar BTC confirmatório.

## Pergunta
Conseguimos caracterizar de forma quantitativa **como** as cascas HDR50 da densidade `p(z,iota,nu)` mudam entre duas fotografias, para além da diferença escalar de não convexidade `ΔD`? SF1, M5 ou M6 reproduzem os movimentos de uma forma melhor? Não há expectativa de previsão, tensão financeira ou lei geométrica inédita.

## Quatro componentes operacionais da transformação
1. **Deslocamento**: `c_B - c_A`, centros volumétricos da região HDR50, em coordenadas fixas, transformadas pela âncora histórica anterior. Norma euclidiana separadamente.
2. **Expansão**: `log(V_B / V_A)`, com volumes de malhas fechadas, e fator isotrópico `(V_B/V_A)^(1/3)`.
3. **Orientação**: eixos principais do **sólido HDR** a partir da inércia volumétrica. Um ângulo de rotação é reportado apenas quando os autovalores estão bem separados (gap relativo ≥ 0,07). Autovetores têm ambiguidade de sinal; resolver pelo alinhamento de forma. Um sólido próximo de esfera ou rotacionalmente simétrico não define rotação global estável: registrar nulo, sem interpolação fictícia.
4. **Deformação residual**: distância Chamfer simétrica aproximada entre pontos de superfície após remover translação, rotação e escala isotrópica. Escalar é um resíduo de *forma*, não deslocamento material ou transporte causal. Para orientação quase degenerada, informar deformação alinhada como **não identificável** e não atribuir valor zero.

**Importante:** Essas quatro saídas são descritores parcialmente convencionais e **não formam uma partição matemática aditiva única do transporte de probabilidade**. Não somar os valores como um movimento total. O alinhamento obtido por eixos principais e pontos amostrados tem incerteza própria.

## Geração das superfícies
- Ajustar GMM2 às duas metades cronológicas (aprox. 35% e 35%) após os primeiros 30% fixarem a transformação marginal de scores de postos.
- Extrair `p(x)=tau_HDR50` em grade 35³ (domínio `[-3.5,3.5]^3`) com Marching Cubes; seguir portas M1 de fechamento, ausência de truncamento, massa na grade ≥95%, volume positivo.
- Controles adicionais `D` e `C` não convexos herdados do M2, apenas para interpretar diferenças entre descrição morfológica e mudanças globais.

## Desenho exploratório
- BTCUSDT spot 1m maio–julho/2026, prefixo 5000 candles + 1500 avaliados; BTC spot 1h 2020–2024, prefixo 2000 + 1008.
- Seis origens sem lacunas e não sobrepostas, equiespaçadas deterministicamente dentre elegíveis. Três simulações pareadas por origem e modelo (SF1, M5, M6), com 1700 candles de aquecimento. Uma janela usa modelos ajustados **somente no prefixo**.
- Compare erro absoluto das medianas sintéticas versus movimento observado. Em três origens por escala, bootstrap circular da fotografia real com 12 reamostragens em blocos (1m: 15; 1h: 12), sem treinar novos mapeamentos marginais futuros; registrar quantis descritivos e proporção de amostras válidas.
- Em primeira/última origem válida, repetir grade 49³ para deslocamento, log(volume) e deformação residual, com **mesma semente** na amostragem de superfície.
- **Critérios de qualidade:** no mínimo 2 simulações válidas das 3 em cada modelo para inferir erro numa origem; diferenças de rotação nunca comparadas se uma das formas não permite eixos únicos; não escolher vencedor geral se menos de quatro origens tiverem pares completos.
- Resultados de simulação morfológica dependem de janelas, malhas, GMM e resolução; nulos SF1 não inteiramente calibrados para regimes.

## Controles sintéticos
Esferas transladadas: deslocamento sem rotação identificável. Elipsoides com deslocamento e expansão conhecidos: recuperar centro, volume e ângulo compatíveis, resíduo próximo de zero sujeito a discretização. Testar lacunas temporais, falhas de malha, repetibilidade por seed e não repintar histórico após alterar futuro.

## Saídas
`reports/SGV_M8_1m.json`, `reports/SGV_M8_1h.json`, tabelas CSV e relatório interpretativo. A análise é **descritiva e exploratória**; não constitui teste confirmatório, sinal de trading, curvatura Fisher–Rao intrínseca nem prova de tensão.
