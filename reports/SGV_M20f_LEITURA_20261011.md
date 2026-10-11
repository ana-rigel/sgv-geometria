# SGV-M20f — Leitura científica: invariância SO(3) não implica poder temporal

**Data:** 11/10/2026.
**Ramo:** `research/m20f-kernels-invariantes`.
**Protocolo:** `reports/PROTOCOLO_SGV_M20f_20261011.md` commit
`a401403651e59f88e7f0b2b9e7a15d5842da8e61`, registrado
antes do código e da primeira execução.
**Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38164938906
**Engenharia:** SUCCESS. 13/13 testes, piloto, cinco shards de
64 ensaios e agregação fail-closed concluídos.
**Veredito científico:** G0/G1 PASSARAM; G2/G3/G4/G5/G6 FALHARAM.
**Artefatos:** `SGV-M20f-analise` (ID 11712280019),
`SGV-M20f-shard-0..4`, `SGV-M20f-piloto`.
**Âmbito:** EXCLUSIVAMENTE sintético, sem BTC, holdout ou alterações de main.

## 1. Pergunta e construção
O M20e selecionou uma direção latente entre 32 candidatas no
prefixo, mas não atingiu poder mínimo em H+/H−. O M20f eliminou
a necessidade de eixo latente para as medidas multivariadas
`rbf_hsic_selected`, `rbf_hsic_fixed` e
`distance_covariance`. RBF-HSIC e distância-covariância
dependem apenas das distâncias Euclidianas dos estados e são
invariantes à mesma rotação ortogonal conjunta dos estados.
São métricas/testes ESTATÍSTICOS CONVENCIONAIS, não uma teoria
física de transporte e não demonstram novidade geométrica.

Cinco cenários: N0 ruído iid gaussiano 3D; NVAR estacionário
VAR isotrópico rho=.38; H+ e H− dependência rank-one
não linear oculta, eta=±.43, marginal N(0,I) e autocovariâncias
lineares nulas; VOL memória de volatilidade latente.
64 trajetórias independentes por cenário (total 320).
Prefixo=800, futuro=1800, janelas futuras de 500 e 1800
**extraídas da mesma trajetória**. Modelo temporal de referência:
VAR(1) fitted EXCLUSIVAMENTE aos 800 prefixos, 19 futuros
independentes condicionados ao último estado do prefixo.
Alarme por posto extremo (score observado > máximo de 19 scores
de referência), nível discreto nominal ~5% sob nulo conhecido,
SEM garantia de uniformidade exata sob nulo composto prefix-fitted.

Todos os métodos usam os MESMOS pares ordenados dentro de cada
janela, mas só 192 de 499 pares na janela 500, e 320 de
1799 pares na janela 1800. Índices igualmente espaçados e
predefinidos; nenhum embaralhamento da ordem dos pares.
Métodos comparadores: RFF-HSIC 3D (aproximado, orientação
fixada por características Fourier), HSIC na direção estimada
no prefixo (M20e), busca de 32 direções calibrada na referência
e HSIC na direção verdadeira como teto sintético ORACULAR.
O oráculo utiliza a mesma SUBAMOSTRA de pares que os demais,
não é equivalente ao oráculo do M20e que usou quase todos os pares.

A seleção de banda RBF foi prefix-only:
treino nos primeiros 400 prefixos para mediana sigma0 de distâncias
e validação nos 400 pontos seguintes para selecionar
(.5,1,2)×sigma0 pela maior HSIC bruta.
O valor foi congelado no futuro observado e em 19 referências.

## 2. Resultados n=1800, SOMENTE 320 pares em cada score

| Cenário | RBF selecionado | RBF fixo | dCov | RFF-HSIC 3D | HSIC prefixo 1D | HSIC scan 1D | Oráculo direção |
|---|---:|---:|---:|---:|---:|---:|---:|
| N0 | 2/64 | 0/64 | 0/64 | 0/64 | 2/64 | 3/64 | 1/64 |
| NVAR | 5/64 | 5/64 | 6/64 | 5/64 | 1/64 | 2/64 | 2/64 |
| H+ | **3/64** | 2/64 | 2/64 | 0/64 | 6/64 | 2/64 | 8/64 |
| H− | **3/64** | 2/64 | 2/64 | 6/64 | 6/64 | 2/64 | 12/64 |
| VOL | 21/64 | 1/64 | 1/64 | 16/64 | 57/64 | 47/64 | 64/64 |

Na janela n=500 (192 pares):
- N0: RBF selecionado 1/64, dCov 0/64.
- NVAR: RBF selecionado 1/64, dCov 2/64.
- H+: RBF selecionado 5/64, dCov 2/64, oráculo 6/64.
- H−: RBF selecionado 0/64, dCov 0/64, oráculo 11/64.
- VOL: RBF selecionado 12/64, dCov 4/64,
  HSIC direção prefixada 36/64, oráculo 38/64.

