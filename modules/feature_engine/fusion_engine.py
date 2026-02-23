from __future__ import annotations
import pandas as pd
from typing import Dict, List, Any


class FusionEngine:
    """
    Combines multiple feature sets using join, weighting, or stacking.

    config example:
    {
        "mode": "join",          # join | weighted | stacking
        "on": "timestamp",
        "weighted": {"close_z": 0.7, "sentiment": 0.3}
    }
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.mode = self.config.get("mode", "join")

    # ---------------- MAIN ENTRY -----------------
    def fuse(self, frames: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        if self.mode == "join":
            return self._fuse_join(frames)
        elif self.mode == "weighted":
            return self._fuse_weighted(frames)
        elif self.mode == "stacking":
            return self._fuse_stacking(frames)
        else:
            raise ValueError(f"Unknown fusion mode: {self.mode}")

    # ---------------- MODES ----------------------

    def _fuse_join(self, frames):
        keys = list(frames.keys())
        out = frames[keys[0]]
        join_key = self.config.get("on", "timestamp")
        for k in keys[1:]:
            out = out.merge(frames[k], on=join_key, how="inner")
        return out

    def _fuse_weighted(self, frames):
        """
        Weighted blending of numeric features across frames.

        Behavior:
        - Performs an inner join of frames on the join key.
        - For each requested base column name in the `weighted` map, tries:
            1) exact column match in merged
            2) first column in merged whose name startswith the base name
            3) first column in merged whose name contains the base name
        - Uses the first successful match; raises if none found.
        """
        weights = self.config.get("weighted", {})
        join_key = self.config.get("on", "timestamp")

        # Merge all frames (inner join) preserving pandas default suffixing for colliding names.
        merged = self._fuse_join(frames).set_index(join_key)

        weighted_components = {}
        for base_col, w in weights.items():
            # direct match
            if base_col in merged.columns:
                match_col = base_col
            else:
                # try columns that startwith base_col (preserves left-frame preference)
                starts = [c for c in merged.columns if c.startswith(base_col)]
                contains = [c for c in merged.columns if base_col in c]
                match_col = None
                if starts:
                    match_col = starts[0]
                elif contains:
                    match_col = contains[0]

            if match_col is None:
                raise ValueError(f"Column {base_col} not found for weighted fusion (tried exact/start/contains).")

            # multiply by weight and keep as component column
            weighted_components[match_col] = merged[match_col] * float(w)

        if not weighted_components:
            # nothing to weight => empty result with join key only
            return merged.reset_index()[[join_key]]

        # sum all weighted components row-wise
        out = pd.DataFrame(index=merged.index)
        for comp_name, series in weighted_components.items():
            out[comp_name] = series

        out["weighted_fusion"] = out.sum(axis=1)
        out = out.reset_index()
        return out

    def _fuse_stacking(self, frames):
        """
        Creates a single vector-like stacked feature frame.
        """
        join = self._fuse_join(frames)
        # everything except join key becomes vector components
        join_key = self.config.get("on", "timestamp")
        feature_cols = [c for c in join.columns if c != join_key]

        join["stack_vector"] = join[feature_cols].values.tolist()
        return join[[join_key, "stack_vector"]]
