# Leitura contra a previsão registrada (PREDICAO_jerk_original.md, commit c6a4fbc)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38794638105).

## Resíduo do original (raridade + volume) × |jerk|, por semana

| | jun–jul | ago–set |
|---|---|---|
| Real (média de 9 semanas) | +0,088 | +0,087 |
| Nula VAR(1) 4D, média [faixa das 5 réplicas] | +0,196 [+0,135; +0,247] | +0,221 [+0,161; +0,263] |
| Δ médio / semanas com real acima | **−0,108** / 2 de 9 | **−0,135** / 1 de 9 |
| Classificação | **artefato da medida** | **artefato da medida** |
| Faixa semanal do real | −0,21 a +0,44 | −0,31 a +0,32 |

- **Classificação:** "artefato" nos dois períodos, então a classificação repetiu. A nula reproduz o padrão, e com mais força que o real. A ligação de +0,15 a +0,19 vista antes vem da medida: a dependência radial que a cúbica em log ρ não captura toda ao longo do eixo do jerk.
- **Aposta:** artefato tinha ~55%. Acertou.
- **Observação, sem critério registrado:** o real fica *abaixo* da nula em 7 a 8 de 9 semanas, nos dois períodos. Em |jerk| alto, o mercado real agita menos do que um sistema linear com a mesma memória e volatilidade agitaria.
  - Uma explicação possível: o jerk extremo costuma ser um solavanco de um minuto que se desfaz. Isso é não linear, e pode ser em parte efeito da própria construção da segunda diferença.
  - Não foi previsto. Fica como pista, não como achado.
- **Jerk com sinal (descritivo):** Δ −0,13 em jun–jul e 0,00 em ago–set. Nada estável.

## Para o programa

A última sobra de geografia do original não se sustenta. Nos dois espaços, o tamanho da agitação de lugar para lugar é volume + raridade, e o resto é ruído ou artefato da medida.
