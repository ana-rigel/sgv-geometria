# Leitura contra a previsão registrada (PREDICAO_dimensao_original_nu.md, commit b5f4db0)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38791831641).
- **Paridade:** o real só com log ρ repete exatamente a rodada anterior (+0,392 e +0,308).

## Original

| | jun–jul | ago–set |
|---|---|---|
| **Com raridade e volume:** persistência do resíduo, real / nula | +0,278 / +0,186 | +0,163 / +0,172 |
| Δ médio / pares com real acima | **+0,092** / 6 de 8 | **−0,009** / 5 de 8 |
| Classificação | indício fraco | não há |
| R²: real / nula | 0,87 / 0,77 | 0,92 / 0,87 |
| **Só raridade** (comparação, mesma nula de 4 dimensões): Δ médio / pares | +0,175 / 8 de 8 | +0,128 / 6 de 8 |
| Resíduo médio × \|E_norm\|: só raridade → com volume | +0,38 → +0,01 | +0,46 → +0,03 |

- **Classificação:** muda de período para período. Pela regra registrada, **"não estável"**.
- **Aposta "o volume reduz o Δ":** acertou nos dois períodos.
  - Jun–jul: de +0,175 para +0,092.
  - Ago–set: de +0,128 para −0,009.
- **Aposta "se sobrar geografia, ela segue em |E_norm|":** errou. A ligação com |E_norm| some quando o volume entra. Era volume.
  - O pouco que sobra se correlaciona fracamente com |jerk| (+0,15 e +0,19).
  - Não conferi isso na nula. A rodada anterior mostrou que esse tipo de padrão pode vir da própria medida.

## Para o programa

Nos dois espaços, depois de descontar volume e raridade, nenhuma geografia de agitação se repete de semana a semana de forma estável além de uma nula com memória linear e volatilidade agrupada.

O "campo de tamanho" observado em jun–set é, essencialmente, volume + raridade.
