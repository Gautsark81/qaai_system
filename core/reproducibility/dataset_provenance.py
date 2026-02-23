# core/reproducibility/dataset_provenance.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import json


@dataclass(frozen=True)
class DatasetProvenance:
    source_type: str              # "s3" | "gcs" | "local" | "db" | "nse_live"
    source_identifier: str        # bucket/path/table name
    snapshot_id: str              # version ID / partition ID / timestamp
    symbol_list: List[str]
    start_date: str
    end_date: str
    record_count: int

    def to_canonical_dict(self) -> Dict:
        return {
            "source_type": self.source_type,
            "source_identifier": self.source_identifier,
            "snapshot_id": self.snapshot_id,
            "symbol_list": sorted(self.symbol_list),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "record_count": self.record_count,
        }

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )