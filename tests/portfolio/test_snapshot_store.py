from datetime import datetime
from pathlib import Path

from modules.portfolio.state import PortfolioSnapshot, Position
from modules.portfolio.snapshots import PortfolioSnapshotStore
from modules.portfolio.state import Symbol, StrategyId


def test_snapshot_persistence_and_replay(tmp_path: Path):
    store = PortfolioSnapshotStore(tmp_path)

    snap = PortfolioSnapshot(
        timestamp=datetime(2025, 1, 1, 9, 30),
        cash=100_000,
        realized_pnl=500,
        metrics={"equity": 100_500},
        positions={
            Symbol("NIFTY"): Position(
                symbol=Symbol("NIFTY"),
                quantity=10,
                avg_price=100,
                strategy_id=StrategyId("trend"),
            )
        },
    )

    store.append(snap)

    loaded = store.load_all()
    assert len(loaded) == 1

    replay = loaded[0]
    assert replay.cash == snap.cash
    assert replay.realized_pnl == snap.realized_pnl
    assert replay.metrics["equity"] == 100_500
    assert replay.positions[Symbol("NIFTY")].quantity == 10
