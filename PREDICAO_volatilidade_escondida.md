# Previsão registrada antes de calcular: a volatilidade é a dimensão escondida do espaço 3D?

**Registrada em:** 15/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "Precisamos fechar a questão da volatilidade."

**Status:** exploração, **não** confirmatória. Jun–set já foram abertos. Nada de outubro é lido, e nada congelado muda.

**Ramo:** `exploracao/volatilidade-escondida`, a partir de `exploracao/saltos-markov@9aba56d`.

## Por que outro teste

No teste anterior (`LEITURA_saltos_markov.md`), a validação falhou. No sintético G, a volatilidade é a variável escondida por construção, e mesmo assim a quarta coordenada (o desvio dos 60 min anteriores, como coordenada do vizinho mais próximo) reduziu a memória só em 30 a 40 %. Não deu para saber se a falha era da estimativa de volatilidade ou do jeito de usá-la. Este teste separa as duas coisas, e **valida o método antes de olhar o real**.

## Mudança de método

A volatilidade entra **multiplicando**, e não como uma quarta coordenada do vizinho mais próximo. É assim que um processo de volatilidade estocástica funciona: passo = tamanho do lugar × volatilidade × choque.

- **Passo padronizado:** ŝ_t = s_t / σ̂_{t−1}, com s_t = x_t − x_{t−1} no espaço original na régua de caudas.
- **Agitação do lugar:** m2*(x) = média tricúbica de |ŝ|² entre os k = 200 vizinhos de x na semana anterior.
- **Surpresa:** ε_{t+1} = |s_{t+1}|² / (σ̂_t² · m2*(x_t)).
- **Memória que sobra:** M = Spearman(ε_{t+1}, média de ε_{t−9}, …, ε_t). São 5.000 instantes sorteados por semana avaliada (semente 20261020). Os valores das semanas são agrupados.
- **Sem volatilidade:** σ̂ ≡ 1, que reproduz o M_3D do teste anterior.

## Estimativas de volatilidade

Todas usam o retorno log de 1 min do fechamento. As causais usam só o que é anterior a t.

| Nome | Definição |
|---|---|
| `c60` | desvio dos 60 min anteriores (a do teste anterior) |
| `ew10` | raiz da EWMA de r² com α = 0,1 (~10 min), defasada de 1 |
| `ew30` | raiz da EWMA de r² com α = 0,033 (~30 min), defasada de 1 |
| `har` | raiz da média de três variâncias realizadas anteriores: 10, 60 e 240 min |
| `oraculo` | **só nos sintéticos:** o s_t que gerou a série (caminho de volatilidade verdadeiro, multiplicado pela escala do AR) |

## Séries

- **Real.**
- **G:** 5 réplicas, sementes 3026 a 3030. AR(1) mais o caminho de volatilidade real, com choques gaussianos. A volatilidade é a única variável escondida.
- **S:** 3 réplicas, sementes 2026 a 2028. Igual ao G, mas com os choques reais embaralhados. Entra só como descrição.

## Etapa A — validação, só nos sintéticos G e sem olhar o real

**Redução:** Red(σ̂) = 1 − M(σ̂) / M(σ̂ ≡ 1).

1. **O método funciona?** Red_G(`oraculo`) ≥ 0,7, na média das 5 réplicas, nos dois períodos. Se não, o teste é **INCONCLUSIVO** e para aqui.
2. **Estimativa escolhida:** a causal com maior Red_G médio, somando os dois períodos.

## Etapa B — o real, com a estimativa escolhida na etapa A

- **"Fechado: a volatilidade é a dimensão escondida":** M_real(σ̂) ≤ máximo das 5 réplicas G de M_G(σ̂). Ou seja, a memória que sobra no real não é maior que a de um processo em que a volatilidade é a única variável escondida, medida com a mesma estimativa.
- **"Sobra memória além da volatilidade":** M_real(σ̂) > máximo das réplicas G.
- **Só conta se repetir nos dois períodos.** Senão, "não estável".

**Descritivo:** M_real com cada estimativa, e o mesmo no S.

## Aposta de Claude, antes de tudo

| Aposta | Probabilidade |
|---|---|
| Etapa A: a validação passa (Red_G(oráculo) ≥ 0,7) | ~75 % |
| Etapa A: a estimativa escolhida é `har` | ~45 % |
| Etapa A: a estimativa escolhida é `ew10` | ~30 % |
| Etapa B: "fechado", se a validação passar | ~55 % |
| Etapa B: "sobra além", se a validação passar | ~25 % |

## Como roda

- **Fumaça:** maio, sem imprimir estatísticas.
- **Jun–jul:** localmente.
- **Ago–set:** no GitHub Actions.
