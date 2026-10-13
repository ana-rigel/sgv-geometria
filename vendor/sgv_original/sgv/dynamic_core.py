"""Arquivo 10 — núcleo dinâmico (energia, memória, catraca O_dyn).

Reescrita de ``sgv_dynamic_core.py``. Energia como soma de |Δ|/σ, parâmetros
adaptativos, memória EMA, catraca O_dyn e desacoplamento estrutural mantidos.
Itens 10.1–10.8.

As funções continuam aceitando qualquer objeto de estado (como o runner já
usa). :class:`DynamicState` é o estado tipado recomendado: com ``slots``, um
nome de atributo digitado errado gera erro em vez de criar um campo novo.

Depois das correções 10.1 e 10.2 a catraca anda menos e a energia fica menos
ruidosa: as estatísticas de saída precisam ser medidas de novo antes de
qualquer comparação com o histórico.
"""
from __future__ import annotations

import logging
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .common.numeric import to_float as _safe_float
from .config import DEFAULT_CONFIG, SGVConfig

log = logging.getLogger("sgv.dynamic_core")

NAN = math.nan


@dataclass(slots=True)
class DynamicState:
    _prev_align_energy: float = NAN
    _prev_crit_energy: float = NAN
    _prev_stress_energy: float = NAN
    align_energy_buf: deque = field(default_factory=deque)
    crit_energy_buf: deque = field(default_factory=deque)
    stress_energy_buf: deque = field(default_factory=deque)
    _energy_cache: tuple | None = None
    _energy_warmup: bool = True
    _energy_history: deque = field(default_factory=deque)
    _last_memory_alignment_check_bar_time: Any = None
    memory_alignment: float = NAN
    memory_prev_alignment: float = NAN
    memory_accel_buffer: deque = field(default_factory=deque)
    _last_odyn_check_bar_time: Any = None
    odyn_alignment: float = NAN
    entry_alignment: float = NAN
    odyn_pending_alignment: float = NAN
    odyn_pending_wait_bars: int = 0
    _lifecycle_open: bool | None = None


def _buf(state, name: str, maxlen: int) -> deque:
    """Lê um buffer (lista ou deque) e devolve um deque com ``maxlen``."""
    cur = getattr(state, name, None)
    if isinstance(cur, deque) and cur.maxlen == maxlen:
        return cur
    d = deque(list(cur or [])[-maxlen:], maxlen=maxlen)
    setattr(state, name, d)
    return d


def _record_energy(state, energy_state: str, cfg: SGVConfig) -> None:
    hist = _buf(state, "_energy_history", cfg.dynamic.ENERGY_HISTORY)
    hist.append(energy_state)


# =========================================================
# ENERGY STATE
# =========================================================
def compute_energy_state(
    state,
    alignment: float,
    criticality: float,
    stress: float,
    *,
    current_bar_time=None,
    cfg: SGVConfig = DEFAULT_CONFIG,
) -> tuple[str, float]:
    L, d = cfg.legacy, cfg.dynamic

    # 10.2: uma única atualização por barra
    guard = (not L.LEGACY_ENERGY_NO_GUARD) and current_bar_time is not None
    if guard:
        cache = getattr(state, "_energy_cache", None)
        if cache is not None and cache[0] == current_bar_time:
            return cache[1], cache[2]

    def finish(es: str, score: float, warmup: bool) -> tuple[str, float]:
        setattr(state, "_energy_warmup", warmup)
        if guard:
            setattr(state, "_energy_cache", (current_bar_time, es, float(score)))
        _record_energy(state, es, cfg)
        return es, float(score)

    prev_align = _safe_float(getattr(state, "_prev_align_energy", NAN))
    prev_crit = _safe_float(getattr(state, "_prev_crit_energy", NAN))
    prev_stress = _safe_float(getattr(state, "_prev_stress_energy", NAN))

    if math.isnan(prev_align) or math.isnan(prev_crit) or math.isnan(prev_stress):
        state._prev_align_energy = alignment
        state._prev_crit_energy = criticality
        state._prev_stress_energy = stress
        return finish("MID", 1.0, True)

    delta_align = abs(alignment - prev_align)
    delta_crit = abs(criticality - prev_crit)
    delta_stress = abs(stress - prev_stress)

    align_buf = _buf(state, "align_energy_buf", d.ENERGY_BUFFER)
    crit_buf = _buf(state, "crit_energy_buf", d.ENERGY_BUFFER)
    stress_buf = _buf(state, "stress_energy_buf", d.ENERGY_BUFFER)
    align_buf.append(delta_align)
    crit_buf.append(delta_crit)
    stress_buf.append(delta_stress)

    def zscore(x, buf):
        ref = list(buf)[:-1] if d.ENERGY_STD_EXCLUDES_CURRENT else buf   # 10.8
        std = np.std(ref) if len(ref) >= d.ENERGY_MIN_BUFFER else 0.0
        return x / std if std > 0 else 0.0

    energy_score = zscore(delta_align, align_buf) + zscore(delta_crit, crit_buf) + zscore(delta_stress, stress_buf)

    state._prev_align_energy = alignment
    state._prev_crit_energy = criticality
    state._prev_stress_energy = stress

    if len(align_buf) < d.ENERGY_MIN_BUFFER and not L.LEGACY_ENERGY_WARMUP:
        return finish("MID", 1.0, True)                                     # 10.4

    if energy_score < d.ENERGY_LOW_THRESHOLD:
        return finish("LOW", energy_score, False)
    if energy_score < d.ENERGY_HIGH_THRESHOLD:
        return finish("MID", energy_score, False)
    return finish("HIGH", energy_score, False)


