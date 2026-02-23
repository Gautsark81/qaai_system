from domain.canary.canary_mode import CanaryMode
from domain.canary.canary_envelope import CanaryEnvelope
from domain.canary.canary_capital_gate import CanaryCapitalGate
from domain.canary.canary_execution_router import CanaryExecutionRouter


class CanaryGuard:
    """
    Enforces LIVE canary invariants.
    """

    @staticmethod
    def approve(
        mode: CanaryMode,
        envelope: CanaryEnvelope,
        approved_capital: float,
    ) -> tuple[str, float] | None:

        if mode != CanaryMode.LIVE:
            return None

        capped = CanaryCapitalGate.allow(envelope, approved_capital)
        if capped is None:
            return None

        route = CanaryExecutionRouter.route(mode)
        return route, capped
