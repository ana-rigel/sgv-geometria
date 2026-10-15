# Previsão registrada antes de calcular: com volatilidade em várias escalas, sobra memória no real?

**Registrada em:** 15/10/2026, antes de escrever o código desta rodada e antes de calcular qualquer coisa com o novo sintético.

**Pedido da Ana:** "faça isso", o sintético multiescala proposto em `LEITURA_volatilidade_escondida_v2.md`.

**Status:** exploração, não confirmatória. Nada de outubro é lido, e nada congelado muda.

**Ramo:** `exploracao/volatilidade-multiescala`, a partir de `exploracao/volatilidade-escondida@c0908d9`.

## Correção de interpretação antes do teste

Na leitura da 2ª rodada, atribuí a "sobra" a escalas **lentas** (horas a dias). Isso estava mal pensado. O sintético G usa o caminho de volatilidade **real** suavizado em 61 min, então as variações de horas e dias já estão nele. O que o G **não** tem é variação de volatilidade **dentro da hora** (minutos). Por isso este sintético acrescenta a escala rápida.

## O sintético M (multiescala)

Em cada semana, a partir de 01/06, com AR(1) por MQO nos retornos reais da semana:

- **Escala lenta:** s_t = o caminho real suavizado em 61 min, idêntico ao do G. Ele carrega horas e dias.
- **Escala rápida:** h_t, um AR(1) em log-volatilidade, h_t = φ_h h_{t−1} + η_t.
  - **Calibração:** pelos choques padronizados reais da mesma semana, u_t = e_t / s_t.
  - Com y_t = log(u_t² + 10⁻¹²), a autocorrelação de y no atraso k é c · φ_h^k para k ≥ 1, em que c = 4·Var(h) / Var(y).
  - φ_h e c saem de MQO de log(autocorrelação) em k, para k = 1 a 20, usando só atrasos com autocorrelação > 0.
  - Var(h) = c · Var(y) / 4.
  - **Limites:** φ_h fica em [0; 0,995] e Var(h) em [0; 2]. Se não houver autocorrelação positiva, Var(h) = 0 e o M vira o G.
- **Choque:** u*_t = exp(h_t − Var(h)) · z_t, com z_t ~ N(0, 1). Não há saltos além dos que a mistura de volatilidades produz.
- **Retorno:** r*_t = a + φ r*_{t−1} + s_t · u*_t.
- **Oráculo:** s_{t} · exp(h_{t} − Var(h)), a volatilidade verdadeira do retorno r*_t, alinhada como no v2 para o passo t → t+1.
- **Réplicas:** 5, com sementes 4026 a 4030.

## Medida e estimativas

Idênticas à 2ª rodada (`explora_volatilidade_escondida_v2.py`):
- **Surpresa:** ε_{t+1} = r_{t+1}² / (σ̂_t² · m_r(x_t)), com x_t o estado 3D.
- **Memória:** M = Spearman(ε_{t+1}, média de ε_{t−9..t}).
- **Estimativas:** c60, ew10, ew30, har e, nos sintéticos, o oráculo.
- **Séries:** real, M (5 réplicas) e, como referência, G (5 réplicas, sementes 3026 a 3030, iguais às da 2ª rodada).

## Regras

1. **Validação:** Red_M(oráculo) ≥ 0,7, na média das réplicas, nos dois períodos. Senão: INCONCLUSIVO.
2. **Estimativa primária:** `ew10`, a mesma escolhida pela regra da 2ª rodada. A comparação fica direta com o veredito anterior, e não se escolhe estimativa de novo depois de ver os dados.
3. **Classificação, com a estimativa primária:**
   - **"Fechado: volatilidade multiescala":** M_real ≤ máximo das 5 réplicas M, nos dois períodos.
   - **"Sobra além da volatilidade multiescala":** M_real > máximo das réplicas M, nos dois períodos.
   - **Senão:** "não estável".
4. **Robustez (descritivo):** a mesma comparação com c60, ew30 e har. Se as quatro estimativas concordarem nos dois períodos, a classificação é **robusta**.
5. **Descritivo também:**
   - os parâmetros calibrados (φ_h e Var(h)) por semana;
   - o M "sem volatilidade" do real contra as réplicas M, para ver se o M reproduz o nível de memória bruto do real.

## Aposta de Claude, antes de calcular

| Aposta | Probabilidade |
|---|---|
| Validação passa | ~85 % |
| "Fechado" com ew10 | ~50 % |
| "Sobra" | ~30 % |
| Robusto (as quatro estimativas concordam) | ~35 % |
| O M reproduz o "sem volatilidade" do real melhor que o G | ~70 % |
