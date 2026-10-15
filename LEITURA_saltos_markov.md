# Leitura contra a previsão registrada (PREDICAO_saltos_markov.md, commit 0354e6a)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38814539791).

O código e o workflow foram commitados antes das rodadas (`cc79362`, `2138c93`). A fumaça em maio não imprimiu estatísticas.

## Teste 1 — difusão ou saltos (curtose condicional do passo de E_norm, mediana por região)

| Região | jun–jul real | G (difusão pura) | S (choques reais embaralhados) | ago–set real | G | S |
|---|---|---|---|---|---|---|
| núcleo (< 1) | **2,45** | 1,11 a 1,15 | 2,69 a 2,90 | **2,80** | 1,28 a 1,42 | 3,28 a 3,36 |
| meio (1–3) | **1,73** | 0,86 a 1,04 | 2,31 a 2,68 | **1,53** | 0,89 a 1,02 | 2,73 a 2,83 |
| extremos (3–10) | **0,85** | 0,52 a 0,74 | 1,44 a 1,96 | **1,09** | 0,35 a 0,47 | 1,67 a 2,63 |

**Classificação:** "saltos, reproduzidos pelas caudas dos choques" nas três regiões e nos dois períodos. É **estável**.

**Apostas:**
- saltos nos extremos (~70 %): acertou;
- saltos no núcleo (~45 %): acertou;
- saltos reproduzidos pelas caudas (~60 %): acertou.

**Leitura:**
1. **O campo não é difusão pura em nenhuma região.** A curtose condicional do passo real fica acima de tudo o que a difusão com volatilidade estocástica produz (G), nos dois períodos. Pelo critério de Pawula, a descrição por Fokker–Planck, só com correnteza e tremor contínuo, **não vale exatamente**. O campo certo tem saltos.
2. **Os saltos não são especiais.** O sintético S, que só embaralha os choques reais padronizados, tem saltos iguais ou maiores.
3. **Observação (sem critério registrado).** O real fica **abaixo do mínimo do S** em todas as regiões e nos dois períodos (6 de 6). Os saltos reais são menos "surpreendentes" para o estado do que choques do mesmo tamanho postos ao acaso. Uma explicação compatível: no mercado, os choques grandes acontecem quando a volatilidade já está alta, então o tamanho deles é em parte esperado. Ao embaralhar, choques grandes caem em momentos calmos e viram saltos de verdade. Fica como pista.
4. **Curiosidade.** A curiosa curtose negativa do eixo jerk (−0,5 a −1,6) aparece igual em todas as séries. É da construção da segunda diferença.

## Teste 2 — Markov em 3D ou 4D

| | jun–jul M_3D | jun–jul M_4D | jun–jul Red | ago–set M_3D | ago–set M_4D | ago–set Red |
|---|---|---|---|---|---|---|
| real | +0,221 | +0,138 | 0,37 | +0,334 | +0,239 | 0,29 |
| S (3) | +0,236 a +0,252 | +0,150 a +0,152 | 0,36 a 0,40 | +0,303 a +0,309 | +0,205 a +0,210 | 0,32 |
| G (3) | +0,247 a +0,252 | +0,141 a +0,154 | 0,39 a 0,43 | +0,315 a +0,329 | +0,211 a +0,223 | 0,31 a 0,34 |

**Classificação pela regra:** "não é a volatilidade" (Red < 0,5) nos dois períodos.

**A validação do método falhou.** A previsão exigia que, no G, onde a volatilidade é por construção a variável escondida, a redução chegasse a 0,5 (aposta de ~80 %). Ficou em 0,31 a 0,43. A quarta coordenada usada (o desvio dos 60 min anteriores, causal) captura só parte do caminho de volatilidade verdadeiro. Por isso a classificação "não é a volatilidade" **não deve ser lida ao pé da letra**: o teste não consegue confirmar nem uma dimensão escondida que sabemos existir.

**O que o Teste 2 mostra de forma descritiva, e com clareza:**
1. **A memória que quebra Markov em 3D é igual à de um processo de volatilidade estocástica pura.** O real tem M_3D de +0,22 e +0,33, e o G, que só tem o caminho de volatilidade como variável escondida, tem +0,25 e +0,32.
2. **A quarta coordenada reduz essa memória na mesma proporção no real e no G**: cerca de 30 a 40 %.
3. **Tudo o que o espaço 3D deixa de fora, nesta medida, é compatível com volatilidade.** Para fechar Markov seria preciso uma medida de volatilidade melhor que a janela causal de 60 min, não outra dimensão.

## Para o programa

A linguagem geométrica do SGV fica assim:
- **Espaço:** 3D, com uma dimensão escondida compatível com a volatilidade.
- **Campo:** difusão **com saltos**, e não difusão pura.
- **Saltos:** ligados às caudas dos choques e um pouco menos surpreendentes que choques ao acaso.

Nada disso é próprio do mercado além dos fatos conhecidos: caudas pesadas e volatilidade agrupada.
