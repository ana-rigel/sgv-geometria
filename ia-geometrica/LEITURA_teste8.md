# Leitura do teste 8 (a escada pela tensão) — REPROVADO em (a); (b) passou

**Predição:** PREDICAO_teste8_escada_pela_tensao.md (cdef51a), antes de rodar. **Resultado:** resultados_teste8.json. Um julgamento; sem emenda.

| mundo | recupera (razões em 7–13) | alguma razão fora | ganha da fixa (erro de leitura) | razões medianas | λ_j · τ_j (mediano) | erro: tensão / fixa / teste 4 |
|---|---|---|---|---|---|---|
| escada-2 | **1/100** | 99 | 15 | 4,6 | **0,82 · 1,79** | 1,063 / 1,011 / 0,686 |
| escada-3 | **4/100** | 96 | 32 | 4,8 · 5,0 | **0,73 · 1,50 · 2,91** | 1,014 / 1,021 / 0,691 |
| escada-4 | **1/100** | 99 | 33 | 5,1 · 4,9 · 11,0 | **0,66 · 1,30 · 2,50 · 1,44** | 1,000 / 1,024 / 0,691 |
| cíclico | 0/100 | **100** | **89** | 1,3 · 1,4 · 204 | — | 0,386 / 0,392 / 0,383 |

Critério: (a) razões em [7, 13] em ≥ 80 sementes por mundo-escada: **não** (1, 4, 1); (b) cíclico fora da progressão e melhor que a fixa em ≥ 80: **sim** (100 e 89). **Reprovado.** Apostas: 30 % em passar (certa a não-passagem); por mundo 55/50/40 % (certas as três não-passagens, isto é, erradas as apostas); cíclico 70 % (certa); λ·τ entre 0,2 e 5 em todos os andares (**certa**); erro de leitura maior que o do teste 4 nos mundos-escada (certa).

## O que o resultado diz

Comparado ao teste 4, o ajuste pela tensão fez a coisa que o ajuste pelo erro não fez: **pôs os andares nas constantes de tempo do mundo.** λ_j · τ_j ficou em 0,7–2,9 (no teste 4: 7, 3,7, 2,5, 0,0004); o primeiro andar caiu em λ₁ ≈ 0,12 para τ₁ = 7, não em 1,0. A escada pela tensão lê a escala absoluta do mundo. E, no mundo sem escada, amontoou três andares em torno de 1/300 e jogou o quarto para longe (razão 204): soube que não há escada, e ainda leu melhor que a fixa em 89 sementes.

O que ela não fez foi reproduzir a **razão** 10: achou ≈ 5 em todos os pares (exceto o último da escada-4, 11). O motivo é visível nos λ·τ, que crescem com o andar (0,7 → 1,5 → 2,9): os cortes são puxados uns para os outros. Dividir a potência em partes iguais com filtros de primeira ordem obriga cada fatia a roubar um pouco das vizinhas (o corte suave deixa vazar potência dos dois lados), e para equilibrar as fatias o ajuste aproxima os cortes. A escada que a tensão lê é a do mundo comprimida por um fator ≈ 2 na razão; a compressão é do instrumento (filtro de primeira ordem), não do mundo, e é a mesma suavidade de corte que fez o andar 2 errar no teste 6 (defeito 14).

Em erro de leitura, a escada pela tensão fica entre a fixa e a do teste 4, como previsto: ela otimiza outra coisa.

## O que fecha e o que não

- Fecha: o critério de razões em 7–13 não é atendido por este ajuste; e a escada b = 10 do projeto, quando lida pela tensão num mundo b = 10, aparece com b ≈ 5. Fecha também, pelo lado bom, que a tensão (e não o erro) é o critério que reencontra a **escala** do mundo: λ·τ de ordem 1 em todos os andares, pela primeira vez em oito testes.
- Não fecha: se a compressão da razão é exatamente a do corte suave (previsível a partir de |H|² e corrigível por construção), ou se tem outra origem. Um teste com filtros de corte mais abrupto (dois andares de primeira ordem em cascata por nível, ou a declaração com ganho real do teste 6 usada aqui como pesagem) responderia. Com predição própria.

## Para a lista de defeitos de desenho do projeto

18. Fatias de potência com filtros de primeira ordem vazam para os vizinhos: a razão lida é comprimida (≈ 5 para um mundo 10). Mesma raiz do defeito 14; o conserto é um só (ganho real do andar) e serve aos dois.

Oito testes, oito reprovações, dezoito defeitos. Leitura consolidada em LEITURA_v0.md.
