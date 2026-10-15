# SGV-ID4 — Freeze pré-teste e leitura de desenvolvimento (15/10/2026)

A hipótese e os limiares foram registrados no commit anterior ao código no arquivo `PREDICAO_ID4_VOL_VS_DIRECAO_20261015.md`. A implantação inicial está no ramo `research/identificabilidade-4d-memoria-direcional-20261015` e usa **apenas controles sintéticos independentes**. O C01 e as explorações M35, saltos/Markov e volatilidade-multiescala permanecem inalterados.

## Proveniência verificável antes de abrir teste

- Fonte Python congelada no Git blob SHA1 `471070b3d179d9bad50aaab3756ac1484008bd15`.
- JSON de modelos congelados no Git blob SHA1 `d99568bd2f4998a0f1ca8e6411ca6afa44135c4b`.
- Pré-registro no Git blob `85650afa5d9a0b35f317e8bf9dd1e53e1c4225e3`.
- Execução de pré-teste: GitHub Actions `38826542962`, status `success`: 9 verificações de sanidade, 12 trajetórias de treino IDs 0–11, validação descritiva 6 IDs 12–17, nenhuma geração dos 12 IDs de teste 18–29.
- Modelos comparados: regressão logística padrão com estado geométrico `(E_norm, jerk, memory_flux)` reconstruído separadamente em cada preço sintético, duas volatilidades latentes **verdadeiras** `h_slow,h_fast` e últimos três sinais, contra as mesmas variáveis acrescidas do quarto sinal (`sign_t_minus_3`) alinhado com o alvo `sign_{t+1}`.
- Dataset emparelhado em cada trajetória: `r_null²=r_direction²` por construção e caminho `sigma_t` idêntico. Isso torna um teste que dependa **somente** de energia observacional incapaz de distinguir as histórias, mesmo com volatilidade conhecida. Este é um contraexemplo proposital de identificação, não uma alegação sobre o BTC.

## Desenvolvimento, somente descritivo

| Condição | Log-loss base | Log-loss com sinal t−3 | Delta base−ampliado |
|---|---:|---:|---:|
| Somente volatilidade | 0,69315545 | 0,69316063 | −0,00000518 |
| Volatilidade mais memória de direção | 0,65959160 | 0,42553035 | +0,23406125 |

Esses seis pares de validação foram inspecionados e **não** podem justificar seleção de novas variáveis. Não alterar classificador, gerador, escala, limiar ou seeds após esta observação.

## Veredito futuro predefinido

Os **12 pares de teste** devem ser gerados uma única vez pelos mesmos parâmetros congelados e estratificados por trajetória. A hipótese instrumental passa somente quando:
1. Na condição positiva de memória direcional, delta de log-loss ≥ 0,05 nat/observação **e** limite inferior do bootstrap 95% por trajetórias inteiras > 0 (2.000 reamostragens).
2. Na condição nula sem memória direcional, |delta de log-loss| ≤ 0,015 nat/observação.
3. Igualdade **exata** da energia de retornos normalizados por volatilidade em cada par, verificada no gerador e nos testes.

Se qualquer gate falhar, registrar resultado negativo ou inconclusivo. O experimento não demonstra memórias adicionais no BTC. Nenhuma série real de mercado foi lida.

## Limite importante

O braço base é propositalmente forte (usa o estado 3D, os dois estados de volatilidade verdadeiros e três sinais prévios). O teste controla se o quarto atraso possui informação que não está nas variáveis anteriores **nesse gerador específico**. Não prova que todas as memórias temporais além da volatilidade seriam detectadas pelo mesmo lag. O observador original de agitação não é um teste completo de Markov; a identidade da energia neste par foi projetada para demonstrar sua não identificabilidade.

**Estado no momento da escrita:** modelos já congelados; teste final ainda não aberto. O próximo workflow exigirá comparação exata dos blobs acima e marcará a liberação antes de acessar IDs 18–29.
