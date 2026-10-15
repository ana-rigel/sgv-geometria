# Previsão registrada antes de ver agosto–setembro/2026: forma de D × forma da casca

**Registrada em:** 15/10/2026, antes de qualquer cálculo desta medida em agosto–setembro. Esses meses foram abertos em 13/10 só para o H-σRTT-01, e ninguém mediu forma de D ou de casca neles.

**Status:** exploração fora da amostra, **não** confirmatória. Agosto–setembro já não são virgens. Esta rodada serve para ver se o achado de jun–jul se repete num segundo período antes de decidir um pré-registro (H-FORMA-D-02) para outubro ou novembro. Nada de outubro é lido.

## O que foi visto em jun–jul (Navegador SGV, 15/10)
- **Fluxo (z, ι, ν), mesmo mapa:** a mudança de forma de D acompanha a mudança de forma da casca. A correlação dFD×dFS@0 é +0,63 [0,55; 0,70] no real e **+0,88** [0,83; 0,91] na nula de pipeline. O mercado real **desacopla** as duas formas em relação ao que as fórmulas impõem.
- **Nenhuma defasagem com D antecedendo (j > 0)** fica acima da nula, nos dois espaços.
- **Original:** acoplamento fraco no real e na nula (+0,20 / +0,12), sem diferença clara.

## Previsões para agosto–setembro (mesmo código, mesmas medidas, sem mudança)
1. **Primária, fluxo, dFD×dFS@0:** real < nula. Previsão de diferença real − nula ≈ −0,25, com os ICs de 95% sem sobreposição.
2. **Fluxo, angD×angS@0:** real < nula.
3. **Antecede, dFD×dFS@+1 e @+2:** real não acima da nula, nos dois espaços.
4. **Original:** sem diferença clara entre real e nula no mesmo mapa.

## Critério de leitura
- **"Repete":** a previsão 1 com os ICs sem sobreposição.
- **"Repete fraco":** real abaixo da nula, com os ICs sobrepostos.
- **"Não repete":** real ≥ nula.

Aposta de Claude, antes dos dados: repete ~55%, repete fraco ~25%, não repete ~20%.

## Como roda
`.github/workflows/explora-forma-D-casca.yml`, disparado pelo push deste ramo:
1. Baixa agosto e setembro da Binance e confere o SHA-256.
2. Roda `pipeline/explora_forma_D_casca.py --periodo agoset`.
3. Grava `resultados/forma_D_casca_agoset.json` e o log neste ramo.

A paridade do script com a exploração de jun–jul foi conferida localmente antes deste commit. No fluxo, os 25 valores real/nula e os ICs saíram idênticos (dFD×dFS@0: +0,627 / +0,878). O arquivo completo `resultados/forma_D_casca_junjul.json` entra num commit seguinte, que não dispara o workflow.
