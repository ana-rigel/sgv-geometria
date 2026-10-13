"""Configuração central do SGV (camada geométrica).

Todas as constantes que antes ficavam no topo de cada script estão aqui, com os
mesmos nomes e valores padrão. As flags ``LEGACY_*`` reproduzem o comportamento
dos scripts originais (pasta ``legacy/``); o padrão de cada uma é ``False``.

Uso típico::

    from sgv.config import SGVConfig
    cfg = SGVConfig()                 # comportamento novo
    cfg_old = SGVConfig.legacy_config()   # todas as flags LEGACY_* ligadas
    cfg2 = cfg.with_legacy(LEGACY_NAN_COS=True)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, fields, replace


@dataclass(frozen=True)
class LegacyFlags:
    """Cada flag em ``True`` reproduz o comportamento original daquele item.

    Os números entre parênteses são os itens da especificação
    "SGV — Especificação de melhorias técnicas da camada geométrica".
    """

    # C1, 1.1, 2.1, 3.2, 5.3 — KDE em unidades absolutas (sem padronização)
    LEGACY_UNSCALED_KDE: bool = False
    # C2, 2.1, 5.3 — KDE ajustada uma única vez no período inteiro
    LEGACY_GLOBAL_KDE: bool = False
    # C3, 2.2, 5.3 — derivadas por grade + np.gradient + interpolação
    LEGACY_GRID_DERIVATIVES: bool = False
    # C4, 2.3, 3.5 — Hessiana usada como métrica sem projeção PSD
    LEGACY_RAW_METRIC: bool = False
    # C5 — quantis, z-scores e winsorização no período inteiro
    LEGACY_GLOBAL_QUANTILES: bool = False
    # C6 — divisões com epsilon absoluto (1e-9 / 1e-4)
    LEGACY_ABS_EPS: bool = False
    # C7 — NaN preenchido com zero dentro de cada script
    LEGACY_ZERO_FILL: bool = False
    # 1.3 — sobrescrever E_norm/jerk do input com a versão do preço
    LEGACY_OVERWRITE_KINEMATICS: bool = False
    # 3.A — curvatura 3D por diferenças finitas na grade
    LEGACY_FD_CURVATURE: bool = False
    # 3.4 — velocidade para trás e aceleração centrada em t-1
    LEGACY_KINEMATICS: bool = False
    # 3.9, 4.7 — nove componentes de G_info/T_info
    LEGACY_9_COMPONENTS: bool = False
    # 4.1 — argmax rotula linha toda NaN como "rigidity"
    LEGACY_TYPE_ARGMAX: bool = False
    # 5.1 — bfill no aquecimento do terreno
    LEGACY_BFILL: bool = False
    # 6.1, 7.3 — searchsorted ao agregar, vizinho mais próximo ao consultar
    LEGACY_BINNING: bool = False
    # 6.2 — grade mínimo–máximo
    LEGACY_MINMAX_GRID: bool = False
    # 6.3 — mapa de força único com o período inteiro
    LEGACY_GLOBAL_MAP: bool = False
    # 6.4 — sem contagem mínima por célula
    LEGACY_NO_MIN_CELL: bool = False
    # 6.5, 7.4 — componentes de força em unidades brutas
    LEGACY_UNSCALED_FORCE: bool = False
    # 7.1, 9.2 — célula vazia vira cosseno 1,0
    LEGACY_NAN_COS: bool = False
    # 7.2 — a própria barra entra na média da célula
    LEGACY_SELF_INCLUDED: bool = False
    # 8.1 — janela do EV termina em i-1 para todos os horizontes
    LEGACY_EV_WINDOW: bool = False
    # 9.3 — fillna(0) antes de classificar (NO_EDGE inalcançável)
    LEGACY_EDGE_FILL: bool = False
    # 10.1 — pendente confirmado na mesma chamada em que é criado
    LEGACY_PENDING_SAME_BAR: bool = False
    # 10.2 — energia sem guarda de bar_time
    LEGACY_ENERGY_NO_GUARD: bool = False
    # 10.4 — aquecimento da energia cai em LOW
    LEGACY_ENERGY_WARMUP: bool = False

    @classmethod
    def all_on(cls) -> "LegacyFlags":
        return cls(**{f.name: True for f in fields(cls)})


@dataclass(frozen=True)
class CausalConfig:
    """Janelas causais (C2, C5, 6.3). Em barras de 1 minuto."""

    W_FIT: int = 10080          # 7 dias: janela de ajuste da KDE
    REFIT_EVERY: int = 60       # reajuste a cada 60 barras
    MIN_FIT: int = 1440         # 1 dia: mínimo de amostras para ajustar
    W_QUANTILE: int = 10080     # janela dos quantis / z causais
    MIN_QUANTILE: int = 1440
    W_MAP: int = 10080          # janela do mapa de força causal
    MIN_MAP: int = 1440


@dataclass(frozen=True)
class NumericConfig:
    PSD_FLOOR: float = 1e-3            # C4: piso dos autovalores (unidades padronizadas)
    SAFE_RATIO_Q: float = 0.05         # C6: quantil de |denominador| usado como piso
    FD_DELTA: float = 0.05             # passo das diferenças finitas no fallback PSD
    # Linhas em que a projeção PSD alterou a métrica não têm mais métrica
    # Hessiana: "fd" (especificação) recalcula Γ e Ricci por diferenças
    # finitas da métrica projetada; "hessian_identity" é uma aproximação mais
    # barata (Γ = ½ g_psd⁻¹ ∂³φ e Ricci pela fórmula Hessiana). Nas duas,
    # essas linhas saem com geom_exact = 0.
    PSD_FALLBACK: str = "fd"

    def __post_init__(self):
        if self.PSD_FALLBACK not in ("fd", "hessian_identity"):
            raise ValueError(f"PSD_FALLBACK inválido: {self.PSD_FALLBACK!r} (use 'fd' ou 'hessian_identity')")


@dataclass(frozen=True)
class InfoLocalConfig:
    WINDOW: int = 200
    BANDWIDTH: float = 0.35
    EPS: float = 1e-9
    KINEMATICS_SOURCE: str = "close"   # "close" (como o original) ou "input"


@dataclass(frozen=True)
class InfoFieldConfig:
    TIMESTAMP_COL: str = "timestamp"
    E_COL: str = "E_norm"
    J_COL: str = "jerk"
    L_COL: str = "lambda_dynamic"
    GRID_N: int = 200
    BANDWIDTH: float = 0.35
    EPS: float = 1e-9
    METRIC_REG: float = 1e-6
    ALPHA_E: float = 0.05
    ALPHA_J: float = 0.05
    W1: float = 1.0
    W2: float = 0.5
    W3: float = 0.5
    W4: float = 0.5
    B0: float = -2.0
    B1: float = 0.80
    B2: float = 0.60
    B3: float = 0.50
    B4: float = 0.60
    Q_LOW: float = 0.01
    Q_HIGH: float = 0.99


@dataclass(frozen=True)
class GeodesicConfig:
    E_COL: str = "E_norm"
    J_COL: str = "jerk"
    L_COL: str = "lambda_dynamic"
    GRID_N: int = 200
    BANDWIDTH: float = 0.35
    Q_LOW: float = 0.01
    Q_HIGH: float = 0.99
    GRID_N_E3: int = 48
    GRID_N_J3: int = 48
    GRID_N_M3: int = 32
    BANDWIDTH_3D: float = 0.45
    EPS: float = 1e-9
    METRIC_REG: float = 1e-6
    DET_FLOOR: float = 1e-9
    ALPHA_E: float = 0.05
    ALPHA_J: float = 0.05
    CLIP_GAMMA: float = 1e6
    CLIP_ACC: float = 1e6
    CLIP_CURV_3D: float = 1e6
    CLIP_FIELD_GRAVITY: float = 1e6
    W_INCOH: float = 1.00
    W_GRAD: float = 0.50
    W_GEO_RESID: float = 1.00
    W_ACC_GEO: float = 0.25
    W_CURVATURE: float = 0.25
    W_JERK_OVER_LAMBDA: float = 0.50
    B0: float = -2.0
    B1: float = 1.00
    B2: float = 0.50
    B3: float = 0.40
    B4: float = 0.50
    B5: float = 0.30
    B6: float = 0.40
    W_PHI_STRESS: float = 1.00
    W_MEM_STRESS: float = 0.75
    W_LAMBDA_STRESS: float = 0.25
    KAPPA_INFO: float = 1.0


@dataclass(frozen=True)
class SingularityConfig:
    L_COL: str = "lambda_dynamic"
    EPS: float = 1e-9
    Q_ALERT_90: float = 0.90
    Q_ALERT_95: float = 0.95
    Q_ALERT_99: float = 0.99
    MAX_LOG_COMPONENT: float = 50.0
    MAX_SCORE: float = 1e6
    DOMINANCE_RATIO: float = 1.12


@dataclass(frozen=True)
class TerrainConfig:
    E_COL: str = "E_norm"
    J_COL: str = "jerk"
    LAMBDA_COL: str = "lambda_dynamic"
    R_COL: str = "r"
    WINDOW: int = 80
    ALPHA: float = 0.97
    EPS: float = 1e-4
    BANDWIDTH: float = 0.35
    DELTA: float = 0.03
    BETA: float = 0.60
    HYST_K: int = 10
    WINSOR_LO: float = 0.005
    WINSOR_HI: float = 0.995
    FINAL_SCORE_LO: float = 0.005
    FINAL_SCORE_HI: float = 0.995
    STATE_Q1: float = 0.50
    STATE_Q2: float = 0.80
    STATE_Q3: float = 0.93


@dataclass(frozen=True)
class ForceFieldConfig:
    EPS: float = 1e-9
    GRID_SIZE: int = 40
    MIN_CELL_N: int = 5
    Q_LOW: float = 0.01
    Q_HIGH: float = 0.99
    FORCE_MODE: str = "arrival"        # 6.7: "arrival" (atual) ou "departure"


@dataclass(frozen=True)
class AlignmentConfig:
    E_COL: str = "E_norm"
    J_COL: str = "jerk"
    EPS: float = 1e-12
    FORCE_Q_LOW: float = 0.01
    FORCE_Q_HIGH: float = 0.99


@dataclass(frozen=True)
class ExpectedValueConfig:
    EPS: float = 1e-9
    WINDOW: int = 200
    Q_HIGH: float = 0.95
    Q_LOW: float = 0.05
    MIN_SIGNALS: int = 10
    HORIZONS: tuple[int, ...] = (1, 3, 5)


@dataclass(frozen=True)
class EdgeConfig:
    EPS: float = 1e-9
    ALIGNMENT_STRONG: float = 0.25
    ALIGNMENT_VERY_STRONG: float = 0.50
    EV_THRESHOLD: float = 0.0
    ALIGNMENT_COL: str = "force_alignment_cos"
    JOIN_ON: str = "timestamp"


@dataclass(frozen=True)
class DynamicConfig:
    ODYN_EMA_ALPHA: float = 0.25
    ODYN_REANCHOR_PSI: float = 0.30
    ODYN_COHERENCE_THRESHOLD: float = 0.30
    ODYN_OF_HIGH_THRESHOLD: float = 0.85
    ODYN_MO_HIGH_THRESHOLD: float = 0.50
    ODYN_ACCEL_SIGMA_MULT: float = 1.5
    ODYN_ACCEL_MIN_FLOOR: float = 0.08
    ODYN_PENDING_CONFIRM_BARS: int = 1
    ENERGY_LOW_THRESHOLD: float = 1.0
    ENERGY_HIGH_THRESHOLD: float = 2.0
    ENERGY_BUFFER: int = 20
    ENERGY_MIN_BUFFER: int = 5
    ACCEL_BUFFER: int = 20
    ACCEL_MIN_BUFFER: int = 5
    ENERGY_HISTORY: int = 500              # 10.7: barras usadas na fração por estado
    ENERGY_STD_EXCLUDES_CURRENT: bool = False   # 10.8
    STRICT_LIFECYCLE: bool = False         # 10.3: True transforma o aviso em erro


@dataclass(frozen=True)
class SGVConfig:
    legacy: LegacyFlags = field(default_factory=LegacyFlags)
    causal: CausalConfig = field(default_factory=CausalConfig)
    numeric: NumericConfig = field(default_factory=NumericConfig)
    info_local: InfoLocalConfig = field(default_factory=InfoLocalConfig)
    info: InfoFieldConfig = field(default_factory=InfoFieldConfig)
    geodesic: GeodesicConfig = field(default_factory=GeodesicConfig)
    singularity: SingularityConfig = field(default_factory=SingularityConfig)
    terrain: TerrainConfig = field(default_factory=TerrainConfig)
    force_field: ForceFieldConfig = field(default_factory=ForceFieldConfig)
    alignment: AlignmentConfig = field(default_factory=AlignmentConfig)
    expected_value: ExpectedValueConfig = field(default_factory=ExpectedValueConfig)
    edge: EdgeConfig = field(default_factory=EdgeConfig)
    dynamic: DynamicConfig = field(default_factory=DynamicConfig)

    # ------------------------------------------------------------------
    @classmethod
    def legacy_config(cls) -> "SGVConfig":
        """Todas as flags LEGACY_* ligadas: reproduz os scripts originais."""
        return cls(legacy=LegacyFlags.all_on())

    # alias curto
    legacy_all = legacy_config

    def with_legacy(self, **flags: bool) -> "SGVConfig":
        return replace(self, legacy=replace(self.legacy, **flags))

    def with_causal(self, **kw) -> "SGVConfig":
        return replace(self, causal=replace(self.causal, **kw))

    def with_numeric(self, **kw) -> "SGVConfig":
        return replace(self, numeric=replace(self.numeric, **kw))

    def with_section(self, section: str, **kw) -> "SGVConfig":
        return replace(self, **{section: replace(getattr(self, section), **kw)})

    def to_dict(self) -> dict:
        return asdict(self)

    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


DEFAULT_CONFIG = SGVConfig()
