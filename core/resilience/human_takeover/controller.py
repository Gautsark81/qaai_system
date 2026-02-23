# core/resilience/human_takeover/controller.py
from core.resilience.human_takeover.models import (
    ControlAuthority,
    TakeoverEvent,
)


class HumanTakeoverController:
    """
    Controls authority handoff between system and human.

    HARD RULE:
    - Authority is exclusive at all times.
    """

    def __init__(self):
        self._authority = ControlAuthority.SYSTEM
        self._history = []

    def current_authority(self) -> ControlAuthority:
        return self._authority

    def history(self):
        return list(self._history)

    def request_takeover(self, *, reason: str, evidence: dict) -> TakeoverEvent:
        if self._authority == ControlAuthority.HUMAN:
            # Idempotent
            event = TakeoverEvent(
                authority=ControlAuthority.HUMAN,
                reason="already under human control",
                evidence=evidence,
            )
            self._history.append(event)
            return event

        self._authority = ControlAuthority.HUMAN
        event = TakeoverEvent(
            authority=ControlAuthority.HUMAN,
            reason=reason,
            evidence=evidence,
        )
        self._history.append(event)
        return event

    def release_takeover(self, *, reason: str, evidence: dict) -> TakeoverEvent:
        if self._authority == ControlAuthority.SYSTEM:
            # Idempotent
            event = TakeoverEvent(
                authority=ControlAuthority.SYSTEM,
                reason="already under system control",
                evidence=evidence,
            )
            self._history.append(event)
            return event

        self._authority = ControlAuthority.SYSTEM
        event = TakeoverEvent(
            authority=ControlAuthority.SYSTEM,
            reason=reason,
            evidence=evidence,
        )
        self._history.append(event)
        return event
