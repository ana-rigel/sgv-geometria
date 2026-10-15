# Leitura contra a previsão registrada (PREDICAO_volatilidade_escondida.md, commit cd61db6)

Exploração, não confirmatória.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38816402078).

## Veredito pela regra registrada: INCONCLUSIVO

A validação da etapa A falhou nos dois períodos. No sintético G, dar ao teste a volatilidade **verdadeira** (oráculo) não reduziu a memória: Red = −0,017 em jun–jul e −0,021 em ago–set, contra o mínimo de 0,7. A etapa B não foi aplicada. Pela regra, nada se conclui sobre o real.

| M (memória da surpresa) | jun–jul real | jun–jul G (5) | ago–set real | ago–set G (5) |
|---|---|---|---|---|
| sem volatilidade | +0,221 | +0,241 a +0,252 | +0,334 | +0,315 a +0,329 |
| oráculo | — | +0,238 a +0,261 | — | +0,316 a +0,344 |
| ew10 (a melhor causal no G) | +0,169 | +0,195 a +0,209 | +0,247 | +0,273 a +0,289 |
| har | +0,209 | +0,246 a +0,257 | +0,307 | +0,348 a +0,364 |
| c60 | +0,300 | +0,313 a +0,324 | +0,383 | +0,391 a +0,407 |

**Apostas:**
- validação passa (~75 %): **errou**;
- estimativa escolhida: ew10 (~30 %), mas a regra não chegou a usá-la.

## Diagnóstico da falha (posterior à rodada, não registrado; uma réplica G, jun–jul)

| Medida | M |
|---|---|
| retorno² bruto | 0,43 |
| retorno² ÷ oráculo² | **0,004** |
| \|passo no espaço 3D\|², bruto | 0,49 |
| \|passo no espaço 3D\|² ÷ oráculo² | 0,13 |
| mercado iid sem volatilidade agrupada, \|passo 3D\|² com estado | 0,035 |

- O eixo jerk responde por 96 % de |passo|² no real (E_norm 1,4 %, memory_flux 3 %).
- O passo do jerk é uma combinação de quatro retornos consecutivos, com pesos 1, −3, 3, −1. Por isso passos vizinhos compartilham retornos.

**Leitura:**
1. **A volatilidade funciona quando a medida é limpa.** Nos retornos do preço, a volatilidade verdadeira apaga a memória da agitação (0,43 → 0,004).
2. **A medida registrada não era limpa.** Ela usava o passo das coordenadas, dominado pela terceira diferença do preço. Essa medida mistura memória de construção (sobreposição dos retornos) com memória de volatilidade, e o condicionamento no estado 3D mistura as duas de novo. O teste media a memória errada.
3. **Correção do que escrevi na leitura anterior** (`LEITURA_saltos_markov.md`, Teste 2): a frase "a memória que quebra Markov em 3D é igual à de um processo de volatilidade estocástica pura" está certa nos números (real ≈ G), mas a medida era dominada por essa mistura. Ela não identifica a volatilidade como causa.

## Próximo passo

Segunda rodada, registrada antes de calcular no real: a surpresa medida no **retorno do preço**, dado o estado 3D e a volatilidade (`PREDICAO_volatilidade_escondida_v2.md`).
