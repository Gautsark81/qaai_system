# path: qaai_system/ml/regime_detector.py
from __future__ import annotations

"""
Simple regime detector for intraday strategies.

Inputs (per row):
- vol / atr / hv          : volatility proxy
- trend_score / adx / slope: trend strength proxy
- time_of_day (float, hours) or "HH:MM" string

Outputs:
- regime_label: str  (TRENDING, CHOPPY, HIGH_VOL, NO_TRADE, UNKNOWN)
- regime_score: float
- vol_bucket:   str  (low, medium, high)
- risk_factor:  float in (0, 1]
"""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class RegimeDetectorConfig:
    vol_low: float = 0.5        # below -> low vol
    vol_high: float = 1.5       # above -> high vol

    trend_min_trending: float = 0.6  # trend_score above this -> TRENDING
    trend_mid: float = 0.3           # below -> CHOPPY

    # Time windows (in hours) where we avoid trading (e.g. lunch / illiquid)
    no_trade_windows: Tuple[Tuple[float, float], ...] = ((12.0, 13.0),)

    # Risk factors per regime label
    risk_factor_trending: float = 1.0
    risk_factor_choppy: float = 0.5
    risk_factor_high_vol: float = 0.7
    risk_factor_no_trade: float = 0.0  # 0 -> pure filter, no position
    risk_factor_unknown: float = 0.8


class RegimeDetector:
    def __init__(self, config: Optional[RegimeDetectorConfig] = None) -> None:
        self.config = config or RegimeDetectorConfig()

    def _extract_vol(self, df: pd.DataFrame) -> np.ndarray:
        for col in ("vol", "atr", "hv"):
            if col in df.columns:
                return df[col].fillna(0.0).to_numpy(dtype=float)
        return np.zeros(len(df), dtype=float)

    def _extract_trend(self, df: pd.DataFrame) -> np.ndarray:
        for col in ("trend_score", "adx", "slope"):
            if col in df.columns:
                return df[col].fillna(0.0).to_numpy(dtype=float)
        return np.zeros(len(df), dtype=float)

    def _parse_time_of_day(self, s: str) -> Optional[float]:
        s = str(s).strip()
        if not s or s.lower() == "nan":
            return None
        # If already numeric string (e.g. "10.5")
        try:
            return float(s)
        except ValueError:
            pass
        # Expect "HH:MM"
        try:
            parts = s.split(":")
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return h + m / 60.0
        except Exception:
            return None

    def _extract_tod(self, df: pd.DataFrame) -> np.ndarray:
        if "time_of_day" not in df.columns:
            return np.full(len(df), np.nan)
        col = df["time_of_day"]
        if pd.api.types.is_numeric_dtype(col):
            return col.to_numpy(dtype=float)
        return col.map(self._parse_time_of_day).to_numpy(dtype=float)

    def _is_in_no_trade(self, tod: float) -> bool:
        if np.isnan(tod):
            return False
        for start, end in self.config.no_trade_windows:
            if start <= tod <= end:
                return True
        return False

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add regime-related columns to a copy of df:
        - regime_label
        - regime_score
        - vol_bucket
        - risk_factor
        """
        if df.empty:
            return df

        df = df.copy()

        vol = self._extract_vol(df)
        trend = self._extract_trend(df)
        tod = self._extract_tod(df)

        # Vol bucket
        vol_bucket: List[str] = []
        for v in vol:
            if v < self.config.vol_low:
                vol_bucket.append("low")
            elif v > self.config.vol_high:
                vol_bucket.append("high")
            else:
                vol_bucket.append("medium")

        # Regime label & score
        labels: List[str] = []
        scores: List[float] = []
        risk: List[float] = []

        for v, t, t_hour in zip(vol, trend, tod):
            if not np.isnan(t_hour) and self._is_in_no_trade(t_hour):
                label = "NO_TRADE"
                score = -1.0
                rf = self.config.risk_factor_no_trade
            else:
                if t >= self.config.trend_min_trending and v >= self.config.vol_low:
                    label = "TRENDING"
                    score = t
                    rf = self.config.risk_factor_trending
                elif v > self.config.vol_high:
                    label = "HIGH_VOL"
                    score = t
                    rf = self.config.risk_factor_high_vol
                elif t <= self.config.trend_mid:
                    label = "CHOPPY"
                    score = t
                    rf = self.config.risk_factor_choppy
                else:
                    label = "UNKNOWN"
                    score = t
                    rf = self.config.risk_factor_unknown

            labels.append(label)
            scores.append(score)
            risk.append(rf)

        df["vol_bucket"] = vol_bucket
        df["regime_label"] = labels
        df["regime_score"] = scores
        df["risk_factor"] = risk

        return df
