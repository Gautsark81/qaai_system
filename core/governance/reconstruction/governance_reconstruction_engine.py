from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# ============================================================
# Governance State (Immutable)
# ============================================================

@dataclass(frozen=True)
class GovernanceState:
    governance_id: str
    strategy_id: str

    # Scaling dimension
    final_capital: Optional[float]
    capital_scale_factor: Optional[float]
    capital_scale_reason: Optional[str]

    # Throttle dimension
    throttle_level: Optional[float]
    throttle_factor: Optional[float]
    throttle_reason: Optional[str]

    # Deterministic resolution timestamp
    last_updated_at: datetime


# ============================================================
# Governance Reconstruction Engine
# ============================================================

class GovernanceReconstructionEngine:
    """
    Phase 12.6 Reconstruction Engine

    Deterministic rules:
    - Last event by timestamp wins per dimension
    - Scaling and throttle resolved independently
    - Ledger insertion order must not matter
    - last_updated_at = max timestamp across all matched events
    - Output immutable
    """

    def __init__(self, *, scaling_ledger, throttle_ledger):
        self._scaling_ledger = scaling_ledger
        self._throttle_ledger = throttle_ledger

    # --------------------------------------------------------

    def reconstruct(self, *, governance_id: str) -> GovernanceState:

        scaling_entries = [
            e for e in self._scaling_ledger.entries
            if getattr(e, "governance_id", None) == governance_id
        ]

        throttle_entries = [
            e for e in self._throttle_ledger.entries
            if getattr(e, "governance_id", None) == governance_id
        ]

        all_entries = scaling_entries + throttle_entries

        if not all_entries:
            raise ValueError(
                f"No events found for governance_id={governance_id}"
            )

        latest_scaling = self._latest_by_timestamp(scaling_entries)
        latest_throttle = self._latest_by_timestamp(throttle_entries)

        # System-wide deterministic timestamp
        last_updated_at = max(
            getattr(e, "timestamp", datetime.min)
            for e in all_entries
        )

        strategy_id = None

        final_capital = None
        capital_scale_factor = None
        capital_scale_reason = None

        throttle_level = None
        throttle_factor = None
        throttle_reason = None

        # ---------------- Scaling ----------------

        if latest_scaling:
            strategy_id = latest_scaling.strategy_id
            final_capital = getattr(latest_scaling, "new_capital", None)
            capital_scale_factor = getattr(latest_scaling, "scale_factor", None)
            capital_scale_reason = getattr(
                latest_scaling,
                "decision_reason",
                None,
            )

        # ---------------- Throttle ----------------

        if latest_throttle:
            strategy_id = strategy_id or latest_throttle.strategy_id

            throttle_level = getattr(
                latest_throttle,
                "throttle_level",
                getattr(latest_throttle, "throttle_factor", None),
            )

            throttle_factor = getattr(
                latest_throttle,
                "throttle_factor",
                getattr(latest_throttle, "throttle_level", None),
            )

            throttle_reason = getattr(
                latest_throttle,
                "reason",
                getattr(latest_throttle, "decision_reason", None),
            )

        return GovernanceState(
            governance_id=governance_id,
            strategy_id=strategy_id,
            final_capital=final_capital,
            capital_scale_factor=capital_scale_factor,
            capital_scale_reason=capital_scale_reason,
            throttle_level=throttle_level,
            throttle_factor=throttle_factor,
            throttle_reason=throttle_reason,
            last_updated_at=last_updated_at,
        )

    # --------------------------------------------------------

    @staticmethod
    def _latest_by_timestamp(entries):
        if not entries:
            return None

        return max(
            entries,
            key=lambda e: getattr(e, "timestamp", datetime.min),
        )