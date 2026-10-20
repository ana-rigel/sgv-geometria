# Predição do teste 35 (o relógio v2: a organização sabe quando)

20/10/2026 · escrita antes de rodar · instrumento v0.py (andar 1) sem mudança; laço do ano semeado como em teste33.py, congelado · Ana Rigel

## De onde vem

Do Experimento 1 do Teste B (conversa "SGV - Campo informacional - Testes", 17/10): uma organização com relógio, que não sabe **para onde** o mundo vai, só **quando**. Reprovou, e depois se achou um defeito de instrumento: o relógio zerava no passo do salto antes de a janela ser avaliada. O registro ficou: *o que foi testado é um relógio que se desarma ao tocar*. A v2 ficou pendente, com predição nova.

Da conversa de 20/10 vêm mais três coisas. (1) A v0 não tem fase própria: os andares só relaxam, e entre eles a coerência de fase é a de uma hélice congelada (C ≈ 0,21). Fase própria exige um oscilador. (2) No modelo da NGC 628, uma organização lenta que nasce vazia não aprende a tempo; semeada, segura (a lição do teste 33). (3) A frase original dos três corpos, "se seguem sem se colar", que tem uma forma operacional num relógio acoplado ao mundo.

## O relógio

Um oscilador de fase φ que **nunca se reinicia** (o defeito da v1 some por construção), com frequência natural ω = 2π/365,25 por dia e acoplado à fase que o mundo mostra:

  φ(t) = φ(t−1) + ω + K · sen(θ_obs(t) − φ(t−1)),  φ(início) = ω · t_início.

- **Entrada:** o andar 1 da v0 (λ₁ = 0,15) lendo os três sensores do cubo (água no solo 28–100 cm, chuva − ET0 em 7 dias, VPD), padronizados pela média e desvio de 2010–2017 de cada lugar.
- **O laço do ano, semeado e congelado:** por eixo, mínimos quadrados de 2010–2017 sobre a saída do andar 1, com a base do teste 32 (1, sen/cos de 1 e 2 ciclos por ano, t em dias desde 1970). Fica fixo depois.
- **A fase que o mundo mostra:** θ_obs(t) = atan2(v_s, v_c), com (v_c, v_s) = pinv([b_cos b_sen]) · (R₁(t) − b₀), usando só o 1º harmônico do laço. No ano médio, θ_obs = ωt. O 2º harmônico entra como uma oscilação de fase que se repete todo ano e é absorvida pela calibração de φ_entrada abaixo.
- **K = 0 é o calendário:** o relógio bate sozinho, φ = ωt, e prevê sempre a data média. **K grande gruda no mundo:** φ ≈ θ_obs. Entre os dois, ele se segue sem se colar.

Grade: K ∈ {0; 0,001; 0,002; 0,005; 0,01; 0,02; 0,03; 0,05; 0,07; 0,1; 0,2; 0,5} rad/dia, fina entre 0,01 e 0,1, onde a conta prévia põe o ótimo (defeito 46).

## O alvo: a entrada das águas

Por ano e lugar, a **entrada das águas** é o primeiro dia d a partir de 1º de agosto com chuva somada de d a d+4 ≥ 25 mm e sem nenhuma sequência de ≥ 10 dias seguidos com chuva < 1 mm entre d+1 e d+30. Sem entrada até 31/12, o ano fica fora e é relatado. A régua é fixa: erro absoluto em dias, igual em todos os anos e lugares.

**Previsão:** em t₀ = 1º de setembro de cada ano, entrada prevista = t₀ + ((φ_entrada − φ(t₀)) mod 2π) / ω. φ_entrada é a média circular da fase do relógio nos dias de entrada de 2010–2017, por lugar e por K. Com K = 0, isso dá a data média de entrada da calibração: o nulo do calendário sai do próprio relógio.

## Lugares, períodos, escolha de K

