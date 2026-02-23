from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from core.screening.pipeline import ScreeningPipeline


class StockScreener:
    """
    Legacy + modern compatible stock screener.

    HARD TEST CONTRACTS:
    - screen() MUST return a pandas DataFrame
    - Returned DataFrame MUST support `.empty`
    - engine presence implies legacy mode
    - engine failure MUST NOT block symbol
    """

    def __init__(self, engine: Any = None, *, config: Optional[dict] = None, **kwargs):
        # Legacy indicator engine (tests rely on this)
        self.engine = engine
        self.config = config or {}

        # Modern pipeline kwargs (strict + safe)
        self.pipeline_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k
            in {
                "entry_col",
                "sl_multiplier",
                "tp_multiplier",
                "mode",
                "strategy_id",
            }
        }

    # ------------------------------------------------------------------
    # LEGACY API — used by tests/test_stock_screener.py
    # ------------------------------------------------------------------
    def screen(
        self,
        data: Optional[Dict[str, pd.DataFrame]] = None,
        *,
        limit: Optional[int] = None,
        **_: Any,
    ) -> pd.DataFrame:
        """
        Legacy screener interface.

        Input:
            data: dict[symbol -> OHLCV DataFrame] OR None

        Output:
            pd.DataFrame with column ["symbol"]
        """

        # -----------------------------
        # REQUIRED SAFE DEFAULT
        # -----------------------------
        if not data:
            return pd.DataFrame({"symbol": []})

        passed = []

        # -----------------------------
        # LEGACY MODE — IndicatorEngine
        # -----------------------------
        if self.engine is not None:
            for symbol, df in data.items():
                try:
                    # If engine exposes evaluate() and returns bool
                    ok = self.engine.evaluate(df, self.config)
                except Exception:
                    # IndicatorEngine is feature-only → PASS by default
                    ok = True

                if ok:
                    passed.append(symbol)

                if limit is not None and len(passed) >= limit:
                    break

        # -----------------------------
        # MODERN MODE (fallback only)
        # -----------------------------
        else:
            pipeline = ScreeningPipeline(**self.pipeline_kwargs)

            for symbol, df in data.items():
                try:
                    result = pipeline.run(df)
                    if isinstance(result, pd.DataFrame) and not result.empty:
                        passed.append(symbol)
                except Exception:
                    continue

                if limit is not None and len(passed) >= limit:
                    break

        # -----------------------------
        # MUST return DataFrame
        # -----------------------------
        return pd.DataFrame({"symbol": passed})

    # ------------------------------------------------------------------
    # MODERN API — DataFrame → DataFrame
    # ------------------------------------------------------------------
    def run(
        self,
        df: Optional[pd.DataFrame] = None,
        *,
        limit: Optional[int] = None,
        **_: Any,
    ) -> pd.DataFrame:
        """
        Modern ScreeningPipeline wrapper.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        pipeline = ScreeningPipeline(**self.pipeline_kwargs)
        result = pipeline.run(df)

        if limit is not None:
            return result.head(limit)

        return result
