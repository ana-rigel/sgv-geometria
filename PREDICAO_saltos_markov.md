# Previsão registrada antes de calcular: o campo é difusão ou saltos? Qual dimensão falta?

**Registrada em:** 15/10/2026, antes de escrever o código e de rodar qualquer período.

**Proposta:** de Claude, aprovada pela Ana ("Sim"). Vem da literatura de análise estocástica de sistemas complexos: coeficientes de Kramers–Moyal, teorema de Pawula e equação de Chapman–Kolmogorov (Friedrich, Peinke e colaboradores, Physics Reports 2011).

**Status:** exploração, **não** confirmatória. Jun–set já foram abertos. Nada de outubro é lido, e nada congelado muda.

**Ramo:** `exploracao/saltos-markov`, a partir de `exploracao/geometria-residual@ec8b541`.

## Espaço e séries

**Espaço:** o original (E_norm, jerk, memory_flux) na régua de caudas, com âncora em maio real. Mesmas definições de `explora_geometria_residual.py`.

**Passo:** s_t = x_{t+1} − x_t (1 min).

**Semanas:** blocos de 7 dias desde o início do período. O campo da semana k−1 é avaliado nos estados da semana k.

**Séries comparadas:**
- **Real.**
- **S (sintético da exploração anterior), 3 réplicas, sementes 2026 a 2028.** AR(1) por semana mais o caminho de volatilidade real, com os choques padronizados **reais** embaralhados. Tem saltos herdados das caudas dos choques.
- **G (sintético gaussiano), 3 réplicas, sementes 3026 a 3028.** Idêntico ao S, mas com choques **gaussianos** N(0, 1). É difusão pura com volatilidade estocástica, sem saltos.

## Teste 1 — difusão ou saltos (Pawula / 4º coeficiente de Kramers–Moyal)

Numa difusão, o passo condicional ao estado é gaussiano em tempo curto, e o 4º coeficiente de Kramers–Moyal se anula (teorema de Pawula). Saltos aparecem como curtose condicional em excesso.

**Medida:**
- **Momentos locais:** em cada ponto avaliado x, M2_j(x) = média de s_j² e M4_j(x) = média de s_j⁴ entre os k = 200 vizinhos mais próximos de x na semana anterior, com o núcleo tricúbico (o mesmo vizinhança do campo).
- **Curtose condicional:** κ_j(x) = M4_j / M2_j² − 3.
- **Pontos avaliados:** todos os minutos da semana com extremidade ≥ 1, mais 3.000 sorteados com extremidade < 1 (semente 20261019).
- **Regiões:** núcleo (< 1), meio (1–3) e extremos (3–10).
- **Estatística por região:** a mediana de κ_E no eixo E_norm (**primária**). Os eixos jerk e memory_flux são descritivos.

**O que o G mostra:** ele dá a curtose que a mistura de volatilidades produz sozinha numa mesma região, sem nenhum salto. Por isso é a régua correta, e não o zero.

**Classificação por região e período (eixo E_norm):**
- **"Saltos":** real acima do máximo das 3 réplicas G.
  - Se o real também estiver dentro da faixa das réplicas S, fica **"saltos, reproduzidos pelas caudas dos choques"**.
  - Se ficar acima do máximo do S, fica **"saltos além das caudas dos choques"**.
- **"Difusão adequada":** real dentro da faixa ou abaixo do máximo do G.
- Só conta se repetir nos dois períodos.

## Teste 2 — Markov em 3D ou em 4D (a dimensão escondida)

Num processo markoviano no espaço escolhido, a surpresa de agitação do próximo minuto não depende do passado, uma vez conhecido o estado atual.

**Medida:**
- **Surpresa:** ε_{t+1} = |s_{t+1}|² / m2(x_t), com m2(x) = média de |s|² entre os k = 200 vizinhos tricúbicos de x na semana anterior.
- **Memória além do estado:** M = Spearman(ε_{t+1}, média de ε_{t−9}, …, ε_t). Em cada semana avaliada, 5.000 instantes são sorteados (semente 20261020). Os valores das semanas são agrupados.
- **Em 3D:** o estado é x = (E_norm, jerk, memory_flux).
- **Em 4D:** o estado é (x, v_t). A quarta coordenada é v_t = log do desvio dos retornos de 1 min nos 60 minutos **anteriores** a t, causal, posta na régua de caudas com âncora em maio. m2 vem dos vizinhos em 4D.
- **Redução:** Red = 1 − M_4D / M_3D.

**Validação do método:** no G, a volatilidade é por construção a variável escondida, então Red deve ser grande. Isso mostra que o teste enxerga uma dimensão escondida conhecida.

**Classificação por período:**
- **"A volatilidade é a dimensão que falta":** Red_real ≥ 0,5 e M_4D real < 0,05.
- **"Ajuda, mas falta mais":** Red_real ≥ 0,5 e M_4D real ≥ 0,05.
- **"Não é a volatilidade":** Red_real < 0,5.
- Só conta se repetir nos dois períodos.

## Aposta de Claude, antes de tudo

| Aposta | Probabilidade |
|---|---|
| Teste 1: "saltos" nos extremos (real > máximo G) nos dois períodos | ~70 % |
| Teste 1: "saltos" no núcleo | ~45 % |
| Teste 1: se houver saltos, eles são reproduzidos pelas caudas dos choques (real dentro da faixa S) | ~60 % |
| Teste 2: "a volatilidade é a dimensão que falta" | ~30 % |
| Teste 2: "ajuda, mas falta mais" | ~40 % |
| Teste 2: "não é a volatilidade" | ~30 % |
| Teste 2: Red no G ≥ 0,5 (validação do método) | ~80 % |

## Como roda

- **Fumaça:** maio, código rodando sem imprimir estatísticas.
- **Jun–jul:** localmente.
- **Ago–set:** no GitHub Actions (`.github/workflows/explora-saltos-markov.yml`).
