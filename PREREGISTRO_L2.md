# Pré-registro L2 — Geometria de Fisher–Rao do espaço de modelos

**Estado: ESPECIFICAÇÃO CONGELADA em 09/10/2026, aprovada pela Ana sem alterações** (os quatro pontos da seção 11). Nada foi calculado. O código e a calibração (seção 6) vêm depois e são congelados antes de abrir o período confirmatório. ~~A execução só começa depois que o paper trading da Fase 2 do portfólio estiver rodando.~~ **Emenda 1 (09/10/2026, por decisão da Ana):** a precondição foi substituída por uma cópia própria do `sgv_operavel` congelado (`operavel/`, conferida pelo manifesto). Com isso a L2 roda sem depender da outra conversa. A emenda muda só o calendário: hipótese, dados, teste e critérios continuam os mesmos.

**Relação com o que já foi feito.** Esta é uma **linha nova**, não uma terceira tentativa da linha encerrada. A linha encerrada (C1 e R1) mediu a geometria do **espaço das observações**: cada barra é um ponto, e a curvatura é a da nuvem de barras. O resultado foi que essa geometria é a sombra dos fatos estilizados. A L2 mede a geometria do **espaço dos modelos**: cada ponto é um estado de informação do mercado, descrito pelo modelo SF1 ajustado numa janela. A métrica é a de Fisher–Rao, a única que respeita a estrutura da informação (teorema de Čencov). Não é uma escolha nossa.

## 1. Hipótese

**H-L2.** Quando a estrutura de informação do fluxo muda depressa, a volatilidade muda de regime logo em seguida. "Estrutura de informação do fluxo" quer dizer a relação entre preço e fluxo agressor e a dinâmica da atividade. "Mudar depressa" quer dizer alta velocidade de Fisher–Rao no espaço do SF1. O efeito precisa ir além do que a própria volatilidade e as mudanças recentes dela já antecipam.

Em termos práticos, é um **alarme de risco**, não um sinal de direção.

## 2. Variedade, ponto e métrica

**Modelo local SF1-L**, ajustado em cada janela com as coordenadas da R1 (z, ι, ν, conforme `sgvgeo/flow.py`). O ponto é θ = (log σ; a0, a1, a2, log s1; b0, b1, b2, b3, log s2):

- **Bloco do preço:** r = σ·ε, com ε seguindo uma t de Student com ν graus de liberdade. O valor de ν é fixado uma vez por escala de tempo, no ajuste GARCH-t do período de exploração.
- **Bloco do fluxo:** ι* = arctanh(ι) = a0 + a1·z + a2·ι*₋₁ + e1, com e1 normal de variância s1².
- **Bloco da atividade:** ℓ = log volume = b0 + b1·ℓ₋₁ + b2·|z| + b3·z + e2, com e2 normal de variância s2².

**Métrica de Fisher por observação**, bloco-diagonal (a correlação entre e1 e e2 é ignorada, aproximação declarada):

- log σ: I = 2ν/(ν + 3);
- (a, log s1): I = E[x xᵀ]/s1² ⊕ 2;
- (b, log s2): I = E[x xᵀ]/s2² ⊕ 2.

O E[x xᵀ] vem dos regressores da janela.

**Velocidade.** Na data t, a janela [t − W, t) é dividida em duas metades consecutivas, A (mais antiga) e B (mais recente). O SF1-L é ajustado em cada uma, e a velocidade é

v(t) = √(Δθᵀ Ī Δθ), com Δθ = θ_B − θ_A e Ī a média das matrizes de Fisher de A e B.

- **v_fluxo** usa só os blocos do fluxo e da atividade. É a variável primária.
- **v_total** inclui o bloco do preço. É secundária.

| Escala | W (janela) | Metades | S (passo entre avaliações) |
| --- | --- | --- | --- |
| 1m | 1.440 barras (1 dia) | 720 | 60 barras (1 h) |
| 1h | 1.008 barras (6 semanas) | 504 | 24 barras (1 dia) |

## 3. Alvo e controles

- **Alvo:** Y(t) = |log(RV_seguinte / RV_anterior)|, em que RV é a volatilidade realizada nos S passos seguintes e nos S passos anteriores a t. É o tamanho da mudança de regime de volatilidade logo à frente.
- **Controles:**
    - log RV nos últimos S passos e nos últimos W;
    - |log(RV dos últimos S / RV dos S anteriores)|;
    - |Δ log σ| entre as metades A e B, que é a parte de volatilidade da velocidade;
    - hora do dia (em 1m) ou dia da semana (em 1h).

## 4. Teste primário

