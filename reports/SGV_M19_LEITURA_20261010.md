# SGV-M19 — Leitura do teste confirmatório das rupturas estruturais

**Execução:** GitHub Actions run 38081513156 (13 jobs, todos com sucesso), disparada em 10/10/2026 pelo commit `e12654b` com o protocolo congelado em `60c051d` (SHA-256 `a5ac3873…7e1bbc867d`). Meses reservados baixados só depois do portão, com checksum da Binance. 58/58 janelas válidas (01/08 → 30/09/2026). Contagens conferidas por recontagem independente a partir das referências brutas.
**Mudanças de código depois do congelamento:** só engenharia (ordem permissão/arquivo; download de artefatos numa pasta limpa, depois que um ensaio corrompeu JSON). Medição, nulo, alarme, eventos e testes ficaram inalterados; o caminho completo foi validado num ensaio no Actions (run 38081159547) antes do confirmatório.

## 1. Resultado primário (pré-registrado)

| | Janelas de evento | Demais janelas |
|---|---|---|
| Alarme forte (≥2 réguas) | **2 / 15 (13,3%)** | **1 / 43 (2,3%)** |

Diferença de 11 p.p.; **p unilateral por deslocamentos circulares = 0,155** (α = 0,05).

**Decisão pela regra congelada: H-RUP não apoiada** no confirmatório (1m, ago–set/2026). Os meses de agosto–setembro de 2026 do 1m ficam gastos para esta hipótese: sem reteste, sem troca de régua, de limiar ou de lista.

## 2. Secundários (descritivos, como no protocolo)

| Análise | Evento | Demais | p |
|---|---|---|---|
| Fisher exato (alarme forte) | 2/15 | 1/43 | 0,16 |
| Permutação estratificada por volatilidade | — | — | 0,19 |
| Alarme em ≥1 régua | 4/15 (26,7%) | 3/43 (7,0%) | 0,069 |
| Só eventos agendados | 1/7 (14,3%) | 3,9% | 0,31 |
| Só eventos não agendados | 1/9 (11,1%) | 4,1% | 0,41 |
| Por régua — Fisher–Rao (acoplamento) | **4/15 (26,7%)** | **1/43 (2,3%)** | (não testado) |
| Por régua — energy (massa) | 2/15 (13,3%) | 3/43 (7,0%) | (não testado) |
| Por régua — M11 (forma) | 0 | 0 | — (só 23/58 janelas válidas) |

As duas janelas de evento com alarme forte contêm o relatório de emprego de 07/08 e a proposta da SEC "Regulation Crypto Assets" de 18/08.

## 3. Leitura honesta

- **Todos os números apontam na direção da hipótese, mas nenhum atinge o limiar.** A taxa de alarme nas janelas de evento é 3 a 6 vezes a das demais em todas as variantes, mas com só 15 janelas de evento (e 3 alarmes fortes ao todo no período) a evidência é fraca. Pelo próprio cálculo de poder do protocolo, só um efeito muito grande seria detectável. O resultado é **inconclusivo, não uma refutação forte**.
- **O sinal mais nítido veio da régua de acoplamento (Fisher–Rao): 4 de 15 janelas de evento contra 1 de 43.** Isso não foi um teste pré-registrado e não pode ser promovido a achado. Fica como **hipótese específica para o próximo período virgem**: "eventos estruturais aparecem como mudança no acoplamento entre retorno, agressão e volume".
- **Limitação séria: o M11 (forma) só foi válido em 23 das 58 janelas** com o nulo de blocos longos. O mesmo problema já tinha aparecido no M18 (27/84 inválidas). Na prática, o "alarme forte" dependeu quase só de Fisher–Rao + energy. Antes de qualquer nova rodada, é preciso consertar a reconstrução de cascas nesse nulo.
- **Uma tentação que registro para não ceder a ela:** houve um alarme forte na janela de 25/09, logo depois da janela marcada para o roubo na Bitget (lista: divulgação em 24/09; uma das fontes cita execução na madrugada de 25/09). Remarcar o evento agora seria escolher o dado depois de ver o resultado. A lista congelada vale.

## 4. Placar das apostas de Claude

| Aposta | Resultado | |
|---|---|---|
| Alarme forte nas janelas sem evento: 4–10% | 2,3% | ❌ (abaixo) |
| P(H-RUP apoiada) ≈ 25% | não apoiada | ✅ (o desfecho mais provável) |
| Se apoiada, régua mais frequente: energy 45% / M11 35% / FR 20% | (não se aplica) — descritivamente foi Fisher–Rao | ❌ na direção |

## 5. O que fica para o programa

1. Consertar a validade do M11 sob o nulo de blocos longos.
2. Pré-registrar uma hipótese **mais estreita**, nascida aqui: "janelas de evento estrutural têm alarme de acoplamento (Fisher–Rao) acima da taxa de base", a ser julgada **num período ainda virgem**: 1m a partir de outubro de 2026, quando houver dados, ou o 1h 2025–2026 com um nulo adequado.
3. Aumentar o número de janelas de evento: janelas mais curtas ou um período mais longo, para ter poder contra efeitos moderados.
