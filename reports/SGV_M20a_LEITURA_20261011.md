# SGV-M20a — Leitura científica do teste sintético de trajetórias e acoplamentos
**Data:** 11/10/2026. **Execução:** https://github.com/ana-rigel/sgv-geometria/actions/runs/38158683864
**Ramo:** research/m20-trajetorias-transicoes. **Dados:** EXCLUSIVAMENTE sintéticos.
**Resultado operacional:** 6/6 testes pytest passaram. Piloto e ensaio integral executados.
**Portões do pré-registro:** todos verdadeiros, sem alteração dos parâmetros ou limiares após observar os resultados.
**Artefato:** SGV-M20a-resultados-sinteticos (ID 11709428069; inclui resultados_sinteticos.json, piloto.json e logs).

## 1. Verdades geradoras e delineamento
Modelo linear trivariado X[t+1]=A(beta) X[t]+epsilon[t], epsilon~N(0,I-AA^T), X[0]~N(0,I).
A(beta)=[[0.65,-beta,0],[beta,0.65,0],[0,0,0.65]].
Cenários: beta=0; beta=+0.22; beta=-0.22; beta=0 com deriva determinística
em x_0 ao longo de 1.200 amostras (deslocamento final 1.4).
A covariância marginal estacionária é I nos três casos sem deriva, por
identidade algébrica AA^T+(I-AA^T)=I. As autocovariâncias univariadas em lag1
também são idênticas; a covariância cruzada defasada antissimétrica não é.
Calibração: 320 trajetórias independentes geradas do nulo beta=0.
Avaliação: quatro grupos independentes, 240 trajetórias em cada.
Limiar por estatística: quantil superior 95% da calibração; alarme estritamente acima.

## 2. Taxas observadas (não estimativas de ganho preditivo)
| Estatística | beta=0 (nulo) | rot +0.22 | rot -0.22 | deriva |
|---|---:|---:|---:|---:|
| W2 gaussiano entre metades (endpoint) | 2,50% | 0,83% | 0,00% | 100,00% |
| Comprimento traj. W2 gaussiano | 2,92% | 1,25% | 0,00% | 17,50% |
| Custo pares consecutivos | 4,58% | 5,00% | 5,42% | 4,17% |
| Excesso do custo sobre limite inferior W2² | 4,58% | 5,00% | 5,42% | 4,17% |
| Corrente temporal antissimétrica (valor absoluto) | 4,58% | **100%** | **100%** | 5,42% |
| Covariância defasada (Frobenius contra 0.65 I) | 5,42% | **100%** | **100%** | 50,83% |
| Deslocamento das médias entre metades | 1,67% | 1,25% | 0,00% | **100%** |

Obs.: números extraídos dos logs do próprio Actions; o JSON no artefato contém
contagens exatas (denominador 240), intervalos Wilson e outras estatísticas.

## 3. Portões pré-definidos
- E1, identidade de estacionariedade: PASSOU.
- E2, falso alarme da corrente <=10%: 4,58%, PASSOU.
- E2, poder da corrente >=80% em ambas rotações: 100%/100%, PASSOU.
- E2, medida W2 estática <=15% de alarmes nas rotações: 0,83%/0%, PASSOU.
- E3, endpoint W2 detecta >=80% da deriva suave: 100%, PASSOU.

## 4. Conclusão matemática
A distribuição marginal estacionária N(0,I) NÃO identifica o sentido de
circulação. As distribuições p_t são constantes, e sua velocidade W2
populacional é nula mesmo que o campo de transição tenha componente rotacional.
Para detectar o sentido da circulação, a medição deve observar q(x_t,x_t+1)
ou estatísticas equivalentes dos pares ordenados.

Este caso distingue **geometria das marginais** e **estrutura do acoplamento temporal**.
Não demonstra uma informação inédita atribuível à geometria: o comparador
**convencional da covariância cruzada defasada obteve os mesmos 100% de poder**.
A estatística de corrente usada é ela própria uma função da covariância
cruzada defasada, e portanto redundante por construção neste experimento.
O custo médio de transporte observado e seu excesso escalar não detectaram
a rotação porque a família escolhida mantém invariantes relevantes desses custos.

## 5. Limitações e integridade
- Cenários lineares Gaussianos com parâmetros nulos conhecidos (oráculo),
  não nulos ajustados a um prefixo como M14. O resultado não resolve calibração
  sob incerteza de ajuste, dependência sobreposta nem transferência para BTC.
- W2 aqui é uma proxy exata entre Gaussianas de momentos, não transporte ótimo
  empírico entre misturas GMM, nem um campo inferido unicamente por continuidade.
- O protocolo diz por engano que foi incluído "no mesmo commit" do código;
  registro factual: protocolo 486bb607, código c2c34f87, testes a86f2a99 e
  workflow 25d4c746 — quatro commits SEQUENCIAIS, com protocolo registrado
  antes do código e da execução. A distinção não afeta os limiares pré-fixados.
- Não houve acesso a dados BTC nem uso ou reabertura do confirmatório M19.
- Não há controle de multiplicidade entre as métricas secundárias; resultados
  do ensaio são prova de mecanismo sintético e não confirmação de vantagem econômica.

## 6. Próximo passo científico
O M20b deverá procurar situações onde a estatística de transição usada no M20a
**não é suficiente**: dinâmicas com mesmas marginais e mesmos momentos até
segunda ordem (inclusive defasados), mas diferentes cópulas ou correntes de
ordem superior; controles HMM/VAR/energy e testes kernel-MMD em pares
(X_t,X_t+1), além de transporte condicional.
Exigir calibração aninhada prefix-only, transparência sobre múltiplas escolhas
e ganho sobre os melhores comparadores convencionais antes de qualquer BTC.
