# SGV-C02 — Resultado do portão geométrico V1: BLOQUEADO

**Data:** 14/10/2026. **Natureza:** calibração sintética, sem classificação, sem uso de mercado e sem qualquer abertura do holdout OOD de 490 pares.

## Proveniência

Gerador originalmente distribuído no pacote `SGV_C02_GERADOR_PILOTO_20261014.zip`, SHA-256 `4691266c21d313b3522577a5dfc6390c7dc654b8ee648ba8524a95bc50ebcd7a`. Os módulos numéricos C01 usados para ajustar GMM3, avaliar Fisher–Rao, entropia, energy e HDR foram copiados **byte a byte do C01 congelado**, ZIP SHA-256 `ed4c0307b64462f8f1292179b1a403070898422baae29384688be887b476d746`. Não houve acesso a treino, validação ou holdout C01 durante C02.

Piloto C02 V1: cinco famílias G3/S5/B3/R7/BS35 × sete transformações T0–T6; 35 pares exclusivamente da partição `calibration`, índice reservado 2.000.000, 750 A + 750 B independentes por par, GMM3 fixo, MC 32.000, malha 35³. **23 testes matemáticos locais aprovados**. Retorno de 26 variáveis em **33/35 pares**; falharam BS35-T1 e BS35-T2 por `HDR voxel masks degenerate`. Cobertura probabilística máxima |erro| = `0,010625`, dentro de 0,015; isso **não** prova precisão geométrica.

## Auditoria de precisão que invalida o portão V1

Grades 35³ e 49³, mesmas duas densidades ajustadas, mesmo limiar HDR e mesma caixa. **28 checagens** em sete pares de calibração (duas HDR × A/B); **20 passaram, 8 falharam** contra limite de variação relativa de 10% em volume/área. Todas as oito falhas são BS35; pior variação de volume **245,97%** (BS35-T1, HDR50, A). Em BS35-T1/T2, a HDR50 tinha em certos casos **apenas 2 voxels** na grade 35³, apesar de a malha poder apresentar fechamento topológico.

Exemplos: BS35-T1 HDR50 A 1,90→6,59 unidades cúbicas entre grades; T1 HDR50 B 5,07→11,03; BS35-T2 HDR50 B 3,00→4,68. Mesmo com cobertura MC correta, áreas/volumes não são numericamente robustos. **Portão de engenharia C02 V1 = FALHOU**; nenhum desempenho de classificador foi obtido e não se reivindica ganho incremental.

## Causa científica adicional

Em BS35, Student-t ν=3,5 tem quarto momento divergente; após a deformação banana `Y₂=X₂+s(X₁²−1)` com `s≠0`, a variância populacional de Y₂ é infinita. Portanto, covariâncias populacionais convencionais não têm referência finita nesse eixo, embora a aproximação GMM3 em amostras finitas produza matrizes SPD. Isso é parte da dificuldade OOD, mas **não** justifica aceitar erro de malha. Componentes GMM3 de peso ≈0,0013 ajustados a observações extremas podem expandir o domínio global, tornando a malha uniforme 35³ inadequada.

## Alternativa matemática em investigação, não validada

Para `p(x)=Σ_i w_i φ_i(x)` com K gaussianas, `p(x)≥τ` implica que existe i com `w_i φ_i(x)≥τ/K`. Assim a HDR é coberta por uma união finita de elipsoides componentais com limites matemáticos explícitos; os retângulos envolventes são um certificado conservador e permitem propor refinamento local. **O certificado não calcula HDR, volume, área, IoU ou componente conectado.** Um algoritmo adaptativo de malha e gates de convergência ainda devem ser implementados e validados antes de classificação.

## Artefatos e conclusão

A execução local gerou `C02_PILOTO_35_PARES_CALIBRACAO_MC32000.json`, `C02_SENSIBILIDADE_MALHA_35_49.json` (SHA-256 `7b26df211588035751227831dce58336f7e8e0eed321e31b099bb4ba5470e6c7`) e um pacote de auditoria `SGV_C02_AUDITORIA_GEOMETRIA_20261014.zip` (SHA-256 `76f93684ca22334475671c61532b84c25e8140bb837c757065c26f00c03697be`). O pacote contém o gerador imutado, fontes numéricos C01 copiados do freeze, scripts, testes, dados de calibração, manifesto e relatório. Uma cópia operacional completa foi mantida na conversa; esta nota no GitHub não equivale à transcrição integral dos binários.

**Decisão:** BLOQUEAR C02 V1 no portão instrumental. Não trocar seeds, omitir casos, flexibilizar tolerância nem abrir os 490 casos reservados. Qualquer novo extrator numérico deverá constar de **emenda C02.1 prospectiva**, com novo freeze antes de treino/validação e OOD. C01 confirmatório permanece encerrado.
