# SGV-C01 — Fase I: relatório de calibração local do oráculo

**Data:** 14/10/2026. **Ramo:** `research/hdr-fisher-entropia-controle-sintetico`. **Escopo:** engenharia sintética exclusivamente; nenhuma avaliação confirmatória de ganho incremental, nenhum dado financeiro.

## Execução local

- Python e bibliotecas numericamente instaladas na sessão de trabalho.
- `PYTHONPATH=. pytest -q tests/test_c01_instrumentacao.py` → **12 testes aprovados**.
- `python scripts/c01_portao1_calibrar.py --out reports/c01_portao1_calibracao.json` → **28/28 verificações aprovadas**.
- Sete casos de verdade conhecida T0–T6, duas densidades por caso (A/B), HDR50/HDR95, comparação em grades **35³ e 49³**.
- Tolerâncias pré-execução do gate local: erro de cobertura absoluta < 0,015; desvio relativo de volume e área entre resoluções <= 10%; malhas fechadas e não truncadas.
- Piores desvios observados nas 28 verificações: **volume relativo 2,2777%**, **área relativa 1,4873%**, **cobertura absoluta 0,76875 p.p.**.
- Caso T6, densidade B, HDR50: **duas componentes conexas** na malha, de acordo com modo raro separado. Não confundir contagem topológica da malha com diagnóstico de risco financeiro.
- Testes passaram para densidade GMM3, geração independente, invariância analítica de média/covariância sob T3, diferença entre `fr_cov` e `FR_ambient`, entropia de gaussiana e variação analítica sob escala, energy distance e malha.

## Resultados que NÃO podem ser alegados

1. Nenhum teste da classificação multiclasse definitiva, nenhum ganho de log-loss, nenhuma vantagem incremental HDR vs Fisher–Rao/entropia/energy em casos novos.
2. Não há medição de incerteza de parâmetros de GMM reajustados, nem de taxa de erro tipo I em séries temporais.
3. O sucesso é local; o workflow de GitHub foi criado para réplica na infraestrutura remota, mas o sucesso dele exige consulta posterior ao respectivo run. Não anunciar CI aprovado sem evidência.
4. As 28 verificações compartilham modelos de verdade e não são 28 experimentos estatisticamente independentes; são **checagens de engenharia** de combinações já definidas.
5. Além das checagens numéricas, falta auditar integridade, reprodutibilidade e precisão dos futuros ajustes GMM3 com 750 observações por braço.

## Integridade

Origem do ramo: protocolo científico documental preservado; `main`, M8–M11, M15, M35 e períodos reservados não tocados. A API de GitHub recebeu somente arquivos novos em `experiments/`, `tests/`, `scripts/`, workflow e este relatório. Arquivos de avaliação final ainda não criados nem executados.

**Próximo gate:** confirmar CI remota e congelar manifest de oráculo antes de construir a etapa de estimação e comparação pareada fora da amostra.

**Arquivos de execução:** `experiments/c01_oraculo_hdr_fisher.py`, `tests/test_c01_instrumentacao.py`, `scripts/c01_portao1_calibrar.py`, `.github/workflows/c01-calibracao-sintetica.yml`.
