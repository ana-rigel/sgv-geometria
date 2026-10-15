# Resultado RB-01: régua bruta sob caudas pesadas

**Veredito pelas regras registradas: NENHUM candidato aprovado.** Pela seção 6 do protocolo, a linha para aqui, sem dado de mercado.

Execução: 15/10/2026, código congelado em `3aef064` e julgamento em `e33efea` (hashes em `referencia/HASHES_RB-01.txt`), 6 famílias × 8 casos × 8 pares, 5 reajustes por janela. Dados em `resultados/rb01/`; julgamento em `resultados/rb01/julgamento_rb01.json`.

**Transparência:** antes do congelamento, um teste de tempo numa única janela da F3 mostrou o GMM2 com massa real do HDR50 de 0,77 e a mistura de t com 0,50. Nada mudou no código depois disso.

## Portões (✓ passa, ✗ falha), por família F0–F5

| | G1 numérico | G2 validade | G3 fidelidade | G4 confiabilidade | G5 recuperação |
|---|---|---|---|---|---|
| A, atual (vendor) | ✗✗✗✗✗✗ | ✗✗✗✓✗✗ | ✓✓✗✗✗✗ | ✓✗✗✗✗✗ | ✗✗✗✗✗✗ |
| B, GMM2 + Hyndman | ✓✗✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✗✗✗✗ | ✓✗✗✗✗✗ | ✗✗✗✗✗✗ |
| C, GMM3 + Hyndman | ✓✗✗✗✓✗ | ✓✓✓✓✓✓ | ✓✓✓✓✓✗ | ✓✓✓✗✗✗ | ✗✗✗✗✗✗ |
| D, mistura de t | ✓✓✗✓✓✓ | ✗✗✗✗✓✗ | ✓✓✓✓✓✓ | ✓✗✗✗✓✓ | ✗✗✗✗✗✗ |
| E, KDE | ✓✓✓✗✓✓ | ✓✓✓✓✓✓ | ✗✗✗✗✗✗ | ✓✓✓✓✓✓ | ✗✗✗✗✓✗ |

## Achados

1. **A régua atual (A) falha no que importa.**
   - Descarta de 2% a 12% das janelas por cobertura do HDR50 (grade ±3,5).
   - O "HDR50" do GMM2 contém de fato até 61% da massa real (F5: +11 pp; F4: +5,6 pp).
   - Na régua secundária `flow_raw`, com ν ≤ 3,5, ela invalida 98% a 100% das janelas.
2. **O GMM2 lê caudas onde não há mudança.** Em pares sem transformação, a feature de caudas do GMM2 (A e B) dá +0,13 ± 0,23 (F2) e +0,14 ± 0,26 (F5). Um aumento real de 5% de massa nas caudas dá +0,14. Com o GMM2, pares sem mudança e pares com caudas reais são indistinguíveis nesse nível.
3. **Com modelos melhores, a feature de caudas funciona.** Com GMM3, mistura de t ou KDE, o viés nos nulos cai para ~0,01 e a dispersão para 0,02–0,06. A separação "5% de caudas contra nada" (AUC) fica entre 0,94 e 1,00 com GMM3, contra 0,72 do GMM2 na F2.
4. **Cada alternativa falha num ponto diferente.**
   - **C (GMM3):** a mais equilibrada. Fidelidade dentro do limite em 5 de 6 famílias (F5: 1,08 pp contra 1,00). A confiabilidade fica abaixo de 0,80 em F3 (feature 0,77), F4 (núcleo 0,73) e F5 (núcleo 0,795).
   - **D (mistura de t):** a melhor fidelidade (viés ≈ 0 em tudo). O EM não converge em 200 iterações em 2% a 16% das janelas, o que reprova a validade.
   - **E (KDE):** a mais estável e a de menor leitura espúria. Mas o HDR50 contém de 5 a 10 pp de massa a mais, porque o núcleo fica alisado.

## Defeitos de desenho do próprio protocolo (reportados, sem mudar o veredito)

- **G5 tem teto abaixo do limiar.** Cinco dos 8 casos têm feature verdadeira = 0 (afins). Com esses empates, o ρ máximo possível é 0,87 com estimativa perfeita. Além disso, a verdade de Monte Carlo dos casos afins oscila ±0,005 em torno de zero, o que baixa ainda mais o ρ registrado. Pela análise pós-hoc (`regua/posthoc_rb01.py`, escrita depois de ver os dados), a razão ρ/teto fica em 0,91–1,00 para C em todas as famílias.
- **G1 está no limite da resolução do Monte Carlo.** Com 20.000 amostras para o limiar e 20.000 para a massa, o p95 esperado de |erro| no HDR50 é ≈ 0,98 pp, contra o limite de 1,0 pp. As falhas de G1 em B–E (p95 de 0,81 a 1,08 pp) são ruído de amostragem, não do método.

Esses dois defeitos não salvam nenhum candidato: mesmo ignorando G1 e G5, nenhum passa G2–G4 em todas as famílias. C fica perto (G3 por 0,08 pp na F5, G4 em três famílias).

## Apostas registradas

A ~2% (reprovado), B ~15% (reprovado), C ~20% (reprovado), D ~45% (reprovado), E ~10% (reprovado). "Pelo menos um" ~55%: errou.

## Consequência

- A leitura "envelope crescendo mais que o núcleo = caudas" **não é confiável com o GMM2** do painel em dados de caudas pesadas.
- A feature é recuperável com GMM3, mistura de t ou KDE, mas nenhuma construção passou em todos os portões.
- Qualquer continuação exige um protocolo novo (RB-02), registrado antes de rodar, com G1 e G5 corrigidos e candidatos ajustados.
