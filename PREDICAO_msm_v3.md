# Previsão registrada antes de calcular (MSM v3): a escada sobrevive ao ciclo de 24 h?

**Registrada em:** 17/10/2026 (madrugada, UTC), depois da leitura do MSM v2 e antes de escrever o código da v3.

**Pedido da Ana:** "faça o Teste", sobre a pergunta: removido o ciclo diário, o degrau de 10–16 h cai e sobram 3 andares, ou a escada fica de pé?

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já abertos. Nada de outubro. Um julgamento por período.

**Ramo:** `exploracao/msm` (continuação), a partir de 29d1f29.

## Mudanças em relação à v2 (as únicas)

1. **Dessazonalização por variância:** s(h) = raiz da média de r² no minuto-do-dia h (h = 0…1439), calculada **em maio** (âncora, como nas rodadas anteriores), suavizada por média móvel circular de 31 min; r_des,t = r_t / s(h_t). Mesma dessazonalização aplicada aos sintéticos de validação (gerados sem ciclo, logo quase neutra) e, para comparação direta, nada é aplicado à v2 (já lida).
2. **Grade k = 1…5** (32 estados em k = 5), para que k* = 4 deixe de ser fronteira.
3. Sem réplica M (descritivo caro; o ponto já foi registrado na v2).

Tudo o mais como PREDICAO_msm.md + PREDICAO_msm_v2.md (Emenda 2): Student-t padronizada, BIC, validação com sintéticos k = 2 e 3 (b = 25, γ_k = 0,5, m₀ = 1,4, ν = 4), sementes 8026/8027.

## Classificação (por período; só vale se repetir)

- **"Escada fica de pé":** validação passa e k* ≥ 4.
- **"Cai para três":** validação passa e k* = 3.
- **"Menos que três":** k* ≤ 2.
- Validação reprovando → INCONCLUSIVO.

Descritivos: posição do degrau intermediário (está ou não em 8–16 h?), ganho de BIC do último degrau escolhido comparado ao da v2, razão b.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| "Escada fica de pé" (k* ≥ 4) nos dois períodos | ~65 % |
| "Cai para três" em algum período | ~35 % |
| k* = 5 em algum período | ~30 % |
| Degrau intermediário sai da faixa 8–16 h nos dois períodos | ~55 % |
| Ganho de BIC do 4º degrau cai menos que pela metade em relação à v2 | ~50 % |
| b ≥ 8 nos dois períodos (a escada continua "×10") | ~60 % |

## O que isto não decide

Se a escada é discreta ou uma rampa (um contínuo de escalas discretizado pelo modelo): o MSM impõe b único e não distingue as duas. Um ganho de BIC que decai geometricamente com k e não zera é compatível com rampa. Fica anotado como leitura, não como teste.

## Emenda 1 (registrada depois de ago–set produzir ajuste degenerado, antes de rodar de novo)

Ago–set (Actions run 39001860521; log em resultados/msm_v3_agoset_INVALIDO_emenda1.log): validação passou, mas o ajuste do real com k = 2 terminou em m₀ = 2,000 e ν = 2,16 (fronteiras), com BIC não monótono (k1 169248, k2 148246, k3 218060). Com m₀ → 2 um estado tem volatilidade → 0 e a densidade explode nos retornos exatamente nulos, que a dessazonalização por divisão conserva. Falha numérica do instrumento; a classe "menos que três" **não é lida**. Jun–jul (k* = 5, m₀ 1,52, ν 6,8, BIC monótono) foi um ajuste regular, mas será rodado de novo com o instrumento emendado para manter os dois períodos comparáveis.

**Mudanças (únicas):** limites internos m₀ ∈ (1,01, 1,95) e ν ∈ (2,3, 50); três pontos iniciais (volta ao desenho original da v1) e, por k, descarte de qualquer solução em que algum parâmetro fique a menos de 0,5 % do limite (marcada como degenerada e substituída pelo melhor ponto regular). Resto inalterado, inclusive as apostas. Última emenda da v3.

## Emenda 2 (registrada depois da rodada da Emenda 1 abortar, antes de rodar de novo)

Rodada 39005824801: o descarte de "qualquer parâmetro a menos de 0,5 % do limite" eliminou soluções legítimas (b na fronteira inferior quando k = 1, onde b não tem efeito; γ_k ≈ 0,999 como reparametrização válida da componente mais rápida) e, em k = 5, todos os pontos iniciais; o programa parou na validação, sem ler nada. **Mudança (única):** o descarte passa a valer só para m₀ a menos de 0,5 % do teto (1,95) e ν a menos de 0,5 % do piso (2,3), as duas degenerações que explodem a verossimilhança. Resto inalterado. O compromisso "última emenda" da Emenda 1 é substituído por este: a Emenda 2 corrige um erro introduzido pela Emenda 1, não o desenho original; se a rodada falhar de novo por instrumento, a v3 encerra INCONCLUSIVA.
