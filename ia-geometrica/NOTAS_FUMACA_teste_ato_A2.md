# Fumaça do teste do ato A2 (histerese na troca de marca)

20/10/2026 · regra escrita e commitada **antes** de rodar a fumaça · sementes de desenho 5000–5009

**O que muda em relação ao ato A:** só a troca de marca. O órgão guarda a marca atual k e só passa para a melhor k* quando W[k] − W[k*] > δ (custo descontado; uma cheia perdida vale 100). Todo o resto é igual: mundos, marcas, h = 1 ano, L 1 h, C 10, assoreamento no 5º ano, afinada e controle D.

**Candidatos:** δ ∈ {0, 50, 100, 200, 400, 800}.

**Regra de escolha:** o **menor** δ em que, nas sementes de desenho, (a) o órgão fica ≤ 1,05 da afinada nos anos 3–8 do mundo parado em **≥ 9 de 10** mundos e (b) o ganho em B nos anos 6–8 não cai mais de **5 pontos** em relação a δ = 0. Se nenhum δ cumprir as duas, fica o δ com mais mundos em (a) entre os que cumprem (b); se nenhum cumprir (b), o teste não é feito e a leitura da fumaça é registrada.

## Saída da fumaça

(acrescentada depois de rodar)
```
fumaça do teste do ato A2 — sementes de desenho 5000–5009; nenhuma semente do teste
  δ    0: C mundos ≤ 1,05 da afinada 9/10, razão total 0.917, trocas médias 15.9 | ganho B anos 6–8 0.443, ganho C 0.066
  δ   50: C mundos ≤ 1,05 da afinada 9/10, razão total 0.958, trocas médias 5.9 | ganho B anos 6–8 0.442, ganho C 0.032
  δ  100: C mundos ≤ 1,05 da afinada 8/10, razão total 0.948, trocas médias 2.2 | ganho B anos 6–8 0.447, ganho C 0.051
  δ  200: C mundos ≤ 1,05 da afinada 7/10, razão total 0.990, trocas médias 1.4 | ganho B anos 6–8 0.405, ganho C 0.037
  δ  400: C mundos ≤ 1,05 da afinada 10/10, razão total 0.950, trocas médias 0.2 | ganho B anos 6–8 0.354, ganho C 0.068
  δ  800: C mundos ≤ 1,05 da afinada 10/10, razão total 0.954, trocas médias 0.0 | ganho B anos 6–8 0.119, ganho C 0.080
```

**A regra escolhe δ = 0, ou seja, nenhuma histerese, e o A2 viraria o próprio ato A.** O defeito está na regra, não no órgão. Nas 10 sementes de desenho, o órgão sem histerese já ficava ≤ 1,05 da afinada em 9 de 10 mundos, enquanto nas sementes do teste ficou em 67 de 100. Dez mundos não bastam para ver uma falha de ≈ 1 em 3, e a condição (a) passou por acaso no ponto de partida. Além disso, a regra não excluía δ = 0, que é o controle e não um candidato. O que a fumaça mostra mesmo assim: a histerese corta as trocas de marca (15,9 → 5,9 com δ = 50; 0,2 com δ = 400) sem custo para a readaptação até δ ≈ 100. Com δ ≥ 400 a readaptação cai (−9 pontos com 400; −32 com 800).

## Regra corrigida (escrita antes de rodar a segunda fumaça)

- **Sementes de desenho novas e mais numerosas:** 5100–5149 (50 mundos nunca rodados).
- **Candidatos:** δ ∈ {50, 100, 200, 400}; δ = 0 é rodado só como referência.
- **Escolha:** o menor δ em que (a) a fração de mundos com o órgão ≤ 1,05 da afinada nos anos 3–8 do mundo parado é **≥ 0,85** e **maior que a de δ = 0 nas mesmas sementes**, e (b) o ganho em B nos anos 6–8 não cai mais de **5 pontos** em relação a δ = 0. Se nenhum cumprir, fica o que cumpre (b) com a maior fração em (a); se nenhum cumprir (b), o teste não é feito.

## Saída da segunda fumaça (sementes 5100–5149)

```
  δ    0: C fração ≤ 1,05 0.78, razão total 0.946, trocas 15.4 | ganho B 0.246, ganho C 0.049
  δ   50: C fração ≤ 1,05 0.78, razão total 0.955, trocas 5.3 | ganho B 0.239, ganho C 0.049
  δ  100: C fração ≤ 1,05 0.72, razão total 0.968, trocas 2.3 | ganho B 0.236, ganho C 0.032
  δ  200: C fração ≤ 1,05 0.74, razão total 0.975, trocas 1.0 | ganho B 0.210, ganho C 0.037
  δ  400: C fração ≤ 1,05 0.62, razão total 1.006, trocas 0.2 | ganho B 0.162, ganho C -0.019
```

**Nenhum δ cumpre (a).** A histerese corta as trocas de marca (15,4 → 5,3 → 0,2), mas a fração de mundos em que o órgão fica ≤ 1,05 da afinada **não melhora**: fica igual com δ = 50 e piora daí em diante. Pela regra, ficaria o δ = 50, que é o que cumpre (b) com a maior fração em (a). Mas ele não muda nada no que o A2 queria consertar.

**O diagnóstico da leitura do ato A estava errado.** O órgão não perde da afinada em ≈ 1 de cada 4 mundos por trocar demais de marca; com um quarto das trocas, perde nos mesmos mundos. A causa mais provável é outra: com meia-vida h = 1 ano, o órgão escolhe com ≈ 1,4 ano de memória efetiva, menos que os 2 anos com que a afinada foi escolhida. Num mundo parado, ele escolhe com menos dados que ela. A fumaça do ato A escolheu h olhando só a readaptação (B), não o mundo parado (C). O candidato certo para o próximo passo é h, não δ.

**Decisão:** o teste do ato A2 com δ = 50 **não é rodado**. A fumaça já responde a pergunta dele (a histerese não resolve o J3), e rodá-lo nas sementes do teste só gastaria as sementes. Fica registrado como fumaça.
