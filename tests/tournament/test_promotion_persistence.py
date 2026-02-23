# tests/tournament/test_promotion_persistence.py

import shutil
from datetime import datetime, timezone

from core.tournament.metrics_contract import StrategyMetrics
from core.tournament.promotion_contracts import PromotionDecision
from core.tournament.promotion_persister import persist_promotion_decisions
from core.tournament.promotion_store import PromotionStore


def _metrics(strategy_id: str):
    return StrategyMetrics(
        strategy_id=strategy_id,
        metrics_version="v1",
        computed_at=datetime.now(timezone.utc),

        total_trades=300,
        win_trades=240,
        loss_trades=60,
        ssr=0.8,

        max_drawdown_pct=10.0,
        max_single_loss_pct=2.0,

        avg_rr=1.5,
        expectancy=0.4,

        time_in_market_pct=20.0,
        avg_trade_duration=15.0,

        volatility_sensitivity={},
        symbol_count=25,
        notes=[],
    )


def test_promotion_persistence(tmp_path):
    store = PromotionStore(root_dir=tmp_path)

    metrics = [_metrics("s1"), _metrics("s2")]

    decisions = [
        PromotionDecision("s1", True, []),
        PromotionDecision("s2", False, ["SSR below threshold"]),
    ]

    persist_promotion_decisions(
        run_id="run_001",
        metrics_list=metrics,
        decisions=decisions,
        store=store,
    )

    results = store.load_run("run_001")

    assert len(results) == 2
    ids = {r["strategy_id"] for r in results}
    assert ids == {"s1", "s2"}

    promoted = {r["strategy_id"]: r["promoted"] for r in results}
    assert promoted["s1"] is True
    assert promoted["s2"] is False
