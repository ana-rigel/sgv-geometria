# SGV-M21b — Leitura: dependência temporal entre instantes no BTC exploratório

**Execução:** GitHub Actions run 38167731272 (23 jobs, todos com sucesso; 84/84 origens válidas). Só dados exploratórios. Contagem principal conferida por recontagem independente (MSDCCLM, HSIC lag 1: 68/84). (Cosmético: o cabeçalho da tabela gerada cita `scripts/m21b_agregar.py`; a agregação está em `experiments/m21b_dependencia_btc.py --mode aggregate`.)

## 1. Taxas de alarme (posto conservador, nominal 5%; "elevado" = Wilson inferior > 7%)

| Nulo | lin 1/5/30 | vol 1/5/30 | HSIC 1/5/30 |
|---|---|---|---|
| MS (2 escalas) | 85 / 74 / 71% | 96 / 81 / 52% | 83 / 80 / 77% |
| **MSDCCLM** (melhor paramétrico) | **74 / 43 / 25%** | **88 / 66 / 33%** | **81 / 61 / 37%** |
| BL (blocos reais de 8 h) | 11 / 14 / 13% | 10 / 7 / 10% | 10 / 11 / 16% |

## 2. Veredito pré-registrado

- **Lag 1 e lag 5: "dependência não reproduzida, compatível com memória de volatilidade."** HSIC elevado, mas `vol` também; o HSIC **não** alarma mais que `vol` (P2a: p=0,98 e 0,89).
- **Lag 30:** mesmo padrão, mas **veredito suspenso** pela regra: a sanidade do BL falhou (HSIC_30 em 15,5%, Wilson [9,3–24,7%]).
- **Nenhuma defasagem com o padrão "tipo M20"** (dependência não linear além da 2ª ordem e da volatilidade).

## 3. O que isso significa

1. **A linha M20 não tem objeto demonstrado no BTC nesta escala.** Toda a dependência não linear que o HSIC encontra é acompanhada (e não superada) pela memória de volatilidade. Não há sinal de dependências "escondidas" do tipo H±. Pela regra do programa, a linha M20 fica **encerrada** até surgir evidência nova no próprio mercado.
2. **Achado mais importante, e inesperado: o melhor modelo paramétrico não reproduz nem a dependência *linear* de curto prazo.** No lag 1, a covariância cruzada defasada alarma em 74% das janelas. O modelo de duas escalas emite, dentro de cada estado, pontos sem autocorrelação própria — e o BTC no 1m tem dinâmica linear de curto prazo forte (por exemplo, o volume tem autocorrelação ~0,47 no lag 1). **Isso explica por que os nulos paramétricos nunca fecharam a lacuna no M16–M18**: faltava a peça mais convencional de todas.
3. **Memória de volatilidade de curto prazo também falta** (`vol_1` 88%).
4. **O BL continua o nulo de trabalho**, mas é **levemente liberal** (~10–15% em vez de 5–7%) nas estatísticas de dependência com lag ≥ 5, provavelmente pelas emendas entre blocos e pela não estacionariedade entre o prefixo e a janela. Isso deve ser levado em conta ao ler alarmes isolados.

## 4. Placar das apostas de Claude
| Aposta | Resultado | |
|---|---|---|
| HSIC_1 elevado sob MSDCCLM (60%) | sim (81%) | ✅ |
| Algum lag "tipo M20" (15%) | não | ✅ (não ocorreu) |
| Algum lag "memória de volatilidade" (45%) | sim (lags 1 e 5) | ✅ |
| BL passa na sanidade nos 3 lags (85%) | não (lag 30) | ❌ |

## 5. Próximo passo sugerido
Se o objetivo for um **modelo** do funcionamento (e não só o nulo empírico BL), a peça que falta é conhecida e convencional: **regimes de duas escalas com emissões autorregressivas e volatilidade condicional** (Markov-switching VAR com GARCH, por exemplo). Testar se isso fecha a lacuna nas três réguas e nas estatísticas de dependência seria o "modelo mínimo" do BTC no 1m. Senão, o BL segue como nulo de trabalho.
