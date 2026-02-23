import json
from pathlib import Path
from typing import List

from core.telemetry.metrics_snapshot import MetricsSnapshot


class MetricsHistoryStore:
    """
    Append-only store for metrics snapshots.
    Read-only consumers (dashboard) must never mutate.
    """

    def __init__(self, root_dir: str | Path = "metrics_history"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def append(self, snapshot: MetricsSnapshot) -> None:
        """
        Persist snapshot as append-only JSONL.
        """
        path = self.root / f"{snapshot.strategy_id}.jsonl"

        with open(path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "strategy_id": snapshot.strategy_id,
                        "source": snapshot.source,
                        "ssr": snapshot.ssr,
                        "total_trades": snapshot.total_trades,
                        "max_drawdown": snapshot.max_drawdown,
                        "avg_rr": snapshot.avg_rr,
                        "latency_ms": snapshot.latency_ms,
                        "slippage_pct": snapshot.slippage_pct,
                        "recorded_at": snapshot.recorded_at.isoformat(),
                        "version": snapshot.version,
                    }
                )
                + "\n"
            )

    def load(self, strategy_id: str) -> List[dict]:
        """
        Load all historical snapshots for a strategy.
        """
        path = self.root / f"{strategy_id}.jsonl"
        if not path.exists():
            return []

        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]
