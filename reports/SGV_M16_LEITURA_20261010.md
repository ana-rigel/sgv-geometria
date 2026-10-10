# SGV-M16 — Leitura dos resultados contra o pré-registro

**Execução:** GitHub Actions run 38017854001 (29 jobs, todos com sucesso; piloto confirmou 84 origens no 1m e 18 no 1h). Somente dados exploratórios; nenhum mês reservado aberto. Tabelas: `reports/m16/SGV_M16_RESULTADOS.md`; dados brutos de cada origem: `reports/m16/shards/`.
**Lembrete:** origens consecutivas não são independentes; tudo aqui é auditoria exploratória, não teste confirmatório.

## 1. Classificações pré-registradas

| | N0 blocos curtos | N1 GARCH-t + SF1 | N2 regime, blocos curtos | N3 regime, blocos longos |
|---|---|---|---|---|
| **1m** | **falta memória/massa** (energy 72,6% vs M11 29,3%) | inadequado, tipo indefinido | **falta memória/massa** (energy 46,4% vs M11 18,5%) | inadequado, tipo indefinido (energy 23,8% vs M11 10,3%, p=0,026, abaixo do limiar) |
| **1h** | indefinido (energy 55,6%) | indefinido | indefinido (energy 55,6%) | indefinido (energy 38,9%) |

Nenhum nulo passou como "sem evidência de inadequação" em nenhuma escala.

## 2. O que isso diz sobre o funcionamento do BTC (nestes dados exploratórios)

1. **O mecanismo que mais falta aos nulos é memória — massa que migra e fica.** No 1m a energy distance cai de forma ordenada à medida que o nulo ganha memória: N0 72,6% → N2 46,4% → N3 23,8%. É a mesma "curva de dose" que o M15 mostrou com blocos sintéticos (15 → 60 → 150). Mesmo os blocos longos do N3 ainda não bastam: a persistência real dos estados do BTC no 1m é mais longa (ou mais estruturada) do que o catálogo de 2 estados com blocos de 60 minutos.
2. **A forma é o aspecto mais bem reproduzido.** O M11 é a régua com a **menor** taxa em 7 das 8 células; com o N3 no 1m (10,3%) e com todos os nulos no 1h (6–18%) fica perto do nível de ~7% de uma família correta. Ou seja: depois de dar memória ao nulo, a deformação de *forma* das cascas do BTC é em grande parte explicada pelos mecanismos conhecidos.
3. **O N1 (paramétrico) falha de um jeito diferente: na covariância.** Fisher–Rao 53,6% contra M11 36,6% e energy 34,5%. Essa assinatura ("falta acoplamento") não existia no mapa sintético do M15: o GARCH-t + SF1 não reproduz como o acoplamento entre retorno, agressão e volume muda de uma metade da janela para a outra. É candidato a mecanismo ausente no SF1 (correlação variável no tempo entre z, ι e ν) — descritivo, não classificado pelo protocolo.
4. **No 1h a direção é a mesma do 1m** (energy > M11 em todos os nulos, p 0,02–0,06), mas 18 origens não atingem o limiar corrigido.

## 3. Observação exploratória (não testada, declarada como tal no protocolo)

No 1h, o M11 alarmou em só 3 das 18 origens — e as três janelas contêm episódios estruturais conhecidos:
- origem 0 (30/03 → 11/05/2022): início do colapso Terra/LUNA;
- origem 5 (26/10 → 07/12/2022): colapso da FTX;
- origem 10 (20/12/2023 → 31/01/2024): aprovação dos ETFs de BTC à vista nos EUA — única origem em que **todos os nulos alarmam nas três réguas**.

Isso sugere que **alarmes de forma, depois que os nulos já têm memória, podem marcar rupturas estruturais**. Mas foi visto *depois* dos dados, com 18 origens e sem controle de multiplicidade: é hipótese para um pré-registro futuro, não achado. (Os eventos de mar/2020 e mai/2021 não entraram: as lacunas do 1h em 2020–2021 impediram origens contíguas de 3500+1008 horas.)

## 4. Placar das apostas de Claude

| Aposta | Resultado | |
|---|---|---|
| 1m: todo nulo com ≥1 régua > 20% (75%) | sim (o menor máximo é 23,8%, N3/energy) | ✅ |
| N0 no 1m = "falta memória/massa" (45%) | sim | ✅ |
| N1 no 1m = "falta forma" (45%) | não — indefinido, com covariância no topo | ❌ |
| N3 com a menor taxa energy no 1m (50%) | sim (23,8%) | ✅ |
| Algum nulo "sem evidência" no 1m (15%) | não | ✅ (não ocorreu) |
| Alguma classificação de tipo no 1h (30%) | não | ✅ (não ocorreu) |
| fr_cov a menor régua na maioria das células (70%) | não — fr_cov nunca foi a menor; o M11 foi a menor em 7/8 | ❌ |

## 5. Próximos passos sugeridos

- **Nulo com memória longa de verdade:** HMM ajustado com mais estados e/ou durações semi-Markov (tempos de permanência não geométricos) no lugar dos blocos — é o mecanismo que o M16 aponta como faltante.
- **SF1 com acoplamento variável** (correlação dinâmica entre z, ι, ν) para atacar a assinatura de covariância do N1.
- **Pré-registrar a hipótese "alarmes de forma marcam rupturas estruturais"** com lista de eventos fixada antes, para julgar no período confirmatório do 1h (≥ jan/2025) — sem abri-lo antes do congelamento.
