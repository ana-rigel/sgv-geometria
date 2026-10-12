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
