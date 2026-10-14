# SGV-C01 — Protocolo pré-execução: comparação controlada de HDR, Fisher–Rao e entropia

**14/10/2026 · estudo exclusivamente sintético · ramo `research/hdr-fisher-entropia-controle-sintetico`.** Este documento precede qualquer execução ou inspeção de resultados C01. Não modificar o experimento M8–M11, o M15, a `main`, nem ler arquivos de mercado. A etapa 1 consiste em testes matemáticos e piloto de engenharia; a avaliação final requer código congelado e registro de sementes separados.

## 1. Objeto e alegações separadas

Alegação 1, instrumental: as superfícies HDR50/HDR95, definidas no **mesmo espaço 3D fixo** para A e B, permitem medir deslocamento, volume, topologia e diferença de superfície de maneira reproduzível.

Alegação 2, complementaridade: para identificar tipos de transformação **sintética**, adicionar descritores HDR a um conjunto base aumenta desempenho fora da amostra ou melhora calibração/detecção com orçamento semelhante.

Alegação 3, nenhuma previsão: C01 não diz respeito a BTC, tensão de mercado, causalidade, interpretação humana ou rentabilidade.

**Ressalva lógica:** HDR é funcional da densidade; não acrescenta informação à distribuição completa conhecida. Testa-se apenas informação **não capturada pelas estatísticas resumidas escolhidas**.

## 2. Distribuições com verdade conhecida

Família positiva e normalizada: mistura finita de gaussianas 3D, `p(x)=sum_k w_k N_3(x | mu_k, Sigma_k)`, pesos positivos com soma 1, covariâncias simétricas definidas positivas. Separar o gerador da inferência.

Controles exatos por transformações afins: (0) identidade, (1) translação, (2) escala isotrópica, (3) rotação rígida em torno da origem/centro comum, (4) deformação anisotrópica determinante 1.

Transformações não afins: (5) perturbação de separação modal e (6) mudança de pesos; documentar efeitos concomitantes sobre média/covariância/entropia, não declarar isolação perfeita de um mecanismo.

Controle discriminante: misturas de pares simétricos `±a e_j` com `Sigma_j=I-aaᵀ e_j e_jᵀ` (0<a<1), em eixos diferentes, exibem **média zero, covariância I e entropia igual por simetria rotacional**, mas distribuições distintas. Comparar também uma gaussiana N(0,I). Essa construção permite refutar alegação de que momentos e entropia bastam para descrever toda a forma, sem atribuir exclusividade à HDR.

## 3. Métricas matemáticas

- **Momentos:** diferenças da média `||mu_B-mu_A||`, log determinante das covariâncias, norma Frobenius das covariâncias e espectros; registrar opção de coorientação e invariância.
- **Entropia:** `H(p)=-E_p[log p(X)]`, calculada com amostras independentes Monte Carlo e intervalo de erro numérico. Mudança `DeltaH=H(B)-H(A)`. Em uma transformação invertível comum `Y=T(X)`, `H(Y)=H(X)+log|det DT|` quando Jacobiano constante.
- **Distância de informação de distribuições:** `A(p,q)=int sqrt(pq) dx`, `D_sphere(p,q)=2 arccos A(p,q)`, com convenção geométrica explícita. Trata-se da distância no **ambiente não paramétrico das densidades sob a métrica clássica de Fisher–Rao (embedding por raiz quadrada)**, não necessariamente da distância geodésica **restrita à subvariedade paramétrica GMM**. Estimar por importância amostrando `m=(p+q)/2` e `A=E_m[sqrt(pq)/m]`; truncar estimativa ao domínio [0,1] apenas por erro Monte Carlo e registrar SE. Não confundir com `fr_cov` de M15, restrita a gaussianas centradas com covariâncias estimadas.
- **Energy distance:** `2 E||X-Y||-E||X-X'||-E||Y-Y'||`, amostragem pareada e réplicas.
- **HDR:** `R_alpha={x:p(x)>=tau_alpha}`, calibrar `tau_alpha` usando quantis da densidade avaliada sob amostras próprias; calcular grade 3D/marching cubes em domínio controlado, malhas fechadas sem truncamento, medir volumes e mudanças de casca com distância à superfície/descritores, auditando estabilidade 35³→49³ (ou maior após gate). **HDR50 e HDR95 não são entropia.** Não confundir casca HDR com transporte material de probabilidade.
- **Distância completa é referência oracular**, não comparador barato; qualquer transformação detectável pode alterar afinidade apesar de nenhuma mudança de entropia.

## 4. Ordem de trabalho e critérios de aprovação

**Portão 0 (antes dos resultados):** testes para normalização numérica das misturas, entropia da gaussiana simples conhecida, afinidade identidade ≈1, simetria A↔B e rotação com conservação exata de entropia/momentos; efeito de translação nos descritores; exemplos de momentos e entropia equiparados.

**Portão 1 (calibração sintética):** instrumentos reproduzíveis com seeds explícitas; volume/massa HDR estáveis à grade dentro da tolerância de engenharia fixada antes da avaliação; intervalo de erro e pares independentes. Ações corretivas devem ser documentadas antes da confirmação.

**Portão 2 (comparação fora da amostra):** gerar novas misturas e transformações, separar rigorosamente sementes de treino e teste por família geradora; comparar classificador base (`momentos + DeltaH + D_sphere + energy`) com base+HDR, algoritmo, custo/regularização e hiperparâmetros pré-fixados, mesmo conjunto de folds e normalização somente no treino. Primário: diferença de log-loss médio nos pares de teste independentes, com intervalo por bootstrap no nível do par gerador. Secundário: balanced accuracy por tipo, taxas de falso alarme e curvas de calibração. Um ganho isolado em exemplos vistos ou mais parâmetros não basta.

**Critério de fracasso:** se diferença primária não melhorar com intervalo excluindo zero em replicações independentes e ganho prático definido no protocolo executável, não alegar utilidade incremental nesse gerador. Se estimador HDR não passar gates de massa, grade ou tempo/custo, encerrar ou reclassificar como estudo de engenharia. Repetir avaliação no mesmo holdout depois de ajustar método é proibido.

## 5. Limites e resultados anteriores

Os M8–M11 implementaram e calibraram parcialmente geometria **HDR50 em coordenadas gaussianizadas**; M15 comparou M11 com `fr_cov` e energy em sintéticos e encontrou sensibilidades complementares sob ressalvas de calibração. Nenhum deles comprovou ganho incremental em relação a entropia e distância de Fisher–Rao entre misturas completas. C01 não reabre resultados anteriores e não reusa dados financeiros.

Referência auditada: [nota científica de 14/10/2026](https://github.com/ana-rigel/sgv-geometria/blob/research/nota-hdr-fisher-entropia-20261014/reports/SGV_NOTA_HDR_FISHER_RAO_ENTROPIA_20261014.md).

## 6. O que se pode comunicar durante o piloto

São válidos apenas afirmações de implementação, propriedades analíticas e resultados de testes de consistência. Números produzidos em piloto não são evidência confirmatória nem poderão ser usados para ajustar os critérios da avaliação fechada sem novo protocolo e novo conjunto de amostras.
