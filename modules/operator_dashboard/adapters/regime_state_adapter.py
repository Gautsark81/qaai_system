# modules/operator_dashboard/adapters/regime_state_adapter.py

from dataclasses import dataclass
from typing import Optional

from core.regime.signals import latest_regime_signal
from core.regime.taxonomy import RegimeLabel


@dataclass(frozen=True)
class RegimeSnapshot:
    """
    Read-only dashboard view of current market regime.

    GUARANTEES:
    - Immutable
    - Serializable
    - Deterministic
    - Never mutates core state
    """

    label: RegimeLabel
    confidence: float


def get_regime_snapshot() -> RegimeSnapshot:
    """
    Return the latest known regime snapshot for the dashboard.

    Safe behavior:
    - If no regime signal exists → return UNKNOWN
    """

    signal = latest_regime_signal()

    if signal is None:
        return RegimeSnapshot(
            label=RegimeLabel.NORMAL,
            confidence=0.0,
        )

    return RegimeSnapshot(
        label=signal.label,
        confidence=signal.confidence,
    )
