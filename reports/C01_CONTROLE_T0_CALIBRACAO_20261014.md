# SGV-C01 — Auditoria T0 de falso alarme (14/10/2026)

**Escopo:** controle sintético do mesmo gerador, exclusivamente engenharia. Nenhum dado BTC, nenhuma partição oficial de teste, nenhum classificador supervisionado. Código: `scripts/c01_t0_null_calibration.py`; testes: `tests/test_c01_t0_null.py`. Esta nota relata execuções locais, não certifica GitHub Actions.

## Desenho realizado

120 pares A/B independentes de `T0`, com 750 observações por braço e GMM3 reajustado em cada braço. Todos os pares usam IDs de calibração a partir de 1.000.000, fora dos IDs que serão reservados à comparação supervisionada. Divisão interna: 40 pares para escalar 12 descritores HDR50/HDR95 pelo q75; 40 pares para estimar q95 do máximo dos 12 desvios escalados; 40 pares independentes para medir alarmes com limiar congelado. Alarme estritamente `score > limiar`. Não alterar estatísticas ou limiares depois de observar o terceiro grupo. A inferência de taxa nominal 5% é **diagnóstico**, não confirmação de calibração.

## Execução original com 8.000 pontos por integração MC

- Ajustes válidos: **120/120**.
- Alarmes no terceiro grupo: **4/40 = 10,0%**; Wilson95 aproximadamente **[3,96%, 23,05%]**.
- **12/120** pares tiveram ao menos um erro de cobertura HDR50/HDR95 superior ao gate absoluto de 0,015.
- Medianas T0: Fisher–Rao ambiente `0,30200`, Fisher–Rao covariâncias `0,11583`, energy `0,00535`, |delta entropia| `0,03923`, centro HDR50 `0,09654`, perda IoU HDR50 `0,21630`, tensor HDR50 `0,08017`.
- Interpretação: o orçamento numérico de 8.000 pontos apresentou cobertura insuficiente em alguns pares; a diferença estimada entre duas amostras do mesmo gerador é material.

## Diagnóstico adicional do orçamento MC, 32.000 pontos

As **mesmas 120 sementes observacionais** foram reavaliadas com MC=32.000, sem troca das 750 amostras A/B de nenhum caso e sem alterar o algoritmo/12 descritores. Logo, **não constitui repetição estatística independente**. O objetivo foi testar precisão numérica, não procurar o melhor limiar ex post.

- Ajustes válidos: **120/120**.
- Erros de cobertura maiores que 0,015: **0/120**.
- Alarmes no terceiro grupo, com escala e limiar recalculados pelo protocolo previamente fixado nos dois grupos próprios: **2/40 = 5,0%**; Wilson95 **[1,38%, 16,50%]**.
- Medianas T0: Fisher–Rao ambiente `0,30296`, Fisher–Rao covariâncias `0,11583`, energy `0,00535`, |delta entropia| `0,03558`, centro HDR50 `0,09627`, perda IoU HDR50 `0,21838`, tensor HDR50 `0,07893`.
- Não atribuir a diferença de alarme 4→2 exclusivamente ao orçamento MC sem estudo adicional. Não selecionar a execução de 32k como 'evidência de sucesso' ignorando a anterior: ambas ficam preservadas.

## Julgamento e portões

1. **Instrumentação:** 35 testes locais passaram (29 anteriores + 6 para isolamento de grupos, aplicação de limiar e fechamento em falha).
2. **Falso alarme:** o estimador conjunto ainda não pode ser declarado calibrado nominalmente em 5%. O intervalo 95% com 40 pares avaliados é amplo, e verificações repetidas no mesmo conjunto não são confirmação nova.
3. **Precisão numérica:** MC=32k eliminou falhas de cobertura nesses pares. Isso é benefício instrumental no conjunto estudado, não garantia universal de cobertura; os custos de execução aumentam.
4. **Comparador do projeto:** não comparar os valores brutos de FR, energy e HDR entre si como se tivessem mesmas unidades. Não inferir que um valor FR≈0,303 seja erro de implementação: `fr_ambient` é a distância **entre duas densidades GMM3 reajustadas** do mesmo gerador, não a distância entre geradores verdadeiros (zero).
5. **Limite inferencial:** a classificação oficial sete classes (T0–T6) contra momentos + entropia + Fisher–Rao + energy permanece **não executada**. Os descritores HDR do estágio II não estão congelados ainda quanto a dimensionalidade e custo.

## Reprodutibilidade

Executar `python -m pytest -q tests/test_c01_oraculo.py tests/test_c01_instrumentacao.py tests/test_c01_estimacao.py tests/test_c01_t0_null.py`, depois `OPENBLAS_NUM_THREADS=1 python scripts/c01_t0_null_calibration.py --out reports/c01_t0_null_calibration_mc32000.json`.

Execução local de 32k: SHA-256 do JSON gerado `ccb29f78389ae1a0d9689771b836dffd8babef87ee64c2405c093f3216e0da24`. O hash pode mudar se versão da biblioteca/ambiente modificar arredondamentos, embora os gates sejam esperados reproduzíveis.

**Estado GitHub Actions:** workflows de sintético, estimação e T0 adicionados ao ramo. Ainda é necessário conferir as execuções reais no painel; sem afirmar CI remoto aprovado.

**Decisão:** preservar os dois diagnósticos e não abrir a partição de teste. Antes da classificação, definir política para dimensão extra HDR, amostras faltantes e orçamento numérico igualitário entre comparadores; calibrar em conjuntos verdadeiramente novos se a reivindicação for taxa nominal.
