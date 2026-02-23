from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class CooldownPolicy:
    clean_windows_required: int = 3
    freeze_multiplier: int = 2


@dataclass(frozen=True)
class CooldownResult:
    strike_reduced: bool
    new_strike_count: int
    governance_id: str
    evaluated_at: datetime


class GovernanceCooldownEngine:
    """
    C7.3 — Strike Cooldown Engine

    Pure evaluation engine.
    Does NOT mutate strike ledger.
    Determines whether a strike reduction is allowed.
    """

    def __init__(self, policy: Optional[CooldownPolicy] = None):
        self.policy = policy or CooldownPolicy()

    def evaluate(
        self,
        *,
        governance_id: str,
        current_strikes: int,
        escalation_level: str,
        clean_windows: int,
    ) -> CooldownResult:

        now = datetime.now(timezone.utc)

        if current_strikes <= 0:
            return CooldownResult(
                strike_reduced=False,
                new_strike_count=0,
                governance_id=governance_id,
                evaluated_at=now,
            )

        # ZERO_CAPITAL never auto-decays
        if escalation_level == "ZERO_CAPITAL":
            return CooldownResult(
                strike_reduced=False,
                new_strike_count=current_strikes,
                governance_id=governance_id,
                evaluated_at=now,
            )

        required = self.policy.clean_windows_required

        if escalation_level == "FREEZE":
            required *= self.policy.freeze_multiplier

        if clean_windows >= required:
            return CooldownResult(
                strike_reduced=True,
                new_strike_count=max(current_strikes - 1, 0),
                governance_id=governance_id,
                evaluated_at=now,
            )

        return CooldownResult(
            strike_reduced=False,
            new_strike_count=current_strikes,
            governance_id=governance_id,
            evaluated_at=now,
        )