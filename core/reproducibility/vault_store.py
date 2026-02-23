# core/reproducibility/vault_store.py

from __future__ import annotations
from pathlib import Path
import json
from typing import List

from .vault_models import BacktestReproducibilityRecord


class VaultStore:

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def append(self, record: BacktestReproducibilityRecord) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.__dict__, default=str))
            f.write("\n")

    def get_all(self) -> List[dict]:
        with self.path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def get_by_id(self, record_id: str) -> dict:
        for record in self.get_all():
            if record["record_id"] == record_id:
                return record
        raise KeyError("Record not found")