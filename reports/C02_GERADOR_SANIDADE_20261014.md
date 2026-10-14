# SGV-C02 — Início de implementação e sanidade do gerador (14/10/2026)

**Natureza:** relatório de engenharia inicial; **sem classificação, sem inferência de ganho, sem abertura de amostra OOD**.

O protocolo C02 foi registrado em `reports/PROTOCOLO_SGV_C02_OOD_NAO_LINEAR_20261014.md` antes da implementação e das verificações.

## Implementação local preliminar
Arquivos no ZIP `SGV_C02_GERADOR_PILOTO_20261014.zip` armazenado na conversa: `sgv_c02/experiments/c02_generators.py`, `sgv_c02/tests/test_c02_generators.py`, `sgv_c02/README.md`.

- Geração das famílias de desenvolvimento G3 (mistura gaussiana), S5 (mistura Student-t com 5 graus de liberdade), B3 (mistura gaussiana deformada por banana invertível).
- Famílias reservadas R7 (mistura gaussiana multimodal anelar com pesos desiguais) e BS35 (mistura Student-t ν=3,5 com deformação banana); **nenhum caso da partição `ood_test` foi gerado**, embora a matemática do gerador possa ser inspecionada no grupo de calibração.
- Transformações sintéticas T0–T6 e nuisance compartilhado em cada par; 750 observações A e B independentes.
- Separação de seeds SHA-256 por finalidade, classe, família, repetição e split; recusa explícita de `ood_test` e recusa de famílias reservadas em `training` e `validation`.

## Resultados locais de engenharia
`cd sgv_c02 && PYTHONPATH=. python -m pytest -q tests/test_c02_generators.py` → **7/7 testes aprovados**. Primeira tentativa de rodar o teste fora da pasta (sem configurar `PYTHONPATH`) falhou apenas na importação; corrigido o caminho, sem alteração matemática do gerador.

ZIP local identificado por SHA-256 `4691266c21d313b3522577a5dfc6390c7dc654b8ee648ba8524a95bc50ebcd7a`. Esse hash é da versão **local**; não confundir com artefato de fonte já integrado ao GitHub. **Os códigos do gerador e dos testes ainda não foram transferidos para o ramo pelo conector.** O GitHub contém protocolo e esta nota, enquanto o ZIP da conversa fornece cópia executável.

## Gates ainda pendentes
1. Revisar formalmente transformações e distinguibilidade T0–T6 por família, especialmente T3 e o significado de T5/T6 no gerador com Student-t/deformação.
2. Implementar a estimação fixa GMM3 e a extração dos mesmos 14+12 descritores do C01 sobre amostras C02, mantendo a aproximação probabilística explícita.
3. Preflight numérico sob caudas pesadas e superfícies HDR: cobertura, malha fechada, sensibilidade à resolução e falha fechada.
4. Só depois processar treino/validação e congelar modelos. OOD permanece interditado até congelamento e liberação separados.

**Conclusão:** prontidão inicial do gerador demonstrada por 7 testes locais; nenhuma hipótese científica nova considerada aprovada. C01 permanece encerrado e intocado.
