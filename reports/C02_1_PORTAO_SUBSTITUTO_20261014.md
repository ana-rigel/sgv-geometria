# SGV-C02.1 — Portão substituto de engenharia: o extrator sem malha resolve a grade, mas o portão registrado não passa

**Data:** 14/10/2026. **Natureza:** engenharia, **não** é o portão oficial (seção 4 da emenda). O gerador oficial da C02 (`SGV_C02_GERADOR_PILOTO_20261014.zip`, SHA-256 `4691266c…`) não está no ramo; aqui foram usados geradores locais que imitam G3 (mistura de 3 gaussianas) e BS35 (mistura de 3 t de Student ν = 3,5 com banana), com T0–T6 e operador de incômodo como no protocolo C02. Nenhum treino, validação ou caso OOD.

Emenda: `PROTOCOLO_SGV_C02_1_EMENDA_HDR_SEM_MALHA_20261014.md` (commit `44c6541`, antes deste código). Código: `experiments/c02_1_hdr_sem_malha.py`; testes: `tests/test_c02_1_hdr_sem_malha.py` (9 analíticos, todos passam: volume exato do HDR gaussiano, translação, escala, rotação, identidade, determinismo, falha fechada); script: `scripts/c02_1_portao_substituto.py`; dados: `reports/c02_1/portao_substituto.json`.

## Desenho

2 famílias substitutas × 7 transformações × 3 réplicas = 42 pares, 750 + 750 observações independentes, GMM3 com as regras do C01. Em cada par, **as mesmas densidades ajustadas** passam pelos dois extratores:
- **grade do C01** (`hdr_pair`): volume do HDR50 em 35³ contra 49³;
- **HDR12-ML**: orçamento ×1 contra ×2, sementes de Monte Carlo independentes, julgado pelas checagens registradas na seção 4 da emenda.

## Resultado

**1. O substituto reproduz a falha do V1, e o extrator sem malha a elimina no HDR50.**

| | G3 substituto | BS35 substituto |
|---|---|---|
| Grade do C01, variação do volume HDR50 entre 35³ e 49³ | 2 % a 4 % | **33 % a 394 %** |
| HDR12-ML, \|Δ log V\| do HDR50 entre ×1 e ×2 (máximo) | 0,041 | **0,053** |

**2. O portão de precisão registrado não passa em nenhuma das famílias.** Pares com pelo menos uma checagem falha: **G3 10/21, BS35 18/21**. Pela regra da emenda (uma falha bloqueia), a C02.1 *como registrada* ficaria bloqueada.

**3. As falhas têm duas causas distintas.**

*(a) Erro de desenho do portão (meu), visível até na família bem comportada.* Em G3, 12 das 13 falhas são `center_distance`: o limite relativo de 10 % de uma distância de ≈ 0,2 (≈ 0,02) é menor que o ruído do próprio Monte Carlo (\|Δ\| p90 de 0,017 no HDR50 e 0,028 no HDR95). Os demais ruídos em G3 ficam bem abaixo das escalas dos valores: log V p90 0,03 (valores medianos 0,05–0,07); forma p90 0,015; Jaccard p90 0,011; massa cruzada p90 0,003. O limite de log V (0,05) também é mais apertado que o equivalente ao critério do V1 (10 % relativos = 0,095) sem justificativa; no teste de identidade gaussiano, o ruído de log V no HDR95 é ≈ 0,013 por lado.

*(b) Instabilidade real das medidas de volume do HDR95 com caudas pesadas.* Em BS35, \|Δ\| máximo: log V do HDR95 0,090; centro do HDR95 0,145; forma do HDR50 0,125 e do HDR95 0,048; o tamanho amostral efetivo dos pesos 1/p̂ no HDR95 cai a 1.624 (mediana 5.095, contra ≈ 13.000 em G3). A região de 95 % de um GMM3 ajustado a dados com ν = 3,5 se estende por componentes de peso mínimo nas caudas; volume, centroide e forma **da medida uniforme** dessa região dependem desses componentes. Isso é mal-condicionamento da quantidade, não da malha: tirar a malha não o resolve. As medidas de **probabilidade** (massa cruzada, p90 0,004) e o Jaccard (p90 0,019) seguem estáveis, e `w2_hdr` é determinístico (nunca falha).

## Consequência e decisão pendente (Ana)

Nada foi alterado na emenda depois destes números. A C02.1 como registrada **não deve seguir** para o portão oficial. Opções para uma errata C02.1a, a registrar antes do portão oficial e sem tocar treino/validação/OOD:

1. **Corrigir só o desenho do portão (causa a):** limites com piso absoluto em unidades de s_A para `center_distance` (por exemplo 0,05 · s_A) e log V ancorado no V1 (\|Δ\| ≤ log 1,10). Insuficiente sozinho: BS35 continuaria falhando no HDR95 (causa b).
2. **Trocar as medidas de volume do HDR95 por medidas de probabilidade:** manter HDR50 como está (estável); no HDR95 usar centroide e forma **ponderados por p̂** (sem pesos 1/p̂), manter Jaccard, massa cruzada e `w2_hdr`, e retirar o log-volume do HDR95. O bloco perde dimensão (11 variáveis) ou ganha uma variável de probabilidade no lugar; isso precisa ser decidido antes.
3. **Trocar HDR95 por um nível menos extremo (HDR80):** reduz a dependência das caudas, mas muda a pergunta do C01/C02 (HDR95).

**Recomendação:** 1 + 2. Ela ataca as duas causas, preserva a parte do bloco que se mostrou estável e não ajusta nada pelo desempenho de nenhum classificador. Antes do portão oficial, o gerador oficial C02 precisa entrar no ramo byte a byte.

**Ressalva:** os geradores substitutos imitam, mas não são, G3 e BS35 oficiais. A conclusão de engenharia (o extrator de grade falha no BS35, o sem malha resolve o HDR50 e o HDR95-volume é mal condicionado com caudas pesadas) é o que se leva daqui; números não.
