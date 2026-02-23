from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class MutationEngine:
    """
    Apply deterministic feature transformations (mutations)
    to a pandas DataFrame.

    Config example:
    {
        "pct_change": ["close", "volume"],
        "rolling": {
            "close": [{"window": 5, "op": "mean"}, {"window": 20, "op": "std"}]
        },
        "lag": {"close": [1, 5]},
        "clip": {"close": [-3, 3]},
        "normalize": {"close": "zscore"}
    }
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}

    # ---------------- CORE METHODS -----------------

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        if "pct_change" in self.config:
            out = self._apply_pct_change(out, self.config["pct_change"])

        if "rolling" in self.config:
            out = self._apply_rolling(out, self.config["rolling"])

        if "lag" in self.config:
            out = self._apply_lags(out, self.config["lag"])

        if "clip" in self.config:
            out = self._apply_clip(out, self.config["clip"])

        if "winsor" in self.config:
            out = self._apply_winsor(out, self.config["winsor"])

        if "normalize" in self.config:
            out = self._apply_normalize(out, self.config["normalize"])

        return out

    # ---------------- MUTATION OPS -----------------

    def _apply_pct_change(self, df, cols: List[str]):
        for c in cols:
            df[f"{c}_pct"] = df[c].pct_change().fillna(0)
        return df

    def _apply_rolling(self, df, cfg: Dict[str, Any]):
        for col, ops in cfg.items():
            for spec in ops:
                w = spec["window"]
                op = spec["op"]
                name = f"{col}_r{w}_{op}"

                if op == "mean":
                    df[name] = df[col].rolling(w).mean()
                elif op == "std":
                    df[name] = df[col].rolling(w).std()
                elif op == "sum":
                    df[name] = df[col].rolling(w).sum()
                else:
                    raise ValueError(f"Unsupported rolling op: {op}")

        return df

    def _apply_lags(self, df, lag_cfg):
        for col, lags in lag_cfg.items():
            for L in lags:
                df[f"{col}_lag{L}"] = df[col].shift(L)
        return df

    def _apply_clip(self, df, clip_cfg):
        for col, (lo, hi) in clip_cfg.items():
            df[f"{col}_clip"] = df[col].clip(lo, hi)
        return df

    def _apply_winsor(self, df, win_cfg):
        # win_cfg: {col: [p_low, p_high]}
        for col, (lo_p, hi_p) in win_cfg.items():
            lo_v = df[col].quantile(lo_p)
            hi_v = df[col].quantile(hi_p)
            df[f"{col}_win"] = df[col].clip(lo_v, hi_v)
        return df

    def _apply_normalize(self, df, norm_cfg):
        # norm_cfg: {col: "zscore" | "minmax"}
        for col, mode in norm_cfg.items():
            x = df[col]
            if mode == "zscore":
                df[f"{col}_z"] = (x - x.mean()) / (x.std() + 1e-9)
            elif mode == "minmax":
                df[f"{col}_mm"] = (x - x.min()) / (x.max() - x.min() + 1e-9)
            else:
                raise ValueError(f"Unsupported normalize mode: {mode}")
        return df
