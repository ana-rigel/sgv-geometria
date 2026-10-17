# Leitura: MSM v5, volume na equação de observação (jun–jul e ago–set/2026)

**Predição:** PREDICAO_msm_v5_volume_observacao.md + Emenda 1, registradas antes de cada rodada. **Rodadas:** Actions 39031639278 (jun–jul concluído; ago–set falhou sem log) e 39036063353 (ago–set com a Emenda 1).

## Validação

| | jun–jul | ago–set |
|---|---|---|
| sintético k = 2, δ 0,5 | k* = 2, δ̂ 0,505 | k* = 2, δ̂ 0,501 |
| sintético k = 3, δ 0,5 | k* = 3, δ̂ 0,495 | k* = 3, δ̂ 0,498 |

O instrumento recupera k e δ com precisão nos dois períodos.

## Real

| | jun–jul | ago–set |
|---|---|---|
| k\* | **4** | 2, **degenerado** (m₀ no teto 1,95 e ν no piso 2,3 em todos os pontos iniciais de k = 1 e 2) |
| δ̂ | 0,467 | 0,78 (num ajuste degenerado) |
| ν̂ (v2: 6,3 / 2,75) | **33,6** | 2,33 (piso) |
| escalas 1/γ | 14,8 min · 3,2 h · 1,8 d · 23 d | — |
| ΔBIC por degrau (v2: 5192 / 1828 / 908 e 7969 / 4241 / 2456) | 2171 / 846 / 385 | não monótono (4232 / −1578 / 1558) |
| **Classe** | hierarquia própria | **INCONCLUSIVO** (cláusula da Emenda 1) |

## Veredito

**Sem veredito: só um período tem leitura.** Jun–jul, com instrumento validado, diz "hierarquia própria": o volume do minuto entra com δ̂ ≈ 0,47 (quase a mistura de distribuições pura, ½), absorve a cauda quase inteira (ν̂ de 6,3 para 33,6: a inovação vira praticamente gaussiana), e **mesmo assim a escada de quatro andares fica**, com ganhos de BIC pela metade dos da v2 mas ainda de centenas. Ago–set não admite ajuste regular, como já não admitia na v3: o modelo quer um estado de volatilidade quase nula (m₀ → teto) e uma cauda mais gorda do que a t permite (ν → piso). Um período não conta; fica como observação forte, não como resultado.

## O que ago–set está dizendo sobre o instrumento (hipótese, não medida)

Nas duas versões em que ago–set degenerou (v3 e v5), o padrão foi o mesmo: m₀ no teto. Um estado com multiplicador 2 − m₀ ≈ 0,05 serve para absorver **retornos exatamente nulos** (minutos sem mudança de preço), que a Student-t de escala normal penaliza. A hipótese é que ago–set tenha mais minutos mortos (preço parado, volume baixo) que jun–jul; com o volume na observação isso piora, porque dividir por (v/v̄)^δ com v pequeno infla a escala justamente onde o retorno é zero. Verificação pendente: fração de retornos exatamente nulos por período (não calculada aqui; os dados de ago–set não estão neste contêiner). Instrumento futuro: inovação com massa discreta em zero (ou mistura), antes de qualquer v6.

## Apostas

| Aposta | Prob. | Saiu |
|---|---|---|
| Validação passa nos dois | 65 % | sim |
| δ̂ entre 0,3 e 0,6 nos dois | 65 % | não julgável (jun–jul sim, 0,47) |
| ν̂ maior que o da v2 nos dois | 75 % | não julgável (jun–jul sim, e muito: 33,6) |
| "Hierarquia própria" nos dois | 45 % | não julgável (jun–jul sim) |

## O que fecha e o que não

- Não fecha nada pelo critério; a pergunta "o volume absorve a escada?" segue aberta com uma resposta parcial e forte em jun–jul: **não absorve; absorve a cauda**.
- Registra uma limitação estrutural do MSM-t para este ativo em períodos com retornos nulos: três degenerações em ago–set (v3, v5 duas vezes). O próximo instrumento precisa tratar o zero antes de voltar a perguntar.
- Em nenhum caso há direção, previsão ou lucro.
