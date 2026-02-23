from typing import Optional, List, Tuple, Iterable
from dataclasses import dataclass

from core.screening.rules import MarketSnapshot
from core.screening.scorer import ScreeningScorer

# ============================================================
# Canonical ScreeningResult (single source of truth)
# ============================================================
from screening.result import ScreeningResult


# ============================================================
# ScreenConfig — canonical if present, fallback if not
# ============================================================
try:
    from core.screening.config import ScreenConfig
except ModuleNotFoundError:
    @dataclass(frozen=True)
    class ScreenConfig:
        name: str
        timeframe: str
        top_n: int = 10
        min_liquidity: float = 0.0
        watchlist_name: Optional[str] = None
        prefer_feature_score: bool = True


# ============================================================
# ENGINE
# ============================================================
class ScreeningEngine:
    """
    Deterministic screening engine.

    Guarantees:
    - Deterministic ordering
    - Signed momentum preserved
    - FeatureStore API tolerant
    """

    def __init__(self, rules=None):
        self.rules = rules or []
        self.scorer = ScreeningScorer()

    # -------------------------------------------------
    # RULE-ONLY SNAPSHOT
    # -------------------------------------------------
    def screen(self, snap):
        for rule in self.rules:
            if not rule.evaluate(snap):
                return type(
                    "Decision",
                    (),
                    {
                        "symbol": snap.symbol,
                        "passed": False,
                        "reasons": [rule.name],
                        "failed_rules": [rule.name],
                    },
                )()
        return type(
            "Decision",
            (),
            {
                "symbol": snap.symbol,
                "passed": True,
                "reasons": ["passed"],
                "failed_rules": [],
            },
        )()

    # -------------------------------------------------
    # CONTEXT SCREENING
    # -------------------------------------------------
    def run(self, ctx, cfg: ScreenConfig) -> List[ScreeningResult]:
        ranked: List[Tuple[float, float, ScreeningResult]] = []

        # -----------------------------
        # Resolve universe
        # -----------------------------
        if hasattr(ctx, "universe"):
            symbols: Iterable[str] = ctx.universe
        elif hasattr(ctx, "watchlists") and cfg.watchlist_name:
            symbols = ctx.watchlists.get(cfg.watchlist_name, [])
        else:
            raise ValueError("No symbol universe available")

        # -----------------------------
        # Evaluate
        # -----------------------------
        for symbol in symbols:
            bars = ctx.ohlcv_store.get_bars(
                symbol=symbol,
                timeframe=cfg.timeframe,
                limit=1,
            )
            if not bars:
                continue

            bar = bars[-1]
            liquidity = bar.close * bar.volume

            if liquidity < cfg.min_liquidity:
                continue

            # -----------------------------
            # Feature store (tolerant)
            # -----------------------------
            features = {}
            fs = getattr(ctx, "feature_store", None)

            if fs is not None and hasattr(fs, "get"):
                try:
                    features = fs.get(symbol, cfg.timeframe) or {}
                except TypeError:
                    features = fs.get(symbol) or {}

            snap = MarketSnapshot(
                symbol=symbol,
                timeframe=cfg.timeframe,
                close=bar.close,
                volume=bar.volume,
                atr=features.get("atr", 0.0),
                volatility=features.get("volatility", 0.0),
                features=features,
            )

            decision = self.screen(snap)
            if not decision.passed:
                continue

            # -----------------------------
            # Scoring (signed)
            # -----------------------------
            if cfg.prefer_feature_score:
                score = float(self.scorer.score(snap))
            else:
                open_px = features.get("open", bar.open)
                close_px = features.get("close", bar.close)
                score = float(close_px - open_px)

            result = ScreeningResult(
                symbol=symbol,
                passed=True,
                reasons=["passed"],
                score=score,
                liquidity=liquidity,
            )

            ranked.append((score, liquidity, result))

        # -----------------------------
        # Sort: |score| DESC → liquidity DESC
        # -----------------------------
        ranked.sort(
            key=lambda x: (abs(x[0]), x[1]),
            reverse=True,
        )

        return [r for _, _, r in ranked[: cfg.top_n]]

    # Backward compatibility
    run_screen = run
