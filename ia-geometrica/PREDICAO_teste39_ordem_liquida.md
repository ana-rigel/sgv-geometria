# Predição do teste 39 (a ordem líquida: a autoconsistência descontada do piso do acaso)

20/10/2026 · escrita antes de rodar · modelo de teste38.py, sem mudança na dinâmica · Ana Rigel

## De onde vem

Da leitura do teste 38. O Laço III-a (autoconsistência, log g ← log g + η(C − |R₃|)) travou o disco em 0,999 em todo K e até com a memória vazia. Com 12 anéis soltos, C tem um piso de acaso, enquanto |R₃|, média lenta de um Z que gira, vai a quase zero; C − |R₃| fica positivo e a voz corre ao teto. A Ana trouxe uma proposta (de outro assistente) para descontar o piso do acaso. Dela se aproveita a ideia central, a **ordem líquida**:

  ordem(x, piso) = max(0, (x − piso) / (1 − piso)).

Quatro pontos da proposta foram corrigidos antes deste desenho (conversa de 20/10):

1. O piso de C para 12 fases sorteadas é a média **0,257**, e não 1/√N = 0,289, que é o RMS (200 mil sorteios; √(π/4N) = 0,256).
2. A memória tem o seu próprio piso. Medido no modelo com K = 0, depois de 2 Gyr, 100 sementes: campo 0,261; andares 1–4: 0,26 · 0,21 · **0,088** · 0,027. Para o andar 3, o piso é **0,088**.
3. A regra de rigidez da proposta endurece, e não amolece, no caso da memória "estátua"; ela não entra aqui.
4. O ajuste de K com zona morta em ordem líquida [0,1; 0,8] (C bruto ≈ [0,36; 0,86]) esconde um alvo que contém 0,627; ele não entra aqui.

Este teste muda **uma** coisa no III-a: C e |R₃| viram ordem líquida.

## O laço

```
log g ← log g + η · [ordem(C, 0,257) − ordem(|R₃|, 0,088)],   η = 0,05 por Myr,  g ∈ [0,05; 20]
```

Em dois sabores:

- **cortada:** a fórmula da proposta, com max(0, ·);
- **sem corte:** (x − piso)/(1 − piso), que pode ser negativa.

O motivo dos dois está na conta prévia. Modelo, braços e medida como no teste 38: 12 anéis, m = 5, 200 km/s, D = 2,5 × 10⁻⁴ rad²/Myr, escuta no andar 3, 5.000 Myr, 100 sementes (semente 39), C̄ medida em 3.000–5.000 Myr, faixa [0,527; 0,727]. Braços: memória semeada em K = 0,7 · 0,8 · 0,9 K_c, memória vazia em 0,8 K_c, nos dois sabores; referência sem laço (g = 1) nos três K.

## Conta prévia (só o instrumento; disco solto do modelo, K = 0, 2–6 Gyr)

- **O corte tem viés.** Com o disco solto, a média da ordem líquida cortada é **0,073** no disco e **0,016** na memória: as flutuações acima do piso contam, as de baixo não. A diferença, **+0,057**, faz log g subir ≈ 0,003 por Myr no caos puro. Isso é dobrar g a cada ≈ 240 Myr, e ir de 0,05 a 20 em ≈ 2 Gyr. A versão cortada deve **recriar o falso positivo do teste 38, só que mais devagar**, e travar o disco antes de 5 Gyr.
- **Sem corte, o viés some:** +0,0034 no disco e −0,0010 na memória, uma diferença de ≈ 0,004 (g mal triplica em 5 Gyr).
- **O ponto fixo continua degenerado.** Semeada, a memória começa com ordem líquida ≈ 0,99, maior que a do disco; a voz cai ao piso, o disco se solta, a memória decai em ≈ 1–2 Gyr até o piso dela. Aí as duas ordens líquidas ficam perto de zero e g para. Sem corte, o disco deve terminar **solto**, perto de 0,26, em qualquer K: o "mesmo ponto em todo K" seria o caos, por isso o J4 exige um ponto acima dele.

## Critérios

**J1, a versão cortada não cria ordem (memória vazia, 0,8 K_c):** mediana de C̄(3.000–5.000) ≤ **0,31** (piso + 0,05).

**J2, a versão sem corte não cria ordem (memória vazia, 0,8 K_c):** mediana de C̄(3.000–5.000) ≤ **0,31**.

**J3, a versão sem corte apara até a faixa (semeada, 0,8 K_c):** C̄(3.000–5.000) na faixa em **≥ 80 de 100**.

**J4, a versão sem corte tem um ponto próprio acima do caos (semeada):** as medianas de C̄ em 0,7 · 0,8 · 0,9 K_c ficam a ≤ **0,05** umas das outras **e** todas ≥ **0,40**.

Relatado: os braços semeados da versão cortada; a referência; as trajetórias de g, |R₃| e C a cada 250 Myr; a fração de anéis travados; o tempo até g atingir o teto, quando atingir.

## Apostas (Claude, antes de rodar)

- **J1: 35 %.** O viés de +0,057 deve levar g ao teto em ≈ 2 Gyr.
- **J2: 85 %.**
- **J3: 10 %.** A conta prévia diz que o disco termina solto.
- **J4: 10 %.**

## O que fecha

- **J1 reprova, J2 passa:** descontar o piso conserta o falso positivo só se for feito sem corte. Cortar em zero devolve o erro do teste 38 por outra porta: as flutuações do caos acima do piso viram ordem.
- **J2 passa, J3 e J4 reprovam:** com o piso certo, a autoconsistência deixa de criar ordem, e com isso também deixa de segurá-la. Ela leva o disco ao caos e para lá, porque "a memória não guarda mais ordem líquida que o disco" é satisfeita pelo caos. Aparar até um nível exige outro princípio, e a autoconsistência sozinha sai da lista.
- **J3 ou J4 passam:** a autoconsistência com o piso certo acha um nível próprio, contra a conta prévia, e isso pede uma leitura com cuidado antes de qualquer coisa.

Um julgamento por hipótese; sem emenda. Instrumento: teste39.py, escrito depois do commit desta predição. Ramo: ia-geometrica/v0.
