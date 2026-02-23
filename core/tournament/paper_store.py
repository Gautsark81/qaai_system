# core/tournament/paper_store.py

import json
from pathlib import Path
from typing import Iterable, List

from core.tournament.paper_contracts import PaperEvaluation


class PaperEvaluationStore:
    """
    Append-only store for paper trading evaluations.
    """

    def __init__(self, root_dir: str = "tournament/paper_evaluations"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def persist(self, evaluations: Iterable[PaperEvaluation]) -> None:
        for ev in evaluations:
            self._write(ev)

    def _write(self, ev: PaperEvaluation) -> None:
        run_dir = self.root / ev.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        path = run_dir / f"{ev.strategy_id}.json"

        # Immutable rule: never overwrite
        if path.exists():
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_id": ev.run_id,
                    "strategy_id": ev.strategy_id,
                    "total_trades": ev.total_trades,
                    "win_trades": ev.win_trades,
                    "loss_trades": ev.loss_trades,
                    "paper_ssr": ev.paper_ssr,
                    "slippage_pct": ev.slippage_pct,
                    "avg_latency_ms": ev.avg_latency_ms,
                    "risk_blocks": ev.risk_blocks,
                    "metrics_version": ev.metrics_version,
                    "paper_version": ev.paper_version,
                    "evaluated_at": ev.evaluated_at.isoformat(),
                    "notes": ev.notes,
                },
                f,              # ✅ FIX: pass file handle
                indent=2,
            )

    def load_run(self, run_id: str) -> List[dict]:
        run_dir = self.root / run_id
        if not run_dir.exists():
            return []

        out: List[dict] = []
        for path in sorted(run_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                out.append(json.load(f))
        return out
