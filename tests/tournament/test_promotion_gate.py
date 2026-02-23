# tests/tournament/test_promotion_gate.py

from datetime import datetime, timezone

from core.tournament.metrics_contract import StrategyMetrics
from core.tournament.promotion_gate import evaluate_for_paper
from core.tournament.promotion_contracts import PromotionThresholds


def _metrics(
    *,
    strategy_id="s1",
    ssr=0.85,
    trades=300,
    dd=10.0,
    max_loss=2.0,
):
    return StrategyMetrics(
        strategy_id=strategy_id,
        metrics_version="v1",
        computed_at=datetime.now(timezone.utc),

        total_trades=trades,
        win_trades=int(trades * ssr),
        loss_trades=trades - int(trades * ssr),

        ssr=ssr,

        max_drawdown_pct=dd,
        max_single_loss_pct=max_loss,

        avg_rr=1.5,
        expectancy=0.4,

        time_in_market_pct=20.0,
        avg_trade_duration=15.0,

        volatility_sensitivity={},
        symbol_count=25,
        notes=[],
    )


def test_strategy_promoted_when_all_rules_pass():
    metrics = _metrics()
    decision = evaluate_for_paper(metrics, PromotionThresholds())

    assert decision.promoted is True
    assert decision.reasons == []


def test_reject_low_ssr():
    metrics = _metrics(ssr=0.6)
    decision = evaluate_for_paper(metrics, PromotionThresholds())

    assert decision.promoted is False
    assert any("SSR below threshold" in r for r in decision.reasons)


def test_reject_insufficient_trades():
    metrics = _metrics(trades=50)
    decision = evaluate_for_paper(metrics, PromotionThresholds())

    assert decision.promoted is False
    assert any("Insufficient trades" in r for r in decision.reasons)


def test_reject_high_drawdown():
    metrics = _metrics(dd=25.0)
    decision = evaluate_for_paper(metrics, PromotionThresholds())

    assert decision.promoted is False
    assert any("Max drawdown too high" in r for r in decision.reasons)


def test_multiple_failures_reported():
    metrics = _metrics(ssr=0.5, trades=50, dd=30.0)
    decision = evaluate_for_paper(metrics, PromotionThresholds())

    assert decision.promoted is False
    assert len(decision.reasons) >= 2
