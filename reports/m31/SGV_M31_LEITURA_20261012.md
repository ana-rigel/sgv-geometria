# SGV-M31 — Leitura: a forma não acrescenta informação de risco a um baseline forte

**Execução:** GitHub Actions run 38339336194 (resultados em `56cfb47`). Protocolo `reports/PROTOCOLO_SGV_M31_20261012.md` (SHA-256 `eb82e7bb…2a85`) e módulo de engenharia (`f8a27723…2476`) conferidos pelo código antes de baixar os dados. **ETHUSDT 1m 2026-05..09**, um único trecho contínuo (220.320 min, sem lacunas); 14.490 origens, **11.711 avaliadas** (jun–set). Casca válida em 100% das janelas.

## Resultado
| Teste | Comparação | skill | p (HAC, 1 dia) | p (bootstrap) | critério | resultado |
|---|---|---|---|---|---|---|
| **T1** | B1 vs B0 | **−0,07%** | 0,65 | 0,64 | p < 0,05 e skill ≥ 1% | **FALHA** |
| T2 | B1+ vs B0+ | — | — | — | — | não testado (hierarquia) |
| T3 | B2 vs B1+ | — | — | — | — | não testado (hierarquia) |

Descritivos: skill de B1 vs B0 por mês −0,06%, −0,38%, +0,17%, −0,09% (jun a set); B0+ vs B0 +0,03% (a elasticidade móvel também não acrescenta nada).

**Leitura pré-registrada: a forma não acrescenta informação de risco relevante ao baseline forte.** Com o poder medido antes (efeito mínimo detectável ≈ 0,45% de skill a 80%), o resultado é **informativo**: se existe algum ganho, ele é menor que ~0,5%, metade do limiar de relevância. O intervalo do efeito exclui ganhos de 1%: o EP do delta é 0,00064 sobre uma deviança média de 0,381, ou seja, ±0,33% de skill em 2 EP em torno de −0,07%.

## O que isso diz
- O cone, a cintura e a elasticidade volatilidade–volume são estados reais e persistentes da forma (vistos no BTC), mas, **para prever o risco dos próximos 15 min**, a informação deles já está no que um HAR-X sazonal forte usa: volatilidade passada em várias escalas, amplitude, quarticidade, volume, relógio. A geometria descreve o funcionamento; ela não traz informação de risco que a econometria padrão não tenha.
- Como T1 falhou, as perguntas de atribuição (T2) e de geometria intrínseca (T3) não chegam a ser feitas, por desenho. Elas só fariam sentido se houvesse algo a atribuir.

## Apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| T1 passa (12%) | não | ✅ (não ocorreu) |
| T1 e T2 (6%) / T1, T2 e T3 (2%) | não testados | ✅ |
| B0+ melhora o B0 em ≥ 0,5% (30%, descritivo) | não (+0,03%) | ✅ (não ocorreu) |

## Errata e ressalvas (após auditoria independente, 12/10/2026)
Auditoria publicada no issue #3. Aceito os três pontos; nenhum muda o julgamento de T1.

1. **Escopo da conclusão (correção minha).** A frase "a geometria … não traz informação de risco que a econometria padrão não tenha" é **ampla demais**. O T1 testou **cone, cintura e cone × ν**, que são **estatísticas condicionais de uma cópula local**, não a curvatura da casca. A variável nativa da casca (área em sela da HDR50) estava no T3, que **não foi avaliado** por causa da hierarquia. Conclusão correta: *as variáveis de forma especificadas no T1 não acrescentam ganho relevante (≥ 1%) à previsão do risco de 15 min no ETH 1m jun–set/2026, contra este baseline.* A curvatura da casca segue **sem teste confirmatório**.
2. **Seleção das origens pelo alvo.** `segment_rows` só inclui uma origem se o RV dos 15 min seguintes for finito e positivo. As variáveis e as previsões continuam causais, mas a *elegibilidade* depende do futuro, o que não serve para uso ao vivo. No ETH, o efeito é nulo na prática (11.711 de 11.712 origens programadas; a que faltou não tinha horizonte completo). Para experimentos futuros: separar "origem elegível para prever" de "alvo disponível para avaliar". O módulo congelado **não** é alterado, para que o M31 continue reproduzível com o portão de SHA.
3. **Poder.** O efeito mínimo detectável de ~0,45% veio do erro-padrão sob placebos e de aproximação normal, não de simulação com ganho plantado; "≈ 100% de poder para 1%" é aproximação não validada. O negativo se apoia no **intervalo observado**, não no poder.
4. **Dependência.** HAC e bootstrap usaram a mesma escala (1 dia). Sensibilidade **pós-hoc e só descritiva**, a partir das previsões já publicadas (`m31_confirmatorio_previsoes.csv.gz`), sem mudar o julgamento:

| Inferência | IC 95% do skill de B1 vs B0 |
|---|---|
| HAC 1 dia (pré-registrado) | −0,39% a +0,26% |
| HAC 2 dias | −0,37% a +0,24% |
| HAC 1 semana | −0,40% a +0,27% |
| bootstrap em blocos de 1 dia | −0,36% a +0,31% |
| bootstrap em blocos de 1 semana | −0,37% a +0,31% |

Em todas as variantes o ganho de 1% fica de fora. Para pesquisas futuras: pré-definir sensibilidades de 2 dias e 1 semana.

**Recomendação mantida:** não reabrir ETH jun–set para novos indicadores.
