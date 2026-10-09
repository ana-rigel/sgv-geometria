# SGV-M5 — Validação conjunta de controles SF1 (protocolo pré-execução)

**Data:** 2026-10-09. **Ramo isolado:** `research/m5-validacao-conjunta-sf1`.

## Pergunta
Entre SF1 original, +memória de volume, +sazonalidade e +ambos, alguma variante melhora a **fidelidade conjunta** das séries `(z,iota,nu)` em replays exploratórios sem degradar a memória curta? Isso é diagnóstico de adequação do simulador, não validação de um índice de estresse ou nova lei geométrica.

## Ajustes em relação ao M4
- A disponibilidade de sazonalidade depende de **três ciclos diários completos**, amostra utilizável de pelo menos 1500 observações e dados em sequência; não se aplica um mínimo arbitrário de 3000 candles a dados de 1h. Prefixos: 5000 barras 1m e 2000 barras 1h, ambos suficientes em duração, desde que contínuos.
- Os modelos alternativos **alteram somente volume** e preservam o mesmo preço e o mesmo desequilíbrio `iota` que o SF1 original a cada semente. Múltiplas métricas de preço e fluxo serão comuns por construção e não fornecerão evidência de superioridade dos modelos alternativos.
- Em cada origem: mesmo caminho SF1 base, mesmas sementes para comparar variantes, prefixo passado exclusivamente para o fit; janelas posteriores somente para diagnóstico. A inovação de volume dos modelos alternativos não mantém obrigatoriamente o acoplamento residual fluxo-volume original, limitação explicitada.

## Amostragem e estatísticas
- BTCUSDT spot exclusivamente exploratório: 1m maio-julho/2026; 1h janeiro/2020-dezembro/2024. Conferência de arquivos na allowlist e checksum do downloader. Nenhum mês confirmatório será lido.
- Até 8 origens cronológicas sem gaps, escolhidas determinística e uniformemente das elegíveis por índice, e 8 trajetórias SF1 por origem e variante. Os segmentos de avaliação de origens distintas **não devem se sobrepor**.
- Avaliar erro absoluto de mediana simulada versus observado: `acf(nu,1)`, `acf(nu,10)`, `std(nu)`, `corr(|z|,nu)`, `corr(iota,nu)`, `acf(iota,1)`, `corr(z,iota)`, `acf(|z|,1)`. Métricas de preço/fluxo imutáveis são controles.
- **Critério conjunto primário pré-especificado**: média de erros absolutos padronizados em quatro métricas sensíveis a volume. Escalas fixas `[0.15, 0.15, 0.25, 0.15]` para `acf(nu,1), acf(nu,10), std(nu), corr(|z|,nu)`. A média é uma *função de perda diagnóstica*, não um p-valor.
- Critérios secundários: (a) redução da perda mediana frente a SF1, (b) degradação mediana de ACF(nu,1) não maior que 0.04 pontos absolutos e (c) percentual de origens que melhoram. Declarar `sem vencedor` se não houver variante com perda menor e gate ACF1 satisfeito. Todas as análises são exploratórias e sensíveis às escalas de normalização da perda.
- Disponibilizar CSV por origem/variante/métrica e JSON agregado, incluindo motivos de indisponibilidade. Testes sintéticos verificam invariância preço-iota, causalidade do fit e sazonalidade em 1h.

## Não inferir
Não se infere causalidade, informação nova, desempenho preditivo, estados físicos, curvatura Fisher–Rao intrínseca nem estresse do BTC. Mesmo melhoria de métricas marginais não garante simulações morfológicas adequadas; verificar dependências conjuntas e regimes antes de voltar às superfícies HDR.
