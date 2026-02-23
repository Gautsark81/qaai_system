from dataclasses import dataclass


# ============================================================
# Phase 13 — Drift Result
# ============================================================

@dataclass(frozen=True)
class CapitalExposureDriftResult:
    """
    Immutable drift evaluation result.
    """

    over_allocated: bool
    under_utilized: bool
    utilization_ratio: float
    drift_amount: float

    @property
    def is_safe(self) -> bool:
        return not self.over_allocated


# ============================================================
# Phase 13 — Drift Detector
# ============================================================

class CapitalExposureDriftDetector:
    """
    Detects capital exposure drift relative to allocated capital.

    Must be:
    - Pure
    - Deterministic
    - Side-effect free
    """

    def detect(
        self,
        allocated_capital: float,
        used_capital: float,
    ) -> CapitalExposureDriftResult:

        if allocated_capital <= 0:
            return CapitalExposureDriftResult(
                over_allocated=False,
                under_utilized=False,
                utilization_ratio=0.0,
                drift_amount=0.0,
            )

        utilization_ratio = used_capital / allocated_capital
        drift_amount = used_capital - allocated_capital

        over_allocated = utilization_ratio > 1.0
        under_utilized = utilization_ratio < 0.5

        return CapitalExposureDriftResult(
            over_allocated=over_allocated,
            under_utilized=under_utilized,
            utilization_ratio=utilization_ratio,
            drift_amount=drift_amount,
        )