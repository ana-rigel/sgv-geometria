# SGV-C01 — Resultado confirmatório único (14/10/2026)

**VEREDITO: HIPÓTESE PRIMÁRIA APROVADA, exclusivamente no experimento sintético predefinido.** Este documento registra **uma única abertura** dos 280 pares reservados; encerra a hipótese C01 original. Não implica informação além da distribuição completa ou previsão financeira.

## Proveniência
- Ramo criado diretamente do **freeze pré-holdout** `research/c01-freeze-pre-holdout-20261014@24543c8f937a7e558ca6b838a3fd02ed16f89dcd`; nem `main` nem os ramos experimentais anteriores foram modificados.
- ZIP operacional congelado, SHA-256 `ed4c0307b64462f8f1292179b1a403070898422baae29384688be887b476d746`.
- Manifesto verificado SHA-256 `9e880cb7606743f52d6213ece44278aceb5395dae8d76f855c8b7cbba7811fd2`; 44 testes locais aprovados e validação reproduzida sem retreinar.
- Liberação única gravou `HOLDOUT_RELEASED` antes de gerar amostras. Encerramento: `CONFIRMATORY_COMPLETED`.
- **280 pares, 40 por classe T0–T6**, com 750 observações em cada braço A/B; **280 válidos**, nenhuma falha, nenhuma identidade duplicada, nenhuma interseção dos SHA-256 A/B; cobertura HDR no limite de 0,015 (máximo absoluto observado 0,01434375).
- Dois modelos persistidos e **não modificados**: regressão logística com escalonamento fixo, treino original de 560 pares. Modelo base: momentos + delta de entropia + Fisher–Rao de covariâncias gaussianas + Fisher–Rao ambiente entre densidades + energy distance (14 descritores); modelo ampliado: mesmas 14 + 12 medidas HDR50/HDR95 (26).
- Comparação em famílias GMM3 sintéticas; Monte Carlo 32.000 e malha 35³; **zero acesso a BTC, qualquer mercado ou dados humanos**.

## Endpoint primário e julgamento pré-definido

`Delta = logloss(base14) - logloss(base14+HDR12)`.
Regras cumulativas: `Delta >= 0,03 nats/par` e `limite inferior do IC95 bootstrap pareado estratificado por classe > 0` (2.000 réplicas, seed 202610142800). Portão de validade: mínimo 38/40 pares por classe; falhas não podem ser repostas.

| Medida | Base (14) | Base + HDR (26) |
|---|---:|---:|
| Log-loss | 0,07898360621702434 | **0,022134025962886557** |
| Balanced accuracy | 0,9821428571428571 | **1,0000000000** |
| Macro-F1 | 0,9821422990199362 | **1,0000000000** |
| Erros de classe | 5/280 | **0/280** |

**Delta = +0,05684958025413777 nats/par.** IC95 = **[+0,04123669156147212; +0,07517219146594187]**. **Passou ambos os critérios**. 259/280 pares obtiveram menor perda individual no modelo ampliado.

Ganho médio por classe, secundário: T0 +0,03465; T1 +0,10358; T2 +0,00465; T3 +0,03299; T4 +0,02173; T5 +0,12659; T6 +0,07375. Ganho heterogêneo; T2 quase redundante apesar da vitória agregada.

## Auditoria independente de leitura dos resultados

Um script read-only, fora do executor, recalculou logits e softmax dos coeficientes congelados, perdas por exemplo, ganhos e o bootstrap estratificado de 2.000 réplicas. Concordou integralmente até erro <1e-12, confirmou 280 IDs únicos, não repetição de amostras A/B e cobertura máxima de 0,01434375. **Nenhuma segunda geração de teste foi realizada**.

Hashes:
- `RESULTADO_FINAL.json`: `5966724e6faf11e76ca8a2891aacec1fe291b9064c1118b745acb45df6e71831`.
- `TEST_CASES.json`: `6dd54e06fe505d6d09426b6cfaa4f32e6583036987c4db603dff8465044c70d9`.
- Pacote integral de resultado e freeze: `C01_RESULTADO_CONFIRMATORIO_20261014.zip`, SHA-256 `8cb158c0c527f83a59a57a9e1e2941ab4f269adeab73a6972af0a2e900892723` — salvo separadamente na conversa/Biblioteca, não anexo automaticamente a este commit.

## Alcance e limitações

O resultado demonstra **ganho operacional condicional** para classificar sete transformações sintéticas conhecidas sob regressão logística de configuração fixa e comparação de resumos estatísticos. HDR é uma transformação não linear da **mesma** densidade estimada: não gera informação independente da distribuição completa. O Fisher–Rao usado entre misturas é distância **ambiente** por afinidade integrada, não necessariamente a geodésica intrínseca da variedade GMM.

A amostra de teste é independente em realizações, mas usa a **mesma família geradora** do treinamento/validação; não demonstra generalização fora desta família ou em dados reais/temporais. Diferenças de regularização e representação podem contribuir para o ganho. Os controles pós-validação de dimensionalidade são exploratórios e não fazem parte do endpoint primário.

**A hipótese C01 original está ENCERRADA como positiva no domínio sintético especificado.** Proibido reabrir o mesmo holdout para seleção de variáveis, ajuste de classificadores, otimização de nulos ou nova confirmação. Novas hipóteses precisam de novo desenho e amostras novas; períodos BTC reservados continuam protegidos.
