# Leitura contra a previsão registrada (PREDICAO_volatilidade_multiescala.md, commit 5837a8b)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38820737141).

O código e o workflow foram commitados antes das rodadas (`a543fdc`, `2bdbcac`). A calibração foi conferida num processo conhecido (φ 0,90 → 0,91; Var 0,30 → 0,32).

## Veredito pela regra: FECHADO, volatilidade multiescala — robusto

- **Validação:** Red_M(oráculo) = 0,99 (jun–jul) e 0,99 (ago–set). **Passa.**

| Estimativa | jun–jul: real / faixa M | ago–set: real / faixa M | Classe |
|---|---|---|---|
| **ew10 (primária)** | −0,004 / [+0,037; +0,047] | +0,062 / [+0,080; +0,098] | fechado / fechado |
| c60 | +0,097 / [+0,204; +0,220] | +0,154 / [+0,261; +0,285] | fechado / fechado |
| ew30 | +0,059 / [+0,150; +0,166] | +0,121 / [+0,205; +0,229] | fechado / fechado |
| har | +0,035 / [+0,135; +0,150] | +0,101 / [+0,188; +0,213] | fechado / fechado |

As quatro estimativas concordam nos dois períodos, então a classificação é **robusta**.

**Apostas:**

| Aposta | Probabilidade | Resultado |
|---|---|---|
| Validação passa | ~85 % | acertou |
| "Fechado" | ~50 % | acertou |
| Robusto | ~35 % | acertou |
| O M reproduz o "sem volatilidade" do real melhor que o G | ~70 % | **errou** |

No último caso, o real tem 0,218 e 0,349. O G ficou em 0,25 e 0,31; o M, em 0,28 e 0,30. Nenhum dos dois reproduz o nível bruto do real melhor que o outro de forma clara.

## Ressalva: o real fica **entre** dois processos de volatilidade pura

| ew10 | G (só escala lenta) | real | M (lenta + rápida) |
|---|---|---|---|
| jun–jul | −0,049 a −0,032 | −0,004 | +0,037 a +0,047 |
| ago–set | −0,041 a −0,032 | +0,062 | +0,080 a +0,098 |

O mesmo vale nas outras estimativas, com uma diferença em jun–jul: com c60 e har, o real fica um pouco **abaixo** até do G.

O M deixa **mais** memória residual que o real em todas as comparações. Por isso o critério "real ≤ máximo do M" é atendido com folga, e um sintético mais generoso facilitaria a aprovação. A leitura mais forte que os dados sustentam não é "o real é igual ao M". É esta:

> **A memória que sobra no real fica dentro do intervalo entre dois processos em que a volatilidade é a única variável escondida.** Um tem volatilidade só em escalas de hora a dias (G); o outro também em minutos (M). Não é preciso nenhuma memória que não seja volatilidade para explicar o que se mede no real.

A calibração da escala rápida (φ_h de 0,83 a 0,98; Var h de 0,04 a 0,57) varia muito de semana para semana. A volatilidade rápida do BTC muda de intensidade ao longo do tempo.

## Fechamento da questão

1. **A dimensão escondida do espaço 3D é volatilidade em várias escalas.** Com a medida limpa (surpresa do retorno do preço, dado o estado 3D), o real fica entre dois processos de volatilidade pura, com quatro estimativas e nos dois períodos.
2. **A "sobra" da 2ª rodada era a escala rápida da volatilidade (minutos),** que o G não tinha. Não era memória de outra natureza, nem escalas lentas, como eu tinha suposto antes de corrigir.
3. **Limites:**
   - É exploração em períodos já abertos.
   - A medida é a memória da agitação do preço; não se testa outro tipo de memória, como a de direção.
   - A conclusão é "compatível com volatilidade multiescala", não "provado que só existe volatilidade". Um processo com outra memória que deixasse resíduo dentro desse intervalo não seria distinguido por este teste.
