# Previsão registrada antes de calcular: o que sobra da geometria do mercado quando os fatos conhecidos são reproduzidos?

**Registrada em:** 15/10/2026, antes de escrever o código e de rodar qualquer período.

**Proposta:** de Claude, aprovada pela Ana ("Sim").

**Status:** exploração, **não** confirmatória. Jun–set já foram abertos. Nada de outubro é lido, e nada congelado muda (H-DIF-01, H-DIR-01, H-FORMA-D-01, H-FORMA-D-02).

**Ramo:** `exploracao/geometria-residual`, a partir de `exploracao/dimensao-campo@31bef36`.

## Por que

Três resultados geométricos do programa foram comparados só com nulas que **destroem** o agrupamento de volatilidade:

1. **Agitação nos extremos.** No espaço original, na régua de caudas, a agitação D(x) do estimador localmente linear cresce ×10,6 do núcleo à faixa 5–10. Na nula de permutação dentro do dia, cresce ×2,3. Fonte: `campo_caudas/RESULTADO_CAMPO_CAUDAS.md`.
2. **Persistência das cascas.** A orientação e o tamanho das cascas mudam menos entre dias vizinhos do que entre dias distantes: rotação mediana de 16° contra 66° no original bruto. Fonte: relatório de mercado do navegador, parte 2.
3. **Assinatura de caudas.** A feature de caudas da casca acompanha a cauda real dos retornos: ρ = +0,64 no BTC.

As explorações de 15/10 (`exploracao/dimensao-campo`, `exploracao/memoria-D`) mostraram que a geografia da agitação e o desacoplamento entre D e a casca são explicados por **memória linear, volatilidade agrupada e volume**. Este teste aplica a mesma pergunta aos três resultados acima.

## O mercado sintético (no nível do preço; as coordenadas saem das mesmas fórmulas)

Ele preserva **tudo o que já se sabe** e destrói o resto. As coordenadas E_norm, jerk e memory_flux dependem só do fechamento, por isso o sintético muda só o fechamento.

**Construção dos retornos**, com r = retorno log de 1 min do fechamento, de 01/06 em diante (maio fica real, porque é a âncora da régua). Em cada semana de 7 dias contada a partir de 01/06:

1. **Memória linear:** ajusta AR(1) por MQO, r_t = a + φ r_{t−1} + e_t.
2. **Volatilidade local:** s_t = raiz da média centrada de e² em 61 min (mínimo de 10).
3. **Choques padronizados:** u_t = e_t / s_t.
4. **Embaralhamento:** u é embaralhado dentro da semana. O retorno sintético é refeito com o **mesmo** caminho s_t e o **mesmo** AR(1): r*_t = a + φ r*_{t−1} + s_t · u*_t.

**Preço:** fechamento* = exp(log c₀ + Σ r*). Máximas, mínimas e volume permanecem os reais, mas não entram nas coordenadas.

**O que ele preserva:**
- a memória linear de 1 minuto;
- o caminho de volatilidade minuto a minuto (agrupamento exato);
- a distribuição dos choques padronizados, com as caudas deles.

**O que ele destrói:** qualquer dependência não linear entre choques além do caminho de volatilidade. Por exemplo, a ordem dos choques dentro de um surto e a ligação entre sinal e tamanho.

**Réplicas:** 5, com sementes 2026 a 2030.

**Referência de continuidade:** a nula antiga (permutação dentro do dia de retornos, sombras e volume), 1 réplica com semente 2026.

## As três propriedades, com as definições de antes

**Régua de caudas:** (x − mediana de maio) / (q99,5 de |x − mediana| em maio / 3), sempre com o maio **real** como âncora. Extremidade = max |xⱼ|.

### P1 — agitação nos extremos

**Estimador:** o localmente linear, idêntico ao do H-CAUDA-01: k = 200, tricúbico, correção por ESS.
- O campo da semana k−1 é avaliado nos minutos da semana k.
- Pontos avaliados: todos os minutos com extremidade ≥ 1, mais 3.000 sorteados com extremidade < 1 (semente 20261019).

**Estatística:**

> R = mediana de D nos minutos com 3 ≤ extremidade < 10 ÷ mediana de D nos minutos com extremidade < 1

Calculada sobre todas as semanas avaliadas do período, com o perfil das faixas < 1, 1–2, 2–3, 3–5 e 5–10.

### P2 — persistência das cascas

**Mapas:** um a cada 240 min desde o início do período, com janela de 1.500 min. HDR50 por `build_shell(X, seed = 20261009, n = 25)` do M11-I, na régua de caudas. Mapas inválidos ficam de fora.

**Pares:** mapas a 7 posições de distância (28 h), ambos válidos.

**Estatística primária:** rotação mediana do eixo principal da HDR50, pelo tensor de inércia da malha, módulo inversões, como em `mercado/assinaturas.py`.

**Secundária:** |log V50| mediano / 3.

### P3 — assinatura de caudas

- **HDR95:** vem do mesmo ajuste GMM2, grade 61³, ±10 (`u031_casca`).
- **Feature:** caudas = log(V95_B/V95_A)/3 − log(V50_B/V50_A)/3.
- **Estatística:** ρ de Spearman, nos pares de 28 h, entre a feature e Δlog(q99,9/mediana de |r|), calculado com os retornos **da própria série** (real ou sintética).

## Critério, por propriedade e por período

| Classificação | P1 | P2 | P3 |
|---|---|---|---|
| **Própria do mercado** | real acima do máximo das 5 réplicas | real abaixo do mínimo das 5 réplicas (mais persistente) | real acima do máximo das 5 réplicas |
| **Indício** | real acima da média, mas não do máximo | real abaixo da média, mas não do mínimo | real acima da média, mas não do máximo |
| **Reproduzida pelos fatos conhecidos** | o resto | o resto | o resto |

**Só conta se repetir nos dois períodos** (jun–jul e ago–set). Classificações diferentes são relatadas como "não estável".

## Aposta de Claude, antes de tudo

| Propriedade | Própria nos dois períodos |
|---|---|
| P1 (agitação nos extremos) | ~30 % |
| P2 (persistência das cascas) | ~20 % |
| P3 (assinatura de caudas) | ~15 % |

**As três reproduzidas pelos fatos conhecidos (nenhuma "própria" estável): ~55 %.**

## Como roda

- **Fumaça:** maio, 2 semanas, código rodando sem imprimir estatísticas.
- **Jun–jul:** localmente.
- **Ago–set:** no GitHub Actions (`.github/workflows/explora-geometria-residual.yml`), disparado pelo push do workflow, com download de agosto e setembro conferido por `.CHECKSUM`.