Todos os numeradores, limiares e intervalos Wilson constam
do JSON consolidado e arquivos por trial do GitHub Actions.

## 3. Decisão pelos portões congelados

**G0 INTEGRIDADE + SO(3): PASSOU.** 13 testes,
320 trials completos; `rbf_hsic_selected` e dCov
mantêm escore após transformação SO(3) na verificação
matemática de tolerância 1e-9.

**G1 CALIBRAÇÃO OPERACIONAL: PASSOU.**
Em ambos nulos e ambas janelas, RBF selected/dCov <=8/64.
Maior alarme dentro desse conjunto: dCov sob NVAR n=1800
6/64=9,375%, RBF selected 5/64=7,8125%.
Os limites <=12,5% são permissivos, não prova de nível 5%
ou validade robusta frente a outros nulos.

**G2 PODER RBF >=25% em H+ E H−, n=1800: FALHOU.**
RBF selected 3/64=4,6875% em ambos (vs >=16/64 esperado).

**G3 RBF melhor que RFF-HSIC 3D em >=10pp e McNemar
p<.025, n=1800 em H+ E H−: FALHOU.**
H+: delta +4,6875pp, só RBF 3, só RFF 0,
p unilateral=0,125. H−: delta −4,6875pp,
só RBF 1, só RFF 4, p=0,96875.

**G4 RBF melhor que prefix-direction HSIC 1D em >=10pp
e McNemar p<.025, n=1800 em ambas H±: FALHOU.**
H+: delta −4,6875pp, p=0,9375.
H−: delta −4,6875pp, p=0,96875.

**G5 dCov poder >=25% em ambas H±, n=1800: FALHOU.**
dCov 2/64=3,125% em ambos.

**G6 seleção causal da banda supera banda fixa >=10pp
e McNemar p<.025 em ambas H±, n=1800: FALHOU.**
H+: delta +1,5625pp, p=0,5; H−:
delta +1,5625pp, p=0,5.

## 4. Diagnóstico metodológico que NÃO deve ser escondido

**Os 320 ensaios escolheram a menor banda (.5×sigma0).**
Contagens de seleção, por cenário: N0 [64,0,0];
NVAR [64,0,0]; H+ [64,0,0]; H− [64,0,0];
VOL [64,0,0]. A maximização da HSIC bruta nos
prefixos de validação NÃO demonstrou seleção informativa
de escalas. O seletor parece favorecer sistematicamente
a menor banda no desenho atual. Isso merece investigar
viés de escala do critério, mas NÃO autoriza escolher
banda melhor depois dos resultados.

**Até o ORÁCULO de direção teve poder baixo:**
H+ 8/64=12,5%; H− 12/64=18,75% com n=1800.
É imprescindível notar que aqui o oráculo recebe SOMENTE
320 pares amostrados, enquanto M20e avaliou 1799
pares consecutivos sob n=1800 e obteve oráculo
H+ 57/64, H− 53/64. Esses ensaios diferem ainda
em outras sementes/caminhos e no acesso de score; logo
o contraste é sugestivo, não é uma ablação causal
controlada da densidade de pares. O resultado
impede atribuir toda a perda de poder à dimensionalidade,
invariância ou dificuldade de estimar a direção.

**Desempenho em VOL** favoreceu o detector univariado
que aprende direção no prefixo: 57/64 contra RBF
selected 21/64 e dCov 1/64 na janela longa.
Essa diferença reforça que a qualidade da representação,
o kernel escolhido e o tipo de dependência importam.
Não inferir vitória universal de nenhuma família.

## 5. Conclusão e decisão

M20f cumpriu a tarefa de implementar RBF-HSIC
e distância-covariância **matematicamente invariantes à rotação**
sob condições sintéticas e mostrou calibração operacional
nos dois nulos escolhidos. Mas **NÃO alcançou poder mínimo**
em H+/H−, não venceu baselines convencionais e
não demonstrou benefício da banda causal selecionada.

**RESULTADO CIENTÍFICO PREDOMINANTEMENTE NEGATIVO.**
Invariância geométrica por si só não produz identificabilidade
estatística com amostra finita e nulo estimado. A medida
RBF não oferece evidência de vantagem original e
nem garante detecção de acoplamento temporal oculto.

Próximo passo digno de teste: ablação PRÉ-REGISTRADA
da densidade de pares 320 vs TODOS os 1799,
mantendo as MESMAS 64 trajetórias, nulo e largura
de banda FIXOS; comparar oráculo e detector 3D,
com custos O(n²) explicitamente reconhecidos.
Alternativamente, estimadores lineares em amostra
por random features com projeção isotrópica/integrada
e largura controlada por protocolo novo.
Uma etapa futura deve separar calibração aninhada
prefix-only do limite de memória de pares.
Ainda NÃO abrir BTC ou propor aplicações de mercado.
