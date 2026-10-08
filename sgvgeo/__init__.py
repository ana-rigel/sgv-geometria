"""sgvgeo — reconstrução exata e causal da camada de geometria informacional do SGV.

Módulos
-------
data       : séries sintéticas (GARCH-t), substitutas (surrogates) e leitura de klines da Binance
features   : coordenadas de estado do SGV (v, a, jerk, E, memória, λ) e escalas causais
kde        : estimador de densidade gaussiano com derivadas analíticas (ρ, ∇ρ, ∇²ρ)
geometry   : métricas (informação observada, Fisher local), Christoffel, Riemann, Ricci, R, Einstein
legacy     : execução da camada original (pasta legacy/) sem modificações
"""

__version__ = "0.1.0"
