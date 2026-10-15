# SGV — Saltos e memória V2b: reanálise DESCRITIVA de junho–setembro após controles positivos

**Data: 15/10/2026, posterior à execução de controles sintéticos V2.** Ramo `research/saltos-markov-v2-controles-20261015`. Este documento especifica a reanálise **antes de executar código V2b**, mas junho–setembro já foram examinados extensamente na V1. Logo V2b é **exploratório e não confirmatório**; nenhuma regra de sucesso científico é atribuída a esses meses.

## Escopo e mecanismos separados

- **Teste A observacional:** os retornos logarítmicos de BTCUSDT 1m são avaliados nas escalas 1,2,4,8 minutos por `M4(h)/h` e curtose empírica (incrementos sem sobreposição). **Não extrapolar para dt<1min**; o intercepto 1→8 min, se relatado, é descritivo e não um estimador identificável do coeficiente infinitesimal de Pawula.
- **Controles G/S causais por semana:** dados da semana `k−1` estimam AR(1) do retorno e AR(1) da *log-variância* dos resíduos, usando volatilidade de 60 minutos calculada estritamente com observações anteriores. Para a semana `k`, simula-se recursivamente volatilidade latente AR(1) endógena; G recebe choques gaussianos independentes e S reamostra os choques padronizados da semana anterior. **Nenhum `rolling(center=True)`, nem calibração com a semana avaliada.** Três sementes G (3026–3028) e S (2026–2028), e todas as semanas de cada período; as médias/mínimos/máximos das três réplicas são descritivas, não p-valores.
- **Teste B descritivo SGV original 3D:** usar as coordenadas `(E_norm,jerk,memory_flux)` do ramo V1 e régua de caudas ancorada em maio (sem alteração de definições). Reproduzir `memoria` da V1: `M_3D=Spearman(eps_t,média dos dez eps anteriores)`, em que `eps_t` é energia do próximo deslocamento normalizada por estimativa local `m2(x)` obtida nos 200 vizinhos na semana anterior.
- **Proxies 4D causais:** acrescentar respectivamente log do desvio dos retornos logarítmicos dos **30, 60 e 120 minutos anteriores** (`rolling(n).std().shift(1)`, sem futuro) e calcular `M_4D(n)`, `Red_n=1-M_4D(n)/M_3D`. Mesmos 5.000 tempos por semana e mesma semente da V1 em todos os braços. Não ajustar n com base na inspeção dos números.
- **Limite lógico:** Spearman de agitação padronizada **não é** o teste de Markov/Chapman–Kolmogorov; redução não identifica nem exclui dimensão latente. O quarto momento de um minuto **não prova** saltos físicos. O retorno bruto e as coordenadas SGV respondem a perguntas diferentes; não fundir os testes em um escalar de "campo verdadeiro".

## Comparações e integridade

- Períodos: `junjul` e `agoset`; nenhuma leitura de outubro nem de holdout reservado. Dados mensais com SHA-256 conferido pela função `E.carregar`; junho–setembro são **consumidos para fins confirmatórios**.
- Estatísticas A: mediana dos `M4(h)/h` semanais e curtose por escala, e faixas das três séries G/S; **não classificar saltos ou continuidade** em dados de 1 min.
- Estatísticas B: `M_3D, M_4D(30/60/120), Red(30/60/120)` em ambos os períodos, sem limiar de vitória e sem seleção posterior de janela. A estatística de M pode ser negativa; redução não é definida se M3≈0.
- Gates de engenharia: amostras finitas, semanas causais, seeds declaradas, `lag>0` para estimador de volatilidade; não mascarar falhas. Os resultados de controles sintéticos V2 anteriores devem permanecer imutados.
- **Decisão pré-fixada:** relato descritivo integral dos dois períodos, sem reclassificar o V1 como validado ou falsificado; destacar onde as caudas e volatilidade reproduzem o comportamento. Dados novos seriam necessários para qualquer classificação prospectiva.

## Execução

`python pipeline/reteste_saltos_markov_v2_mercado.py --periodo junjul` e `--periodo agoset`. O workflow de reanálise deverá registrar JSONs em `resultados/`; resultados só serão interpretados **após leitura de ambos os períodos**, sem alterar métodos ou limiares entre eles.
