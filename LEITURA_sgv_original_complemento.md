# Leitura contra a previsão registrada (PREDICAO_sgv_original_complemento.md, commit 2107535)

Exploração.
- **Jun–jul:** rodou localmente.
- **Ago–set:** rodou no GitHub Actions (run 38799031936).
- **Paridade com o rascunho do H-SGV-01:** diferença 0 nos ρ semanais primários e secundários originais, no real e na nula.

## 1. Ago–set fora da amostra, controles primários

| Variável | jun–jul | ago–set | Semanas com o sinal | Nula ago–set | Classificação |
|---|---|---|---|---|---|
| log ρ (raridade) | −0,079 | **−0,107** | 9 de 9 | −0,003 | **Repete** |
| Deslocamento | +0,031 | **+0,061** | 9 de 9 | −0,012 | **Repete** |
| `mem_e` | −0,027 | **−0,018** | 8 de 9 | +0,008 | **Repete** (\|ρ̄\| = 65% de jun–jul) |

basin e n_obs acompanham log ρ, como no rascunho.

## 2. `mem_e` com o controle "fluxo"

O controle "fluxo" é: controles primários + log ρ, log tr D e c(x) do campo de fluxo + ν.

| | jun–jul | ago–set |
|---|---|---|
| Primário | −0,0274 | −0,0178 |
| Com o fluxo nos controles | −0,0260 (95%) | −0,0172 (97%) |

**Complementar** nos dois períodos. O fluxo não carrega a memória do esticamento.

## 3. `mem_e` com retornos de 60, 240 e 1.440 min nos controles

| | jun–jul | ago–set |
|---|---|---|
| Com retornos lentos | −0,0275 (100%) | −0,0189 (106%) |

**Esticamento próprio.** Não é alavancagem de prazo mais longo.

## Descritivo

| Variável | Com o campo original (rascunho) | Com o fluxo nos controles | Com retornos lentos |
|---|---|---|---|
| log ρ | −0,020 / −0,052 (25% / 49%) | −0,064 / −0,092 (**81% / 86%**) | 99% / 100% |
| Deslocamento | −0,030 / +0,001 (inverte / some) | +0,014 / +0,044 (46% / 71%) | 99% / 101% |

Os pares de valores são jun–jul / ago–set.

- **A raridade do plano (E_norm, jerk)** é em boa parte redundante com o campo do **próprio** original, mas **não** com o campo de fluxo: mantém 81% a 86%.
- **O deslocamento** continua sendo raridade vista de outro ângulo. Com o campo original nos controles, ele inverte em jun–jul e some em ago–set.

## Apostas

Todas as previsões acertaram:
- log ρ repete (~75%);
- deslocamento repete (~45%);
- `mem_e` repete (~45%);
- complementar (~50%);
- esticamento próprio (~40%).

Ressalva: o efeito de `mem_e` é pequeno, |ρ| de 0,02 a 0,03, frações de ponto percentual de R². Duas semanas de ago–set ficaram perto de zero (−0,001 e −0,002).

## Para o H-SGV-01 (rascunho; decisão de Ana)

- As três variáveis repetem fora da amostra. O rascunho fica mais sólido.
- Há evidência de **complementaridade**: a raridade do original e a memória do esticamento acrescentam ao fluxo quase sem perda. Isso pode virar hipótese registrada, testando cada variável com o fluxo nos controles.
- O deslocamento segue sendo raridade com outro nome.
