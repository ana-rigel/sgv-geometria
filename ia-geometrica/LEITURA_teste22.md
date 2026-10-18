# Leitura do teste 22 (OBS-01, etapa um: a rede recorrente sintética) — PASSOU na rede linear; a tanh grande ensinou o limite

**Predição:** PREDICAO_teste22_rnn_sintetica.md (d53c2cb), antes de rodar. **Resultado:** resultados_teste22.json. Um julgamento (rede linear); as duas tanh relatadas. Sem emenda.

| versão | corte a ±30 % | f_c verdade / estimado (mediana) | \|ν̂ − ν\| mediano | \|ε̂ − ε\| mediano | cobertura (coerência ≥ 0,5) | nos três ao mesmo tempo |
|---|---|---|---|---|---|---|
| **linear** | **97/100** | 4,03 × 10⁻³ / 3,91 × 10⁻³ | **0,003** | **0,013** | 1,00 | 76 |
| tanh, entrada 0,1 | 84/100 | 4,03 × 10⁻³ / 5,25 × 10⁻³ | 0,011 | 0,048 | 1,00 | 49 |
| tanh, entrada 3 | 29/100 | 4,03 × 10⁻³ / 6,96 × 10⁻³ | 0,113 | 0,705 | **0,91** | 6 |

Critério (rede linear): (a) corte ≥ 80: sim (97); (b) ν ≤ 0,05: sim (0,003); (c) ε ≤ 0,05: sim (0,013). **Passou.** Terceira passagem do projeto, em 22 julgamentos. Apostas: 60 % em passar, certa; tanh pequena nos três em ≥ 60 sementes (errada: 49); tanh grande com cobertura < 0,8 (**errada**: 0,91); corte verdadeiro entre 1/300 e 1/30 (certa: 1/250).

## O que o resultado diz

**Uma rede de 32 unidades com constantes de tempo de 3 a 300 passos, acopladas, lida por uma projeção, é medida pela régua como um filtro é:** corte a 3 % do verdadeiro, "não ver" a 0,003, "errar" a 0,013. A régua não sabe que há 32 unidades; o espectro cruzado vê a rede inteira como um só observador, e a verdade analítica (a função de transferência matricial) confirma que esse observador equivalente é o que ela mede. A etapa um do OBS-01 está feita no linear.

**A não linearidade pequena custa pouco** (corte 84/100, ν a 0,011, ε a 0,048 da linearização), e o que custa é sistemático: o corte estimado sobe (5,25 contra 4,03 × 10⁻³), porque a tanh comprime os picos e a rede responde, na média, mais rápido do que a linearização diz.

**A não linearidade grande é o limite, e a régua não o declara.** Com entrada de escala 3 a rede satura: o corte estimado vai a 7 × 10⁻³ (70 % acima), "não ver" erra 0,11 e "errar" 0,7. E a cobertura por coerência fica em **0,91**: a régua acha que alcança. A coerência cai pouco porque uma rede saturada ainda responde de forma coerente a um mundo lento; ela não "ruidifica" a saída, ela a deforma. A coerência mede ruído, não deformação. A aposta de 65 % em cobertura < 0,8 estava errada, e esse é o erro mais útil do teste: **a régua, como está, não distingue um observador linear lento de um observador não linear saturado**, e um modelo de IA é o segundo caso.

## O que fecha e o que não

- Fecha: a régua mede redes recorrentes lineares de muitas escalas (etapa um, linear). E fecha que a coerência não é detector de não linearidade.
- Não fecha, e é o próximo instrumento: como a régua é também o mundo (ela escolhe a entrada), ela pode medir a mesma rede com **duas amplitudes** de entrada; um observador linear dá o mesmo Ĥ nas duas, um não linear não. A diferença entre os dois Ĥ é uma medida de não linearidade que não depende da coerência, e é natural para o OBS-01, onde a entrada é nossa. Teste 23, com predição própria.

## Para a lista de defeitos de desenho do projeto

34. Cobertura por coerência tomada como "onde a régua alcança": só mede ruído; deformação por saturação passa com coerência alta. O OBS-01 precisa de um teste de amplitude.

Vinte e dois testes, dezenove reprovações, **três passagens**, trinta e quatro defeitos. Sexta cláusula para o OBS-01, nomeada antes de ser testada: **a régua mede a mesma rede em duas amplitudes; se Ĥ muda, o observador não é linear e as cláusulas 1–5 valem só por amplitude.**
