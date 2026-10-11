# SGV-M20d — Leitura científica da ablação fatorial 2×2×2

**Data:** 11/10/2026.
**Protocolo congelado:** `reports/PROTOCOLO_SGV_M20d_20261011.md`,
commit `1b774ea26138b76b4d5bd94fc7a4da1890b92f70`,
**registrado ANTES do código, do piloto e dos ensaios.**
**Branch:** `research/m20d-ablacao-fatorial`.
**Execução definitiva:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38162216087
**Status de engenharia:** success; 12/12 testes do piloto; cinco shards
64/64 e agregação fail-closed concluídos.
**Status científico:** G0/G2/G3/G4 **PASSARAM**; G1/G5 **FALHARAM**.
**Artefato:** `SGV-M20d-analise` (ID 11710297650) com `analise.json`;
mais cinco `SGV-M20d-shard-*` e `SGV-M20d-piloto`.
**Integridade:** apenas dados sintéticos; não houve BTC, modificação da
main ou reabertura de holdout.

## 1. Objetivo e desenho factual
Separar três diferenças entre M20b e M20c sem variar tudo de uma vez:
- D: projeção na direção latente verdadeira (ORÁCULO) vs projeção fixa e1,
  cega à rotação própria de cada trajetória;
- N: 500 vs 1.800 pontos prospectivos da **mesma** realização;
- R: modelo de referência nulo com parâmetros conhecidos vs VAR(1)
  ajustado EXCLUSIVAMENTE aos 800 pontos anteriores.

Geradores: N0 iid Gaussiano, NVAR isotrópico AR(1) rho=.38,
H+/H- cadeia rank-one oculta M20b (eta=±.43), VOL com memória
de |retorno| preservando autocovariância linear nula.
Cada trajetória rotacionada por matriz ortogonal aleatória e idêntica
nos fatores do mesmo trial. 64 trajetórias independentes por cenário,
cinco cenários, 8 células por trajetória, 19 referências de Monte Carlo
por modalidade de nulo. Mesmos caminhos observados e referências
compatilhadas entre D,N da mesma modalidade R; estatística
prefix-only nas referências ajustadas ao passado.

Métricas primárias: HSIC-1D (Fourier), CQW2-1D (quantis
condicionais, proxy geométrica, NÃO OT exata), LAG-1D linear;
RFF-HSIC-3D cego como controle exploratório independente de D.
A lógica de sucesso e limiares foi congelada antes de executar.

## 2. Reintrodução do sinal H± em condição favorável
HSIC-1D com direção verdadeira, 1.800 pontos, nulo conhecido:
- H+: **61/64 = 95,3125%**;
- H−: **58/64 = 90,6250%**.

Na condição cega, 500 pontos, VAR ajustado:
- H+: **5/64 = 7,8125%**;
- H−: **2/64 = 3,1250%**.

Mantendo o nulo ajustado, ao alterar um fator:
- Direção conhecida e 500 pontos: H+ **18/64 = 28,125%**,
  H− **25/64 = 39,0625%**.
- Direção cega e 1.800 pontos: H+ **5/64 = 7,8125%**,
  H− **4/64 = 6,25%**.

Portanto **há interação D×N**: aumentar a amostra mantendo direção
cega quase não ajuda; conhecer direção mesmo com 500 amostras
ajuda parcialmente. O teste *não* mostra que todos detectores
cegos em 3D necessariamente falham: o detector primário cego
aqui é uma projeção univariada fixa (e1).

## 3. Efeitos médios pareados de cada fator no HSIC-1D

Diferenças em pontos percentuais, média sobre as quatro combinações
dos outros dois fatores, com 95% de percentis bootstrap
re-amostrando **64 trials independentes**, nunca células individuais:

| Fator | H+: efeito [bootstrap95] | H−: efeito [bootstrap95] |
|---|---|---|
| Direção conhecida − cega | **+50,000** [43,359;56,641] | **+54,297** [46,094;62,109] |
| Janela 1800 − 500 | **+34,375** [27,344;41,416] | **+28,516** [21,875;35,156] |
| Nulo conhecido − ajustado | +0,000 [−4,688;+4,297] | +1,172 [−3,125;+5,469] |

