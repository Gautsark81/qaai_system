from typing import Dict, List

from modules.strategy_genome.lineage import LineageRecord


# ==========================================================
# LINEAGE STORE
# ==========================================================

class LineageStore:
    """
    Append-only, in-memory lineage store.

    Can later be backed by DB / S3 / Parquet without changes.
    """

    def __init__(self):
        self._records: Dict[str, LineageRecord] = {}

    # ------------------------------------------------------
    # WRITE (ONCE)
    # ------------------------------------------------------

    def add(self, record: LineageRecord) -> None:
        if record.strategy_id in self._records:
            raise ValueError(
                f"Lineage already exists for strategy_id={record.strategy_id}"
            )
        self._records[record.strategy_id] = record

    # ------------------------------------------------------
    # READ (SAFE)
    # ------------------------------------------------------

    def get(self, strategy_id: str) -> LineageRecord:
        return self._records[strategy_id]

    def ancestors(self, strategy_id: str) -> List[str]:
        """
        Returns ancestor chain (parent → root).
        """
        chain: List[str] = []
        current = strategy_id

        while True:
            record = self._records.get(current)
            if not record or not record.parent_id:
                break
            chain.append(record.parent_id)
            current = record.parent_id

        return chain

    def all(self) -> List[LineageRecord]:
        return list(self._records.values())
