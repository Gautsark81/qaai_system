# core/strategy_factory/screening/meta_alpha_models.py

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple


@dataclass(frozen=True)
class MetaAlphaSignal:
    signal_type: str
    value: Decimal
    description: str


@dataclass(frozen=True)
class MetaAlphaReport:
    signals: Tuple[MetaAlphaSignal, ...]
    state_hash: str