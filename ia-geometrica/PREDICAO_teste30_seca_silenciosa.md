# Predição do teste 30 (a seca silenciosa em Juara)

20/10/2026 · escrita antes de abrir os dados de clima (o download só contou linhas e campos vazios; ver clima/COBERTURA.md) · Ana Rigel

## De onde vem

Proposta da Ana, a partir de um texto trazido de fora: usar a v0 para perceber uma **seca silenciosa**, quando o solo profundo não se recupera mesmo com chuva na superfície. As correções feitas antes deste registro: a escada da v0 com passo diário tem τ ≈ 7 dias, 67 dias, 1,8 ano e 18 anos (os números do texto eram períodos de corte, não τ); a estação do INMET de Juara é a A914, com buracos grandes demais para ser entrada contínua; o INMET não mede umidade do solo; os testes 23 e 25 não têm relação com seca; cores e regimes do SGV não entram aqui.

## Dados

ERA5-Land (solo, temperatura, umidade, VPD) e ERA5 (chuva, ET0), via Open-Meteo, hora a hora de 2010 a 2025, ponto em Juara (−11,255; −57,520), agregados por dia. **Calibração 2010–2017** (climatologias, escolhas de leitura). **Medida 2018–2025.**

**Ressalva declarada:** a umidade do solo do ERA5-Land é calculada por um modelo de superfície a partir da mesma chuva e da mesma atmosfera que a v0 recebe. O teste pergunta se a v0 integra a água como esse modelo de solo integra, não se ela acerta o solo real de Juara. Para o solo real, só uma sonda.

## A verdade

Anomalia padronizada da umidade da camada **28–100 cm** em relação ao mesmo dia do ano (média e desvio da calibração, suavizados em 31 dias). **Dia de seca profunda:** anomalia ≤ −1. **Dia silencioso:** a camada 0–7 cm está com anomalia ≥ 0 (a superfície parece normal ou molhada).

## A v0 (sem mudança)

Um registro de quatro andares (λ₁ = 0,15, b = 10) sobre a anomalia diária de chuva − ET0. Seis leituras candidatas: os níveis R1, R2, R3 e os vincos R1−R3, R2−R3, R2−R4. A melhor é escolhida pela AUC na calibração, com o primeiro ano fora (andares enchendo).

## O nulo (o que um meteorologista usa)

SPI (só chuva) e SPEI (chuva − ET0) simplificados: soma da anomalia em 30, 90 e 180 dias, padronizada por dia do ano. Seis candidatos, a melhor escolhida pela AUC na calibração. Mesmo número de candidatos que a v0.

## Critérios (medida 2018–2025)

AUC diária: quanto mais seco o índice, mais alto o escore; positivo = dia de seca profunda. Intervalos por bootstrap em blocos de 90 dias (1.000 reamostras).

**J1, a v0 acompanha a seca profunda:** AUC da v0 em todos os dias da medida **≥ 0,80**, com o limite inferior do intervalo acima de 0,5.

**J2, a v0 vê a seca silenciosa melhor que o índice padrão** (a afirmação central do texto): nos dias silenciosos, AUC da v0 − AUC do nulo **≥ 0,03**, com o limite inferior do intervalo da diferença acima de zero. Se a medida tiver menos de 30 dias de seca silenciosa, ou menos de 30 dias silenciosos sem seca, J2 é **INCONCLUSIVO**.

## Apostas (Claude, antes de abrir os dados)

- **J1 passa: 70 %.** O solo de 28–100 cm acumula chuva − evaporação ao longo de semanas a meses; um registro com τ de 67 dias é quase isso.
- **A leitura escolhida da v0 é R2 ou R2−R3: 60 %.** O nulo escolhido é SPEI-90 ou SPEI-180: 65 %.
- **J2 passa: 10 %.** A v0 e o SPEI fazem quase a mesma conta (média exponencial contra soma em janela). Espero diferença entre −0,03 e +0,02 nos dias silenciosos. O que o texto chama de "vinco" é, aqui, um índice de seca com outro nome, a menos que a forma exponencial siga o solo melhor do que a janela reta, e é só isso que o teste pode mostrar.
- **J2 inconclusivo por falta de dias: 15 %.**

## O que fecha

- **J1 passa, J2 reprova (o que espero):** a v0 lê a seca profunda tão bem quanto o índice padrão, não melhor. Para Juara, o índice padrão (público, mensal) já faz o serviço; a v0 não traz um alarme novo de seca.
- **J1 e J2 passam:** a memória em escada segue o solo profundo melhor que uma janela reta quando a superfície engana; vale um teste com outro ponto (outra cidade de MT) antes de qualquer conclusão.
- **J1 reprova:** nem a v0 acompanha o solo profundo com esta entrada; a leitura dirá se falta a escala (andares) ou a entrada (VPD, radiação).
