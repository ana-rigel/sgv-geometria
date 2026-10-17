# Leitura do teste 1 (deriva) — REPROVADO

**Predição:** PREDICAO_teste1.md (c0f3171), antes de rodar. **Resultado:** resultados_teste1.json. Um julgamento; sem emenda.

| φ | V média (vantagem da pilha sobre o melhor registro único) | envelope (100 sementes) | melhor λ único |
|---|---|---|---|
| 0 | −0,3 % | −2,3 a 0,0 | 0,05 |
| 0,5 | **−10,9 %** | −21,0 a −9,0 | 0,95 |
| 0,9 | **−56,1 %** | −95,8 a −47,6 | 0,95 |
| 0,99 | **−92,4 %** | −186,1 a −72,6 | 0,95 |

Critério: (a) V > 0 nos três φ > 0: **não**; (b) monotônica crescente: **não** (decresce); (c) nula em φ = 0: sim. **Reprovado.** Apostas: 55 % em passar, errada; 70 % em (a), errada; 60 % em (b), errada; 85 % em (c), certa; "V(0,99) entre 2 e 15 %", errada.

## O que o resultado diz

A pilha perdeu, e perdeu mais quanto mais memória o mundo tem. O motivo está na arquitetura, não no ruído: num AR(1) o previsor ótimo é φ·x_{t−1}, isto é, **uma memória de um passo**; o registro único com λ = 0,95 é quase isso. A v0 herdou de março λ₁ = 0,15, um andar mais rápido com constante de tempo de ~7 passos. Ela é cega, por construção, à estrutura de um passo, que é toda a estrutura que esse mundo tem. É a cegueira espectral agindo contra a própria mente: o andar mais rápido da pilha define o que ela consegue ver, e aqui o mundo vive abaixo desse corte.

A leitura por mínimos quadrados também mostrou um defeito de instrumento: os andares lentos são quase colineares e os pesos explodem (−8,4 no andar 4 em φ = 0,5), sinal de mau condicionamento; uma regularização (ridge) seria o conserto. Fica registrado, não aplicado: mesmo com pesos bem comportados, a pilha não teria como representar x_{t−1}.

## O que fecha e o que não

- Fecha: com λ₁ fixo em 0,15, a pilha v0 não rastreia melhor que um registro único em mundos AR(1). O teste 1, como foi escrito, está respondido: não.
- Não fecha: se a pilha com λ₁ **livre** (em pé de igualdade com o nulo, que teve λ livre) acrescentaria algo. Isso é outro teste, com predição própria, e a aposta que eu faria agora: a pilha com λ₁ livre empata com o registro único em AR(1) puro (não há duas escalas para somar) e só ganha em mundos com duas ou mais escalas (o mundo do teste 4). Isto é, o teste 1 estava mal posto como teste da pilha: um mundo de uma escala não pode premiar uma mente de várias.

## Para a lista de defeitos de desenho do projeto

1. λ₁ herdado de março sem perguntar ao mundo qual é a sua escala mais rápida.
2. Mundo de uma escala só para testar uma arquitetura de várias.
3. Leitura por mínimos quadrados sem regularização.

Três erros, nenhum escondido. O teste 2 segue conforme o projeto, com o que este ensinou escrito antes.
