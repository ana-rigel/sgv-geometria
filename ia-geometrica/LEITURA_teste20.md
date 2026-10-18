# Leitura do teste 20 (escada pela tensão, andares de segunda ordem) — REPROVADO

**Predição:** PREDICAO_teste20_andares_abruptos.md (da684a5), antes de rodar. **Resultado:** resultados_teste20.json. Um julgamento; sem emenda.

| mundo | recupera (razões em 7–13) | ganha da fixa (2ª ordem) | razões medianas (teste 8, 1ª ordem) | λ_j · τ_j |
|---|---|---|---|---|
| escada-2 | 9/100 | 13 | **36,8** (4,6) | 0,81 · 0,17 |
| escada-3 | 2/100 | 44 | **5,5 · 6,1** (4,8 · 5,0) | 0,91 · 1,55 · 2,18 |
| escada-4 | 0/100 | 59 | **4,5 · 4,3 · 52,9** (5,1 · 4,9 · 11,0) | 1,08 · 2,35 · 5,24 · 0,71 |
| cíclico | 0/100 | **79** | 1,2 · 1,2 · 412 (1,3 · 1,4 · 204) | — |

Critério: (a) razões em [7, 13] em ≥ 80 por mundo-escada: **não**; (b) cíclico fora da progressão em ≥ 80 (sim, 100) **e** ganha da fixa em ≥ 80: **não** (79). **Reprovado nos dois.** Apostas: 35 % em passar (certa a não-passagem); razões medianas entre 6 e 9 (errada: 5,5–6,1 na escada-3, 4,3–4,5 na escada-4, e 36,8 na escada-2); cíclico quebra (certa) e ganha da fixa (errada, por uma semente); (a) por mundo 45/35/25 (certas as três não-passagens).

## O que o resultado diz

A ordem do andar não era a causa, ou não era a causa toda. Na escada-3 a razão subiu de 4,9 para 5,8: um quinto do caminho até 10, não a metade que a predição esperava se a compressão fosse só vazamento. Na escada-4 as duas primeiras razões **caíram** (4,5 e 4,3) e a última disparou (53): com andares abruptos o ajuste achou outra solução, três fatias apertadas e uma solta. Na escada-2 o mesmo, em extremo: λ₂ foi para 0,0024 num mundo de τ₂ = 70 (λ·τ 0,17), isto é, o segundo andar foi parar muito abaixo da escala do mundo, e a razão deu 37. O critério "partes iguais de potência" tem mais de um mínimo quando as fatias são abruptas, e a bissecção por três partidas cai em qualquer um.

O que fica de pé do teste 8 fica aqui também: o primeiro andar cai no corte do mundo (λ₁·τ₁ 0,8–1,1 em todos), e no cíclico a progressão quebra. O que não fica: a leitura da **razão**. A compressão é, em parte, do critério de ajuste: dividir a potência em partes iguais não é o mesmo que pôr um corte entre cada par de escalas quando as componentes têm variância igual e cortes com transição; o ajuste prefere cortes mais próximos porque as fatias extremas (a mais rápida e a mais lenta) recebem potência de uma só vizinha e as do meio de duas. O defeito 18 estava meio diagnosticado: o vazamento existe, mas o critério também empurra.

## O que fecha e o que não

- Fecha: trocar a ordem dos andares não lê a razão do mundo; o diagnóstico "vazamento de primeira ordem" do teste 8 era incompleto.
- Não fecha: outro critério de ajuste pela tensão, a **descorrelação entre fatias adjacentes** (minimizar |corr(D_j, D_{j+1})|), que não premia fatias de potência igual e por isso não deveria puxar os cortes uns para os outros. É o próximo e último teste desta linha, com predição própria. Se também não ler a razão, a conclusão é que a escada do mundo é legível em **escala** pela tensão (o que já se sustenta) e não em **razão**, e a v0 fica com isso.

## Para a lista de defeitos de desenho do projeto

32. Diagnóstico do defeito 18 incompleto: a compressão da razão vem também do critério de partes iguais, não só do vazamento; e esse critério tem vários mínimos com andares abruptos.

Vinte testes, dezoito reprovações, duas passagens, trinta e dois defeitos.
