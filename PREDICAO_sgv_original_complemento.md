# Previsão registrada antes de calcular: complemento à exploração do H-SGV-01 (rascunho)

**Registrada em:** 15/10/2026, antes de rodar.
- **Ramo:** criado a partir de `research/sgv-original-variaveis` (e9ddd10). O rascunho não é alterado.
- **Status:** exploração. Nada de outubro é lido, e nada congelado muda.
- **Fumaça:** rodou em maio só para conferir o código. Não imprimiu estatísticas.

## O que esta rodada acrescenta

O rascunho do H-SGV-01 explorou só jun–jul. Esta rodada usa as mesmas funções (`explorar_sgv_original.py`, importado) e acrescenta:

1. **Ago–set fora da amostra.**
   - Semana de treino: 25/07–01/08.
   - Semanas julgadas: 01/08, 08/08, 15/08, 22/08, 29/08, 05/09, 12/09, 19/09 e 26/09–01/10 (5 dias). São 9 semanas.
   - Mesmo alvo, mesmos controles, mesma nula de pipeline.
2. **Controle "fluxo" (complementaridade).** Os controles primários mais quatro variáveis do espaço de fluxo:
   - log ρ, log tr D e c(x) do campo do H-DIF-01, todos calculados no fluxo;
   - ν(t).

   Pergunta: o original acrescenta ao fluxo?
3. **Controle "retornos lentos".** Os controles primários mais retornos com sinal de 60, 240 e 1.440 min. Pergunta: `mem_e` é esticamento ou só alavancagem de prazo mais longo?

**Paridade.** Em jun–jul, os ρ semanais dos controles primários e da secundária original têm que repetir os de `resultados/explorar_sgv_original_jun_jul.json`, com diferença ≤ 1e-4 (arredondamento).

## Critérios

### 1. Ago–set, controles primários

Valores de jun–jul: log ρ −0,079; deslocamento +0,031; `mem_e` −0,027.

| Classificação | Condição |
|---|---|
| **Repete** | mesmo sinal em ≥ 7 de 9 semanas e \|ρ̄\| ≥ 50% do valor de jun–jul |
| **Repete fraco** | mesmo sinal da média e ≥ 5 de 9 semanas, sem atingir o anterior |
| **Não repete** | o resto |

### 2. `mem_e` com o controle "fluxo", nos dois períodos

| Classificação | Condição |
|---|---|
| **Complementar** | mantém o sinal e ≥ 50% do ρ̄ primário do mesmo período, nos dois períodos |
| **Parcial** | mantém o sinal com 25–50% |
| **Redundante** | < 25% ou troca de sinal |

### 3. `mem_e` com o controle "retornos lentos"

As mesmas faixas:

| Classificação | Condição |
|---|---|
| **Esticamento próprio** | ≥ 50% nos dois períodos |
| **Parcial** | 25–50% |
| **Alavancagem lenta** | < 25% ou troca de sinal |

### Descritivo

log ρ e deslocamento com os controles "fluxo" e "retornos lentos".

## Aposta de Claude, antes dos dados

**Ago–set, controles primários:**

| Variável | Repete | Fraco | Não repete |
|---|---|---|---|
| log ρ | ~75% | ~15% | ~10% |
| Deslocamento | ~45% | ~30% | ~25% |
| `mem_e` | ~45% | ~30% | ~25% |

**`mem_e` com o controle "fluxo":** complementar ~50%, parcial ~25%, redundante ~25%. O fluxo não tem o nível do preço em relação à média, então espero que `mem_e` sobreviva.

**`mem_e` com os retornos lentos:** esticamento próprio ~40%, parcial ~30%, alavancagem lenta ~30%. Retornos de 4 h e de 1 dia podem absorver boa parte do efeito.

## Como roda

- **Jun–jul:** localmente.
- **Ago–set:** `.github/workflows/explora-sgv-original-complemento.yml`, disparado pelo push deste ramo.
