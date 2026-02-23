# core/tournament/paper_metrics.py

from typing import Iterable

from core.tournament.paper_contracts import PaperEvaluation


def compute_paper_ssr(win_trades: int, total_trades: int) -> float:
    if total_trades == 0:
        return 0.0
    return win_trades / total_trades


def build_paper_evaluation(
    *,
    run_id: str,
    strategy_id: str,
    trades: Iterable,
    slippage_pct: float,
    avg_latency_ms: float,
    risk_blocks: int,
    metrics_version: str,
    paper_version: str = "t5_v1",
) -> PaperEvaluation:

    trades = list(trades)
    total_trades = len(trades)

    win_trades = sum(1 for t in trades if t.pnl > 0)
    loss_trades = sum(1 for t in trades if t.pnl <= 0)

    paper_ssr = compute_paper_ssr(win_trades, total_trades)

    return PaperEvaluation(
        run_id=run_id,
        strategy_id=strategy_id,

        total_trades=total_trades,
        win_trades=win_trades,
        loss_trades=loss_trades,

        paper_ssr=paper_ssr,

        slippage_pct=slippage_pct,
        avg_latency_ms=avg_latency_ms,
        risk_blocks=risk_blocks,

        metrics_version=metrics_version,
        paper_version=paper_version,

        evaluated_at=PaperEvaluation.now_utc(),
        notes=[],
    )
