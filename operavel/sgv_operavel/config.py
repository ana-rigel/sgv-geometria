"""Configuração central do SGV Operável.

Todo parâmetro tem ORIGEM documentada. Parâmetros sem origem não entram.
Alterações exigem nova entrada no CHANGELOG do README (governança, plano §6).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CostConfig:
    """Custos de execução. Origem: Doc Pesquisa v5 §4.3 (Binance, maker)."""
    fee: float = 0.00008          # taxa maker por lado
    slippage: float = 0.00005     # slippage estimado por lado (ordens limite)

    @property
    def round_trip(self) -> float:
        return 2 * (self.fee + self.slippage)   # 0.026% total -> 0.00026


@dataclass(frozen=True)
class CollapseConfig:
    """Sleeve B — evento de RUPTURA de atividade (sucessor observável do OIT).

    Origem: fenômeno validado em 45.860 candles 1m (p=1.6e-28) e 15m
    (p=7.8e-6); engenharia reversa de 06/08/2026 mostrou que OIT-baixo
    corresponde a vol_ratio ALTO (AUC 0.725) e que o detector direto é mais
    forte (p=2e-11). Threshold ADAPTATIVO (percentil móvel), nunca absoluto.
    """
    timeframe: str = "1h"   # adaptação por disponibilidade de dados (klines 1h); janelas mantidas em barras
    span_short: int = 12          # vol curta (~3h em 15m)
    span_long: int = 96           # vol longa (~1 dia em 15m)
    quantile: float = 0.90        # evento = vol_ratio > p90 móvel (burst)
    quantile_window: int = 500    # janela do percentil (~5 dias em 15m)
    cluster_bars: int = 3         # T2: evento repetido em <=3 barras (Doc v5 §5.2, único amplificador com AUC OOS)
    momentum_bars: int = 8        # direção = sinal do momentum (~2h). Origem: momentum foi o único preditor direcional (auditoria 08/2026)
    hold_bars: int = 4            # ~1h de hold (janela do drift medido no 15m)
    stop_ret: float = -0.012      # stop escalado por sqrt(tempo) p/ hold 4h; regra definida ANTES de rodar (06/08/2026)
    only_cluster: bool = True     # operar apenas eventos T2 (o amplificador validado)
    block_hours_utc: tuple[int, ...] = ()  # H-N2: (0..5) SÓ após validação Fase 1/2


@dataclass(frozen=True)
class TrendConfig:
    """Sleeve A — time-series momentum 4h/1d.

    Origem: literatura TSMOM (Moskowitz et al. 2012; replicações cripto).
    Parâmetros redondos e padrão de literatura — deliberadamente NÃO
    otimizados neste dataset para não contaminar o gate.
    """
    timeframe: str = "4h"
    lookback_bars: int = 180      # ~30 dias em 4h
    ma_bars: int = 120            # filtro: preço acima da média ~20 dias
    vol_span: int = 90            # vol EWMA p/ sizing
    allow_short: bool = False    # começar long/flat; short só via perpétuo na Fase 3+


@dataclass(frozen=True)
class CarryConfig:
    """Sleeve C — carry de funding delta-neutro (spot long + perp short).

    Origem: mecanismo econômico documentado (funding paga o lado short quando
    alavancados compram). Requer série de funding; sem ela a sleeve fica off.
    """
    min_annualized: float = 0.05  # entra só se funding anualizado > 5% a.a.
    exit_annualized: float = 0.0  # sai quando funding vira <= 0
    funding_period_hours: int = 8


@dataclass(frozen=True)
class RiskConfig:
    """Plano §4 Fase 3 — inegociável."""
    risk_per_trade: float = 0.005      # <=0.5% do capital por trade (Sleeve B)
    target_vol_annual: float = 0.20    # vol-alvo da Sleeve A
    max_position: float = 1.0          # sem alavancagem nas sleeves direcionais
    circuit_breaker_dd: float = 0.10   # DD 10% -> sistema para


@dataclass(frozen=True)
class GateConfig:
    """Plano §4 Fase 1 — critérios PRÉ-REGISTRADOS. Não alterar após ver resultados."""
    min_sharpe_oos: float = 0.8
    min_years_pass: int = 4
    total_years: int = 5
    min_edge_cost_ratio: float = 3.0
    max_drawdown: float = 0.20
    max_single_quarter_share: float = 0.60  # nenhum trimestre pode responder por >60% do retorno


@dataclass(frozen=True)
class Config:
    costs: CostConfig = field(default_factory=CostConfig)
    collapse: CollapseConfig = field(default_factory=CollapseConfig)
    trend: TrendConfig = field(default_factory=TrendConfig)
    carry: CarryConfig = field(default_factory=CarryConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    gates: GateConfig = field(default_factory=GateConfig)


DEFAULT = Config()
