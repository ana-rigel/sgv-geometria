# Notas da fumaça (17/10/2026) — instrumento v0, antes de qualquer teste

Rodado: `python ia-geometrica/v0.py --fumaca` (3 sementes, 3.000 passos, cinco mundos). O código roda de ponta a ponta; nenhum critério foi avaliado. `--teste N` recusa rodar enquanto não existir `PREDICAO_testeN.md`.

## O que a fumaça mostrou e fica registrado como item de instrumento

1. **Colapso C_j sai negativo** (−0,9 a −50). A definição provisória divide T_j ponto a ponto por T_{j+1}, que é pequena e ruidosa, e isso infla a dispersão em vez de reduzi-la. No SGV a escala era um σ̂ suavizado (HAR), não um valor instantâneo. **Antes do teste que usar C_j** a escala deve ser uma versão suavizada de T_{j+1} (média móvel com a constante de tempo do andar j+1), e a mudança fica registrada na predição daquele teste, não feita em silêncio agora.
2. **Cegueira por andar satura em ~1,0** nos andares 2 e 3: as frequências de corte λ_j/2π são muito baixas (0,0024 e 0,00024 ciclos/passo) e quase toda a potência da tensão fica acima delas. A medida é correta mas pouco discriminante; a predição do teste que a usar deve dizer se a lê em escala log de frequência ou como "fração abaixo do corte", que é o complemento e varia mais.
3. **A política de olhar funciona mecanicamente:** com θ = 1 na régua e n_max = 8, olha 25–28 % dos passos; o erro sobe de 1,6 para 2,3–2,4 (sem custo contabilizado ainda). É só fumaça; o teste 2 define c, θ e n_max.
4. **O regime na régua é muito mais parcimonioso que o relativo** (ruptura em 0,3–1,9 % dos passos contra 37–41 %): o detector de março passa um terço do tempo em "ruptura" num mundo de deriva suave. É exatamente o que o teste 3 vai julgar; aqui é só o cheiro.

Nada disto é resultado. Os quatro testes começam quando a Ana pedir, um por vez, cada um com a sua predição.
