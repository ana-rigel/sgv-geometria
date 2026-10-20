# Leitura do teste 28 (ato automático) — J1 PASSOU, J2 REPROVADO; a regra mais simples ganhou de todas

**Predição:** PREDICAO_teste28_ato_automatico.md (15d84bc), antes de rodar. **Instrumento:** teste28.py, mesmo commit. **Resultado:** resultados_teste28.json. Dois julgamentos e um mapa relatado; sem emenda.

## Ponto julgado: ato que vale em 1 h e custa 1 (100 sementes)

| | fração do teto | custo médio por semente (2 anos) | cheias perdidas por ano | chamadas por ano |
|---|---|---|---|---|
| nunca | 0 % | 1.867 | 9,3 | 0 |
| N2, córrego comum | 86,6 % | | | |
| **N3, alarme de chuva e nível** | **85,6 %** | 283 | 1,2 | 21 |
| v0 córrego | 82,7 % | | | |
| **v0 dois sensores** | **79,6 %** | 395 | 1,8 | 20 |
| **cada chuva** (sem afinação) | **89,3 %** | 217 | 0,5 | 54 |
| oráculo | 100 % | 18 | 0 | 9 |

**J1, o sítio fica resolvível:** N3 captura 85,6 % do teto e fica abaixo de "nunca" nas 100 sementes. **Passou.**
**J2, a v0 vê o que o alarme comum não vê:** a v0 com dois sensores custa **39 % mais** que N3; mais barata em 34 sementes. **Reprovado.**

Apostas: J1 passa (85 %), certa, e N3 caiu na faixa apostada (80–95 %); "cada chuva" ≥ 70 % (70 %), certa (89 %); J2 reprova (85 %), certa, mas a faixa (−10 a +10 %) errou: perto do teto, uma cheia perdida a mais pesa muito no custo relativo.

## O mapa (30 sementes, fração do teto capturada por N3; entre parênteses, "cada chuva")

| | C = 1 | C = 3 | C = 10 |
|---|---|---|---|
| **L = 1 h** | 85 % (89) | 81 % (79) | 71 % (40) |
| **L = 3 h** | 81 % (70) | 64 % (59) | 30 % (19) |
| **L = 6 h** | 78 % (47) | 55 % (36) | −1 % (−6) |

A célula (6, 10) reproduz os testes 26–27 (−1 %), como apostado. A célula (1, 10) passa de 50 % (71 %), como apostado. A aposta de que a rapidez pesava mais que o preço **errou**: com o ato barato (C = 1), mesmo lento (6 h), o alarme chega a 78 %. Com o ato caro, só a rapidez salva.

O mecanismo do (6, 1) é simples e foi a afinação que achou, não eu: o alarme baixa o limiar de nível para 0,6 m e chama ≈ 90 vezes por ano, isto é, **mantém o sítio protegido a estação chuvosa quase inteira**. Quando proteger custa pouco, não é preciso prever a cheia; basta estar sempre pronto quando o rio está cheio.

## O que o resultado diz

1. **O problema do sítio, neste mundo, é de engenharia, não de mente.** Com o ato automático, a regra mais boba ("a cada chuva, aciona") é a melhor das cinco, sem afinação nenhuma. As regras afinadas perdem um pouco dela por terem sido ajustadas a dois anos só.
2. **O preço do ato pesa tanto quanto a rapidez, ou mais.** Um ato barato permite ficar protegido o tempo todo; um ato rápido permite esperar o sinal. Qualquer dos dois resolve boa parte; os dois juntos resolvem quase tudo.
3. **A v0 não ajudou em nenhum dos três testes do sítio.** Ela empatou com o alarme comum onde o problema era difícil (26–27) e perdeu onde ficou fácil (28). Como alarme, ela não tem o que acrescentar a uma regra de chuva e nível. O que ficou de pé nos testes 16–17, a declaração de cegueira, ainda não foi testado no sítio.

## Para a lista de defeitos de desenho

39. O "teto da chuva" dos testes 27–28 não era teto: ele chama uma vez por chuva, e com ato barato ficar protegido a estação inteira o supera (N3 com 78 % contra 43 % do "teto" na célula (6, 1)). Era um limite de **uma estratégia** (chamar no início da chuva), não do sensor. O nome fica corrigido aqui: "limite de chamar no início da chuva".

Placar: 28 testes numerados (o 25 sem resultado). 26: J1 passou, J2 reprovou; 27: J1 e J2 reprovaram; 28: J1 passou, J2 reprovou. 39 defeitos, 1 emenda.
