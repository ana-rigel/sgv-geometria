# Previsão registrada antes de calcular: o desacoplamento D × casca no fluxo é memória linear?

**Registrada em:** 15/10/2026, antes de rodar a medida em jun–jul e em ago–set.

**Status:** exploração, **não** confirmatória. Jun–set já foram abertos.
- Nada de outubro é lido. O script recusa dados de outubro.
- Nada do H-FORMA-D-02 congelado muda.

Só um teste de fumaça rodou antes deste registro: 3 dias de maio (o mês da âncora), 17 mapas, para ver se o código roda. No fluxo ele deu B = +0,96 e A = +0,65. Com 17 mapas isso é quase só ruído, mas eu vi e entra na aposta.

## O ponto de partida: o que é identidade e o que é empírico

Pela lei da variância total, a média de Var(x_{t+1} | x_t) é a variância de x_{t+1} menos a variância da parte previsível do passo. Então a forma média de D já é, por construção, a forma da nuvem menos a parte previsível. "Memória explica o desacoplamento" é quase uma identidade.

A pergunta empírica é **que tipo de memória**:
- **Linear de 1 minuto:** um VAR(1), x_{t+1} = c + Φ x_t + e. Se a deriva fosse linear, a forma média de D seria a forma de Q = cov(e). O núcleo h = 0,45 acrescenta um viés pequeno.
- **Não linear:** uma deriva que depende de onde o mercado está, de um jeito que um plano não captura.

**O que este teste NÃO vê:** D(x) que muda de lugar para lugar só em tamanho ou forma da agitação (heterocedasticidade). A média de variâncias condicionais apaga isso. Um F alto não diz que D(x) é homogêneo. Diz só que a forma **média** de D acompanha a memória linear.

## Medidas, em cada mapa de 4 h

Mesmas coordenadas, régua, mapas, D̄ e Σ_mix de `explora_forma_D_casca.py`. As funções são importadas, não copiadas.

- Q e Φ do VAR(1) por MQO nos pares consecutivos da janela de 1.500 min; forma FQ = Q / tr Q.
- Mudanças entre mapas consecutivos: dFD, dFS, dFQ (norma de Frobenius) e |Δφ_jj| (o diagonal de Φ).
- **A** = ρ_S(dFD, dFS) no real, o desacoplamento já conhecido (≈ +0,63).
- **B** = ρ_S(dFD, dFQ) no real.
- **C** = média de 5 réplicas da nula de ρ_S(dFD, dFQ). É o teto: o quanto duas formas "iguais por construção" mudam juntas, dado o ruído de estimação.
- **F = (B − A) / (C − A)**: a fração do desacoplamento que a memória linear fecha. IC 90% por blocos de dia, B = 1.000, semente 20261017.

## Previsões para o fluxo (primária desta exploração)

1. **Classificação por F**, em cada período:
   - **"Memória linear explica":** F ≥ 0,75 e IC 90% de F com limite inferior > 0,25.
   - **"Explica em parte":** 0,25 ≤ F < 0,75; ou F ≥ 0,75 com o IC tocando 0,25.
   - **"Não explica":** F < 0,25. Sobra deriva não linear.
2. **Só conta se repetir nos dois períodos.** Uma classificação diferente em jun–jul e em ago–set é relatada como "não estável".
3. **Eixo:** entre z, ι e ν, o eixo cujo |Δφ| mais se correlaciona com a parte de dFD que dFS não explica. É uma previsão nominal, sem limiar.

O original é **descritivo**, sem previsão. Lá as fórmulas (EMA, segunda diferença) já impõem memória na nula, então C não é um teto limpo.

## Aposta de Claude, antes dos dados

| Classificação no fluxo, nos dois períodos | Probabilidade |
|---|---|
| Memória linear explica | ~60% |
| Em parte | ~30% |
| Não explica | ~10% |

| Eixo | Probabilidade |
|---|---|
| ν | ~40% |
| ι | ~35% |
| z | ~25% |

Rebaixei ν depois da fumaça de maio, onde ele saiu negativo, mas com 17 mapas.

## Como roda

- **Jun–jul:** localmente, `python pipeline/explora_memoria_D.py --periodo junjul`. O mês está no repositório.
- **Ago–set:** `.github/workflows/explora-memoria-D.yml`, disparado pelo push deste ramo. Baixa agosto e setembro com SHA-256 conferido e grava `resultados/memoria_D_agoset.{json,log}` neste ramo.
- **Paridade:** as séries dFD e dFS do real e da réplica 0 em jun–jul serão comparadas com `resultados/forma_D_casca_junjul.json`.
