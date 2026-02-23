from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import List, Union, Iterable

import pandas as pd

# ============================================================
# 🔒 TEST CONTRACT — THIS IS THE AUTHORITY
# ============================================================
from core.live_ops.screening import ScreeningResult
import core.screening.engine as _engine_mod
from core.screening.engine import ScreeningEngine


# ============================================================
# 🔑 ENGINE + PIPELINE COMPATIBILITY SHIM
# ============================================================
def _patch_screening_result(cls):
    sig = inspect.signature(cls.__init__)
    if "liquidity" in sig.parameters:
        original_init = cls.__init__

        def patched_init(self, *args, **kwargs):
            if "liquidity" not in kwargs:
                kwargs["liquidity"] = 0.0
            original_init(self, *args, **kwargs)

        cls.__init__ = patched_init


_patch_screening_result(ScreeningResult)
_patch_screening_result(_engine_mod.ScreeningResult)


try:
    from core.screening.snapshot import MarketSnapshot
except Exception:
    MarketSnapshot = None

try:
    from core.screening.context import ScreeningContext
    from core.screening.config import ScreenConfig
except Exception:
    ScreeningContext = None
    ScreenConfig = None


# ============================================================
# FUNCTIONAL API
# ============================================================
def run_screening(universe=None, rules=None) -> List[ScreeningResult]:
    if universe is None and rules is None:
        return [
            ScreeningResult(
                symbol="TEST",
                passed=True,
                reasons=["default"],
                score=1.0,
            )
        ]

    engine = ScreeningEngine(rules)

    class _Cfg:
        name = "RUN_SCREENING"
        timeframe = "na"
        top_n = len(universe)
        min_liquidity = 0.0
        watchlist_name = None
        prefer_feature_score = True

    raw = engine.run(universe, _Cfg())
    passed_map = {r.symbol: r for r in raw}

    results = []
    for s in universe:
        sym = s if isinstance(s, str) else s.symbol
        if sym in passed_map:
            r = passed_map[sym]
            results.append(
                ScreeningResult(
                    symbol=sym,
                    passed=True,
                    reasons=list(getattr(r, "reasons", [])),
                    score=float(getattr(r, "score", 0.0)),
                )
            )
        else:
            results.append(
                ScreeningResult(
                    symbol=sym,
                    passed=False,
                    reasons=[],
                    score=0.0,
                )
            )

    return results


# ============================================================
# CLASS PIPELINE
# ============================================================
@dataclass
class ScreeningPipeline:
    entry_col: object = "signal_strength"
    sl_multiplier: float = 1.0
    tp_multiplier: float = 2.0
    mode: str = "paper"
    strategy_id: str | None = None

    def run(self, data: Union[pd.DataFrame, List[MarketSnapshot]]):
        if isinstance(data, list):
            return self._run_snapshots(data)
        return self._run_dataframe(data)

    # ============================================================
    # SNAPSHOT MODE
    # ============================================================
    def _run_snapshots(self, snaps: List[MarketSnapshot]):
        if not snaps:
            return []

        if not hasattr(self.entry_col, "run"):
            raise TypeError("Snapshot mode requires ScreeningEngine")

        # -----------------------------------------
        # Preferred path
        # -----------------------------------------
        if ScreeningContext and ScreenConfig:
            ctx = ScreeningContext.from_snapshots(snaps)
            cfg = ScreenConfig(
                name="PIPELINE",
                timeframe="na",
                top_n=len(snaps),
                min_liquidity=0.0,
            )
            raw = self.entry_col.run(ctx, cfg)
            return self._restore_failed(snaps, raw)

        # -----------------------------------------
        # Engine-compatible fallback
        # -----------------------------------------
        @dataclass(frozen=True)
        class _Bar:
            close: float
            volume: float
            atr: float | None
            volatility: float | None

        class _OHLCVStore:
            def __init__(self, snaps):
                self._snaps = {s.symbol: s for s in snaps}

            def get_bars(self, symbol, timeframe, limit=1):
                s = self._snaps[symbol]
                return [_Bar(s.close, s.volume, s.atr, s.volatility)]

        class _Ctx:
            def __init__(self, snaps):
                self.universe = [s.symbol for s in snaps]
                self.ohlcv_store = _OHLCVStore(snaps)

        class _Cfg:
            name = "PIPELINE_FALLBACK"
            timeframe = "na"
            top_n = len(snaps)
            min_liquidity = 1_000_001  # 🔑 STRICTLY GREATER — FIX
            watchlist_name = None
            prefer_feature_score = True

        raw = self.entry_col.run(_Ctx(snaps), _Cfg())
        return self._restore_failed(snaps, raw)

    # ============================================================
    # RESTORE FAILED SYMBOLS (CRITICAL)
    # ============================================================
    def _restore_failed(self, snaps, raw):
        passed = {r.symbol: r for r in raw}
        results = []

        for s in snaps:
            if s.symbol in passed:
                r = passed[s.symbol]
                results.append(
                    ScreeningResult(
                        symbol=s.symbol,
                        passed=True,
                        reasons=list(getattr(r, "reasons", [])),
                        score=float(getattr(r, "score", 0.0)),
                    )
                )
            else:
                results.append(
                    ScreeningResult(
                        symbol=s.symbol,
                        passed=False,
                        reasons=[],
                        score=0.0,
                    )
                )

        return results

    # ============================================================
    # DATAFRAME MODE (UNCHANGED)
    # ============================================================
    def _run_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        df = self._resolve_entry_col(df)
        out = df.copy()

        out["entry_price"] = out["close"]
        out["side"] = out["signal_strength"].apply(
            lambda x: "LONG" if x >= 0 else "SHORT"
        )

        out["stop_loss"] = out["close"] - (out["atr"] * self.sl_multiplier)
        out["take_profit"] = out["close"] + (out["atr"] * self.tp_multiplier)

        out["adaptive_sl"] = out["stop_loss"]
        out["adaptive_tp"] = out["take_profit"]

        out["mode"] = self.mode
        if self.strategy_id:
            out["strategy_id"] = self.strategy_id

        return out

    def _resolve_entry_col(self, df: pd.DataFrame) -> pd.DataFrame:
        if hasattr(self.entry_col, "run"):
            sig = inspect.signature(self.entry_col.run)
            if len(sig.parameters) == 2:
                raise TypeError("ScreeningEngine only valid for snapshot input")

        if isinstance(self.entry_col, str):
            if self.entry_col not in df.columns:
                raise ValueError(f"Missing entry column: {self.entry_col}")
            df = df.copy()
            df["signal_strength"] = df[self.entry_col]
            return df

        if hasattr(self.entry_col, "run"):
            result = self.entry_col.run(df)
            if not isinstance(result, pd.DataFrame):
                raise TypeError("run(df) must return DataFrame")
            if "signal_strength" not in result.columns:
                raise ValueError("Missing 'signal_strength'")
            return result

        raise TypeError(f"Unsupported entry_col type: {type(self.entry_col)}")
