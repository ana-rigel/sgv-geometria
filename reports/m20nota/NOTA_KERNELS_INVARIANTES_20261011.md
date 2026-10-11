# Nota exploratória (Claude, 11/10/2026) — kernels 3D invariantes a rotação resolvem o H±?

**Contexto:** o M20e propôs, para o M20f, "kernels multivariados invariantes a rotações". Antes de abrir um experimento, uma checagem rápida com as duas ferramentas padrão desse tipo, nos mesmos geradores do M20d/M20e (`make_truth`, rotação aleatória por trajetória):
- **HSIC com kernel gaussiano** no vetor 3D inteiro, banda pela mediana (invariante a rotação);
- **covariância de distância (dCov)** entre x_t e x_{t+1} em ℝ³ (invariante a rotação).

Nulo: 100 trajetórias iid (N0) por tamanho, limiar = quantil 95%; 40 trajetórias por cenário. **Nulo conhecido** (condição favorável, sem ajuste no prefixo). Script: `scripts/m20_nota_kernels_invariantes.py`. **Não pré-registrado; serve só para orientar o desenho.**

| N | Estatística | H+ | H− | VOL |
|---|---|---|---|---|
| 500 | HSIC gaussiano 3D | 7,5% | 7,5% | 67,5% |
| 500 | dCov 3D | 0% | 7,5% | 15% |
| 1800 | HSIC gaussiano 3D | 2,5% | 10% | 100% |
| 1800 | dCov 3D | 2,5% | 7,5% | 45% |

**Leitura:** as ferramentas invariantes padrão também **não** detectam o H± — nem com 1.800 pontos e nulo conhecido. A dependência do H± é fraca, de alta frequência (sin 2x) e vive numa única direção entre três; um kernel global "dilui" o sinal nas duas direções de ruído. Com a direção verdadeira (oráculo, M20d) o HSIC-1D chega a ~90–95% em 1.800 pontos: **o gargalo é informacional (achar uma direção fraca com ~1.000 pontos), não falta de invariância**. Um M20f com kernels invariantes provavelmente repetiria o resultado negativo do M20e.
