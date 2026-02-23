from typing import Protocol
from .events import CapitalEvent


class CapitalEventHook(Protocol):
    """
    Phase-11 hook interface.
    Implementations must never raise.
    """

    def on_capital_event(self, event: CapitalEvent) -> None:
        ...
