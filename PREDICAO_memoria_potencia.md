# Previsão registrada antes de calcular: a memória da volatilidade é lei de potência ou soma de exponenciais?

**Registrada em:** 16/10/2026, antes de escrever o código e de rodar qualquer período.

**Pedido da Ana:** "FAÇA", sobre o teste certo apontado na Emenda 1 do H-TEMPO-01: um sintético com escala lenta **ajustada** (não o caminho real), e a comparação direta das formas da memória.

**Status:** exploração, não confirmatória. Jun–jul e ago–set já abertos. Nada de outubro. Nada congelado muda; o H-TEMPO-01 fica como está.

**Ramo:** `exploracao/memoria-potencia`, a partir de `confirmatorio/H-TEMPO-01@574363d`.

## O que estava errado

O M usa como escala lenta o caminho real de volatilidade suavizado em 61 min. Isso importa para o M toda a memória de horas e dias do real. Comparar o real com o M, em memória longa, é comparar o real com ele mesmo.

## O sintético E2 (duas exponenciais ajustadas)

Por semana, a partir de 01/06, como no M:
- **Retorno:** AR(1) por MQO nos retornos reais da semana (a, φ), como no M.
- **Escala lenta, ajustada:** ℓ_t = log s_t do caminho real suavizado (61 min). Ajusta-se por MQO ℓ_t = c + φ_ℓ ℓ_{t−1} + η_t na semana e **simula-se** um novo ℓ*_t com os mesmos c, φ_ℓ e Var(η), partindo do ℓ real do primeiro minuto da semana. s*_t = exp(ℓ*_t).
- **Escala rápida:** h_t AR(1) calibrado como no M (`calibrar`), por semana.
- **Choque:** r*_t = a + φ r*_{t−1} + s*_t · exp(h_t − Var h) · z_t, z gaussiano.
- 5 réplicas, sementes 5026 a 5030.

Nele, por construção, a autocovariância de log-volatilidade é soma de duas exponenciais, com constantes de tempo 1/(1−φ_ℓ) e 1/(1−φ_h) barras. Guardam-se os parâmetros por semana.

## Medidas (idênticas ao H-TEMPO-01a)

a_t = |r_t| / s(h_t) com s(h) de maio; ρ(τ) nos 21 atrasos da grade geométrica de 1 a 1.440 min, período agrupado. Para o real, o M (5 réplicas, 4026–4030, como referência do erro) e o E2.

## Ajustes às três formas, em log ρ, nos atrasos com ρ > 0

1. **Potência:** log ρ = a − β·log τ (2 parâmetros).
2. **Exponencial:** log ρ = a − τ/θ (2).
3. **Duas exponenciais:** ρ = A·e^{−τ/θ₁} + B·e^{−τ/θ₂}, ajustada em log ρ por mínimos quadrados não lineares, θ₁ < θ₂, com limites [1; 10⁴] min (4).

Para cada forma, AIC = n·log(SQR/n) + 2k, com n = atrasos usados e k = parâmetros. Diferenças de AIC maiores que 2 contam como preferência.

## Classificação (por período; só conta se repetir em jun–jul e ago–set)

**Do real:**
- **"Potência":** AIC_pot < AIC_2exp − 2 e 0,1 ≤ β ≤ 0,6.
- **"Duas exponenciais":** AIC_2exp < AIC_pot − 2.
- **"Indistinguível":** o resto. Com 21 atrasos até 1 dia, é o resultado mais provável se as duas formas se parecerem nessa janela.

**Validação do instrumento:** o E2 precisa sair "duas exponenciais" ou "indistinguível" em ≥ 4 das 5 réplicas. Se o E2 sair "potência" com frequência, o ajuste não distingue as formas nesta grade, e o período é INCONCLUSIVO.

**Contra o E2 (secundário):** classe de ΔR² = R²_pot − R²_exp do real em relação ao envelope das 5 réplicas E2 (acima / dentro / abaixo); e o primeiro atraso em que ρ_real sai do envelope do E2 ("descola").

**Descritivos:** β, θ, θ₁, θ₂ e os AIC de cada série; os parâmetros ajustados do E2 por semana (φ_ℓ, Var η); o mesmo para o M, para registrar a diferença entre as duas nulas.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Real "potência" nos dois períodos | ~40 % |
| Real "indistinguível" nos dois períodos | ~40 % |
| Real "duas exponenciais" em algum período | ~20 % |
| E2 passa na validação | ~75 % |
| ΔR² do real acima do envelope E2 (dois períodos) | ~70 % |
| E2 descola do real antes de 2 h | ~65 % |
| β do real entre 0,1 e 0,2 (como no H-TEMPO-01) | ~70 % |

## O que confirma e o que não

- **Potência, estável:** a volatilidade do BTC tem memória que duas exponenciais ajustadas não imitam entre 1 min e 1 dia. O M fecha a memória de 10 min só porque herda a memória longa do real; um sintético honesto não fecharia em horas.
- **Indistinguível:** a janela de 1 dia não separa as formas; precisaria de meses de dados e atrasos de semanas, que o SGV não usa.
- **Duas exponenciais:** o M está certo por um motivo melhor do que parecia: a memória até 1 dia é de poucas escalas.
- Em nenhum caso há direção, previsão ou lucro.

## Como roda

Fumaça em maio sem imprimir; jun–jul local; ago–set no Actions.
