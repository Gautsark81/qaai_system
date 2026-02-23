from core.strategy_factory.health.decay.decay_state import AlphaDecayState
from core.strategy_factory.health.retirement.retirement_state import RetirementState

class RetirementPolicy:
    def decide(
        self,
        current_state: RetirementState,
        decay_state: AlphaDecayState,
        consecutive_degraded: int,
    ) -> RetirementState | None:

        if decay_state == AlphaDecayState.CRITICAL:
            return RetirementState.COOLING

        if (
            decay_state == AlphaDecayState.DEGRADING
            and consecutive_degraded >= 3
            and current_state == RetirementState.ACTIVE
        ):
            return RetirementState.AT_RISK

        return None
