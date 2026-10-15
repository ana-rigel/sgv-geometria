# Previsão registrada antes de calcular (2ª rodada): a volatilidade é a dimensão escondida? Medida no retorno do preço

**Registrada em:** 15/10/2026. É a **segunda tentativa**: a primeira (`PREDICAO_volatilidade_escondida.md`) deu INCONCLUSIVO pela regra, porque a validação falhou.

O diagnóstico da falha está em `LEITURA_volatilidade_escondida.md`. A medida usava o passo das coordenadas, dominado pela terceira diferença do preço, que tem memória por construção.

**O que já foi visto antes deste registro:**
- **Na 1ª rodada, real, G e S:** a memória do passo das coordenadas.
- **No diagnóstico, só numa réplica G de jun–jul:** a memória de r² bruto (0,43) e de r² ÷ oráculo² (0,004), **sem** condicionar no estado.
- **Nenhuma medida desta 2ª rodada foi calculada no real.**

**Status:** exploração, não confirmatória. Nada de outubro é lido, e nada congelado muda.

## Medida (única mudança em relação à 1ª rodada)

A surpresa passa a ser medida no **retorno do preço** do minuto seguinte, dado o estado 3D e a volatilidade.

- **Surpresa:** ε_{t+1} = r_{t+1}² / (σ̂_t² · m_r(x_t)), em que:
  - r é o retorno log de 1 min do fechamento;
  - x_t é o estado 3D (E_norm, jerk, memory_flux) na régua de caudas;
  - m_r(x) = média tricúbica de (r_{i+1} / σ̂_i)² entre os k = 200 vizinhos de x na semana anterior.
- **Memória que sobra:** M = Spearman(ε_{t+1}, média de ε_{t−9}, …, ε_t), com 5.000 instantes por semana avaliada (semente 20261020), valores agrupados.
- **Linha de base:** σ̂ ≡ 1, só o estado.
- **Iguais à 1ª rodada:** estimativas (`c60`, `ew10`, `ew30`, `har`, `oraculo`), séries (real; G com 5 réplicas; S com 3), semanas e períodos.

## Regras

**Etapa A (só nos G):**
- **Validação:** Red_G(oráculo) = 1 − M(oráculo) / M(σ̂ ≡ 1) ≥ 0,7, na média das réplicas, nos dois períodos. Se falhar: INCONCLUSIVO.
- **Estimativa escolhida:** a causal com maior Red_G, somando os dois períodos.

**Etapa B (real, com a estimativa escolhida):**
- **"Fechado: a volatilidade é a dimensão escondida":** M_real ≤ máximo das 5 réplicas G, nos dois períodos.
- **"Sobra memória além da volatilidade":** M_real > máximo G, nos dois períodos.
- **Senão:** "não estável".

**Descritivo:** M_real com cada estimativa; S.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Validação passa | ~90 % |
| "Fechado" | ~55 % |
| "Sobra além" | ~30 % |

O risco principal está no real. Os retornos reais têm memória de volatilidade em escalas mais longas que qualquer das estimativas, o que é conhecido (memória longa da volatilidade). O G só tem a escala de 61 min.
