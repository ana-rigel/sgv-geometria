# Pré-registro H-VOL-01 — a dimensão escondida do espaço 3D é volatilidade em várias escalas

**Congelado em:** 15/10/2026, antes de qualquer acesso aos dados de outubro de 2026. O arquivo mensal de outubro da Binance ainda não existe nesta data.

**Decisão da Ana (15/10/2026):** "Sim". Registrar e congelar a versão confirmatória para outubro, julgada junto com o H-DIF-01.

**Quem julga:** `pipeline/confirmatorio_vol.py --julgamento`, executado uma única vez no GitHub Actions deste repositório, sem edição depois deste commit. Os hashes estão em `referencia/HASHES_H-VOL-01.txt`.

**Regra da casa:** nenhuma vitória não conquistada será anunciada.

## Origem

Explorações em BTCUSDT 1m, jun–jul e ago–set/2026, ramos `exploracao/volatilidade-escondida` e `exploracao/volatilidade-multiescala`:

1. **1ª rodada:** INCONCLUSIVA. A medida usava o passo das coordenadas, dominado pela terceira diferença do preço.
2. **2ª rodada:** a medida passou a ser a surpresa do **retorno** do preço, dado o estado 3D. Validação passou. Sobrava memória além de uma volatilidade de escala única.
3. **3ª rodada (multiescala):** "FECHADO", robusto nas quatro estimativas e nos dois períodos. O real ficou entre dois processos de volatilidade pura: o G, só com escala lenta, e o M, com escala lenta e escala rápida.

Como tudo isso foi exploratório e em períodos já abertos, o teste vai para um mês nunca visto.

## Hipótese

**H-VOL-01:** em outubro/2026, a memória residual da agitação do preço real, dado o estado 3D do SGV e a volatilidade estimada (`ew10`), **não excede** a de um processo em que a volatilidade multiescala é a única variável escondida.

## Dados

- **Série:** BTCUSDT spot, klines de 1 min da Binance, com SHA-256 conferido.
  - Maio a julho vêm do repositório (`dados/SHA256SUMS`).
  - Agosto, setembro e outubro são baixados com `.CHECKSUM`.
- **Âncora da régua:** maio/2026.
- **Semanas:** blocos de 7 dias a partir de 24/09/2026.
  - 24/09 a 01/10 serve só como campo da primeira semana julgada.
  - **Julgadas:** 01–08, 08–15, 15–22 e 22–29/10.
  - 29–31/10 fica de fora.
- Junho a setembro entram só como aquecimento das coordenadas e dos sintéticos. Nenhum valor deles é julgado.

## Definições congeladas

Idênticas às da 3ª rodada exploratória, pelo mesmo código:
- `explora_volatilidade_multiescala.py`;
- `explora_volatilidade_escondida_v2.py`;
- `explora_volatilidade_escondida.py`;
- `explora_geometria_residual.py`;
- `explora_forma_D_casca.py`.

**Estado:** x_t = (E_norm, jerk, memory_flux) do sgv_original (ac6b986), na régua de caudas com âncora em maio.

**Surpresa:** ε_{t+1} = r_{t+1}² / (σ̂_t² · m_r(x_t)), em que:
- r é o retorno log de 1 min do fechamento;
- σ̂ = `ew10`, a raiz da EWMA de r² com α = 0,1, usando retornos até t;
- m_r(x) é a média tricúbica de (r_{i+1} / σ̂_i)² entre os 200 vizinhos de x na semana anterior.

**Memória:** M = Spearman(ε_{t+1}, média de ε_{t−9}, …, ε_t), com 5.000 instantes por semana julgada (semente 20261020) e valores agrupados.

**Sintéticos:** gerados a partir de 01/06 com as mesmas sementes da exploração, sempre com o caminho de volatilidade e os parâmetros da própria semana.
- **M**, 5 réplicas, sementes 4026 a 4030: AR(1), mais a escala lenta real (61 min), mais uma escala rápida AR(1) em log-volatilidade calibrada na semana, com choques gaussianos.
- **G**, 5 réplicas, sementes 3026 a 3030: o mesmo sem a escala rápida.

## Julgamento (único)

1. **Validação:** Red_M(oráculo) = 1 − M(oráculo) / M(sem volatilidade) ≥ 0,7, na média das 5 réplicas M. Se falhar, o resultado é **INCONCLUSIVO**.
2. **Primário:** H-VOL-01 é **CONFIRMADA** se M_real(`ew10`) ≤ máximo das 5 réplicas M(`ew10`). Caso contrário, é **NÃO CONFIRMADA**: sobra memória além da volatilidade multiescala.
3. **Secundários (só leitura):**
   - a mesma comparação com `c60`, `ew30` e `har` (robustez);
   - o intervalo mínimo G ≤ real ≤ máximo M em cada estimativa;
   - M sem volatilidade do real, do G e do M;
   - os parâmetros calibrados por semana.
4. **Sem segunda execução,** sem trocar estimativa, réplicas, k, semanas ou mês.

Outubro também é o mês de julgamento do H-DIF-01 e do H-FORMA-D-01/02. Os testes são independentes, cada um pré-registrado por si, e não há correção entre famílias.

## Ensaio de paridade

Antes de baixar outubro, o mesmo script (`--paridade`) roda jun–jul. Ele precisa reproduzir **exatamente** (diferença < 1e-9) os valores de `resultados/volatilidade_multiescala_junjul.json`: as memórias do real, das 5 réplicas M e das 5 réplicas G, com todas as estimativas.

## O que confirma e o que não

- **Confirmada:** num mês nunca visto, o espaço 3D do SGV se comporta como a projeção de um sistema cuja variável escondida é a volatilidade em várias escalas. A memória que sobra não pede outra explicação. Isso é descritivo: não tem alegação de previsão nem de lucro.
- **Não confirmada:** em outubro sobra memória da agitação que um processo de volatilidade multiescala, com essa calibração, não produz. A conclusão das explorações não se transporta.
- **Ressalva já conhecida:** na exploração, o M deixou mais memória residual que o real em todas as comparações, então o critério tende a ser atendido com folga. Por isso o intervalo G–M (secundário) entra no relatório ao lado do veredito.

## Aposta (Claude, antes dos dados)

| Aposta | Probabilidade |
|---|---|
| Validação passa | ~95 % |
| H-VOL-01 confirmada | ~75 % |
| Robusta (as quatro estimativas concordam) | ~50 % |
