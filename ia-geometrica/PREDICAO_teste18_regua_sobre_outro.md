# Predição do teste 18 (a régua sobre outro observador)

18/10/2026 · escrita antes de rodar · primeiro teste em que a v0 mede um observador que não é ela

## Pergunta

Os testes 16 e 17 mostraram que a v0 declara a própria cegueira com verdade, usando ganhos que ela conhece. O OBS-01 quer medir a cegueira de um observador cujos ganhos ninguém conhece: um registro Ω que recebe o mesmo mundo x e produz uma saída y. **Vendo só x e y, a v0 estima onde está o corte de Ω e quanto do mundo Ω não vê?**

## O que a v0 faz (instrumento declarado)

Com x (o mundo) e y (a saída de Ω) na mão, e sem saber nada da forma de Ω, a v0 estima o ganho empírico por espectro cruzado (Welch, segmentos de 8.192 passos, janela de Hann): Ĥ(f) = S_yx(f) / S_xx(f), e a coerência γ²(f). Dali declara:

- **o corte estimado** f̂_c: a primeira frequência, de baixo para cima, em que |Ĥ|² cruza ½;
- **a cegueira estimada** β̂_Ω = Σ_f S_xx(f) · (1 − min(|Ĥ(f)|², 1)) / Σ_f S_xx(f), a mesma regra dos testes 9–17 com o ganho real trocado pelo estimado;
- **a cobertura**: a fração da potência de x nas frequências em que γ² ≥ 0,5, isto é, onde a estimativa tem apoio. É a v0 declarando onde a sua régua não alcança: onde o mundo não tem potência, não há como medir o que Ω deixa de ver.

## Os observadores Ω (desconhecidos para a v0, conhecidos para o teste)

1. EMA λ = 0,3 (rápido); 2. EMA λ = 0,03; 3. EMA λ = 0,003 (lento, período ≈ 2.000); 4. cascata de duas EMAs λ = 0,03 (segunda ordem: a v0 nunca viu essa forma); 5. média móvel de janela W = 50 (ganho com zeros, forma fora da família da v0); 6. EMA λ = 0,03 com ruído branco σ = 0,2 somado à saída (a v0 vê uma saída suja; a cegueira de Ω é a da saída limpa).

Verdade: f_c de cada Ω resolvido numericamente no ganho analítico (|H|² = ½; na cascata |H|⁴ = ½); β_Ω = E‖x − y_limpo‖² / Var(x) na medida.

## Mundos

N = 200.000, 100 sementes. **escada-3** (τ 7, 70, 700: potência em três décadas; é o mundo de julgamento) e **deriva φ = 0,9** (potência estreita; relatado, não julgado: espera-se que a cobertura caia para os Ω rápidos e a v0 declare isso).

## Critério (um julgamento, no mundo escada-3)

(a) f̂_c a ±30 % de f_c em ≥ 80 das 100 sementes, para cada um dos seis Ω; **e** (b) erro absoluto mediano |β̂_Ω − β_Ω| ≤ 0,05 para cada um dos seis. Relata-se a cobertura por Ω e mundo.

## Apostas

- **Passar: 50 %.** A favor: o espectro cruzado é o estimador clássico de função de transferência e o mundo tem potência onde os cortes estão; o ruído na saída (Ω 6) não enviesa S_yx/S_xx. Contra: (i) no Ω 3 (λ = 0,003) o corte está em 4,8 × 10⁻⁴ e as bolhas de Welch com 8.192 passos têm resolução 1,2 × 10⁻⁴; a primeira travessia de ½ pode cair uma bolha fora (±25 %) e o critério é ±30 %; (ii) na média móvel os zeros do ganho fazem |Ĥ|² oscilar e a primeira travessia pode ser achada tarde; (iii) o viés de Welch nas frequências baixas pode empurrar β̂ para cima de 0,05 no Ω 3. Por Ω: 1: 85 %, 2: 85 %, 3: 45 %, 4: 70 %, 5: 60 %, 6: 75 %.
- Cobertura ≥ 0,9 em escada-3 para todos os Ω (70 %); cobertura < 0,5 em deriva para o Ω 1 (60 %).

## O que fecha

Passar: a v0 é régua sobre registros lineares de forma desconhecida, vendo entrada e saída; é a primeira cláusula do OBS-01 fora do sintético fechado. Reprovar só no Ω 3: a resolução, não o método; fica como limite declarado (a régua mede o que é mais rápido que o seu segmento). Reprovar em 4 ou 5: o método não generaliza além da primeira ordem, e o OBS-01 precisa de outro estimador. Limitação escrita antes: quando só se vê y, sem x, a cegueira não é identificável sem hipótese sobre o espectro do mundo; esse é o caso de um modelo de IA cuja entrada não se conhece, e fica fora deste teste.
