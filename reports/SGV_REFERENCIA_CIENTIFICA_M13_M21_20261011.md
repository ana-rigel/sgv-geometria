# SGV — Documento de referência científica, parte 2 (M13–M21)

**Data:** 11/10/2026. Continua `reports/SGV_REFERENCIA_CIENTIFICA_M1_M12_20261009.md` (ramo M13).
**Ramo deste documento:** `research/m21-m11-robusto`. **`main` intocada.**
**Função:** dizer, numa página de cada coisa, o que está estabelecido, o que foi refutado, o que segue aberto, quais dados já foram gastos e quais regras de trabalho valem daqui em diante. Cada linha aponta para o relatório que a sustenta.

## 1. Linha do tempo (M13–M21)

| Etapa | Pergunta | Resultado | Relatório |
|---|---|---|---|
| M13 | Calibrar falsos alarmes sob gerador conhecido | Implementado; posto válido só com parâmetros verdadeiros (oráculo) — não mede o erro de ajuste | `PROTOCOLO_SGV_M13_20261009.md` (ramo M13) |
| M14 | Calibração **aninhada** (nulo ajustado no prefixo) | VAR→VAR 6,2%; HMM→HMM 7,3% (levemente liberal); HMM→VAR 57,6%; HMM→blocos15 16,2% | `reports/m14_artefatos/` (ramo M15) |
| M15 | Forma × persistência; M11 contra comparadores | **Persistência e forma pesam** (GMM-IID 37%, VAR 60%); réguas **complementares**: M11 vê forma, energy vê massa/memória, Fisher–Rao a 2ª ordem | `SGV_M15_LEITURA_20261009.md` |
| M16 | Três réguas sobre N0–N3 no BTC exploratório | Nenhum nulo do M12 reproduz o BTC; falta principalmente **memória/massa**; a forma é o mais bem reproduzido; N1 falha na covariância | `SGV_M16_LEITURA_20261010.md` |
| M17 | Que tipo de memória? | **Markov de várias escalas** reduz a lacuna; envelhecimento (semi-Markov) e relógio **não** acrescentam; sobra ~30% | `SGV_M17_LEITURA_20261010.md` |
| M18 | Acoplamento dinâmico × memória longa | **Memória longa do nível de atividade** explica o resíduo; DCC (acoplamento rápido) não; **blocos reais de ~8 h (BL) fecham a lacuna no 1m** | `SGV_M18_LEITURA_20261010.md` |
| M19a | Alarmes do BL são choques de volatilidade? | **Não** (ρ≈0 com razão de vol., movimentos extremos e volume) | `reports/m19/SGV_M19a_LEITURA.md` |
| M19 | **Confirmatório:** alarmes marcam rupturas estruturais? (1m ago–set/2026) | **H-RUP não apoiada** (2/15 vs 1/43, p=0,155); todas as direções a favor; Fisher–Rao 4/15 vs 1/43 (não testado) | `SGV_M19_LEITURA_20261010.md` |
| M20a–e | Dependência temporal que as marginais/2ª ordem não veem (sintético) | Marginais **não identificam** a dinâmica (M20a/b); detectar H± exige **saber a direção** (M20d); aprender a direção do passado falha em H± (M20e); geometria (W2/CQW2) **não** supera HSIC | `SGV_M20a..e_LEITURA_20261011.md` (ramos M20*) |
| Nota M20 | Kernels 3D invariantes resolvem H±? | **Não** (HSIC gaussiano e dCov ≤10% com N=1800 e nulo conhecido): o gargalo é informacional | `reports/m20nota/` (ramo `research/m20-nota-kernels-invariantes`) |
| **M21b** | O BTC tem dependência entre instantes que o melhor paramétrico não reproduz? | Sim, mas **compatível com memória de volatilidade** (lags 1, 5); **nada do tipo M20**; o paramétrico falha até na dependência **linear** de curto prazo; BL levemente liberal (~10–15%) | `SGV_M21b_LEITURA_20261011.md` (ramo M21b) |
| **M23** | Um modelo mínimo explícito (2 escalas + VAR(1) + GARCH + bloco lento real) reproduz o BTC 1m? | Melhora enorme no lag 1 (lin 70→13%, vol 88→23%), mas **não fecha a lacuna**: falta a escala **intermediária (~5–15 min)** e a forma não gaussiana | `SGV_M23_LEITURA_20261011.md` (ramo M23) |
| **M24** | HAR (1/15/60 min) + inovações reais filtradas fecham a lacuna? | Grande avanço (HSIC_5 60→32%, M11 33→18%), mas **não fecha**: falta **memória de volatilidade multiescala**; a forma não gaussiana mora nas **inovações** | `SGV_M24_LEITURA_20261011.md` (ramo M24) |
| **M25** | Volatilidade multiescala por coordenada (HARCH 1/15/60/240) fecha o resto? | **Não** (vol inalterada); diagnóstico exploratório: o descompasso é **cruzado** — após |retorno| grande, a agressão do minuto seguinte é **mais equilibrada** que o modelo prevê (100% das origens checadas): assinatura de **resiliência da liquidez** | `SGV_M25_LEITURA_20261011.md` (ramo M25) |
| **M26** | Volatilidade cruzada (resiliência) fecha o resto? | **Mecanismo confirmado em dados exploratórios:** choque de preço reduz a volatilidade da agressão no minuto seguinte em **83/83** origens; acoplamento (Fisher–Rao) agora igual ao BL; **não fecha**: resta dependência não linear/volatilidade em 5–30 min (provável não estacionariedade dos parâmetros) | `SGV_M26_LEITURA_20261011.md` (ramo M26) |
| **M27** | O resto (vol/HSIC em 5–30 min) é **não estacionariedade dos parâmetros**? | **Sim para a volatilidade:** parâmetros locais (~13 h) levam vol_5/vol_30 de 21% a 10/7% (= BL) e vencem o controle de ruído; modelo **indistinguível do BL em 10 de 12** estatísticas; resta só **HSIC 5/30** (27% vs 12–14%): dependência não linear que não é volatilidade. Resiliência negativa em 97% dos 504 trechos locais | `SGV_M27_LEITURA_20261011.md` (ramo M27) |
| **M28** | A **atividade** (volume) governa a escala do retorno e da agressão? | **Mecanismo confirmado nas origens de teste** (ímpares, não vistas no diagnóstico): mais volume → retorno mais volátil (41/42) e agressão mais concentrada perto de zero (42/42) — mistura de distribuições minuto a minuto. **HSIC não melhora**; pós-hoc: sem o volume, a dependência não linear já está reproduzida — o resto mora na **dinâmica própria do volume** (30 min) | `SGV_M28_LEITURA_20261012.md` (ramo M28) |
| **M29** | O volume tem um **relógio de minuto da hora**? | **Sim:** pico no :00 (81% dos prefixos de teste), na meia hora, vale em :57–:58; com o relógio, hsic_30 cai 29→21% (n.s., 4×1) e deixa de ser pior que o BL; o modelo agora é pior que os blocos reais **só em hsic_5** (24% vs 11%) | `SGV_M29_LEITURA_20261012.md` (ramo M29) |
| **M21a** | Por que o M11 falha sob BL? | Pontos fora da faixa da âncora se empilham no extremo → componente GMM degenerado → casca aberta. **Regra do posto conservador** recupera 82/84 (M18) e 54/58 (M19) sem mudar o instrumento | `reports/m21/SGV_M21a_LEITURA.md` |

