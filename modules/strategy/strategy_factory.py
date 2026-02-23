from __future__ import annotations
import pandas as pd
import operator
from typing import Any, Dict, List, Union, Callable


# Supported comparison ops mapped to functions
_COMPARISONS: Dict[str, Callable[[pd.Series, Any], pd.Series]] = {
    ">": lambda s, v: s > v,
    "<": lambda s, v: s < v,
    ">=": lambda s, v: s >= v,
    "<=": lambda s, v: s <= v,
    "==": lambda s, v: s == v,
    "!=": lambda s, v: s != v,
}


class StrategyFactory:
    """
    Deterministic rule-based strategy loader & evaluator.

    Strategy config example (python dict):
    {
        "rules": {
            "r1": {"op": ">", "col": "close_z", "val": 1.5},
            "r2": {"op": "between", "col": "volume", "low": 1000, "high": 5000},
            "r3": {"and": ["r1", "r2"]},
            "long": {"and": ["r3", {"op": "==", "col": "trend", "val": 1}]}
        },
        "signals": {
            "buy": {"rule": "long", "value": 1},
            "sell": {"rule": {"op": "<", "col": "close_z", "val": -1.5}, "value": -1}
        }
    }

    Usage:
      sf = StrategyFactory(cfg)
      signals_df = sf.generate_signals(features_df)
    """

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg or {}
        self.rules = self.cfg.get("rules", {})
        self.signals_cfg = self.cfg.get("signals", {})

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate rules and return a DataFrame containing:
        - columns for each rule (bool -> int8)
        - named signal columns for each configured signal (int8)
        - an aggregated 'signal' column produced by aggregation strategy.

        Signal config entries (each) support:
          - "rule": rule_spec (string name or dict)
          - "value": int (1/-1/0) default 1
          - "priority": int (higher wins). Default 0.
          - "name": optional override for column name (key is used by default)

        Aggregation mode (top-level in self.cfg):
          - self.cfg.get("aggregation", "priority")
          - supported: "priority" (default), "sum_clip" (legacy behavior)
        """

        df = df.copy()
        # Evaluate and cache rules
        evaluated: Dict[str, pd.Series] = {}
        for name in self.rules:
            evaluated[name] = self._evaluate_rule(self.rules[name], df, evaluated)

        # Add rule columns (int8)
        for k, mask in evaluated.items():
            df[f"rule__{k}"] = mask.astype("int8")

        # Prepare signals: compute mask and metadata per configured signal
        # signals_cfg can be dict mapping name -> {rule, value, priority}
        signals_cfg = self.signals_cfg or {}
        # allow top-level aggregation mode override
        aggregation_mode = self.cfg.get("aggregation", "priority")

        # store per-signal masks & values
        sig_names = []
        sig_masks: Dict[str, pd.Series] = {}
        sig_values: Dict[str, int] = {}
        sig_priorities: Dict[str, int] = {}

        for sig_name, s_cfg in signals_cfg.items():
            # s_cfg can be a dict or a simple reference
            rule_spec = s_cfg.get("rule") if isinstance(s_cfg, dict) else s_cfg
            value = int(s_cfg.get("value", 1)) if isinstance(s_cfg, dict) else int(1)
            priority = int(s_cfg.get("priority", 0)) if isinstance(s_cfg, dict) else 0

            mask = self._evaluate_rule(rule_spec, df, evaluated)
            sig_names.append(sig_name)
            sig_masks[sig_name] = mask.fillna(False)
            sig_values[sig_name] = int(value)
            sig_priorities[sig_name] = int(priority)

            # add named per-signal column (int8) so callers can inspect
            df[sig_name] = sig_masks[sig_name].astype("int8") * sig_values[sig_name]

        # Build aggregated signal column
        n = len(df)
        # default 0 series
        agg = pd.Series([0] * n, index=df.index, dtype="int64")

        if aggregation_mode == "sum_clip":
            # legacy: sum all signals then clip
            for s in sig_names:
                agg = agg + df[s].astype("int64")
            agg = agg.clip(-1, 1).astype("int8")
        elif aggregation_mode == "priority":
            # priority aggregation:
            # for each row, find max priority among signals that are active
            # if none active -> 0
            # if one or more active at max priority -> sum those values, then clip
            # Implementation vectorized by computing DataFrame of (mask * priority) per signal.
            if not sig_names:
                agg = agg.astype("int8")
            else:
                # Build a DataFrame where each col = priority if mask True else -inf
                prio_matrix = {}
                val_matrix = {}
                for s in sig_names:
                    pr = sig_priorities[s]
                    # priority where mask True, else a very small number
                    prio_matrix[s] = sig_masks[s].astype("int64") * pr + (~sig_masks[s]).astype("int64") * (-(10**9))
                    # value where mask True else 0
                    val_matrix[s] = sig_masks[s].astype("int64") * sig_values[s]

                prio_df = pd.DataFrame(prio_matrix, index=df.index)
                val_df = pd.DataFrame(val_matrix, index=df.index)

                # max priority per row
                max_prio = prio_df.max(axis=1)

                # mask of which signals have priority == max_prio and are active
                selected = prio_df.eq(max_prio, axis=0) & (prio_df > -(10**9))

                # sum their corresponding values (tie-handling)
                selected_vals = val_df.where(selected, other=0)
                agg = selected_vals.sum(axis=1).clip(-1, 1).astype("int8")

        else:
            # unknown aggregation mode -> fall back to legacy sum_clip
            for s in sig_names:
                agg = agg + df[s].astype("int64")
            agg = agg.clip(-1, 1).astype("int8")

        df["signal"] = agg
        return df


    def _evaluate_rule(
        self,
        rule_spec: Union[str, Dict[str, Any]],
        df: pd.DataFrame,
        cache: Dict[str, pd.Series],
    ) -> pd.Series:
        """
        Evaluate a rule spec and return a boolean pd.Series.

        Supports:
          - named rule references (strings)
          - {"rule": ...} wrapper
          - logical ops: and/or/not
          - atomic ops: >, <, >=, <=, ==, !=, between, in

        Frame-qualified column support:
          - If rule col is "frame.colbase" then resolution behavior depends on
            self.cfg.get("frame_resolution", "lenient") which can be "lenient" or "strict".
          - Lenient (default): try multiple heuristics and fallback to previous behavior.
          - Strict: only accept explicit/standard merged column patterns (exact, colbase_frame, frame_colbase).
            If strict resolution fails, raise ValueError to surface misconfiguration.
        """
        # ----------------- named rule short-circuit -----------------
        if isinstance(rule_spec, str):
            if rule_spec in cache:
                return cache[rule_spec]
            if rule_spec in self.rules:
                out = self._evaluate_rule(self.rules[rule_spec], df, cache)
                cache[rule_spec] = out
                return out
            raise KeyError(f"Unknown rule name: {rule_spec}")

        # single-key wrapper {"rule": ...}
        if isinstance(rule_spec, dict) and "rule" in rule_spec and len(rule_spec) == 1:
            return self._evaluate_rule(rule_spec["rule"], df, cache)

        # logical ops
        if isinstance(rule_spec, dict) and "and" in rule_spec:
            masks = [self._evaluate_rule(s, df, cache) for s in rule_spec["and"]]
            return self._all(masks)
        if isinstance(rule_spec, dict) and "or" in rule_spec:
            masks = [self._evaluate_rule(s, df, cache) for s in rule_spec["or"]]
            return self._any(masks)
        if isinstance(rule_spec, dict) and "not" in rule_spec:
            m = self._evaluate_rule(rule_spec["not"], df, cache)
            return ~m.fillna(False)

        # atomic ops
        if isinstance(rule_spec, dict) and "op" in rule_spec:
            op = rule_spec["op"]
            col = rule_spec.get("col")
            if col is None:
                raise ValueError("Atomic rule missing 'col' field")

            # resolution mode: 'lenient' (default) or 'strict'
            mode = str(self.cfg.get("frame_resolution", "lenient")).lower()
            if mode not in ("lenient", "strict"):
                mode = "lenient"

            # ----------------- Column resolution -----------------
            series = None

            if isinstance(col, str) and "." in col:
                frame_key, col_base = col.split(".", 1)

                # 1) exact as written (rare but allowed)
                if col in df.columns:
                    series = df[col]
                else:
                    # Strict behavior: only accept canonical patterns
                    if mode == "strict":
                        # prefer "colbase_frame" then "frame_colbase" then exact
                        candidate_1 = f"{col_base}_{frame_key}"
                        candidate_2 = f"{frame_key}_{col_base}"

                        if candidate_1 in df.columns:
                            series = df[candidate_1]
                        elif candidate_2 in df.columns:
                            series = df[candidate_2]
                        else:
                            # strict mode: fail loudly
                            raise ValueError(
                                f"Strict frame match: could not resolve frame-qualified column '{col}'. "
                                f"Checked: '{candidate_1}', '{candidate_2}', and exact '{col}'. "
                                f"Available columns: {list(df.columns)}"
                            )
                    else:
                        # Lenient behavior: try several heuristics (backwards-compatible)
                        candidate_1 = f"{col_base}_{frame_key}"
                        candidate_2 = f"{frame_key}_{col_base}"

                        if candidate_1 in df.columns:
                            series = df[candidate_1]
                        elif candidate_2 in df.columns:
                            series = df[candidate_2]
                        else:
                            candidates = [c for c in df.columns if frame_key in c and col_base in c]
                            if candidates:
                                series = df[candidates[0]]
                            else:
                                starts = [c for c in df.columns if c.startswith(col_base)]
                                if starts:
                                    series = df[starts[0]]
                                else:
                                    series = None

            # fallback: unqualified column name or if col resolution failed
            if series is None:
                if col in df.columns:
                    series = df[col]
                else:
                    # create None-filled series to yield False after comparisons
                    series = pd.Series([None] * len(df), index=df.index)

            # ----------------- Perform requested atomic operation -----------------
            if op in _COMPARISONS:
                val = rule_spec.get("val")
                return _COMPARISONS[op](series, val).fillna(False)
            if op == "between":
                low = rule_spec.get("low")
                high = rule_spec.get("high")
                return series.between(low, high).fillna(False)
            if op == "in":
                vals = set(rule_spec.get("vals", []))
                return series.isin(vals).fillna(False)

            raise ValueError(f"Unsupported atomic op: {op}")

        raise ValueError(f"Unsupported rule_spec: {rule_spec}")

    @staticmethod
    def _all(masks: List[pd.Series]) -> pd.Series:
        if not masks:
            return pd.Series([True] * 0)
        out = masks[0].astype(bool)
        for m in masks[1:]:
            out = out & m.astype(bool)
        return out.fillna(False)

    @staticmethod
    def _any(masks: List[pd.Series]) -> pd.Series:
        if not masks:
            return pd.Series([False] * 0)
        out = masks[0].astype(bool)
        for m in masks[1:]:
            out = out | m.astype(bool)
        return out.fillna(False)
