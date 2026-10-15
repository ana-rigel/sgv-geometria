# SGV-ID4 — Identificabilidade da memória além da volatilidade multiescala (PRÉ-REGISTRO)

**Registrado em 15/10/2026, antes de criar/rodar o código ou conhecer resultados ID4.** Ramo isolado `research/identificabilidade-4d-memoria-direcional-20261015`, a partir de `exploracao/volatilidade-multiescala@5c55d4a`. Não alterar V1/V2 ou qualquer holdout do SGV; não ler BTC ou outros dados financeiros.

## Questão

Uma estatística baseada **somente na agitação quadrática** consegue distinguir um modelo em que a volatilidade multiescala é o único mecanismo de persistência, de outro com **a mesma volatilidade e magnitudes dos choques**, mas persistência direcional adicional? Um teste de log-loss da direção futura condicionado no estado 3D, volatilidade conhecida e sinais recentes consegue distingui-los?

A meta é testar **identificabilidade** e **sensibilidade do observador**, não demonstrar que o BTC possui memória direcional ou exatamente uma quarta dimensão.

## Gerador emparelhado, inteiramente novo e conhecido

Por trajetória, simular estados independentes AR(1) de log-variância `hL[t]` e `hF[t]` com `rhoL=0.999`, `rhoF=0.90`, variâncias estacionárias `varL=0.30`, `varF=0.20`. `sigma[t]=0.0007*exp(0.5*(hL[t]+hF[t]-0.5))`. Gerar magnitudes dos choques `a[t]=|Z[t]|`, `Z~N(0,1)`.

Dois processos emparelhados em cada trajetória (mesmos `hL,hF,a`):
- **VOL_ONLY (nulo):** sinais `s[t]` iid equiprováveis ±1; retorno `r[t]=sigma[t]*a[t]*s[t]`.
- **VOL_PLUS_DIRECTION (controle positivo):** quatro sinais iniciais equiprováveis ±1; para t≥4, `s[t]=s[t-4]` com probabilidade 0,85 e `-s[t-4]` com probabilidade 0,15. Mesmo sinal marginal equiprovável e `r[t]^2` **exatamente idêntico ao nulo** em todos os instantes. A regra de ordem quatro insere memória de sinais adicional à volatilidade, sem alterar as magnitudes.

Não chamar essa dependência de memória longa, salto físico ou dimensão física adicional. Cada sistema possui um estado aumentado conhecido por construção.

## Coordenadas SGV

Construir de **cada preço sintético individual** `E_norm` como `E_raw=(close−EMA_0.05(close))/|EMA|` padronizado robustamente; `jerk=Δ²retorno_simples_1m`; `memory_flux=ΔEMA_0.05(E_norm)`. A referência de robustização e escala é obtida somente do prefixo **de aquecimento**, nunca da avaliação. Declarar que esta é uma implementação sintética equivalente em definições essenciais, não reprodução bit a bit dos parâmetros de `SGVConfig` do mercado. Usar as coordenadas e volatilidade verdadeira sincronizadas sem olhar o retorno seguinte.

## Partições e observador

**30 trajetórias emparelhadas**, cada uma de 10.000 passos após burn-in de 1.000 para `h`; 12 pares para treino, 6 pares para validação descritiva, **12 pares intactos para teste** (somente abrir após o código, preflight e modelo fixados; sem tuning pela validação). Prefixo de cada trajetória para âncora de escala: 1.000 passos; início dos rótulos no índice 1.100; horizonte um minuto.

Estatística **negativa de energia**: `U[t]=r[t]^2 / sigma[t]^2 = a[t]^2`, correlacionada por Spearman com a média dos dez valores anteriores `U[t-10:t]`. Como as magnitudes e a volatilidade são emparelhadas, esta estatística é **matematicamente idêntica em VOL_ONLY e VOL_PLUS_DIRECTION**, por construção. Esse resultado é um **contraexemplo de identificação**, não uma descoberta empírica. Como diagnóstico secundário, calcular a estatística do observador de agitação `r[t+1]^2/(sigma[t+1]^2 m_r(X_t))` com `m_r` condicionado em 200 vizinhos 3D e treino em prefixo independente; ela pode diferir por viés de condicionamento na representação.

**Classificador discriminativo principal:** prever sinal do retorno `s[t+1]`. Base observa `E_norm[t]`, `jerk[t]`, `memory_flux[t]`, `hL[t]`, `hF[t]`, `s[t]`, `s[t−1]`, `s[t−2]`; braço ampliado inclui `s[t−3]` (memória adicional verdadeira do gerador positivo). Este desenho é **mais informativo que apenas o 3D+volatilidade**, pois inclui três sinais históricos; evita um controle base artificialmente cego a dinâmica imediata. Ambos recebem as mesmas trajetórias e mesmos rótulos, e diferem em exatamente uma variável.

Fixar `StandardScaler+LogisticRegression(C=1, max_iter=1000)` sem busca de hiperparâmetros; ajustar **separadamente** nulo e positivo usando apenas suas 12 trajetórias de treino. Validação serve só para verificar execução, **sem escolha de variáveis ou limiares**.

## Endpoint e decisão antes do teste

`Δ_N = logloss(base)−logloss(base+lag4)` em VOL_ONLY, `Δ_D` equivalente em VOL_PLUS_DIRECTION.

- **Sensibilidade aprovada** se `Δ_D>=0.05` nat/observação e limite inferior do IC95 bootstrap por **trajetórias inteiras**, 2.000 réplicas, >0.
- **Especificidade aprovada** se `|Δ_N|<=0.015` nat/observação.
- **Demonstração de não identificabilidade do observador de energia:** diferença absoluta de estatística limpa <1e−12 em cada par emparelhado (deve passar por construção); não estimar p-valor dessa identidade.
- **Portão:** nenhum modelo deve treinar ou alterar hipóteses depois de abrir as 12 trajetórias de teste. Falhas, amostras não finitas ou hashes duplicados resultam em INCONCLUSIVO, não reposição seletiva. Resultados da memória 3D corrigida são somente descritivos.

**O resultado positivo mostrará:** um processo com volatilidade multiescala **e outra memória** pode ser indistinguível por um observador somente quadrático, enquanto um observador direcional apropriado o distingue. **Não mostrará:** que essa outra memória existe no BTC nem que volatilidade seja insuficiente na série real. Um resultado negativo exige revisar o instrumento sintético antes de qualquer conclusão financeira.

Conservar o resultado anterior `FECHADO` como classificação **pela regra própria e exploratória**, sem endossar unicidade causal. Protocolo assinado por ordem de commit, não por documentos administrativos.
