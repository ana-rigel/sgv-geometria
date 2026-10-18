# Predição do teste 21 (escada pela tensão: descorrelação entre fatias)

18/10/2026 · escrita antes de rodar · corrige o defeito 32 do teste 20, e só ele · último teste da linha da escada

## Pergunta

Os testes 8 e 20 mostraram que o critério "partes iguais de potência" põe o primeiro andar no corte do mundo mas comprime a razão (≈ 5–6 para um mundo 10), e que o critério, não só a ordem dos andares, empurra os cortes uns para os outros. **Ajustando os andares para que as fatias adjacentes sejam descorrelacionadas, a escada pela tensão reencontra a razão do mundo?**

## O critério de ajuste (declarado antes)

Fatias D₀ = x − R₁, D_j = R_j − R_{j+1} (andares de primeira ordem, os da v0). O ajuste escolhe λ minimizando a soma de |corr(D_j, D_{j+1})| sobre os k − 1 pares adjacentes (correlação média sobre as coordenadas, na calibração). Por que pode ler a razão: duas fatias adjacentes são correlacionadas quando os dois cortes estão perto demais (a mesma componente do mundo vaza nas duas); afastar os cortes descorrelaciona, e o critério não tem o viés das pontas do teste 8 (ele não pede que as fatias tenham a mesma potência). Por que pode não ler: com filtros de primeira ordem duas fatias adjacentes nunca são totalmente descorrelacionadas, e o mínimo pode ser atingido jogando um andar para fora da banda do mundo (λ → 10⁻⁴ ou → 0,99), o que "descorrelaciona" uma fatia esvaziando-a; para isso o ajuste parte da escada b = 10 em três partidas e fica a melhor, como antes, e a leitura olhará λ·τ para ver se foi isso.

## Mundos, instrumento e critério

Os dos testes 8 e 20 sem mudança: escada-2/3/4 e cíclico, N = 20.000, calibração [0, 10.000), 100 sementes, faixa λ ∈ [10⁻⁴, 0,99], Nelder–Mead com três partidas; critério (a) razões em [7, 13] em ≥ 80 por mundo-escada, (b) cíclico fora da progressão em ≥ 80 e ganha da fixa (b = 10, primeira ordem) em leitura em ≥ 80. Relata-se λ·τ, razões medianas, e a correlação residual mínima.

## Apostas

- **Passar: 30 %.** (a) por mundo: escada-2 50 %, escada-3 35 %, escada-4 25 %; (b): quebra 80 %, ganha da fixa 55 %.
- Razões medianas acima das do teste 8 em todos os mundos-escada (65 %); pelo menos um mundo com um andar jogado para fora da banda (λ·τ < 0,2 ou > 10) em ≥ 30 sementes (50 %).
- **Cláusula de fechamento, escrita antes:** reprovando (a), a linha da escada fecha com a conclusão "a escada do mundo é legível pela tensão em escala, não em razão", e a v0 fica com b lido do mundo só no primeiro andar.

## O que fecha

Passar: a razão é legível pela tensão com o critério certo, e a auto-similaridade da v0 pode ser lida do mundo inteira. Reprovar: a cláusula acima; a razão fica como propriedade do modelo (como o b único do MSM), declarada.
