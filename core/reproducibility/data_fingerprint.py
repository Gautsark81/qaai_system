# core/reproducibility/data_fingerprint.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
import pytz

from .utils import sha256_string, sha256_bytes

IST = pytz.timezone("Asia/Kolkata")


@dataclass(frozen=True)
class DataFingerprint:
    symbols_hash: str
    date_range: str
    dataset_hash: str
    record_count: int
    timeframe: str
    source_id: str
    created_at: datetime

    @staticmethod
    def from_file(
        file_path: Path,
        symbols: List[str],
        date_range: Tuple[str, str],
        timeframe: str,
        source_id: str,
        record_count: int,
    ) -> "DataFingerprint":

        file_bytes = file_path.read_bytes()
        dataset_hash = sha256_bytes(file_bytes)

        symbols_hash = sha256_string(",".join(sorted(symbols)))

        return DataFingerprint(
            symbols_hash=symbols_hash,
            date_range=f"{date_range[0]}:{date_range[1]}",
            dataset_hash=dataset_hash,
            record_count=record_count,
            timeframe=timeframe,
            source_id=source_id,
            created_at=datetime.now(IST),
        )