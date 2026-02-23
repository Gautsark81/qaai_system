# core/live/live_approval.py

import yaml
from pathlib import Path


class LiveApproval:
    """
    Human approval validator for LIVE trading.
    """

    def __init__(self, base_path: str = "data/live/approvals"):
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)

    def is_approved(self, strategy_id: str) -> bool:
        approval_file = self.base / f"{strategy_id}.yaml"
        return approval_file.exists()

    def load(self, strategy_id: str) -> dict:
        approval_file = self.base / f"{strategy_id}.yaml"
        if not approval_file.exists():
            raise RuntimeError("LIVE approval missing")

        return yaml.safe_load(approval_file.read_text())