Juara e os cinco de MT dos testes 31–33 (Sinop, Cuiabá, Barra do Garças, Alta Floresta, Rondonópolis). Calibração 2010–2017; medida 2018–2025, ou seja, até 6 × 8 = 48 previsões. **K\*** é escolhido uma vez, com todos os lugares juntos, pelo menor erro absoluto médio (EAM) das previsões de 2010–2017. Intervalos por bootstrap das previsões lugar-ano da medida (1.000, semente 35), pareado entre K\* e K = 0.

## Conta prévia (sem olhar nenhuma data de entrada)

1. Na literatura do Brasil central, a data de entrada varia entre anos com desvio de 2 a 3 semanas. O calendário deve errar 10–20 dias em média.
2. O relógio só ganha se, em 1º de setembro, o estado da estação seca (solo, balanço e VPD vistos pelo andar 1) estiver adiantado ou atrasado de um jeito que anuncie a entrada. Há um mecanismo conhecido, mas fraco: estação seca mais seca e mais longa, entrada mais tarde (retroalimentação entre solo e atmosfera). Espero, no máximo, poucos dias de ganho.
3. O ótimo de K é o de um PLL: 1/K da ordem do tempo em que uma anomalia de fase da estação persiste, de 1 a 2 meses. Então K\* entre 0,02 e 0,05.
4. **Risco de clima deslocado (defeito 44):** 2018–2025 foi mais seco que 2010–2017 em MT. Se a entrada vier sistematicamente mais tarde na medida, um relógio que lê atraso de fase pode ganhar por acompanhar a tendência, e não por antecipar cada ano. Relato o erro médio com sinal (viés) do calendário e do relógio, além do EAM.
5. **Isto não é o Kuramoto da galáxia.** Com um único relógio acoplado ao mundo, um K ótimo no meio é o compromisso de banda de um PLL (seguir sem copiar o ruído). Os relógios acoplados entre si, que fariam a crítica de K_c, ficam para depois.

## Critérios

**J1, o relógio antecipa melhor que o calendário:** EAM(K\*) − EAM(K = 0) ≤ **−3 dias** na medida, com o limite superior do IC 95 % **abaixo de 0**.

**J2, seguir sem se colar:** na medida, a curva EAM(K) tem o mínimo num K **interior** da grade (nem 0, nem 0,5), e esse mínimo fica **≥ 2 dias** abaixo do menor entre EAM(0) e EAM(0,5).

Relatado: K\*; EAM e viés por lugar; o número de anos sem entrada; a correlação, na medida, entre a anomalia de fase do relógio em 1º de setembro (em dias, φ(t₀) − ωt₀, com K\*) e a anomalia da entrada; o desvio-padrão das entradas; as previsões feitas em 15/08 e 15/09.

## Apostas (Claude, antes de rodar)

- **J1 passa: 25 %.** O mecanismo físico existe, mas é fraco, e são 48 previsões.
- **J2 passa: 30 %.** Mesmo que haja um ótimo interior, 2 dias de margem sobre os dois extremos é pedir muito com essa amostra.
- **A correlação entre a fase em 1º/09 e a entrada é positiva e ≥ 0,3 (atraso anuncia atraso): 40 %.**
- **O EAM do calendário fica entre 10 e 20 dias: 60 %.**

## O que fecha

- **J1 e J2 passam:** um relógio que se segue sem se colar antecipa a entrada das águas, e o ótimo não é nem o calendário nem o mundo cru. É a primeira função da organização ⋄ que a v0 crua não tem.
- **J1 passa, J2 reprova:** o relógio ajuda, mas o melhor é grudar no mundo (ou o ganho não depende do K). Então quem antecipa é o estado de 1º de setembro, e a fase própria não acrescenta nada.
- **J1 reprova:** em MT, a fase da estação seca em 1º de setembro não anuncia a entrada das águas além do calendário. O relógio fica sem alvo de previsão aqui. O que sobra para ele é o papel da v1: abrir a plasticidade da memória na hora certa, que é outro teste.

Um julgamento por hipótese; sem emenda. Instrumento: teste35.py, escrito depois do commit desta predição.
