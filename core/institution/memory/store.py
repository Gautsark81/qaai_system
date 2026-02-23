# core/institution/memory/store.py
from typing import List
from core.institution.memory.models import OrgMemoryRecord


class OrgMemoryStore:
    """
    Append-only institutional memory store.
    """

    def __init__(self):
        self._records: List[OrgMemoryRecord] = []

    def append(self, *, record: OrgMemoryRecord) -> None:
        self._records.append(record)

    def list_all(self) -> List[OrgMemoryRecord]:
        return list(self._records)

    def list_by_portfolio(self, *, portfolio_id: str) -> List[OrgMemoryRecord]:
        return [
            r for r in self._records
            if r.portfolio_id == portfolio_id
        ]
