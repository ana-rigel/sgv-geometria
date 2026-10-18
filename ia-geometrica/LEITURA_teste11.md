# Leitura do teste 11 (ritmo por regime) — REPROVADO (V > 0 na média)

**Predição:** PREDICAO_teste11_ritmo.md (db983a2), antes de rodar. **Instrumento:** teste11.py, com um pré-filtro analítico na afinação (só roda os pares cuja fração esperada, com ocupação ½/½, fica a ±6 pp do alvo; a fração que decide é a medida), acrescentado antes de rodar, para caber no tempo. **Resultado:** resultados_teste11.json. Um julgamento; sem emenda.

| | erro de predição médio (medida) |
|---|---|
| teto: olhar sempre | 4,10 |
| nulo: a cada 4 | 5,34 |
| v0: ritmo por regime | 5,30 |

V média **+0,67 %**, envelope −0,8 % a +2,4 %, positiva em 72 de 97 válidas. Par mais frequente (p_q, p_f) = (3, 5); em muitas sementes a afinação escolheu (4, 4), que **é** o periódico (V = 0). Critério: (a) válidas ≥ 95: sim (97); (b) envelope acima de zero: **não**. **Reprovado.** Apostas: 60 % em passar, errada; V entre +2 e +8 %, errada (0,67); V > 0 em ≥ 90, errada (72); ≥ 95 válidas, certa; p_f ≥ 2 p_q, errada (3 e 5).

## O que o resultado diz

É a primeira política que ganha do periódico na média, e ganha pouco: 0,67 %. A forma está certa (o ritmo usa a informação sem concentrar: V deixou de ser negativa pela primeira vez em quatro testes de política), e o tamanho diz onde está o gargalo. Com λ₁ = 0,15 o registro move 15 % do caminho por olhada; entre olhar a cada 3 ou a cada 5 a diferença no erro é pequena, porque em qualquer ritmo a memória fica longe do mundo. A afinação sente isso: em muitas sementes nenhum ritmo desigual bate o (4, 4) por margem que a janela de afinação distinga, e ela devolve o periódico.

A predição nomeou esse cenário: "reprovar com V ≤ 0: o gargalo é o registro lento, não a política". Deu V > 0, pequeno, e a conclusão é a mesma com um atenuante: a política funciona, e o registro que ela serve é lento demais para o ganho aparecer. A herança λ₁ = 0,15 (defeito 1) chegou ao teste de política.

## O que fecha e o que não

- Fecha: o ritmo por regime é a forma certa de política de olhar neste mundo (única com V > 0 na média), e com λ₁ = 0,15 o ganho é < 1 %.
- Não fecha: a mesma política com λ₁ escolhido pelo mundo na calibração (o melhor ganho único, como o nulo do teste 1 teve). Se com um registro que acompanha o mundo o ritmo render mais, o ato da v0 vale e o que o segurava era a herança.

## Para a lista de defeitos de desenho do projeto

23. Política testada sobre um registro cujo λ₁ ninguém perguntou ao mundo: o ganho da política fica abaixo do que o registro deixa passar. Mesma raiz do defeito 1.

Onze testes, onze reprovações, vinte e três defeitos.