def get_adaptive_params(energy_state: str) -> dict[str, float | int]:
    if energy_state == "LOW":
        return {"psi": 0.40, "coherence_threshold": 0.35, "required_score": 3, "pending_confirm_bars": 2}
    if energy_state == "HIGH":
        return {"psi": 0.15, "coherence_threshold": 0.20, "required_score": 2, "pending_confirm_bars": 1}
    return {"psi": 0.30, "coherence_threshold": 0.30, "required_score": 2, "pending_confirm_bars": 1}


# =========================================================
# MEMORY / O_DYN CORE
# =========================================================
def _update_memory_alignment(state, current_bar_time, *, alignment: float, alpha: float) -> float:
    last_checked = getattr(state, "_last_memory_alignment_check_bar_time", None)
    memory_alignment = _safe_float(getattr(state, "memory_alignment", NAN))
    if last_checked == current_bar_time:
        return memory_alignment
    setattr(state, "_last_memory_alignment_check_bar_time", current_bar_time)
    if math.isnan(alignment):
        return memory_alignment
    if math.isnan(memory_alignment):
        memory_alignment = alignment
    else:
        memory_alignment = (alpha * alignment) + ((1.0 - alpha) * memory_alignment)
    setattr(state, "memory_alignment", memory_alignment)
    return float(memory_alignment)


def _update_memory_acceleration(state, *, memory_alignment: float, sigma_mult: float, min_floor: float,
                                cfg: SGVConfig) -> tuple[float, float, bool]:
    d = cfg.dynamic
    prev_memory = _safe_float(getattr(state, "memory_prev_alignment", NAN))
    buffer = _buf(state, "memory_accel_buffer", d.ACCEL_BUFFER)
    if math.isnan(memory_alignment) or math.isnan(prev_memory):
        setattr(state, "memory_prev_alignment", memory_alignment)
        return 0.0, min_floor, False
    memory_accel = abs(memory_alignment - prev_memory)
    buffer.append(memory_accel)
    sigma_m20 = float(np.std(buffer)) if len(buffer) >= d.ACCEL_MIN_BUFFER else 0.0
    memory_accel_threshold = max(sigma_mult * sigma_m20, min_floor)
    accel_confirmed = memory_accel > memory_accel_threshold
    setattr(state, "memory_prev_alignment", memory_alignment)
    return float(memory_accel), float(memory_accel_threshold), bool(accel_confirmed)


