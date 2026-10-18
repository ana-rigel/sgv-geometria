# Predição do teste 5 (a régua de cegueira): desenho

18/10/2026 · desenho escrito antes de qualquer código · não rodado · depende de autorização da Ana

## Por que este teste e não os quatro anteriores

Os testes 1–4 perguntaram se a v0 rastreia, decide, detecta e ajusta melhor que um filtro. Reprovou nos quatro. Nenhum perguntou a única coisa que a distingue de um filtro por construção: **ela declara, por andar, o que não vê.** Um filtro de Kalman também não vê acima da sua banda, mas não diz isso a ninguém. A pergunta do OBS-01 é se um observador pode medir o próprio ponto cego e se essa medida serve a quem o lê. Este teste é essa pergunta em mundo sintético, onde a cegueira real é calculável. Duas hipóteses, dois julgamentos.

## As duas grandezas

**Cegueira declarada δ̂_j (de dentro).** O que a v0 publica hoje (`v0.cegueira`): para o andar j, a fração da potência da sua própria tensão T_{j−1} que está acima da frequência de corte f_j = λ_j / 2π. É calculada só com o que a v0 tem (as suas tensões), nunca com o mundo. É a frase "isto durou menos que o meu período, eu não vi", em número.

**Cegueira real β_j (de fora).** Em mundo sintético sabemos x. A cegueira real do andar j é a fração da variância do mundo que o registro j não representa: β_j = E‖x_t − R_{j,t}‖² / E‖x_t − x̄‖², com o observador olhando sempre. É o que um auditor externo mediria. A v0 não tem acesso a β; o teste tem.

A pergunta A é se δ̂ acompanha β. A pergunta B é se entregar δ̂ a um leitor o faz errar menos.

## Mundos

N = 20.000, d = 2, 100 sementes (1000–1099), observador fixo da v0 (k = 4, λ₁ = 0,15, b = 10; a declaração é sobre **este** instrumento, com a sua rigidez herdada, e isso é o que se quer: cegueira relativa a uma rigidez dada). Olhar sempre (a política reprovou no teste 2 e não entra aqui). Calibração [0, 10.000), medida [10.000, 20.000).

Quatro mundos com espectros conhecidos e diferentes, para que β_j varie entre mundos no mesmo andar:

- **branco:** ruído branco σ = 1 (quase toda a potência acima de qualquer f_j: β alta em todos os andares);
- **deriva:** AR(1) φ = 0,9 (potência concentrada abaixo de ≈ 0,02 ciclos/passo);
- **escada-3:** soma de AR(1) com τ = 7, 70, 700 (potência espalhada por três décadas);
- **cíclico:** senoide de período 300 mais ruído fraco (quase toda a potência numa frequência só: andares com f_j acima de 1/300 veem, abaixo não).

Os mundos foram escolhidos para que a ordem dos β_j entre mundos **não** seja a mesma em todos os andares; é isso que uma declaração verdadeira tem de acompanhar e que uma declaração cega ao mundo não consegue.

## Hipótese A: a declaração é verdadeira

**Medida.** Para cada andar j, a correlação de Spearman ρ_j entre δ̂_j e β_j através dos 400 pares (mundo, semente).

**Nulo.** Permutação: δ̂_j embaralhado entre pares (mundo, semente), 1.000 vezes; envelope de ρ_j sob permutação. Nulo nominal, relatado e não julgado: a declaração que um filtro faria sem olhar nada, δ_nom,j = fração da potência de ruído branco acima de f_j (um número por andar, igual em todos os mundos: correlação indefinida, porque não varia; é por isso que ele não pode ser o nulo do critério e é por isso que a declaração da v0 vale alguma coisa se passar).

**Critério A (um julgamento).** Passa se ρ_j ≥ 0,7 **e** acima do envelope de permutação, nos quatro andares. Relata-se também o erro absoluto mediano |δ̂_j − β_j| por andar, sem critério: a declaração pode ser verdadeira na ordem e errada no valor, e a leitura dirá qual.

