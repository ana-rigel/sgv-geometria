# Previsão registrada antes de calcular: no original, sobra geografia depois de descontar raridade **e volume**?

**Registrada em:** 15/10/2026, antes de rodar com o controle de volume.

**Proposta de Ana:** trazer ν, o volume relativo de 1.500 min do espaço de fluxo, como variável de controle no espaço original.

**Status:** exploração, **não** confirmatória. Nada de outubro é lido, e nada congelado muda.

**Esta rodada é menos cega que as anteriores.** Já vimos o original controlado só por raridade (`LEITURA_dimensao_campo.md`):

| | Δ médio | Pares com real acima da nula |
|---|---|---|
| jun–jul | +0,175 | 8 de 8 |
| ago–set | +0,131 | 6 de 8 |

O resíduo médio acompanhava |E_norm|. A fumaça em maio não imprimiu estatísticas.

## Medidas

São as de `explora_dimensao_campo.py`: mesmos 1.500 pontos, mesmas semanas, mesmo estimador e mesmo limiar de massa efetiva. Muda o seguinte:

- **Volume no lugar p:** ν̄_w(p), a média de ν (gaussianizado com a âncora de maio) nos minutos da semana w perto de p. O peso é o mesmo núcleo h = 0,45 do campo.
- **Resíduo:** log tr D(p) menos um polinômio cúbico completo em (ν̄_w(p), log ρ_w(p)).
- **Nula: VAR(1) em 4 dimensões** (E_norm, jerk, memory_flux, ν) por semana, com a volatilidade agrupada no tempo, como antes, em 5 réplicas. A nula carrega o ν com a sua memória e a sua ligação linear com o original.
- **Comparação no mesmo arquivo:** o resíduo só com log ρ, contra esta nova nula.
  - Paridade: os valores do real só com log ρ devem repetir exatamente os da rodada anterior (+0,392 e +0,308).

## Critério (o mesmo da rodada anterior), aplicado ao resíduo com ν̄ e log ρ

| Classificação | Condição |
|---|---|
| **Geografia além de volume e raridade** | Δ médio ≥ 0,10 e real acima da nula em ≥ 7 de 8 pares |
| **Indício fraco** | Δ médio > 0 e ≥ 5 de 8 pares, sem atingir o anterior |
| **Não há** | o resto |

Só conta se repetir nos dois períodos. Senão, "não estável".

## Aposta de Claude, antes dos dados

| Classificação | Probabilidade |
|---|---|
| Geografia além de volume e raridade | ~35% |
| Indício fraco | ~35% |
| Não há | ~30% |

Outras apostas:
- **O volume reduz o Δ do original** em relação ao Δ só com log ρ, nos dois períodos: ~70%.
- **Se sobrar geografia, ela segue ligada a |E_norm|:** ~60%.

## Como roda

- **Jun–jul:** localmente.
- **Ago–set:** `.github/workflows/explora-dimensao-original-nu.yml`, disparado pelo push deste ramo.
