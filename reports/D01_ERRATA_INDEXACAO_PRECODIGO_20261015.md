# D01 — Errata formal de indexação anterior ao código e ao teste

No pré-registro D01, a memória plantada foi descrita como s[t]=s[t−20], enquanto o preditor de histórico contém s[t−20] para prever Y[t+1]. Isso seria um desencontro de uma unidade: s[t+1] depende de s[t−19], não de s[t−20].

**Correção anterior ao código:** o gerador positivo usará **s[k]=s[k−21]**, com probabilidade 0,82, para k>=21. Portanto, ao prever s[t+1], a característica adicional s[t−20] é exatamente a memória plantada (lag 21 em relação ao próximo retorno). Quatro sinais recentes e volatilidade permanecem as mesmas. Todos os limiares, splits, hipóteses, seeds, comparadores, estatísticas e protocolos de leitura permanecem fixos. A frase 'memória no atraso 20' do protocolo designa aqui atraso 20 **em relação ao estado t disponível**, equivalente ao atraso 21 relativo ao próximo sinal.

O código e as avaliações ainda não existiam quando esta errata foi registrada. Sem adaptação ao resultado.