Leitura: o fator direção, no par conhecido/cego tal como
definido, foi o maior efeito; aumentar dados foi o segundo;
a modalidade de nulo teve efeito médio pequeno NESSE desenho.
Essas medidas não identificam separadamente todos os termos de
interação, nem provam que as mesmas magnitudes ocorram em BTC.
A diferença entre tipos de nulo pode afetar a calibração mesmo
quando tem efeito baixo no poder.

## 4. Portões pré-registrados

- **G0 — integridade e 320 trials completos:** PASSOU.
  Todas as cinco matrizes 64x8 presentes e verificadas;
  observações idênticas entre modalidade R; testes 12/12.
- **G1 — calibração operacional N0 e NVAR:** **FALHOU**.
  Taxas médias entre oito células: N0 HSIC=2,93%, CQW2=3,52%;
  NVAR HSIC=7,23%, CQW2=8,40%. Maiores células:
  N0 HSIC=4,69%, CQW2=6,25%;
  NVAR HSIC=10,94%, CQW2=**18,75% (12/64)**.
  O máximo da célula NVAR/CQW2 supera 16%, o limite congelado.
  Não rebaixar esse limite retrospectivamente. Isso NÃO significa
  calibração universal em células restantes.
- **G2 — poder >60% oráculo/dados longos:** PASSOU,
  HSIC 95,3%/90,6%.
- **G3 — poder <20% cego/curto/nulo ajustado:** PASSOU,
  HSIC 7,8%/3,1%.
- **G4 — algum fator com efeito >=10 pp em ambas H±:**
  PASSOU (direção e tamanho da janela).
- **G5 — vantagem geométrica CQW2 contra HSIC >=10 pp
  e McNemar exato unilateral p<.025 em H±:** **FALHOU**.
  H+: CQW2 3/64, HSIC 5/64, diferença **−3,125 pp**;
  discordantes: só CQW2=2, só HSIC=4;
  McNemar p=**0,890625**.
  H−: CQW2 2/64, HSIC 2/64, diferença **0 pp**;
  discordantes: só CQW2=2, só HSIC=2;
  McNemar p=**0,6875**.

**Os portões G1 e G5 falharam e continuam reprovados, embora
o workflow GitHub Actions tenha terminado com sucesso.**

## 5. Falhas e reparos de engenharia anteriores ao teste científico

- Primeiro GitHub Actions, `38162128579`, parou ANTES do piloto
  porque uma expectativa do teste unitário de efeito sintético
  dizia 25 pp, mas seu próprio arranjo de células implica 50 pp.
  Foi corrigida a expectativa do teste, sem alterar o cálculo
  nem o protocolo. Commit `d9c96abeb885f620758837ad9f3c385e4b55b83f`.
- Segundo Actions, `38162172451`, obteve 12 testes aprovados,
  mas o script direto falhou em importar o pacote `experiments`;
  foi adicionado o caminho do repositório no ponto de entrada.
  Commit `22df68773c8d52b98645ac7590dfc219e37d46ee`.
- Terceiro Actions `38162216087`: 12 testes, piloto, todos os
  320 ensaios e agregação terminaram. Os dois incidentes não
  produziram resultados científicos usados para alterar parâmetros.

## 6. Conclusão disciplinada e próximo passo

**Diagnóstico sintético bem delimitado:** o contraste principal
M20b→M20c foi fortemente sensível ao conhecimento da direção latente,
e também ao número de observações; alteração de nulo conhecido
para prefix-fitted afetou muito menos o poder *médio* aqui.

**Não encontramos superioridade geométrica**: a CQW2-1D não venceu
o HSIC-1D e teve alarme acima do limite numa célula de NVAR.
Métricas de transição ainda fornecem mais informação que
fotografias marginais, mas este resultado NÃO demonstra novidade
estatística, vantagem financeira ou uma "velocidade" física do BTC.

**Decisão:** congelar M20d como MISTO (diagnóstico fatorial positivo,
calibração e vantagem geométrica negativas). Não explorar BTC agora.
Próximo candidato: testar instrumentos rotation-invariant/adaptativos
de estrutura condicional (sem direção latente oracular), com
ablação de vieses de seleção e calibração prefix-only aninhada.
Exigir desempenho não inferior a baselines HSIC/MMD e calibração
tipo I sob nulos compostos antes de qualquer aplicação a dados reais.
Um eventual ensaio novo requer protocolo próprio, sem promover
resultados exploratórios atuais a evidência confirmatória.
