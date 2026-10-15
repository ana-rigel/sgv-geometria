# Campo de agitação D(x) do espaço original na régua de caudas — exploratório (14/10/2026)

**Não é o H-DIF-01**, que fica congelado na régua gaussianizada. Só BTCUSDT 1m jun–jul/2026 (maio = âncora); outubro intocado. Script `campo_caudas.py` (lê os klines e as coordenadas como `nulls_space_ref.py`, cópia do script do ambiente de análise); saída `campo_caudas.json`.

**Régua** (definição da Ana, `cascas_btc.py`, espaço `orig_raw`): por coordenada, (x − mediana de maio) / (q99,5 de |x − mediana| em maio / 3), linear. Escalas obtidas: E_norm 2,254; jerk 0,001503; memory_flux 0,07897. SHA-256 das coordenadas brutas (linhas finitas, arredondadas a 12 casas): `3d3eb6eb…434b52eb` — para conferir contra o `cascas_btc.py`, que não está neste ambiente.

**Estimadores** (campo da semana k−1 avaliado nos minutos da semana k; persistência = campo da semana k+1 nos mesmos pontos): NW de banda fixa h = 0,45 (o do relatório do campo); kNN constante local (k = 200, tricúbico); **kNN localmente linear** (ajuste 1 do OBS-01 v2.1: resíduos de s ≈ m + B(x − x₀)) **com correção de amostra pequena** (ajuste 2: ÷ (1 − 4/ESS)). As fórmulas exatas do OBS-01 v2.1 não estavam disponíveis; estas são as formas padrão, a conferir. Nula de pipeline passa pela mesma régua com a mesma âncora.

## Cobertura da régua (jun–jul)

Curtoses preservadas: 11,4 / 11,7 / 9,4 (na régua gaussianizada caíam a −0,02 / −0,31 / −0,07, com teto |4,23|). Máximos |x|: 11,1 / 16,3 / 9,9. Fora do cubo [−2, 2]³: 7,1 % dos minutos; além de 3: 2,3 %.

## D por faixa de extremidade (max |xⱼ|)

| faixa | % minutos | D NW (h fixo) | D constante local | **D localmente linear** | ESS | persistência log D | ρ parcial Range₅ (LL) | nula: D LL | nula: ρ |
|---|---|---|---|---|---|---|---|---|---|
| < 1 | 75,3 | 0,67 | 0,33 | **0,31** | 87 | 0,57 | 0,000 | 0,40 | −0,012 |
| 1–2 | 19,3 | 1,13 | 0,90 | **0,77** | 83 | 0,54 | +0,043 | 0,69 | −0,068 |
| 2–3 | 3,7 | 1,92 | 1,86 | **1,40** | 78 | 0,55 | −0,002 | 0,98 | −0,080 |
| 3–5 | 1,4 | 2,23 | 3,34 | **2,05** | 68 | 0,47 | **+0,207** | 1,14 | −0,035 |
| 5–10 | 0,3 | 1,13 | 7,03 | **3,29** | 47 | 0,11 | — (n pequeno) | 0,91 | — |
| ≥ 10 | 16 min | — | — | — | — | — | — | — | — |

ρ parcial: log D contra log Range dos 5 min seguintes, controles fortes do H-DIF (σ 10/30/60, HAR 1d/1s, retornos 5/30, log-volume 10/60, hora) + log ρ (kNN); janelas de 5 min não sobrepostas.

## Leitura

1. **A agitação cresce com a extremidade, monotonicamente, só no estimador localmente linear:** 0,31 → 3,29 (×10,6) do núcleo à faixa 5–10. Na nula, 0,40 → 0,91 (×2,3). A parte extrema do espaço original é de fato muito mais agitada que o resto, e isso não é efeito das fórmulas.
2. **Os dois ajustes do OBS-01 fazem diferença exatamente onde a Ana previu.** O NW de banda fixa **subestima** nos extremos (1,13 na faixa 5–10, menor que nas faixas 2–3 e 3–5), porque poucos vizinhos caem na banda. A constante local **superestima** (7,03), porque mistura a variação da deriva dentro da vizinhança com agitação. O localmente linear fica entre os dois e é monotônico.
3. **Antecipação nos extremos (hipótese, não achado) — CORRIGIDO em 14/10.** O +0,21 da tabela vem de **uma** das cinco subamostras "1 a cada 5 minutos" possíveis, e foi a mais favorável. Na faixa 3–5 (972 minutos): defasagens 0 a 4 dão +0,207 / +0,074 / −0,020 / +0,008 / +0,058; todos os minutos, +0,088; um minuto por bloco de 5 min do relógio (616 janelas), **+0,125** (IC 95 % por bootstrap simples 0,047 a 0,203, estreito demais porque ignora a dependência dentro dos dias), contra +0,028 na nula (IC −0,05 a 0,11). Por quintil de D (já sem os controles), a amplitude seguinte além do esperado sobe de forma monotônica: −3,8, −1,4, −0,9, +1,6, +4,5 pontos de posto; na nula, sem padrão. **Estimativa honesta: entre +0,06 e +0,12, com incerteza grande.** Continua sendo hipótese para amostra nova (`sinal_faixa35.json`).
4. **Persistência cai nos extremos** (0,57 no núcleo, 0,11 na faixa 5–10): poucos minutos por semana nessa região; o campo extremo não se repete de uma semana para outra com a resolução atual.
5. **Uma direção do passo é quase determinística em todo o espaço** (menor autovalor de D ≈ 0 em ~100 % dos pontos, depois de tirar a deriva local): o memory_flux é Δ EMA(E_norm), quase uma função do passo de E_norm. A anisotropia útil é máx/médio ≈ 7–8.

## Limites

Exploratório; um período; seis faixas comparadas sem correção; janelas de 5 min dentro de semanas; ajustes do OBS-01 implementados pela forma padrão, sem o texto da v2.1.
