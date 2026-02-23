# path: qaai_system/ml/meta_signal_filter.py
from __future__ import annotations

"""
Meta-signal layer for ML confidence & regime-aware filtering.

Typical flow:

    base_engine = MySignalEngine(...)
    prob_model = ProbabilityModel(...)
    regime_detector = RegimeDetector(...)
    meta_filter = MetaSignalFilter(prob_model, regime_detector)

    wrapped_engine = MetaSignalEngineWrapper(base_engine, meta_filter)

    # Then hand 'wrapped_engine' to ExecutionEngine

Design:
- MetaSignalFilter:
    * adds win_prob, ml_confidence, regime_label, risk_factor columns
    * applies composed filters: [MlConfidenceFilter, WinProbFilter, RegimeFilter]
    * optionally scales position_size by risk_factor
- Each filter implements .apply(df) -> df
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence

import pandas as pd

from qaai_system.ml.probability_model import ProbabilityModel
from qaai_system.ml.regime_detector import RegimeDetector


# ---------------------------------------------------------------------------
# Base filter interface
# ---------------------------------------------------------------------------

class BaseSignalFilter:
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


@dataclass
class MlConfidenceFilter(BaseSignalFilter):
    conf_min: float = 0.55
    column: str = "ml_confidence"

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns or df.empty:
            return df
        return df[df[self.column] >= self.conf_min].copy()


@dataclass
class WinProbFilter(BaseSignalFilter):
    prob_min: float = 0.55
    column: str = "win_prob"

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns or df.empty:
            return df
        return df[df[self.column] >= self.prob_min].copy()


@dataclass
class RegimeFilter(BaseSignalFilter):
    blocked_regimes: Sequence[str] = field(default_factory=lambda: ("NO_TRADE",))

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if "regime_label" not in df.columns or df.empty:
            return df
        mask = ~df["regime_label"].isin(self.blocked_regimes)
        return df[mask].copy()


@dataclass
class RiskFactorSizer(BaseSignalFilter):
    """
    Scales 'position_size' (if present) by 'risk_factor' column.

    - position_size_new = round(position_size * risk_factor)
    - Never drops rows; only modifies position_size.
    """

    min_size: int = 1
    column_size: str = "position_size"
    column_rf: str = "risk_factor"

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column_size not in df.columns or self.column_rf not in df.columns:
            return df
        if df.empty:
            return df

        df = df.copy()
        orig = df[self.column_size].fillna(0).astype(int)
        rf = df[self.column_rf].fillna(1.0).astype(float)

        new_size = (orig * rf).round().astype(int)
        new_size = new_size.clip(lower=self.min_size)

        df[self.column_size] = new_size
        return df


# ---------------------------------------------------------------------------
# MetaSignalFilter orchestrator
# ---------------------------------------------------------------------------

@dataclass
class MetaSignalFilterConfig:
    enabled: bool = True
    conf_min: float = 0.55
    prob_min: float = 0.55
    blocked_regimes: Sequence[str] = field(default_factory=lambda: ("NO_TRADE",))
    apply_risk_sizer: bool = True


class MetaSignalFilter:
    """
    Orchestrates probability model + regime detector + filter composition.
    """

    def __init__(
        self,
        probability_model: ProbabilityModel,
        regime_detector: RegimeDetector,
        config: Optional[MetaSignalFilterConfig] = None,
        filters: Optional[List[BaseSignalFilter]] = None,
    ) -> None:
        self.probability_model = probability_model
        self.regime_detector = regime_detector
        self.config = config or MetaSignalFilterConfig()

        if filters is not None:
            self.filters = filters
        else:
            self.filters = [
                MlConfidenceFilter(conf_min=self.config.conf_min),
                WinProbFilter(prob_min=self.config.prob_min),
                RegimeFilter(blocked_regimes=self.config.blocked_regimes),
            ]
            if self.config.apply_risk_sizer:
                self.filters.append(RiskFactorSizer())

    @property
    def enabled(self) -> bool:
        return self.config.enabled

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich & filter the signal DataFrame.

        - Adds win_prob, ml_confidence, regime_label, risk_factor
        - Applies composition filters
        """
        if not self.enabled or df is None or len(df) == 0:
            return df

        # Step 1: add probability columns
        df = self.probability_model.enrich(df)

        # Step 2: add regime columns
        df = self.regime_detector.enrich(df)

        # Step 3: apply filters
        for f in self.filters:
            df = f.apply(df)
            if df is None or df.empty:
                return df

        return df


# ---------------------------------------------------------------------------
# SignalEngine wrapper
# ---------------------------------------------------------------------------

class MetaSignalEngineWrapper:
    """
    Wrap any SignalEngine so that ExecutionEngine sees already-filtered,
    ML-augmented signals.

    Expected base_interface:
        base_engine.run(*args, **kwargs) -> DataFrame or list[dict]
    """

    def __init__(
        self,
        base_engine: Any,
        meta_filter: MetaSignalFilter,
    ) -> None:
        self.base_engine = base_engine
        self.meta_filter = meta_filter

    def run(self, *args, **kwargs):
        base = self.base_engine.run(*args, **kwargs)

        # Case 1: DataFrame
        if isinstance(base, pd.DataFrame):
            return self.meta_filter.apply(base)

        # Case 2: list of dicts -> DataFrame -> filter -> list[dict]
        if isinstance(base, list) and base and isinstance(base[0], dict):
            df = pd.DataFrame(base)
            df_f = self.meta_filter.apply(df)
            if df_f is None or df_f.empty:
                return []
            return df_f.to_dict(orient="records")

        # Fallback: unknown type -> pass through
        return base
