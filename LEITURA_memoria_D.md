# Leitura contra a previsão registrada (PREDICAO_memoria_D.md, commit 1bd4a24)

Exploração, não confirmatória. Jun–jul rodou localmente; ago–set rodou no GitHub Actions (run 38782502140, commit c76acb6).
Paridade: as séries dFD e dFS de jun–jul batem exatamente (diferença 0) com `resultados/forma_D_casca_junjul.json`.

## Fluxo

| | jun–jul | ago–set |
|---|---|---|
| A: ρ(dFD, dFS) real | +0,627 | +0,639 |
| B: ρ(dFD, dFQ) real | **+0,905** | **+0,917** |
| C: ρ(dFD, dFQ) nula, 5 réplicas (teto) | +0,882 | +0,913 |
| **F = (B − A)/(C − A)** | **+1,09** [1,01; 1,20] | **+1,01** [0,96; 1,08] |
| ρ parcial(dFD, dFS \| dFQ) | −0,20 | −0,28 |
| Distância mediana FD–FS, real / nula | 0,102 / 0,029 | 0,084 / 0,031 |
| Distância mediana FD–FQ, real / nula | 0,032 / 0,029 | 0,028 / 0,030 |
| φ mediano real (z, ι, ν) | −0,01; 0,10; **0,50** | 0,01; 0,15; **0,49** |
| φ mediano nula (z, ι, ν) | 0,00; 0,00; 0,02 | −0,01; 0,00; 0,03 |

Os intervalos são IC 90%.

- **Previsão 1 (classificação):** **"Memória linear explica"** nos dois períodos. F ≥ 0,75, com o limite inferior do IC acima de 0,25. A forma de Q, do VAR(1) de 1 minuto, fecha todo o desacoplamento e chega ao teto da nula. Depois de saber como Q mudou, a mudança da casca não acrescenta nada sobre a mudança de D; a parcial chega a ser negativa.
- **Previsão 2 (estabilidade):** repetiu.
- **Previsão 3 (eixo):** **errou.**
  - Previ ν. A correlação do resíduo com |Δφ| ficou assim:

    | | z | ι | ν |
    |---|---|---|---|
    | jun–jul | −0,05 | +0,04 | −0,14 |
    | ago–set | −0,01 | +0,18 | −0,23 |

  - O maior foi ι nos dois períodos, mas só em ago–set ele se afasta de zero.
  - Em nível, a memória está quase toda em ν (φ ≈ 0,5 contra ≈ 0,02 na nula), com um pouco em ι.
  - O que muda mês a mês não é o tamanho da memória de ν.

## Original (descritivo, sem previsão)

| | jun–jul | ago–set |
|---|---|---|
| F | +0,75 [0,58; 0,93] | +1,31 [0,83; 2,46] |
| ρ parcial(dFD, dFS \| dFQ) | +0,00 | +0,09 |

O que a casca acrescentava sobre D no original também desaparece depois de Q, ou quase. No original, a nula também tem φ ≈ 0,94 em E_norm e memory_flux e ≈ −0,65 em jerk. Essa memória vem das fórmulas.

## O que isto implica para o H-FORMA-D-02 (congelado, não muda)

- O desacoplamento do fluxo é, nestes quatro meses, memória linear de 1 minuto, sobretudo do volume relativo ν. A nula de pipeline, que permuta os minutos dentro do dia, destrói essa memória.
- Se a primária do H-FORMA-D-02 confirmar em outubro, a leitura registrada aqui, antes de outubro, é esta: o mercado tem memória linear de 1 minuto (principalmente em ν) que a nula destrói. Não é deriva não linear nem estrutura de campo.
- Uma nula que preservasse a memória linear provavelmente apagaria o efeito.
- O que este teste não vê, como registrado: a heterocedasticidade local de D(x). A média de variâncias condicionais a apaga.
