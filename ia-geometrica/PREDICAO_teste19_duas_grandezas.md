# Predição do teste 19 (não ver e errar: a régua declara as duas)

18/10/2026 · escrita antes de rodar · corrige o defeito 29 do teste 18, e só ele

## Pergunta

O teste 18 achou o corte de seis observadores desconhecidos em 600 de 600 casos e reprovou na cegueira porque declarava "não ver" (1 − |H|²) e o teste media "errar" (|1 − H|²). **Declarando as duas, a partir do mesmo Ĥ complexo, a régua acerta as duas no valor?**

## O que muda e o que não muda

- **Duas declarações, do mesmo espectro cruzado:** ν̂ = Σ S_xx (1 − min(|Ĥ|², 1)) / Σ S_xx (**não ver**: a fração da potência do mundo que a saída não contém) e ε̂ = Σ S_xx |1 − Ĥ|² / Σ S_xx (**errar**: a fração da potência do mundo que a saída não reproduz, com fase).
- **Duas verdades:** ν = Σ S_xx (1 − |H|²) / Σ S_xx com o ganho analítico de Ω (o que uma régua perfeita declararia) e ε = E‖x − y_limpo‖² / Var(x) (o resíduo; a verdade do teste 18).
- **Tudo o mais igual ao teste 18:** os seis Ω, escada-3 julgado e deriva relatado, N = 200.000, 100 sementes, Welch com 8.192 passos; os mundos via `lfilter` (iguais aos do 18).

## Critério (um julgamento, em escada-3)

Erro absoluto mediano |ν̂ − ν| ≤ 0,05 **e** |ε̂ − ε| ≤ 0,05, para cada um dos seis Ω. Relata-se ε − ν por Ω (o atraso em número) e os mesmos erros em deriva.

## Apostas

- **Passar: 65 %.** A favor: Ĥ já era bom o bastante para o corte; ε̂ usa o mesmo Ĥ com a fase, e ε é o que ν̂ errou por 0,04–0,09, logo ε̂ deve fechar. Contra: ν̂ contra ν ainda carrega o viés de Welch nas baixas frequências do Ω lento (λ = 0,003), que pode passar de 0,05 (aposto 40 % que o Ω 3 reprova em ν); e na média móvel os zeros do ganho são mal resolvidos por Welch e |1 − Ĥ|² pode errar na banda dos zeros.
- ε − ν mediano entre 0,03 e 0,10 nos Ω de primeira ordem e acima de 0,08 na cascata e na média móvel (60 %).
- Em deriva, ε̂ a ≤ 0,05 de ε nos seis (55 %): a deriva tem a potência na banda de transição, onde a fase pesa mais, e é lá que ε̂ se separa de ν̂.

## O que fecha

Passar: a régua mede, de um observador de forma desconhecida, o corte, o que ele não vê e o que ele erra, com erro conhecido; e o OBS-01 ganha as duas grandezas com nome. Reprovar só no Ω lento: resolução, limite declarado (segmentos maiores, série maior). Reprovar na média móvel: o estimador de Welch não resolve ganhos com zeros, e a régua precisa de um estimador de maior resolução para observadores de janela.
