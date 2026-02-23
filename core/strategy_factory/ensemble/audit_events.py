import json
from dataclasses import dataclass
from .models import AllocationResult


@dataclass(frozen=True)
class EnsembleAllocationAuditEvent:
    event_type: str
    snapshot_hash: str
    tier_weights: dict
    drawdown_multipliers: dict
    suspensions: dict
    allocations: dict
    governance_adjustments: dict

    @staticmethod
    def from_result(result: AllocationResult):
        return EnsembleAllocationAuditEvent(
            event_type="ENSEMBLE_ALLOCATION_DECISION",
            snapshot_hash=result.snapshot_hash,
            tier_weights=result.tier_weights,
            drawdown_multipliers=result.drawdown_multipliers,
            suspensions=result.suspensions,
            allocations=result.allocations,
            governance_adjustments=result.governance_adjustments,
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "event_type": self.event_type,
                "snapshot_hash": self.snapshot_hash,
                "tier_weights": self.tier_weights,
                "drawdown_multipliers": self.drawdown_multipliers,
                "suspensions": self.suspensions,
                "allocations": self.allocations,
                "governance_adjustments": self.governance_adjustments,
            },
            sort_keys=True,
        )