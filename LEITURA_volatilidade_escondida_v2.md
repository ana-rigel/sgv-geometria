# Leitura contra a previsão registrada, 2ª rodada (PREDICAO_volatilidade_escondida_v2.md)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38817601660).

O código e o workflow foram commitados antes das rodadas (`c2ac71e`, `c572481`).

## Etapa A — validação: PASSA

| | jun–jul | ago–set |
|---|---|---|
| Red_G(oráculo) | **0,98** | **1,00** |
| Red_G(ew10) | 1,15 | 1,12 |
| Red_G(har) | 0,79 | 0,79 |
| Red_G(ew30) | 0,75 | 0,78 |
| Red_G(c60) | 0,57 | 0,62 |

Medindo no retorno do preço, a volatilidade verdadeira apaga a memória do processo de volatilidade pura. O método enxerga a dimensão escondida conhecida.

**Estimativa escolhida pela regra:** `ew10`. Ela tem Red > 1 porque **corrige demais**: a EWMA rápida inclui os retornos recentes, e a memória vira levemente negativa.

## Etapa B — o real: "SOBRA memória além da volatilidade" nos dois períodos (estável)

| | M_real (ew10) | M_G (ew10), 5 réplicas | Classe |
|---|---|---|---|
| jun–jul | −0,004 | −0,049 a −0,032 | sobra |
| ago–set | +0,062 | −0,041 a −0,032 | sobra |

**Veredito pela regra: SOBRA memória além da volatilidade.**

**Apostas:**
- validação (~90 %): acertou;
- "fechado" (~55 %): errou;
- "sobra" (~30 %): aconteceu.

## Robustez com as outras estimativas (descritivo, não muda o veredito)

| Estimativa | jun–jul: real vs G | ago–set: real vs G | Redução no real (jun–jul / ago–set) |
|---|---|---|---|
| c60 | abaixo do G | acima (sobra) | 0,56 / 0,56 |
| ew10 | acima (sobra) | acima (sobra) | 1,02 / 0,82 |
| ew30 | dentro | acima (sobra) | 0,73 / 0,65 |
| har | abaixo do G | acima (sobra) | 0,84 / 0,71 |

- **Ago–set:** a sobra é robusta, porque todas as estimativas a mostram.
- **Jun–jul:** só a estimativa escolhida a mostra. As outras deixam o real igual ou abaixo do G.

## Leitura

1. **A volatilidade explica a maior parte.** Dada a posição no espaço 3D, a volatilidade remove de 56 % a 100 % da memória da agitação do preço real, conforme a estimativa. Com a melhor, remove 82 % a 100 %.
2. **Mas não fecha sozinha, como um processo de volatilidade de uma escala só.** O real guarda memória a mais, sobretudo em ago–set. O sintético G só tem volatilidade numa escala de ~1 hora (o caminho suavizado em 61 min).
3. **A explicação mais provável para a sobra é volatilidade em escalas mais longas,** que nenhuma das estimativas captura inteira e que o G não tem. É a conhecida memória longa da volatilidade, de horas a dias, e é coerente com o M17, onde uma escala lenta de horas foi o que mais reduziu a lacuna do Markov. **Isso é interpretação, não resultado deste teste.** Ele mostra que sobra memória além de uma volatilidade de escala única, e não diz de onde ela vem.

## Para fechar de vez (se a Ana quiser)

Um terceiro sintético com volatilidade em **várias escalas** (minutos, horas e dias, por exemplo em cascata, tipo HAR), comparado com o real usando a estimativa `har`.
- **Se o real ficar dentro dele:** a dimensão escondida é volatilidade multiescala, e a questão fecha.
- **Se continuar sobrando:** há memória que não é volatilidade.
