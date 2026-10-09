# SGV-M12 — Nulos temporais com persistência, sazonalidade e regimes

**Pré-registro de implementação — 09/10/2026.** Ramo `research/m12-nulos-regimes-temporais`; `main` intocada. BTCUSDT spot 1m maio–julho/2026 e 1h 2020–2024 exclusivamente. É proibida leitura de períodos confirmatórios (1m desde agosto/2026 e 1h desde janeiro/2025).

## Motivação e pergunta

M11 reduziu o piso geométrico do registro e mostrou comportamento contraditório sob um nulo pooled simplificado (0/2 janelas 1m e 2/2 janelas 1h acima de q90). Essa comparação é insuficiente por não reproduzir memória, regimes, heterocedasticidade e calendário. O M12 investiga se o contraste muda quando as **duas fotografias sintéticas vêm do mesmo mecanismo calibrado exclusivamente ANTES da janela de avaliação**, utilizando nulos temporais com controles progressivamente mais ricos. **Não se testa causalidade, trading alpha ou tensão econômica.**

## Origem e fronteira temporal

- Quatro origens contínuas, não sobrepostas, selecionadas deterministicamente entre candidatas elegíveis: prefixo de **5000 candles (1m) ou 3500 candles (1h)** e janela seguinte 1500/1008 candles.
- `flow_coordinates` é calculada causalmente sobre observações disponíveis até cada candle (z, desequilíbrio agressor iota, atividade relativa nu). Nulos são calibrados **somente no prefixo**, sem usar valores do período de avaliação para definir parâmetros, blocos, estados ou limiares; somente timestamps futuros conhecidos servem para comparar horário do dia.
- O primeiro 30% da janela sintética define os postos marginais; as duas metades posteriores são reconstruídas com a mesma âncora. A distância M11 usa cascas GMM2 HDR50 grade 35³, registro ICP multistart e distância determinística à superfície de triângulos usando 256/512 pontos de quadratura.
- Mesmas sementes e especificação de nulo mantidas antes de inspecionar resultados. Simular **seis realizações por origem e modelo**. A unidade de comparação é a origem, não a realização.

## Quatro nulos concorrentes

**N0 — Bootstrap estacionário em blocos:** concatenar blocos circulares de comprimento L curto retirados somente de coordenadas trivariadas do prefixo; preserva correlações dentro do bloco mas destrói memória acima de L e sazonalidade sistemática.

**N1 — SF1-M5:** GARCH(1,1)-t para retornos e modelo de desequilíbrio agressor SF1; volume simulado por dinâmica de memória (lags 1,2,5,10) e primeiro harmônico do relógio diário, parâmetros estimados **somente no prefixo**, inovações de volume do histórico. Captura agrupamento de volatilidade por GARCH, memória de atividade e sazonalidade parametrizada, mas não reproduz necessariamente regimes prolongados nem todas as dependências cruzadas.

**N2 — Blocos condicionados por regime e relógio (L curto)** e **N3 — mesmos blocos com L longo:** a partir das coordenadas passadas, estimar um estado binário de volatilidade/atividade por média móvel dos últimos candles e um limiar mediano do prefixo; estimar transições de Markov entre estados separados por L; escolher blocos históricos conjuntos `(z,iota,nu)` condicionados ao estado simulado e à faixa de 6 horas do relógio conhecida para cada bloco futuro. Cada bloco é **contíguo no histórico**; sequências de blocos imitam persistência entre blocos via transição de estado. Se não houver candidato simultaneamente no mesmo regime e horário, registrar fallback para regime isolado, e se necessário falhar explicitamente. **Trata-se de aproximação heurística**, não um modelo semi-Markov validado nem garantia de preservar distribuição de durações, dependência longa ou sazonalidade intradiária.

Comprimentos: 1m `L=15/60`, 1h `L=12/36`; o mesmo L curto é usado no N0. Os dois modelos condicionais compartilham definição de estado, mas têm transições específicas ao seu L.

## Critérios e métricas

1. **Adequação antes do contraste geométrico:** comparar erro mediano dos nulos na `acf(nu,1)`, `acf(nu,10)`, `acf(|z|,1)`, `std(nu)`, `corr(iota,nu)` e perfil horário de `nu` em quatro faixas de seis horas. Adequação tem interpretação descritiva; não afirmar que um nulo seja ótimo por um único critério.
2. **Distância geométrica:** distância observada direta M11 com 512 pontos, por janela; distribuição de seis distâncias simuladas dentro de cada família. Reportar q10/q50/q90, diferenças observada–mediana e o indicador `observada > q90` somente quando ao menos quatro das seis réplicas forem válidas.
3. **Convergência numérica:** guardar diferença relativa 256→512; não comparar nulos onde a medição divergir ou a geometria falhar.
4. **Aptidão de estados e calendário:** reportar taxas de candidatos com relógio compatível, frequência empírica e persistência dos estados, número de blocos disponíveis e fallback. Não chamar *regime preservado* sem métricas de adequação.
5. **Sem interpretação confirmatória:** 4 origens e 6 réplicas oferecem no máximo um rastreio instrumental. q90 calculado com seis realizações é instável e não é nível de teste calibrado. As famílias são nulos distintos e nenhum controla completamente caudas, regimes macro ou transições reais. Não corrigir multiplicidade com p-values que não foram calibrados.

## Calibração sintética e portas

- Caminho de dois regimes artificialmente persistentes: o estimador de estados deve produzir transições mais persistentes que sorteios independentes, a amostragem manter a associação temporal dos três observáveis dentro de blocos e respeitar as faixas horárias quando há candidatos.
- Garantir seleção de dados só do prefixo: alterar a janela futura não altera parâmetros, catálogo, nem a série sintética gerada com a mesma seed.
- Rejeitar saltos temporais e sequências com falta de dados; não fabricar distâncias para malhas inválidas.
- Confirmar que M11 dá distância próxima de zero para malha idêntica e distingue deformação conhecida. Nenhuma modificação em M11.
- Os trabalhos reais só serão iniciados se a calibração e testes passarem.

## Entregáveis e decisão

Implementação `experiments/m12_nulos_regimes_temporais.py`, testes `tests/test_m12_nulos_regimes_temporais.py`, workflow `.github/workflows/m12-nulos-regimes-temporais.yml`, arquivos JSON/CSV por escala e relatório final de limites. Avançar a M13 apenas quando os nulos melhorados demonstrarem adequação temporal e houver condições para ampliar origens/réplicas. **Não abrir os dados confirmatórios nesta etapa.**
