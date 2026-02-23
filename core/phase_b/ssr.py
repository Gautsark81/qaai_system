from typing import Optional
from core.phase_b.metrics import StrategyMetrics


def compute_ssr(metrics: StrategyMetrics) -> Optional[float]:
    """
    Strategy Success Ratio (SSR)

    Placeholder formula (Phase O):
    SSR = win_rate * log(1 + trades)
    """
    if metrics.win_rate is None:
        return None

    return metrics.win_rate * (1 + metrics.trades) ** 0.5
