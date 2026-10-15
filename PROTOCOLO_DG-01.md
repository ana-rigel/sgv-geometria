# Protocolo DG-01: o +0,64 do BTC sobrevive à troca de régua?

**Registrado em 15/10/2026, antes do código e de qualquer resultado.** Decisão de Ana: "diagnóstico no BTC" (antes de qualquer confirmatório com a régua atual). Exploratório: usa só BTCUSDT 1m mai–jul/2026, já explorado. Nenhum período ou ativo reservado é tocado.

## Pergunta

A ligação entre a feature de caudas das cascas e a cauda real dos retornos no BTC (ρ = +0,638 em 291 pares; +0,656 em 20 pares disjuntos) é do mercado, ou é produto da régua atual (GMM2 + grade do vendor), que o RB-01 mostrou ter viés de caudas sob caudas pesadas?

## Desenho

- **Dados e coordenadas:** os do `pipeline/confirmatorio_casca.py`, sem mudança: BTCUSDT 1m mai–jul/2026 (SHA-256 conferido), espaço original (E_norm, jerk, memory_flux), régua `orig_raw` com âncora de maio, janelas de 1.500 min.
- **Pares:** os dois desenhos já usados. (i) Relatório: um mapa a cada 240 min, pares a 28 h (7 mapas). (ii) Disjunto: janelas a cada 28 h, pares (2m, 2m+1).
- **Feature:** f = (Δlog V95 − Δlog V50)/3. **Referência:** Δlog(q99,9/mediana de |r|).
- **Construções comparadas** (as mesmas do RB-01):
  - **A0, atual:** volumes das malhas do vendor. Precisa reproduzir +0,638 e +0,656 (paridade).
  - **B:** GMM2 + limiar de Hyndman, sem malha.
  - **C:** GMM3 + Hyndman.
  - **D:** mistura de 2 t + Hyndman.
  - **E:** KDE + Hyndman.
- **Nula de pipeline:** a do H-CASCA-01 (retornos, sombras e volume permutados dentro de cada dia a partir de junho, semente 2026), com as cinco construções.

## Medidas

Para cada construção e desenho: ρ de Spearman entre f e a referência, no real e na nula; número de mapas válidos; ρ entre o f de cada construção e o f da A0.

## Leitura combinada antes dos dados

Usando as construções C, D e E (as que o RB-01 mostrou sem viés de caudas espúrias):

| Resultado no desenho do relatório | Leitura |
|---|---|
| ρ de C, D e E todos ≥ 0,45 e acima da nula | A ligação do BTC **não** é artefato do GMM2; a casca lê a cauda no BTC com qualquer régua razoável |
| ρ de C, D e E todos < 0,30 | O +0,64 era em boa parte **produto do GMM2** |
| Qualquer outra combinação | Ambíguo; depende da construção |

O desenho disjunto (20 pares) é relatado, mas é pequeno demais para decidir sozinho (erro-padrão ~0,2).

## Ressalvas registradas

- Exploratório: estes pares já foram vistos. Não confirma nada; só diz se vale gastar um ativo novo depois.
- Nenhuma construção foi aprovada no RB-01. C, D e E são usadas aqui porque não têm o viés de caudas espúrias, não porque sejam réguas validadas.

## Aposta de Claude

~45 % de "não é artefato", ~25 % de "produto do GMM2", ~30 % de ambíguo.
