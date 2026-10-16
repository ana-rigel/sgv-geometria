# Previsão registrada antes de calcular: quantas escalas de volatilidade o BTC de 1 min pede? (MSM, k = 1…4)

**Registrada em:** 16/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "Teste", depois da explicação do MMAR/MSM.

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já abertos. Nada de outubro. Um julgamento por período.

**Ramo:** `exploracao/msm`, a partir de `exploracao/multifractal@13f0771`.

## A pergunta

O v3 achou duas memórias (10–50 min, 1–3 dias); a multifractal v2 achou que um σ̂ de três janelas absorve toda a estrutura de escala. O MSM pergunta a mesma coisa de frente: ajustando o modelo de Calvet–Fisher com k componentes de volatilidade, cada um com sua frequência de troca, **em que k a verossimilhança para de compensar o custo?**

## Modelo e ajuste

- MSM binomial (Calvet & Fisher 2004): r_t = σ̄ · (Π_{i=1}^{k} M_{i,t})^{1/2} · ε_t, com M_{i,t} ∈ {m₀, 2 − m₀}, trocas independentes com probabilidade γ_i = 1 − (1 − γ_k)^{b^{i−k}}; estados 2^k; filtro de Hamilton.
- **Inovações Student-t** com ν livre, não gaussianas: a v1/v2 mostraram cauda gorda condicional em 1 min; com ε gaussiano, componentes extras serviriam para imitar a cauda e inflariam k. Declarado antes.
- Parâmetros livres: m₀ ∈ (1, 2), b ∈ (1,01, 50), γ_k ∈ (0,001, 0,999), ν ∈ (2,1, 50); σ̄ = desvio-padrão amostral, fixo (perfilado). Nelder–Mead a partir de 2 pontos iniciais (reduzido de 3 após a fumaça, por custo: ~1 h por período); fica o melhor.
- Retornos log de 1 min do período (índices das semanas), sem dessazonalizar (declarado: o ciclo diário pode aparecer como uma componente de ~1 dia).
- **Seleção:** BIC por k; k* = argmin BIC em {1, 2, 3, 4}. Descritivo: ΔBIC entre k consecutivos; as escalas 1/γ_i em minutos; ν.

## Validação do instrumento (antes de ler o real)

Dois sintéticos MSM-t gerados com parâmetros fixados agora: m₀ = 1,4, b = 3, γ_k = 0,5, ν = 4, σ̄ do real, com **k = 2** (semente 8026) e **k = 3** (semente 8027), mesmo comprimento do período. O instrumento é válido no período se k* recuperar o k gerador **nos dois**. Se não, o período é INCONCLUSIVO e a leitura diz por quê.

Descritivo adicional: k* da réplica M_4026 (que tem, por construção, uma escala lenta real suavizada em 61 min e uma rápida AR(1)).

## Classificação (por período; só vale se repetir)

- **"Poucas escalas":** k* ∈ {2, 3}.
- **"Uma escala":** k* = 1.
- **"Muitas escalas (≥ 4)":** k* = 4 (fronteira da grade; não distingue 4 de mais).

## Limitações declaradas

- k ≤ 4 por custo (16 estados; 0,4 s por verossimilhança). k* = 4 é fronteira.
- BIC com 87 mil observações penaliza pouco; tende a favorecer k maior quando há qualquer estrutura não modelada (ciclo diário, saltos). Por isso a validação e a leitura das escalas 1/γ_i importam tanto quanto o k*.
- MSM binomial com um único m₀ para todas as componentes é restritivo; é o modelo padrão da literatura, não o melhor possível.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Validação passa (k = 2 e 3 recuperados) nos dois períodos | ~65 % |
| "Poucas escalas" (k* = 2 ou 3) nos dois períodos | ~55 % |
| k* = 4 em algum período | ~35 % |
| k* = 1 em algum período | ~5 % |
| Alguma escala 1/γ_i entre 10 e 60 min e outra entre 0,5 e 3 dias, no real, dois períodos | ~60 % |
| ν entre 2,5 e 5 | ~70 % |

Os 35 % em k* = 4 vêm da limitação do BIC com amostra grande e do ciclo diário não removido.

## O que confirma e o que não

- **Poucas escalas, validado:** o tempo de negociação θ(t) do BTC de 1 min é uma tempestade de dois ou três andares; concorda com v3 e multifractal v2. Fecha "quantas escalas" nestes dados.
- **≥ 4:** ou há hierarquia mais funda que o v3 viu, ou o BIC está comprando ciclo diário e saltos; a leitura das escalas 1/γ_i decide qual, e o resultado fica como descritivo.
- Em nenhum caso há direção, previsão ou lucro.