**Aposta A: 55 %.** A favor: δ̂ e β são o mesmo objeto (o que passa acima de f_j), um visto pela tensão e outro pelo resíduo. Contra, nomeado antes: δ̂ é calculada sobre a **norma** da tensão (não linear; a norma dobra frequências) e sobre T_{j−1}, que já é o resíduo do andar anterior, não o mundo; os dois desvios podem bagunçar a ordem, sobretudo no andar 1, onde T₀ = ‖x − R₁‖ mistura a potência de todas as frequências. Aposta por andar: 1: 45 %, 2: 60 %, 3: 65 %, 4: 55 % (no 4 o período é 42.000 passos, maior que a série; a FFT mal o resolve, e isso é um defeito nomeado antes: a declaração do andar mais lento precisa de uma série mais longa do que a sua constante de tempo, o que é o Paper A dizendo que a identidade só se mede em prazo maior que ela).

## Hipótese B: a declaração é útil a quem lê

**O leitor.** Um leitor linear fixo: pesos w sobre os quatro registros, ajustados por mínimos quadrados (ridge 10⁻⁶, como no teste 4) **num único mundo de treino** (deriva), para prever x_t a partir de R_{t−1}. Depois o leitor é levado aos outros três mundos sem retreinar. É a situação do OBS-01: quem lê um observador foi calibrado em outro lugar e não vê o mundo atual, só os registros.

**Sem declaração:** o leitor usa w como veio. **Com declaração:** o leitor reescala cada peso pela visibilidade declarada no mundo atual em relação ao mundo de treino: w'_j = w_j · (1 − δ̂_j^{atual}) / (1 − δ̂_j^{treino}), e renormaliza para Σ w' = Σ w. O leitor nunca vê x; só os registros e os quatro números que a v0 declara.

**Nulo.** O leitor sem declaração (w fixo). Nulo de sanidade: o leitor com a declaração **nominal** (δ_nom, igual em todos os mundos: w' = w; coincide com o nulo, e isso é intencional: uma declaração que não depende do mundo não pode ajudar).

**Medida.** Erro de predição médio na janela de medida, por mundo de destino e semente; vantagem U = 1 − e_com / e_sem.

**Critério B (um julgamento).** Passa se U > 0 em ≥ 80 das 100 sementes em **cada** um dos três mundos de destino (branco, escada-3, cíclico). Relata-se o teto: o leitor retreinado no mundo de destino (o melhor que um leitor com acesso ao mundo faria).

**Aposta B: 40 %.** A favor: reescalar pelo que cada andar vê é a correção certa em primeira ordem quando o espectro muda. Contra: a reescala por (1 − δ̂) é uma heurística minha, não derivada; no branco todos os andares são quase cegos e a renormalização pode amplificar ruído; no cíclico o leitor talvez precise mudar o **sinal** de um peso, que nenhuma reescala positiva faz. Aposta por destino: branco 35 %, escada-3 55 %, cíclico 35 %.

## O que fecha

- A reprova: a declaração da v0 não acompanha a cegueira real; a frase "sei do que sou cega" é retórica, e o OBS-01 não pode usar este instrumento como está. Candidato a conserto, só com predição nova: declarar sobre a potência do próprio registro (R_{j−1} − R_j, linear) em vez da norma da tensão.
- A passa e B reprova: a v0 sabe do que é cega mas isso não serve a um leitor linear com esta reescala. O defeito pode ser do leitor (heurística) e não da declaração; a leitura separa os dois pelo teto.
- A e B passam: a v0 tem, dentro destes mundos, a única propriedade que a distingue de um filtro, e ela é verdadeira e útil. Aí, e só aí, o próximo mundo pode ser a saída de um modelo de IA (OBS-01), com predição própria.

## O que não conta

Correlação alta só nos andares rápidos. Utilidade só no mundo de treino. Qualquer ajuste da reescala, dos mundos ou do limiar 0,7 depois de ver os números: se a heurística do leitor for ruim, o teste B diz isso e fica.

## Custo

Quatro mundos × 100 sementes × um observador fixo: minutos. O instrumento novo é só `beta_real`, a FFT de `v0.cegueira` com série mais longa, e o leitor com reescala. Nada do v0 muda.
