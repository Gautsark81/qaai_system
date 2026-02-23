# core/strategy_factory/probability_map.py

from core.strategy_factory.probability_layers import ProbabilityLayers


class ProbabilityMap:
    """
    Evaluates BUY / SELL probability zones.
    """

    @staticmethod
    def evaluate(ctx: dict) -> dict:
        layers = {
            "structural": ProbabilityLayers.structural_trap(ctx),
            "volume": ProbabilityLayers.volume_confirmation(ctx),
            "microstructure": ProbabilityLayers.microstructure(ctx),
            "correlation": ProbabilityLayers.correlation(ctx),
            "trend": ProbabilityLayers.trend_overlay(ctx),
            "volatility": ProbabilityLayers.volatility_overlay(ctx),
        }

        passed = all(layers.values())

        score = round(sum(1 for v in layers.values() if v) / len(layers), 2)

        return {
            "passed": passed,
            "layers": layers,
            "score": score,
        }
