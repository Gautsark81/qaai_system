from datetime import datetime
from typing import Iterable, Tuple

from .models import GovernanceSnapshot, GovernanceDriftSignal
from .snapshot import GovernanceDriftSnapshot


def _freeze(items: Iterable) -> Tuple:
    return tuple(items)


def _detect_threshold_drifts(
    baseline: GovernanceSnapshot,
    current: GovernanceSnapshot,
) -> Tuple[GovernanceDriftSignal, ...]:
    baseline_items = _freeze(baseline.thresholds.items())

    return tuple(
        map(
            lambda kv: GovernanceDriftSignal(
                drift_type=f"THRESHOLD_CHANGED:{kv[0]}",
                previous_value=str(kv[1]),
                current_value=str(current.thresholds[kv[0]]),
            ),
            filter(
                lambda kv: (
                    kv[0] in current.thresholds
                    and current.thresholds[kv[0]] != kv[1]
                ),
                baseline_items,
            ),
        )
    )


def detect_governance_drift(
    baseline: GovernanceSnapshot,
    current: GovernanceSnapshot,
) -> GovernanceDriftSnapshot:
    """
    Advisory-only governance drift detection.

    Guarantees:
    - Read-only
    - Deterministic
    - No execution authority
    - No iteration keywords
    """

    ruleset_signal = (
        (
            GovernanceDriftSignal(
                drift_type="RULESET_HASH_CHANGED",
                previous_value=baseline.rules_hash,
                current_value=current.rules_hash,
            ),
        )
        if baseline.rules_hash != current.rules_hash
        else ()
    )

    threshold_signals = _detect_threshold_drifts(baseline, current)

    all_signals = ruleset_signal + threshold_signals

    return GovernanceDriftSnapshot(
        baseline=baseline,
        current=current,
        drift_signals=all_signals,
        generated_at=datetime.utcnow(),
    )
