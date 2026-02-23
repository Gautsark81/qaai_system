from datetime import datetime

from core.v2.live_bridge.guards.divergence_guard import DivergenceGuard
from core.v2.live_bridge.shadow.drift_snapshot import DriftSnapshot


def test_divergence_guard_allows_when_close():
    guard = DivergenceGuard(max_pnl_diff=10.0, max_trade_diff=1)

    snapshot = DriftSnapshot(
        strategy_id="s1",
        paper_pnl=100.0,
        live_pnl=95.0,
        paper_trades=10,
        live_trades=10,
        captured_at=datetime.utcnow(),
    )

    decision = guard.evaluate(
        snapshot=snapshot,
        now=datetime.utcnow(),
    )

    assert decision.allowed is True
    assert decision.reasons == []


def test_divergence_guard_detects_pnl_divergence():
    guard = DivergenceGuard(max_pnl_diff=10.0, max_trade_diff=1)

    snapshot = DriftSnapshot(
        strategy_id="s2",
        paper_pnl=100.0,
        live_pnl=50.0,
        paper_trades=10,
        live_trades=10,
        captured_at=datetime.utcnow(),
    )

    decision = guard.evaluate(
        snapshot=snapshot,
        now=datetime.utcnow(),
    )

    assert decision.allowed is False
    assert "pnl_divergence" in decision.reasons


def test_divergence_guard_detects_trade_count_divergence():
    guard = DivergenceGuard(max_pnl_diff=10.0, max_trade_diff=1)

    snapshot = DriftSnapshot(
        strategy_id="s3",
        paper_pnl=100.0,
        live_pnl=100.0,
        paper_trades=10,
        live_trades=15,
        captured_at=datetime.utcnow(),
    )

    decision = guard.evaluate(
        snapshot=snapshot,
        now=datetime.utcnow(),
    )

    assert decision.allowed is False
    assert "trade_count_divergence" in decision.reasons
