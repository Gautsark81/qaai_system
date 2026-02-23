from core.dashboard_read.snapshot import PaperState
from core.dashboard_read.providers._sources import paper as paper_source


def build_paper_state() -> PaperState:
    """
    Paper trading state provider.
    Copy-only.
    """

    metrics = paper_source.read_paper_metrics()

    return PaperState(
        pnl=metrics.pnl,
        drawdown=metrics.drawdown,
        active_positions=metrics.trades_executed,
    )
