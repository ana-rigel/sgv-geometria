# Leitura do teste 10 (expectativa num mundo com regimes) — REPROVADO

**Predição:** PREDICAO_teste10_regimes.md (81219d4), antes de rodar. **Resultado:** resultados_teste10.json. Um julgamento; sem emenda.

| | erro de predição médio (medida) |
|---|---|
| teto: olhar sempre | 4,15 |
| nulo: olhar a cada 4 | 5,40 |
| v0: expectativa, n_max 16 | 5,45 |

V média **−1,53 %**, envelope −7,6 % a +3,0 %, positiva em 12 sementes; **48 sementes válidas** (a afinação de θ só acertou 25 % ± 3 pp em metade). Critério: (a) não; (b) não. **Reprovado.** Apostas: 55 % em passar, errada; V entre +3 e +12 %, errada; V > 0 em ≥ 90, errada; b_n > 0,2 até n = 16, **certa** (0,73 → 0,63, estável).

## O que o resultado diz

A expectativa **funcionou como informação e falhou como política.** b_n ficou em 0,63–0,73 em todos os horizontes: a tensão lida diz, sim, em que regime o mundo está, e continua dizendo 16 passos depois. A predição acertou isso e errou o resto, e o erro é instrutivo.

O que a política faz com essa informação: no quente, a expectativa passa de θ já em n = 1, e ela olha **todo passo, em sequência**; no frio, dorme até n_max. Com orçamento de 25 % e blocos quentes que ocupam metade do tempo, θ sobe até ela só olhar nos momentos mais quentes, em rajadas, e no frio fica 16 passos cega. Duas coisas a derrubam:

1. **Olhadas em rajada valem pouco para um registro lento.** R₁ tem λ₁ = 0,15: cada olhada move a memória 15 % do caminho. Dez olhadas seguidas chegam a 80 % do caminho, mas a mesma dez espalhadas a cada 2 passos acompanham o mundo por 20 passos. A política concentra onde o periódico espalha, e o periódico ganha mesmo sem saber do regime.
2. **A afinação por bissecção quebrou** (defeito 5, agora grave): com blocos raros a fração de olhadas é uma função em degraus de θ, e metade das sementes caiu fora da faixa.

A pergunta certa não era "quando olhar?" mas "**com que ritmo** olhar em cada regime?": a cada 2 no quente, a cada 8 no frio, por exemplo, com o regime lido pela tensão na régua. Essa política usa a informação que b_n mostrou existir sem concentrar as olhadas. É outra política, com predição própria.

## O que fecha e o que não

- Fecha: a política de limiar na expectativa (olha quando a expectativa passa de θ) não vale num mundo com regimes, e não vale num mundo sem (teste 7): o problema é a **forma** limiar, que concentra olhadas, não a informação, que existe.
- Não fecha: uma política de **ritmo por regime** (período de olhada escolhido pela tensão na régua, dois ou três ritmos fixados na calibração), nulo periódico, mesmo mundo.

## Para a lista de defeitos de desenho do projeto

21. Política de limiar com registro lento: concentra as olhadas onde o registro menos aproveita. A grandeza certa é o ritmo, não o instante.
22. Bissecção de θ num mundo com blocos: fração em degraus; metade das sementes inválidas. A afinação deve ser por ritmo (inteiro), não por limiar (contínuo).

Dez testes, dez reprovações, vinte e dois defeitos.
