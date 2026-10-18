# Leitura do teste 21 (descorrelação entre fatias) — REPROVADO; a linha da escada fecha pela cláusula

**Predição:** PREDICAO_teste21_descorrelacao.md (d8a47e2), antes de rodar. **Resultado:** resultados_teste21.json. Um julgamento; sem emenda.

| mundo | recupera | ganha da fixa | razões medianas | λ_j · τ_j | sementes com andar fora da banda (λ·τ < 0,2 ou > 10) | correlação residual mediana |
|---|---|---|---|---|---|---|
| escada-2 | 3/100 | 0 | 74,8 | 0,05 · 0,01 | **100** | 0,016 |
| escada-3 | 0/100 | 3 | 63,1 · 12,4 | 0,55 · 0,09 · 0,07 | **100** | 0,096 |
| escada-4 | 0/100 | 56 | 29 · 14,5 · 2,0 | 1,23 · 0,42 · 0,15 · 0,70 | 54 | 0,266 |
| cíclico | 0/100 | 13 | 313 · 3,1 · 1,1 | — | — | — |

Critério: (a) **não** (3, 0, 0); (b) quebra sim (100), ganha da fixa **não** (13). **Reprovado nos dois.** Apostas: 30 % em passar (certa a não-passagem); razões acima das do teste 8 em todos os mundos (certa, pelo motivo errado); "pelo menos um mundo com um andar jogado para fora da banda em ≥ 30 sementes" (certa: dois mundos em 100 de 100, um em 54).

**Cláusula de fechamento, escrita antes:** reprovando (a), a linha da escada fecha.

## O que o resultado diz

O modo de falha que a predição nomeou foi exatamente o que aconteceu: o ajuste descorrelaciona as fatias **esvaziando-as**. Na escada-2 e na escada-3, em todas as sementes, pelo menos um andar foi parar muito abaixo da banda do mundo (λ·τ 0,01–0,09): uma fatia quase sem potência é quase descorrelacionada de qualquer outra, e a correlação residual chegou a 0,016. As "razões" de 75 e 63 não são leitura do mundo; são a distância entre um andar que ficou e um que fugiu. Na escada-4 o ajuste não achou como esvaziar sem perder o objetivo (correlação residual 0,27) e as razões saíram desordenadas (29 · 14,5 · 2,0). No cíclico, pela primeira vez em três testes de escada, o ajustado **perdeu** da fixa (13 de 100), porque jogou andares para fora da banda da senoide.

Três critérios de ajuste pela tensão, três resultados: pelo erro de predição (teste 4), a escada da predição; por partes iguais de potência (8, 20), a escala certa e a razão comprimida; por descorrelação (21), andares esvaziados. Nenhum lê a razão. A escala do mundo, no primeiro andar, apareceu em todos os de tensão (λ₁·τ₁ entre 0,55 e 1,23) e é o que fica.

## O que fecha, pela cláusula

**A escada do mundo é legível pela tensão em escala, não em razão.** A v0 pode perguntar ao mundo onde está a sua escala mais rápida (e acerta, teste 8 e 20: λ₁·τ₁ ≈ 1) e se há escada ou não (cíclico quebra a progressão em 100 de 100 nos três testes). A razão entre andares fica como propriedade declarada do modelo, como o b único do MSM, não como leitura; a auto-similaridade da v0 é, nesse ponto, projeção dela, e isso está escrito desde o projeto ("no seu limite").

## Para a lista de defeitos de desenho do projeto

33. Critério de descorrelação sem penalidade para fatias vazias: tem mínimo trivial. Nomeado antes; não corrigido, porque a cláusula fecha a linha.

Vinte e um testes, dezenove reprovações, duas passagens, trinta e três defeitos. Três linhas fechadas por cláusula ou veredito (máquina, política, escada); uma de pé com número (declaração e régua sobre outro observador).
