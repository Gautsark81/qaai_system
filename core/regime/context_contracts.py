# core/regime/context_contracts.py

from types import MappingProxyType
from typing import Dict, Any

from core.regime.regime_context import RegimeContext


class _BaseContextView:
    """
    Internal base for all context views.
    Enforces read-only snapshots and field filtering.
    """

    __slots__ = ("_base",)

    def __init__(self, base: RegimeContext):
        self._base = base

    def _filter(self, snapshot: Dict[str, Any], allowed_keys):
        return MappingProxyType(
            {k: snapshot[k] for k in allowed_keys if k in snapshot}
        )


class StrategyContextView(_BaseContextView):
    """
    Minimal context exposed to strategies.
    """

    _ALLOWED_KEYS = {
        "current_regime",
        "stability_score",
    }

    def snapshot(self, symbol: str):
        base_snapshot = self._base.snapshot(symbol)
        return self._filter(base_snapshot, self._ALLOWED_KEYS)


class MetaModelContextView(_BaseContextView):
    """
    Expanded context for meta-models (still read-only).
    """

    _ALLOWED_KEYS = {
        "current_regime",
        "stability_score",
        "switch_count",
        "transition_frequency",
        "confidence_stats",
    }

    def snapshot(self, symbol: str):
        base_snapshot = self._base.snapshot(symbol)
        return self._filter(base_snapshot, self._ALLOWED_KEYS)


class ObservabilityContextView(_BaseContextView):
    """
    Full descriptive context for dashboards / operators.
    """

    _ALLOWED_KEYS = {
        "current_regime",
        "stability_score",
        "switch_count",
        "transition_frequency",
        "confidence_stats",
        "dominant_transition",
    }

    def snapshot(self, symbol: str):
        base_snapshot = self._base.snapshot(symbol)
        return self._filter(base_snapshot, self._ALLOWED_KEYS)
