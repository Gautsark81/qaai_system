# strategies/momentum_intraday.py

from __future__ import annotations

from typing import Any, Dict, Optional

from strategies.base import StrategyBase

# Local type aliases – tests don't care about these names, just the behavior
BarDict = Dict[str, Any]
FeatureDict = Dict[str, Any]
OrderDict = Dict[str, Any]


class MomentumIntradayStrategy(StrategyBase):
    """
    Very simple intraday momentum strategy used mainly for testing wiring,
    but also safe to use as a production building block.

    Rules (as expected by tests)
    ----------------------------
    - Use `features["screen_score"]` as the signal.
    - If abs(score) < min_score or score == 0 => no trade (return None).
    - score > 0  => BUY
      score < 0  => SELL
    - Base position size is `base_size`.
    - If `max_size` > 0, cap size at `max_size`.
    - If `inv_vol_target` > 0 and `atr` is provided:
        size_cap_by_vol = inv_vol_target / atr
        final size = min(current_size, size_cap_by_vol)
    - If final size <= 0 => no trade.

    Production extras (non-breaking)
    --------------------------------
    - Optional SL/TP hints encoded in ATR units:
        sl_dist_atr = atr * sl_atr_mult
        tp_dist_atr = atr * tp_atr_mult
      These are only hints and are not used in tests.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config=config)

        # Strategy parameters with sensible defaults
        self.min_score: float = float(config.get("min_score", 0.0))
        self.base_size: float = float(config.get("base_size", 1.0))
        self.max_size: float = float(config.get("max_size", 0.0))  # 0 => no explicit cap
        self.inv_vol_target: float = float(config.get("inv_vol_target", 0.0))  # 0 => disabled

        # Optional ATR-based SL/TP distances (in ATR multiples, not prices)
        self.sl_atr_mult: float = float(config.get("sl_atr_mult", 0.0))  # 0 => disabled
        self.tp_atr_mult: float = float(config.get("tp_atr_mult", 0.0))  # 0 => disabled

        # Tag is useful for logging / attribution in tests & router
        self.tag: str = str(config.get("tag", config.get("name", "MOM_INTRADAY")))

    def on_bar(
        self,
        symbol: str,
        bar: BarDict,
        features: FeatureDict,
    ) -> Optional[OrderDict]:
        # 1) Extract and validate score
        raw_score = features.get("screen_score", 0.0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            # If score is missing or non-numeric, do nothing
            return None

        # No trade if score is 0 or below threshold
        if score == 0.0 or abs(score) < self.min_score:
            return None

        # 2) Direction from sign of score
        side = "BUY" if score > 0 else "SELL"

        # 3) Start from base_size (tests use this behaviour)
        size = float(self.base_size)

        # 4) Apply max_size cap if configured (> 0)
        if self.max_size and self.max_size > 0.0:
            size = min(size, float(self.max_size))

        # 5) Optional inverse-vol scaling using ATR
        atr = features.get("atr", None)
        if (
            self.inv_vol_target
            and self.inv_vol_target > 0.0
            and isinstance(atr, (int, float))
            and atr > 0.0
        ):
            max_by_vol = float(self.inv_vol_target) / float(atr)
            size = min(size, max_by_vol)

        # 6) Final guard: if size collapsed to <= 0, skip
        if size <= 0.0:
            return None

        # 6b) Optional SL/TP hints in ATR units (for router/risk engine)
        sl_dist_atr: Optional[float] = None
        tp_dist_atr: Optional[float] = None
        if isinstance(atr, (int, float)) and atr > 0.0:
            if self.sl_atr_mult > 0.0:
                sl_dist_atr = float(atr) * self.sl_atr_mult
            if self.tp_atr_mult > 0.0:
                tp_dist_atr = float(atr) * self.tp_atr_mult

        # 7) Build order dict; include meta with strategy + screen_score
        #    NOTE: Tests assert:
        #      - meta["strategy"] == tag
        #      - meta["screen_score"] == score
        order: OrderDict = {
            "symbol": symbol,
            "side": side,
            "size": size,
            "qty": size,
            "tag": self.tag,
            "score": score,  # top-level for convenience
            "meta": {
                "strategy": self.tag,
                "screen_score": score,
                # Optional risk hints for production router:
                "atr": atr,
                "sl_dist_atr": sl_dist_atr,
                "tp_dist_atr": tp_dist_atr,
                "sl_atr_mult": self.sl_atr_mult,
                "tp_atr_mult": self.tp_atr_mult,
            },
        }

        return order