## 2. O que está estabelecido (até aqui, com as ressalvas de cada relatório)

1. **A geometria descreve a estrutura da incerteza, não a direção do preço.** (SGV ao vivo, ΔF, M16–M18.)
2. **O BTC no 1m tem memória multiescala e longa** (minutos a muitas horas) do nível de atividade; é isso que os modelos paramétricos mais não reproduzem. (M16–M18.)
3. **Existe um nulo adequado no 1m: blocos reais de ~8 h (BL)** — ~7–10% de alarmes nas três réguas, perto do nível de uma família correta (~7%, M14/M15). No 1h, nem blocos de uma semana bastam. (M18, M21a.)
4. **As três réguas são complementares e juntas diagnosticam o tipo de inadequação:** M11 ≫ energy → falta forma; energy ≫ M11 → falta memória/massa; Fisher–Rao alto → falta acoplamento. (M15, M16.)
5. **As marginais não bastam para a dinâmica:** duas dinâmicas diferentes podem ter as mesmas fotografias. A geometria das cascas tem nicho em **forma**; para **dinâmica/acoplamento temporal**, kernels e covariâncias convencionais são iguais ou melhores. (M20a–e.)
6. **Nulos ajustados no passado são levemente liberais** (~7% contra 5%) mesmo quando a família é correta. (M14.)

