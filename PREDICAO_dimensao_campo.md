# Previsão registrada antes de calcular: quantas dimensões o campo de agitação tem?

**Registrada em:** 15/10/2026, antes de rodar em jun–jul e em ago–set.

**Status:** exploração, **não** confirmatória. Jun–set já foram abertos.
- Nada de outubro é lido. O script recusa dados de outubro.
- Nada congelado muda: H-DIF-01, H-DIR-01, H-FORMA-D-01 e H-FORMA-D-02.

Antes deste registro rodou só um teste de fumaça: 3 semanas de maio, o mês da âncora. Ele **não imprime estatísticas**. Conferi apenas três coisas mecânicas:
- quase todos os 1.500 pontos têm massa efetiva ≥ 30, no real e na nula;
- a nula simulada é finita;
- a nula tem dispersão parecida com a do real.

## A pergunta

O tamanho da agitação, tr D(x), muda de lugar para lugar. Isso já se sabe. A pergunta é se essa mudança é:
- **uma função de duas variáveis simples:** o volume relativo ν (eixo do fluxo; volume alto anda com agitação alta) e a raridade log ρ (distância ao núcleo);
- **ou uma geografia em 3D** que sobra depois de descontá-las e que se repete de uma semana para outra.

## Medidas

- **Campo:** o estimador do H-DIF-01 (h = 0,45) com os pares de cada semana, avaliado em 1.500 pontos fixos sorteados dos estados de maio (semente 20261018).
- **Semanas:** blocos de 7 dias a partir de 01/06 e de 01/08. A última semana entra se tiver ≥ 5 dias. São 9 semanas por período, 8 pares consecutivos.
- **Resíduo em cada semana:** log tr D(p) menos o ajuste por MQO de um polinômio cúbico completo.
  - No fluxo: em (ν(p), log ρ_w(p)).
  - No original: só em log ρ_w(p).
  - Entram os pontos com massa efetiva ≥ 30.
- **Persistência:** Spearman, entre pontos, do resíduo da semana w com o da semana w+1. Os dados das duas semanas são disjuntos.
- **Nula: 5 réplicas por semana**, sementes 2026 a 2030.
  1. VAR(1) ajustado nos dados reais da semana.
  2. Resíduos padronizados pela volatilidade local no tempo (RMS centrado de 61 min, por eixo).
  3. Os padronizados são embaralhados dentro da semana e reescalados na ordem original.
  4. A série é reconstruída.
- **O que a nula preserva e o que destrói:**
  - Preserva a memória linear e o agrupamento de volatilidade.
  - Destrói a ligação entre o tamanho do passo e o lugar, exceto a radial: surtos geram excursões maiores, então a raridade continua ligada à agitação na nula.
- **Δ por par** = persistência do resíduo no real − média das 5 réplicas.

## Previsões para o fluxo (primária desta exploração)

1. **Classificação, em cada período:**
   - **"Geografia 3D além de volume e raridade":** Δ médio ≥ 0,10 e real acima da média da nula em ≥ 7 dos 8 pares.
   - **"Indício fraco":** Δ médio > 0 e real acima em ≥ 5 dos 8 pares, sem atingir o critério anterior.
   - **"Não há":** o resto. O campo de tamanho é essencialmente volume + raridade.
2. **Só conta se repetir nos dois períodos.** Classificações diferentes são relatadas como "não estável".
3. **Descritivo, sem limiar:**
   - R² de (ν, log ρ) sobre log tr D;
   - persistência do log tr D bruto;
   - correlação do resíduo médio com z, |z|, ι e |ι|, para ver onde mora a geografia que sobra.

O original é **descritivo**. Lá não há eixo de volume, e a memória imposta pelas fórmulas deixa a nula VAR menos limpa: a dispersão simulada sai até 15% maior.

## Aposta de Claude, antes dos dados

| Classificação no fluxo, nos dois períodos | Probabilidade |
|---|---|
| Geografia 3D | ~40% |
| Indício fraco | ~30% |
| Não há | ~30% |

Outras apostas:
- **R² mediano de (ν, log ρ) no fluxo ≥ 0,6:** ~60%.
- **Se sobrar geografia, ela mora principalmente em |z| ou em ι:** ~60%. Grandes movimentos normalizados e agressão unilateral seriam os candidatos naturais.

## Como roda

- **Jun–jul:** localmente.
- **Ago–set:** `.github/workflows/explora-dimensao-campo.yml`, disparado pelo push deste ramo. Grava `resultados/dimensao_campo_agoset.{json,log}`.
