# Predição do teste 49 (a geometria da janela contra as velocidades de padrão medidas na NGC 628)

20/10/2026 · escrita antes de calcular · teoria contínua dos testes 46–47 · dados: Speights, Aust & Lu (2025), ApJ 981, 115 · Ana Rigel

## De onde vem

O teste 47 e a figura da geometria da janela mostraram que, no modelo de anéis, a sincronização parcial divide a zona estável (254″–395″) em duas partes: os anéis externos travam num padrão m = 5 que gira rígido, e os internos deslizam. A leitura do teste 48 deixou como teste seguinte o confronto com as velocidades de padrão Ωp(r) medidas por Speights et al. (2025), que, segundo o colaborador, indicariam o oposto. A Ana anexou o artigo.

## O que o artigo cobre (lido antes de escrever esta predição)

- **Escala:** D = 7,0 Mpc, 34,2 pc/″; inclinação adotada 6,0°, PA 21,8°.
- **O "rígido por dentro, cisalhando por fora" do artigo é outra escala.** O disco rígido deles é o interno, até ≈ 4 kpc (corrotação em 3,4 kpc, Ωp ≈ 61 km/s/kpc, dominado por dois braços m = 2). O cisalhamento é de ≈ 4 kpc para fora. A nossa zona começa em 254″ = **8,7 kpc**. O artigo não contradiz o modelo na escala do modelo; os dois falam de regiões diferentes.
- **A cobertura na nossa zona é parcial.** O perfil radial mais detalhado (modelo PCM, Figura 12) para o H I vai até r_max = **310″ = 10,6 kpc** (Tabela 4), cortado em R25 de propósito para evitar o warp; os anéis além de r_max foram excluídos da figura. A sobreposição com a nossa zona é **254″–310″**, os 40 % internos (em raio) da zona. A parte que o modelo prevê rígida (a externa) **não é coberta**. O que o artigo pode testar é a parte interna, onde o modelo prevê deslizamento (e uma faixa de K da janela).
- **As figuras são imagens (JPEG), não vetores.** Os pontos terão de ser digitalizados por cor, com erro de leitura.
- **Já vi as figuras e o texto.** A Figura 12d (Ωp do H I, PCM, com Ω sobreposto) e a frase da seção 5.3.2 ("as tendências... semelhantes às de Ω na forma, mas tipicamente menores que Ω nos valores") foram vistas antes desta predição. Os julgamentos J1 e J3, sobre os dados, **não são cegos**; o J2, sobre o modelo, é; o J4 é meio cego (vi a figura, não medi a diferença).

## Diferença de representação (vale para todos os julgamentos)

O modelo trata as fases m = 5 de anéis; a velocidade de padrão de um anel é a taxa da sua fase dividida por m. Speights et al. medem Ωp pela equação de continuidade sobre a intensidade do H I, sem separar m (o m = 2 domina para além de ≈ 8 kpc no infravermelho). Um acordo ou desacordo aqui é com o padrão total do H I, não com o m = 5. A frequência natural de cada anel no modelo é a velocidade material (sem acoplamento, o padrão cisalha com o material); essa é a hipótese que o modelo põe.

## O que o modelo prevê para a velocidade de padrão

No estado parcialmente travado (frequências relativas, Ω_c a frequência do aglomerado, a = Kρ):

- anel travado: velocidade de padrão = Ω_c/m, a mesma para todos (rígido);
- anel que desliza, d = Δω − Ω_c: frequência média Ω_c + sgn(d)·√(d² − a²). Ela tem a forma da material, mas puxada para o aglomerado. Como o aglomerado está do lado externo (frequências mais baixas), os anéis internos que deslizam giram **mais devagar que o material**, e o atraso d − √(d² − a²) **cresce para fora**, chegando a a na borda r\*.

Assinaturas, na sobreposição 254″–310″, se ela inteira desliza:

| | modelo (deslizando, puxado para o aglomerado externo) | onda rígida única com corrotação dentro | padrão material puro |
|---|---|---|---|
| Ωp(r) | cai como Ω | constante | = Ω |
| Ω − Ωp | > 0, **cresce para fora** | > 0, **diminui para fora** | 0 |

Ordem de grandeza: na curva plana, no começo da janela (K ≈ 0,89 K_c, ρ ≈ 0,39), a ≈ 0,22 da abertura de frequências da zona. Com v ≈ 200 km/s, Ω vai de ≈ 23 a ≈ 15 km/s/kpc na zona, e o atraso máximo seria ≈ 1,8 km/s/kpc (≈ 10 % de Ω) em r\*. É pequeno diante das barras de erro do PCM; só o sinal e a tendência dos valores centrais podem ser julgados.

