# core/strategy_factory/probability_layers.py

from typing import Dict


class ProbabilityLayers:
    """
    Hard-gated confirmation layers.
    ALL must pass.
    """

    @staticmethod
    def structural_trap(ctx: Dict) -> bool:
        return (
            ctx["price_trap"] and
            ctx["vwap_reclaim"]
        )

    @staticmethod
    def volume_confirmation(ctx: Dict) -> bool:
        return ctx["volume_cluster"] and ctx["volume_above_avg"]

    @staticmethod
    def microstructure(ctx: Dict) -> bool:
        return ctx["order_imbalance"] > 1.5

    @staticmethod
    def correlation(ctx: Dict) -> bool:
        return ctx["sector_trend"] >= 0

    @staticmethod
    def trend_overlay(ctx: Dict) -> bool:
        return (
            ctx["supertrend_direction"] == ctx["trade_direction"] and
            ctx["ema_alignment"]
        )

    @staticmethod
    def volatility_overlay(ctx: Dict) -> bool:
        return ctx["atr_ok"] and ctx["bollinger_expansion"]
