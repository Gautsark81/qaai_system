# tests/tournament/test_paper_evaluation.py

from core.tournament.paper_metrics import build_paper_evaluation
from core.tournament.paper_store import PaperEvaluationStore


class DummyTrade:
    def __init__(self, pnl: float):
        self.pnl = pnl


def test_paper_metrics_computation():
    trades = [DummyTrade(5), DummyTrade(-3), DummyTrade(4)]

    ev = build_paper_evaluation(
        run_id="run_paper_001",
        strategy_id="s1",
        trades=trades,
        slippage_pct=0.12,
        avg_latency_ms=45.0,
        risk_blocks=1,
        metrics_version="v1",
    )

    assert ev.total_trades == 3
    assert ev.win_trades == 2
    assert ev.loss_trades == 1
    assert abs(ev.paper_ssr - (2 / 3)) < 1e-9


def test_paper_persistence(tmp_path):
    store = PaperEvaluationStore(root_dir=tmp_path)

    ev = build_paper_evaluation(
        run_id="run_paper_002",
        strategy_id="s2",
        trades=[DummyTrade(1)],
        slippage_pct=0.05,
        avg_latency_ms=30.0,
        risk_blocks=0,
        metrics_version="v1",
    )

    store.persist([ev])

    loaded = store.load_run("run_paper_002")
    assert len(loaded) == 1
    assert loaded[0]["strategy_id"] == "s2"
