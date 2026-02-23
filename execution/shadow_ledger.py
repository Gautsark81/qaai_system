from typing import Dict, Any, List
from threading import Lock


class ShadowLedger:
    """
    Append-only ledger for shadow execution records.
    """

    def __init__(self):
        self._records: List[Dict[str, Any]] = []
        self._lock = Lock()

    def append(self, record: Dict[str, Any]) -> None:
        """
        Append a new shadow record.

        The record must be JSON-serializable.
        """
        if not isinstance(record, dict):
            raise TypeError("ShadowLedger record must be a dict")

        with self._lock:
            self._records.append(record)

    def all(self) -> List[Dict[str, Any]]:
        """
        Return a copy of all shadow records.
        """
        with self._lock:
            return list(self._records)

    def filter(
        self,
        *,
        strategy_id: str | None = None,
        symbol: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter records by strategy and/or symbol.
        """
        with self._lock:
            out = self._records

            if strategy_id is not None:
                out = [r for r in out if r.get("strategy_id") == strategy_id]

            if symbol is not None:
                out = [r for r in out if r.get("symbol") == symbol]

            return list(out)

    def clear(self) -> None:
        """
        Clear all records (testing only).
        """
        with self._lock:
            self._records.clear()
