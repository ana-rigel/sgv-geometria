# Previsão registrada antes de calcular (v2): cascata ou cauda? Concavidade em q baixo e espectro dos retornos padronizados

**Registrada em:** 16/10/2026, depois da leitura da v1 (LEITURA_multifractal.md) e antes de escrever o código da v2.

**Pedido da Ana:** "Sim vai pra 2".

**Status:** exploração, **não** confirmatória. Jun–jul e ago–set já abertos. Nada de outubro. Um julgamento por período.

**Ramo:** `exploracao/multifractal` (continuação), a partir de dbe9872.

## O que a v1 ensinou

κ = 2ζ(2) − ζ(4) é dominado pela cauda de 1 min e pela sua gaussianização: a série embaralhada (caudas iguais, sem agrupamento) deu κ maior que o real. Para separar **cascata** (hierarquia de escalas de volatilidade) de **cauda** (distribuição marginal gorda), a v2 usa duas medidas que respondem à cauda de forma diferente da v1.

## Medidas

1. **Concavidade em q baixo:** κ₁ = 2ζ(1) − ζ(2), com ζ ajustada até 240 min como na v1. Para i.i.d. de variância finita e cauda gorda, ζ(2) ≈ 1 e ζ(1) ≳ 0,5 (a razão ⟨|r|⟩/√⟨r²⟩ sobe ao gaussianizar), logo κ₁ ≲ 0. Para cascata lognormal, ζ(q) = qH − λ²q(q−1)/2 e κ₁ = λ² > 0. **Os sinais são opostos:** é o discriminador.
2. **Espectro dos retornos padronizados:** z_t = r_t / σ̂_{t−1}, com σ̂ = HAR de `estimativas` (médias de r² em 10, 60 e 240 min), **atrasado em 1 minuto** para que r_t não entre no próprio denominador. Se σ̂ captura toda a cascata, z é aproximadamente i.i.d. e seu espectro deve ser igual ao do z embaralhado. Medimos κ(z) = 2ζ(2) − ζ(4) e κ₁(z) sobre z, com os mesmos τ e q.

Séries: real; M (5 réplicas); embaralhado (5 permutações dos retornos de 1 min, e, para (2), 5 permutações de z).

## Classificação (por período; só vale se repetir)

**(1) Cascata, por κ₁ dos retornos brutos:**
- **"Cascata além do M":** κ₁_real > máx κ₁_M e > máx κ₁_embaralhado.
- **"Cascata como o M":** mín κ₁_M ≤ κ₁_real ≤ máx κ₁_M, e > máx κ₁_embaralhado.
- **"Sem cascata além da cauda":** κ₁_real ≤ máx κ₁_embaralhado.

**(2) Resíduo após σ̂, por κ₁(z):**
- **"Resíduo de cascata":** κ₁(z_real) > máx κ₁(z_embaralhado).
- **"σ̂ absorve a cascata":** senão.

Descritivos: ζ(q) completas; κ(z) de q alto; H.

## Limitações declaradas

- κ₁ é uma diferença pequena de inclinações; com dois meses, o envelope do embaralhado pode ter largura comparável ao sinal. Se o envelope embaralhado cruzar zero por mais de ±0,02, o teste (1) é fraco e a leitura dirá.
- σ̂ HAR causal de 1 min é um estimador ruidoso da volatilidade instantânea; z conserva ruído de estimação, que infla as caudas de z e pode imitar "resíduo". Por isso o nulo de (2) é o **z embaralhado**, que carrega o mesmo ruído.
- Sazonalidade intradiária permanece em (1); em (2) σ̂ a remove em parte.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| κ₁_embaralhado ≤ 0 nos dois períodos (o discriminador funciona como previsto) | ~70 % |
| κ₁_real > máx embaralhado nos dois períodos (há cascata além da cauda) | ~65 % |
| "Cascata como o M", dois períodos | ~40 % |
| "Cascata além do M", dois períodos | ~25 % |
| "σ̂ absorve a cascata", dois períodos | ~55 % |
| κ(z) real < κ_real da v1 (padronizar afina a cauda aparente) | ~80 % |

## O que confirma e o que não

- **Cascata como o M + σ̂ absorve:** a hierarquia de escalas do BTC de 1 min é a que duas memórias de volatilidade produzem, e o σ̂ do cubo já a contém. Fecha a pergunta "multifractal" nestes dados: cauda gorda + agrupamento de poucas escalas.
- **Cascata além do M, ou resíduo após σ̂:** há estrutura de escala que nem o M nem o HAR capturam. Candidata a hipótese sobre a escala rápida; não indicador.
- Em nenhum caso há direção, previsão ou lucro.
