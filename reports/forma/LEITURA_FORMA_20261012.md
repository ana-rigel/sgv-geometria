# A forma da casca HDR50 do BTC — investigação descritiva (12/10/2026)

**Ramo:** `research/forma-isosuperficie`. **`main` intocada. Só dados exploratórios** (1m mai–jul/2026; 1h 2020–2024), as mesmas 6 janelas por escala e o mesmo método do M1 (âncora 30% + metades; GMM2; curvatura gaussiana analítica), com grade 49³. Descritivo, sem inferência.
Scripts: `scripts/forma_isosuperficie.py` (componentes e selas), `scripts/forma_checagens.py` (checagens sem modelo), `scripts/forma_figuras.py` (figuras). Figuras: `fig1_cascas_3d.png`, `fig2_o_que_da_a_forma.png`.

## A forma: um "coração" deitado na diagonal compra/venda
1. **Esticada na diagonal compra/venda.** Retorno e agressão andam juntos (correlação ~0,6 no 1m, ~0,55 no 1h): minutos de alta são de agressão compradora, e de baixa, vendedora.
2. **Dois lóbulos com uma cintura.** A mistura de duas gaussianas separa, em 10 das 12 janelas, um lado comprador (retorno e agressão > 0) de um vendedor (< 0), com pesos parecidos. Entre eles fica uma cintura em sela (curvatura negativa; 16–27% da área nessas janelas). Nas 2 janelas restantes do 1m, a separação foi por nível de volume e as selas quase somem (3%).
3. **Um cone ao longo do volume.** Vista de frente (retorno × volume), a casca é estreita embaixo (volume baixo) e larga em cima (volume alto), com um entalhe no topo: com muito volume, o minuto vai para um lado; com pouco volume, fica perto do neutro.

## O que os dados confirmam sem o modelo (6 janelas por escala)
- **Cone:** o desvio-padrão do retorno sobe do quintil de volume mais baixo para o mais alto de **0,63 → 1,25** (1m) e **0,59 → 1,42** (1h). A agressão não muda (~1,0). É a fotografia do "a atividade governa a escala" (M28).
- **Topo achatado na diagonal:** curtose −0,24 (1m) e −0,28 (1h); menos minutos neutros que numa elipse (massa central 0,96× e 0,90× a normal).
- **O achatamento cresce com o volume no 1h:** curtose −0,23 → −0,65 e massa central 0,96× → 0,80–0,84× do quintil mais baixo para os mais altos. No 1m também aparece (até −0,46), mas sem ordem clara.
- **Ressalva:** nos cortes do modelo ajustado (GMM2), a casca do 1m em volume alto se parte em duas ilhas. Nos dados, o centro **esvazia, mas não se parte**: a separação total é exagero do modelo de duas gaussianas.

## Leitura
A forma da casca é a geometria de três fatos de funcionamento: o preço se move junto com o lado que agride; com pouco volume quase nada acontece; com muito volume o minuto "escolhe um lado". Nada disso fala de direção futura: são relações dentro do mesmo minuto.

## Poderia ser um toro? (checagem adicional, 12/10/2026)
`scripts/forma_toro.py` e `scripts/forma_toro_controle.py`: topologia das HDR 25/50/75 com densidade **livre** (KDE gaussiano), nas mesmas 6 janelas × 2 metades por escala, com suavização padrão (Scott) e reduzida (×0,7, ×0,5), e um **controle** com amostras gaussianas (sem furo por construção) do mesmo tamanho e covariância.
- **Suavização padrão:** nenhum furo (gênero 0) em todas as superfícies válidas, 1m e 1h — igual ao M1 com GMM2.
- **Suavização reduzida:** furos aparecem, mas sempre junto com pedaços soltos, e **na mesma taxa no controle gaussiano** (ex.: ×0,5, HDR50: 12/12 real × 11/11 gaussiano no 1m; 12/12 × 12/12 no 1h). São bolhas de ruído de amostra (~525 pontos por metade), não um anel.
- **Conclusão:** nada indica toro. A forma é de gênero 0 (feijão/coração): os dois lóbulos se ligam em volume baixo e se afastam em volume alto, sem uma segunda ponte que fechasse um anel.

## A forma se desfaz e se remonta? (checagem adicional, 12/10/2026)
`scripts/forma_movimento.py`: janelas móveis de 6 h (passo 1 h, 2.197 janelas) no 1m mai–jul/2026, cópula local; nulo = a mesma série com os minutos embaralhados no tempo e as mesmas janelas móveis (mesma sobreposição).
- **Cintura** (massa central da diagonal compra/venda entre os minutos de volume alto; 1 = elíptico): varia 1,25× mais que no nulo; cintura forte (abaixo do p5 do nulo) em **11,9%** das janelas contra 4,8% no nulo; episódios duram ~2,4 h (nulo 1,75 h, efeito da sobreposição); persistência entre janelas sem sobreposição: 0,20 em 6 h, ~0 em 24 h (nulo ~0). O centro nunca se esvazia: mínimo 0,32× a normal, abaixo de 0,5× em só 1,1% das janelas.
- **Cone** (dp do retorno no volume alto / no volume baixo): varia **2,1×** mais que no nulo (p10–p90 1,46–2,20 contra 1,49–1,86), persistência 0,51 em 6 h e 0,20 em 24 h (nulo ~0).
- **Leitura:** a forma respira. A cintura aparece e some em episódios de poucas horas; a abertura do cone muda bastante e lentamente (escala de um dia) — a imagem geométrica da não estacionariedade do M27. Nada disso chega a partir a casca nem a fechar um anel em janelas de 6 h. Com ~360 pontos por janela, a topologia (furos) não é medível com confiança (ver controle gaussiano).
