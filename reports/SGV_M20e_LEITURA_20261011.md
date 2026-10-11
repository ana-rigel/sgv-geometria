# SGV-M20e — Leitura científica: aprendizagem causal da direção

**Data:** 11/10/2026.
**Ramo:** `research/m20e-direcao-adaptativa`.
**Protocolo pré-execução:** `reports/PROTOCOLO_SGV_M20e_20261011.md`;
commit `4827ed2d689d706ecfd26d1c0551f61ce4d582c3`,
registrado antes do código e do Action de teste.
**Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38163281173
**Status de engenharia:** concluída com sucesso, 13/13 testes
automáticos, piloto isolado, cinco cenários x 64 trials e agregação
fail-closed concluída.
**Resultado científico:** **G0/G1/G5 passaram; G2/G3/G4/G6 falharam.**
**Artefatos:** `SGV-M20e-analise` ID 11711246279 e
`SGV-M20e-shard-0..4`, mais `SGV-M20e-piloto`.
**Integridade:** dados EXCLUSIVAMENTE sintéticos. Nenhuma
modificação da main e nenhum acesso a BTC ou holdout M19.

## 1. O que o instrumento de fato faz

O M20e tenta identificar uma direção de dependência temporal a partir
de um prefixo HISTÓRICO de 800 observações de uma trajetória 3D,
cuja direção latente verdadeira foi rotacionada ao acaso por trial.
Escolhe `d_hat` dentre 32 direções candidatas fixas maximizando
Fourier-HSIC calculado exclusivamente sobre os pares históricos.
Depois calcula sobre o futuro a estatística Fourier-HSIC na
direção selecionada, comparando-a à mesma estatística em 19
futuros de referência VAR(1), cujos parâmetros foram ajustados
somente no prefixo observado. A direção é congelada nas
referências; nenhum dado prospectivo entra no ajuste ou seleção.

Há comparadores: e1 fixa, varredura in-window de 32 direções
calibrada com varreduras equivalentes nas 19 referências,
HSIC 3D de projeções aleatórias, medida de quantis
condicionais (CQW2) na direção adaptativa e HSIC na
direção verdadeira APENAS COMO TETO (ORÁCULO).

5 cenários: N0 iid, NVAR gaussiano rho=.38,
cadeias H+/H− rank-one eta=±.43 com marginais
gaussianas e autocovariâncias nulas em TODOS os
lags, e memória de volatilidade VOL. 64 trials por
cenário, 800 prefixo +1800 futuro; janelas aninhadas
500/1800; 19 referências por trial e parâmetros VAR
ajustados no prefixo.

## 2. Recuperação da direção causal a partir do prefixo

Condição de sucesso |cos(d_hat,d_true)|>=0.80
(mede alinhamento sem distinguir sinal):
- H+: **33/64 = 51,56%**, Wilson95 [39,58%;63,37%],
  média |cos|=0,708808.
- H−: **41/64 = 64,06%**, Wilson95 [51,82%;74,71%],
  média |cos|=0,762572.
- VOL: **64/64 = 100%**, média |cos|=0,974963.
- N0: 16/64; NVAR: 10/64. Em N0/NVAR a direção "verdadeira"
  da construção não é informativa; essas proporções
  não são taxa de identificação real de dependência.

O critério G2 requer >=60% em AMBOS H±; **FALHOU**
porque H+ ficou abaixo, mesmo que H− tenha passado isoladamente.

## 3. Alarmes por instrumento e janela (contagens / 64)

| Cenário | N | HSIC adaptativo | HSIC fixo e1 | scan HSIC | HSIC 3D | CQW2 adaptativa | HSIC oráculo |
|---|---:|---:|---:|---:|---:|---:|---:|
| N0 | 500 | 1 | 0 | 4 | 2 | 1 | 3 |
| N0 | 1800 | 4 | 1 | 1 | 2 | 0 | 3 |
| NVAR | 500 | 0 | 5 | 1 | 7 | 0 | 5 |
| NVAR | 1800 | 1 | 6 | 2 | 4 | 5 | 6 |
| H+ | 500 | **8** | 5 | 1 | 2 | 1 | 14 |
| H+ | 1800 | **17** | 7 | 17 | 1 | 2 | 57 |
| H− | 500 | **7** | 7 | 7 | 1 | 2 | 21 |
| H− | 1800 | **25** | 6 | 26 | 2 | 2 | 53 |
| VOL | 500 | **59** | 12 | 49 | 22 | 36 | 63 |
| VOL | 1800 | **64** | 21 | 64 | 37 | 62 | 64 |