## 3. O que foi refutado ou não apoiado

- Curvatura de Fisher como informação própria além da volatilidade (G1, R1, L2 — fase anterior).
- "A forma pesa mais que a persistência" — leitura pós-M14, **corrigida** pelo M15.
- Acoplamento dinâmico rápido (DCC) como explicação do resíduo (M18).
- Envelhecimento e relógio como memória faltante (M17).
- **H-RUP no confirmatório 1m ago–set/2026** (M19) — inconclusivo por poder, mas não apoiada pela regra.
- Kernels invariantes a rotação como solução para H± (nota M20).

## 4. Em aberto (por prioridade)

1. ~~Existe no BTC dependência temporal não linear além da volatilidade?~~ **Respondido no M21b: não nesta escala** → linha M20 encerrada. Em aberto agora: um **modelo mínimo** que feche a lacuna sem blocos reais — o M23 mostrou que duas escalas + VAR(1) + GARCH não bastam; o M24 resolveu boa parte da escala intermediária (HAR) e da forma (inovações reais); o M25 mostrou que a volatilidade multiescala por coordenada não resolve; o M26 confirmou a **resiliência da liquidez** (83/83 origens) e reproduziu o acoplamento; resta 17–31% de alarmes de volatilidade/dependência não linear em 5–30 min; o M27 mostrou que a parte de **volatilidade** era **não estacionariedade dos parâmetros** (o funcionamento muda ao longo do dia; com parâmetros de ~13 h o modelo empata com o BL em 10 de 12 estatísticas). O M28 confirmou que a **atividade governa a escala** (42/42 e 41/42 nas origens de teste), mas o HSIC não mudou; o pós-hoc mostra que, sem o volume, a dependência não linear já está reproduzida. O M29 achou um **relógio de minuto da hora** no volume (pico no :00) que explica parte do resto em 30 min. Em aberto agora: **uma única estatística**, a dependência não linear em 5 min — candidato: o **nível** do volume reage ao tamanho dos choques (retorno grande → mais volume; agressão desequilibrada → menos volume). Tudo isso em dados exploratórios: o modelo local (HXLOC) é candidato a nulo explícito para teste em dado virgem.
2. **H-FR:** eventos estruturais aparecem como mudança de **acoplamento** (Fisher–Rao)? — regras **congeladas** em `PROTOCOLO_SGV_M22_HFR_20261011.md` (ramo M21b) para o 1m out–dez/2026; execução quando os arquivos de dezembro saírem (início de jan/2027).
3. Nulo adequado no **1h**.
4. Memória lenta além do que as coordenadas atuais veem (normalização local corta memória > ~1 dia no 1m).

## 5. Dados: o que já foi usado

| Conjunto | Estado |
|---|---|
| 1m mai–jul/2026 | exploratório — usado à vontade |
| 1h 2020–2024 | exploratório — usado à vontade |
| **1m ago–set/2026** | **gasto** para H-RUP (M19). Não serve mais como dado virgem para hipóteses sobre eventos/alarmes. |
| 1m a partir de out/2026 | **virgem** (arquivo mensal de out/2026 só sai em nov/2026) |
| 1h jan/2025 em diante | **virgem** (sem nulo adequado no 1h ainda) |

## 6. Regras de trabalho daqui em diante

1. **Posto conservador** (M21a) é a regra padrão: referência que falha conta contra o alarme; observado que falha fica inválido.
2. Cada experimento declara **qual pergunta sobre o BTC** responde; experimento puramente sintético precisa dizer por que é necessário para uma pergunta sobre o BTC.
3. **No máximo um ou dois experimentos por dia** e **uma síntese a cada três**.
4. Protocolo e apostas em commit **antes** do código; dados reservados só com protocolo congelado e o OK da Ana; mudanças pós-congelamento só de engenharia, registradas.
5. Nenhum relatório transforma achado descritivo/pós-hoc em conclusão: vira hipótese para dado virgem.
