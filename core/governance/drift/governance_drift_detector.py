from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime


@dataclass(frozen=True)
class GovernanceDriftReport:
    governance_id: str
    strategy_id: Optional[str]
    valid: bool
    errors: Tuple[str, ...]


class GovernanceDriftDetector:
    """
    Phase 12.6.3 — Governance Drift Detection

    Detects:
    - Orphan governance chains
    - Capital continuity violations
    - Cross-strategy governance collisions
    - Throttle-scaling conflict
    """

    def __init__(self, *, scaling_ledger, throttle_ledger):
        self._scaling_ledger = scaling_ledger
        self._throttle_ledger = throttle_ledger

    # -------------------------------------------------------------

    def detect(self, *, governance_id: str) -> GovernanceDriftReport:

        scaling = [
            e for e in self._scaling_ledger.entries
            if getattr(e, "governance_id", None) == governance_id
        ]

        throttle = [
            e for e in self._throttle_ledger.entries
            if getattr(e, "governance_id", None) == governance_id
        ]

        errors = []

        if not scaling and not throttle:
            return GovernanceDriftReport(
                governance_id=governance_id,
                strategy_id=None,
                valid=False,
                errors=("NO_EVENTS_FOUND",),
            )

        # ---------------------------------------------------------
        # Strategy Consistency
        # ---------------------------------------------------------

        strategy_ids = {
            getattr(e, "strategy_id", None)
            for e in scaling + throttle
        }

        if len(strategy_ids) > 1:
            errors.append("CROSS_STRATEGY_COLLISION")

        strategy_id = next(iter(strategy_ids)) if strategy_ids else None

        # ---------------------------------------------------------
        # Orphan Detection
        # ---------------------------------------------------------

        if scaling and not throttle:
            errors.append("THROTTLE_MISSING")

        if throttle and not scaling:
            errors.append("SCALING_MISSING")

        # ---------------------------------------------------------
        # Capital Continuity
        # ---------------------------------------------------------

        scaling_sorted = sorted(
            scaling,
            key=lambda e: getattr(e, "timestamp", datetime.min),
        )

        for i in range(1, len(scaling_sorted)):
            prev = scaling_sorted[i - 1]
            curr = scaling_sorted[i]

            if getattr(prev, "new_capital", None) != getattr(curr, "previous_capital", None):
                errors.append("CAPITAL_CONTINUITY_VIOLATION")
                break

        # ---------------------------------------------------------
        # Throttle / Scale Conflict (same timestamp)
        # ---------------------------------------------------------

        scaling_by_ts = {
            getattr(e, "timestamp", None): e
            for e in scaling
        }

        for t_event in throttle:
            ts = getattr(t_event, "timestamp", None)
            s_event = scaling_by_ts.get(ts)

            if s_event:
                scale_factor = getattr(s_event, "scale_factor", None)
                throttle_level = getattr(
                    t_event,
                    "throttle_level",
                    getattr(t_event, "throttle_factor", None),
                )

                if scale_factor and throttle_level:
                    if scale_factor > 1.0 and throttle_level < 1.0:
                        errors.append("THROTTLE_SCALE_CONFLICT")

        return GovernanceDriftReport(
            governance_id=governance_id,
            strategy_id=strategy_id,
            valid=len(errors) == 0,
            errors=tuple(errors),
        )