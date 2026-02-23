from domain.strategy_factory.strategy_candidate import StrategyCandidate
from domain.strategy_factory.ssr_admission_rules import SSRAdmissionRules
from domain.validation.fingerprint_validator import FingerprintValidator


class StrategyGovernanceGate:
    """
    Final admission gate for strategy factory output.
    """

    @staticmethod
    def evaluate(
        *,
        strategy_id: str,
        fingerprint,
        ssr: float,
    ) -> StrategyCandidate:
        fp_res = FingerprintValidator.validate(fingerprint)
        if not fp_res.valid:
            return StrategyCandidate(
                strategy_id=strategy_id,
                fingerprint=fingerprint,
                ssr=ssr,
                eligible=False,
                rejection_reason="Invalid fingerprint",
            )

        ssr_res = SSRAdmissionRules.validate(ssr)
        if not ssr_res.valid:
            return StrategyCandidate(
                strategy_id=strategy_id,
                fingerprint=fingerprint,
                ssr=ssr,
                eligible=False,
                rejection_reason=ssr_res.errors[0],
            )

        return StrategyCandidate(
            strategy_id=strategy_id,
            fingerprint=fingerprint,
            ssr=ssr,
            eligible=True,
            rejection_reason=None,
        )
