from domain.canary.canary_envelope import CanaryEnvelope


class CanaryCapitalGate:
    """
    Final rupee-level gate for LIVE canary.
    """

    @staticmethod
    def allow(
        envelope: CanaryEnvelope,
        approved_capital: float,
    ) -> float | None:
        return envelope.clamp(approved_capital)
