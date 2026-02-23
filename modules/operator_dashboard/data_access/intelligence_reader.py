from pathlib import Path
from typing import List, Dict
from intelligence.snapshots.snapshot_reader import SnapshotReader
from modules.operator_dashboard.data_contracts import StrategySnapshotDTO


class IntelligenceReader:
    def __init__(self):
        self.reader = SnapshotReader(
            Path("intelligence/snapshots/data")
        )

    # -------------------------------------------------
    def list_strategies(self) -> List[str]:
        return sorted(self.reader.list_strategies())

    # -------------------------------------------------
    def latest_snapshot(self, strategy_id: str) -> StrategySnapshotDTO | None:
        snap = self.reader.latest(strategy_id)
        return self._to_dto(snap) if snap else None

    # -------------------------------------------------
    def latest_snapshots(self) -> List[StrategySnapshotDTO]:
        result = []
        for sid in self.list_strategies():
            snap = self.reader.latest(sid)
            if snap:
                result.append(self._to_dto(snap))
        return result

    # -------------------------------------------------
    def history(self, strategy_id: str) -> List[StrategySnapshotDTO]:
        return [
            self._to_dto(s)
            for s in self.reader.history(strategy_id)
        ]

    # -------------------------------------------------
    @staticmethod
    def _to_dto(snap) -> StrategySnapshotDTO:
        return StrategySnapshotDTO(
            snapshot_id=snap.snapshot_id,
            strategy_id=snap.strategy_id,
            strategy_version=snap.strategy_version,
            created_at=snap.created_at,
            window_start=snap.window_start,
            window_end=snap.window_end,
            stage=snap.stage,
            ssr=snap.ssr,
            expectancy=snap.expectancy,
            max_drawdown=snap.max_drawdown,
            total_trades=snap.total_trades,
            win_rate=snap.win_rate,
            symbol_metrics=snap.symbol_metrics,
            regime_metrics=snap.regime_metrics,
            risk_events=snap.risk_events,
            governance_flags=snap.governance_flags,
            notes=snap.notes,
            schema_version=snap.schema_version,
        )
