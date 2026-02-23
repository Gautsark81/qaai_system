# core/strategy_factory/capital/productivity/productivity_ledger.py

from typing import Tuple
from .productivity_model import ProductivitySnapshot


class ProductivityLedger:

    def __init__(self):
        self._history: Tuple[ProductivitySnapshot, ...] = ()

    def append(self, snapshot: ProductivitySnapshot) -> None:
        self._history = self._history + (snapshot,)

    def history(self) -> Tuple[ProductivitySnapshot, ...]:
        return tuple(self._history)