# Previsão registrada antes de calcular: a mente geométrica é mais que um filtro?

**Registrada em:** 17/10/2026, antes de escrever o código e de rodar qualquer simulação.

**Pedido da Ana:** "Vamos brincar então", sobre os dois experimentos propostos na Fase 0: uma organização que aprende ritmo e uma rigidez modulada pela surpresa. Brincadeira com as regras da casa: critério antes, nulo ao lado, um julgamento.

**Status:** exploração em mundo sintético (nada de mercado, nada de outubro). Ramo `exploracao/mente-geometrica`, pasta `mente/`.

## O mundo e a mente de base (o Teste B de 4/3/2026)

- Plano [−10, 10]². O campo F é um ponto que **teleporta** para posição uniforme aleatória. Entre teleportes, F recebe ruído gaussiano de desvio σ_n = 0,3 por passo (sem ruído, a melhor mente seria copiar o campo e nada se aprenderia).
- **Mente M0 (original):** M ← M + lr·(F − M), O ← O + pull·(M − O), lr = 1 − rigidez, rigidez 0,85, pull 0,05. Tensão T = ‖F − M‖; EMA_T com α 0,08; E_norm = (T − EMA_T)/EMA_T.
- Dois mundos: **W1, com ritmo:** teleporte exatamente a cada P = 20 passos. **W0, sem ritmo** (nulo do experimento 1): teleportes em instantes geométricos com o mesmo intervalo médio de 20. Mesmo número esperado de saltos, mesma amplitude, só o ritmo difere.
- Cada rodada: 4.000 passos (≈ 200 saltos), 100 sementes (1000–1099). As medidas são médias por semente; o envelope é o intervalo entre o mínimo e o máximo das 100 sementes do nulo, como nas rodadas do SGV.

## Medidas

1. **Custo de salto** J_salto = soma de T nos 10 passos após cada teleporte, média por salto (quanto tempo a mente fica cega depois que o mundo muda).
2. **Custo de calma** J_calma = média de ‖M − F̄‖ nos passos 11 a 19 de cada ciclo, com F̄ = posição do campo sem o ruído (quanto a mente se deixa levar pelo ruído quando nada mudou).
3. **Custo total** J = J_salto + 10·J_calma (o fator 10 põe os dois na mesma escala: 10 passos de salto contra uma média de calma).

## Experimento 1: organização que aprende ritmo (mente M1)

M1 = M0 mais um relógio na organização: a organização guarda, além da posição, uma estimativa do período P̂ (média exponencial dos intervalos entre saltos detectados; salto detectado quando T > 3·EMA_T) e a fase. Quando o relógio diz que um salto é esperado (passo ≡ 0 mod P̂, com tolerância ±1), a mente **abre a plasticidade** por 3 passos: lr sobe de 0,15 para 0,8. Fora da janela, lr = 0,15. A mente não sabe para onde o campo vai; só sabe quando.

- **Critério "aprendeu o ritmo":** a redução de J_salto de M1 em relação a M0 em **W1** excede a redução em **W0** em pelo menos 15 pontos percentuais, e a redução em W1 está acima do máximo do envelope das 100 sementes de W0. Se a redução for igual nos dois mundos, M1 é só um filtro com plasticidade intermitente, não uma mente que aprendeu algo do mundo.
- **Critério de custo:** J_calma de M1 não piora mais que 10 % em relação a M0 em W1 (abrir a plasticidade na hora errada custaria calma).

## Experimento 2: rigidez modulada pela surpresa (mente M2)

M2 = M0 com lr_t = lr_min + (lr_max − lr_min)·s(E_norm), s = sigmoide centrada em 0,3 com largura 0,15, lr_min = 0,05, lr_max = 0,8. Plástica quando surpresa, rígida quando o mundo está calmo. Sem relógio, sem memória do ritmo.

- **Nulo (o adversário justo):** a **melhor rigidez fixa**, escolhida por varredura de lr em {0,05; 0,10; …; 0,95} minimizando J no mesmo mundo e nas mesmas sementes. O nulo é otimizado com os mesmos dados: uma mente só vale o nome se bater o melhor botão fixo.
- **Critério "venceu o dilema estabilidade–plasticidade":** J(M2) < mín_lr J(lr fixo) nos dois mundos (W1 e W0), com margem acima do máximo do envelope das sementes. Se M2 só empatar com o melhor fixo, a modulação é cosmética.
- Descritivo: J_salto e J_calma separados, para ver de onde veio o ganho.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Exp. 1: M1 reduz J_salto em W1 (qualquer redução) | ~90 % |
| Exp. 1: critério "aprendeu o ritmo" passa (diferença W1 − W0 ≥ 15 pp, acima do envelope) | ~60 % |
| Exp. 1: J_calma de M1 piora menos de 10 % | ~70 % |
| Exp. 2: M2 bate o melhor lr fixo em W1 | ~65 % |
| Exp. 2: M2 bate o melhor lr fixo em W0 | ~60 % |
| Exp. 2: critério completo (os dois mundos, acima do envelope) | ~50 % |

A dúvida do experimento 2 é a sigmoide escolhida à mão: um lr fixo bem escolhido é um adversário forte, e um limiar mal posto deixa M2 lenta demais no salto ou nervosa demais na calma. Não vou ajustar a sigmoide depois de ver o resultado; se ela for ruim, o resultado diz isso.

## O que isto não é

Não é mercado, não é previsão, não é lucro. É a pergunta da Fase 0: o que separa uma mente geométrica de um filtro com três botões. Duas respostas registradas antes: aprender o ritmo do mundo (exp. 1) e modular a própria rigidez pela surpresa melhor do que qualquer rigidez constante (exp. 2).

## Emenda 1 (registrada depois da primeira rodada, antes de rodar de novo)

**Primeira rodada (4060037; resultados_mente_v1_REPROVADO.json):** os dois critérios reprovaram. Exp. 1: M1 reduziu J_salto só 2,1 % em W1 e 1,0 % em W0. Exp. 2: o melhor lr fixo foi 0,95 (quase copiar o campo), com J 4,2 contra 10,6 de M2.

**Dois defeitos, nenhum de hipótese:**
1. *Instrumento (M1):* o detector de salto "T > 3·EMA_T" perde metade dos saltos porque a EMA ainda está alta quando o salto seguinte chega; P̂ convergiu para ~40 em vez de 20 e as janelas abriram na hora errada (verificado numa semente: detectados 20, 40, 80, 100, 140…). **Correção:** salto detectado quando T_t − T_{t−1} > 2 (o ruído σ_n produz variações de ~0,4). Nada mais muda em M1.
2. *Mundo (exp. 2):* com σ_n = 0,3 contra saltos de ~6, não há dilema estabilidade–plasticidade: copiar o campo é quase ótimo, e qualquer mente com memória perde. O mundo não testava a pergunta. **Correção:** σ_n = 2,0 em W1 e W0 (ruído da ordem de um terço do salto típico), para que lembrar valha alguma coisa. O limiar do detector (2) foi escolhido com σ_n = 2,0 em mente: ΔT de ruído ≈ 2,8·σ_n·… não; com σ_n = 2,0 a variação de T por ruído chega perto de 2, então o limiar passa a **3** em vez de 2, fixado agora.

Critérios, apostas e tudo o mais permanecem. Última emenda: se reprovar de novo, fica reprovado.