## O cálculo

**Dados (digitalizados da Figura 12d, H I):** os centros dos marcadores vermelhos de Ωp e a curva pontilhada preta de Ω, calibrados pelos traços dos eixos (0–10 kpc; 0–100 km/s/kpc). Raio convertido para segundos de arco por 34,2 pc/″. Na sobreposição (8,69–10,60 kpc):

- S = (queda de Ωp)/(queda de Ω), pelas inclinações de retas ajustadas aos valores centrais;
- a fração dos pontos com Ωp < Ω (Ω interpolado no raio de cada ponto);
- a inclinação da reta de Ω − Ωp contra r.

Calibração e máscaras de cor registradas no instrumento; um sobreposto dos pontos digitalizados sobre a figura é salvo para conferência visual.

**Modelo:** curva plana em 254″–395″ (β = 0, 400 anéis, a referência), e, como relato, a curva publicada de Aniyan et al. (254″–350″, inclinação fixa; a do teste 48). Ao longo da janela (do K com metade travada até K_L, passo 0,0025 K_c), o solver do teste 46 dá Ω_c, a e os anéis travados. Daí: o r\* em função de K, a fração da janela em que nenhum anel de 254″–310″ está travado, e o perfil de velocidade de padrão (atraso e S na sobreposição).

## Conta prévia

Na curva plana com r uniforme, metade travada no começo da janela significa r\* ≈ 324″, então a sobreposição inteira desliza no começo. Ela continua inteira deslizando enquanto a fração travada for ≤ (395 − 310)/(395 − 254) ≈ 0,60. Se a fração travada subir linearmente de 0,5 a 1 ao longo da janela, isso é o primeiro **≈ 20 %** da janela; se subir devagar no começo, um pouco mais. Na curva de Aniyan cortada em 350″, a condição seria fração travada ≤ 0,42, abaixo do começo da janela: nenhuma parte da janela seria compatível (mas aquela zona é cortada pelos dados, não pela física).

## Critérios

**J1, a sobreposição cisalha:** S ≥ **0,5** (Ωp cai pelo menos metade do que Ω cai em 254″–310″).

**J2, os dados restringem K à parte baixa da janela:** na curva plana, a faixa de K em que nenhum anel de 254″–310″ está travado é ≤ **1/3** da largura da janela.

**J3, o padrão gira mais devagar que o material:** Ωp < Ω em **≥ 80 %** dos pontos da sobreposição (valores centrais).

**J4, o atraso cresce para fora (a assinatura própria do modelo):** a reta de Ω − Ωp contra r na sobreposição tem inclinação **> 0**.

Relatado sem critério: o r\* ao longo da janela; o atraso e o S previstos pelo modelo na sobreposição no começo da janela; os mesmos números com a curva de Aniyan; Ωp e Ω digitalizados.

## Apostas (Claude, antes de calcular)

- **J1: 85 %** (não cego: a Figura 12d foi vista).
- **J2: 60 %.**
- **J3: 70 %** (não cego: o texto do artigo diz "tipicamente menores").
- **J4: 35 %.** Na figura, Ωp e Ω parecem se aproximar perto de 10,5 kpc, o que daria inclinação negativa; mas a borda r_max é onde o PCM é menos confiável.

## O que fecha

- **J1 e J2 passam:** o artigo é compatível com o modelo só na parte baixa da janela (a sobreposição inteira deslizando); a parte da zona que o modelo prevê rígida continua sem medida, e o teste decisivo exige Ωp além de 310″ (o H I vai até 28 kpc, mas o PCM foi cortado em R25 por causa do warp).
- **J1 reprova:** a sobreposição é rígida; o modelo só a acomoda com parte dela travada (K mais alto na janela), e o lado rígido teria de começar dentro de 310″.
- **J3 e J4 passam:** os dados mostram a assinatura do aglomerado externo puxando os anéis internos; nem uma onda rígida única nem o padrão material puro dão os dois.
- **J3 passa e J4 reprova:** o atraso existe mas não tem a forma do modelo; o "menor que Ω" de Speights et al. é explicado igualmente por ondas sobrepostas ou por uma onda com corrotação mais para dentro.

Um julgamento por hipótese; sem emenda. Instrumento: teste49.py, escrito depois do commit desta predição.
