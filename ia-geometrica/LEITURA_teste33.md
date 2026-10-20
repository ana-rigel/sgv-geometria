# Leitura do teste 33 (a organização nasce sabendo o clima): portão OK; J1 e J2 REPROVADOS. Onde perde, perde pela memória; aprender custa pouco, onde custa

**Predição:** PREDICAO_teste33_organizacao_semeada.md (dc46977), antes de rodar. **Instrumento:** teste33.py. **Resultado:** resultados_teste33.json. Portão e dois julgamentos; sem emenda.

AUC dentro de cada mês, medida 2019–2025:

| lugar | ⋄ semeada | ⋄ semeada congelada | SPEI-90 | ⋄ fria | v0 crua | v0 clim. fixa | calendário |
|---|---|---|---|---|---|---|---|
| Sinop | 0,665 | 0,687 | 0,728 | 0,615 | 0,662 | 0,688 | 0,514 |
| Cuiabá | 0,918 | 0,951 | 0,876 | 0,782 | 0,943 | 0,950 | 0,519 |
| Barra do Garças | 0,598 | 0,626 | 0,672 | 0,564 | 0,634 | 0,632 | 0,522 |
| Alta Floresta | 0,715 | 0,699 | 0,715 | 0,718 | 0,652 | 0,718 | 0,448 |
| Rondonópolis | 0,958 | 0,940 | 0,932 | 0,908 | 0,926 | 0,947 | 0,512 |
| *Juara (relatado)* | 0,796 | 0,812 | 0,813 | 0,748 | 0,752 | 0,819 | 0,445 |

| lugar | J1: semeada − SPEI (IC 95 %) | J2: semeada − congelada (IC 95 %) | normal de chuva − ET0: semente → fim de 2025 (mm/d) |
|---|---|---|---|
| Sinop | −0,063 (−0,157; +0,011) | −0,022 (−0,072; +0,024) | +0,82 → +0,31 |
| Cuiabá | **+0,042** (−0,006; +0,097) | −0,032 (−0,127; +0,006) | −0,23 → −0,86 |
| Barra do Garças | −0,074 (−0,239; +0,058) | −0,028 (−0,079; +0,017) | −0,82 → −1,22 |
| Alta Floresta | **0,000** (−0,073; +0,063) | **+0,016** (−0,003; +0,041) | +0,98 → +0,70 |
| Rondonópolis | **+0,027** (−0,029; +0,084) | **+0,019** (−0,006; +0,063) | −0,64 → −1,16 |
| *Juara* | −0,018 (−0,139; +0,065) | −0,016 (−0,049; +0,016) | +0,82 → +0,29 |

**Portão:** o calendário ficou entre 0,445 e 0,522 nos cinco lugares. A métrica por mês removeu o prêmio do calendário. **OK.**
**J1, a placa semeada empata com o SPEI-90:** **3 de 5** (Cuiabá, Alta Floresta, Rondonópolis). **Reprovado.**
**J2, aprender depois de semeada não atrapalha:** **2 de 5** (Alta Floresta, Rondonópolis). Sinop, Cuiabá e Barra do Garças ficaram entre −0,022 e −0,032, logo além do limite de −0,02. **Reprovado.**

Apostas: portão passa (85 %), certa; J1 passa (55 %), errada; J2 reprova (65 %), certa, e nos lugares que a conta prévia apontou (Cuiabá e Barra do Garças, mas não Rondonópolis); v0 crua abaixo da ⋄ fria em ≥ 4 de 5 (70 %), **errada: 1 de 5**.

Verificação: a ⋄ semeada deu, na AUC comum, os mesmos números da ⋄ morna do teste 32 (0,590; 0,891; 0,579; 0,673; 0,827). Isso era esperado, porque semear com mínimos quadrados de 2010–2017 equivale a ter aprendido desde 2010. As duas implementações concordam.

## O que o resultado diz

