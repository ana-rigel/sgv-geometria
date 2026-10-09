# Reformulação R1 — Julgamento do portão G1′ em dado real

**Data:** 09/10/2026 · **Pré-registro:** `PREREGISTRO_R1.md`, congelado no commit `6dcd828` antes de qualquer cálculo das coordenadas de fluxo em dado real · **Dados:** BTCUSDT spot, períodos de exploração travados em 08/10/2026

**Veredito: o G1′ reprova em 1m e em 1h. Pela regra do plano, a linha geométrica do SGV se encerra.**

Nas duas escalas, o critério que decide é o 3. A média de ΔF no BTC real não se distingue da média de 39 réplicas do nulo SF1 ajustado a cada segmento: p = 0,25 em 1m e p = 0,10 em 1h. O SF1 reproduz só os fatos estilizados conhecidos: volatilidade agrupada, impacto linear, persistência do fluxo e a relação entre volume e volatilidade. Isso fecha o programa iniciado na Fase 1: nem as coordenadas de preço (C1) nem as de fluxo (R1) mostram geometria de curvatura além desses fatos, pelo critério fixado antes de ver os dados.

| Critério | 1m | 1h | Nulo sintético (calibração) |
| --- | --- | --- | --- |
| 1. Mensurável (confiabilidade de ΔF ≥ 0,8; largura escolhida) | 0,96 com 3× ✓ | 0,95 com 3× ✓ | 0,93 com 3× ✓ |
| 2′. Além da posição (ΔF pareado por raio vs. SF1, p ≤ 0,05) | p = 0,025 ✓ | p = 0,10 ✗ | p = 0,05 ✓ |
| 3. **Existe** (média de ΔF vs. SF1, p ≤ 0,05) | **p = 0,25 ✗** | **p = 0,10 ✗** | p = 0,175 ✗ |
| 4. Além da volatilidade (R² ≤ 0,5) | 0,37 ✓ | 0,47 ✓ | 0,507 ✗ |
| **G1′** | **reprova** | **reprova** | reprova |

Arquivos: `reports/r1_real_1m/` e `reports/r1_real_1h/` (`r1_portao.json` e a série barra a barra).

## Como ler o resultado

- **O teste tinha poder.** Na calibração, uma estrutura fora do SF1 (impacto que depende da atividade) deslocou a média de ΔF com z = −25 na versão forte e z = −8,8 na fraca. No BTC real, o deslocamento foi z = +1,2 em 1m e +1,8 em 1h, na direção oposta à das estruturas plantadas e dentro do intervalo do nulo.
- **O critério 2′ passou em 1m, mas não decide sozinho.** Ele também passou no nulo sintético (p = 0,05), e o portão exige os quatro critérios.
- **Dois critérios que eram dúvida passaram.** Ao contrário de C1, ΔF aqui é mensurável e menos ligado à volatilidade (R² de 0,37 e 0,47). O que falta é ΔF ser diferente do que o modelo simples já produz.

## Observações exploratórias (não são resultado)

Entre as estatísticas secundárias, que não decidem nada, duas se separaram do SF1:

- **log det F**, o volume da métrica de informação: z = −7,2 em 1m e −13,4 em 1h, ambos com p = 0,025.
- **Autocorrelação de φ**: z = +4,1 em 1m.

Isso mostra que o SF1 não reproduz toda a distribuição conjunta do fluxo real. Era de esperar de um modelo deliberadamente simples, e é uma diferença de **densidade**, não de **curvatura**. Não foi pré-registrado e envolveu várias comparações. Se algum dia virar hipótese, precisa de pré-registro e de dados que estas rodadas não tocaram, ou seja, o período reservado.

## Ressalvas registradas

- As janelas de D8 e D4/D5 são as declaradas antes da rodada: as últimas 4.500 e 6.000 barras de cada período de exploração (cerca de 3 dias em 1m e cerca de 6 a 8 meses em 1h). D7 usou o período inteiro.
- O código do SF1 é uma reconstrução: o original foi sobrescrito antes de ser commitado. Os 3 testes da especificação passam, e a calibração foi refeita com o código reconstruído antes do congelamento.
- O critério 4 quase não discrimina estruturas fracas (calibração). Aqui ele não pesou: passou nas duas escalas, e quem reprovou foi o critério 3.
