from core.dashboard_read.providers.paper import build_paper_state
from core.dashboard_read.snapshot import PaperState


def test_paper_state(monkeypatch):
    class DummyPaperMetrics:
        enabled = True
        trades_executed = 50
        pnl = 12500.0
        win_rate = 0.58
        drawdown = 0.12

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.paper.read_paper_metrics",
        lambda: DummyPaperMetrics(),
    )

    state = build_paper_state()

    assert isinstance(state, PaperState)
    assert state.pnl == 12500.0
    assert state.drawdown == 0.12