**1. Onde a placa perde do SPEI, perde pela memória, não pela organização.** Em Sinop e Barra do Garças, todas as séries que passam pelo R2 ficam abaixo do SPEI-90, inclusive a semeada congelada (−0,041 e −0,046) e a v0 com a climatologia de 365 dias (−0,040 e −0,040). A organização semeada não é a causa, porque mesmo a referência perfeita de 2010–2017 perde ali. A média exponencial de τ ≈ 67 dias e a soma reta de 90 dias pesam o passado de forma diferente, e nesses dois solos a janela reta segue melhor. Esse é o terceiro ramo do "o que fecha": a pergunta volta para os andares. Em Cuiabá e Rondonópolis é o contrário: a memória da v0 passa o SPEI por 0,03–0,08.

**2. Aprender o normal custa pouco, e não custa em todo lugar.** Onde o clima mais secou em relação a 2010–2017, a organização que continua aprendendo perdeu 0,02–0,03 para a congelada. Ela moveu metade do caminho até o normal seco (Cuiabá −0,23 → −0,86) e passou a chamar de normal uma parte da seca. Em Alta Floresta e Rondonópolis, aprender **ajudou** um pouco (+0,016 e +0,019), mesmo com Rondonópolis tendo secado tanto quanto Cuiabá. A conta prévia acertou o sinal em três lugares e errou em um. Nenhum intervalo exclui o zero. É um custo pequeno e incerto, não uma condenação do aprendizado.

**3. A aposta errada ensina mais que as certas.** Com a AUC por mês, a v0 **crua** ficou praticamente igual à v0 com a climatologia fixa (Cuiabá 0,943 contra 0,950; Rondonópolis 0,926 contra 0,947) e acima da ⋄ fria em quatro lugares. A razão é aritmética: dentro de um mesmo mês, a estação é quase constante, então ordenar os dias pelo valor cru é o mesmo que ordená-los pela anomalia contra um normal fixo. **A métrica por mês tira o calendário de todas as séries ao mesmo tempo**, inclusive da crua. Com ela, o trabalho da organização (tirar o ano) não vale nada. O que vale é não mover a referência, e a crua nunca move a sua.

## O que fica para a organização ⋄

- Comparar pelo **ranking** dos dias não mede o valor de tirar o ano. Esse valor aparece quando há **um limiar fixo**, que é a régua: núcleo, transição e ruptura com os mesmos números em janeiro e em setembro. É aí que a v0 crua daria falso alarme na seca de todo ano e a organização evitaria. O teste certo para a ⋄ é um alarme na régua ao longo do ano, não uma AUC.
- **Semear com 5 números e congelar** fica a menos de 0,01 da climatologia de 365 dias em cinco dos seis lugares (Sinop −0,001, Cuiabá +0,001, Barra −0,006, Rondonópolis −0,007, Juara −0,007). A exceção é Alta Floresta, com −0,019. Na maior parte de MT, 5 coeficientes guardam o normal do lugar quase tão bem quanto 365 médias.
- **Aprender depois de semeada** é um ajuste fino de sinal incerto. Com uma verdade ancorada no clima antigo, ele custa até 0,03 onde o clima mudou.

## Para a lista de defeitos de desenho

45. A AUC por mês foi escolhida para tirar o prêmio do calendário da v0 crua. Mas ela tira o calendário de **todas** as séries, e com isso apaga a única coisa que a organização faz: tirar o ano. O J1 virou um teste da memória e da referência, não da organização. Uma conta de uma linha (dentro do mês, o valor cru e a anomalia contra um normal fixo têm a mesma ordem) teria mostrado isso antes. O valor da ⋄ só se mede com um limiar fixo ao longo do ano.

Placar: 33 testes numerados (o 25 sem resultado). 26, 28, 31: J1 passou, J2 reprovou; 27, 29, 30, 32, 33: ambos reprovaram. 45 defeitos, 1 emenda.
