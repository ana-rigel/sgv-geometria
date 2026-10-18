# Leitura do teste 13 (saltos em cachos) — REPROVADO, e o teto não se mediu

**Predição:** PREDICAO_teste13_saltos_em_cachos.md (df7d6bb), antes de rodar. **Resultado:** resultados_teste13.json. Um julgamento; sem emenda.

| | erro de predição médio (medida) |
|---|---|
| teto 1: olhar sempre | 1,9 |
| teto 2: oráculo (sabe o cacho), ritmo afinado | V_orac **+6,9 %**, envelope **−31 % a +37 %** |
| nulo: a cada 4 | — |
| v0: ritmo lido na régua, H aprendido | V **+0,05 %**, envelope −3,9 % a +5,1 %, positiva em 22 de 85 válidas |

Critério: (a) válidas ≥ 95: **não** (85); (b) envelope acima de zero: **não**. **Reprovado.** Apostas: V_orac entre +10 e +25 %, errada (6,9 % na média, e com envelope que cruza −31 %); passar 45 %, certa a não-passagem; V média entre +4 e +15 %, errada; V > 0 em ≥ 85, errada; captura ≥ 50 % do oráculo, errada.

## O que o resultado diz

O resultado principal não é sobre a v0; é sobre o mundo e a afinação. O oráculo, que sabe o cacho verdadeiro, deveria ser um teto estável, e não foi: em sementes como a 1090 ele ganha 24 % com (1, 4) e em outras **perde** 31 % com pares absurdos como (4, 1) (devagar no cacho, rápido fora). A razão: com probabilidade 1/2.000 de salto fora de cacho, a janela de afinação de 2.000 passos tem, em média, **um** cacho, muitas vezes nenhum. Sem cacho na afinação, qualquer p_q cabe no orçamento e a afinação escolhe ao acaso; na medida, com cachos, o acaso cobra. O par mais frequente da v0 foi (4, 4), o periódico, por isso mesmo. E a fração de olhadas na medida saiu da faixa em 15 sementes, porque a ocupação de cacho na medida não é a da afinação.

A v0 por cima disso: H aprendido (mediana 60, igual ao do mundo, quando havia rupturas para medir; 11 ou 32 quando não havia), λ₁ = 0,95 em todas, e um V que é ruído em torno de zero. Onde a afinação acertou (s1060: oráculo +24,6 %), a v0 capturou +6,7 %: um quarto, com a régua como gatilho. Isso é a única leitura sobre a política que o teste permite, e é uma semente.

O defeito 24 foi atacado (calculei o teto antes) e o cálculo errou por um motivo que eu não vi: contei saltos por tempo total, não por janela, e um mundo com teto alto **na média** pode não ter teto nenhum numa janela de 2.000 passos. A conta certa teria mostrado que o mundo precisava de cachos a cada 300–400 passos, não a cada 2.000.

## O que fecha e o que não

- Fecha: neste mundo, com estas janelas, nem o oráculo mede o teto; o teste não responde sobre a política. Reprovado pelo critério, **inconclusivo** quanto à pergunta.
- Não fecha: o mesmo teste com cachos densos o bastante para que cada janela tenha vários (p_fora ≈ 1/400, mantendo 1/12 por 60 passos dentro), onde o oráculo deve ficar estável e alto, e a distância v0–oráculo passa a ser a medida da régua como gatilho.

## Para a lista de defeitos de desenho do projeto

25. Mundo raro demais para as janelas: um cacho por janela de afinação; o teto de oráculo vira ruído e o ritmo é escolhido ao acaso. O teto tem de ser calculado **por janela**, não por série.

Treze testes, treze reprovações (um inconclusivo), vinte e cinco defeitos.
