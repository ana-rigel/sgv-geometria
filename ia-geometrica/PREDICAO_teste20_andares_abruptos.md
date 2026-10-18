# Predição do teste 20 (escada pela tensão com andares de segunda ordem)

18/10/2026 · escrita antes de rodar · corrige o defeito 18 do teste 8, e só ele

## Pergunta

No teste 8 a escada ajustada pela tensão caiu nas constantes de tempo do mundo (λ·τ ≈ 1) mas leu razão ≈ 5 num mundo de razão 10, porque as fatias de primeira ordem vazam para as vizinhas. **Com andares de corte mais abrupto (cada andar = duas EMAs de mesmo λ em cascata, segunda ordem), a escada pela tensão reencontra a razão do mundo?**

## O que muda e o que não muda

- **Andar de segunda ordem:** R_j = EMA_λj(EMA_λj(R_{j−1})); ganho |H_j|⁴ em vez de |H_j|²; a transição cai duas vezes mais rápido em dB por década. Nada mais na arquitetura muda: a mesma escada, a mesma tensão D_j = R_j − R_{j+1}, o mesmo ajuste (desvio-padrão de log Var(D_j) mínimo), a mesma faixa λ ∈ [10⁻⁴, 0,99], as mesmas três partidas.
- **Nulo:** a escada fixa de segunda ordem com λ₁ = 0,15, b = 10 (o nulo tem a mesma ordem que o ajustado; o teste é da razão, não da ordem).
- **Tudo o mais igual ao teste 8:** escada-2/3/4 (τ 7, 70, 700, 7.000; k = número de escalas), cíclico (k = 4); N = 20.000; calibração [0, 10.000); 100 sementes; leitura por mínimos quadrados com ridge sobre os registros R_{t−1} para "ganha da fixa".

## Critério (um julgamento)

O do teste 8: (a) razões em [7, 13] em ≥ 80 sementes em cada mundo-escada; (b) no cíclico, alguma razão fora de [7, 13] em ≥ 80 **e** o ajustado ganha da fixa em erro de leitura em ≥ 80. Relata-se λ_j · τ_j (com a nota de que o corte de segunda ordem para o mesmo λ fica em ≈ 0,64 do corte de primeira ordem, logo λ·τ ≈ 1,5 é "no corte certo") e as razões medianas.

## Apostas

- **Passar: 35 %.** A favor: o vazamento entre fatias cai com a ordem; se a compressão do teste 8 (≈ 2 na razão) for toda do vazamento, a segunda ordem deve reduzi-la a ≈ 1,4, o que leva as razões medianas de 5 para 7 e deixa o critério na borda. Contra: é exatamente a borda; e os cortes de segunda ordem têm mais atraso, o que não afeta as fatias de potência mas afeta a leitura (b).
- Razões medianas entre 6 e 9 nos mundos-escada (60 %): melhora e não chega.
- Cíclico: quebra em ≥ 80 (85 %); ganha da fixa em ≥ 80 (60 %).
- (a) passa na escada-2 (45 %), escada-3 (35 %), escada-4 (25 %).

## O que fecha

Passar: a razão do mundo é legível pela tensão com andares abruptos, e a escada da v0 pode ser lida do mundo em escala **e** razão. Reprovar com razões entre 6 e 9: a compressão não é só vazamento de primeira ordem; parte é da própria divisão em partes iguais, e o próximo passo é outro critério de ajuste (descorrelação entre fatias), não outra ordem. Reprovar sem melhora: a ordem não é a causa, e o defeito 18 está mal diagnosticado.
