# core/strategy_factory/health/metrics.py
def bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


def weighted_score(weights: dict, values: dict) -> float:
    score = 0.0
    for k, w in weights.items():
        score += w * values.get(k, 0.0)
    return bounded(score)
