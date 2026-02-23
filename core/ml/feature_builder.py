# core/ml/feature_builder.py

from typing import Dict, List


class FeatureBuilder:
    """
    Builds ML features from telemetry.
    No access to execution or risk.
    """

    @staticmethod
    def build_from_trades(trades: List[dict]) -> Dict[str, float]:
        if not trades:
            return {}

        wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
        total = len(trades)

        return {
            "win_rate": wins / total if total else 0.0,
            "trade_count": float(total),
        }

    @staticmethod
    def build_from_tournament(result: dict) -> Dict[str, float]:
        return {
            "ssr": result.get("ssr", 0.0),
            "total_trades": result.get("total_trades", 0),
        }
