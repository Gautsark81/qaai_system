from datetime import datetime, timezone

from core.tournament.paper_contracts import PaperEvaluation
from core.tournament.live_promotion_gate import evaluate_for_live
from core.tournament.live_promotion_contracts import LivePromotionThresholds


def _paper(
    *,
    run_id="run_paper",
    strategy_id="s1",
    ssr=0.85,
    trades=150,
    slip=0.10,
    lat=120.0,
    blocks=0,
):
    return PaperEvaluation(
        run_id=run_id,
        strategy_id=strategy_id,
        total_trades=trades,
        win_trades=int(trades * ssr),
        loss_trades=trades - int(trades * ssr),
        paper_ssr=ssr,
        slippage_pct=slip,
        avg_latency_ms=lat,
        risk_blocks=blocks,
        metrics_version="v1",
        paper_version="t5_v1",
        evaluated_at=datetime.now(timezone.utc),
        notes=[],
    )


def test_promote_when_all_rules_pass():
    ev = _paper()
    d = evaluate_for_live(ev, LivePromotionThresholds())
    assert d.promoted is True
    assert d.reasons == []


def test_reject_on_multiple_violations():
    ev = _paper(ssr=0.6, trades=50, slip=0.5, lat=400.0, blocks=1)
    d = evaluate_for_live(ev, LivePromotionThresholds())
    assert d.promoted is False
    assert len(d.reasons) >= 3