Obs.: somar alarmes de N=500 e N=1800 como se fossem amostras
independentes seria incorreto; são janelas aninhadas do mesmo trial.
Os arquivos JSON do Actions guardam limiares, contagens, intervalos
Wilson e decisões binárias por trial.

**H+ / H− e N=500:** HSIC adaptativo 8/64=12,5%
e 7/64=10,9375%, muito abaixo do G3 mínimo de 35%.
**VOL e N=500:** HSIC adaptativo 59/64=92,1875%,
o que indica que a recuperação direcional pode funcionar
em outro tipo de dependência latente mais forte.

**H± e N=1800:** o adaptativo recupera parte
do poder (26,6%/39,1%) mas fica bem abaixo do
oráculo (89,1%/82,8%). O prefixo de seleção,
projeções discretizadas e estatística HSIC
não reproduziram o teto de informação latente.

## 4. Portões congelados, sem reinterpretação

- **G0 integridade e testes:** PASSOU (13/13 testes e 320 trials).
- **G1 calibração nos dois nulos (N0,NVAR) para adaptativo e scan
  em N=500/1800, cada célula <=12,5%:** PASSOU.
  Máximos respectivos: adaptativo 4/64 N0 ou 1/64 NVAR,
  scan 4/64 N0 ou 2/64 NVAR. Este limite é
  *operacional e permissivo*, não uma demonstração de
  nível exato sob todo nulo composto.
- **G2 direção |cos|>=.8 em >=60% H+ E H−:** FALHOU
  (51,56% / 64,06%).
- **G3 poder adaptativo N=500 >=35% H+ E H−:** FALHOU
  (12,50% / 10,94%).
- **G4 adaptativo vence direção fixa >=10 pp, McNemar
  p<.025 em H+ E H−, N=500:** FALHOU.
  H+: delta +4,6875 pp, discordantes 7 só adaptativo
  contra 4 só fixo, p=**0,27441406**.
  H−: delta 0 pp, discordantes 5 vs 5,
  p=**0,62304688**.
- **G5 adaptativo não fica >10 pp abaixo do scan em ambos
  H±, N=500:** PASSOU. H+ adaptativo excede o scan
  em 10,9375 pp; H− empata. Isso NÃO significa
  vantagem generalizável, pois ambos têm baixo poder.
- **G6 CQW2 vence adaptativo >=10 pp + McNemar p<.025
  em ambos H±, N=500:** FALHOU.
  H+: CQW2 1/64 vs adaptativo 8/64; delta
  **-10,9375 pp**, p=0,99804688.
  H−: CQW2 2/64 vs adaptativo 7/64; delta
  **-7,8125 pp**, p=0,98046875.

## 5. Leitura teórica

O instrumento estimou do passado uma direção latente relativamente
bem para memória de volatilidade, e recuperou parcialmente a
direção H±. Mas a amostra prefixada de 800 pontos e a busca
sobre apenas 32 candidatos não atingiram G2/G3 para processos
rank-one com dependências além da segunda ordem. Isso NÃO
prova impossibilidade de estimar a direção: é uma limitação
da técnica e condições congeladas deste experimento.

O CQW2 adaptativo ficou substancialmente abaixo de HSIC,
sem evidência de vantagem geométrica no M20e.
O método de escolha é ele próprio Fourier-HSIC,
estatística convencional; logo não há descoberta de
uma "força" temporal ou de métrica intrínseca única
do espaço de distribuições. A verdade de d e o oráculo
existem apenas em sintéticos; não são acessíveis
em aplicações cegas. O posto Monte Carlo usando nulo
ajustado ao prefixo ainda requer calibração aninhada
e cenários de controle heterogêneos.

A grande diferença de comportamento entre H± e VOL
indica **dependência de família e de mecanismo**, e
não existência de um detector universal de "tensão".

## 6. Conclusão e decisão

M20e **encerrado com resultado predominantemente negativo**
para sua hipótese primária H±: G2/G3/G4/G6 falharam.
Não alterar amostra, direção, projeções ou limiar após
ver os resultados. Arquivar a recuperação de VOL como
CONTROLE POSITIVO, não sucesso confirmatório H±.

Próxima investigação, se desejada: separar seleção
da direção em *prefixos independentes* de treino e
validação, investigar detectores invariantes a
rotação por kernels radiais multivariados e
acoplamentos condicionais em dimensão completa,
com escalas de kernel e nulos ajustados/ressimulados
sem escolher melhor instrumento ex post.
Registrar novo protocolo, focar calibração sob nulos
compostos e não abrir dados reais ou holdout BTC.
