# SGV-M20c — Leitura científica da geometria dos acoplamentos condicionais

**Data:** 11/10/2026. **Ramo:** `research/m20c-acoplamento-condicional`.
**Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38161520572
**Estado:** ENGENHARIA CONCLUÍDA; H20c NÃO CONFIRMADA / POTÊNCIA INSUFICIENTE.
**Protocolo:** `reports/PROTOCOLO_SGV_M20c_20261011.md`, commit
`80de7f9734f485bf3bc837df1857d0ac54eefd07`, registrado antes do código.
**Artefato consolidado:** `SGV-M20c-analise-consolidada` (ID 11710966906).
**Artefatos individuais:** `SGV-M20c-shard-0..4` (todas as 400 trajetórias em JSON)
e `SGV-M20c-piloto-engenharia`.
**Código:** `experiments/m20c_acoplamento_condicional.py`,
`scripts/m20c_agregar.py`, `tests/test_m20c_acoplamento_condicional.py`.
**Testes:** 16/16 pytest aprovados no piloto. Cinco shards concluídos.
A consolidação checou presença, integridade e identidade dos 80 trials por cenário.

## 1. Pergunta e método

Comparamos três estatísticas de acoplamento de pares sucessivos:
- `conditional_sw2`, média de deslocamentos quadráticos de quantis
  condicionais ao tercil das projeções antecedentes, comparados com
  quantis incondicionais (inspirado em W2 fatiado; NÃO é OT exata);
- `rff_hsic`, covariância cruzada quadrática de características
  trigonométricas fixadas, comparador convencional principal;
- `joint_mmd`, diferença entre características conjuntas e
  produto dos embeddings marginais, comparador não linear secundário.

Também testamos covariâncias lineares e quadráticas e deslocamento
marginal. Direções de projeção e recursos Fourier escolhidos globalmente
por sementes fixas, sem acesso à rotação geradora. Sob H+/H- e volatilidade
cada trajetória recebeu uma rotação SO(3) aleatória oculta aos detectores.

A cada trial, uma trajetória geradora forneceu 800 observações de prefixo,
para ajuste de modelo VAR(1) trivariado; a avaliação ocorreu nos 500 pontos
seguintes. O VAR foi ajustado EXCLUSIVAMENTE ao prefixo. Para cada futuro
observado houve 19 futuros simulados com parâmetros fixados no prefixo.
Alarme: score observado estritamente maior que o máximo das referências,
posto extremo de 20 (nível discreto nominal 5% SE nulo fosse conhecido).
Com modelo ajustado ao prefixo o posto não é automaticamente exato:
o desempenho sob N0/NVAR foi medido empiricamente.

Cinco grupos x 80 ensaios independentes (N0,NVAR,H+,H-,VOL).
Sem BTC real, sem holdout e sem qualquer teste de trading.

## 2. Taxas de alarme (contagem / 80)

| Medida | N0 iid | NVAR Gaussiano | H+ | H- | VOL |
|---|---:|---:|---:|---:|---:|
| conditional_sw2 | 2/80 (2,50%) | 7/80 (8,75%) | 1/80 (1,25%) | 1/80 (1,25%) | 2/80 (2,50%) |
| rff_hsic | 5/80 (6,25%) | 4/80 (5,00%) | 3/80 (3,75%) | 2/80 (2,50%) | 23/80 (28,75%) |
| joint_mmd | 3/80 (3,75%) | 5/80 (6,25%) | 6/80 (7,50%) | 3/80 (3,75%) | 5/80 (6,25%) |
| linear_lag | 0/80 (0%) | 7/80 (8,75%) | 2/80 (2,50%) | 1/80 (1,25%) | 2/80 (2,50%) |
| quadratic_lag | 3/80 (3,75%) | 3/80 (3,75%) | 3/80 (3,75%) | 5/80 (6,25%) | 61/80 (76,25%) |
| marginal_shift | 5/80 (6,25%) | 2/80 (2,50%) | 3/80 (3,75%) | 7/80 (8,75%) | 6/80 (7,50%) |

Os artefatos registram por trial: observação, máximo nulo e binários
de alarme, mais contagens e intervalos de Wilson na consolidação.
Os numeradores não justificam estimar diferenças pequenas com precisão
ou assegurar controle universal de erro tipo I.

## 3. Portões FIXADOS antes da execução

- **G0 calibração operacional:** PASSOU. Em N0 e NVAR,
  conditional_sw2 e rff_hsic ficaram abaixo de 12,5% (limite
  permissivo de protocolo).
- **G1 poder mínimo >=35% em cada H+,H- por pelo menos um dos
  dois detectores:** **FALHOU**. Melhor poder observado foi rff_hsic
  3/80 em H+ (3,75%) e 2/80 em H- (2,50%).
- **G2 vantagem geométrica >=10 pontos percentuais EM AMBAS H±
  e McNemar unilateral exato p<0,025 EM AMBAS:** **FALHOU**.
  Em H+: só geometria 1, só HSIC 3; diferença -2,5 pp;
  p=0,9375. Em H-: só geometria 1, só HSIC 2;
  diferença -1,25 pp; p=0,8750.
- **G3 comparadores linear_lag e quadratic_lag <=15% em H±:**
  PASSOU. Detectores convencionais de segunda ordem foram
  essencialmente cegos para H±, como construído.

**Veredito pré-registrado: não demonstramos vantagem geométrica e
não conseguimos detecção confiável de H+/H- com os dois métodos
principais no regime prefix-only, 500 observações e direções ocultas.**

## 4. O que explica o contraste com o M20b?

M20b atingiu 95,5%/96,0% com Fourier-HSIC projetado na coordenada
LATENTE CONHECIDA e 1800 observações por trajetória, calibrado
contra um nulo independente completamente especificado.
M20c adiciona rotação tridimensional desconhecida, reduz a janela
de avaliação para 500, utiliza recursos Fourier aleatórios
em 3D e referencias VAR ajustadas ao prefixo.
Todos os fatores foram modificados SIMULTANEAMENTE. Não é
possível atribuir a perda de poder a um fator sem ablações
separadas pré-registradas. A constatação não refuta a
identificabilidade matemática do acoplamento de transições.

Controle VOL: quadratic_lag 61/80 (76,25%), rff_hsic 23/80
(28,75%), conditional_sw2 2/80 (2,5%). Mostra que métricas
diferentes respondem a famílias diferentes de dependência,
mas NÃO certifica superiority geométrica.

## 5. Conclusão científica e próxima decisão

A passagem de marginais estáticas para transições é necessária
para discernir os pares de processos teóricos. Entretanto,
**nossa implementação condicional simplificada não apresentou
vantagem empírica contra HSIC e ambas falharam em detectar
adequadamente a dependência oculta**, depois que o experimento
se aproximou de condições mais realistas de orientação desconhecida,
amostra finita e nulo ajustado ao passado.

Decisão: congelar estes resultados como negativos. Não aumentar
a posteriori número de direções, custo de OT, tamanho de janela,
força do sinal ou limiar para declarar o mesmo teste positivo.
Uma investigação nova (eventual M20d) deveria usar ablações
fatoriais independentes: (A) direção conhecida/oculta,
(B) 500/1800 observações e (C) nulo conhecido/prefix-fitted,
com comparadores kernel convencionais e eventuais métodos de
transporte condicional exato/regularizado. Pré-registrar
nova hipótese e teste antes de qualquer execução.
Sem confirmação externa, não usar BTC ou alegar aplicação financeira.
