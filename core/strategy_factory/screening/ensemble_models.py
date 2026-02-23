# core/strategy_factory/screening/ensemble_models.py

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple


@dataclass(frozen=True)
class EnsembleSignal:
    signal_type: str
    value: Decimal
    description: str


@dataclass(frozen=True)
class EnsembleIntelligenceReport:
    signals: Tuple[EnsembleSignal, ...]
    state_hash: str