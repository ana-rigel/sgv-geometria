# Predição do teste 42 (42-A: a memória das interações e a largura da janela)

20/10/2026 · escrita antes de rodar · mapa de teste41.py, acrescido da memória q · Ana Rigel

## De onde vem

Do teste 41 e do terceiro texto do colaborador (20/10). O teste 41 mostrou que a faixa da NGC 628 é um regime persistente de sincronização parcial, numa janela estreita de K/K_c ≈ 0,970–1,035 (≈ 6,5–7 % de K_c), com 0,627 na borda caótica. O colaborador propôs o **Caminho A**: uma memória dinâmica, sem coerência-alvo, consegue alargar a janela? A forma é dele; a conta prévia, os controles extras e a malha foram acertados na conversa de 20/10.

## O sistema

```
Sᵢ = C sen(ψ − θᵢ)                                  (a interação do modelo original)
θᵢ ← θᵢ + Δωᵢ + K [(1 − α) Sᵢ + α qᵢ]
qᵢ ← qᵢ + (Sᵢ − qᵢ)/τ,    qᵢ(0) = Sᵢ(0)
```

α = 0 é o modelo do teste 41. Não há coerência-alvo. Os estados travados continuam sendo soluções (no travamento, Sᵢ é constante e qᵢ = Sᵢ).

**Malha fixada aqui:** α ∈ {0,25; 0,5; 0,75; 1} × τ ∈ {30; 100; 300; 1.000} Myr, mais α = 0. Disco de 12 anéis (9–14 kpc, 200 km/s), K/K_c de 0,90 a 1,20, passo 0,005; 20.000 Myr por trajetória, 4.000 de transiente; deriva entre quatro janelas de 4.000 Myr, como no teste 41.

**Condições iniciais:** 10 de **seleção** (semente 420) e 10 de **validação** (semente 421), cada uma com fases N(0; 0,15), nunca reaproveitadas. A seleção escolhe a célula; o julgamento usa só a validação.

**As três larguras** (cada uma como número de pontos da grade × 0,005):

- **janela da faixa:** os K em que a mediana de C̄ entre as condições fica em [0,527; 0,727] **e** a mediana da deriva ≤ 0,02;
- **janela de sincronização parcial:** os K em que, na maioria das condições, o aglomerado travado tem ≥ 6 anéis e ≥ 1 anel escorrega;
- **K_L:** o menor K em que os 12 anéis travam em todas as condições.

**Seleção:** a célula (α, τ) de maior janela da faixa nas condições de seleção. Empate: menor α; depois, menor τ.

**Controle das frequências uniformes** (sem memória): Δωᵢ igualmente espaçadas com a mesma amplitude total de N = 12, para N = 12, 16, 24 e 48, cinco condições, janela de sincronização parcial.

Relatado: a tabela inteira da seleção (as três larguras para as 16 células e α = 0); a inclinação dC̄/dK no centro da janela; o λ_max (direção da fase global projetada fora) em 20 e 40 Gyr, condição coerente, para α = 0 e a célula escolhida.

## Conta prévia

- No teste 41, os anéis que escorregam giram 8–20 mrad/Myr em relação ao aglomerado. Para essas frequências ν, o filtro passa uma fração 1/√(1 + (ντ)²) da força oscilante, com atraso de fase atan(ντ). Com τ = 30, quase nada muda (ντ ≈ 0,25–0,6). Com τ ≥ 100, a força sobre os anéis que escorregam cai pela metade ou mais e fica atrasada: é um acoplamento com defasagem (Sakaguchi–Kuramoto), que dificulta recrutar anéis.
- Nos anéis travados, Sᵢ é quase constante e a memória quase não age.
- **Previsão de mecanismo:** com α e τ grandes, o recrutamento dos anéis internos fica mais difícil, a curva C̄(K) fica menos íngreme e o travamento total (K_L) sobe. A janela da faixa (que é a faixa de C dividida pela inclinação) deve **alargar**, mas por achatamento da curva, não por uma organização mais forte. A janela de sincronização parcial também deve alargar, porque K_L sobe.
- Com τ grande, a memória também atrasa a resposta do aglomerado aos transientes. Isso pode mudar a estabilidade do travamento (o colaborador apontou) e criar oscilações; o J5 vigia o caso extremo.
- **Controle uniforme:** para a distribuição uniforme, no limite N → ∞, a transição é direta do incoerente ao travamento total, e a janela de sincronização parcial some. Com frequências uniformes, ela deve estreitar com N. A janela de ≈ 6,5 % que parou de estreitar no teste 41 viria da não uniformidade de Ω ∝ 1/r.

## Critérios

**J1, recuperação:** com α = 0 e as condições de validação, a janela da faixa vai de **0,965–0,975** até **1,030–1,040** (as bordas do teste 41, ± 0,005).

**J2, ampliação:** na validação, a janela da faixa da célula escolhida é **≥ 1,5 ×** a de α = 0.

**J3, robustez:** na célula escolhida e na validação, em **≥ 80 %** dos K da janela da faixa, a diferença entre o maior e o menor C̄ das 10 condições é **≤ 0,03**.

**J4, escala:** com N = 16 e N = 24 (cinco condições de validação; a célula escolhida em N = 12), a razão de larguras célula / α = 0 é **≥ 1,5** nas duas.

**J5, sincronização parcial genuína:** na célula escolhida e na validação, em **≥ 80 %** dos K da janela da faixa, o aglomerado tem ≥ 6 anéis e ≥ 1 anel escorrega (não é travamento total).

**J6, o controle uniforme estreita:** a janela de sincronização parcial com frequências uniformes decresce estritamente de N = 12 a 16, 24 e 48.

## Apostas (Claude, antes de rodar)

- **J1: 95 %.**
- **J2: 45 %.** O achatamento deve acontecer, mas 1,5 × é muito.
- **J3: 65 %.**
- **J4: 40 %.**
- **J5: 60 %.**
- **J6: 70 %.**
- **A célula escolhida tem τ ≥ 100 e α ≥ 0,5, e K_L sobe em relação a α = 0: 65 %.**

## O que fecha

- **J2, J3, J5 passam:** uma memória das interações, sem alvo, alarga a janela da organização parcial de forma robusta. Se a inclinação cair e K_L subir, o mecanismo é o previsto: a memória dificulta o recrutamento e torna a coerência menos sensível a K. É robustez em K, mas por uma organização mais **fraca** por anel, e a leitura dirá isso.
- **J2 reprova:** neste modelo, a memória das interações não resolve o ajuste fino; o Caminho B (mudar a física) passa a ser necessário.
- **J4 reprova com J2 passando:** o ganho é de disco pequeno.
- **J6 passa:** a sobrevivência da janela no contínuo depende da forma da curva de rotação, não de N. Isso vira uma pergunta física para a NGC 628: a sua curva de rotação na zona estável é plana o bastante?

Um julgamento por hipótese; sem emenda. Instrumento: teste42.py, escrito depois do commit desta predição.
