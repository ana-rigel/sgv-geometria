# Leitura do teste 53 (a entrada das águas lida na fase do ritmo aprendido): J1 e J2 REPROVADOS; J3 PASSOU. O relógio que continua olhando o campo erra muito mais que o calendário; o relógio que parou de olhar, corrigido uma vez por ano, prevê tão bem quanto o relógio v1 sem ter o calendário escrito

**Predição:** PREDICAO_teste53_entrada_pela_fase.md (f22bd33), antes de calcular. **Instrumento:** teste53.py. **Resultado:** resultados_teste53.json. **Diagnóstico depois do julgamento:** diagnostico_teste53_pos_julgamento.txt. Três julgamentos; sem emenda.

## Resultados (42 previsões, 2019–2025; erro = entrada − previsão)

| braço | EAM | viés |
|---|---|---|
| C, calendário fixo | 20,0 | +16,9 |
| V1, relógio v1 (dia aprendido) | **18,8** | +9,7 |
| F, fase aprendida, olhando | 36,5 | −3,0 |
| F0, fase fixa, olhando | 34,7 | +4,6 |
| S, fase aprendida, em silêncio (uma olhada por ano) | **21,2** | −6,2 |

| | resultado | critério | |
|---|---|---|---|
| **J1** F ≤ V1 + 1 | 36,5 contra 19,8 | | **reprovado** |
| **J2** F0 ≤ C − 2, IC < 0 | **+14,7** (IC +4,2; +26,6) | | **reprovado** (o contrário: pior) |
| **J3** S ≤ V1 + 3 | 21,2 contra 21,8 | | **passou** |

Por lugar, S ganha de V1 em Cuiabá (23,4 contra 23,1, praticamente empate), Alta Floresta (19,4 contra 21,1) e Rondonópolis (15,6 contra 21,9), e perde em Juara, Sinop e Barra do Garças.

Apostas: J1 (65 %), errada; J2 (15 %), certa a reprovação; J3 (40 %), errada.

## O que o resultado diz

**1. O relógio que olha o campo tem a fase sacudida pelo tempo de cada ano.**
- Olhando, a fase do andar 2 em 1/09, medida contra o calendário, varia entre anos de **13 a 49 dias** de desvio padrão.
- Em Cuiabá e Rondonópolis, ela **escorrega** de ≈ 60 para ≈ −40 dias em anos isolados (2021, 2024, 2025). Daí os erros de 110 a 138 dias.
- O relógio está travado no ano, mas com uma margem pequena. No fim da seca, a forçante é fraca e cheia de anomalia, e o ruído empurra a fase.

É o achado do teste 35, de novo: no fim da seca, a fase que o campo mostra é ruído para um relógio. O teste 52 só olhou frequências e períodos, nunca a estabilidade da fase enquanto ela olha (defeito 74).

**2. O relógio em silêncio é um calendário aprendido, e com o laço do v1 funciona.**
- Sem ouvir o campo, a fase anda lisa e atrasa de forma regular (3 a 8 dias por ano, como no teste 52).
- A fase esperada da entrada, corrigida uma vez por ano pela entrada vivida, acompanha esse atraso.
- O resultado prevê tão bem quanto o v1 (21,2 contra 18,8; o critério era + 3) e melhor que o calendário fixo em três lugares. O viés virou de +9,7 para −6,2: o laço passou da conta.

O importante é o que a v0 tem nesse braço: **nenhum calendário escrito.** O ano que ela usa foi aprendido do mundo (teste 52); depois ela parou de olhar o campo e só corrigiu a fase da entrada uma vez por ano.

**3. Aqui lembrar vale mais que reobservar.** Esta é a pergunta de origem da v0 (o único ato dela é decidir quando olhar), e este é o primeiro caso medido em que ela tem resposta prática: para prever a entrada das águas, o relógio que parou de olhar o campo erra 15 dias a menos que o que continuou olhando. Olhar todo dia trouxe o ruído do fim da seca para dentro da memória do ritmo; olhar uma vez por ano, no evento que importa, trouxe só a correção.

**4. O ritmo não anuncia a anomalia do ano (J2).** A fase olhando, mesmo sem aprender, é pior que o calendário fixo, com o intervalo inteiro acima de zero. O andar 2 não carrega informação sobre o atraso das águas; carrega ruído. Junto com o teste 35: nem o andar 1 nem o andar 2 anunciam a entrada pela forma da seca.

## O que fecha

- O caminho do teste 52 até a previsão existe, mas pelo silêncio. A v0 aprende o ano ouvindo o campo (teste 52), para de ouvi-lo e passa a corrigir a fase pela entrada vivida (este teste): assim ela prevê como o relógio v1, sem calendário escrito, olhando uma vez por ano.
- Ela não prevê melhor que o v1, e o ritmo não sabe nada da anomalia do ano.

Para o desenho da v0, isso sugere separar dois tempos:
1. **aprender o ritmo** ouvindo o mundo;
2. **depois, guardar o ritmo** e olhar só os eventos.

Isso é uma política de olhar decidida pela tarefa, e não um filtro que olha sempre. Fica como proposta, sem teste.

## Para a lista de defeitos de desenho

74. A conta prévia pôs F a 1–2 dias de V1 sem estimar a estabilidade da fase de um relógio travado com margem pequena (F₂ ≈ 2 × o desvio de frequência inicial), forçado por um campo que o teste 35 já tinha mostrado ruidoso no fim da seca. O teste 52 relatou frequências e períodos, mas nenhuma medida do espalhamento da fase entre anos, que teria antecipado o resultado.

Placar: 53 testes numerados (o 25 sem resultado), mais o teste do ato A. 53: J3 passou, J1 e J2 reprovaram. 74 defeitos nesta numeração, 1 emenda.