- **Estatística:** correlação de Spearman parcial. Os postos de v_fluxo e de Y são residualizados nos controles por mínimos quadrados, e mede-se a correlação dos resíduos.
- **p-valor:** permutação por **deslocamento circular** da série de resíduos de v_fluxo em relação à de Y, com 999 deslocamentos e deslocamento mínimo de W/S passos. Isso preserva a autocorrelação das duas séries. Teste **unilateral** (ρ > 0).
- **Decisão:** H-L2 é confirmada numa escala se p ≤ 0,025. A correção de Bonferroni cobre as duas escalas.

## 5. Dados

| Escala | Período confirmatório (nunca carregado) | Avaliações (aprox.) | Réplica prospectiva |
| --- | --- | --- | --- |
| 1m | 01/08/2026 a 30/09/2026 | ~1.440 | out–dez/2026, julgada à parte |
| 1h | 01/01/2025 a 30/09/2026 | ~610 | — |

Os dois períodos fazem parte do período reservado travado em 08/10/2026, que nenhuma rodada abriu até agora.

## 6. Etapas antes do confirmatório (nenhuma olha o alvo Y em dado real)

1. **Calibração sintética.**
    - Uma série SF1 estacionária deve dar p > 0,025: o teste não pode gerar falso positivo.
    - Uma série SF1 com regime oculto em que a curva de impacto muda **antes** de a volatilidade mudar deve dar p ≤ 0,025: o teste precisa ter poder.
    - Se não houver poder, o teste é declarado sem poder e o confirmatório não roda.
2. **Mensurabilidade nos dados de exploração** (1m de maio a julho de 2026; 1h de 2020 a 2024).
    - Medida: confiabilidade de v_fluxo entre amostras intercaladas (barras pares contra ímpares de cada metade), em postos. O mínimo é 0,5.
    - Se não atingir, W é ampliado **uma única vez** para 1,5× e depois 2× (a primeira que atingir).
    - Esta etapa não calcula Y.
3. **Congelamento** do código e dos parâmetros. Só então o período confirmatório é carregado.

## 7. Secundários (reportados, sem valor de decisão)

- v_total no lugar de v_fluxo.
- Alvo alternativo: o nível de RV seguinte, residualizado.
- Mudança seguinte da inclinação do impacto, |Δa1|.
- **Direção:** sinal do retorno nos S passos seguintes. O resultado esperado é nulo, e ele fica declarado para não ser procurado depois.

## 8. Auditoria de novidade (feita antes de afirmar qualquer novidade)

Não reivindicamos novidade de método. Os vizinhos mais próximos:

- **Detecção de mudança por divergência de Kullback–Leibler** (CUSUM e semelhantes). A velocidade de Fisher–Rao é a versão local disso, porque a divergência KL entre modelos vizinhos vale aproximadamente ½·ds².
- **Alerta precoce de transições críticas.** O "índice de informação de Fisher" é usado em sistemas ecológicos. Em mercados, há o trabalho de Gatfaoui e de Peretti (*Scientific Reports*, 2019), que usa oscilações na difusão de informação numa rede causal de índices. Não há Fisher–Rao nele.
- **Mudanças no fluxo de informação** medidas por entropia condicional, num sistema de alerta para mercados emergentes (arXiv:2404.03319).

O que talvez seja específico daqui é a combinação: a métrica canônica sobre um modelo de microestrutura com fluxo agressor, usada para antecipar mudança de regime de volatilidade além da própria volatilidade. Isso será conferido de novo antes de qualquer texto público.

## 9. Quem paga e por que continua pagando?

Ninguém paga diretamente: o uso é **defensivo**. Se H-L2 se confirmar, o valor está em reduzir a exposição do portfólio (tendência e carry) antes de mudanças de volatilidade, cortando perdas. A utilidade econômica seria um teste separado, com custos, depois da confirmação. A resposta fica registrada como fraca para fins de alfa.

## 10. Aposta do Claude (registrada antes de qualquer dado)

| Desfecho | Probabilidade |
| --- | --- |
| H-L2 confirmada em pelo menos uma escala | ~20% |
| Confirmada em 1m | ~15% |
| Confirmada em 1h | ~8% |

Raciocínio:

- A favor: há base teórica, porque fluxo informado e liquidações tendem a mudar a relação preço–fluxo antes da volatilidade.
- Contra: os controles são duros, já que a mudança recente de volatilidade e |Δ log σ| entram na regressão. Em 1h há poucas avaliações (~610). E o histórico do projeto é de zero sobreviventes prospectivos.

## 11. Revisão da Ana (09/10/2026): todos os pontos aprovados como propostos

1. Janelas: W = 1 dia com S = 1 h (1m); W = 6 semanas com S = 1 dia (1h). **Aprovado.**
2. Alvo primário: a mudança de regime de volatilidade. |Δa1| fica como secundário. **Aprovado.**
3. Correção de Bonferroni para as duas escalas, α = 0,025 em cada. **Aprovado.**
4. Execução depois do início do paper trading do portfólio. **Aprovado.** Depois substituído pela Emenda 1: execução autorizada com a cópia própria do `sgv_operavel`.
