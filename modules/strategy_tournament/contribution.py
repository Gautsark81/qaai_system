# modules/strategy_tournament/contribution.py

from dataclasses import dataclass
from modules.strategy_tournament.metrics import SymbolMetrics
from modules.strategy_tournament.portfolio_state import PortfolioState
from modules.strategy_tournament.ssr import compute_ssr


@dataclass(frozen=True)
class Contribution:
    delta_ssr: float
    delta_drawdown: float
    delta_symbols: int


def compute_contribution(
    baseline: PortfolioState,
    candidate_metrics: list[SymbolMetrics],
    max_dd_threshold: float,
) -> Contribution:
    base_ssr = compute_ssr(
        [m for metrics in baseline.symbol_metrics.values() for m in metrics],
        max_dd_threshold,
    )

    new_metrics = baseline.symbol_metrics.copy()
    new_metrics["candidate"] = candidate_metrics

    new_ssr = compute_ssr(
        [m for metrics in new_metrics.values() for m in metrics],
        max_dd_threshold,
    )

    delta_dd = min(
        m.max_drawdown for m in candidate_metrics
    ) - baseline.max_drawdown

    return Contribution(
        delta_ssr=new_ssr - base_ssr,
        delta_drawdown=-delta_dd,  # lower DD = positive
        delta_symbols=len(candidate_metrics),
    )
