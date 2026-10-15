# Leitura contra a previsão registrada (PREDICAO_geometria_residual.md, commit d7327a5)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38810333137).

O código e o workflow foram commitados antes das duas rodadas (`2a09079`, `ea7f7eb`). A fumaça em maio não imprimiu estatísticas.

**Sintético:** AR(1) por semana mais o caminho de volatilidade minuto a minuto, com os choques padronizados embaralhados.
- Conferência mecânica: desvio dos retornos sintético/real = 0,995; maio intacto.
- 5 réplicas.

## Resultados

| | jun–jul real | jun–jul sintético (5) | jun–jul nula antiga | ago–set real | ago–set sintético (5) | ago–set nula antiga |
|---|---|---|---|---|---|---|
| **P1** R = D extremos (3–10) ÷ D núcleo (< 1) | **6,83** | 5,70 a 6,85 (média 6,28) | 2,72 | **6,48** | 5,22 a 6,27 (média 5,69) | 2,09 |
| **P2** rotação mediana das cascas a 28 h | **16,2°** | 14,0° a 33,9° (média 23,7°) | 20,5° | **10,9°** | 22,0° a 67,3° (média 33,6°) | 17,4° |
| P2 secundária \|log V50\|/3 | 0,215 | 0,186 a 0,214 | 0,204 | 0,162 | 0,154 a 0,217 | 0,196 |
| **P3** ρ(caudas, Δlog q99,9/mediana \|r\|) | **+0,640** | +0,618 a +0,789 (média +0,687) | +0,522 | **+0,743** | +0,671 a +0,754 (média +0,698) | +0,604 |

| Classificação | jun–jul | ago–set | Pela regra |
|---|---|---|---|
| P1 agitação nos extremos | indício (abaixo do máximo por 0,02) | própria | **não estável** |
| P2 rotação das cascas | indício | própria | **não estável** |
| P2 secundária log V50 | reproduzida | indício | não estável |
| P3 assinatura de caudas | reproduzida | indício | **não estável** |

**Apostas:**
- "Nenhuma própria estável", ~55 %: aconteceu.
- Própria estável em cada propriedade (P1 30 %, P2 20 %, P3 15 %): nenhuma.

## Leitura

1. **A maior parte da geometria é a forma de fatos conhecidos.**
   - Agitação nos extremos: o mercado sintético, que só tem memória linear e o caminho de volatilidade, já faz a agitação crescer ×5,2 a ×6,9 do núcleo aos extremos. O real fica em ×6,5 a ×6,8. O ×10,6 de antes era a faixa 5–10 sozinha; aqui a estatística registrada é a faixa 3–10.
   - A nula antiga, que destruía o agrupamento de volatilidade, dava ×2,1 a ×2,7.
   - Ou seja, cerca de 85–90 % do "extremo agitado" vem dos surtos de volatilidade. O que antes parecia geometria própria era em boa parte agrupamento de volatilidade.
2. **Assinatura de caudas (P3).** É reproduzida: no sintético a casca acompanha as caudas tão bem quanto no real (+0,62 a +0,79). A casca lê caudas que nascem do caminho de volatilidade. Isso confirma a validade do instrumento, e mostra que não há nada de próprio nele.
3. **Sobra um resíduo pequeno e de sinal consistente, que não passou no critério.**
   - **P1:** o real fica acima da média do sintético nos dois períodos (+9 % e +14 %). Em jun–jul fica a 0,02 do máximo; em ago–set fica acima de todos.
   - **P2:** as cascas reais giram menos que a média do sintético nos dois períodos (16° contra 24°; 11° contra 34°). Em ago–set ficam abaixo de todas as réplicas.
   - As réplicas do sintético variam muito em P2 (de 14° a 67°). Com 5 réplicas, a classificação depende de quanto a réplica extrema cai longe.
4. **O que isso significa para a pergunta da Ana.** "O mercado, representado assim, tem uma geometria própria?" Quase tudo da geometria 3D observada (agitação nas bordas, persistência e caudas da casca) aparece igual num mercado que só tem memória linear e surtos de volatilidade. A parte possivelmente própria é pequena: alguns por cento a mais de agitação nos extremos e cascas um pouco mais estáveis na orientação. Pelo critério registrado, ela não se estabeleceu.

## Se for confirmar

- **O que fica de fora:** P3 é reproduzida e não merece confirmação.
- **Candidato:** um teste com P1 e P2 juntos, no espaço original e na régua de caudas, contra o mesmo sintético com **20 réplicas**, porque 5 deixam P2 instável.
- **Dados:** novembro/2026, depois dos julgamentos de outubro, ou outro ativo.
- **Critério:** real acima do percentil 95 das réplicas.
- **Aposta sugerida:** ~25 % para P1 e ~25 % para P2.
