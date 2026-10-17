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
