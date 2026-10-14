# SGV-U2 — resultado (13/10/2026)

Pré-registro: `PREREGISTRO_U2.md` (commit f1dcdb3, antes do código). Código: `gerar.py`, `classificar.py` (commit seguinte, antes dos resultados). Única alteração depois disso: uma casca de A inválida (cobertura 0,945) derrubava a execução; passou a contar como invalidez do M11-I nas 7 comparações da réplica. O desenho não mudou. 630 comparações (3 famílias × 30 réplicas × 7 mecanismos), N = 750, grade 25³, entradas em ordem canônica. Validação deixando uma família inteira de fora.

## Floresta aleatória (classificador registrado como principal)

| Classe | M11-I | convencional | combinado | M11-I − conv (IC 95%) | Aposta | Saiu |
|---|---|---|---|---|---|---|
| nenhum | 0,44 | 0,73 | 0,68 | −0,29 (−0,41; −0,17) | empate | **errou**: o M11-I tem nulo ruidoso |
| translacao | 0,69 | 0,98 | 0,98 | −0,29 (−0,39; −0,19) | empate ou pior | acertou (pior) |
| escala | 0,53 | 0,93 | 0,91 | −0,40 (−0,51; −0,29) | empate ou pior | acertou (pior) |
| rotacao | 0,30 | 0,42 | 0,41 | −0,12 (−0,27; +0,01) | pior | na direção, IC toca o zero |
| bimodal | 0,24 | 0,22 | 0,27 | +0,02 (−0,09; +0,14) | ligeiramente melhor | **errou**: empate, os dois ruins |
| curvatura | 0,59 | 0,43 | 0,41 | +0,16 (+0,02; +0,29) | ligeiramente melhor | acertou |
| caudas | 0,30 | 0,84 | 0,78 | −0,54 (−0,66; −0,43) | pior | acertou |
| **F1 macro** | 0,433 | 0,641 | 0,632 | −0,21 (−0,26; −0,16) | conv > M11-I | acertou |

Combinado − convencional (F1 macro): −0,009 (−0,031; +0,014). Aposta: ganho < 0,03 — acertou: o M11-I não acrescenta nada ao painel convencional.

## Regressão logística (segundo classificador)

F1 macro: M11-I 0,398, convencional 0,628, combinado 0,655 (combinado − conv +0,027; IC −0,001; +0,055). Curvatura **inverte**: M11-I sozinho 0,34 contra 0,51 do convencional, mas o combinado chega a 0,73 (+0,22 sobre o convencional). Bimodal empata de novo (0,24 vs 0,22).

## Outros números

- **Invalidez do M11-I:** 4 % na família gaussiana, 12 % na assimétrica, 20 % na t₆ (cobertura insuficiente da grade: as caudas saem do cubo). Por classe: de 8 % (bimodal) a 21 % (escala).
- **θ não identificável:** 33–47 % das comparações, em todas as classes — inclusive na rotação (39 %).
- **ΔD > 0,01:** bimodal 54 %, curvatura 35 %, nenhum 7 %, caudas 0 %. O ΔD é de fato um marcador de não convexidade, mas não separa bimodal de curvatura (as duas acendem), e por isso o M11-I confunde as duas.
- **Generalização entre famílias:** o M11-I cai para 27 % de acerto quando testado na família assimétrica sem tê-la visto (convencional: 67 %).

## Leitura

As apostas acertaram 5 de 7 classes e as duas apostas globais; erraram em `nenhum` (o M11-I é pior até para dizer "não mudou nada") e em `bimodal` (nenhum dos painéis vê bem bimodalidade com momentos casados). A única vantagem do M11-I é a curvatura, e ela é frágil: aparece sozinho com a floresta (+0,16), some no combinado com a floresta, inverte sozinho com a logística e reaparece no combinado com a logística (+0,22). Isso fica abaixo do que o pré-registro chamou de "rotulador de forma": é um sinal de não convexidade que às vezes ajuda a reconhecer curvatura, dependendo de como é combinado. Detector, classificador geral e marcador de mudança nula: não.

Consequência prática para o SGV: a casca continua útil para ver (navegador), o ΔD pode entrar como um indicador entre outros num painel convencional, e nenhuma afirmação de "o SGV explica o mecanismo" se sustenta sem esse painel ao lado.

## Limites

Efeitos de tamanho moderado fixados a priori, sem curva de dose-resposta; grade 25³ (a oficial é 35³/49³); N = 750 iid, enquanto o mercado tem 1.500 minutos autocorrelacionados; o painel convencional também não tem uma variável direta de bimodalidade (p. ex. coeficiente de bimodalidade de Sarle por projeção), e foi isso que deixou os dois empatados em bimodal.