def _update_odyn(
    state,
    current_bar_time,
    *,
    alignment: float,
    memory_alignment: float,
    position_direction: int,
    psi: float,
    coherence_threshold: float,
    accel_sigma_mult: float,
    accel_min_floor: float,
    pending_confirm_bars: int,
    cfg: SGVConfig = DEFAULT_CONFIG,
) -> tuple[float, float, float, bool, bool]:
    L = cfg.legacy
    last_checked = getattr(state, "_last_odyn_check_bar_time", None)
    odyn_alignment = _safe_float(getattr(state, "odyn_alignment", NAN))
    if last_checked == current_bar_time:
        return odyn_alignment, 0.0, accel_min_floor, False, False
    setattr(state, "_last_odyn_check_bar_time", current_bar_time)
    if math.isnan(alignment):
        return odyn_alignment, 0.0, accel_min_floor, False, False
    if math.isnan(odyn_alignment):
        odyn_alignment = _safe_float(getattr(state, "entry_alignment", NAN))
        if math.isnan(odyn_alignment):
            odyn_alignment = alignment
    if math.isnan(memory_alignment):
        setattr(state, "odyn_alignment", odyn_alignment)
        return float(odyn_alignment), 0.0, accel_min_floor, False, False

    memory_accel, memory_accel_threshold, accel_confirmed = _update_memory_acceleration(
        state, memory_alignment=memory_alignment, sigma_mult=accel_sigma_mult,
        min_floor=accel_min_floor, cfg=cfg,
    )
    mf_norm = abs(memory_alignment - alignment)
    coherent_move = mf_norm < coherence_threshold

    pending_alignment = _safe_float(getattr(state, "odyn_pending_alignment", NAN))
    pending_confirmed = False
    created_now = False

    if coherent_move and accel_confirmed:
        new_candidate = odyn_alignment + psi * (alignment - odyn_alignment)
        if position_direction > 0:
            odyn_alignment = max(odyn_alignment, new_candidate)
        elif position_direction < 0:
            odyn_alignment = min(odyn_alignment, new_candidate)
        setattr(state, "odyn_pending_alignment", NAN)
        setattr(state, "odyn_pending_wait_bars", 0)
    elif coherent_move and not accel_confirmed:
        if math.isnan(pending_alignment):
            setattr(state, "odyn_pending_alignment", alignment)
            setattr(state, "odyn_pending_wait_bars", 0)
            created_now = True

    pending_alignment = _safe_float(getattr(state, "odyn_pending_alignment", NAN))
    pending_wait_bars = int(getattr(state, "odyn_pending_wait_bars", 0))

    # 10.1: o pendente só começa a contar na chamada seguinte à criação
    if not math.isnan(pending_alignment) and (L.LEGACY_PENDING_SAME_BAR or not created_now):
        pending_wait_bars += 1
        setattr(state, "odyn_pending_wait_bars", pending_wait_bars)
        if pending_wait_bars >= pending_confirm_bars:
            sustain_ok = False
            if position_direction > 0:
                sustain_ok = alignment >= pending_alignment
            elif position_direction < 0:
                sustain_ok = alignment <= pending_alignment
            if sustain_ok:
                new_candidate = odyn_alignment + psi * (pending_alignment - odyn_alignment)
                if position_direction > 0:
                    odyn_alignment = max(odyn_alignment, new_candidate)
                elif position_direction < 0:
                    odyn_alignment = min(odyn_alignment, new_candidate)
                pending_confirmed = True
            setattr(state, "odyn_pending_alignment", NAN)
            setattr(state, "odyn_pending_wait_bars", 0)

    setattr(state, "odyn_alignment", odyn_alignment)
    return (float(odyn_alignment), float(memory_accel), float(memory_accel_threshold),
            bool(accel_confirmed), bool(pending_confirmed))


# =========================================================
# CICLO DE VIDA (10.3)
# =========================================================
def on_position_open(state, entry_alignment: float) -> None:
    """Zera O_dyn, pendente e buffer de aceleração ao abrir uma posição."""
    state.entry_alignment = _safe_float(entry_alignment)
    state.odyn_alignment = NAN
    state.odyn_pending_alignment = NAN
    state.odyn_pending_wait_bars = 0
    state.memory_accel_buffer = deque(maxlen=DEFAULT_CONFIG.dynamic.ACCEL_BUFFER)
    state._last_odyn_check_bar_time = None
    state._lifecycle_open = True


def on_position_close(state) -> None:
    state.entry_alignment = NAN
    state.odyn_alignment = NAN
    state.odyn_pending_alignment = NAN
    state.odyn_pending_wait_bars = 0
    state.memory_accel_buffer = deque(maxlen=DEFAULT_CONFIG.dynamic.ACCEL_BUFFER)
    state._last_odyn_check_bar_time = None
    state._lifecycle_open = False


def _lifecycle_check(state, position_direction: int, cfg: SGVConfig) -> str | None:
    opened = getattr(state, "_lifecycle_open", None)
    if opened is None:             # runner que não usa o contrato: comportamento antigo
        return None
    msg = None
    if position_direction != 0 and not opened:
        msg = "posição ativa sem on_position_open: O_dyn pode carregar a âncora do trade anterior"
    elif position_direction == 0 and opened:
        msg = "O_dyn ativa sem posição (on_position_close não foi chamado)"
    if msg:
        if cfg.dynamic.STRICT_LIFECYCLE:
            raise AssertionError(msg)
        log.warning(msg)
    return msg


