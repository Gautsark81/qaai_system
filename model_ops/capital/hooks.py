from __future__ import annotations

from typing import Protocol

from .events import CapitalEvent


class CapitalEventHook(Protocol):
    """
    Protocol for observing capital lifecycle events.

    Phase-11:
    - Hooks are OPTIONAL
    - Hooks MUST be side-effect safe
    - No mutation, no execution, no persistence

    Later phases may register concrete implementations.
    """

    def on_event(self, event: CapitalEvent) -> None:
        ...