# =========================================================
# TENSOR NORMS
# =========================================================
def _compute_of_norm(*, odyn_alignment: float, alignment: float) -> float:
    if math.isnan(odyn_alignment) or math.isnan(alignment):
        return NAN
    return abs(odyn_alignment - alignment)


def _compute_mo_norm(*, memory_alignment: float, odyn_alignment: float) -> float:
    if math.isnan(memory_alignment) or math.isnan(odyn_alignment):
        return NAN
    return abs(memory_alignment - odyn_alignment)


def _is_structural_decoupling(*, terrain_state: str, bars_in_position: int, of_norm: float, mo_norm: float,
                              coherent_min_bars: int, of_high_threshold: float | None = None,
                              mo_high_threshold: float | None = None, cfg: SGVConfig = DEFAULT_CONFIG) -> bool:
    d = cfg.dynamic
    of_t = d.ODYN_OF_HIGH_THRESHOLD if of_high_threshold is None else of_high_threshold
    mo_t = d.ODYN_MO_HIGH_THRESHOLD if mo_high_threshold is None else mo_high_threshold
    if str(terrain_state).strip().upper() != "COHERENT":
        return False
    if bars_in_position < coherent_min_bars:
        return False
    if math.isnan(of_norm) or math.isnan(mo_norm):
        return False
    return of_norm >= of_t and mo_norm >= mo_t


# =========================================================
# SHARED SNAPSHOT BUILDER
# =========================================================
def energy_state_fractions(state) -> dict[str, float]:
    hist = getattr(state, "_energy_history", None)
    if not hist:
        return {}
    n = len(hist)
    return {k: sum(1 for h in hist if h == k) / n for k in ("LOW", "MID", "HIGH")}


def build_dynamic_snapshot(
    state,
    *,
    current_bar_time,
    alignment: float,
    criticality: float,
    stress: float,
    position_direction: int,
    cfg: SGVConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    d = cfg.dynamic
    lifecycle_warning = _lifecycle_check(state, position_direction, cfg)
    energy_state, energy_score = compute_energy_state(
        state, alignment, criticality, stress, current_bar_time=current_bar_time, cfg=cfg,
    )
    params = get_adaptive_params(energy_state)
    adaptive_psi = float(params["psi"])
    adaptive_coherence_threshold = float(params["coherence_threshold"])
    required_score = int(params["required_score"])
    pending_confirm_bars = int(params["pending_confirm_bars"])

    memory_alignment = _update_memory_alignment(state, current_bar_time, alignment=alignment,
                                                alpha=d.ODYN_EMA_ALPHA)
    (odyn_alignment, memory_accel, memory_accel_threshold, accel_confirmed, pending_confirmed) = _update_odyn(
        state, current_bar_time,
        alignment=alignment, memory_alignment=memory_alignment, position_direction=position_direction,
        psi=adaptive_psi, coherence_threshold=adaptive_coherence_threshold,
        accel_sigma_mult=d.ODYN_ACCEL_SIGMA_MULT, accel_min_floor=d.ODYN_ACCEL_MIN_FLOOR,
        pending_confirm_bars=pending_confirm_bars, cfg=cfg,
    )
    of_norm = _compute_of_norm(odyn_alignment=odyn_alignment, alignment=alignment)
    mo_norm = _compute_mo_norm(memory_alignment=memory_alignment, odyn_alignment=odyn_alignment)

    return {
        "energy_state": energy_state,
        "energy_score": float(energy_score),
        "adaptive_psi": adaptive_psi,
        "adaptive_coherence_threshold": adaptive_coherence_threshold,
        "required_score": required_score,
        "pending_confirm_bars": pending_confirm_bars,
        "memory_alignment": float(memory_alignment),
        "memory_accel": float(memory_accel),
        "memory_accel_threshold": float(memory_accel_threshold),
        "accel_confirmed": bool(accel_confirmed),
        "pending_confirmed": bool(pending_confirmed),
        "odyn_alignment": float(odyn_alignment),
        "odyn_pending_alignment": _safe_float(getattr(state, "odyn_pending_alignment", NAN)),
        "odyn_pending_wait_bars": int(getattr(state, "odyn_pending_wait_bars", 0)),
        "of_norm": float(of_norm),
        "mo_norm": float(mo_norm),
        # novos (10.7)
        "bar_time": current_bar_time,
        "energy_warmup": bool(getattr(state, "_energy_warmup", False)),
        "energy_state_fractions": energy_state_fractions(state),
        "lifecycle_warning": lifecycle_warning,
    }
